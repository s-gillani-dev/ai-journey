# aiva/agents/order_taker.py
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.orchestration.helpers import load_order_taker_prompt, render_menu_context
# from aiva.orchestration.ambiguity_gate import AmbiguityGate
# from aiva.tools.search.hybrid import hybrid_search
# from aiva.validation.schemas import ActionRequest, ActionType

# class OrderTakerAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         # Improvement 1: Store immutable snapshots
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         # 1️⃣ HYBRID SEARCH (Get candidate set)
#         relevant_menu_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
#         menu_string = render_menu_context(menu_items=relevant_menu_items)
        
#         # 2️⃣ MEMORY & 3️⃣ PROMPT
#         history_str = memory.get_context(user_input)
#         prompt_template = load_order_taker_prompt()
#         system_prompt = prompt_template.replace("{{MENU_CONTEXT}}", menu_string).replace("{{CHAT_HISTORY}}", history_str)

#         # 4️⃣ LLM REASONING
#         raw_output = call_llm(system_prompt, user_input)
#         action = parse_action(raw_output)

#         # Improvement 3: Defensive Contract Check (Prevent prompt drift)
#         if action.action_type == ActionType.TRANSFER:
#             raise ValueError("OrderTakerAgent contract violation: Emitted a TRANSFER action.")

#         # 5️⃣ AMBIGUITY GATE
#         # Improvement 2: Only show candidates to AmbiguityGate, not full menu
#         action = AmbiguityGate.process(
#             session=session,
#             action=action,
#             menu_items=relevant_menu_items, 
#             user_input=user_input,
#             bm25_engine=self.bm25_engine
#         )

#         return action




# # aiva/agents/order_taker.py
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.orchestration.helpers import load_order_taker_prompt, render_menu_context
# from aiva.orchestration.ambiguity_gate import AmbiguityGate
# from aiva.tools.search.hybrid import hybrid_search
# from aiva.validation.schemas import ActionRequest, ActionType

# class OrderTakerAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine
        
#         # 🔧 Pre-compute category mappings for O(1) lookup
#         self._build_category_index()

#     def _build_category_index(self):
#         """Build deterministic category patterns for cheap pre-LLM matching."""
#         self.category_patterns = {
#             "pizza": [item for item in self.all_menu_items if "pizza" in item.name.lower()],
#             "beer": [item for item in self.all_menu_items if "beer" in item.name.lower()],
#         }

#     def _check_deterministic_ambiguity(self, user_input: str) -> ActionRequest | None:
#         """
#         Pre-LLM pattern matching for common ambiguous requests.
#         Returns ActionRequest if deterministic match found, None otherwise.
#         """
#         text_lower = user_input.lower().strip()
        
#         # Pattern: "I want a [category]" or "get me a [category]"
#         for category, items in self.category_patterns.items():
#             # Check for category mention with ordering intent
#             if category in text_lower and any(
#                 verb in text_lower for verb in ["want", "get", "order", "add", "buy"]
#             ):
#                 # Only trigger if there are multiple options
#                 if len(items) > 1:
#                     options = ", ".join([
#                         f"{item.name} (${item.price})" for item in items
#                     ])
#                     return ActionRequest(
#                         action_type=ActionType.ASK_CLARIFICATION,
#                         sku=None,
#                         confidence=0.8,
#                         clarification_payload=f"Which {category} would you like? We have: {options}",
#                         meta={"optimization": "deterministic_ambiguity", "category": category}
#                     )
                
#                 # If only one item, skip to LLM for proper ADD_TO_CART
#                 # (LLM will handle quantity, notes, etc.)
        
#         return None

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         # 🔧 NEW: Deterministic ambiguity check (pre-LLM)
#         deterministic_result = self._check_deterministic_ambiguity(user_input)
#         if deterministic_result:
#             return deterministic_result
        
#         # 1️⃣ HYBRID SEARCH (Get candidate set)
#         relevant_menu_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
#         menu_string = render_menu_context(menu_items=relevant_menu_items)
        
#         # 2️⃣ MEMORY & 3️⃣ PROMPT
#         history_str = memory.get_context(user_input)
#         print("history_str using get_context-----------------", history_str)
#         prompt_template = load_order_taker_prompt()
#         system_prompt = prompt_template.replace("{{MENU_CONTEXT}}", menu_string).replace("{{CHAT_HISTORY}}", history_str)

#         # 4️⃣ LLM REASONING
#         raw_output = call_llm(system_prompt, user_input)
#         action = parse_action(raw_output)

#         # Improvement 3: Defensive Contract Check (Prevent prompt drift)
#         if action.action_type == ActionType.TRANSFER:
#             raise ValueError("OrderTakerAgent contract violation: Emitted a TRANSFER action.")

