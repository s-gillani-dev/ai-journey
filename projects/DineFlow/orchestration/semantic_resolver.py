# DineFlow/orchestration/semantic_resolver.py
"""
Semantic Resolver — Hybrid Context-Aware Reference Resolution

Purpose:
    Converts vague references ("all", "that", "same", "2", "cancel that",
    and multilingual equivalents) into concrete resolved intents using the
    Active Context Graph on the session.

Architecture (Hybrid):
    1. NORMALIZE     — strip noise (politeness words, punctuation)
    2. RULE ENGINE   — exact set membership and regex patterns only
                       NO language-dependent substring/verb checks
    3. CONFIDENCE    — gate LLM calls by rule confidence score
    4. LLM FALLBACK  — handles fuzzy/multilingual inputs rules miss
    5. RESOLVE       — derive concrete SKUs from active_context

Design principles:
    - Rules handle structure (numbers, exact keywords, positions).
      LLM handles meaning (language, intent, nuance, multilingual).
    - No English-dependent substring checks in rules — these break
      for Urdu, Spanish, Arabic, etc. LLM handles those cases.
    - Confidence layer prevents LLM calls for high-confidence rule
      matches (60-80% cost reduction at scale).
    - Single-token inputs with zero rule confidence still reach LLM
      because they may be meaningful single words in other languages:
      "sab" (Urdu: all), "todo" (Spanish: all), "alles" (German: all).
    - Context is sent to LLM as structured JSON with positions, enabling
      positional resolution ("the first one") in any language.
    - active_context is built from system outputs only (never user input).
    - Returns None for non-references — golden_loop proceeds to router.

Context expiry:
    Items older than MAX_CONTEXT_TURNS are ignored.
"""

import re
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from state_machine.types import SessionState

MAX_CONTEXT_TURNS = 3

# LLM is only called when rule confidence is below this threshold.
_LLM_CONFIDENCE_THRESHOLD = 0.7

# Minimum token count for LLM fallback — BUT only when confidence > 0.
# When confidence == 0.0 (no rule matched at all), single-token inputs
# may be meaningful references in other languages ("sab", "todo", "alles")
# and should reach the LLM regardless of token count.
_LLM_MIN_TOKENS = 2

# ── Politeness normalization (regex — extensible, not a brittle set) ──────────
_POLITENESS_RE = re.compile(
    r"\b(please|pls|plz|kindly|thanks|thank you|thank you so much|thx|cheers)\b",
    re.IGNORECASE
)

# ── Positional words ──────────────────────────────────────────────────────────
_POSITION_WORDS: Dict[str, int] = {
    "first": 0, "second": 1, "third": 2, "fourth": 3, "last": -1,
}


class ReferenceIntent(str, Enum):
    ADD_ALL      = "ADD_ALL"
    ADD_THAT     = "ADD_THAT"
    REPEAT       = "REPEAT"
    QUANTITY     = "QUANTITY"
    CANCEL       = "CANCEL"
    NOT_RESOLVED = "NOT_RESOLVED"


@dataclass
class ResolvedIntent:
    intent: ReferenceIntent
    skus: List[str] = field(default_factory=list)
    quantity: Optional[int] = None
    source: str = "active_context"


# ── Rule word sets — exact membership only, no substring/verb checks ──────────
# Multilingual variants not in these sets fall through to LLM automatically.

_COLLECTION_WORDS = {
    "all", "everything", "those", "them", "all of them", "all of those",
    "yes all", "add all", "add them all", "get all", "order all",
    "i want all", "all mentioned", "i want all mentioned",
    "add all of them", "yes add all", "all of those please"
}

_THAT_WORDS = {
    "that", "this", "that one", "this one", "it", "the one",
    "that item", "this item", "that pizza", "that beer",
    "add it", "add that", "add this", "order it",
    "order that", "yes add it", "add the one", "i'll take it",
    "i'll take that", "get it", "get that"
}

_REPEAT_WORDS = {
    "same", "same again", "another", "one more", "again",
    "repeat", "the same", "same one", "same thing"
}

_CANCEL_WORDS = {
    "cancel", "cancel that", "undo", "never mind", "nevermind",
    "remove", "remove that", "remove last", "take that back",
    "forget it", "forget that", "scratch that", "dont add that",
}

_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


