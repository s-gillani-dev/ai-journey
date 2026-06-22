# DineFlow/state_machine/query_classifier.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional


# =============================================================================
# 🔍 QUERY CLASSIFIER — STRUCTURAL INTENT ANALYSIS (v1.0)
#
# Purpose:
#   Determine whether a user query is referencing a SPECIFIC menu item
#   (entity-bound) or asking about a PROPERTY across the catalog
#   (attribute-bound), so Authority can grant the correct context scope.
#
# Design Principle — Structural over Lexical:
#   A hardcoded keyword set ("spicy", "vegan", "cheap") is a lookup table
#   pretending to be intelligence. It breaks as user vocabulary expands.
#   This classifier instead reads GRAMMATICAL STRUCTURE — patterns that are
#   stable regardless of menu size or item names.
#
#   Entity query:    "Tell me about the Pepperoni Pizza"   → FILTERED_SEARCH
#   Attribute query: "Do you have anything spicy?"         → FULL_CATALOG
#   Ambiguous:       "What about pizza?"                   → FULL_CATALOG (safe default)
#
# Failure Mode Policy:
#   Always fail toward MORE data (FULL_CATALOG), never toward LESS.
#   A false-negative (full scan when filtered would suffice) costs one extra
#   retrieval. A false-positive (filtered when full scan was needed) causes
#   a silent knowledge failure and a broken user experience.
# =============================================================================


class QueryClass(Enum):
    ENTITY_BOUND    = "entity_bound"    # User references a specific named item
    ATTRIBUTE_BOUND = "attribute_bound" # User references a property/category
    AMBIGUOUS       = "ambiguous"       # Insufficient signal; defaults to safe path


@dataclass
class ClassifiedQuery:
    query_class: QueryClass
    confidence: float
    resolved_entity: Optional[str]  # SKU if a named item was found, else None
    reasoning: str                  # Auditable trace for logs


class QueryClassifier:
    """
    Classifies a user query as entity-bound or attribute-bound using
    structural signals, not vocabulary matching.

    Instantiated once at bootstrap and reused across all requests.
    The name index is built at construction time (O(n) once),
    and all classify() calls are O(n) name lookups at worst.
    """

    def __init__(self, all_menu_items: list):
        """
        Args:
            all_menu_items: The full list of MenuItemSnapshot objects.
                            Passed in from the bootstrap so the classifier
                            shares the same data source as the rest of the system.
        """
        # Build name → SKU index once. Lower-cased for case-insensitive matching.
        self._name_index: dict[str, str] = {
            item.name.lower(): item.sku for item in all_menu_items
        }

    def classify(self, user_input: str) -> ClassifiedQuery:
        """
        Classify the query. Returns a ClassifiedQuery with full audit trace.
        Never raises — returns AMBIGUOUS on any unexpected input.
        """
        if not user_input or not user_input.strip():
            return ClassifiedQuery(
                query_class=QueryClass.AMBIGUOUS,
                confidence=0.0,
                resolved_entity=None,
                reasoning="Empty input; defaulting to AMBIGUOUS."
            )

        normalized = user_input.lower().strip()

        # ── Signal 1: Named Entity Resolution ─────────────────────────────────
        # If the user mentions a known item by name, this is entity-bound.
        # This check runs first because it's the most precise signal.
        resolved_sku = self._resolve_entity(normalized)
        if resolved_sku:
            return ClassifiedQuery(
                query_class=QueryClass.ENTITY_BOUND,
                confidence=0.95,
                resolved_entity=resolved_sku,
                reasoning=f"Known menu item name detected in query; SKU resolved: '{resolved_sku}'"
            )

        # ── Signal 2: Categorical Grammar Patterns ────────────────────────────
        # These words grammatically indicate the user is scanning a category,
        # not referencing a specific item. Stable regardless of menu content.
        if self._has_categorical_structure(normalized):
            return ClassifiedQuery(
                query_class=QueryClass.ATTRIBUTE_BOUND,
                confidence=0.88,
                resolved_entity=None,
                reasoning="Categorical grammar pattern detected (anything/something/any/which/what/options)"
            )

        # ── Signal 3: Price/Quantity Comparator Patterns ──────────────────────
        # Comparators ("under $15", "cheapest", "less than") structurally
        # require scanning the full catalog to find qualifying items.
        if self._has_comparator_structure(normalized):
            return ClassifiedQuery(
                query_class=QueryClass.ATTRIBUTE_BOUND,
                confidence=0.85,
                resolved_entity=None,
                reasoning="Price/quantity comparator structure detected"
            )

        # ── Default: Ambiguous → Safe Path ────────────────────────────────────
        # No strong signal found. Default to FULL_CATALOG to avoid silent failures.
        return ClassifiedQuery(
            query_class=QueryClass.AMBIGUOUS,
            confidence=0.5,
            resolved_entity=None,
            reasoning="No structural signals found; defaulting to AMBIGUOUS (safe: FULL_CATALOG)"
        )

    # ── Private Signal Detectors ───────────────────────────────────────────────

    def _resolve_entity(self, text: str) -> Optional[str]:
        """Returns SKU if any known item name appears in the query, else None."""
        # Exact match
        if text in self._name_index:
            return self._name_index[text]
        # Substring match — item name appears anywhere in the query
        for name, sku in self._name_index.items():
            if name in text:
                return sku
        return None

    def _has_categorical_structure(self, text: str) -> bool:
        """
        Detects grammatical patterns that indicate category-scanning intent.
        These are NOT menu keywords — they are structural query patterns.

        "anything spicy" → "anything" signals category scan
        "any vegan options" → "any " signals category scan
        "what do you have that's gluten-free" → "what do you have" signals scan
        "show me something light" → "something" signals category scan
        """
        categorical_patterns = [
            "anything",
            "something",
            "any ",
            "what's on",
            "what do you have",
            "what do you offer",
            "which ",
            "do you have any",
            "do you have anything",
            "what are your",
            "show me",
            "what kind",
            "options",
            "what can i get",
            "what would you recommend",
            "suggestions",
        ]
        return any(p in text for p in categorical_patterns)

    def _has_comparator_structure(self, text: str) -> bool:
        """
        Detects price or quantity comparator patterns that require
        scanning the full catalog to find qualifying items.

        These are structural patterns (under $, cheaper than, most expensive),
        not open-ended adjectives like "cheap" which can appear in non-scan
        contexts ("is the beer cheap?").
        """
        comparator_patterns = [
            "under $",
            "over $",
            "less than $",
            "more than $",
            "cheaper than",
            "most expensive",
            "least expensive",
            "cheapest",
            "between $",
            "around $",
            "within my budget",
            "affordable",
        ]
        return any(p in text for p in comparator_patterns)