#         # 5️⃣ AMBIGUITY GATE
#         action = AmbiguityGate.process(
#             session=session,
#             action=action,
#             menu_items=relevant_menu_items, 
#             user_input=user_input,
#             bm25_engine=self.bm25_engine
#         )

#         return action



# Claud give this version
# aiva/agents/order_taker.py
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.orchestration.helpers import load_order_taker_prompt, render_menu_context
# from aiva.orchestration.ambiguity_gate import AmbiguityGate
# from aiva.tools.search.hybrid import hybrid_search
# from aiva.validation.schemas import ActionRequest, ActionType

# class OrderTakerAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         # 🔧 STEP 11: Removed _check_deterministic_ambiguity()
#         # OrderTaker is now OPTIMISTIC - tries to fulfill, Authority judges
        
#         # 1️⃣ HYBRID SEARCH (Get candidate set)
#         relevant_menu_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
#         menu_string = render_menu_context(menu_items=relevant_menu_items)
        
#         # 2️⃣ MEMORY & 3️⃣ PROMPT
#         history_str = memory.get_context(user_input)
#         prompt_template = load_order_taker_prompt()
#         system_prompt = prompt_template.replace("{{MENU_CONTEXT}}", menu_string).replace("{{CHAT_HISTORY}}", history_str)

#         # 4️⃣ LLM REASONING
#         raw_output = call_llm(system_prompt, user_input)
#         action = parse_action(raw_output)

#         # Contract Check (Prevent prompt drift)
#         if action.action_type == ActionType.TRANSFER:
#             raise ValueError("OrderTakerAgent contract violation: Emitted a TRANSFER action.")

#         # 5️⃣ AMBIGUITY GATE (Keep for retry logic, but simplified)
#         action = AmbiguityGate.process(
#             session=session,
#             action=action,
#             menu_items=relevant_menu_items, 
#             user_input=user_input,
#             bm25_engine=self.bm25_engine
#         )

#         return action
    



# # gemini gives the claud verson with fixes (testing)
# # DineFlow/agents/order_taker.py
# from llm.client import call_llm
# from llm.response_parser import parse_action
# from orchestration.helpers import load_order_taker_prompt, render_menu_context
# from tools.search.hybrid import hybrid_search
# from validation.schemas import ActionRequest, ActionType

# class OrderTakerAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         """
#         🔧 STEP 11: Optimized OrderTaker.
#         Internal ambiguity logic removed. Agent suggests, Authority validates.
#         """
        
#         # 1️⃣ HYBRID SEARCH (Context Retrieval)
#         relevant_menu_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
#         menu_string = render_menu_context(menu_items=relevant_menu_items)
        
#         # 2️⃣ CONTEXT PREPARATION
#         history_str = memory.get_context(user_input)
#         prompt_template = load_order_taker_prompt()
#         system_prompt = prompt_template.replace("{{MENU_CONTEXT}}", menu_string).replace("{{CHAT_HISTORY}}", history_str)

#         # 3️⃣ LLM INFERENCE
#         raw_output = call_llm(system_prompt, user_input)
#         action = parse_action(raw_output)

#         # 4️⃣ CONTRACT ENFORCEMENT
#         if action.action_type == ActionType.TRANSFER:
#             # OrderTaker cannot decide to transfer; that is the Router's job.
#             action.action_type = ActionType.NO_OP
#             action.message = "I'm sorry, I'm having trouble processing that request."

#         # 🔧 Note: AmbiguityGate.process() removed. 
#         # Authority in golden_loop.py now handles the check for missing/ambiguous SKUs.
        
#         return action



# claud recent version testing....

# # DineFlow/agents/order_taker.py
# from llm.client import call_llm
# from llm.response_parser import parse_action
# from orchestration.helpers import load_order_taker_prompt, render_menu_context
# from tools.search.hybrid import hybrid_search
# from validation.schemas import ActionRequest, ActionType


# class OrderTakerAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         """
#         Converts user ordering intent into a structured ActionRequest.

#         Context assembly has two modes based on whether the current input
#         is a response to a pending clarification:

#         ── Normal turn ────────────────────────────────────────────────────────
#             hybrid_search(user_input) → top-k relevant items
#             get_context(user_input)   → standard window + past facts

#         ── Clarification response ("yes", "add this", "sure") ────────────────
#             FULL CATALOG              → LLM must see all SKUs so it can
#                                         resolve the item from the hint
#             get_context_with_clarification_hint() → prepends PENDING block
#                                         so LLM knows what it asked and
#                                         how to interpret the confirmation

#             Why full catalog here:
#                 hybrid_search("add this") or hybrid_search("yes") returns
#                 near-zero scores — no menu tokens. The LLM receives poor
#                 candidate items and cannot find the SKU it needs even though
#                 the clarification hint correctly identifies the item by name.
#                 Full catalog guarantees the SKU is visible in the prompt.
#         """

