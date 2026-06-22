# # DineFlow/orchestration/memory_manager.py
# from tools.search.vector import save_memory, retrieve_memories
# from typing import Optional, Any
# class MemoryManager:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.window = []  # Short-term sliding window

#     def update(self, user_in: str, aiva_out: str, agent_name: str = "OrderTaker", **meta: Any):
#         """
#         Records the turn in both the short-term window and long-term vector store.
#         The agent_name helps distinguish context when multiple agents are used.
#         Meta can include: status, action_type, violation, intent, etc.
#         """
#         # 1. Update Short-term Window (Sliding)
#         record = {
#             "agent": agent_name,
#             "user": user_in,
#             "aiva": aiva_out,
#             **meta
#         }
#         self.window.append(record)
        
#         if len(self.window) > 3:
#             self.window.pop(0)

#         # 2. Update Long-term Memory (Vector DB)
#         # We pass the agent_name here to be stored in metadata/documents
#         save_memory(
#             session_id=self.session_id, 
#             user_in=user_in, 
#             aiva_out=aiva_out,
#             agent_name=agent_name,
#             meta=meta
#         )
#     def last(self) -> dict | None:
#         return self.window[-1] if self.window else None
    
#     def get_context(self, current_input: str, limit: Optional[int] = None) -> str:
#         """
#         Retrieves hybrid context with optional turn limiting.
        
#         Args:
#             current_input: Current user query for semantic retrieval
#             limit: Max number of recent turns to include (None = all in window)
        
#         Returns:
#             Formatted context string with past facts + recent chat
#         """
#         # --- 1. Recent Window Construction ---
#         window_to_use = self.window[-limit:] if limit else self.window
        
#         if not window_to_use:
#             recent = "No recent history."
#         else:
#             recent = "\n".join([
#                 f"[{t['agent']}] User: {t['user']}\n[{t['agent']}] DineFlow: {t['aiva']}" 
#                 for t in window_to_use
#             ])
        
#         # --- 2. Long-term Semantic Retrieval ---
#         past = retrieve_memories(self.session_id, query=current_input)
        
#         if past:
#             past_str = "\n".join(past)
#         else:
#             past_str = "No specific past facts relevant to this query."
        
#         return f"--- RELEVANT PAST FACTS ---\n{past_str}\n\n--- RECENT CHAT WINDOW ---\n{recent}"






# claud recent version testing.....

# DineFlow/orchestration/memory_manager.py
# from tools.search.vector import save_memory, retrieve_memories
# from typing import Optional, Any


# class MemoryManager:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.window = []  # Short-term sliding window

#     def update(self, user_in: str, aiva_out: str, agent_name: str = "OrderTaker", **meta: Any):
#         """
#         Records the turn in both the short-term window and long-term vector store.
#         Meta can include: status, action_type, violation, intent, etc.
#         """
#         record = {
#             "agent": agent_name,
#             "user": user_in,
#             "aiva": aiva_out,
#             **meta
#         }
#         self.window.append(record)

#         if len(self.window) > 3:
#             self.window.pop(0)

#         save_memory(
#             session_id=self.session_id,
#             user_in=user_in,
#             aiva_out=aiva_out,
#             agent_name=agent_name,
#             meta=meta
#         )

#     def last(self) -> dict | None:
#         return self.window[-1] if self.window else None

#     def pending_clarification(self) -> Optional[dict]:
#         """
#         Returns the last window turn if it was a clarification request, else None.

#         Canonical method for agents to detect they are handling a response to
#         their own question. Centralises window inspection so no agent
#         reimplements this pattern independently.

#         Returns the full turn record so callers have access to both the
#         question that was asked ('aiva') and any metadata on that turn
#         (e.g. action_type, status).
#         """
#         last = self.last()
#         if last and last.get("status") in {"agent_clarification", "authority_clarification"}:
#             return last
#         return None

#     def get_context(self, current_input: str, limit: Optional[int] = None) -> str:
#         """
#         Retrieves hybrid context: recent window turns + semantically retrieved past facts.

#         Args:
#             current_input: Current user query for semantic retrieval.
#             limit: Max recent turns to include (None = all in window).

#         Returns:
#             Formatted context string.
#         """
#         window_to_use = self.window[-limit:] if limit else self.window

