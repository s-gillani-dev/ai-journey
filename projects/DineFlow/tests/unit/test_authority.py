# tests/unit/test_authority.py
# from aiva.validation.schemas import ActionRequest, ActionType
# from aiva.state_machine.types import SessionState, KitchenSnapshot, MenuItemSnapshot
# from aiva.state_machine.authority import evaluate_action
# from aiva.validation.errors import RejectionCode

# def test_rejects_missing_item():
#     """Reject action if menu item not found"""
#     action = ActionRequest(
#         action_type=ActionType.ADD_TO_CART,
#         sku="PZ-404"
#     )

#     session = SessionState(
#         session_id="abc",
#         active_agent="OrderTaker"
#     )

#     kitchen = KitchenSnapshot(load_percentage=30)

#     result = evaluate_action(
#         action=action,
#         session=session,
#         menu_item=None,   # Simulating "not found"
#         kitchen=kitchen
#     )

#     assert result.approved is False
#     assert result.rejection_code == RejectionCode.ERR_ITEM_NOT_FOUND


# def test_rejects_alcohol_if_not_verified():
#     """Reject adding alcohol if age_verified is False"""
#     action = ActionRequest(
#         action_type=ActionType.ADD_TO_CART,
#         sku="BEER-001"
#     )

#     session = SessionState(
#         session_id="abc",
#         active_agent="OrderTaker",
#         age_verified=False
#     )

#     kitchen = KitchenSnapshot(load_percentage=20)

#     menu_item = MenuItemSnapshot(
#         sku="BEER-001",
#         name="Beer",
#         price=5.5,
#         in_stock=True,
#         is_alcohol=True,
#         complexity_score=1
#     )

#     result = evaluate_action(
#         action=action,
#         session=session,
#         menu_item=menu_item,
#         kitchen=kitchen
#     )

#     assert result.approved is False
#     assert result.rejection_code == RejectionCode.ERR_AGE_RESTRICTION


# def test_rejects_if_kitchen_overloaded():
#     """Reject complex items if kitchen load is high"""
#     action = ActionRequest(
#         action_type=ActionType.ADD_TO_CART,
#         sku="PZ-MARG"
#     )

#     session = SessionState(
#         session_id="abc",
#         active_agent="OrderTaker",
#         age_verified=True
#     )

#     kitchen = KitchenSnapshot(load_percentage=90)  # High load

#     menu_item = MenuItemSnapshot(
#         sku="PZ-MARG",
#         name="Margherita Pizza",
#         price=10.0,
#         in_stock=True,
#         is_alcohol=False,
#         complexity_score=5  # High complexity
#     )

#     result = evaluate_action(
#         action=action,
#         session=session,
#         menu_item=menu_item,
#         kitchen=kitchen
#     )

#     assert result.approved is False
#     assert result.rejection_code == RejectionCode.ERR_KITCHEN_OVERLOAD


# def test_allows_simple_item_when_kitchen_busy():
#     """Approve simple items even if kitchen load is high"""
#     action = ActionRequest(
#         action_type=ActionType.ADD_TO_CART,
#         sku="SALAD-001"
#     )

#     session = SessionState(
#         session_id="abc",
#         active_agent="OrderTaker",
#         age_verified=True
#     )

#     kitchen = KitchenSnapshot(load_percentage=90)  # High load

#     menu_item = MenuItemSnapshot(
#         sku="SALAD-001",
#         name="Caesar Salad",
#         price=7.5,
#         in_stock=True,
#         is_alcohol=False,
#         complexity_score=1  # Low complexity
#     )

#     result = evaluate_action(
#         action=action,
#         session=session,
#         menu_item=menu_item,
#         kitchen=kitchen
#     )

#     assert result.approved is True
#     assert result.rejection_code is None




# # DineFlow/tests/unit/test_authority.py
# import pytest
# from validation.schemas import ActionRequest, ActionType, IntentType
# from state_machine.types import SessionState, KitchenSnapshot, MenuItemSnapshot
# from state_machine.authority import evaluate_action
# from validation.errors import RejectionCode, ViolationType, Severity

