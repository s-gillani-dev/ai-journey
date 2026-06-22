# # # final working version for step 1-4
# # aiva/orchestration/ambiguity_gate.py
# from typing import List
# from aiva.state_machine.types import SessionState, MenuItemSnapshot
# from aiva.tools.search.hybrid import hybrid_search
# from aiva.validation.schemas import ActionRequest, ActionType

# class AmbiguityGate:
#     MAX_RETRIES = 2
#     CONFIDENCE_THRESHOLD = 0.9

#     @staticmethod
#     def is_ambiguous(action: ActionRequest, menu_items: List[MenuItemSnapshot], user_input: str) -> bool:
#         # Already asking clarification
#         if action.action_type == ActionType.ASK_CLARIFICATION:
#             return True

#         # Confidence low
#         if action.confidence < AmbiguityGate.CONFIDENCE_THRESHOLD:
#             return True

#         # SKU invalid or missing
#         valid_sku = any(item.sku == action.sku for item in menu_items)
#         if not action.sku or not valid_sku:
#             return True

#         return False

#     @staticmethod
#     def top_suggestions(user_input: str, menu_items: List[MenuItemSnapshot]) -> List[str]:
#         results = hybrid_search(user_input, menu_items)
#         return [item.name for item in results[:3]]

#     @staticmethod
#     def process(session: SessionState, action: ActionRequest, menu_items: List[MenuItemSnapshot], user_input: str) -> ActionRequest:
#         ambiguous = AmbiguityGate.is_ambiguous(action, menu_items, user_input)

#         # Reset retries if new input
#         if session.last_ambiguous_intent != user_input:
#             session.ambiguous_retries = 0

#         if ambiguous:
#             session.ambiguous_retries += 1
#             session.last_ambiguous_intent = user_input

#             action.action_type = ActionType.ASK_CLARIFICATION

#             if session.ambiguous_retries >= AmbiguityGate.MAX_RETRIES:
#                 suggestions = AmbiguityGate.top_suggestions(user_input, menu_items)
#                 action.clarification_payload = f"I'm having trouble finding that. Did you mean: {', '.join(suggestions)}?"
#                 session.ambiguous_retries = 0
#             else:
#                 if not action.clarification_payload:
#                     action.clarification_payload = "Could you please clarify which item you'd like?"
#         else:
#             session.ambiguous_retries = 0
#             session.last_ambiguous_intent = None

#         return action






# aiva/orchestration/ambiguity_gate.py
# from typing import List
# from aiva.state_machine.types import SessionState, MenuItemSnapshot
# from aiva.tools.search.hybrid import hybrid_search
# from aiva.validation.schemas import ActionRequest, ActionType

# class AmbiguityGate:
#     MAX_RETRIES = 2
#     CONFIDENCE_THRESHOLD = 0.9

#     @staticmethod
#     def is_ambiguous(action: ActionRequest, menu_items: List[MenuItemSnapshot], user_input: str) -> bool:
#         if action.action_type == ActionType.ASK_CLARIFICATION:
#             return True

#         if action.confidence < AmbiguityGate.CONFIDENCE_THRESHOLD:
#             return True

#         valid_sku = any(item.sku == action.sku for item in menu_items)
#         if not action.sku or not valid_sku:
#             return True

#         return False

#     @staticmethod
#     def top_suggestions(user_input: str, menu_items: List[MenuItemSnapshot], bm25_engine: any) -> List[str]:
#         # UPDATED: Now passes the bm25_engine required by the new hybrid_search
#         results = hybrid_search(user_input, menu_items, bm25_engine)
#         return [item.name for item in results[:3]]

#     @staticmethod
#     def process(
#         session: SessionState, 
#         action: ActionRequest, 
#         menu_items: List[MenuItemSnapshot], 
#         user_input: str,
#         bm25_engine: any  # NEW: Must pass the engine down from the golden_loop
#     ) -> ActionRequest:
#         ambiguous = AmbiguityGate.is_ambiguous(action, menu_items, user_input)

#         if session.last_ambiguous_intent != user_input:
#             session.ambiguous_retries = 0

#         if ambiguous:
#             session.ambiguous_retries += 1
#             session.last_ambiguous_intent = user_input
#             action.action_type = ActionType.ASK_CLARIFICATION

#             if session.ambiguous_retries >= AmbiguityGate.MAX_RETRIES:
#                 # UPDATED: Pass bm25_engine to get accurate fallback suggestions
#                 suggestions = AmbiguityGate.top_suggestions(user_input, menu_items, bm25_engine)
#                 action.clarification_payload = f"I'm having trouble finding that. Did you mean: {', '.join(suggestions)}?"
#                 session.ambiguous_retries = 0
#             else:
#                 if not action.clarification_payload:
#                     action.clarification_payload = "Could you please clarify which item you'd like?"
#         else:
#             session.ambiguous_retries = 0
#             session.last_ambiguous_intent = None

#         return action



# # aiva/orchestration/ambiguity_gate.py
# from typing import List
# from aiva.state_machine.types import SessionState, MenuItemSnapshot
# from aiva.tools.search.hybrid import hybrid_search
# from aiva.validation.schemas import ActionRequest, ActionType

# class AmbiguityGate:
#     MAX_RETRIES = 2
#     CONFIDENCE_THRESHOLD = 0.9

#     @staticmethod
#     def is_ambiguous(action: ActionRequest, menu_items: List[MenuItemSnapshot], user_input: str) -> bool:
#         # 1. If the LLM *intentionally* asked a question, it's NOT a system failure.
#         # This allows the LLM to have a conversation without the retry counter going up.
#         if action.action_type == ActionType.ASK_CLARIFICATION and action.confidence >= AmbiguityGate.CONFIDENCE_THRESHOLD:
#             return False

