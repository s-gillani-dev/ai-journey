# # aiva/agents/router.py
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.validation.schemas import ActionRequest, ActionType, IntentType

# class IntentRouter:
#     ALLOWED_AGENTS = {"Greeter", "OrderTaker", "MenuExpert"}

#     def __init__(self):
#         self.prompt_path = "aiva/llm/prompts/router.md"

#     def _load_prompt(self, active_agent: str) -> str:
#         with open(self.prompt_path, "r") as f:
#             template = f.read()
#         return template.replace("{{ACTIVE_AGENT}}", active_agent)

#     def route(self, user_input: str, active_agent: str) -> ActionRequest:
#         text = user_input.lower().strip()

#         # --- IMPROVEMENT 4: Deterministic Short-Circuit (Zero-Cost) ---
#         if text in {"hi", "hello", "hey", "bye", "thanks", "thank you"}:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="Greeter",
#                 confidence=1.0,
#                 meta={"intent": IntentType.GREETING, "reasoning": "Exact match (Greeting)"}
#             )

#         if text in {"yes", "no", "ok", "okay", "sure", "yep", "nope"}:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent=active_agent,
#                 confidence=1.0,
#                 meta={"intent": "AMBIGUOUS", "reasoning": "Sticky response (Confirmation/Negation)"}
#             )

#         # --- LLM Fallback for Complex Intent ---
#         system_prompt = self._load_prompt(active_agent)
#         raw_output = call_llm(system_prompt, user_input)
#         action = parse_action(raw_output)
        
#         # --- IMPROVEMENT 5: Validate Target Agent Allowlist ---
#         if action.target_agent not in self.ALLOWED_AGENTS:
#             action.target_agent = active_agent  # Default to current to avoid crash
#             action.meta = action.meta or {}
#             action.meta["router_error"] = "Hallucinated agent corrected"

#         # Force ActionType to TRANSFER regardless of LLM output
#         action.action_type = ActionType.TRANSFER
                
#         return action




# aiva/agents/router.py
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.validation.schemas import ActionRequest, ActionType, IntentType

# class IntentRouter:
#     ALLOWED_AGENTS = {"Greeter", "OrderTaker", "MenuExpert"}

#     def __init__(self):
#         self.prompt_path = "aiva/llm/prompts/router.md"

#     def _load_prompt(self, active_agent: str) -> str:
#         with open(self.prompt_path, "r") as f:
#             template = f.read()
#         return template.replace("{{ACTIVE_AGENT}}", active_agent)

#     def route(self, user_input: str, active_agent: str) -> ActionRequest:
#         text = user_input.lower().strip()
#         tokens = set(text.split()) # 🔧 Improvement 1: Tokenization for exact matches

#         # --- Deterministic Greetings ---
#         if text in {"hi", "hello", "hey", "bye", "thanks", "thank you"}:
#             print(f"🎯 Router: Deterministic match for '{text}' → Greeter")  # ⬅️ ADD THIS
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="Greeter",
#                 confidence=1.0,
#                 meta={"intent": IntentType.GREETING}
#             )

#         # --- 🔧 Improvement 6 & Polish 1: Verb-based Bias with Token Matching ---
#         order_verbs = {"add", "order", "buy", "get", "want", "take", "checkout"}
#         has_order_verb = bool(tokens & order_verbs) # No more substring false positives
        
#         inquiry_keywords = {"menu", "price", "spicy", "ingredient", "allergy", "is there", "contain"}
#         has_inquiry_keyword = bool(tokens & inquiry_keywords)

#         if not has_order_verb and has_inquiry_keyword:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="MenuExpert",
#                 confidence=0.85, # 🔧 Polish 3: Deterministic Confidence Floor
#                 meta={"intent": IntentType.INQUIRY}
#             )

#         # --- LLM Fallback ---
#         system_prompt = self._load_prompt(active_agent)
#         raw_output = call_llm(system_prompt, user_input)
#         action = parse_action(raw_output)
        
#         # 🔧 Polish 3: Prevent LLM over-confidence
#         action.confidence = min(action.confidence or 0.7, 0.85)
#         action.action_type = ActionType.TRANSFER
                
