# # aiva/state_machine/authority.py
# from aiva.state_machine.types import SessionState, MenuItemSnapshot, KitchenSnapshot
# from aiva.validation.schemas import ActionRequest, ValidationResult, ActionType
# from aiva.validation.errors import RejectionCode

# # Business thresholds
# HIGH_KITCHEN_LOAD_THRESHOLD = 85
# MAX_COMPLEXITY_WHEN_BUSY = 3


# def evaluate_action(
#     action: ActionRequest,
#     session: SessionState,
#     menu_item: MenuItemSnapshot | None,
#     kitchen: KitchenSnapshot,
# ) -> ValidationResult:
#     """
#     Deterministic authority function.
#     SAME INPUTS => SAME OUTPUTS (NO EXCEPTIONS)
#     """

#     # -------------------------------------------------
#     # 1️⃣ GLOBAL ORDER STATE — ABSOLUTE PRIORITY
#     # -------------------------------------------------
#     # Once confirmed, the order is immutable.
#     if (
#         session.order_status == "CONFIRMED"
#         and action.action_type != ActionType.ASK_CLARIFICATION
#     ):
#         return ValidationResult(
#             approved=False,
#             rejection_code=RejectionCode.ERR_INVALID_STATE,
#             user_message="Your order is already being prepared. I can help you check its status!"
#         )

#     # -------------------------------------------------
#     # 2️⃣ SAFETY — TOOL / TURN BUDGET
#     # -------------------------------------------------
#     if session.tool_budget_remaining <= 0:
#         return ValidationResult(
#             approved=False,
#             rejection_code=RejectionCode.BUDGET_EXCEEDED,
#             user_message="I'm having a little trouble processing that. Let's try something simpler."
#         )

#     # -------------------------------------------------
#     # 3️⃣ ITEM PRESENCE (ONLY IF REQUIRED)
#     # -------------------------------------------------
#     requires_sku = action.action_type in {
#         ActionType.ADD_TO_CART,
#         ActionType.MODIFY_ITEM,
#         ActionType.REMOVE_FROM_CART,
#     }

#     if requires_sku and not menu_item:
#         return ValidationResult(
#             approved=False,
#             rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#             user_message="I couldn't find that item on our current menu."
#         )

#     # -------------------------------------------------
#     # 4️⃣ ITEM-DEPENDENT RULES
#     # -------------------------------------------------
#     if menu_item:
#         if not menu_item.in_stock:
#             return ValidationResult(
#                 approved=False,
#                 rejection_code=RejectionCode.ERR_OUT_OF_STOCK,
#                 user_message=f"I'm sorry, we just ran out of that item."
#             )

#         if menu_item.is_alcohol and not session.age_verified:
#             return ValidationResult(
#                 approved=False,
#                 rejection_code=RejectionCode.ERR_AGE_RESTRICTION,
#                 user_message="I'll need to verify your ID before I can add alcohol."
#             )

#     # -------------------------------------------------
#     # 5️⃣ KITCHEN LOAD THROTTLING
#     # -------------------------------------------------
#     if (
#         kitchen.load_percentage >= HIGH_KITCHEN_LOAD_THRESHOLD
#         and menu_item
#         and menu_item.complexity_score > MAX_COMPLEXITY_WHEN_BUSY
#     ):
#         return ValidationResult(
#             approved=False,
#             rejection_code=RejectionCode.ERR_KITCHEN_OVERLOAD,
#             user_message="Our kitchen is extremely busy right now. Can I suggest something quicker?"
#         )

#     # -------------------------------------------------
#     # ✅ APPROVED
#     # -------------------------------------------------
#     return ValidationResult(approved=True)





# # aiva/state_machine/authority.py
# from aiva.state_machine.types import SessionState, MenuItemSnapshot, KitchenSnapshot
# from aiva.validation.schemas import ActionRequest, ValidationResult, ActionType
# from aiva.validation.errors import RejectionCode

# HIGH_KITCHEN_LOAD_THRESHOLD = 85
# MAX_COMPLEXITY_WHEN_BUSY = 3

# def evaluate_action(
#     action: ActionRequest,
#     session: SessionState,
#     menu_item: MenuItemSnapshot | None,
#     kitchen: KitchenSnapshot,
# ) -> ValidationResult:
#     """
#     Deterministic authority function.
#     SAME INPUTS => SAME OUTPUTS
#     """

#     # 1️⃣ Global order state
#     if session.order_status == "CONFIRMED" and action.action_type != ActionType.ASK_CLARIFICATION:
#         return ValidationResult(
#             approved=False,
#             rejection_code=RejectionCode.ERR_INVALID_STATE,
#             user_message="Your order is already being prepared. I can help you check its status!"
#         )

#     # 2️⃣ Safety — Tool Budget
#     if session.tool_budget_remaining <= 0:
#         return ValidationResult(
#             approved=False,
#             rejection_code=RejectionCode.BUDGET_EXCEEDED,
#             user_message="I'm having trouble processing that. Let's try something simpler."
#         )

#     # 3️⃣ Item Presence
#     requires_sku = action.action_type in {ActionType.ADD_TO_CART, ActionType.MODIFY_ITEM, ActionType.REMOVE_FROM_CART}
#     if requires_sku and not menu_item:
#         return ValidationResult(
#             approved=False,
#             rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#             user_message="I couldn't find that item on our current menu."
#         )

#     # 4️⃣ Item-dependent rules
#     if menu_item:
#         if not menu_item.in_stock:
#             return ValidationResult(
#                 approved=False,
#                 rejection_code=RejectionCode.ERR_OUT_OF_STOCK,
#                 user_message="I'm sorry, we just ran out of that item."
#             )
#         if menu_item.is_alcohol and not session.age_verified:
#             return ValidationResult(
#                 approved=False,
#                 rejection_code=RejectionCode.ERR_AGE_RESTRICTION,
#                 user_message="I'll need to verify your ID before I can add alcohol."
#             )

#     # 5️⃣ Kitchen load throttling
#     if kitchen.load_percentage >= HIGH_KITCHEN_LOAD_THRESHOLD and menu_item and menu_item.complexity_score > MAX_COMPLEXITY_WHEN_BUSY:
#         return ValidationResult(
#             approved=False,
#             rejection_code=RejectionCode.ERR_KITCHEN_OVERLOAD,
#             user_message="Our kitchen is extremely busy right now. Can I suggest something quicker?"
#         )

#     # ✅ Approved
#     return ValidationResult(approved=True)











# claud gives this
# aiva/state_machine/authority.py
# from typing import List
# from aiva.state_machine.types import SessionState, MenuItemSnapshot, KitchenSnapshot
# from aiva.validation.schemas import ActionRequest, ValidationResult, ActionType
# from aiva.validation.errors import RejectionCode, ViolationType, Severity

# HIGH_KITCHEN_LOAD_THRESHOLD = 85
# MAX_COMPLEXITY_WHEN_BUSY = 3
# LOW_CONFIDENCE_THRESHOLD = 0.7
# HIGH_COMPLEXITY_THRESHOLD = 4
# LARGE_QUANTITY_THRESHOLD = 5

# def evaluate_action(
#     action: ActionRequest,
#     session: SessionState,
#     menu_item: MenuItemSnapshot | None,
#     kitchen: KitchenSnapshot,
#     all_menu_items: List[MenuItemSnapshot],  # 🆕 Need full menu for ambiguity detection
# ) -> ValidationResult:
#     """
#     🆕 STEP 11: Authoritative validation with violation taxonomy.
    
#     This is the ONLY place allowed to judge whether an action is:
#     - Legal
#     - Safe
#     - Allowed
#     - Ambiguous
#     - Confident enough
    
#     SAME INPUTS => SAME OUTPUTS (deterministic)
#     """

#     # ═══════════════════════════════════════════════════════════════
#     # 🔴 FATAL VIOLATIONS (Hard Blocks)
#     # ═══════════════════════════════════════════════════════════════

#     # 1️⃣ Order State Check
#     if session.order_status == "CONFIRMED" and action.action_type != ActionType.ASK_CLARIFICATION:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_STATE,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_INVALID_STATE,
#             user_message="Your order is already being prepared. I can help you check its status!",
#             system_hint="Order already confirmed"
#         )

#     # 2️⃣ Tool Budget Check
#     if session.tool_budget_remaining <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.BUDGET_EXCEEDED,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.BUDGET_EXCEEDED,
#             user_message="I'm having trouble processing that. Let's try something simpler.",
#             system_hint="Budget exhausted"
#         )

#     # 3️⃣ Quantity Validation (🆕 Moved from Pydantic to Authority)
#     requires_quantity = action.action_type in {ActionType.ADD_TO_CART, ActionType.REMOVE_FROM_CART}
#     if requires_quantity and action.quantity <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_QUANTITY,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_INVALID_QUANTITY,
#             user_message="Quantity must be at least 1.",
#             system_hint=f"Invalid quantity: {action.quantity}"
#         )

#     # 4️⃣ SKU Existence Check (🆕 Enhanced with ambiguity detection)
#     requires_sku = action.action_type in {ActionType.ADD_TO_CART, ActionType.MODIFY_ITEM, ActionType.REMOVE_FROM_CART}
    
#     if requires_sku:
#         if not action.sku:
#             # 🆕 Check if this is a category ambiguity issue
#             ambiguity_result = _check_category_ambiguity(action, all_menu_items)
#             if ambiguity_result:
#                 return ambiguity_result
            
#             # Otherwise, just missing SKU
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I couldn't identify which item you want. Could you be more specific?",
#                 system_hint="No SKU provided"
#             )
        