#         # 2. Low confidence is a failure.
#         if action.confidence < AmbiguityGate.CONFIDENCE_THRESHOLD:
#             return True

#         # 3. Invalid SKUs are a failure.
#         requires_sku = action.action_type in {ActionType.ADD_TO_CART}
#         if requires_sku:
#             valid_sku = any(item.sku == action.sku for item in menu_items)
#             if not action.sku or not valid_sku:
#                 return True

#         return False

#     @staticmethod
#     def top_suggestions(user_input: str, menu_items: List[MenuItemSnapshot], bm25_engine: any) -> List[str]:
#         results = hybrid_search(user_input, menu_items, bm25_engine)
#         return [item.name for item in results[:3]]

#     @staticmethod
#     def process(
#         session: SessionState, 
#         action: ActionRequest, 
#         menu_items: List[MenuItemSnapshot], 
#         user_input: str,
#         bm25_engine: any 
#     ) -> ActionRequest:
#         ambiguous = AmbiguityGate.is_ambiguous(action, menu_items, user_input)

#         # FIXED: We no longer reset retries to 0 just because the user changed their words.
#         # We only reset if the loop successfully resolves an intent (is NOT ambiguous).

#         if ambiguous:
#             session.ambiguous_retries += 1
#             session.last_ambiguous_intent = user_input
#             action.action_type = ActionType.ASK_CLARIFICATION

#             if session.ambiguous_retries >= AmbiguityGate.MAX_RETRIES:
#                 # Use RRF Hybrid Search to find what the user likely wants
#                 suggestions = AmbiguityGate.top_suggestions(user_input, menu_items, bm25_engine)
                
#                 if suggestions:
#                     action.clarification_payload = f"I'm having trouble finding that. Did you mean: {', '.join(suggestions)}?"
#                 else:
#                     action.clarification_payload = "I'm sorry, I couldn't find anything like that on our menu. Could you try a different name?"
                
#                 # Reset after escalation to prevent an infinite suggestion loop
#                 session.ambiguous_retries = 0
#             else:
#                 # If LLM didn't provide a specific question, use a default
#                 if not action.clarification_payload:
#                     action.clarification_payload = "Could you please clarify which item you'd like?"
#         else:
#             # SUCCESS: Reset retries only when the intent is clear and valid
#             session.ambiguous_retries = 0
#             session.last_ambiguous_intent = None

#         return action


# DineFlow/orchestration/ambiguity_gate.py
from typing import List
from state_machine.types import SessionState, MenuItemSnapshot
from tools.search.hybrid import hybrid_search
from validation.schemas import ActionRequest, ActionType

class AmbiguityGate:
    """
    🔧 STEP 11: Simplified to only handle retry counting.
    Validation logic moved to Authority.
    """
    MAX_RETRIES = 2

    @staticmethod
    def top_suggestions(user_input: str, menu_items: List[MenuItemSnapshot], bm25_engine: any) -> List[str]:
        """Get top 3 menu suggestions."""
        results = hybrid_search(user_input, menu_items, bm25_engine)
        return [item.name for item in results[:3]]

    @staticmethod
    def process(
        session: SessionState, 
        action: ActionRequest, 
        menu_items: List[MenuItemSnapshot], 
        user_input: str,
        bm25_engine: any 
    ) -> ActionRequest:
        """
        Lightweight retry counter. 
        Authority handles validation, this just tracks escalation.
        """
        
        # If it's already a clarification request, increment retries
        if action.action_type == ActionType.ASK_CLARIFICATION:
            session.ambiguous_retries += 1
            session.last_ambiguous_intent = user_input
            
            # After MAX_RETRIES, provide suggestions
            if session.ambiguous_retries >= AmbiguityGate.MAX_RETRIES:
                suggestions = AmbiguityGate.top_suggestions(user_input, menu_items, bm25_engine)
                
                if suggestions:
                    action.clarification_payload = f"I'm having trouble finding that. Did you mean: {', '.join(suggestions)}?"
                else:
                    action.clarification_payload = "I'm sorry, I couldn't find anything like that on our menu. Could you try a different name?"
                
                # Reset after escalation
                session.ambiguous_retries = 0
        else:
            # Success - reset retries
            session.ambiguous_retries = 0
            session.last_ambiguous_intent = None

        return action



# ```

# ---

# ## 🧪 Expected Behavior After Step 11:

# ### **Test Case 1: "add 3 pepperoni pizzas"**
# ```
# Router → OrderTaker
# OrderTaker LLM → Tries ADD_TO_CART with SKU: PZ-PEP
# Authority → Checks SKU exists ✅, quantity > 0 ✅, confidence OK ✅
# Result → APPROVED ✅
# Response: "Excellent choice! I've added 3 Pepperoni Pizza to your order."
# ```

# ### **Test Case 2: "add 3 pizzas" (ambiguous)**
# ```
# Router → OrderTaker
# OrderTaker LLM → Tries ADD_TO_CART but can't determine SKU (returns null)
# Authority → Detects no SKU, checks if category ambiguity
# Authority → Finds "pizza" matches 3 items
# Result → RECOVERABLE, requires_clarification=True
# Golden Loop → Converts to ASK_CLARIFICATION
# Response: "Which pizza would you like? We have: Pepperoni Pizza ($12.99), ..."
# ```

# ### **Test Case 3: "Truffle Pizza" (no verb)**
# ```
# Router → Routes to OrderTaker (simplified routing)
# OrderTaker → Optimistically tries ADD_TO_CART with PZ-FANCY
# Authority → Checks all rules ✅
# Result → APPROVED ✅
# Response: "Excellent choice! I've added Fancy Truffle Pizza to your order."