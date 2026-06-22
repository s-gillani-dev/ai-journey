# # DineFlow/tests/unit/test_memory_manager.py
# from unittest.mock import MagicMock, patch
# from orchestration.memory_manager import MemoryManager

# def test_memory_window_sliding():
#     """Ensure short-term window only keeps the last 2 turns."""
#     manager = MemoryManager(session_id="test-session")
    
#     with patch("orchestration.memory_manager.save_memory"):
#         manager.update("Order 1", "DineFlow 1", agent_name="AgentA")
#         manager.update("Order 2", "DineFlow 2", agent_name="AgentB")
#         manager.update("Order 3", "DineFlow 3", agent_name="AgentC")
    
#     assert len(manager.window) == 2
#     # Verify the sliding window preserved the correct agents/turns
#     assert manager.window[0]["agent"] == "AgentB"
#     assert manager.window[1]["user"] == "Order 3"

# def test_get_context_assembly():
#     """Verify that context combines both recent turns and retrieved past turns."""
#     manager = MemoryManager(session_id="test-session")
#     # Manually seed the window for testing
#     manager.window = [{"agent": "OrderTaker", "user": "Recent User", "DineFlow": "Recent DineFlow"}]
    
#     mock_past = ["User: I am allergic to nuts\nDineFlow: Noted."]
    
#     with patch("orchestration.memory_manager.retrieve_memories", return_value=mock_past):
#         context = manager.get_context("Current Input")
        
#         assert "Recent User" in context
#         assert "allergic to nuts" in context
#         assert "[OrderTaker]" in context
#         assert "--- RELEVANT PAST FACTS ---" in context





# claud recnt version testing...

# DineFlow/tests/unit/test_memory_manager.py
from unittest.mock import MagicMock, patch
import pytest
from orchestration.memory_manager import MemoryManager


# =============================================================================
# SHARED FIXTURES
# =============================================================================

@pytest.fixture
def manager():
    """Fresh MemoryManager with save_memory patched out for all tests."""
    with patch("orchestration.memory_manager.save_memory"):
        yield MemoryManager(session_id="test-session")


# =============================================================================
# SHORT-TERM WINDOW TESTS
# =============================================================================

class TestSlidingWindow:
    def test_window_keeps_last_three_turns(self, manager):
        """
        Window pops when len > 3, so it holds up to 3 turns.
        Adding a 4th must evict Turn 1, not the last.

        Original test asserted cap=2 after 3 inserts — that was wrong.
        The implementation pops when len > 3, meaning 3 inserts all fit.
        Eviction first fires on the 4th insert.
        """
        with patch("orchestration.memory_manager.save_memory"):
            manager.update("Order 1", "Resp 1", agent_name="AgentA")
            manager.update("Order 2", "Resp 2", agent_name="AgentB")
            manager.update("Order 3", "Resp 3", agent_name="AgentC")
            manager.update("Order 4", "Resp 4", agent_name="AgentD")

        assert len(manager.window) == 3
        assert manager.window[0]["agent"] == "AgentB"
        assert manager.window[2]["user"] == "Order 4"

    def test_three_turns_do_not_evict(self, manager):
        """Exactly 3 turns must all be retained — eviction only fires on the 4th."""
        with patch("orchestration.memory_manager.save_memory"):
            manager.update("Order 1", "Resp 1", agent_name="AgentA")
            manager.update("Order 2", "Resp 2", agent_name="AgentB")
            manager.update("Order 3", "Resp 3", agent_name="AgentC")

        assert len(manager.window) == 3

    def test_window_empty_on_init(self, manager):
        """Window must start empty — no phantom turns from prior sessions."""
        assert manager.window == []

    def test_window_holds_one_turn_before_cap(self, manager):
        """Window of exactly 1 turn must not evict anything."""
        with patch("orchestration.memory_manager.save_memory"):
            manager.update("Only turn", "Only response", agent_name="AgentA")

        assert len(manager.window) == 1
        assert manager.window[0]["user"] == "Only turn"

    def test_window_preserves_status_field(self, manager):
        """
        The status field is written by the golden loop to mark clarification
        turns. _is_optimistic_mutation_authorized reads last_turn.get("status")
        to decide whether a noun-only order is safe. It must survive writes
        and remain accessible on the correct turn.
        """
        with patch("orchestration.memory_manager.save_memory"):
            manager.update(
                "Which pizza?", "Which one?",
                agent_name="MenuExpert",
                status="agent_clarification"
            )
            manager.update("Pepperoni", "Added!", agent_name="OrderTaker")

        assert manager.window[0].get("status") == "agent_clarification"