#         # SKU provided, but doesn't match any item
#         if not menu_item:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I couldn't find that item on our current menu.",
#                 system_hint=f"SKU not found: {action.sku}"
#             )

#     # 5️⃣ Stock Availability
#     if menu_item and not menu_item.in_stock:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.OUT_OF_STOCK,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_OUT_OF_STOCK,
#             user_message="I'm sorry, we just ran out of that item.",
#             system_hint=f"{menu_item.name} out of stock"
#         )

#     # 6️⃣ Age Restriction
#     if menu_item and menu_item.is_alcohol and not session.age_verified:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.AGE_RESTRICTION,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_AGE_RESTRICTION,
#             user_message="I'll need to verify your ID before I can add alcohol.",
#             system_hint="Age verification required"
#         )

#     # 7️⃣ Kitchen Load Throttling
#     if (kitchen.load_percentage >= HIGH_KITCHEN_LOAD_THRESHOLD and 
#         menu_item and menu_item.complexity_score > MAX_COMPLEXITY_WHEN_BUSY):
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.KITCHEN_OVERLOAD,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_KITCHEN_OVERLOAD,
#             user_message="Our kitchen is extremely busy right now. Can I suggest something quicker?",
#             system_hint=f"Kitchen at {kitchen.load_percentage}%, complexity {menu_item.complexity_score}"
#         )

#     # 8️⃣ Item Must Exist in Cart for REMOVE
#     if action.action_type == ActionType.REMOVE_FROM_CART:
#         if action.sku not in session.cart:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.ITEM_NOT_IN_CART,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_IN_CART,
#                 user_message="That item isn't in your cart yet.",
#                 system_hint=f"Attempted to remove {action.sku} which is not in cart"
#             )

#     # ═══════════════════════════════════════════════════════════════
#     # 🟡 RECOVERABLE VIOLATIONS (Can be fixed with clarification)
#     # ═══════════════════════════════════════════════════════════════

#     # 9️⃣ Low Confidence Detection (🆕)
#     if action.confidence < LOW_CONFIDENCE_THRESHOLD and action.action_type == ActionType.ADD_TO_CART:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.LOW_CONFIDENCE,
#             severity=Severity.RECOVERABLE,
#             rejection_code=RejectionCode.ERR_LOW_CONFIDENCE,
#             requires_clarification=True,
#             user_message="I'm not quite sure which item you mean. Could you clarify?",
#             system_hint=f"Confidence {action.confidence} below threshold {LOW_CONFIDENCE_THRESHOLD}"
#         )

#     # ═══════════════════════════════════════════════════════════════
#     # 🟢 DEFERRED CHECKS (Warnings, but allowed to proceed)
#     # ═══════════════════════════════════════════════════════════════

#     # 🔟 High Complexity Confirmation (🆕)
#     if (menu_item and 
#         menu_item.complexity_score >= HIGH_COMPLEXITY_THRESHOLD and
#         action.action_type == ActionType.ADD_TO_CART):
#         # For now, we ALLOW but could require confirmation later
#         # This is where you'd add human-in-the-loop confirmation
#         pass  # Future: return requires_confirmation=True

#     # 1️⃣1️⃣ Large Quantity Warning (🆕)
#     if action.quantity >= LARGE_QUANTITY_THRESHOLD:
#         # For now, we ALLOW but could warn user
#         # Future: "Are you sure you want 10 pizzas?"
#         pass

#     # ═══════════════════════════════════════════════════════════════
#     # ✅ APPROVED
#     # ═══════════════════════════════════════════════════════════════
    
#     return ValidationResult(
#         approved=True,
#         system_hint=f"Approved: {action.action_type} for {action.sku or 'N/A'}"
#     )


# def _check_category_ambiguity(
#     action: ActionRequest, 
#     all_menu_items: List[MenuItemSnapshot]
# ) -> ValidationResult | None:
#     """
#     🆕 STEP 11: Detect if user's intent matches multiple items (category ambiguity).
    
#     Example:
#     - User says "add pizza" → matches 3 items → AMBIGUOUS
#     - User says "add pepperoni pizza" → matches 1 item → OK (not called if SKU exists)
    
#     Returns:
#         ValidationResult if ambiguous, None if OK
#     """
#     # This function is only called when SKU is missing
#     # Check if the action metadata contains hints about what was attempted
    
#     if not action.meta:
#         return None
    
#     # If OrderTaker tried to match a category and found multiple items
#     category_hint = action.meta.get("attempted_category")
#     if category_hint:
#         matching_items = [
#             item for item in all_menu_items 
#             if category_hint.lower() in item.name.lower()
#         ]
        
#         if len(matching_items) > 1:
#             options = ", ".join([f"{item.name} (${item.price})" for item in matching_items])
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.AMBIGUOUS_CATEGORY,
#                 severity=Severity.RECOVERABLE,
#                 rejection_code=RejectionCode.ERR_AMBIGUOUS_CATEGORY,
#                 requires_clarification=True,
#                 user_message=f"Which {category_hint} would you like? We have: {options}",
#                 system_hint=f"Category '{category_hint}' matched {len(matching_items)} items"
#             )
    
#     return None








# gemini gives the claud verson with fixes (testing)
# # aiva/state_machine/authority.py
# from typing import List, Dict, Any
# from aiva.state_machine.types import SessionState, MenuItemSnapshot, KitchenSnapshot, ContextScope
# from aiva.validation.schemas import ActionRequest, ValidationResult, ActionType, IntentType
# from aiva.validation.errors import RejectionCode, ViolationType, Severity
# from aiva.orchestration.memory_manager import MemoryManager


# HIGH_KITCHEN_LOAD_THRESHOLD = 85
# MAX_COMPLEXITY_WHEN_BUSY = 3
# LOW_CONFIDENCE_THRESHOLD = 0.7

# # 🆕 The Jurisdictional Matrix: Which agents can handle which intents?
# AGENT_PERMISSION_MATRIX = {
#     "OrderTaker": {IntentType.ORDERING, IntentType.GREETING},
#     "MenuExpert": {IntentType.INQUIRY, IntentType.GREETING},
#     "Greeter": {IntentType.GREETING}
# }

# def evaluate_action(
#     action: ActionRequest,
#     session: SessionState,
#     menu_item: MenuItemSnapshot | None,
#     kitchen: KitchenSnapshot,
#     all_menu_items: List[MenuItemSnapshot],
#     memory: MemoryManager 
# ) -> ValidationResult:
#     """
#     🆕 STEP 11: Authoritative Supreme Court.
#     Enforces the Jurisdictional Law to fix routing errors systemically.
#     """

#     # 1️⃣ ⚖️ JURISDICTIONAL CHECK (Systemic Fix)
#     # Ensure the active agent is legally allowed to handle the requested intent
#     if action.intent and session.active_agent in AGENT_PERMISSION_MATRIX:
#         allowed_intents = AGENT_PERMISSION_MATRIX[session.active_agent]
#         if action.intent not in allowed_intents:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_STATE, # Wrong agent state
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_INVALID_STATE,
#                 user_message="I should let our Menu Expert handle that inquiry for you.",
#                 system_hint=f"JURISDICTION_MISMATCH: Agent {session.active_agent} cannot handle {action.intent}"
#             )

#     # 2️⃣ Order State Check (FATAL)
#     if session.order_status == "CONFIRMED" and action.action_type != ActionType.ASK_CLARIFICATION:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_STATE,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_INVALID_STATE,
#             user_message="Your order is already being prepared. I can help you check its status!"
#         )

#     # 3️⃣ Tool Budget Check (FATAL)
#     if session.tool_budget_remaining <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.BUDGET_EXCEEDED,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.BUDGET_EXCEEDED,
#             user_message="I'm having trouble processing that. Let's try something simpler."
#         )

#     # 3️⃣ Quantity Validation (FATAL)
#     requires_quantity = action.action_type in {ActionType.ADD_TO_CART, ActionType.REMOVE_FROM_CART}
#     if requires_quantity and action.quantity <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_QUANTITY,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_INVALID_QUANTITY,
#             user_message="Quantity must be at least 1."
#         )

#     # 4️⃣ SKU & Ambiguity Check (RECOVERABLE)
#     requires_sku = action.action_type in {ActionType.ADD_TO_CART, ActionType.MODIFY_ITEM, ActionType.REMOVE_FROM_CART}
#     if requires_sku:
#         if not action.sku:
#             # Check for category-based ambiguity (e.g., "add pizza")
#             ambiguity_result = _check_category_ambiguity(action, all_menu_items)
#             if ambiguity_result:
#                 return ambiguity_result
            
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I'm not sure which item you'd like. Could you specify?"
#             )
        
#         if not menu_item:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I couldn't find that item on our current menu."
#             )

#     # 5️⃣ Business Rules: Stock & Alcohol (FATAL)
#     if menu_item:
#         if not menu_item.in_stock:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.OUT_OF_STOCK,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_OUT_OF_STOCK,
#                 user_message="I'm sorry, we just ran out of that item."
#             )
#         if menu_item.is_alcohol and not session.age_verified:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.AGE_RESTRICTION,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_AGE_RESTRICTION,
#                 user_message="I'll need to verify your ID before I can add alcohol."
#             )

#     # 6️⃣ Kitchen Load Throttling (FATAL/DEFERRED)
#     if (kitchen.load_percentage >= HIGH_KITCHEN_LOAD_THRESHOLD and 
#         menu_item and menu_item.complexity_score > MAX_COMPLEXITY_WHEN_BUSY):
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.KITCHEN_OVERLOAD,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_KITCHEN_OVERLOAD,
#             user_message="Our kitchen is extremely busy right now. Can I suggest something quicker?"
#         )

