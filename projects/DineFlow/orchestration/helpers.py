# aiva/orchestration/helpers
# from pathlib import Path
# from typing import List, Optional
# from aiva.state_machine.types import MenuItemSnapshot, SessionState
# from aiva.validation.schemas import ActionRequest, ActionType


# def load_order_taker_prompt() -> str:
#     """
#     Loads the Order Taker system prompt from disk using robust absolute paths.
#     """
#     # Ensures path resolution works regardless of where the app is launched from
#     base_dir = Path(__file__).parent.parent
#     prompt_path = base_dir / "llm" / "prompts" / "order_taker.md"
    
#     # Specify encoding to prevent OS-specific read errors
#     return prompt_path.read_text(encoding="utf-8")

# def render_menu_context(*, menu_items: List[MenuItemSnapshot]) -> str:
#     """
#     Generates a clean, readable string of the current menu.
#     """
#     return "\n".join(
#         f"- {item.sku}: {item.name} (${item.price})"
#         for item in menu_items
#     )


# def resolve_menu_item(
#     menu_items: List[MenuItemSnapshot],
#     sku: Optional[str],
# ) -> Optional[MenuItemSnapshot]:
#     """
#     Finds the specific item object from the list based on SKU.
#     """
#     if not sku:
#         return None

#     # Case-insensitive matching is a pro-move for production robustness
#     search_sku = sku.strip().upper()
#     return next(
#         (item for item in menu_items if item.sku.upper() == search_sku),
#         None,
#     )

# def consume_tool_budget(session: SessionState) -> None:
#     """
#     Decrements budget. Note: Actual enforcement (blocking) 
#     happens inside authority.py or golden_loop.py.
#     """
#     session.tool_budget_remaining -= 1


# def apply_approved_action(session: SessionState, action: ActionRequest) -> None:
#     """
#     Handles all state changes for an approved action and notifies the kitchen.
#     """
#     if action.action_type == ActionType.ADD_TO_CART:
#         sku = action.sku
#         qty = action.quantity or 1
        
#         # 1. Update Cart State
#         session.cart[sku] = session.cart.get(sku, 0) + qty

#     elif action.action_type == ActionType.REMOVE_FROM_CART:
#         sku = action.sku
#         if sku in session.cart:
#             del session.cart[sku]






# # DineFlow/orchestration/helpers.py
# from pathlib import Path
# from typing import List, Optional
# from state_machine.types import MenuItemSnapshot, SessionState
# from validation.schemas import ActionRequest, ActionType


# def load_order_taker_prompt() -> str:
#     """
#     Loads the Order Taker system prompt from disk using robust absolute paths.
#     """
#     base_dir = Path(__file__).parent.parent
#     prompt_path = base_dir / "llm" / "prompts" / "order_taker.md"
#     return prompt_path.read_text(encoding="utf-8")


# def render_menu_context(*, menu_items: List[MenuItemSnapshot]) -> str:
#     """
#     Generates a clean, readable string of the current menu.
#     """
#     return "\n".join(
#         f"- {item.sku}: {item.name} (${item.price})"
#         for item in menu_items
#     )


# def resolve_menu_item(
#     menu_items: List[MenuItemSnapshot],
#     sku: Optional[str],
# ) -> Optional[MenuItemSnapshot]:
#     """
#     Finds the specific item object from the list based on SKU.
#     """
#     if not sku:
#         return None

#     search_sku = sku.strip().upper()
#     return next(
#         (item for item in menu_items if item.sku.upper() == search_sku),
#         None,
#     )


# def consume_tool_budget(session: SessionState) -> None:
#     """
#     Decrements budget. Actual enforcement happens in authority.py.
#     """
#     session.tool_budget_remaining -= 1


# def apply_approved_action(session: SessionState, action: ActionRequest) -> None:
#     """
#     Handles all state changes for an approved action.
#     Applies cart mutations based on action type.
#     """
#     if action.action_type == ActionType.ADD_TO_CART:
#         sku = action.sku
#         qty = action.quantity or 1
        
#         # Update cart state
#         session.cart[sku] = session.cart.get(sku, 0) + qty

#     elif action.action_type == ActionType.REMOVE_FROM_CART:
#         sku = action.sku
#         qty = action.quantity or 1  # 🔧 FIX: Default to removing 1 item
        