#         if not window_to_use:
#             recent = "No recent history."
#         else:
#             recent = "\n".join([
#                 f"[{t['agent']}] User: {t['user']}\n[{t['agent']}] DineFlow: {t['aiva']}"
#                 for t in window_to_use
#             ])

#         past = retrieve_memories(self.session_id, query=current_input)
#         past_str = "\n".join(past) if past else "No specific past facts relevant to this query."

#         return f"--- RELEVANT PAST FACTS ---\n{past_str}\n\n--- RECENT CHAT WINDOW ---\n{recent}"

#     def get_context_with_clarification_hint(self, current_input: str) -> str:
#         """
#         Like get_context(), but prepends a structured hint when the current
#         input is a response to a pending clarification.

#         Problem this solves:
#             User:     "add 2 pepperoni"
#             DineFlow: "Could you confirm: 2 Pepperoni Pizzas?"
#             User:     "yes"

#             hybrid_search("yes") returns near-zero scores — no menu tokens.
#             The LLM receives poor context and produces NO_OP because it cannot
#             reconstruct what "yes" refers to from the raw window alone.

#         Fix:
#             When the last turn was a clarification, prepend a PENDING ACTION
#             block to the context string. The LLM reads this first and knows
#             exactly what it asked and what to do with a confirmation or denial.

#         If no pending clarification exists, returns identical output to get_context()
#         — callers do not need to branch on this.
#         """
#         base_context = self.get_context(current_input)
#         pending = self.pending_clarification()

#         if not pending:
#             return base_context

#         hint = (
#             "--- PENDING CLARIFICATION RESPONSE ---\n"
#             f"You previously asked: \"{pending['aiva']}\"\n"
#             "The user is now responding to that question.\n"
#             "If confirming: produce the ADD_TO_CART action implied by that question with the correct SKU.\n"
#             "If denying or changing topic: produce NO_OP.\n"
#             "--- END PENDING CLARIFICATION ---\n\n"
#         )

#         return hint + base_context


# # DineFlow/orchestration/memory_manager.py
# from tools.search.vector import save_memory, retrieve_memories
# from typing import Optional, Any


# class MemoryManager:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.window = []  # Short-term sliding window

#     def update(self, user_in: str, dine_flow_out: str, agent_name: str = "OrderTaker", **meta: Any):
#         """
#         Records the turn in both the short-term window and long-term vector store.
#         Meta can include: status, action_type, pending_sku, violation, intent, etc.
#         """
#         record = {
#             "agent": agent_name,
#             "user": user_in,
#             "dine_flow": dine_flow_out,
#             **meta
#         }
#         self.window.append(record)

#         if len(self.window) > 3:
#             self.window.pop(0)

#         save_memory(
#             session_id=self.session_id,
#             user_in=user_in,
#             dine_flow=dine_flow_out,
#             agent_name=agent_name,
#             meta=meta
#         )

#     def last(self) -> dict | None:
#         return self.window[-1] if self.window else None

#     def pending_clarification(self) -> Optional[dict]:
#         """
#         Returns the last window turn if it was a clarification request, else None.

#         Canonical method for agents to detect they are handling a response to
#         their own question. Centralises window inspection so no agent
#         reimplements this pattern independently.

#         Returns the full turn record — callers can read 'dine_flow' (the question
#         asked), 'pending_sku' (the resolved SKU if available), and any other
#         metadata stored on that turn.
#         """
#         last = self.last()
#         if last and last.get("status") in {"agent_clarification", "authority_clarification"}:
#             return last
#         return None

#     def get_context(self, current_input: str, limit: Optional[int] = None) -> str:
#         """
#         Retrieves hybrid context: recent window turns + semantically retrieved past facts.

#         Args:
#             current_input: Current user query for semantic retrieval.
#             limit: Max recent turns to include (None = all in window).

#         Returns:
#             Formatted context string.
#         """
#         window_to_use = self.window[-limit:] if limit else self.window

#         if not window_to_use:
#             recent = "No recent history."
#         else:
#             recent = "\n".join([
#                 f"[{t['agent']}] User: {t['user']}\n[{t['agent']}] DineFlow: {t['dine_flow']}"
#                 for t in window_to_use
#             ])

#         past = retrieve_memories(self.session_id, query=current_input)
#         past_str = "\n".join(past) if past else "No specific past facts relevant to this query."

#         return f"--- RELEVANT PAST FACTS ---\n{past_str}\n\n--- RECENT CHAT WINDOW ---\n{recent}"