#     # 7️⃣ 🛡️ Optimistic Mutation Authorization Gate (Systemic Fix)
#     # Replaces the legacy 'Confidence Guard' to allow context-aware ordering.
#     mutating_actions = {ActionType.ADD_TO_CART, ActionType.REMOVE_FROM_CART, ActionType.MODIFY_ITEM}
    
#     if action.action_type in mutating_actions:
#         # Check if we have a 'Permit' to allow low-confidence (noun-only) mutations
#         if not _is_optimistic_mutation_authorized(action, session, memory):
#             item_name = menu_item.name if menu_item else "that item"
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.LOW_CONFIDENCE,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_LOW_CONFIDENCE,
#                 user_message=(
#                     f"I see you're referring to {item_name}. "
#                     "Would you like me to add it to your order, or would you like to know more about it?"
#                 ),
#                 system_hint="OPTIMISM_DENIED: Inquiry Suppressor active or no established ordering context."
#             )
        
#     return ValidationResult(approved=True, system_hint=getattr(session, "authority_hint", "Validated."), meta={"context_scope": session.context_scope})

# def _check_category_ambiguity(
#     action: ActionRequest, 
#     all_menu_items: List[MenuItemSnapshot]
# ) -> ValidationResult | None:
#     """Detects if an optimistic intent (no SKU) matches multiple menu items."""
#     if not action.meta or "attempted_category" not in action.meta:
#         return None
    
#     cat = action.meta["attempted_category"].lower()
#     matches = [i for i in all_menu_items if cat in i.name.lower()]
    
#     if len(matches) > 1:
#         options = ", ".join([f"{i.name} (${i.price})" for i in matches])
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.AMBIGUOUS_CATEGORY,
#             severity=Severity.RECOVERABLE,
#             requires_clarification=True,
#             rejection_code=RejectionCode.ERR_AMBIGUOUS_CATEGORY,
#             user_message=f"Which {cat} did you mean? We have: {options}"
#         )
#     return None

# def decide_context_scope(session: SessionState) -> Dict[str, Any]:
#     """
#     ⚖️ SYSTEMIC POLICY: Authority defines the data permission.
#     Returns a dictionary to be placed in ValidationResult.meta.
#     """
#     scope = ContextScope.FILTERED_SEARCH
#     hint = "Standard context applied."

#     if getattr(session, "active_intent", None) == IntentType.INQUIRY:
#         scope = ContextScope.FULL_CATALOG
#         hint = "Broad inquiry detected: Full catalog access authorized."

#     return {"context_scope": scope, "system_hint": hint}

# def _is_optimistic_mutation_authorized(
#     action: ActionRequest,
#     session: SessionState,
#     memory: Any
# ) -> bool:
#     """
#     ⚖️ Optimistic Mutation Authorization Gate
#     """
#     # 1️⃣ EXPLICIT INTENT (Priority 1)
#     if action.confidence >= 1.0:
#         return True

#     # 2️⃣ INQUIRY SUPPRESSOR (Priority 2)
#     # Combined Safety: Check if memory exists, window exists, AND window is not empty
#     if memory and getattr(memory, "window", None) and memory.window:
#         last_turn = memory.window[-1]
#         if last_turn.get("agent") == "MenuExpert":
#             return False 

#     # 3️⃣ ACTIVE ORDERING CONTEXT (Priority 3)
#     if session.cart and len(session.cart) > 0:
#         return True

#     # 4️⃣ DEFAULT SAFETY (Priority 4)
#     return False









# # DineFlow/state_machine/authority.py
# from typing import List, Dict, Any
# from state_machine.types import SessionState, MenuItemSnapshot, KitchenSnapshot, ContextScope
# from validation.schemas import ActionRequest, ValidationResult, ActionType, IntentType
# from validation.errors import RejectionCode, ViolationType, Severity
# from orchestration.memory_manager import MemoryManager


# # =============================================================================
# # ⚖️ AUTHORITY LAYER — CONTRACT v1.1 (FROZEN)
# #
# # Canonical Principles:
# # - Authority is the ONLY component allowed to approve or deny state mutation.
# # - Authority owns legality, safety, deferral, and optimistic mutation permits.
# # - LLMs, Routers, and Agents may be optimistic or incorrect.
# # - Authority MUST NOT be wrong.
# #
# # Canonical Output Rule:
# # - ViolationType is the canonical decision signal.
# # - RejectionCode exists ONLY for backward compatibility and UX mapping.
# #
# # Context Ownership:
# # - Authority may DEFINE or DELEGATE context scope.
# # - In v1.1, Authority validates but does not recompute context scope.
# #
# # Any action reaching Authority may be fuzzy, inferred, or incomplete.
# # Authority alone decides whether it is:
# #   - Allowed
# #   - Recoverable
# #   - Deferred
# #   - Fatal
# # =============================================================================


# HIGH_KITCHEN_LOAD_THRESHOLD = 85
# MAX_COMPLEXITY_WHEN_BUSY = 3
# LOW_CONFIDENCE_THRESHOLD = 0.7


# # 🆕 Jurisdictional Matrix: Which agents can legally handle which intents
# AGENT_PERMISSION_MATRIX = {
#     "OrderTaker": {IntentType.ORDERING, IntentType.GREETING},
#     "MenuExpert": {IntentType.INQUIRY, IntentType.GREETING},
#     "Greeter": {IntentType.GREETING}
# }


# def evaluate_action(
#     action: ActionRequest,
#     session: SessionState,
#     menu_item: MenuItemSnapshot | None,
#     kitchen: KitchenSnapshot,
#     all_menu_items: List[MenuItemSnapshot],
#     memory: MemoryManager
# ) -> ValidationResult:
#     """
#     ⚖️ AUTHORITY — SUPREME COURT (STEP 11)

#     Final arbiter of all proposed actions.

#     Responsibilities:
#     - Enforce jurisdictional legality
#     - Validate irreversible mutations
#     - Classify violations (FATAL / RECOVERABLE / DEFERRED)
#     - Control optimistic mutation permits
#     """

#     # 1️⃣ ⚖️ JURISDICTION CHECK (NEGATIVE POWER)
#     if action.intent and session.active_agent in AGENT_PERMISSION_MATRIX:
#         allowed_intents = AGENT_PERMISSION_MATRIX[session.active_agent]
#         if action.intent not in allowed_intents:
#              # 🔐 Authority decides the correct jurisdiction
#             target_agent = None
#             for agent, intents in AGENT_PERMISSION_MATRIX.items():
#                 if action.intent in intents:
#                     target_agent = agent
#                     break
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_STATE,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=False,
#                 rejection_code=RejectionCode.ERR_INVALID_STATE,
#                 user_message="I should let our Menu Expert handle that inquiry for you.",
#                 system_hint=f"JURISDICTION_MISMATCH: Agent {session.active_agent} cannot handle {action.intent}",
#                  meta={
#                 "target_agent": target_agent
#             }
#             )

#     # 2️⃣ ORDER STATE CHECK - FIX: SEMANTIC TRUTH (INVALID_STATE + FATAL)
#     if session.order_status == "CONFIRMED" and action.action_type != ActionType.ASK_CLARIFICATION:
#         # ✅ TRUTHFUL: The state cannot accept mutations.
#         # ✅ FATAL: Prevents the loop from recursing (no infinite retry).
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_STATE,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_INVALID_STATE,
#             requires_clarification=False,
#             user_message="Your order is already being prepared. I can help you check its status!"
#         )

#     # 3️⃣ TOOL BUDGET CHECK (FATAL)
#     if session.tool_budget_remaining <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.BUDGET_EXCEEDED,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.BUDGET_EXCEEDED,
#             user_message="I'm having trouble processing that. Let's try something simpler."
#         )

#     # 4️⃣ QUANTITY VALIDATION (FATAL)
#     if action.action_type in {ActionType.ADD_TO_CART, ActionType.REMOVE_FROM_CART} and action.quantity <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_QUANTITY,
#             severity=Severity.RECOVERABLE,
#             rejection_code=RejectionCode.ERR_INVALID_QUANTITY,
#             requires_clarification=True,
#             user_message="Quantity must be at least 1."
#         )

#     # 5️⃣ SKU & AMBIGUITY VALIDATION (AUTHORITY-OWNED)
#     requires_sku = action.action_type in {
#         ActionType.ADD_TO_CART,
#         ActionType.MODIFY_ITEM,
#         ActionType.REMOVE_FROM_CART
#     }

#     if requires_sku:
#         if not action.sku:
#             ambiguity_result = _check_category_ambiguity(action, all_menu_items)
#             if ambiguity_result:
#                 return ambiguity_result

#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I'm not sure which item you'd like. Could you specify?"
#             )

#         if not menu_item:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I couldn't find that item on our current menu."
#             )

#     # 6️⃣ BUSINESS RULES — STOCK (FATAL) & ALCOHOL (DEFERRED)
#     if menu_item:
#         if not menu_item.in_stock:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message=f"I'm sorry, the {menu_item.name} is currently out of stock."
#             )

#         if menu_item.is_alcohol and not session.age_verified:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.AGE_RESTRICTION,
#                 severity=Severity.DEFERRED,
#                 requires_clarification=False,
#                 rejection_code=RejectionCode.ERR_AGE_RESTRICTION,
#                 user_message="I'll need to verify your ID before adding alcohol.",
#                 meta={"required_capability": "ID_VERIFIER"}
#             )

