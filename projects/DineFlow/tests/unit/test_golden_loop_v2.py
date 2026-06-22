# tests/unit/test_golden_loop_v2.py
# from unittest.mock import patch, MagicMock
# from aiva.orchestration.golden_loop import golden_loop
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.validation.schemas import ActionRequest, ActionType

# # Note: We now patch the AGENT_REGISTRY and Router
# PATCH_ROUTER = "aiva.orchestration.golden_loop.router.route"
# PATCH_REGISTRY = "aiva.orchestration.golden_loop.AGENT_REGISTRY"

# def test_golden_loop_routes_to_greeter_and_bypasses_budget():
#     session = SessionState(session_id="s1", active_agent="OrderTaker", tool_budget_remaining=5)
#     kitchen = KitchenSnapshot(load_percentage=10)
#     mock_memory = MagicMock()

#     # 1. Mock Router to say: "Go to Greeter"
#     mock_router_action = ActionRequest(
#         action_type=ActionType.TRANSFER,
#         target_agent="Greeter",
#         confidence=1.0
#     )

#     # 2. Mock Greeter Agent to say: "Hello!"
#     mock_greeter = MagicMock()
#     mock_greeter.run.return_value = ActionRequest(
#         action_type=ActionType.NO_OP,
#         message="Hello! I am AIVA.",
#         confidence=1.0
#     )

#     with patch(PATCH_ROUTER, return_value=mock_router_action), \
#          patch(PATCH_REGISTRY, {"Greeter": mock_greeter}):

#         response = golden_loop(session=session, user_input="Hi", kitchen=kitchen, memory=mock_memory)

#     # ASSERTIONS
#     assert response == "Hello! I am AIVA."
#     assert session.active_agent == "Greeter"
#     assert session.tool_budget_remaining == 5  # ✅ IMPORTANT: Budget did not drop!
#     assert mock_memory.update.called

# def test_golden_loop_fails_loudly_on_unimplemented_agent():
#     session = SessionState(session_id="s2", active_agent="OrderTaker")
#     kitchen = KitchenSnapshot(load_percentage=10)
    
#     # 🆕 FIX: Setup a mock memory that returns a string
#     mock_memory = MagicMock()
#     mock_memory.get_context.return_value = "No history" # ⬅️ This prevents the TypeError
    
#     # Mock router suggesting a non-existent agent
#     mock_router_action = ActionRequest(
#         action_type=ActionType.TRANSFER,
#         target_agent="NonExistentAgent",
#         confidence=1.0
#     )

#     with patch(PATCH_ROUTER, return_value=mock_router_action):
#         # We expect a NotImplementedError because of our guard in golden_loop
#         # If your code defaults to OrderTaker instead of raising, 
#         # then we should check if it actually runs the OrderTaker.
        
#         response = golden_loop(
#             session=session, 
#             user_input="Chaos", 
#             kitchen=kitchen, 
#             memory=mock_memory
#         )
        
#     # If your golden_loop code has the "Default to OrderTaker" logic:
#     assert session.active_agent == "OrderTaker"





# # tests/unit/test_golden_loop_v2.py
# from unittest.mock import patch, MagicMock
# import pytest
# from orchestration.golden_loop import golden_loop
# from state_machine.types import SessionState, KitchenSnapshot
# from validation.schemas import ActionRequest, ActionType
# from validation.errors import ViolationType, Severity

# PATCH_ROUTER = "orchestration.golden_loop.router.route"
# PATCH_REGISTRY = "orchestration.golden_loop.AGENT_REGISTRY"

# def create_valid_session(session_id, agent="OrderTaker", budget=5):
#     return SessionState(
#         session_id=session_id,
#         user_id="test_user_123",
#         active_agent=agent,
#         tool_budget_remaining=budget,
#         cart={}
#     )

# def test_golden_loop_menu_expert_bypasses_budget():
#     session = create_valid_session("s_exp")
#     kitchen = KitchenSnapshot(load_percentage=10)
#     mock_memory = MagicMock()