# # Mock data for shared use
# @pytest.fixture
# def base_session():
#     return SessionState(
#             session_id="sess-gauntlet",
#             user_id="test-user-99",         # ✅ Added required field
#             active_agent="OrderTaker",
#             tool_budget_remaining=5,
#             cart={},                        # ✅ Changed [] to {}
#             age_verified=False,
#             order_status="DRAFT"            # Added for completeness
#         )

# @pytest.fixture
# def low_load_kitchen():
#     return KitchenSnapshot(load_percentage=20)

# # 1. TEST JURISDICTION (NEGATIVE ROUTING POWER)
# def test_rejects_jurisdiction_mismatch(base_session, low_load_kitchen):
#     """Authority must block OrderTaker from handling an INQUIRY intent."""
#     action = ActionRequest(
#         action_type=ActionType.NO_OP,
#         intent=IntentType.INQUIRY, # Illegal for OrderTaker
#         confidence=1.0
#     )

#     result = evaluate_action(
#         action=action,
#         session=base_session,
#         menu_item=None,
#         kitchen=low_load_kitchen,
#         all_menu_items=[],
#         memory=None
#     )

#     assert result.approved is False
#     assert result.violation_type == ViolationType.INVALID_STATE
#     assert result.severity == Severity.RECOVERABLE # Allows auto-switch to MenuExpert

# # 2. TEST ALCOHOL (DEFERRED SEMANTICS)
# def test_defers_alcohol_if_not_verified(base_session, low_load_kitchen):
#     """Alcohol should return DEFERRED, not FATAL, because it's a prerequisite block."""
#     action = ActionRequest(
#         action_type=ActionType.ADD_TO_CART,
#         sku="BEER-01",
#         quantity=1,
#         confidence=1.0
#     )

#     menu_item = MenuItemSnapshot(
#         sku="BEER-01", name="Cold Beer", price=5.0,
#         in_stock=True, is_alcohol=True, complexity_score=1
#     )

#     result = evaluate_action(
#         action=action,
#         session=base_session,
#         menu_item=menu_item,
#         kitchen=low_load_kitchen,
#         all_menu_items=[menu_item],
#         memory=None
#     )

#     assert result.approved is False
#     assert result.violation_type == ViolationType.AGE_RESTRICTION
#     assert result.severity == Severity.DEFERRED # Prerequisite check
#     assert "verify your ID" in result.user_message

# # 3. TEST KITCHEN LOAD (DEFERRED SEMANTICS)
# def test_defers_complex_item_when_busy(base_session):
#     """High complexity while busy should be DEFERRED."""
#     action = ActionRequest(
#         action_type=ActionType.ADD_TO_CART,
#         sku="PIZZA-PRO",
#         quantity=1,
#         confidence=1.0
#     )
    
#     busy_kitchen = KitchenSnapshot(load_percentage=90)
#     complex_item = MenuItemSnapshot(
#         sku="PIZZA-PRO", name="Complex Pizza", price=20.0,
#         in_stock=True, is_alcohol=False, complexity_score=5 # Busy limit is 3
#     )

#     result = evaluate_action(
#         action=action,
#         session=base_session,
#         menu_item=complex_item,
#         kitchen=busy_kitchen,
#         all_menu_items=[complex_item],
#         memory=None
#     )

#     assert result.approved is False
#     assert result.violation_type == ViolationType.KITCHEN_OVERLOAD
#     assert result.severity == Severity.DEFERRED

# # 4. TEST BUDGET EXHAUSTION (FATAL)
# def test_rejects_budget_exhaustion(base_session, low_load_kitchen):
#     """Budget = 0 must be a FATAL block."""
#     base_session.tool_budget_remaining = 0
    
#     # ✅ FIX: Added the required clarification_payload for this action type
#     action = ActionRequest(
#         action_type=ActionType.ASK_CLARIFICATION,
#         clarification_payload="I'm sorry, I've run out of processing power."
#     )