#     # 7️⃣ KITCHEN LOAD THROTTLING (DEFERRED)
#     if (
#         kitchen.load_percentage >= HIGH_KITCHEN_LOAD_THRESHOLD and
#         menu_item and menu_item.complexity_score > MAX_COMPLEXITY_WHEN_BUSY
#     ):
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.KITCHEN_OVERLOAD,
#             severity=Severity.DEFERRED,
#             rejection_code=RejectionCode.ERR_KITCHEN_OVERLOAD,
#             user_message="Our kitchen is extremely busy right now. Can I suggest something quicker?"
#         )

#     # 8️⃣ 🛡️ OPTIMISTIC MUTATION AUTHORIZATION
#     mutating_actions = {
#         ActionType.ADD_TO_CART,
#         ActionType.REMOVE_FROM_CART,
#         ActionType.MODIFY_ITEM
#     }

#     if action.action_type in mutating_actions:
#         if not _is_optimistic_mutation_authorized(action, session, memory):
#             item_name = menu_item.name if menu_item else "that item"
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.LOW_CONFIDENCE,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_LOW_CONFIDENCE,
#                 user_message=(
#                     f"I see you're referring to {item_name}. "
#                     "Would you like me to add it to your order, or would you like to know more about it?"
#                 ),
#                 system_hint="OPTIMISM_DENIED: No explicit intent or active ordering context."
#             )

#     return ValidationResult(
#         approved=True,
#         system_hint=getattr(session, "authority_hint", "Validated."),
#         meta={"context_scope": session.context_scope}
#     )


# def _check_category_ambiguity(
#     action: ActionRequest,
#     all_menu_items: List[MenuItemSnapshot]
# ) -> ValidationResult | None:
#     """Detects if a category-level intent maps to multiple menu items."""

#     if not action.meta or "attempted_category" not in action.meta:
#         return None

#     cat = action.meta["attempted_category"].lower()
#     matches = [i for i in all_menu_items if cat in i.name.lower()]

#     if len(matches) > 1:
#         options = ", ".join(f"{i.name} (${i.price})" for i in matches)
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.AMBIGUOUS_CATEGORY,
#             severity=Severity.RECOVERABLE,
#             requires_clarification=True,
#             rejection_code=RejectionCode.ERR_AMBIGUOUS_CATEGORY,
#             user_message=f"Which {cat} did you mean? We have: {options}"
#         )

#     return None


# def decide_context_scope(session: SessionState) -> Dict[str, Any]:
#     """
#     ⚖️ CONTEXT SCOPE POLICY (DECLARATIVE)

#     NOTE:
#     - Authority defines the rules.
#     - Router or Orchestrator may apply the scope.
#     """

#     scope = ContextScope.FILTERED_SEARCH
#     hint = "Standard context applied."

#     if getattr(session, "active_intent", None) == IntentType.INQUIRY:
#         scope = ContextScope.FULL_CATALOG
#         hint = "Broad inquiry detected: Full catalog access authorized."

#     return {"context_scope": scope, "system_hint": hint}


# def _is_optimistic_mutation_authorized(
#     action: ActionRequest,
#     session: SessionState,
#     memory: Any
# ) -> bool:
#     """
#     ⚖️ OPTIMISTIC MUTATION AUTHORIZATION — SYSTEMATIC (v1.0)

#     Allows noun-only mutations ONLY when the system can PROVE
#     the user is responding to a clarification request.
#     """

#     # 1️⃣ Explicit intent (hard override)
#     if action.confidence >= 1.0:
#         return True

#     # Defensive guard
#     if not memory or not getattr(memory, "window", None) or not memory.window:
#         return False

#     last_turn = memory.window[-1]

#     # 2️⃣ SYSTEMATIC CLARIFICATION LOOP (PRIMARY SIGNAL)
#     if last_turn.get("status") in {
#         "agent_clarification",
#         "authority_clarification"
#     }:
#         return True

#     # 3️⃣ MenuExpert safety block (prevents inquiry → accidental add)
#     if last_turn.get("agent") == "MenuExpert":
#         return False

#     # 4️⃣ Existing cart = active ordering context
#     if session.cart:
#         return True

#     return False





# claud recent version testing
# # DineFlow/state_machine/authority.py
# from typing import List, Dict, Any
# from state_machine.types import SessionState, MenuItemSnapshot, KitchenSnapshot, ContextScope
# from state_machine.query_classifier import QueryClassifier, QueryClass
# from validation.schemas import ActionRequest, ValidationResult, ActionType, IntentType
# from validation.errors import RejectionCode, ViolationType, Severity
# from orchestration.memory_manager import MemoryManager


# # =============================================================================
# # ⚖️ AUTHORITY LAYER — CONTRACT v1.2
# #
# # Canonical Principles:
# # - Authority is the ONLY component allowed to approve or deny state mutation.
# # - Authority owns legality, safety, deferral, and optimistic mutation permits.
# # - LLMs, Routers, and Agents may be optimistic or incorrect.
# # - Authority MUST NOT be wrong.
# #
# # Canonical Output Rule:
# # - ViolationType is the canonical decision signal.
# # - RejectionCode exists ONLY for backward compatibility and UX mapping.
# #
# # Context Ownership (v1.2 change):
# # - decide_context_scope now accepts user_input and delegates structural
# #   classification to QueryClassifier.
# # - This replaces the intent-only check from v1.1 which could not see the
# #   raw query and therefore could not classify attribute-style questions.
# #
# # Any action reaching Authority may be fuzzy, inferred, or incomplete.
# # Authority alone decides whether it is:
# #   - Allowed
# #   - Recoverable
# #   - Deferred
# #   - Fatal
# # =============================================================================


# HIGH_KITCHEN_LOAD_THRESHOLD = 85
# MAX_COMPLEXITY_WHEN_BUSY = 3
# LOW_CONFIDENCE_THRESHOLD = 0.7


# # 🆕 Jurisdictional Matrix: Which agents can legally handle which intents
# AGENT_PERMISSION_MATRIX = {
#     "OrderTaker": {IntentType.ORDERING, IntentType.GREETING},
#     "MenuExpert": {IntentType.INQUIRY, IntentType.GREETING},
#     "Greeter": {IntentType.GREETING}
# }


# # QueryClassifier is instantiated lazily on first call to decide_context_scope.
# # It cannot be instantiated here at module load time because all_menu_items
# # is not yet available — the registry is bootstrapped in golden_loop.py.
# # The classifier is then cached for the lifetime of the process.
# _query_classifier: QueryClassifier | None = None


# def _get_classifier(all_menu_items: list) -> QueryClassifier:
#     """
#     Returns the shared QueryClassifier instance, creating it on first call.
#     Thread-safe for read-heavy workloads (construction is idempotent).
#     """
#     global _query_classifier
#     if _query_classifier is None:
#         _query_classifier = QueryClassifier(all_menu_items)
#     return _query_classifier


# def evaluate_action(
#     action: ActionRequest,
#     session: SessionState,
#     menu_item: MenuItemSnapshot | None,
#     kitchen: KitchenSnapshot,
#     all_menu_items: List[MenuItemSnapshot],
#     memory: MemoryManager
# ) -> ValidationResult:
#     """
#     ⚖️ AUTHORITY — SUPREME COURT

#     Final arbiter of all proposed actions.

#     Responsibilities:
#     - Enforce jurisdictional legality
#     - Validate irreversible mutations
#     - Classify violations (FATAL / RECOVERABLE / DEFERRED)
#     - Control optimistic mutation permits
#     """

#     # 1️⃣ ⚖️ JURISDICTION CHECK (NEGATIVE POWER)
#     if action.intent and session.active_agent in AGENT_PERMISSION_MATRIX:
#         allowed_intents = AGENT_PERMISSION_MATRIX[session.active_agent]
#         if action.intent not in allowed_intents:
#             # 🔐 Authority decides the correct jurisdiction
#             target_agent = None
#             for agent, intents in AGENT_PERMISSION_MATRIX.items():
#                 if action.intent in intents:
#                     target_agent = agent
#                     break
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_STATE,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=False,
#                 rejection_code=RejectionCode.ERR_INVALID_STATE,
#                 user_message="I should let our Menu Expert handle that inquiry for you.",
#                 system_hint=f"JURISDICTION_MISMATCH: Agent {session.active_agent} cannot handle {action.intent}",
#                 meta={"target_agent": target_agent}
#             )

#     # 2️⃣ ORDER STATE CHECK — SEMANTIC TRUTH (INVALID_STATE + FATAL)
#     if session.order_status == "CONFIRMED" and action.action_type != ActionType.ASK_CLARIFICATION:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_STATE,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_INVALID_STATE,
#             requires_clarification=False,
#             user_message="Your order is already being prepared. I can help you check its status!"
#         )

#     # 3️⃣ TOOL BUDGET CHECK (FATAL)
#     if session.tool_budget_remaining <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.BUDGET_EXCEEDED,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.BUDGET_EXCEEDED,
#             user_message="I'm having trouble processing that. Let's try something simpler."
#         )

#     # 4️⃣ QUANTITY VALIDATION
#     if action.action_type in {ActionType.ADD_TO_CART, ActionType.REMOVE_FROM_CART} and action.quantity <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_QUANTITY,
#             severity=Severity.RECOVERABLE,
#             rejection_code=RejectionCode.ERR_INVALID_QUANTITY,
#             requires_clarification=True,
#             user_message="Quantity must be at least 1."
#         )

#     # 5️⃣ SKU & AMBIGUITY VALIDATION (AUTHORITY-OWNED)
#     requires_sku = action.action_type in {
#         ActionType.ADD_TO_CART,
#         ActionType.MODIFY_ITEM,
#         ActionType.REMOVE_FROM_CART
#     }

#     if requires_sku:
#         if not action.sku:
#             ambiguity_result = _check_category_ambiguity(action, all_menu_items)
#             if ambiguity_result:
#                 return ambiguity_result