#     def get_context_with_clarification_hint(self, current_input: str) -> str:
#         """
#         Like get_context(), but prepends a structured hint when the current
#         input is a response to a pending clarification.

#         The hint has two tiers based on what was stored on the pending turn:

#         Tier 1 — SKU known (pending_sku is set):
#             The agent already resolved the item on the previous turn.
#             The hint names both the question AND the exact SKU explicitly.
#             The LLM does not need to infer anything — it just confirms or denies.

#             This is the case for:
#               - authority_clarification (LOW_CONFIDENCE): agent resolved PZ-MARG,
#                 authority asked for confirmation → pending_sku="PZ-MARG"
#               - agent_clarification with resolved SKU: agent asked to confirm
#                 a specific item it had already identified

#         Tier 2 — SKU unknown (pending_sku is None):
#             The agent could not resolve a SKU on the previous turn
#             (e.g. "add pizza" → clarification "which pizza?").
#             The hint names the question and instructs the LLM to resolve
#             the item from the user's current response.

#         If no pending clarification exists, returns identical output to
#         get_context() — callers do not need to branch.
#         """
#         base_context = self.get_context(current_input)
#         pending = self.pending_clarification()

#         if not pending:
#             return base_context

#         pending_sku = pending.get("pending_sku")

#         if pending_sku:
#             # Tier 1: SKU already resolved — name it explicitly.
#             # The LLM only needs to decide confirm vs deny, not infer the item.
#             hint = (
#                 "--- PENDING CLARIFICATION RESPONSE ---\n"
#                 f"You previously asked: \"{pending['dine_flow']}\"\n"
#                 f"The item in question has SKU: {pending_sku}\n"
#                 "The user is now responding to that question.\n"
#                 f"If confirming: produce ADD_TO_CART with sku=\"{pending_sku}\".\n"
#                 "If denying or changing topic: produce NO_OP.\n"
#                 "--- END PENDING CLARIFICATION ---\n\n"
#             )
#         else:
#             # Tier 2: SKU not yet known — instruct LLM to resolve from response.
#             hint = (
#                 "--- PENDING CLARIFICATION RESPONSE ---\n"
#                 f"You previously asked: \"{pending['dine_flow']}\"\n"
#                 "The user is now responding to that question.\n"
#                 "Resolve the item they specify from the menu above and produce ADD_TO_CART with the correct SKU.\n"
#                 "If unclear or denying: produce NO_OP.\n"
#                 "--- END PENDING CLARIFICATION ---\n\n"
#             )

#         return hint + base_context


# DineFlow/orchestration/memory_manager.py
from tools.search.vector import save_memory, retrieve_memories
from typing import Optional, Any


class MemoryManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.window = []  # Short-term sliding window

    def update(self, user_in: str, dine_flow_out: str, agent_name: str = "OrderTaker", **meta: Any):
        """
        Records the turn in both the short-term window and long-term vector store.
        Meta can include: status, action_type, pending_sku, violation, intent, etc.
        """
        record = {
            "agent": agent_name,
            "user": user_in,
            "dine_flow": dine_flow_out,
            **meta
        }
        self.window.append(record)

        if len(self.window) > 3:
            self.window.pop(0)

        save_memory(
            session_id=self.session_id,
            user_in=user_in,
            dine_flow=dine_flow_out,
            agent_name=agent_name,
            meta=meta
        )

    def last(self) -> dict | None:
        return self.window[-1] if self.window else None

    def pending_clarification(self) -> Optional[dict]:
        """
        Returns the last window turn if it was a clarification request, else None.
        Centralises window inspection so no agent reimplements this pattern.
        """
        last = self.last()
        if last and last.get("status") in {"agent_clarification", "authority_clarification"}:
            return last
        return None

    def get_context(self, current_input: str, limit: Optional[int] = None) -> str:
        """
        Retrieves hybrid context: recent window turns + semantically retrieved past facts.
        """
        window_to_use = self.window[-limit:] if limit else self.window

        if not window_to_use:
            recent = "No recent history."
        else:
            recent = "\n".join([
                f"[{t['agent']}] User: {t['user']}\n[{t['agent']}] DineFlow: {t['dine_flow']}"
                for t in window_to_use
            ])

        past = retrieve_memories(self.session_id, query=current_input)
        past_str = "\n".join(past) if past else "No specific past facts relevant to this query."

        return f"--- RELEVANT PAST FACTS ---\n{past_str}\n\n--- RECENT CHAT WINDOW ---\n{recent}"

    def get_context_with_clarification_hint(self, current_input: str) -> str:
        """
        Like get_context(), but prepends a structured hint when the current
        input is a response to a pending clarification.

        Tier 1 — SKU known: LLM only needs to confirm or deny.
        Tier 2 — SKU unknown: LLM resolves from user response.
        """
        base_context = self.get_context(current_input)
        pending = self.pending_clarification()

        if not pending:
            return base_context

        pending_sku = pending.get("pending_sku")

        if pending_sku:
            hint = (
                "--- PENDING CLARIFICATION RESPONSE ---\n"
                f"You previously asked: \"{pending['dine_flow']}\"\n"
                f"The item in question has SKU: {pending_sku}\n"
                "The user is now responding to that question.\n"
                f"If confirming: produce ADD_TO_CART with sku=\"{pending_sku}\".\n"
                "If denying or changing topic: produce NO_OP.\n"
                "--- END PENDING CLARIFICATION ---\n\n"
            )
        else:
            hint = (
                "--- PENDING CLARIFICATION RESPONSE ---\n"
                f"You previously asked: \"{pending['dine_flow']}\"\n"
                "The user is now responding to that question.\n"
                "Resolve the item they specify from the menu above and produce ADD_TO_CART with the correct SKU.\n"
                "If unclear or denying: produce NO_OP.\n"
                "--- END PENDING CLARIFICATION ---\n\n"
            )

        return hint + base_context

    def get_focus_block(self, session, all_menu_items: list, user_input: str) -> str:
        """
        Builds the CONVERSATIONAL FOCUS block for injection into the OrderTaker prompt.

        Resolution priority:
            1. active_context — most recently selected item (confirmed/ordered)
            2. last_action_sku — safety net if context has no selected item

        Signal classification tells the LLM what the user's reference likely means.
        The signal is a HINT — the LLM sees full chat history and can override it.

        Returns empty string if no focus can be determined — callers do not branch.
        """
        # Priority 1: most recently selected item from active_context
        focus_sku = None
        if hasattr(session, "active_context") and session.active_context:
            selected = [
                item for item in session.active_context.values()
                if item.selected
            ]
            if selected:
                selected.sort(key=lambda x: x.last_mentioned_turn, reverse=True)
                focus_sku = selected[0].sku

        # Priority 2: last_action_sku safety net
        if not focus_sku:
            focus_sku = getattr(session, "last_action_sku", None)

        if not focus_sku:
            return ""

        item = next((i for i in all_menu_items if i.sku == focus_sku), None)
        if not item:
            return ""

        normalized = user_input.strip().lower()
        last_qty = getattr(session, "last_quantity", 1) or 1

        if normalized.isdigit() or self._is_number_word(normalized):
            signal = "SIGNAL: Potential Quantity Update (Numeric Only)"
        elif any(w in normalized for w in ["same again", "same", "again"]):
            signal = f"SIGNAL: Repeat Last Order — use quantity={last_qty} and sku={item.sku}"
        elif any(w in normalized for w in ["another", "more", "one more"]):
            signal = "SIGNAL: Potential Repeat/Increment Request"
        elif normalized.startswith("make it"):
            signal = "SIGNAL: Potential Quantity Override"
        elif any(w in normalized for w in ["cancel", "undo", "remove that", "cancel that", "never mind", "forget it"]):
            signal = f"SIGNAL: Cancellation — remove sku={item.sku} quantity={last_qty} from cart"
        else:
            signal = "SIGNAL: New Intent / Open Query"

        return (
            "--- CONVERSATIONAL FOCUS ---\n"
            f"Active Item: {item.name} (SKU: {item.sku})\n"
            f"Last Quantity: {last_qty}\n"
            f"Detected Intent Signal: {signal}\n"
            f"Note: If the signal is a Quantity Update/Repeat, apply it to {item.sku}.\n"
            "--- END FOCUS ---\n\n"
        )

    @staticmethod
    def _is_number_word(text: str) -> bool:
        """Returns True for English number words up to ten."""
        return text in {
            "one", "two", "three", "four", "five",
            "six", "seven", "eight", "nine", "ten"
        }