#         if sku in session.cart:
#             current_qty = session.cart[sku]
            
#             if current_qty <= qty:
#                 # Remove entire item if removing all or more than exists
#                 del session.cart[sku]
#             else:
#                 # Reduce quantity
#                 session.cart[sku] = current_qty - qty
    
#     elif action.action_type == ActionType.MODIFY_ITEM:
#         # 🔧 FIX: Handle modifications
#         # For now, we just ensure the item exists in cart
#         # Future: Could store notes in a separate session.cart_notes dict
#         if action.sku and action.sku not in session.cart:
#             # Can't modify an item that's not in the cart
#             pass  # Authority layer should have caught this
#         # Modification logic could be extended here based on action.notes





# claud recent version testing.....
# # DineFlow/orchestration/helpers.py
# from pathlib import Path
# from typing import List, Optional
# from state_machine.types import MenuItemSnapshot, SessionState
# from validation.schemas import ActionRequest, ActionType


# def load_order_taker_prompt() -> str:
#     """
#     Loads the Order Taker system prompt from disk using robust absolute paths.
#     """
#     base_dir = Path(__file__).parent.parent
#     prompt_path = base_dir / "llm" / "prompts" / "order_taker.md"
#     return prompt_path.read_text(encoding="utf-8")


# def render_menu_context(*, menu_items: List[MenuItemSnapshot]) -> str:
#     """
#     Generates a readable menu string injected into {{MENU_CONTEXT}} in agent prompts.

#     ── Why This Function Is the Final Gate ──────────────────────────────────
#     Even if the QueryClassifier sets FULL_CATALOG, and hybrid_search returns
#     the correct items, the LLM still sees nothing useful if this function only
#     renders name and price. This is the last point where data reaches the model.

#     ── Format Design ────────────────────────────────────────────────────────
#     Each item renders as:
#         - Pepperoni Pizza ($12.99): Classic pizza loaded with spicy pepperoni...
#           [spicy, hot, classic, pork, pepperoni, popular]

#     The description is on the same line so the LLM reads item + attributes
#     as a single coherent unit. Tags are on an indented second line so they
#     don't break the prose flow but remain visible for attribute reasoning.

#     Items with no description or tags (e.g. legacy fixtures, test stubs)
#     render gracefully — the fields default to "" and [] in MenuItemSnapshot,
#     so no KeyError or AttributeError is possible.
#     """
#     lines = []
#     for item in menu_items:
#         # Base line: name and price are always present
#         line = f"- {item.name} (${item.price:.2f})"

#         # Append description if present
#         if item.description:
#             line += f": {item.description}"

#         lines.append(line)

#         # Append tags on an indented second line if present
#         if item.tags:
#             lines.append(f"  [Tags: {', '.join(item.tags)}]")

#     return "\n".join(lines)


# def resolve_menu_item(
#     menu_items: List[MenuItemSnapshot],
#     sku: Optional[str],
# ) -> Optional[MenuItemSnapshot]:
#     """
#     Finds the specific item object from the list based on SKU.
#     """
#     if not sku:
#         return None

#     search_sku = sku.strip().upper()
#     return next(
#         (item for item in menu_items if item.sku.upper() == search_sku),
#         None,
#     )


# def consume_tool_budget(session: SessionState) -> None:
#     """
#     Decrements budget. Actual enforcement happens in authority.py.
#     """
#     session.tool_budget_remaining -= 1


# def apply_approved_action(session: SessionState, action: ActionRequest) -> None:
#     """
#     Handles all state changes for an approved action.
#     Applies cart mutations based on action type.
#     """
#     if action.action_type == ActionType.ADD_TO_CART:
#         sku = action.sku
#         qty = action.quantity or 1
#         session.cart[sku] = session.cart.get(sku, 0) + qty

#     elif action.action_type == ActionType.REMOVE_FROM_CART:
#         sku = action.sku
#         qty = action.quantity or 1

#         if sku in session.cart:
#             current_qty = session.cart[sku]
#             if current_qty <= qty:
#                 del session.cart[sku]
#             else:
#                 session.cart[sku] = current_qty - qty

#     elif action.action_type == ActionType.MODIFY_ITEM:
#         if action.sku and action.sku not in session.cart:
#             pass  # Authority layer should have caught this