#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I'm not sure which item you'd like. Could you specify?"
#             )

#         if not menu_item:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I couldn't find that item on our current menu."
#             )

#     # 6️⃣ BUSINESS RULES — STOCK (RECOVERABLE) & ALCOHOL (DEFERRED)
#     if menu_item:
#         if not menu_item.in_stock:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message=f"I'm sorry, the {menu_item.name} is currently out of stock."
#             )

#         if menu_item.is_alcohol and not session.age_verified:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.AGE_RESTRICTION,
#                 severity=Severity.DEFERRED,
#                 requires_clarification=False,
#                 rejection_code=RejectionCode.ERR_AGE_RESTRICTION,
#                 user_message="I'll need to verify your ID before adding alcohol.",
#                 meta={"required_capability": "ID_VERIFIER"}
#             )

#     # 7️⃣ KITCHEN LOAD THROTTLING (DEFERRED)
#     if (
#         kitchen.load_percentage >= HIGH_KITCHEN_LOAD_THRESHOLD and
#         menu_item and menu_item.complexity_score > MAX_COMPLEXITY_WHEN_BUSY
#     ):
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.KITCHEN_OVERLOAD,
#             severity=Severity.DEFERRED,
#             rejection_code=RejectionCode.ERR_KITCHEN_OVERLOAD,
#             user_message="Our kitchen is extremely busy right now. Can I suggest something quicker?"
#         )

#     # 8️⃣ 🛡️ OPTIMISTIC MUTATION AUTHORIZATION
#     mutating_actions = {
#         ActionType.ADD_TO_CART,
#         ActionType.REMOVE_FROM_CART,
#         ActionType.MODIFY_ITEM
#     }

#     if action.action_type in mutating_actions:
#         if not _is_optimistic_mutation_authorized(action, session, memory):
#             item_name = menu_item.name if menu_item else "that item"
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.LOW_CONFIDENCE,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_LOW_CONFIDENCE,
#                 user_message=(
#                     f"I see you're referring to {item_name}. "
#                     "Would you like me to add it to your order, or would you like to know more about it?"
#                 ),
#                 system_hint="OPTIMISM_DENIED: No explicit intent or active ordering context."
#             )

#     return ValidationResult(
#         approved=True,
#         system_hint=getattr(session, "authority_hint", "Validated."),
#         meta={"context_scope": session.context_scope}
#     )


# def _check_category_ambiguity(
#     action: ActionRequest,
#     all_menu_items: List[MenuItemSnapshot]
# ) -> ValidationResult | None:
#     """Detects if a category-level intent maps to multiple menu items."""

#     if not action.meta or "attempted_category" not in action.meta:
#         return None

#     cat = action.meta["attempted_category"].lower()
#     matches = [i for i in all_menu_items if cat in i.name.lower()]

#     if len(matches) > 1:
#         options = ", ".join(f"{i.name} (${i.price})" for i in matches)
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.AMBIGUOUS_CATEGORY,
#             severity=Severity.RECOVERABLE,
#             requires_clarification=True,
#             rejection_code=RejectionCode.ERR_AMBIGUOUS_CATEGORY,
#             user_message=f"Which {cat} did you mean? We have: {options}"
#         )

#     return None


# def decide_context_scope(session: SessionState, user_input: str, all_menu_items: list = None) -> Dict[str, Any]:
#     """
#     ⚖️ CONTEXT SCOPE POLICY — v1.2 (QueryClassifier-backed)

#     Replaces the v1.1 intent-only check with structural query classification.

#     v1.1 problem: Only checked session.active_intent (INQUIRY vs. not).
#     This meant "Do you have anything spicy?" would only get FULL_CATALOG if
#     the router had already set intent=INQUIRY — a fragile dependency.

#     v1.2 fix: QueryClassifier reads the raw user_input and classifies based
#     on grammatical structure:
#       - ENTITY_BOUND  → FILTERED_SEARCH  (user named a specific item)
#       - ATTRIBUTE_BOUND → FULL_CATALOG   (user asked about a property)
#       - AMBIGUOUS     → FULL_CATALOG     (safe default: fail toward more data)

#     The session intent is used as a secondary signal — if the classifier
#     returns ENTITY_BOUND but the intent is INQUIRY, we still elevate to
#     FULL_CATALOG because the intent signal has higher semantic authority
#     in that case (the router saw something the grammar check missed).

#     Args:
#         session:        Current session state (intent used as secondary signal).
#         user_input:     Raw user query — primary input for classification.
#         all_menu_items: Menu data for name-index construction. Optional because
#                         the classifier is cached after first call; pass on first
#                         call or whenever the menu changes.
#     """
#     # Resolve classifier (lazy init, cached after first call)
#     # If all_menu_items not passed and classifier not yet built, we fall back
#     # gracefully to intent-only logic rather than crashing.
#     classifier = _get_classifier(all_menu_items) if all_menu_items else _query_classifier

#     # ── Primary Path: Structural Classification ────────────────────────────────
#     if classifier and user_input:
#         classification = classifier.classify(user_input)

#         # Attach classification trace to the policy for logging/debugging
#         base_meta = {
#             "classifier_class": classification.query_class.value,
#             "classifier_confidence": classification.confidence,
#             "classifier_reasoning": classification.reasoning,
#             "resolved_entity": classification.resolved_entity,
#         }

#         # ENTITY_BOUND: use filtered search UNLESS intent overrides
#         if classification.query_class == QueryClass.ENTITY_BOUND:
#             # Secondary signal: if router independently flagged this as an INQUIRY,
#             # trust the router — the user may be asking about a named item's properties
#             # (e.g., "Is the Pepperoni Pizza spicy?") which still benefits from full context.
#             if getattr(session, "active_intent", None) == IntentType.INQUIRY:
#                 return {
#                     "context_scope": ContextScope.FULL_CATALOG,
#                     "system_hint": "Entity-bound query but INQUIRY intent: Full catalog authorized.",
#                     **base_meta
#                 }
#             return {
#                 "context_scope": ContextScope.FILTERED_SEARCH,
#                 "system_hint": f"Entity-bound query. Targeted search authorized. Entity: {classification.resolved_entity}",
#                 **base_meta
#             }

#         # ATTRIBUTE_BOUND or AMBIGUOUS: always full catalog
#         return {
#             "context_scope": ContextScope.FULL_CATALOG,
#             "system_hint": f"{'Attribute' if classification.query_class == QueryClass.ATTRIBUTE_BOUND else 'Ambiguous'} query: Full catalog access authorized.",
#             **base_meta
#         }

#     # ── Fallback Path: No classifier or empty input ────────────────────────────
#     # Mirrors v1.1 behavior as a last resort. Should not be reached in normal flow.
#     scope = ContextScope.FILTERED_SEARCH
#     hint = "Standard context applied (classifier unavailable — fallback to intent check)."

#     if getattr(session, "active_intent", None) == IntentType.INQUIRY:
#         scope = ContextScope.FULL_CATALOG
#         hint = "Broad inquiry intent detected (fallback path): Full catalog access authorized."

#     return {"context_scope": scope, "system_hint": hint}


# def _is_optimistic_mutation_authorized(
#     action: ActionRequest,
#     session: SessionState,
#     memory: Any
# ) -> bool:
#     """
#     ⚖️ OPTIMISTIC MUTATION AUTHORIZATION — SYSTEMATIC (v1.0)

#     Allows noun-only mutations ONLY when the system can PROVE
#     the user is responding to a clarification request.
#     """

#     # 1️⃣ Explicit intent (hard override)
#     if action.confidence >= 1.0:
#         return True

#     # Defensive guard
#     if not memory or not getattr(memory, "window", None) or not memory.window:
#         return False

#     last_turn = memory.window[-1]

#     # 2️⃣ SYSTEMATIC CLARIFICATION LOOP (PRIMARY SIGNAL)
#     if last_turn.get("status") in {
#         "agent_clarification",
#         "authority_clarification"
#     }:
#         return True

#     # 3️⃣ MenuExpert safety block (prevents inquiry → accidental add)
#     if last_turn.get("agent") == "MenuExpert":
#         return False

#     # 4️⃣ Existing cart = active ordering context
#     if session.cart:
#         return True

#     return False






# after fix calude version

# # DineFlow/state_machine/authority.py
# from typing import List, Dict, Any
# from state_machine.types import SessionState, MenuItemSnapshot, KitchenSnapshot, ContextScope
# from state_machine.query_classifier import QueryClassifier, QueryClass
# from validation.schemas import ActionRequest, ValidationResult, ActionType, IntentType
# from validation.errors import RejectionCode, ViolationType, Severity
# from orchestration.memory_manager import MemoryManager


# # =============================================================================
# # ⚖️ AUTHORITY LAYER — CONTRACT v1.2
# #
# # Canonical Principles:
# # - Authority is the ONLY component allowed to approve or deny state mutation.
# # - Authority owns legality, safety, deferral, and optimistic mutation permits.
# # - LLMs, Routers, and Agents may be optimistic or incorrect.
# # - Authority MUST NOT be wrong.
# #
# # Canonical Output Rule:
# # - ViolationType is the canonical decision signal.
# # - RejectionCode exists ONLY for backward compatibility and UX mapping.
# #
# # Context Ownership (v1.2 change):
# # - decide_context_scope now accepts user_input and delegates structural
# #   classification to QueryClassifier.
# # - This replaces the intent-only check from v1.1 which could not see the
# #   raw query and therefore could not classify attribute-style questions.
# #
# # Any action reaching Authority may be fuzzy, inferred, or incomplete.
# # Authority alone decides whether it is:
# #   - Allowed
# #   - Recoverable
# #   - Deferred
# #   - Fatal
# # =============================================================================