#     # Create a plain mock and manually add the attributes the loop needs
#     mock_router_action = MagicMock()
#     mock_router_action.intent = "INQUIRY"
#     mock_router_action.target_agent = "MenuExpert"
#     mock_router_action.confidence = 0.9

#     mock_expert = MagicMock()
#     mock_expert.run.return_value = ActionRequest(
#         action_type=ActionType.NO_OP,
#         message="The Margherita pizza is fresh.",
#         meta={"agent": "MenuExpert"}
#     )

#     with patch(PATCH_ROUTER, return_value=mock_router_action), \
#          patch(PATCH_REGISTRY, {"MenuExpert": mock_expert}):
#         response = golden_loop(session=session, user_input="Is it fresh?", kitchen=kitchen, memory=mock_memory)

#     assert "fresh" in response
#     assert session.active_agent == "MenuExpert"
#     assert session.tool_budget_remaining == 5 

# def test_golden_loop_order_taker_consumes_budget():
#     session = create_valid_session("s_order")
#     kitchen = KitchenSnapshot(load_percentage=10)
#     mock_memory = MagicMock()

#     mock_router_action = MagicMock()
#     mock_router_action.intent = "ORDERING"
#     mock_router_action.target_agent = "OrderTaker"
#     mock_router_action.confidence = 1.0

#     mock_ot = MagicMock()
#     mock_ot.run.return_value = ActionRequest(
#         action_type=ActionType.ADD_TO_CART,
#         sku="PZ-MARG",
#         quantity=1
#     )

#     with patch(PATCH_ROUTER, return_value=mock_router_action), \
#          patch(PATCH_REGISTRY, {"OrderTaker": mock_ot}), \
#          patch("orchestration.golden_loop.resolve_menu_item"), \
#          patch("orchestration.golden_loop.evaluate_action") as mock_eval, \
#          patch("orchestration.golden_loop.generate_response", return_value="Added!"):
        
#         mock_eval.return_value = MagicMock(approved=True)
#         golden_loop(session=session, user_input="Add a Margherita", kitchen=kitchen, memory=mock_memory)

#     assert session.tool_budget_remaining == 4 

# def test_golden_loop_systemic_handoff_with_recursion():
#     """✅ FIXED: Verifies silent handoff and recursion happen in one turn."""
#     session = create_valid_session("s_handoff")
#     kitchen = KitchenSnapshot(load_percentage=10)
#     mock_memory = MagicMock()

#     # Pass 1: Authority rejects (wrong agent)
#     mock_result_1 = MagicMock(
#         approved=False,
#         violation_type=ViolationType.INVALID_STATE,
#         severity=Severity.RECOVERABLE,
#         meta={"target_agent": "MenuExpert"}
#     )
#     # Pass 2: Authority approves (correct agent)
#     mock_result_2 = MagicMock(approved=True)

#     # 🔧 FIX: Ensure router action has confidence and target
#     mock_router_action = MagicMock(intent="INQUIRY", target_agent="MenuExpert", confidence=1.0)
    
#     mock_me = MagicMock()
#     # 🔧 FIX: Add action_type to the agent return so it doesn't hit NO_OP short-circuit
#     mock_me.run.return_value = ActionRequest(
#         action_type=ActionType.ADD_TO_CART, 
#         sku="P1", 
#         quantity=1
#     )

#     with patch(PATCH_ROUTER, return_value=mock_router_action), \
#          patch(PATCH_REGISTRY, {"OrderTaker": MagicMock(), "MenuExpert": mock_me}), \
#          patch("orchestration.golden_loop.evaluate_action") as mock_eval, \
#          patch("orchestration.golden_loop.generate_response", return_value="Expert answer."):
        
#         mock_eval.side_effect = [mock_result_1, mock_result_2]
        
#         response = golden_loop(session=session, user_input="How is it made?", kitchen=kitchen, memory=mock_memory)

#     assert response == "Expert answer."
#     assert session.active_agent == "MenuExpert"
#     # This should now be 2 because the mock persists through the recursive call in this context
#     assert mock_eval.call_count == 2 