#     result = evaluate_action(
#         action=action,
#         session=base_session,
#         menu_item=None,
#         kitchen=low_load_kitchen,
#         all_menu_items=[],
#         memory=None
#     )

#     assert result.approved is False
#     assert result.severity == Severity.FATAL
#     assert result.violation_type == ViolationType.BUDGET_EXCEEDED

# # 5. TEST AMBIGUITY (RECOVERABLE)
# def test_rejects_ambiguous_category(base_session, low_load_kitchen):
#     """Generic 'Pizza' with multiple matches must return AMBIGUOUS_CATEGORY."""
#     action = ActionRequest(
#         action_type=ActionType.ADD_TO_CART,
#         sku=None,
#         meta={"attempted_category": "Pizza"}
#     )
    
#     menu_items = [
#         MenuItemSnapshot(sku="P1", name="Veggie Pizza", price=10, in_stock=True, is_alcohol=False, complexity_score=1),
#         MenuItemSnapshot(sku="P2", name="Meat Pizza", price=12, in_stock=True, is_alcohol=False, complexity_score=1)
#     ]

#     result = evaluate_action(
#         action=action,
#         session=base_session,
#         menu_item=None,
#         kitchen=low_load_kitchen,
#         all_menu_items=menu_items,
#         memory=None
#     )

#     assert result.approved is False
#     assert result.violation_type == ViolationType.AMBIGUOUS_CATEGORY
#     assert "Which pizza did you mean?" in result.user_message

# # 🟢 6. NEW: TEST ORDER LOCKING (Semantic Truth)
# def test_rejects_modification_on_confirmed_order(base_session, low_load_kitchen):
#     """Proves that a confirmed order is an INVALID_STATE and FATAL."""
#     base_session.order_status = "CONFIRMED"
#     action = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="P1", quantity=1)

#     result = evaluate_action(action, base_session, None, low_load_kitchen, [], None)

#     assert result.approved is False
#     assert result.violation_type == ViolationType.INVALID_STATE
#     assert result.severity == Severity.FATAL

# # 🟢 7. NEW: TEST SEMANTIC STOCK (Semantic Truth)
# def test_rejects_out_of_stock_as_invalid_sku(base_session, low_load_kitchen):
#     """Proves that Out-of-Stock maps to INVALID_SKU/RECOVERABLE in v1.1."""
#     menu_item = MenuItemSnapshot(sku="P1", name="Pizza", price=10, in_stock=False)
#     action = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="P1", quantity=1)

#     result = evaluate_action(action, base_session, menu_item, low_load_kitchen, [menu_item], None)

#     assert result.approved is False
#     assert result.violation_type == ViolationType.INVALID_SKU
#     assert result.severity == Severity.RECOVERABLE






# claud recent version tetsing.....

# DineFlow/tests/unit/test_authority.py
import pytest
from unittest.mock import MagicMock
from validation.schemas import ActionRequest, ActionType, IntentType
from state_machine.types import SessionState, KitchenSnapshot, MenuItemSnapshot, ContextScope
from state_machine.authority import evaluate_action, decide_context_scope
from validation.errors import RejectionCode, ViolationType, Severity


# =============================================================================
# SHARED FIXTURES
# =============================================================================

@pytest.fixture
def base_session():
    return SessionState(
        session_id="sess-gauntlet",
        user_id="test-user-99",
        active_agent="OrderTaker",
        tool_budget_remaining=5,
        cart={},
        age_verified=False,
        order_status="DRAFT"
    )


@pytest.fixture
def low_load_kitchen():
    return KitchenSnapshot(load_percentage=20)


