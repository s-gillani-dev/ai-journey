# # aiva/agents/menu_expert.py
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.orchestration.helpers import render_menu_context
# from aiva.tools.search.hybrid import hybrid_search
# from aiva.validation.schemas import ActionRequest, ActionType
# from aiva.state_machine.types import ContextScope

# class MenuExpertAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine
#         self.prompt_path = "aiva/llm/prompts/menu_expert.md"

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         # 🔧 Improvement 1: Cheap Guard (Skip search for very short inputs)
#         # 🔧 Improvement 5: Cap results at 3 to prevent hallucination

#         relevant_items = []
#         if session.context_scope == ContextScope.FULL_CATALOG:
#             relevant_items = self.all_menu_items

#         elif session.context_scope == "FILTERED":
#             relevant_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
#             relevant_items = relevant_items[:3]

#         menu_string = render_menu_context(menu_items=relevant_items)
#         history_str = memory.get_context(user_input, limit=3)

#         with open(self.prompt_path, "r") as f:
#             system_prompt = f.read()
        
#         full_prompt = f"{system_prompt}\n\nMENU_CONTEXT:\n{menu_string}\n\nHISTORY:\n{history_str}"

#         raw_output = call_llm(full_prompt, user_input)
#         action = parse_action(raw_output)

#         # 🔧 Improvement 4: Defensive Contract Freeze
#         # 🔧 Improvement 2: Remove clarification_payload fallback
#         # 🔧 Improvement 7: Observability Metadata
#         final_action = ActionRequest(
#             action_type=ActionType.NO_OP,
#             message=action.message or "I can definitely help you with our menu. What would you like to know?",
#             meta={"agent": "MenuExpert", "mode": "read_only"},
#             confidence=1.0
#         )

#         assert final_action.action_type == ActionType.NO_OP, "MenuExpert Security Violation"
#         return final_action






# # DineFlow/agents/menu_expert.py
# from llm.client import call_llm
# from llm.response_parser import parse_action
# from orchestration.helpers import render_menu_context
# from tools.search.hybrid import hybrid_search
# from validation.schemas import ActionRequest, ActionType
# from state_machine.types import ContextScope

# class MenuExpertAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine
#         self.prompt_path = "llm/prompts/menu_expert.md"

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         """
#         ⚖️ SYSTEMIC AGENT: Operates based on Authority-granted scope.
#         """
#         # 1. DATA RETRIEVAL: Respect the systemic 'Permit' granted by Authority
#         relevant_items = []
        
#         if session.context_scope == ContextScope.FULL_CATALOG:
#             # Authority authorized full access (e.g., "What's on the menu?")
#             relevant_items = self.all_menu_items
#         else:
#             # Default to limited search (e.g., "Tell me about the truffle pizza")
#             relevant_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
#             relevant_items = relevant_items[:5] # Slightly higher cap for better variety

#         # 2. CONTEXT PREPARATION
#         menu_string = render_menu_context(menu_items=relevant_items)
#         history_str = memory.get_context(user_input, limit=3)

#         # 3. PROMPT CONSTRUCTION
#         with open(self.prompt_path, "r") as f:
#             system_prompt_template = f.read()
        
#         # Systemic Fix: Replace the placeholder {{MENU_CONTEXT}} in the .md file
#         # If you just append to the end, the LLM might miss it.
#         system_prompt = system_prompt_template.replace("{{MENU_CONTEXT}}", menu_string)
        
#         full_prompt = f"{system_prompt}\n\nHISTORY:\n{history_str}"

#         # 4. LLM INFERENCE
#         raw_output = call_llm(full_prompt, user_input)
#         action = parse_action(raw_output)

#         # 5. DEFENSIVE CONTRACT FREEZE
#         # Ensure MenuExpert NEVER attempts a mutation (Security Layer)
#         return ActionRequest(
#             action_type=ActionType.NO_OP,
#             message=action.message or "I'm the Menu Expert. How can I help you discover our dishes?",
#             meta={
#                 "agent": "MenuExpert", 
#                 "scope_used": session.context_scope,
#                 "items_count": len(relevant_items)
#             },
#             confidence=action.confidence or 0.9
#         )




# claud recent version testing...


# DineFlow/agents/menu_expert.py
# from pathlib import Path
# from llm.client import call_llm
# from llm.response_parser import parse_action
# from orchestration.helpers import render_menu_context
# from tools.search.hybrid import hybrid_search
# from validation.schemas import ActionRequest, ActionType
# from state_machine.types import ContextScope