# def test_golden_loop_fatal_stops_immediately():
#     """✅ FIXED: Proves that FATAL errors terminate the loop."""
#     session = create_valid_session("s_fatal")
#     session.order_status = "CONFIRMED"
#     kitchen = KitchenSnapshot(load_percentage=10)
    
#     # 🔧 FIX: Mock the router response properly so the loop can read confidence
#     mock_router_action = MagicMock(intent="ORDERING", target_agent="OrderTaker", confidence=1.0)

#     mock_result = MagicMock(
#         approved=False,
#         severity=Severity.FATAL,
#         user_message="Order is locked."
#     )

#     with patch(PATCH_ROUTER, return_value=mock_router_action), \
#          patch(PATCH_REGISTRY, {"OrderTaker": MagicMock()}), \
#          patch("orchestration.golden_loop.evaluate_action", return_value=mock_result):
        
#         response = golden_loop(session=session, user_input="Add pizza", kitchen=kitchen, memory=MagicMock())

#     assert response == "Order is locked."

# def test_golden_loop_deferred_capability():
#     session = create_valid_session("s_defer")
#     kitchen = KitchenSnapshot(load_percentage=10)
#     mock_memory = MagicMock()

#     mock_result = MagicMock()
#     mock_result.approved = False
#     mock_result.severity = Severity.DEFERRED
#     mock_result.violation_type = ViolationType.AGE_RESTRICTION
#     mock_result.user_message = "I need to see your ID."
#     mock_result.meta = {"required_capability": "ID_VERIFIER"}

#     mock_router_action = MagicMock()
#     mock_router_action.intent = "ORDERING"
#     mock_router_action.target_agent = "OrderTaker"
#     mock_router_action.confidence = 1.0

#     with patch(PATCH_ROUTER, return_value=mock_router_action), \
#          patch(PATCH_REGISTRY, {"OrderTaker": MagicMock()}), \
#          patch("orchestration.golden_loop.evaluate_action", return_value=mock_result), \
#          patch("orchestration.golden_loop.generate_response") as mock_gen:
        
#         golden_loop(session=session, user_input="Beer please", kitchen=kitchen, memory=mock_memory)
        
#         # Capture the recovery action passed to the generator
#         # Generator is called with (action=..., result=..., menu_items=...)
#         # We look at the keyword argument 'action'
#         recovery_action = mock_gen.call_args.kwargs['action']
#         assert recovery_action.meta["required_capability"] == "ID_VERIFIER"




# claud recent version testing....

# DineFlow/tests/unit/test_golden_loop_v2.py
from unittest.mock import patch, MagicMock, call
import pytest
from orchestration.golden_loop import golden_loop
from state_machine.types import SessionState, KitchenSnapshot, ContextScope
from validation.schemas import ActionRequest, ActionType
from validation.errors import ViolationType, Severity


# =============================================================================
# PATCH TARGETS
# =============================================================================

PATCH_ROUTER   = "orchestration.golden_loop.router.route"
PATCH_REGISTRY = "orchestration.golden_loop.AGENT_REGISTRY"

# ⚠️ CRITICAL: decide_context_scope is now called at Step 2, BEFORE agent
# execution. Every test that mocks the agent registry must also mock this
# function, otherwise the real QueryClassifier runs against a name index
# built from the live registry — which may or may not be initialised in the
# test environment — and the scope on the session will be wrong or the call
# will crash.
PATCH_SCOPE = "orchestration.golden_loop.decide_context_scope"

# Standard scope policy returned by the mock — FULL_CATALOG is the safe
# default in tests because it never silently restricts context.
MOCK_SCOPE_POLICY = {
    "context_scope": ContextScope.FULL_CATALOG,
    "system_hint": "Test: Full catalog authorized.",
    "classifier_reasoning": "mocked",
    "classifier_confidence": 1.0,
    "resolved_entity": None,
}


# =============================================================================
# HELPERS
# =============================================================================