@pytest.fixture
def simple_menu():
    """
    Minimal menu with description and tags populated.
    Used by tests that need real semantic content (scope, search, context).
    Tests that only care about authority rules (budget, stock, alcohol)
    use inline MenuItemSnapshot construction instead.
    """
    return [
        MenuItemSnapshot(
            sku="PZ-PEP",
            name="Pepperoni Pizza",
            price=12.99,
            in_stock=True,
            is_alcohol=False,
            complexity_score=2,
            description="Classic pizza loaded with spicy pepperoni and mozzarella.",
            tags=["spicy", "hot", "classic", "pork"],
        ),
        MenuItemSnapshot(
            sku="PZ-MARG",
            name="Margherita Pizza",
            price=11.49,
            in_stock=True,
            is_alcohol=False,
            complexity_score=2,
            description="Simple and fresh with tomato sauce, basil, and mozzarella.",
            tags=["vegetarian", "mild", "classic"],
        ),
    ]


# =============================================================================
# evaluate_action TESTS
# =============================================================================

class TestJurisdiction:
    def test_rejects_jurisdiction_mismatch(self, base_session, low_load_kitchen):
        """Authority must block OrderTaker from handling an INQUIRY intent."""
        action = ActionRequest(
            action_type=ActionType.NO_OP,
            intent=IntentType.INQUIRY,  # Illegal for OrderTaker
            confidence=1.0
        )

        result = evaluate_action(
            action=action,
            session=base_session,
            menu_item=None,
            kitchen=low_load_kitchen,
            all_menu_items=[],
            memory=None
        )

        assert result.approved is False
        assert result.violation_type == ViolationType.INVALID_STATE
        # RECOVERABLE — allows auto-switch to MenuExpert, not a hard stop
        assert result.severity == Severity.RECOVERABLE
        # Meta must carry the correct target so golden_loop can auto-handoff
        assert result.meta is not None
        assert result.meta.get("target_agent") == "MenuExpert"


class TestAlcohol:
    def test_defers_alcohol_if_not_verified(self, base_session, low_load_kitchen):
        """Alcohol must return DEFERRED — it's a prerequisite block, not a hard rejection."""
        action = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="BEER-01",
            quantity=1,
            confidence=1.0
        )
        menu_item = MenuItemSnapshot(
            sku="BEER-01", name="Cold Beer", price=5.0,
            in_stock=True, is_alcohol=True, complexity_score=1
        )

        result = evaluate_action(
            action=action,
            session=base_session,
            menu_item=menu_item,
            kitchen=low_load_kitchen,
            all_menu_items=[menu_item],
            memory=None
        )

        assert result.approved is False
        assert result.violation_type == ViolationType.AGE_RESTRICTION
        assert result.severity == Severity.DEFERRED
        assert "verify your ID" in result.user_message
        # Must carry capability hint so orchestrator/UI knows what to trigger
        assert result.meta.get("required_capability") == "ID_VERIFIER"


class TestKitchenLoad:
    def test_defers_complex_item_when_busy(self, base_session):
        """High complexity while kitchen is busy must be DEFERRED, not FATAL."""
        action = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="PIZZA-PRO",
            quantity=1,
            confidence=1.0
        )
        busy_kitchen = KitchenSnapshot(load_percentage=90)
        complex_item = MenuItemSnapshot(
            sku="PIZZA-PRO", name="Complex Pizza", price=20.0,
            in_stock=True, is_alcohol=False, complexity_score=5  # Busy threshold is 3
        )

        result = evaluate_action(
            action=action,
            session=base_session,
            menu_item=complex_item,
            kitchen=busy_kitchen,
            all_menu_items=[complex_item],
            memory=None
        )

        assert result.approved is False
        assert result.violation_type == ViolationType.KITCHEN_OVERLOAD
        assert result.severity == Severity.DEFERRED

    def test_allows_simple_item_when_busy(self, base_session):
        """A low-complexity item must be approved even when kitchen load is high."""
        action = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="PZ-MARG",
            quantity=1,
            confidence=1.0
        )
        busy_kitchen = KitchenSnapshot(load_percentage=90)
        simple_item = MenuItemSnapshot(
            sku="PZ-MARG", name="Margherita Pizza", price=11.49,
            in_stock=True, is_alcohol=False, complexity_score=2  # Under threshold
        )

        result = evaluate_action(
            action=action,
            session=base_session,
            menu_item=simple_item,
            kitchen=busy_kitchen,
            all_menu_items=[simple_item],
            memory=None
        )

        assert result.approved is True