# class MenuExpertAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine
#         # Absolute path resolution — immune to working directory differences
#         # between running via CLI, gunicorn, or pytest
#         self.prompt_path = Path(__file__).parent.parent / "llm" / "prompts" / "menu_expert.md"

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         """
#         ⚖️ SYSTEMIC AGENT: Operates based on Authority-granted scope.

#         This agent is intentionally passive about scope — it does NOT decide
#         whether to use FULL_CATALOG or FILTERED_SEARCH. That decision was made
#         by the QueryClassifier in Authority before this method was called, and
#         is already set on session.context_scope.

#         The agent's only job here is to OBEY that decision, not re-evaluate it.
#         """

#         # 1️⃣ DATA RETRIEVAL — Respect the scope permit granted by Authority
#         if session.context_scope == ContextScope.FULL_CATALOG:
#             # Authority authorized full catalog access.
#             # Covers: attribute queries ("anything spicy?"), broad inquiries
#             # ("what's on the menu?"), and ambiguous queries (safe default).
#             relevant_items = self.all_menu_items
#         else:
#             # FILTERED_SEARCH: user referenced a specific item by name.
#             # hybrid_search will find it precisely — no need for full catalog.
#             relevant_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
#             relevant_items = relevant_items[:5]  # Cap for prompt size control

#         # 2️⃣ CONTEXT PREPARATION
#         # render_menu_context now includes description and tags per item,
#         # giving the LLM the semantic surface it needs to answer attribute questions.
#         menu_string = render_menu_context(menu_items=relevant_items)
#         history_str = memory.get_context(user_input, limit=3)

#         # 3️⃣ PROMPT CONSTRUCTION
#         system_prompt_template = self.prompt_path.read_text(encoding="utf-8")

#         # Replace {{MENU_CONTEXT}} inline — appending to the end of the prompt
#         # causes the LLM to weight it less. Inline injection keeps it anchored
#         # to the instruction that references it.
#         system_prompt = system_prompt_template.replace("{{MENU_CONTEXT}}", menu_string)
#         full_prompt = f"{system_prompt}\n\nHISTORY:\n{history_str}"

#         # 4️⃣ LLM INFERENCE
#         raw_output = call_llm(full_prompt, user_input)
#         action = parse_action(raw_output)

#         # 5️⃣ DEFENSIVE CONTRACT FREEZE
#         # MenuExpert is constitutionally read-only. Even if the LLM hallucinates
#         # an ADD_TO_CART action, this layer overwrites it with NO_OP.
#         # This is a hard security boundary, not a soft guideline.
#         return ActionRequest(
#             action_type=ActionType.NO_OP,
#             message=action.message or "I'm the Menu Expert. How can I help you discover our dishes?",
#             meta={
#                 "agent": "MenuExpert",
#                 "scope_used": session.context_scope,
#                 "items_retrieved": len(relevant_items),
#                 # Surface whether context was empty — useful for debugging
#                 # future knowledge gaps without re-running the full loop
#                 "context_was_empty": len(relevant_items) == 0,
#             },
#             confidence=action.confidence or 0.9
#         )

# new fix
# # DineFlow/agents/menu_expert.py
# from pathlib import Path
# from llm.client import call_llm
# from llm.response_parser import parse_action
# from orchestration.helpers import render_menu_context
# from tools.search.hybrid import hybrid_search
# from validation.schemas import ActionRequest, ActionType
# from state_machine.types import ContextScope


# class MenuExpertAgent:
#     def __init__(self, all_menu_items: list, bm25_engine):
#         self.all_menu_items = all_menu_items
#         self.bm25_engine = bm25_engine
#         self.prompt_path = Path(__file__).parent.parent / "llm" / "prompts" / "menu_expert.md"

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         """
#         ⚖️ SYSTEMIC AGENT: Operates based on Authority-granted scope.

#         Uses render_menu_context(include_skus=False) — the default — because
#         MenuExpert is read-only and must never expose internal identifiers.
#         """

#         # 1️⃣ DATA RETRIEVAL — respect the scope permit granted by Authority
#         if session.context_scope == ContextScope.FULL_CATALOG:
#             relevant_items = self.all_menu_items
#         else:
#             relevant_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
#             relevant_items = relevant_items[:5]

#         # 2️⃣ CONTEXT PREPARATION
#         # include_skus=False (default): MenuExpert answers questions about the
#         # menu but never produces SKU values. Omitting them keeps the prompt
#         # clean and prevents the LLM from leaking internal identifiers to users.
#         menu_string = render_menu_context(menu_items=relevant_items, include_skus=False)
#         history_str = memory.get_context(user_input, limit=3)