# HIGH_KITCHEN_LOAD_THRESHOLD = 85
# MAX_COMPLEXITY_WHEN_BUSY = 3
# LOW_CONFIDENCE_THRESHOLD = 0.7


# # 🆕 Jurisdictional Matrix: Which agents can legally handle which intents
# AGENT_PERMISSION_MATRIX = {
#     "OrderTaker": {IntentType.ORDERING, IntentType.GREETING},
#     "MenuExpert": {IntentType.INQUIRY, IntentType.GREETING},
#     "Greeter": {IntentType.GREETING}
# }


# # QueryClassifier is instantiated lazily on first call to decide_context_scope.
# # It cannot be instantiated here at module load time because all_menu_items
# # is not yet available — the registry is bootstrapped in golden_loop.py.
# # The classifier is then cached for the lifetime of the process.
# _query_classifier: QueryClassifier | None = None


# def _get_classifier(all_menu_items: list) -> QueryClassifier:
#     """
#     Returns the shared QueryClassifier instance, creating it on first call.
#     Thread-safe for read-heavy workloads (construction is idempotent).
#     """
#     global _query_classifier
#     if _query_classifier is None:
#         _query_classifier = QueryClassifier(all_menu_items)
#     return _query_classifier


# def evaluate_action(
#     action: ActionRequest,
#     session: SessionState,
#     menu_item: MenuItemSnapshot | None,
#     kitchen: KitchenSnapshot,
#     all_menu_items: List[MenuItemSnapshot],
#     memory: MemoryManager
# ) -> ValidationResult:
#     """
#     ⚖️ AUTHORITY — SUPREME COURT

#     Final arbiter of all proposed actions.

#     Responsibilities:
#     - Enforce jurisdictional legality
#     - Validate irreversible mutations
#     - Classify violations (FATAL / RECOVERABLE / DEFERRED)
#     - Control optimistic mutation permits
#     """

#     # 1️⃣ ⚖️ JURISDICTION CHECK (NEGATIVE POWER)
#     if action.intent and session.active_agent in AGENT_PERMISSION_MATRIX:
#         allowed_intents = AGENT_PERMISSION_MATRIX[session.active_agent]
#         if action.intent not in allowed_intents:
#             # 🔐 Authority decides the correct jurisdiction
#             target_agent = None
#             for agent, intents in AGENT_PERMISSION_MATRIX.items():
#                 if action.intent in intents:
#                     target_agent = agent
#                     break
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_STATE,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=False,
#                 rejection_code=RejectionCode.ERR_INVALID_STATE,
#                 user_message="I should let our Menu Expert handle that inquiry for you.",
#                 system_hint=f"JURISDICTION_MISMATCH: Agent {session.active_agent} cannot handle {action.intent}",
#                 meta={"target_agent": target_agent}
#             )

#     # 2️⃣ ORDER STATE CHECK — SEMANTIC TRUTH (INVALID_STATE + FATAL)
#     if session.order_status == "CONFIRMED" and action.action_type != ActionType.ASK_CLARIFICATION:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_STATE,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.ERR_INVALID_STATE,
#             requires_clarification=False,
#             user_message="Your order is already being prepared. I can help you check its status!"
#         )

#     # 3️⃣ TOOL BUDGET CHECK (FATAL)
#     if session.tool_budget_remaining <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.BUDGET_EXCEEDED,
#             severity=Severity.FATAL,
#             rejection_code=RejectionCode.BUDGET_EXCEEDED,
#             user_message="I've reached my limit for complex requests this session. For simple orders, please continue — or start a new session."
#         )

#     # 4️⃣ QUANTITY VALIDATION
#     if action.action_type in {ActionType.ADD_TO_CART, ActionType.REMOVE_FROM_CART} and action.quantity <= 0:
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.INVALID_QUANTITY,
#             severity=Severity.RECOVERABLE,
#             rejection_code=RejectionCode.ERR_INVALID_QUANTITY,
#             requires_clarification=True,
#             user_message="Quantity must be at least 1."
#         )

#     # 5️⃣ SKU & AMBIGUITY VALIDATION (AUTHORITY-OWNED)
#     requires_sku = action.action_type in {
#         ActionType.ADD_TO_CART,
#         ActionType.MODIFY_ITEM,
#         ActionType.REMOVE_FROM_CART
#     }

#     if requires_sku:
#         if not action.sku:
#             ambiguity_result = _check_category_ambiguity(action, all_menu_items)
#             if ambiguity_result:
#                 return ambiguity_result

#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I'm not sure which item you'd like. Could you specify?"
#             )

#         if not menu_item:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.FATAL,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message="I couldn't find that item on our current menu."
#             )

#     # 6️⃣ BUSINESS RULES — STOCK (RECOVERABLE) & ALCOHOL (DEFERRED)
#     if menu_item:
#         if not menu_item.in_stock:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.INVALID_SKU,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
#                 user_message=f"I'm sorry, the {menu_item.name} is currently out of stock."
#             )

#         if menu_item.is_alcohol and not session.age_verified:
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.AGE_RESTRICTION,
#                 severity=Severity.DEFERRED,
#                 requires_clarification=False,
#                 rejection_code=RejectionCode.ERR_AGE_RESTRICTION,
#                 user_message="I'll need to verify your ID before adding alcohol.",
#                 meta={"required_capability": "ID_VERIFIER"}
#             )

#     # 7️⃣ KITCHEN LOAD THROTTLING (DEFERRED)
#     if (
#         kitchen.load_percentage >= HIGH_KITCHEN_LOAD_THRESHOLD and
#         menu_item and menu_item.complexity_score > MAX_COMPLEXITY_WHEN_BUSY
#     ):
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.KITCHEN_OVERLOAD,
#             severity=Severity.DEFERRED,
#             rejection_code=RejectionCode.ERR_KITCHEN_OVERLOAD,
#             user_message="Our kitchen is extremely busy right now. Can I suggest something quicker?"
#         )

#     # 8️⃣ 🛡️ OPTIMISTIC MUTATION AUTHORIZATION
#     mutating_actions = {
#         ActionType.ADD_TO_CART,
#         ActionType.REMOVE_FROM_CART,
#         ActionType.MODIFY_ITEM
#     }

#     if action.action_type in mutating_actions:
#         if not _is_optimistic_mutation_authorized(action, session, memory):
#             item_name = menu_item.name if menu_item else "that item"
#             return ValidationResult(
#                 approved=False,
#                 violation_type=ViolationType.LOW_CONFIDENCE,
#                 severity=Severity.RECOVERABLE,
#                 requires_clarification=True,
#                 rejection_code=RejectionCode.ERR_LOW_CONFIDENCE,
#                 user_message=(
#                     f"I see you're referring to {item_name}. "
#                     "Would you like me to add it to your order, or would you like to know more about it?"
#                 ),
#                 system_hint="OPTIMISM_DENIED: No explicit intent or active ordering context."
#             )

#     return ValidationResult(
#         approved=True,
#         system_hint=getattr(session, "authority_hint", "Validated."),
#         meta={"context_scope": session.context_scope}
#     )


# def _check_category_ambiguity(
#     action: ActionRequest,
#     all_menu_items: List[MenuItemSnapshot]
# ) -> ValidationResult | None:
#     """Detects if a category-level intent maps to multiple menu items."""

#     if not action.meta or "attempted_category" not in action.meta:
#         return None

#     cat = action.meta["attempted_category"].lower()
#     matches = [i for i in all_menu_items if cat in i.name.lower()]

#     if len(matches) > 1:
#         options = ", ".join(f"{i.name} (${i.price})" for i in matches)
#         return ValidationResult(
#             approved=False,
#             violation_type=ViolationType.AMBIGUOUS_CATEGORY,
#             severity=Severity.RECOVERABLE,
#             requires_clarification=True,
#             rejection_code=RejectionCode.ERR_AMBIGUOUS_CATEGORY,
#             user_message=f"Which {cat} did you mean? We have: {options}"
#         )

#     return None


# def decide_context_scope(session: SessionState, user_input: str, all_menu_items: list = None) -> Dict[str, Any]:
#     """
#     ⚖️ CONTEXT SCOPE POLICY — v1.2 (QueryClassifier-backed)

#     Replaces the v1.1 intent-only check with structural query classification.

#     v1.1 problem: Only checked session.active_intent (INQUIRY vs. not).
#     This meant "Do you have anything spicy?" would only get FULL_CATALOG if
#     the router had already set intent=INQUIRY — a fragile dependency.

#     v1.2 fix: QueryClassifier reads the raw user_input and classifies based
#     on grammatical structure:
#       - ENTITY_BOUND  → FILTERED_SEARCH  (user named a specific item)
#       - ATTRIBUTE_BOUND → FULL_CATALOG   (user asked about a property)
#       - AMBIGUOUS     → FULL_CATALOG     (safe default: fail toward more data)

#     The session intent is used as a secondary signal — if the classifier
#     returns ENTITY_BOUND but the intent is INQUIRY, we still elevate to
#     FULL_CATALOG because the intent signal has higher semantic authority
#     in that case (the router saw something the grammar check missed).

#     Args:
#         session:        Current session state (intent used as secondary signal).
#         user_input:     Raw user query — primary input for classification.
#         all_menu_items: Menu data for name-index construction. Optional because
#                         the classifier is cached after first call; pass on first
#                         call or whenever the menu changes.
#     """
#     # Resolve classifier (lazy init, cached after first call)
#     # If all_menu_items not passed and classifier not yet built, we fall back
#     # gracefully to intent-only logic rather than crashing.
#     classifier = _get_classifier(all_menu_items) if all_menu_items else _query_classifier

