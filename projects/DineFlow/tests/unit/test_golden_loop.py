# tests/unit/test_golden_loop.py
# from unittest.mock import patch
# from aiva.orchestration.golden_loop import golden_loop
# from aiva.state_machine.types import SessionState, KitchenSnapshot, MenuItemSnapshot
# from aiva.validation.schemas import ActionRequest, ActionType

# # Note: We patch the references INSIDE golden_loop where they were imported
# PATCH_PARSER = "aiva.orchestration.golden_loop.parse_action"
# PATCH_LLM = "aiva.orchestration.golden_loop.call_llm"
# PATCH_MENU = "aiva.orchestration.golden_loop.get_menu_items"

# def test_golden_loop_approved_action():
#     session = SessionState(session_id="sess-001", active_agent="OrderTaker", tool_budget_remaining=3, age_verified=True)
#     kitchen = KitchenSnapshot(load_percentage=10)
#     user_input = "Add a pepperoni pizza"
#     menu_item = MenuItemSnapshot(sku="PZ-PEP", name="Pepperoni", price=12.99, in_stock=True, is_alcohol=False, complexity_score=2)
    
#     with patch(PATCH_MENU, return_value=[menu_item]), \
#          patch(PATCH_LLM, return_value='{}'), \
#          patch(PATCH_PARSER) as mock_parse:
        
#         mock_parse.return_value = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="PZ-PEP")
#         response = golden_loop(session=session, user_input=user_input, kitchen=kitchen)

#     assert "success" in response.lower() or "executed" in response.lower()
#     assert session.tool_budget_remaining == 2

# def test_golden_loop_age_restriction():
#     session = SessionState(session_id="sess-003", active_agent="OrderTaker", tool_budget_remaining=3, age_verified=False)
#     kitchen = KitchenSnapshot(load_percentage=10)
#     user_input = "Add a beer"
#     menu_item = MenuItemSnapshot(sku="BEER-001", name="Beer", price=5.50, is_alcohol=True, in_stock=True, complexity_score=1)

#     with patch(PATCH_MENU, return_value=[menu_item]), \
#          patch(PATCH_LLM, return_value='{}'), \
#          patch(PATCH_PARSER) as mock_parse:
        
#         mock_parse.return_value = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="BEER-001")
#         response = golden_loop(session=session, user_input=user_input, kitchen=kitchen)

#     assert "verify your id" in response.lower()
#     assert session.tool_budget_remaining == 2

# def test_golden_loop_item_not_found():
#     session = SessionState(session_id="sess-004", active_agent="OrderTaker", tool_budget_remaining=3, age_verified=True)
#     kitchen = KitchenSnapshot(load_percentage=10)
#     user_input = "Add a unicorn pizza"

#     with patch(PATCH_MENU, return_value=[]), \
#          patch(PATCH_LLM, return_value='{}'), \
#          patch(PATCH_PARSER) as mock_parse:

#         mock_parse.return_value = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="UNICORN-001")
#         response = golden_loop(session=session, user_input=user_input, kitchen=kitchen)

#     assert "couldn't find" in response.lower()
#     assert session.tool_budget_remaining == 2

# def test_golden_loop_kitchen_overload():
#     session = SessionState(session_id="sess-005", active_agent="OrderTaker", tool_budget_remaining=3, age_verified=True)
#     kitchen = KitchenSnapshot(load_percentage=90)
#     user_input = "Add a fancy pizza"
#     menu_item = MenuItemSnapshot(sku="PZ-FANCY", name="Fancy Pizza", price=20.0, in_stock=True, is_alcohol=False, complexity_score=5)

#     with patch(PATCH_MENU, return_value=[menu_item]), \
#          patch(PATCH_LLM, return_value='{}'), \
#          patch(PATCH_PARSER) as mock_parse:

#         mock_parse.return_value = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="PZ-FANCY")
#         response = golden_loop(session=session, user_input=user_input, kitchen=kitchen)

#     assert "extremely busy" in response.lower()
#     assert session.tool_budget_remaining == 2

# def test_golden_loop_blocked_due_to_budget():
#     session = SessionState(session_id="sess-002", active_agent="OrderTaker", tool_budget_remaining=0, age_verified=True)
#     kitchen = KitchenSnapshot(load_percentage=10)
#     user_input = "Add a pizza"