class TestBudget:
    def test_rejects_budget_exhaustion(self, base_session, low_load_kitchen):
        """Budget = 0 must be a FATAL block — no recovery path."""
        base_session.tool_budget_remaining = 0
        action = ActionRequest(
            action_type=ActionType.ASK_CLARIFICATION,
            clarification_payload="I'm sorry, I've run out of processing power."
        )

        result = evaluate_action(
            action=action,
            session=base_session,
            menu_item=None,
            kitchen=low_load_kitchen,
            all_menu_items=[],
            memory=None
        )

        assert result.approved is False
        assert result.severity == Severity.FATAL
        assert result.violation_type == ViolationType.BUDGET_EXCEEDED


class TestAmbiguity:
    def test_rejects_ambiguous_category(self, base_session, low_load_kitchen):
        """Generic 'Pizza' with multiple matches must return AMBIGUOUS_CATEGORY."""
        action = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku=None,
            meta={"attempted_category": "Pizza"}
        )
        menu_items = [
            MenuItemSnapshot(sku="P1", name="Veggie Pizza", price=10, in_stock=True,
                             is_alcohol=False, complexity_score=1),
            MenuItemSnapshot(sku="P2", name="Meat Pizza", price=12, in_stock=True,
                             is_alcohol=False, complexity_score=1),
        ]

        result = evaluate_action(
            action=action,
            session=base_session,
            menu_item=None,
            kitchen=low_load_kitchen,
            all_menu_items=menu_items,
            memory=None
        )

        assert result.approved is False
        assert result.violation_type == ViolationType.AMBIGUOUS_CATEGORY
        # ✅ FIX: Old assertion was exact-match on "Which pizza did you mean?"
        # The actual message includes the item list: "Which pizza did you mean? We have: ..."
        # Use substring check so the test is not brittle to list formatting changes.
        assert "Which pizza did you mean?" in result.user_message
        assert "Veggie Pizza" in result.user_message
        assert "Meat Pizza" in result.user_message


class TestOrderLocking:
    def test_rejects_modification_on_confirmed_order(self, base_session, low_load_kitchen):
        """A confirmed order must reject all mutations as INVALID_STATE + FATAL."""
        base_session.order_status = "CONFIRMED"
        action = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="P1", quantity=1)

        result = evaluate_action(action, base_session, None, low_load_kitchen, [], None)

        assert result.approved is False
        assert result.violation_type == ViolationType.INVALID_STATE
        assert result.severity == Severity.FATAL


class TestStock:
    def test_rejects_out_of_stock_as_recoverable(self, base_session, low_load_kitchen):
        """Out-of-stock maps to INVALID_SKU/RECOVERABLE — user can choose a different item."""
        menu_item = MenuItemSnapshot(sku="P1", name="Pizza", price=10, in_stock=False)
        action = ActionRequest(action_type=ActionType.ADD_TO_CART, sku="P1", quantity=1)

        result = evaluate_action(action, base_session, menu_item, low_load_kitchen, [menu_item], None)

        assert result.approved is False
        assert result.violation_type == ViolationType.INVALID_SKU
        # RECOVERABLE — user can pick something else, not a system error
        assert result.severity == Severity.RECOVERABLE


# =============================================================================
# decide_context_scope TESTS
# =============================================================================

