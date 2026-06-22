# # aiva/response/generator.py
# from typing import Optional
# from aiva.state_machine.authority import ValidationResult
# from aiva.validation.schemas import ActionType

# def generate_response(action, result: Optional[ValidationResult]) -> str:
#     # 1️ Handle Clarification payload (matches test_golden_loop_ambiguous)
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         return action.clarification_payload or "Could you please clarify that?"
    
#      # 2 Safety guard (should never happen, but defensive)
#     if result is None:
#         return "Something went wrong. Please try again."

#     # 3 Handle Rejections (matches test_golden_loop_blocked_due_to_budget)
#     if result and not result.approved:
#         # Check specifically for budget in your tests
#         if result.rejection_code == "BUDGET_EXCEEDED":
#             return "I'm having trouble processing that. Budget exceeded."
#         return f"Action blocked: {result.user_message}"
    
#     # 4 Handle Success (Make it sound premium!)
#     if action.action_type == ActionType.ADD_TO_CART:
#         return f"Excellent choice. I've added the {action.sku} to your order. Anything else?"

#     if action.action_type == ActionType.REMOVE_FROM_CART:
#         return f"No problem. I've removed that from your cart."

#     # 5 Fallback
#     return "Sure! How else can I help?"








# DineFlow/response/generator.py
from typing import Optional, List
from state_machine.authority import ValidationResult
from state_machine.types import MenuItemSnapshot
from validation.schemas import ActionType, ActionRequest


def generate_response(
    action: ActionRequest, 
    result: Optional[ValidationResult],
    menu_items: Optional[List[MenuItemSnapshot]] = None
) -> str:
    """
    Generates user-facing responses based on action and validation result.
    
    Args:
        action: The action being processed
        result: Validation result (None for short-circuit cases like ASK_CLARIFICATION)
        menu_items: Optional menu list for resolving item names
    """
    
    # 1️⃣ Handle Clarification (NO_OP short-circuit from OrderTaker)
    if action.action_type == ActionType.ASK_CLARIFICATION:
        return action.clarification_payload or "Could you please clarify that?"
    
    # 2️⃣ Safety guard (should rarely happen in production)
    if result is None:
        return "Something went wrong. Please try again."

    # 3️⃣ Handle Rejections
    if not result.approved:  # 🔧 FIX: Removed redundant 'result and'
        if result.rejection_code == "BUDGET_EXCEEDED":
            return "I'm having trouble processing that. Budget exceeded."
        
        # Use user_message if available, otherwise fallback to rejection_code
        return result.user_message or f"Action blocked: {result.rejection_code}"
    
    # 4️⃣ Handle Success Cases
    if action.action_type == ActionType.ADD_TO_CART:
        # 🔧 FIX: Resolve item name for better UX
        item_name = _resolve_item_name(action.sku, menu_items)
        qty = action.quantity or 1
        
        if qty > 1:
            return f"Excellent choice! I've added {qty} {item_name} to your order. Anything else?"
        return f"Excellent choice! I've added {item_name} to your order. Anything else?"

    if action.action_type == ActionType.REMOVE_FROM_CART:
        item_name = _resolve_item_name(action.sku, menu_items)
        return f"No problem. I've removed {item_name} from your cart."
    
    if action.action_type == ActionType.MODIFY_ITEM:
        item_name = _resolve_item_name(action.sku, menu_items)
        return f"Got it! I've updated {item_name} in your order."
    
    if action.action_type == ActionType.CHECKOUT:
        return "Perfect! Let me process your order."

    # 5️⃣ Fallback for other action types
    return "Action executed successfully!"


def _resolve_item_name(sku: Optional[str], menu_items: Optional[List[MenuItemSnapshot]]) -> str:
    """
    Helper to resolve SKU to human-readable name.
    Falls back to SKU if menu_items not provided.
    """
    if not sku:
        return "that item"
    
    if not menu_items:
        return sku  # Fallback to SKU if menu not available
    
    # Find the item
    item = next((item for item in menu_items if item.sku.upper() == sku.upper()), None)
    return item.name if item else sku