#     # ── Primary Path: Structural Classification ────────────────────────────────
#     # Check `is not None` explicitly — empty string is valid input that the classifier
#     # handles correctly (returns AMBIGUOUS → FULL_CATALOG). Truthiness check would
#     # treat "" as "no input", skip the classifier, and return FILTERED_SEARCH.
#     if classifier and user_input is not None:
#         classification = classifier.classify(user_input)

#         # Attach classification trace to the policy for logging/debugging
#         base_meta = {
#             "classifier_class": classification.query_class.value,
#             "classifier_confidence": classification.confidence,
#             "classifier_reasoning": classification.reasoning,
#             "resolved_entity": classification.resolved_entity,
#         }

#         # ENTITY_BOUND: use filtered search UNLESS intent overrides
#         if classification.query_class == QueryClass.ENTITY_BOUND:
#             # Secondary signal: if router independently flagged this as an INQUIRY,
#             # trust the router — the user may be asking about a named item's properties
#             # (e.g., "Is the Pepperoni Pizza spicy?") which still benefits from full context.
#             if getattr(session, "active_intent", None) == IntentType.INQUIRY:
#                 return {
#                     "context_scope": ContextScope.FULL_CATALOG,
#                     "system_hint": "Entity-bound query but INQUIRY intent: Full catalog authorized.",
#                     **base_meta
#                 }
#             return {
#                 "context_scope": ContextScope.FILTERED_SEARCH,
#                 "system_hint": f"Entity-bound query. Targeted search authorized. Entity: {classification.resolved_entity}",
#                 **base_meta
#             }

#         # ATTRIBUTE_BOUND or AMBIGUOUS: always full catalog
#         return {
#             "context_scope": ContextScope.FULL_CATALOG,
#             "system_hint": f"{'Attribute' if classification.query_class == QueryClass.ATTRIBUTE_BOUND else 'Ambiguous'} query: Full catalog access authorized.",
#             **base_meta
#         }

#     # ── Fallback Path: No classifier or empty input ────────────────────────────
#     # Mirrors v1.1 behavior as a last resort. Should not be reached in normal flow.
#     scope = ContextScope.FILTERED_SEARCH
#     hint = "Standard context applied (classifier unavailable — fallback to intent check)."

#     if getattr(session, "active_intent", None) == IntentType.INQUIRY:
#         scope = ContextScope.FULL_CATALOG
#         hint = "Broad inquiry intent detected (fallback path): Full catalog access authorized."

#     return {"context_scope": scope, "system_hint": hint}


# def _is_optimistic_mutation_authorized(
#     action: ActionRequest,
#     session: SessionState,
#     memory: Any
# ) -> bool:
#     """
#     ⚖️ OPTIMISTIC MUTATION AUTHORIZATION — SYSTEMATIC (v1.0)

#     Allows noun-only mutations ONLY when the system can PROVE
#     the user is responding to a clarification request.
#     """

#     # 1️⃣ Explicit intent (hard override)
#     if action.confidence >= 1.0:
#         return True

#     # Defensive guard
#     if not memory or not getattr(memory, "window", None) or not memory.window:
#         return False

#     last_turn = memory.window[-1]

#     # 2️⃣ SYSTEMATIC CLARIFICATION LOOP (PRIMARY SIGNAL)
#     if last_turn.get("status") in {
#         "agent_clarification",
#         "authority_clarification"
#     }:
#         return True

#     # 3️⃣ MenuExpert safety block (prevents inquiry → accidental add)
#     if last_turn.get("agent") == "MenuExpert":
#         return False

#     # 4️⃣ Existing cart = active ordering context
#     if session.cart:
#         return True

#     return False


# DineFlow/state_machine/authority.py
from typing import List, Dict, Any
from state_machine.types import SessionState, MenuItemSnapshot, KitchenSnapshot, ContextScope
from state_machine.query_classifier import QueryClassifier, QueryClass
from validation.schemas import ActionRequest, ValidationResult, ActionType, IntentType
from validation.errors import RejectionCode, ViolationType, Severity
from orchestration.memory_manager import MemoryManager


# =============================================================================
# ⚖️ AUTHORITY LAYER — CONTRACT v1.2
#
# Canonical Principles:
# - Authority is the ONLY component allowed to approve or deny state mutation.
# - Authority owns legality, safety, deferral, and optimistic mutation permits.
# - LLMs, Routers, and Agents may be optimistic or incorrect.
# - Authority MUST NOT be wrong.
#
# Canonical Output Rule:
# - ViolationType is the canonical decision signal.
# - RejectionCode exists ONLY for backward compatibility and UX mapping.
#
# Context Ownership (v1.2 change):
# - decide_context_scope now accepts user_input and delegates structural
#   classification to QueryClassifier.
# - This replaces the intent-only check from v1.1 which could not see the
#   raw query and therefore could not classify attribute-style questions.
#
# Any action reaching Authority may be fuzzy, inferred, or incomplete.
# Authority alone decides whether it is:
#   - Allowed
#   - Recoverable
#   - Deferred
#   - Fatal
# =============================================================================


HIGH_KITCHEN_LOAD_THRESHOLD = 85
MAX_COMPLEXITY_WHEN_BUSY = 3
LOW_CONFIDENCE_THRESHOLD = 0.7


# 🆕 Jurisdictional Matrix: Which agents can legally handle which intents
AGENT_PERMISSION_MATRIX = {
    "OrderTaker": {IntentType.ORDERING, IntentType.GREETING},
    "MenuExpert": {IntentType.INQUIRY, IntentType.GREETING},
    "Greeter": {IntentType.GREETING}
}


# QueryClassifier is instantiated lazily on first call to decide_context_scope.
# It cannot be instantiated here at module load time because all_menu_items
# is not yet available — the registry is bootstrapped in golden_loop.py.
# The classifier is then cached for the lifetime of the process.
_query_classifier: QueryClassifier | None = None


def _get_classifier(all_menu_items: list) -> QueryClassifier:
    """
    Returns the shared QueryClassifier instance, creating it on first call.
    Thread-safe for read-heavy workloads (construction is idempotent).
    """
    global _query_classifier
    if _query_classifier is None:
        _query_classifier = QueryClassifier(all_menu_items)
    return _query_classifier