def create_valid_session(session_id, agent="OrderTaker", budget=5):
    return SessionState(
        session_id=session_id,
        user_id="test_user_123",
        active_agent=agent,
        tool_budget_remaining=budget,
        cart={}
    )


# =============================================================================
# TESTS
# =============================================================================

class TestMenuExpertNOOP:
    def test_menu_expert_bypasses_budget(self):
        """
        MenuExpert responses are NO_OP — they short-circuit before budget
        consumption. Budget must remain unchanged after the call.
        """
        session = create_valid_session("s_exp")
        kitchen = KitchenSnapshot(load_percentage=10)
        mock_memory = MagicMock()

        mock_router_action = MagicMock(
            intent="INQUIRY",
            target_agent="MenuExpert",
            confidence=0.9
        )

        mock_expert = MagicMock()
        mock_expert.run.return_value = ActionRequest(
            action_type=ActionType.NO_OP,
            message="The Margherita pizza is fresh.",
            meta={"agent": "MenuExpert"}
        )

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"MenuExpert": mock_expert}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY):

            response = golden_loop(
                session=session, user_input="Is it fresh?",
                kitchen=kitchen, memory=mock_memory
            )

        assert "fresh" in response
        assert session.active_agent == "MenuExpert"
        # NO_OP short-circuits before consume_tool_budget — budget must be untouched
        assert session.tool_budget_remaining == 5


class TestOrderTakerBudget:
    def test_order_taker_consumes_budget_on_approved_action(self):
        """
        An approved ADD_TO_CART must decrement the budget by exactly 1.
        This verifies consume_tool_budget is called on the approved path.
        """
        session = create_valid_session("s_order")
        kitchen = KitchenSnapshot(load_percentage=10)
        mock_memory = MagicMock()

        mock_router_action = MagicMock(
            intent="ORDERING",
            target_agent="OrderTaker",
            confidence=1.0
        )

        mock_ot = MagicMock()
        mock_ot.run.return_value = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="PZ-MARG",
            quantity=1
        )

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"OrderTaker": mock_ot}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY), \
             patch("orchestration.golden_loop.resolve_menu_item"), \
             patch("orchestration.golden_loop.evaluate_action") as mock_eval, \
             patch("orchestration.golden_loop.generate_response", return_value="Added!"):

            mock_eval.return_value = MagicMock(approved=True)
            golden_loop(
                session=session, user_input="Add a Margherita",
                kitchen=kitchen, memory=mock_memory
            )

        assert session.tool_budget_remaining == 4