# new after fix
# # DineFlow/orchestration/helpers.py
# from pathlib import Path
# from typing import List, Optional
# from state_machine.types import MenuItemSnapshot, SessionState
# from validation.schemas import ActionRequest, ActionType


# def load_order_taker_prompt() -> str:
#     base_dir = Path(__file__).parent.parent
#     prompt_path = base_dir / "llm" / "prompts" / "order_taker.md"
#     return prompt_path.read_text(encoding="utf-8")


# def render_menu_context(*, menu_items: List[MenuItemSnapshot], include_skus: bool = False) -> str:
#     """
#     Renders menu items into a string for injection into agent prompts.

#     Args:
#         menu_items:   Items to render.
#         include_skus: Controls whether SKUs appear in the output.

#             True  — SKU leads the line, colon-separated from the name.
#                     Use for agents that must produce SKU values in their
#                     JSON output (OrderTaker, CartReviewer, CheckoutAgent).

#                     Format:
#                         - PZ-PEP: Pepperoni Pizza ($12.99)

#                     This is the original format from v1 — SKU first means
#                     the LLM sees the identifier before the human-readable
#                     name, making it the most natural value to copy into
#                     the `sku` JSON field.

#             False — SKU omitted, description and tags included.
#                     Use for read-only agents that answer questions about
#                     the menu but never produce SKU values (MenuExpert).
#                     Omitting SKUs prevents internal identifiers from being
#                     leaked to users and keeps the prompt focused on the
#                     semantic content the LLM needs to reason from.

#                     Format:
#                         - Pepperoni Pizza ($12.99): Classic pizza loaded with...
#                           [Tags: spicy, hot, classic]

#     Default is False — new agents that forget to set the flag get the safe
#     (no SKU leakage) behavior rather than the dangerous one.
#     """
#     lines = []

#     if include_skus:
#         # Original v1 format — SKU first, then name and price.
#         # Simple, unambiguous, and proven: the LLM reads left-to-right,
#         # sees the SKU before the name, and uses it correctly.
#         for item in menu_items:
#             lines.append(f"- {item.sku}: {item.name} (${item.price:.2f})")
#     else:
#         # Description-rich format for read-only agents.
#         for item in menu_items:
#             line = f"- {item.name} (${item.price:.2f})"
#             if item.description:
#                 line += f": {item.description}"
#             lines.append(line)
#             if item.tags:
#                 lines.append(f"  [Tags: {', '.join(item.tags)}]")

#     return "\n".join(lines)


# def resolve_menu_item(
#     menu_items: List[MenuItemSnapshot],
#     sku: Optional[str],
# ) -> Optional[MenuItemSnapshot]:
#     """Finds the specific item object from the list based on SKU."""
#     if not sku:
#         return None
#     search_sku = sku.strip().upper()
#     return next(
#         (item for item in menu_items if item.sku.upper() == search_sku),
#         None,
#     )


# def consume_tool_budget(session: SessionState) -> None:
#     """Decrements budget. Actual enforcement happens in authority.py."""
#     session.tool_budget_remaining -= 1


# def apply_approved_action(session: SessionState, action: ActionRequest) -> None:
#     """
#     Handles all state changes for an approved action.
#     Applies cart mutations based on action type.
#     """
#     if action.action_type == ActionType.ADD_TO_CART:
#         sku = action.sku
#         qty = action.quantity or 1
#         session.cart[sku] = session.cart.get(sku, 0) + qty

#     elif action.action_type == ActionType.REMOVE_FROM_CART:
#         sku = action.sku
#         qty = action.quantity or 1
#         if sku in session.cart:
#             current_qty = session.cart[sku]
#             if current_qty <= qty:
#                 del session.cart[sku]
#             else:
#                 session.cart[sku] = current_qty - qty

#     elif action.action_type == ActionType.MODIFY_ITEM:
#         if action.sku and action.sku not in session.cart:
#             pass  # Authority layer should have caught this



# DineFlow/orchestration/helpers.py
from pathlib import Path
from typing import List, Optional
from state_machine.types import MenuItemSnapshot, SessionState
from validation.schemas import ActionRequest, ActionType


def load_order_taker_prompt() -> str:
    base_dir = Path(__file__).parent.parent
    prompt_path = base_dir / "llm" / "prompts" / "order_taker.md"
    return prompt_path.read_text(encoding="utf-8")