#         # 1. DETECT CLARIFICATION RESPONSE — before search
#         pending = memory.pending_clarification()

#         # 2. MENU CONTEXT — scope depends on clarification state
#         if pending:
#             # Full catalog: the hint names the item, the LLM needs to see
#             # its SKU. Filtered search on "yes" / "add this" would miss it.
#             relevant_menu_items = self.all_menu_items
#         else:
#             # Standard path: search for the most relevant items
#             relevant_menu_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)

#         menu_string = render_menu_context(menu_items=relevant_menu_items, include_skus=True)

#         # 3. HISTORY CONTEXT — clarification-aware assembly
#         # get_context_with_clarification_hint() prepends the PENDING block
#         # when pending is not None, returns standard context otherwise.
#         # No branching needed by the caller.
#         history_str = memory.get_context_with_clarification_hint(user_input)

#         # 4. PROMPT CONSTRUCTION
#         prompt_template = load_order_taker_prompt()
#         system_prompt = (
#             prompt_template
#             .replace("{{MENU_CONTEXT}}", menu_string)
#             .replace("{{CHAT_HISTORY}}", history_str)
#         )

#         # 5. LLM INFERENCE
#         raw_output = call_llm(system_prompt, user_input)
#         action = parse_action(raw_output)

#         # 6. CONTRACT ENFORCEMENT
#         # OrderTaker cannot decide to transfer — that is the Router's job.
#         if action.action_type == ActionType.TRANSFER:
#             action.action_type = ActionType.NO_OP
#             action.message = "I'm sorry, I'm having trouble processing that request."

#         return action



# DineFlow/agents/order_taker.py
from llm.client import call_llm
from llm.response_parser import parse_action
from orchestration.helpers import load_order_taker_prompt, render_menu_context, resolve_menu_item
from tools.search.hybrid import hybrid_search
from validation.schemas import ActionRequest, ActionType


class OrderTakerAgent:
    def __init__(self, all_menu_items: list, bm25_engine):
        self.all_menu_items = all_menu_items
        self.bm25_engine = bm25_engine

    def run(self, user_input: str, session, memory) -> ActionRequest:
        """
        Converts user ordering intent into a structured ActionRequest.

        Context assembly has three modes:

        ── Clarification response ("yes", "add this", "sure") ────────────────
            Full catalog + clarification hint block.
            The hint names the pending SKU explicitly so the LLM only needs
            to confirm or deny — no inference required.

        ── Focus response ("2", "another", "one more") ───────────────────────
            Hybrid search + focus item latched into results + focus block.
            The focus block tells the LLM which item is currently "active"
            and classifies the input signal (quantity update / repeat / etc).
            The LLM decides whether to apply it — safe against false positives.

        ── Normal turn ────────────────────────────────────────────────────────
            Hybrid search + standard context.
        """

        # 1. DETECT CLARIFICATION RESPONSE — highest priority, check first
        pending = memory.pending_clarification()

        # 2. MENU CONTEXT
        if pending:
            # Full catalog: the hint names the item, LLM needs to see its SKU.
            relevant_menu_items = self.all_menu_items
        else:
            # Hybrid search for relevant items
            relevant_menu_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)

            # FOCUS ITEM LATCHING
            # If session has a last_action_sku (focus item), ensure it is always
            # visible in the menu context even if hybrid_search("2") returns nothing
            # useful. Without this, the LLM cannot resolve the SKU from the focus block.
            if session.last_action_sku:
                focus_item = resolve_menu_item(self.all_menu_items, session.last_action_sku)
                if focus_item and focus_item not in relevant_menu_items:
                    relevant_menu_items = list(relevant_menu_items) + [focus_item]

        menu_string = render_menu_context(menu_items=relevant_menu_items, include_skus=True)

        # 3. HISTORY CONTEXT — clarification-aware + focus-aware
        history_str = memory.get_context_with_clarification_hint(user_input)

        # 4. FOCUS BLOCK — prepended to history so LLM reads it first
        # Returns empty string if no focus SKU is set — no branching needed.
        focus_block = memory.get_focus_block(session, self.all_menu_items, user_input)
        combined_history = focus_block + history_str

        # 5. PROMPT CONSTRUCTION
        prompt_template = load_order_taker_prompt()
        system_prompt = (
            prompt_template
            .replace("{{MENU_CONTEXT}}", menu_string)
            .replace("{{CHAT_HISTORY}}", combined_history)
        )

        # 6. LLM INFERENCE
        raw_output = call_llm(system_prompt, user_input)
        action = parse_action(raw_output)

        # 7. CONTRACT ENFORCEMENT
        # OrderTaker cannot decide to transfer — that is the Router's job.
        if action.action_type == ActionType.TRANSFER:
            action.action_type = ActionType.NO_OP
            action.message = "I'm sorry, I'm having trouble processing that request."

        return action