class TestSilentHandoff:
    def test_systemic_handoff_with_recursion(self):
        """
        Jurisdiction mismatch triggers a silent auto-handoff via recursion.

        Turn 1: Authority rejects — wrong agent, RECOVERABLE.
                golden_loop swaps active_agent to MenuExpert and recurses.
        Turn 2: Authority approves — correct agent.

        Both evaluate_action calls happen within a single user turn.
        The mock's side_effect list verifies exactly this sequence.
        """
        session = create_valid_session("s_handoff")
        kitchen = KitchenSnapshot(load_percentage=10)
        mock_memory = MagicMock()

        mock_result_1 = MagicMock(
            approved=False,
            violation_type=ViolationType.INVALID_STATE,
            severity=Severity.RECOVERABLE,
            requires_clarification=False,
            meta={"target_agent": "MenuExpert"}
        )
        mock_result_2 = MagicMock(approved=True)

        mock_router_action = MagicMock(
            intent="INQUIRY",
            target_agent="MenuExpert",
            confidence=1.0
        )

        mock_me = MagicMock()
        # Must NOT be NO_OP — NO_OP short-circuits before evaluate_action
        mock_me.run.return_value = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="P1",
            quantity=1
        )

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"OrderTaker": MagicMock(), "MenuExpert": mock_me}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY), \
             patch("orchestration.golden_loop.evaluate_action") as mock_eval, \
             patch("orchestration.golden_loop.generate_response", return_value="Expert answer."):

            mock_eval.side_effect = [mock_result_1, mock_result_2]
            response = golden_loop(
                session=session, user_input="How is it made?",
                kitchen=kitchen, memory=mock_memory
            )

        assert response == "Expert answer."
        assert session.active_agent == "MenuExpert"
        # Exactly 2 calls: one rejection + one approval across the recursive call
        assert mock_eval.call_count == 2

    def test_handoff_without_target_agent_does_not_recurse(self):
        """
        If Authority returns INVALID_STATE/RECOVERABLE but meta carries no
        target_agent, the loop must NOT recurse — it falls through to the
        uncategorized rejection guard instead.

        Prevents infinite recursion on malformed Authority responses.
        """
        session = create_valid_session("s_no_target")
        kitchen = KitchenSnapshot(load_percentage=10)

        mock_router_action = MagicMock(
            intent="ORDERING",
            target_agent="OrderTaker",
            confidence=1.0
        )

        mock_ot = MagicMock()
        mock_ot.run.return_value = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="P1",
            quantity=1
        )

        mock_result = MagicMock(
            approved=False,
            violation_type=ViolationType.INVALID_STATE,
            severity=Severity.RECOVERABLE,
            requires_clarification=False,
            meta={},  # No target_agent — handoff cannot proceed
            rejection_code="ERR_INVALID_STATE",
            system_hint="No target."
        )

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"OrderTaker": mock_ot}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY), \
             patch("orchestration.golden_loop.evaluate_action", return_value=mock_result), \
             patch("orchestration.golden_loop.generate_response", return_value="Fallback."):

            response = golden_loop(
                session=session, user_input="Add pizza",
                kitchen=kitchen, memory=MagicMock()
            )

        # Loop exits via uncategorized rejection guard — does not recurse
        assert response == "Fallback."


class TestFatalStop:
    def test_fatal_stops_immediately(self):
        """
        A FATAL violation must terminate the loop and return the Authority's
        user_message directly. No generate_response, no memory update race.
        """
        session = create_valid_session("s_fatal")
        session.order_status = "CONFIRMED"
        kitchen = KitchenSnapshot(load_percentage=10)

        mock_router_action = MagicMock(
            intent="ORDERING",
            target_agent="OrderTaker",
            confidence=1.0
        )

        mock_ot = MagicMock()
        mock_ot.run.return_value = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="P1",
            quantity=1
        )

        mock_result = MagicMock(
            approved=False,
            severity=Severity.FATAL,
            user_message="Order is locked.",
            requires_clarification=False,
        )

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"OrderTaker": mock_ot}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY), \
             patch("orchestration.golden_loop.evaluate_action", return_value=mock_result):

            response = golden_loop(
                session=session, user_input="Add pizza",
                kitchen=kitchen, memory=MagicMock()
            )

        assert response == "Order is locked."