#         return action





# Claud gives this version
# aiva/agents/router.py
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.validation.schemas import ActionRequest, ActionType, IntentType

# class IntentRouter:
#     """
#     🔧 STEP 11: Simplified router - defaults to OrderTaker for optimistic handling.
#     Only routes to MenuExpert for EXPLICIT questions.
#     """
#     ALLOWED_AGENTS = {"Greeter", "OrderTaker", "MenuExpert"}

#     def __init__(self):
#         self.prompt_path = "aiva/llm/prompts/router.md"

#     def _load_prompt(self, active_agent: str) -> str:
#         with open(self.prompt_path, "r") as f:
#             template = f.read()
#         return template.replace("{{ACTIVE_AGENT}}", active_agent)

#     def route(self, user_input: str, active_agent: str) -> ActionRequest:
#         text = user_input.lower().strip()
#         tokens = set(text.split())

#         # ═══════════════════════════════════════════════════════════
#         # DETERMINISTIC ROUTING (Fast, No LLM)
#         # ═══════════════════════════════════════════════════════════

#         # 1️⃣ Greetings/Farewells
#         if text in {"hi", "hello", "hey", "bye", "thanks", "thank you"}:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="Greeter",
#                 confidence=1.0,
#                 meta={"intent": IntentType.GREETING, "routing": "deterministic"}
#             )

#         # 2️⃣ Explicit Menu Questions (question words + inquiry keywords)
#         question_words = {"what", "which", "how", "does", "is", "are", "can", "tell", "show"}
#         inquiry_keywords = {"menu", "price", "cost", "spicy", "ingredient", "allergy", "contain", "have"}
        
#         has_question_word = bool(tokens & question_words)
#         has_inquiry_keyword = bool(tokens & inquiry_keywords)
#         # 🔍 DEBUG
#         print(f"🔍 Question word: {has_question_word}, Inquiry keyword: {has_inquiry_keyword}")
        
#         # Only route to MenuExpert if BOTH present (explicit question)
#         if has_question_word and has_inquiry_keyword:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="MenuExpert",
#                 confidence=0.9,
#                 meta={"intent": IntentType.INQUIRY, "routing": "deterministic"}
#             )

#         # 3️⃣ 🆕 DEFAULT TO ORDERTAKER (Optimistic approach)
#         # Instead of calling LLM for ambiguous cases, assume ordering intent
#         # Let OrderTaker + Authority handle edge cases
        
#         # Explicit ordering verbs → High confidence OrderTaker
#         order_verbs = {"add", "order", "buy", "get", "want", "need", "take", "checkout"}
#         if tokens & order_verbs:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="OrderTaker",
#                 confidence=0.95,
#                 meta={"intent": IntentType.ORDERING, "routing": "deterministic"}
#             )
        
#         # 🔧 NEW BEHAVIOR: No verb, no question → Still go to OrderTaker
#         # Examples: "Truffle Pizza", "pepperoni", "2 beers"
#         # OrderTaker will be optimistic, Authority will validate
#         return ActionRequest(
#             action_type=ActionType.TRANSFER,
#             target_agent="OrderTaker",
#             confidence=0.7,  # Lower confidence but still OrderTaker
#             meta={"intent": IntentType.ORDERING, "routing": "default_optimistic"}
#         )
    





# gemini gives the claud verson with fixes (testing)
# aiva/agents/router.py
# import string
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.validation.schemas import ActionRequest, ActionType, IntentType

# class IntentRouter:
#     """
#     🔧 STEP 11: Simplified router - defaults to OrderTaker for optimistic handling.
#     Now includes punctuation stripping for robust deterministic matching.
#     """
#     ALLOWED_AGENTS = {"Greeter", "OrderTaker", "MenuExpert"}

#     def __init__(self):
#         self.prompt_path = "aiva/llm/prompts/router.md"

#     def _load_prompt(self, active_agent: str) -> str:
#         with open(self.prompt_path, "r") as f:
#             template = f.read()
#         return template.replace("{{ACTIVE_AGENT}}", active_agent)