def render_menu_context(*, menu_items: List[MenuItemSnapshot], include_skus: bool = False) -> str:
    """
    Renders menu items into a string for injection into agent prompts.

    Args:
        menu_items:   Items to render.
        include_skus: Controls whether SKUs appear in the output.

            True  — SKU leads the line, colon-separated from the name.
                    Use for agents that must produce SKU values in their
                    JSON output (OrderTaker, CartReviewer, CheckoutAgent).

                    Format:
                        - PZ-PEP: Pepperoni Pizza ($12.99)

            False — SKU omitted, description and tags included.
                    Use for read-only agents that answer questions about
                    the menu but never produce SKU values (MenuExpert).

                    Format:
                        - Pepperoni Pizza ($12.99): Classic pizza loaded with...
                          [Tags: spicy, hot, classic]

    Default is False — new agents that forget to set the flag get the safe
    (no SKU leakage) behavior rather than the dangerous one.
    """
    lines = []

    if include_skus:
        for item in menu_items:
            lines.append(f"- {item.sku}: {item.name} (${item.price:.2f})")
    else:
        for item in menu_items:
            line = f"- {item.name} (${item.price:.2f})"
            if item.description:
                line += f": {item.description}"
            lines.append(line)
            if item.tags:
                lines.append(f"  [Tags: {', '.join(item.tags)}]")

    return "\n".join(lines)


def resolve_menu_item(
    menu_items: List[MenuItemSnapshot],
    sku: Optional[str],
) -> Optional[MenuItemSnapshot]:
    """Finds the specific item object from the list based on SKU."""
    if not sku:
        return None
    search_sku = sku.strip().upper()
    return next(
        (item for item in menu_items if item.sku.upper() == search_sku),
        None,
    )


def consume_tool_budget(session: SessionState, action: ActionRequest, result=None) -> None:
    """
    Decrements the tool budget for genuinely ambiguous turns only.

    Budget Purpose:
        Prevents infinite agentic loops — runaway clarification cycles,
        recursive handoffs, repeated LLM calls on unresolvable input.
        It is NOT a cap on how many items a customer can order.

    Decrement Policy:
        The raw confidence score alone is not sufficient to determine whether
        budget should be consumed. A low-confidence action can still be
        contextually clear — for example:

            "pepperoni" (confidence=0.8) after "add 1 Margherita"
            → cart is not empty → ordering context proven
            → authority marked this as contextually_clear=True
            → NO budget decrement

        The authority layer encodes this judgment in result.meta["contextually_clear"].
        If that signal is True, budget is not consumed regardless of confidence.

        DECREMENT when:
            - confidence < 1.0  AND
            - result.meta["contextually_clear"] is False or absent
              (genuinely ambiguous — no cart, no clarification context,
               no explicit ordering signal)

        NO DECREMENT when:
            - confidence == 1.0 (explicit request)
            - contextually_clear == True (cart context or clarification loop
              proved intent even at low confidence)

    Examples:
        "add 2 pepperoni pizzas"          confidence=1.0               → free
        "pepperoni" (cart not empty)      confidence=0.8, clear=True   → free
        confirmed via clarification       confidence=1.0               → free
        "pepperoni" (cart empty)          confidence=0.8, clear=False  → decrements
        "something spicy" (no context)   confidence=0.7, clear=False  → decrements
    """
    if action.confidence >= 1.0:
        return

    contextually_clear = (
        result is not None
        and isinstance(result.meta, dict)
        and result.meta.get("contextually_clear", False)
    )

    if not contextually_clear:
        session.tool_budget_remaining -= 1


def apply_approved_action(session: SessionState, action: ActionRequest) -> None:
    """
    Handles all state changes for an approved action.
    Applies cart mutations based on action type.
    """
    if action.action_type == ActionType.ADD_TO_CART:
        sku = action.sku
        qty = action.quantity or 1
        session.cart[sku] = session.cart.get(sku, 0) + qty

    elif action.action_type == ActionType.REMOVE_FROM_CART:
        sku = action.sku
        qty = action.quantity or 1
        if sku in session.cart:
            current_qty = session.cart[sku]
            if current_qty <= qty:
                del session.cart[sku]
            else:
                session.cart[sku] = current_qty - qty

    elif action.action_type == ActionType.MODIFY_ITEM:
        if action.sku and action.sku not in session.cart:
            pass  # Authority layer should have caught this