def evaluate_action(
    action: ActionRequest,
    session: SessionState,
    menu_item: MenuItemSnapshot | None,
    kitchen: KitchenSnapshot,
    all_menu_items: List[MenuItemSnapshot],
    memory: MemoryManager
) -> ValidationResult:
    """
    ⚖️ AUTHORITY — SUPREME COURT

    Final arbiter of all proposed actions.

    Responsibilities:
    - Enforce jurisdictional legality
    - Validate irreversible mutations
    - Classify violations (FATAL / RECOVERABLE / DEFERRED)
    - Control optimistic mutation permits
    """

    # 1️⃣ ⚖️ JURISDICTION CHECK (NEGATIVE POWER)
    if action.intent and session.active_agent in AGENT_PERMISSION_MATRIX:
        allowed_intents = AGENT_PERMISSION_MATRIX[session.active_agent]
        if action.intent not in allowed_intents:
            # 🔐 Authority decides the correct jurisdiction
            target_agent = None
            for agent, intents in AGENT_PERMISSION_MATRIX.items():
                if action.intent in intents:
                    target_agent = agent
                    break
            return ValidationResult(
                approved=False,
                violation_type=ViolationType.INVALID_STATE,
                severity=Severity.RECOVERABLE,
                requires_clarification=False,
                rejection_code=RejectionCode.ERR_INVALID_STATE,
                user_message="I should let our Menu Expert handle that inquiry for you.",
                system_hint=f"JURISDICTION_MISMATCH: Agent {session.active_agent} cannot handle {action.intent}",
                meta={"target_agent": target_agent}
            )

    # 2️⃣ ORDER STATE CHECK — SEMANTIC TRUTH (INVALID_STATE + FATAL)
    if session.order_status == "CONFIRMED" and action.action_type != ActionType.ASK_CLARIFICATION:
        return ValidationResult(
            approved=False,
            violation_type=ViolationType.INVALID_STATE,
            severity=Severity.FATAL,
            rejection_code=RejectionCode.ERR_INVALID_STATE,
            requires_clarification=False,
            user_message="Your order is already being prepared. I can help you check its status!"
        )

    # 3️⃣ TOOL BUDGET CHECK (FATAL)
    if session.tool_budget_remaining <= 0:
        return ValidationResult(
            approved=False,
            violation_type=ViolationType.BUDGET_EXCEEDED,
            severity=Severity.FATAL,
            rejection_code=RejectionCode.BUDGET_EXCEEDED,
            user_message="I've reached my limit for complex requests this session. For simple orders, please continue — or start a new session."
        )

    # 4️⃣ QUANTITY VALIDATION
    if action.action_type in {ActionType.ADD_TO_CART, ActionType.REMOVE_FROM_CART} and action.quantity <= 0:
        return ValidationResult(
            approved=False,
            violation_type=ViolationType.INVALID_QUANTITY,
            severity=Severity.RECOVERABLE,
            rejection_code=RejectionCode.ERR_INVALID_QUANTITY,
            requires_clarification=True,
            user_message="Quantity must be at least 1."
        )

    # 5️⃣ SKU & AMBIGUITY VALIDATION (AUTHORITY-OWNED)
    requires_sku = action.action_type in {
        ActionType.ADD_TO_CART,
        ActionType.MODIFY_ITEM,
        ActionType.REMOVE_FROM_CART
    }

    if requires_sku:
        if not action.sku:
            ambiguity_result = _check_category_ambiguity(action, all_menu_items)
            if ambiguity_result:
                return ambiguity_result

            return ValidationResult(
                approved=False,
                violation_type=ViolationType.INVALID_SKU,
                severity=Severity.RECOVERABLE,
                requires_clarification=True,
                rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
                user_message="I'm not sure which item you'd like. Could you specify?"
            )

        if not menu_item:
            return ValidationResult(
                approved=False,
                violation_type=ViolationType.INVALID_SKU,
                severity=Severity.FATAL,
                rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
                user_message="I couldn't find that item on our current menu."
            )

    # 6️⃣ BUSINESS RULES — STOCK (RECOVERABLE) & ALCOHOL (DEFERRED)
    if menu_item:
        if not menu_item.in_stock:
            return ValidationResult(
                approved=False,
                violation_type=ViolationType.INVALID_SKU,
                severity=Severity.RECOVERABLE,
                requires_clarification=True,
                rejection_code=RejectionCode.ERR_ITEM_NOT_FOUND,
                user_message=f"I'm sorry, the {menu_item.name} is currently out of stock."
            )

        if menu_item.is_alcohol and not session.age_verified:
            return ValidationResult(
                approved=False,
                violation_type=ViolationType.AGE_RESTRICTION,
                severity=Severity.DEFERRED,
                requires_clarification=False,
                rejection_code=RejectionCode.ERR_AGE_RESTRICTION,
                user_message="I'll need to verify your ID before adding alcohol.",
                meta={"required_capability": "ID_VERIFIER"}
            )

    # 7️⃣ KITCHEN LOAD THROTTLING (DEFERRED)
    if (
        kitchen.load_percentage >= HIGH_KITCHEN_LOAD_THRESHOLD and
        menu_item and menu_item.complexity_score > MAX_COMPLEXITY_WHEN_BUSY
    ):
        return ValidationResult(
            approved=False,
            violation_type=ViolationType.KITCHEN_OVERLOAD,
            severity=Severity.DEFERRED,
            rejection_code=RejectionCode.ERR_KITCHEN_OVERLOAD,
            user_message="Our kitchen is extremely busy right now. Can I suggest something quicker?"
        )

    # 8️⃣ 🛡️ OPTIMISTIC MUTATION AUTHORIZATION
    mutating_actions = {
        ActionType.ADD_TO_CART,
        ActionType.REMOVE_FROM_CART,
        ActionType.MODIFY_ITEM
    }

    if action.action_type in mutating_actions:
        if not _is_optimistic_mutation_authorized(action, session, memory):
            item_name = menu_item.name if menu_item else "that item"
            return ValidationResult(
                approved=False,
                violation_type=ViolationType.LOW_CONFIDENCE,
                severity=Severity.RECOVERABLE,
                requires_clarification=True,
                rejection_code=RejectionCode.ERR_LOW_CONFIDENCE,
                user_message=(
                    f"I see you're referring to {item_name}. "
                    "Would you like me to add it to your order, or would you like to know more about it?"
                ),
                system_hint="OPTIMISM_DENIED: No explicit intent or active ordering context."
            )

    # Determine if this approval was contextually clear — i.e. the system
    # had strong contextual evidence (active cart, clarification loop, or
    # explicit confidence) that justified the action even at low confidence.
    # This signal is used by consume_tool_budget to decide whether to
    # decrement the budget. If contextually clear, no budget is consumed
    # regardless of raw confidence score.
    contextually_clear = (
        action.confidence >= 1.0
        or bool(session.cart)
        or (
            memory.window
            and memory.window[-1].get("status") in {
                "agent_clarification",
                "authority_clarification"
            }
        )
    )

    return ValidationResult(
        approved=True,
        system_hint=getattr(session, "authority_hint", "Validated."),
        meta={
            "context_scope": session.context_scope,
            "contextually_clear": contextually_clear,
        }
    )


def _check_category_ambiguity(
    action: ActionRequest,
    all_menu_items: List[MenuItemSnapshot]
) -> ValidationResult | None:
    """Detects if a category-level intent maps to multiple menu items."""

    if not action.meta or "attempted_category" not in action.meta:
        return None

    cat = action.meta["attempted_category"].lower()
    matches = [i for i in all_menu_items if cat in i.name.lower()]

    if len(matches) > 1:
        options = ", ".join(f"{i.name} (${i.price})" for i in matches)
        return ValidationResult(
            approved=False,
            violation_type=ViolationType.AMBIGUOUS_CATEGORY,
            severity=Severity.RECOVERABLE,
            requires_clarification=True,
            rejection_code=RejectionCode.ERR_AMBIGUOUS_CATEGORY,
            user_message=f"Which {cat} did you mean? We have: {options}"
        )

    return None


def decide_context_scope(session: SessionState, user_input: str, all_menu_items: list = None) -> Dict[str, Any]:
    """
    ⚖️ CONTEXT SCOPE POLICY — v1.2 (QueryClassifier-backed)

    Replaces the v1.1 intent-only check with structural query classification.

    v1.1 problem: Only checked session.active_intent (INQUIRY vs. not).
    This meant "Do you have anything spicy?" would only get FULL_CATALOG if
    the router had already set intent=INQUIRY — a fragile dependency.

    v1.2 fix: QueryClassifier reads the raw user_input and classifies based
    on grammatical structure:
      - ENTITY_BOUND  → FILTERED_SEARCH  (user named a specific item)
      - ATTRIBUTE_BOUND → FULL_CATALOG   (user asked about a property)
      - AMBIGUOUS     → FULL_CATALOG     (safe default: fail toward more data)

    The session intent is used as a secondary signal — if the classifier
    returns ENTITY_BOUND but the intent is INQUIRY, we still elevate to
    FULL_CATALOG because the intent signal has higher semantic authority
    in that case (the router saw something the grammar check missed).

    Args:
        session:        Current session state (intent used as secondary signal).
        user_input:     Raw user query — primary input for classification.
        all_menu_items: Menu data for name-index construction. Optional because
                        the classifier is cached after first call; pass on first
                        call or whenever the menu changes.
    """
    # Resolve classifier (lazy init, cached after first call)
    # If all_menu_items not passed and classifier not yet built, we fall back
    # gracefully to intent-only logic rather than crashing.
    classifier = _get_classifier(all_menu_items) if all_menu_items else _query_classifier

    # ── Primary Path: Structural Classification ────────────────────────────────
    # Check `is not None` explicitly — empty string is valid input that the classifier
    # handles correctly (returns AMBIGUOUS → FULL_CATALOG). Truthiness check would
    # treat "" as "no input", skip the classifier, and return FILTERED_SEARCH.
    if classifier and user_input is not None:
        classification = classifier.classify(user_input)

        # Attach classification trace to the policy for logging/debugging
        base_meta = {
            "classifier_class": classification.query_class.value,
            "classifier_confidence": classification.confidence,
            "classifier_reasoning": classification.reasoning,
            "resolved_entity": classification.resolved_entity,
        }

        # ENTITY_BOUND: use filtered search UNLESS intent overrides
        if classification.query_class == QueryClass.ENTITY_BOUND:
            # Secondary signal: if router independently flagged this as an INQUIRY,
            # trust the router — the user may be asking about a named item's properties
            # (e.g., "Is the Pepperoni Pizza spicy?") which still benefits from full context.
            if getattr(session, "active_intent", None) == IntentType.INQUIRY:
                return {
                    "context_scope": ContextScope.FULL_CATALOG,
                    "system_hint": "Entity-bound query but INQUIRY intent: Full catalog authorized.",
                    **base_meta
                }
            return {
                "context_scope": ContextScope.FILTERED_SEARCH,
                "system_hint": f"Entity-bound query. Targeted search authorized. Entity: {classification.resolved_entity}",
                **base_meta
            }

        # ATTRIBUTE_BOUND or AMBIGUOUS: always full catalog
        return {
            "context_scope": ContextScope.FULL_CATALOG,
            "system_hint": f"{'Attribute' if classification.query_class == QueryClass.ATTRIBUTE_BOUND else 'Ambiguous'} query: Full catalog access authorized.",
            **base_meta
        }

    # ── Fallback Path: No classifier or empty input ────────────────────────────
    # Mirrors v1.1 behavior as a last resort. Should not be reached in normal flow.
    scope = ContextScope.FILTERED_SEARCH
    hint = "Standard context applied (classifier unavailable — fallback to intent check)."

    if getattr(session, "active_intent", None) == IntentType.INQUIRY:
        scope = ContextScope.FULL_CATALOG
        hint = "Broad inquiry intent detected (fallback path): Full catalog access authorized."

    return {"context_scope": scope, "system_hint": hint}


def _is_optimistic_mutation_authorized(
    action: ActionRequest,
    session: SessionState,
    memory: Any
) -> bool:
    """
    ⚖️ OPTIMISTIC MUTATION AUTHORIZATION — SYSTEMATIC (v1.0)

    Allows noun-only mutations ONLY when the system can PROVE
    the user is responding to a clarification request.
    """

    # 1️⃣ Explicit intent (hard override)
    if action.confidence >= 1.0:
        return True

    # Defensive guard
    if not memory or not getattr(memory, "window", None) or not memory.window:
        return False

    last_turn = memory.window[-1]

    # 2️⃣ SYSTEMATIC CLARIFICATION LOOP (PRIMARY SIGNAL)
    if last_turn.get("status") in {
        "agent_clarification",
        "authority_clarification"
    }:
        return True

    # 3️⃣ MenuExpert safety block (prevents inquiry → accidental add)
    if last_turn.get("agent") == "MenuExpert":
        return False

    # 4️⃣ Existing cart = active ordering context
    if session.cart:
        return True

    return False