#     def route(self, user_input: str, active_agent: str) -> ActionRequest:
#         # 🔧 Fix: Strip punctuation to handle "menu?" or "thanks!"
#         text = user_input.lower().strip()
#         text_clean = text.translate(str.maketrans('', '', string.punctuation))
#         tokens = set(text_clean.split())

#         # ═══════════════════════════════════════════════════════════
#         # DETERMINISTIC ROUTING (Fast, No LLM)
#         # ═══════════════════════════════════════════════════════════

#         # 1️⃣ Greetings/Farewells
#         if text_clean in {"hi", "hello", "hey", "bye", "thanks", "thank you"}:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="Greeter",
#                 confidence=1.0,
#                 meta={"intent": IntentType.GREETING, "routing": "deterministic"}
#             )

#         # 2️⃣ Explicit Menu Questions
#         question_words = {"what", "which", "how", "does", "is", "are", "can", "tell", "show"}
#         inquiry_keywords = {"menu", "price", "cost", "spicy", "ingredient", "allergy", "contain", "have"}
        
#         has_question_word = bool(tokens & question_words)
#         has_inquiry_keyword = bool(tokens & inquiry_keywords)
        
#         if has_question_word and has_inquiry_keyword:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="MenuExpert",
#                 confidence=0.9,
#                 meta={"intent": IntentType.INQUIRY, "routing": "deterministic"}
#             )

#         # 3️⃣ DEFAULT TO ORDERTAKER (Optimistic)
#         order_verbs = {"add", "order", "buy", "get", "want", "need", "take", "checkout"}
#         if tokens & order_verbs:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="OrderTaker",
#                 confidence=0.95,
#                 meta={"intent": IntentType.ORDERING, "routing": "deterministic"}
#             )
        
#         return ActionRequest(
#             action_type=ActionType.TRANSFER,
#             target_agent="OrderTaker",
#             confidence=0.7,
#             meta={"intent": IntentType.ORDERING, "routing": "default_optimistic"}
#         )




# # DineFlow/agents/router.py

# import string
# import logging
# from llm.client import call_llm
# from llm.response_parser import parse_action
# from validation.schemas import ActionRequest, ActionType, IntentType

# logger = logging.getLogger(__name__)

# class IntentRouter:
#     """
#     ⚖️ SCALABLE ENTERPRISE ROUTER (v1.5 — PRODUCTION HARDENED)
#     """

#     GREETINGS = {"hi", "hello", "hey", "bye", "thanks", "thank you"}
#     STRONG_ORDER_VERBS = {"add", "order", "buy", "checkout"}

#     def __init__(self):
#         self.prompt_path = "llm/prompts/router.md"

#     def _load_prompt(self, active_agent: str) -> str:
#         with open(self.prompt_path, "r") as f:
#             template = f.read()
#         return template.replace("{{ACTIVE_AGENT}}", active_agent)

#     def route(self, user_input: str, active_agent: str) -> ActionRequest:
#         text = user_input.lower().strip()
#         text_clean = text.translate(str.maketrans('', '', string.punctuation))
#         tokens = set(text_clean.split())

#         # 1️⃣ TIER 1: DETERMINISTIC (Fast/Free)
#         if text_clean in self.GREETINGS:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="Greeter",
#                 intent=IntentType.GREETING,
#                 confidence=1.0,
#                 meta={"routing": "deterministic:greeting"}
#             )

#         if tokens & self.STRONG_ORDER_VERBS:
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="OrderTaker",
#                 intent=IntentType.ORDERING,
#                 confidence=0.95,
#                 meta={"routing": "deterministic:order"}
#             )

#         # 2️⃣ TIER 2: LLM FALLBACK (Resilient/Hardened)
#         try:
#             system_prompt = self._load_prompt(active_agent)
#             raw_output = call_llm(system_prompt, user_input)
#             parsed = parse_action(raw_output)

#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent=parsed.target_agent or "OrderTaker",
#                 intent=parsed.intent or IntentType.ORDERING,
#                 confidence=min(parsed.confidence or 0.7, 0.85),
#                 meta={
#                     **(parsed.meta or {}),
#                     "routing": "llm_fallback"
#                 }
#             )