class TestDecideContextScope:
    """
    Tests for the QueryClassifier-backed scope decision function.

    These tests directly verify the architectural fix: that user_input
    drives scope elevation, not just session.active_intent.

    Each test documents WHAT the classifier signal is and WHY the
    expected scope follows from it.
    """

    def _make_session(self, intent=None, agent="MenuExpert"):
        return SessionState(
            session_id="sess-scope-test",
            user_id="test-user-scope",
            active_agent=agent,
            tool_budget_remaining=5,
            active_intent=intent,
        )

    def test_attribute_query_gets_full_catalog(self, simple_menu):
        """
        'anything spicy?' — categorical grammar ('anything') signals attribute scan.
        Must receive FULL_CATALOG regardless of session intent.
        This is the primary regression test for the original bug.
        """
        session = self._make_session()
        policy = decide_context_scope(session, "Do you have anything spicy?", simple_menu)

        assert policy["context_scope"] == ContextScope.FULL_CATALOG

    def test_named_item_query_gets_filtered_search(self, simple_menu):
        """
        'Tell me about the Pepperoni Pizza' — entity resolved by name.
        Must receive FILTERED_SEARCH: full catalog is wasteful and unnecessary.
        """
        session = self._make_session()
        policy = decide_context_scope(session, "Tell me about the Pepperoni Pizza", simple_menu)

        assert policy["context_scope"] == ContextScope.FILTERED_SEARCH

    def test_named_item_with_inquiry_intent_gets_full_catalog(self, simple_menu):
        """
        'Is the Pepperoni Pizza spicy?' — entity named BUT intent is INQUIRY.
        The router saw the user is asking about a property, not just requesting info.
        Intent is the higher-authority signal here → FULL_CATALOG.
        """
        session = self._make_session(intent=IntentType.INQUIRY)
        policy = decide_context_scope(
            session, "Is the Pepperoni Pizza spicy?", simple_menu
        )

        assert policy["context_scope"] == ContextScope.FULL_CATALOG

    def test_price_comparator_query_gets_full_catalog(self, simple_menu):
        """
        'Something under $12' — comparator pattern requires scanning all prices.
        Must receive FULL_CATALOG.
        """
        session = self._make_session()
        policy = decide_context_scope(session, "Something under $12", simple_menu)

        assert policy["context_scope"] == ContextScope.FULL_CATALOG

    def test_ambiguous_query_defaults_to_full_catalog(self, simple_menu):
        """
        'What about pizza?' — no strong entity or attribute signal.
        Must default to FULL_CATALOG: fail toward more data, not less.
        A wrong FILTERED_SEARCH causes a silent knowledge failure.
        A wrong FULL_CATALOG costs one extra retrieval — acceptable.
        """
        session = self._make_session()
        policy = decide_context_scope(session, "What about pizza?", simple_menu)

        assert policy["context_scope"] == ContextScope.FULL_CATALOG

    def test_vegan_attribute_query_gets_full_catalog(self, simple_menu):
        """
        'Any vegan options?' — categorical grammar ('any') + attribute keyword.
        Must receive FULL_CATALOG.
        """
        session = self._make_session()
        policy = decide_context_scope(session, "Any vegan options?", simple_menu)

        assert policy["context_scope"] == ContextScope.FULL_CATALOG

    def test_policy_carries_classifier_reasoning(self, simple_menu):
        """
        The policy dict must carry classifier_reasoning for auditability.
        Logs must be able to explain WHY a scope decision was made
        without replaying the full request.
        """
        session = self._make_session()
        policy = decide_context_scope(session, "Do you have anything spicy?", simple_menu)

        assert "classifier_reasoning" in policy
        assert policy["classifier_reasoning"]  # Must be non-empty string

    def test_policy_carries_classifier_confidence(self, simple_menu):
        """Confidence score must be present for monitoring and alerting."""
        session = self._make_session()
        policy = decide_context_scope(session, "Tell me about the Pepperoni Pizza", simple_menu)

        assert "classifier_confidence" in policy
        assert isinstance(policy["classifier_confidence"], float)
        assert 0.0 <= policy["classifier_confidence"] <= 1.0

    def test_fallback_on_empty_input(self, simple_menu):
        """
        Empty input must not crash — returns FULL_CATALOG as the safe default.
        Defensive contract: Authority must never raise.
        """
        session = self._make_session()
        policy = decide_context_scope(session, "", simple_menu)

        # Empty input → AMBIGUOUS → FULL_CATALOG
        assert policy["context_scope"] == ContextScope.FULL_CATALOG