class TestDeferredCapability:
    def test_deferred_passes_capability_meta_to_generator(self):
        """
        A DEFERRED result must construct a recovery ASK_CLARIFICATION action
        and pass the original meta (including required_capability) to
        generate_response. The UI/orchestrator reads this to know what
        external capability to trigger (e.g. ID_VERIFIER).
        """
        session = create_valid_session("s_defer")
        kitchen = KitchenSnapshot(load_percentage=10)
        mock_memory = MagicMock()

        mock_router_action = MagicMock(
            intent="ORDERING",
            target_agent="OrderTaker",
            confidence=1.0
        )

        mock_ot = MagicMock()
        mock_ot.run.return_value = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="BEER-001",
            quantity=1
        )

        mock_result = MagicMock(
            approved=False,
            severity=Severity.DEFERRED,
            violation_type=ViolationType.AGE_RESTRICTION,
            requires_clarification=False,
            user_message="I need to see your ID.",
            meta={"required_capability": "ID_VERIFIER"}
        )

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"OrderTaker": mock_ot}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY), \
             patch("orchestration.golden_loop.evaluate_action", return_value=mock_result), \
             patch("orchestration.golden_loop.generate_response") as mock_gen:

            mock_gen.return_value = "Please show your ID."
            golden_loop(
                session=session, user_input="Beer please",
                kitchen=kitchen, memory=mock_memory
            )

            # The recovery action passed to generate_response must carry
            # the original capability meta so the UI knows what to trigger
            recovery_action = mock_gen.call_args.kwargs["action"]
            assert recovery_action.action_type == ActionType.ASK_CLARIFICATION
            assert recovery_action.meta["required_capability"] == "ID_VERIFIER"

    def test_deferred_does_not_consume_budget(self):
        """
        DEFERRED exits before consume_tool_budget is called.
        Budget must be unchanged after a deferred response.
        """
        session = create_valid_session("s_defer_budget", budget=5)
        kitchen = KitchenSnapshot(load_percentage=10)

        mock_router_action = MagicMock(
            intent="ORDERING",
            target_agent="OrderTaker",
            confidence=1.0
        )

        mock_ot = MagicMock()
        mock_ot.run.return_value = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku="BEER-001",
            quantity=1
        )

        mock_result = MagicMock(
            approved=False,
            severity=Severity.DEFERRED,
            violation_type=ViolationType.AGE_RESTRICTION,
            requires_clarification=False,
            user_message="Need ID.",
            meta={"required_capability": "ID_VERIFIER"}
        )

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"OrderTaker": mock_ot}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY), \
             patch("orchestration.golden_loop.evaluate_action", return_value=mock_result), \
             patch("orchestration.golden_loop.generate_response", return_value="Show ID."):

            golden_loop(
                session=session, user_input="Beer please",
                kitchen=kitchen, memory=MagicMock()
            )

        assert session.tool_budget_remaining == 5


class TestScopeGovernance:
    def test_scope_is_set_on_session_before_agent_runs(self):
        """
        Verifies the architectural fix: session.context_scope must be set
        by decide_context_scope BEFORE the agent's run() is called.

        We assert this by checking that when the agent's run() is invoked,
        the session it receives already has the scope from the mock policy.
        This is the key regression test for the original bug where scope
        was set after agent execution.
        """
        session = create_valid_session("s_scope_order")
        kitchen = KitchenSnapshot(load_percentage=10)

        mock_router_action = MagicMock(
            intent="INQUIRY",
            target_agent="MenuExpert",
            confidence=0.9
        )

        captured_scope = {}

        def capture_scope(user_input, sess, memory):
            # Capture what context_scope is on the session when run() is called
            captured_scope["scope"] = sess.context_scope
            return ActionRequest(
                action_type=ActionType.NO_OP,
                message="Scope captured."
            )

        mock_expert = MagicMock()
        mock_expert.run.side_effect = capture_scope

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"MenuExpert": mock_expert}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY):

            golden_loop(
                session=session, user_input="Anything spicy?",
                kitchen=kitchen, memory=MagicMock()
            )

        # Scope must be set before agent.run() was called
        assert captured_scope["scope"] == ContextScope.FULL_CATALOG

    def test_decide_context_scope_called_with_user_input(self):
        """
        decide_context_scope must receive user_input as its second argument.
        Without it, the QueryClassifier never sees the query and scope
        defaults to FILTERED_SEARCH for all attribute queries.
        """
        session = create_valid_session("s_scope_input")
        kitchen = KitchenSnapshot(load_percentage=10)

        mock_router_action = MagicMock(
            intent="INQUIRY",
            target_agent="MenuExpert",
            confidence=0.9
        )

        mock_expert = MagicMock()
        mock_expert.run.return_value = ActionRequest(
            action_type=ActionType.NO_OP,
            message="Sure."
        )

        with patch(PATCH_ROUTER, return_value=mock_router_action), \
             patch(PATCH_REGISTRY, {"MenuExpert": mock_expert}), \
             patch(PATCH_SCOPE, return_value=MOCK_SCOPE_POLICY) as mock_scope:

            golden_loop(
                session=session, user_input="Anything spicy?",
                kitchen=kitchen, memory=MagicMock()
            )

        # First positional arg is session, second must be the raw user_input
        call_args = mock_scope.call_args
        assert call_args.args[1] == "Anything spicy?"