# =============================================================================
# CONTEXT ASSEMBLY TESTS
# =============================================================================

class TestGetContext:
    def test_combines_window_and_past_memories(self, manager):
        """
        get_context must interleave recent window turns with retrieved
        semantic memories so the LLM sees both short-term and long-term context.

        Key fix: window stores assistant response under 'aiva', not 'DineFlow'.
        get_context formats it as: [Agent] DineFlow: {t['aiva']}
        So the content of 'aiva' appears in output, keyed as 'aiva' in the dict.
        """
        # 'aiva' is the correct key — update() stores it as 'aiva'
        # and get_context reads t['aiva'] to build the formatted string.
        # Original test used 'DineFlow' which is silently ignored,
        # making the "Recent DineFlow" content assertion always fail.
        manager.window = [
            {"agent": "OrderTaker", "user": "Recent User", "aiva": "Recent Resp"}
        ]
        mock_past = ["User: I am allergic to nuts\nDineFlow: Noted."]

        with patch("orchestration.memory_manager.retrieve_memories", return_value=mock_past):
            context = manager.get_context("Current Input")

        assert "Recent User" in context
        assert "Recent Resp" in context
        assert "allergic to nuts" in context
        assert "[OrderTaker]" in context
        assert "--- RELEVANT PAST FACTS ---" in context
        assert "--- RECENT CHAT WINDOW ---" in context

    def test_returns_string_with_empty_window_and_no_memories(self, manager):
        """
        get_context must not crash or return None when both sources are empty.
        The LLM prompt always interpolates this return value — None would
        cause a TypeError at prompt construction time.
        """
        with patch("orchestration.memory_manager.retrieve_memories", return_value=[]):
            context = manager.get_context("Hello")

        assert isinstance(context, str)
        assert "--- RELEVANT PAST FACTS ---" in context
        assert "--- RECENT CHAT WINDOW ---" in context

    def test_limit_parameter_restricts_window_turns(self, manager):
        """
        get_context(limit=1) must include at most 1 window turn.
        get_context uses window[-limit:] so limit=1 returns only the last turn.
        """
        manager.window = [
            {"agent": "AgentA", "user": "Turn 1", "aiva": "Resp 1"},
            {"agent": "AgentB", "user": "Turn 2", "aiva": "Resp 2"},
        ]

        with patch("orchestration.memory_manager.retrieve_memories", return_value=[]):
            context = manager.get_context("Current", limit=1)

        assert "Turn 2" in context
        assert "Turn 1" not in context

    def test_no_limit_includes_all_window_turns(self, manager):
        """
        get_context with no limit must include all turns in the window.
        Verifies that limit=None does not accidentally slice to zero.
        """
        manager.window = [
            {"agent": "AgentA", "user": "Turn 1", "aiva": "Resp 1"},
            {"agent": "AgentB", "user": "Turn 2", "aiva": "Resp 2"},
            {"agent": "AgentC", "user": "Turn 3", "aiva": "Resp 3"},
        ]

        with patch("orchestration.memory_manager.retrieve_memories", return_value=[]):
            context = manager.get_context("Current")

        assert "Turn 1" in context
        assert "Turn 2" in context
        assert "Turn 3" in context