def _normalize(text: str) -> str:
    """
    Strips punctuation, politeness words, and collapses whitespace.
    Does NOT strip semantic meaning — only noise.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = _POLITENESS_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_number(clean: str) -> Optional[int]:
    """Extracts the first integer from cleaned input. Catches '2 more', 'add 2'."""
    match = re.search(r"\b(\d+)\b", clean)
    return int(match.group(1)) if match else None


def _extract_position(clean: str) -> Optional[int]:
    """
    Extracts positional index: 'first' → 0, 'last' → -1.
    Returns position as int so resolve() can index into _fresh_mentioned.
    """
    for word, pos in _POSITION_WORDS.items():
        if word in clean.split():
            return pos
    return None


def _rule_confidence(clean: str) -> float:
    """
    Scores rule engine confidence for the cleaned input.

    HIGH confidence (>= 0.7): exact set membership — LLM not needed.
    ZERO confidence: no rule matched — may be another language, send to LLM.

    NO substring/verb checks here. "add", "want", "take" are English verbs
    that would create false confidence and block LLM for non-English inputs.
    Zero confidence correctly routes all unmatched inputs to LLM.
    """
    if clean in _COLLECTION_WORDS:
        return 1.0
    if clean in _THAT_WORDS or _extract_position(clean) is not None:
        return 0.9
    if clean in _REPEAT_WORDS:
        return 0.9
    if clean in _CANCEL_WORDS:
        return 0.9
    # Only return high confidence for numbers when the number IS the intent —
    # i.e. nothing meaningful accompanies it. "remove 2" has a number but the
    # intent is not QUANTITY — it should reach LLM. Same logic as _classify.
    number = _extract_number(clean)
    if number is not None:
        without_number = re.sub(r"\b" + str(number) + r"\b", "", clean).strip()
        non_trivial = [t for t in without_number.split() if len(t) > 2]
        if not non_trivial:
            return 1.0
    elif clean in _NUMBER_WORDS:
        return 1.0
    return 0.0


def _build_context_payload(session: "SessionState") -> List[Dict]:
    """
    Builds structured context for LLM: [{name, position}] with session metadata.
    Only includes fresh, non-expired items from active_context.
    """
    items = []
    if session.active_context:
        current_turn = session.turn_id
        for item in session.active_context.values():
            item_turn = item.last_mentioned_turn // 100
            if item.mentioned and (current_turn - item_turn) <= MAX_CONTEXT_TURNS:
                items.append(item.name)
    if not items and session.last_action_sku:
        items.append(session.last_action_sku)
    return [{"name": name, "position": idx} for idx, name in enumerate(items)]


def _llm_classify(
    user_input: str,
    session: "SessionState"
) -> tuple[ReferenceIntent, Optional[int]]:
    """
    LLM fallback for inputs the rule engine cannot confidently classify.

    Handles:
        - Multilingual: "sab add kar do" (Urdu), "añade todo" (Spanish)
        - Fuzzy phrasing: "add everything you showed me"
        - Positional: "the second one", "the last pizza"

    Sends structured context (positions + session state) so LLM has enough
    information to resolve correctly in any language.

    Returns (NOT_RESOLVED, None) on any failure — safe exit.
    """
    from llm.client import call_llm

    context_payload = _build_context_payload(session)
    normalized_input = _normalize(user_input)

    # Include session state signals to help LLM resolve ambiguous cases
    last_action = getattr(session, "last_action_type", None) or "none"
    last_agent = getattr(session, "active_agent", "unknown")

    prompt = f"""You are an intent classifier for a multilingual food ordering assistant.

User said: "{user_input}"
Normalized: "{normalized_input}"
Last action: {last_action}
Last agent: {last_agent}

Recent items shown to user (ONLY valid references — if user says "all" or "that", it refers ONLY to these):
{json.dumps(context_payload, ensure_ascii=False, indent=2)}

If no items are listed above → return NOT_RESOLVED immediately.

Classify the user's intent into exactly ONE of:
- ADD_ALL: user wants to add all listed items ("all", "everything", "sab", "todos", "همه")
- ADD_THAT: user wants a specific item by reference or position ("that", "it", "the first one")
- REPEAT: user wants to repeat their last order ("same", "another", "ek aur")
- QUANTITY: user is specifying a quantity ("2", "three", "do")
- CANCEL: user wants to remove something ("cancel", "remove", "nahi", "undo")
- NOT_RESOLVED: input is not a reference to the above context

STRICT RULES:
- intent MUST be exactly one of the six values above
- For ADD_THAT with a positional reference, return the position index as quantity
- If input is an explicit new order (names a specific item directly) → NOT_RESOLVED
- Consider ALL languages — user may not be writing in English
- If unsure → NOT_RESOLVED