#         except Exception as e:
#             # Log the full error internally for devs, but keep meta clean
#             logger.error(f"Router LLM Failure: {e}") 
            
#             return ActionRequest(
#                 action_type=ActionType.TRANSFER,
#                 target_agent="OrderTaker",
#                 intent=IntentType.ORDERING,
#                 confidence=0.5,
#                 meta={
#                     "routing": "fallback_error", 
#                     "error_type": type(e).__name__
#                 }
#             )

# DineFlow/agents/router.py

import string
import logging
from llm.client import call_llm
from llm.response_parser import parse_action
from validation.schemas import ActionRequest, ActionType, IntentType

logger = logging.getLogger(__name__)

class IntentRouter:
    """
    ⚖️ SCALABLE ENTERPRISE ROUTER (v1.5 — PRODUCTION HARDENED)
    """

    GREETINGS = {"hi", "hello", "hey", "bye", "thanks", "thank you"}

    STRONG_ORDER_VERBS = {"add", "order", "buy", "checkout"}

    # Continuation phrases that always indicate ordering intent.
    # These bypass LLM routing to prevent misclassification as greetings.
    # "same" / "same again" → repeat last item
    # "another" / "one more" → increment last item
    # These are kept separate from STRONG_ORDER_VERBS to make intent
    # explicit in routing meta for downstream logging.
    CONTINUATION_PHRASES = {"same", "another", "one more", "same again"}

    def __init__(self):
        self.prompt_path = "llm/prompts/router.md"

    def _load_prompt(self, active_agent: str) -> str:
        with open(self.prompt_path, "r") as f:
            template = f.read()
        return template.replace("{{ACTIVE_AGENT}}", active_agent)

    def route(self, user_input: str, active_agent: str) -> ActionRequest:
        text = user_input.lower().strip()
        text_clean = text.translate(str.maketrans('', '', string.punctuation))
        tokens = set(text_clean.split())

        # 1️⃣ TIER 1: DETERMINISTIC (Fast/Free)
        if text_clean in self.GREETINGS:
            return ActionRequest(
                action_type=ActionType.TRANSFER,
                target_agent="Greeter",
                intent=IntentType.GREETING,
                confidence=1.0,
                meta={"routing": "deterministic:greeting"}
            )

        if tokens & self.STRONG_ORDER_VERBS:
            return ActionRequest(
                action_type=ActionType.TRANSFER,
                target_agent="OrderTaker",
                intent=IntentType.ORDERING,
                confidence=0.95,
                meta={"routing": "deterministic:order"}
            )

        # Continuation phrases — ordering intent, always route to OrderTaker.
        # Checked after STRONG_ORDER_VERBS and GREETINGS so they don't shadow
        # explicit orders that happen to contain "same" or "another".
        if text_clean in self.CONTINUATION_PHRASES or tokens & self.CONTINUATION_PHRASES:
            return ActionRequest(
                action_type=ActionType.TRANSFER,
                target_agent="OrderTaker",
                intent=IntentType.ORDERING,
                confidence=0.95,
                meta={"routing": "deterministic:continuation"}
            )

        # 2️⃣ TIER 2: LLM FALLBACK (Resilient/Hardened)
        try:
            system_prompt = self._load_prompt(active_agent)
            raw_output = call_llm(system_prompt, user_input)
            parsed = parse_action(raw_output)

            return ActionRequest(
                action_type=ActionType.TRANSFER,
                target_agent=parsed.target_agent or "OrderTaker",
                intent=parsed.intent or IntentType.ORDERING,
                confidence=min(parsed.confidence or 0.7, 0.85),
                meta={
                    **(parsed.meta or {}),
                    "routing": "llm_fallback"
                }
            )

        except Exception as e:
            logger.error(f"Router LLM Failure: {e}")

            return ActionRequest(
                action_type=ActionType.TRANSFER,
                target_agent="OrderTaker",
                intent=IntentType.ORDERING,
                confidence=0.5,
                meta={
                    "routing": "fallback_error",
                    "error_type": type(e).__name__
                }
            )