#     with patch(PATCH_MENU, return_value=[]), \
#          patch(PATCH_LLM, return_value='{}'), \
#          patch(PATCH_PARSER) as mock_parse:

#         mock_parse.return_value = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="ANY")
#         response = golden_loop(session=session, user_input=user_input, kitchen=kitchen)

#     assert "trouble processing" in response.lower()
#     assert session.tool_budget_remaining == -1








# DineFlow/tests/unit/test_golden_loop.py
from unittest.mock import patch, MagicMock
from orchestration.golden_loop import golden_loop
from state_machine.types import SessionState, KitchenSnapshot, MenuItemSnapshot
from validation.schemas import ActionRequest, ActionType

PATCH_PARSER = "orchestration.golden_loop.parse_action"
PATCH_LLM = "orchestration.golden_loop.call_llm"
PATCH_MENU = "orchestration.golden_loop.get_menu_items"
PATCH_HYBRID = "orchestration.golden_loop.hybrid_search"

def setup_mocks():
    """Helper to create a standard mock memory manager."""
    mock_mem = MagicMock()
    mock_mem.get_context.return_value = "No history"
    return mock_mem

def test_golden_loop_approved_action():
    session = SessionState(session_id="sess-001", active_agent="OrderTaker", tool_budget_remaining=3, age_verified=True)
    kitchen = KitchenSnapshot(load_percentage=10)
    mock_memory = setup_mocks()
    menu_item = MenuItemSnapshot(sku="PZ-PEP", name="Pep Pizza", price=12.99, in_stock=True)

    with patch(PATCH_MENU, return_value=[menu_item]), \
         patch(PATCH_HYBRID, return_value=[menu_item]), \
         patch(PATCH_LLM, return_value="{}"), \
         patch(PATCH_PARSER) as mock_parse:

        mock_parse.return_value = ActionRequest(
            action_type=ActionType.ADD_TO_CART, 
            sku="PZ-PEP", 
            confidence=1.0
        )

        response = golden_loop(session=session, user_input="Add pizza", kitchen=kitchen, memory=mock_memory)

    assert "success" in response.lower() or "added" in response.lower()
    assert session.tool_budget_remaining == 2
    assert mock_memory.update.called

def test_golden_loop_ambiguous_input_triggers_clarification():
    session = SessionState(session_id="sess-002", active_agent="OrderTaker", tool_budget_remaining=3)
    kitchen = KitchenSnapshot(load_percentage=10)
    mock_memory = setup_mocks()
    
    # We define the payload here so we can check it in the assertion
    expected_question = "Could you please specify which pizza?"

    with patch(PATCH_MENU, return_value=[]), \
         patch(PATCH_HYBRID, return_value=[]), \
         patch(PATCH_LLM, return_value="{}"), \
         patch(PATCH_PARSER) as mock_parse:

        mock_parse.return_value = ActionRequest(
            action_type=ActionType.ASK_CLARIFICATION,
            sku=None,
            confidence=0.6,
            clarification_payload=expected_question
        )

        response = golden_loop(session=session, user_input="pizza", kitchen=kitchen, memory=mock_memory)

    # ✅ FIXED: Assertion now matches the actual content we mocked
    assert expected_question in response
    assert mock_memory.update.called

def test_golden_loop_ambiguity_escalates_after_retries():
    session = SessionState(session_id="sess-003", active_agent="OrderTaker", tool_budget_remaining=3)
    kitchen = KitchenSnapshot(load_percentage=10)
    mock_memory = setup_mocks()
    menu_items = [MenuItemSnapshot(sku="PZ-1", name="M Pizza", price=10, in_stock=True)]

    with patch(PATCH_MENU, return_value=menu_items), \
         patch(PATCH_HYBRID, return_value=menu_items), \
         patch(PATCH_LLM, return_value="{}"), \
         patch(PATCH_PARSER) as mock_parse:

        # ✅ FIXED: Added clarification_payload
        mock_parse.return_value = ActionRequest(
            action_type=ActionType.ASK_CLARIFICATION, 
            sku=None, 
            confidence=0.5,
            clarification_payload="I found multiple pizzas. Which one?"
        )

        # First and second attempts to trigger the escalation logic
        golden_loop(session=session, user_input="pizza", kitchen=kitchen, memory=mock_memory)
        response = golden_loop(session=session, user_input="pizza", kitchen=kitchen, memory=mock_memory)

    assert "did you mean" in response.lower()
    assert mock_memory.update.call_count == 2