Return ONLY valid JSON with no explanation or markdown:
{{"intent": "ADD_ALL", "quantity": null, "confidence": 0.9}}"""

    try:
        raw = call_llm(prompt, user_input)
        raw = re.sub(r"```[a-z]*", "", raw).strip().strip("`").strip()
        data = json.loads(raw)
        intent_str = data.get("intent", "NOT_RESOLVED").upper()
        llm_confidence = float(data.get("confidence", 0.5))

        try:
            intent = ReferenceIntent(intent_str)
        except ValueError:
            intent = ReferenceIntent.NOT_RESOLVED

        quantity = data.get("quantity")
        try:
            quantity = int(quantity) if quantity is not None else None
        except (ValueError, TypeError):
            quantity = None

        return intent, quantity, llm_confidence

    except Exception:
        return ReferenceIntent.NOT_RESOLVED, None, 0.0


def _classify(
    user_input: str,
    session: "SessionState"
) -> tuple[ReferenceIntent, Optional[int]]:
    """
    Hybrid classification:
        1. Normalize
        2. Rule engine — exact set membership and regex only (no English verbs)
        3. Confidence gate — high confidence skips LLM
        4. LLM fallback — single-token allowed when confidence=0 (multilingual)
    """
    clean = _normalize(user_input)

    if not clean:
        return ReferenceIntent.NOT_RESOLVED, None

    # ── RULE ENGINE — exact matches only, no language-dependent checks ────────

    if clean in _CANCEL_WORDS:
        return ReferenceIntent.CANCEL, None

    if clean in _COLLECTION_WORDS:
        return ReferenceIntent.ADD_ALL, None

    if clean in _THAT_WORDS:
        return ReferenceIntent.ADD_THAT, None

    position = _extract_position(clean)
    if position is not None:
        return ReferenceIntent.ADD_THAT, position

    if clean == "add":
        # Bare "add" with no target → NOT_RESOLVED, let router handle
        return ReferenceIntent.NOT_RESOLVED, None

    if clean in _REPEAT_WORDS:
        return ReferenceIntent.REPEAT, None

    # QUANTITY: only when the input IS essentially a number.
    # "2", "three", "2 more" are quantity signals.
    # "remove 3", "delete 2", "احذف 3" are NOT — the number is part of
    # a larger intent the rule engine cannot classify. Those fall through
    # to the LLM which resolves them with context regardless of language.
    #
    # Detection: after removing the number itself from the cleaned input,
    # if nothing meaningful remains (≤1 non-trivial token left), treat as
    # QUANTITY. If other words remain, let LLM classify the full intent.
    number = _extract_number(clean)
    if number is not None:
        without_number = re.sub(r"\b" + str(number) + r"\b", "", clean).strip()
        non_trivial = [t for t in without_number.split() if len(t) > 2]
        if not non_trivial:
            return ReferenceIntent.QUANTITY, number
        # Has other words alongside number — fall through to LLM

    if clean in _NUMBER_WORDS:
        return ReferenceIntent.QUANTITY, _NUMBER_WORDS[clean]

    # ── CONFIDENCE GATE + LLM FALLBACK ───────────────────────────────────────
    confidence = _rule_confidence(clean)
    fresh_items = _fresh_mentioned(session)
    has_context = bool(fresh_items) or bool(session.last_action_sku)
    token_count = len(clean.split())

    # Allow LLM for single-token inputs when confidence == 0.0 — these may be
    # meaningful single-word references in non-English languages.
    # For inputs with partial confidence, require _LLM_MIN_TOKENS.
    should_use_llm = (
        confidence < _LLM_CONFIDENCE_THRESHOLD
        and has_context
        and (token_count >= _LLM_MIN_TOKENS or confidence == 0.0)
    )

    if should_use_llm:
        intent, qty, llm_conf = _llm_classify(user_input, session)
        # Log LLM confidence (what the model returned), not rule confidence (0.0)
        # Rule confidence is always < threshold here — logging it is misleading.
        _log_resolution(user_input, clean, intent, source="llm", confidence=llm_conf)
        return intent, qty

    _log_resolution(user_input, clean, ReferenceIntent.NOT_RESOLVED, source="rules", confidence=confidence)
    return ReferenceIntent.NOT_RESOLVED, None


def _log_resolution(
    user_input: str,
    normalized: str,
    intent: ReferenceIntent,
    source: str,
    confidence: float = 0.0
) -> None:
    print(
        f"[SEMANTIC] input={repr(user_input)} normalized={repr(normalized)} "
        f"intent={intent.value} source={source} confidence={confidence:.2f}"
    )


def _fresh_mentioned(session: "SessionState") -> List[str]:
    """
    Returns SKUs from active_context where mentioned=True and not expired.
    Prefers items from the most recent turn only.
    """
    current_turn = session.turn_id
    fresh = []
    for item in session.active_context.values():
        item_turn = item.last_mentioned_turn // 100
        if item.mentioned and (current_turn - item_turn) <= MAX_CONTEXT_TURNS:
            fresh.append(item)

    if not fresh:
        return []

    def turn_of(item):
        return item.last_mentioned_turn // 100

    most_recent_turn = max(turn_of(item) for item in fresh)
    most_recent = [item for item in fresh if turn_of(item) == most_recent_turn]
    result = most_recent if most_recent else fresh
    result.sort(key=lambda x: x.last_mentioned_turn, reverse=True)
    return [item.sku for item in result]


def _last_selected(session: "SessionState") -> Optional[str]:
    """Returns the SKU of the most recently selected (confirmed) item."""
    selected = [
        item for item in session.active_context.values()
        if item.selected
    ]
    if not selected:
        return None
    selected.sort(key=lambda x: x.last_mentioned_turn, reverse=True)
    return selected[0].sku


def resolve(user_input: str, session: "SessionState") -> Optional[ResolvedIntent]:
    """
    Main entry point. Called from golden_loop Step 0 before routing.

    Returns ResolvedIntent if input is a reference that can be resolved.
    Returns None if input is a normal request — golden_loop proceeds to router.
    """
    intent_type, quantity = _classify(user_input, session)

    if intent_type == ReferenceIntent.NOT_RESOLVED:
        return None

    # ── CANCEL ────────────────────────────────────────────────────────────────
    if intent_type == ReferenceIntent.CANCEL:
        # Priority 1: most recently selected item in context
        selected_sku = _last_selected(session)
        if selected_sku:
            return ResolvedIntent(
                intent=ReferenceIntent.CANCEL,
                skus=[selected_sku],
                quantity=session.last_quantity or 1,
                source="active_context"
            )
        # Priority 2: last_action_sku focus
        if session.last_action_sku:
            return ResolvedIntent(
                intent=ReferenceIntent.CANCEL,
                skus=[session.last_action_sku],
                quantity=session.last_quantity or 1,
                source="last_action_sku"
            )
        # Priority 3: cart fallback — if cart has exactly one item type,
        # "cancel" unambiguously refers to it. If multiple items, return
        # None and let OrderTaker ask for clarification ("cancel which one?")
        if session.cart and len(session.cart) == 1:
            cart_sku = next(iter(session.cart))
            return ResolvedIntent(
                intent=ReferenceIntent.CANCEL,
                skus=[cart_sku],
                quantity=session.cart[cart_sku],
                source="cart"
            )
        return None

    # ── ADD_ALL ───────────────────────────────────────────────────────────────
    if intent_type == ReferenceIntent.ADD_ALL:
        mentioned_skus = _fresh_mentioned(session)
        if mentioned_skus:
            return ResolvedIntent(
                intent=ReferenceIntent.ADD_ALL,
                skus=mentioned_skus,
                source="active_context"
            )
        if session.pending_items:
            return ResolvedIntent(
                intent=ReferenceIntent.ADD_ALL,
                skus=list(session.pending_items),
                source="pending_items"
            )
        return None

    # ── ADD_THAT ──────────────────────────────────────────────────────────────
    if intent_type == ReferenceIntent.ADD_THAT:
        mentioned_skus = _fresh_mentioned(session)
        if mentioned_skus:
            if quantity is not None:
                try:
                    target_sku = mentioned_skus[quantity]
                except IndexError:
                    target_sku = mentioned_skus[0]
            else:
                target_sku = mentioned_skus[0]
            return ResolvedIntent(
                intent=ReferenceIntent.ADD_THAT,
                skus=[target_sku],
                source="active_context"
            )
        if session.last_action_sku:
            return ResolvedIntent(
                intent=ReferenceIntent.ADD_THAT,
                skus=[session.last_action_sku],
                source="last_action_sku"
            )
        return None

    # ── REPEAT ────────────────────────────────────────────────────────────────
    if intent_type == ReferenceIntent.REPEAT:
        selected_sku = _last_selected(session)
        target_sku = selected_sku or session.last_action_sku
        if target_sku:
            return ResolvedIntent(
                intent=ReferenceIntent.REPEAT,
                skus=[target_sku],
                quantity=session.last_quantity or 1,
                source="active_context" if selected_sku else "last_action_sku"
            )
        return None

    # ── QUANTITY ──────────────────────────────────────────────────────────────
    if intent_type == ReferenceIntent.QUANTITY:
        selected_sku = _last_selected(session)
        target_sku = selected_sku or session.last_action_sku
        if target_sku:
            return ResolvedIntent(
                intent=ReferenceIntent.QUANTITY,
                skus=[target_sku],
                quantity=quantity,
                source="active_context" if selected_sku else "last_action_sku"
            )
        return None

    return None