#         # 3️⃣ PROMPT CONSTRUCTION
#         system_prompt_template = self.prompt_path.read_text(encoding="utf-8")
#         system_prompt = system_prompt_template.replace("{{MENU_CONTEXT}}", menu_string)
#         full_prompt = f"{system_prompt}\n\nHISTORY:\n{history_str}"

#         # 4️⃣ LLM INFERENCE
#         raw_output = call_llm(full_prompt, user_input)
#         action = parse_action(raw_output)

#         # 5️⃣ DEFENSIVE CONTRACT FREEZE
#         return ActionRequest(
#             action_type=ActionType.NO_OP,
#             message=action.message or "I'm the Menu Expert. How can I help you discover our dishes?",
#             meta={
#                 "agent": "MenuExpert",
#                 "scope_used": session.context_scope,
#                 "items_retrieved": len(relevant_items),
#                 "context_was_empty": len(relevant_items) == 0,
#             },
#             confidence=action.confidence or 0.9
#         )


# DineFlow/agents/menu_expert.py
from pathlib import Path
from llm.client import call_llm
from llm.response_parser import parse_action
from orchestration.helpers import render_menu_context
from tools.search.hybrid import hybrid_search
from validation.schemas import ActionRequest, ActionType
from state_machine.types import ContextScope


class MenuExpertAgent:
    def __init__(self, all_menu_items: list, bm25_engine):
        self.all_menu_items = all_menu_items
        self.bm25_engine = bm25_engine
        self.prompt_path = Path(__file__).parent.parent / "llm" / "prompts" / "menu_expert.md"

    def run(self, user_input: str, session, memory) -> ActionRequest:
        """
        ⚖️ SYSTEMIC AGENT: Operates based on Authority-granted scope.

        After generating a response, marks all shown items as mentioned=True
        in session.active_context. This is the Phase 2 unlock: after the user
        browses the menu ("what's spicy?"), they can say "add that" or "the
        first one" and the SemanticResolver can resolve it correctly because
        the context graph knows what was shown.

        Context principle: we write to active_context from SYSTEM OUTPUTS —
        specifically from relevant_items that were actually shown to the user,
        not from what the user asked for.
        """

        # 1️⃣ DATA RETRIEVAL — respect the scope permit granted by Authority
        if session.context_scope == ContextScope.FULL_CATALOG:
            relevant_items = self.all_menu_items
        else:
            relevant_items = hybrid_search(user_input, self.all_menu_items, self.bm25_engine)
            relevant_items = relevant_items[:5]

        # 2️⃣ CONTEXT PREPARATION
        menu_string = render_menu_context(menu_items=relevant_items, include_skus=False)
        history_str = memory.get_context(user_input, limit=3)

        # 3️⃣ PROMPT CONSTRUCTION
        system_prompt_template = self.prompt_path.read_text(encoding="utf-8")
        system_prompt = system_prompt_template.replace("{{MENU_CONTEXT}}", menu_string)
        full_prompt = f"{system_prompt}\n\nHISTORY:\n{history_str}"

        # 4️⃣ LLM INFERENCE
        raw_output = call_llm(full_prompt, user_input)
        action = parse_action(raw_output)

        # 5️⃣ CONTEXT UPDATE — delegated to golden_loop
        # active_context is NOT written here. golden_loop owns all context writes.
        # After this agent returns, golden_loop Step 5 will call
        # _populate_context_from_response(response_text, session) which uses
        # BM25 scoring against the ACTUAL RESPONSE TEXT — only items the LLM
        # mentioned in its reply enter context, not everything that was searched.
        #
        # Why this matters:
        #   "what's spicy?" → FULL_CATALOG scope → relevant_items = all 5 items
        #   LLM response mentions only: "Pepperoni Pizza"
        #   Writing from relevant_items → all 5 enter context (WRONG)
        #   Writing from response text → only Pepperoni enters context (CORRECT)

        # 6️⃣ DEFENSIVE CONTRACT FREEZE
        return ActionRequest(
            action_type=ActionType.NO_OP,
            message=action.message or "I'm the Menu Expert. How can I help you discover our dishes?",
            meta={
                "agent": "MenuExpert",
                "scope_used": session.context_scope,
                "items_retrieved": len(relevant_items),
                "context_was_empty": len(relevant_items) == 0,
            },
            confidence=action.confidence or 0.9
        )