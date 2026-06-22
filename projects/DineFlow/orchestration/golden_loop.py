# 1.0 version old, (without helper functions) but tested
# aiva/orchestration/golden_loop
# from pathlib import Path
# from aiva.tools.registry import get_menu_items
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution
# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action
# from aiva.state_machine.types import SessionState, KitchenSnapshot


# def render_prompt(template: str, *, menu_items: list) -> str:
#     menu_context = "\n".join(
#         f"- {item.sku}: {getattr(item, 'name', 'Unknown')}"
#         for item in menu_items
#     )
#     return template.replace("{{ menu_context }}", menu_context)


# def golden_loop(
#     *,
#     session: SessionState,
#     user_input: str,
#     kitchen: KitchenSnapshot,
# ):
#     # 1️⃣ Load REAL menu data
#     menu_items = get_menu_items()

#     # 2️⃣ Load prompt template
#     base_dir = Path(__file__).parent.parent 
#     prompt_path = base_dir / "llm" / "prompts" / "order_taker.md"
#     prompt_template = prompt_path.read_text()

#     # 3️⃣ Inject reality
#     system_prompt = render_prompt(
#         prompt_template,
#         menu_items=menu_items,
#     )

#     # 4️⃣ LLM call
#     raw_output = call_llm(system_prompt, user_input)
#     action = parse_action(raw_output)

#     # 5️⃣ Log intent (raw input + action)
#     log_intent(
#         session_id=session.session_id,
#         raw_input=user_input,
#         action=action,
#     )

#     # 6️⃣ Decrement tool budget
#     session.tool_budget_remaining -= 1

#     # 7️⃣ Resolve referenced menu item (if any)
#     menu_item = next(
#         (item for item in menu_items if item.sku == action.sku),
#         None,
#     )

#     # 8️⃣ Authority check
#     result = evaluate_action(
#         action=action,
#         session=session,
#         menu_item=menu_item,
#         kitchen=kitchen,
#     )

#     # 9️⃣ Execution log — fixed to match execution_logger signature
#     log_execution(
#         session_id=session.session_id,
#         action=action,
#         status="approved" if result.approved else "rejected",
#         rejection_code=getattr(result, "rejection_code", None),
#     )

#     # 🔟 Final response
#     # return generate_response(result)
#     return generate_response(action=action, result=result)







# 1.1 version cleaned version with helper functions implementation (without AmbiguityGate) also tested.
# aiva/orchestration/golden_loop
# from aiva.tools.registry import get_menu_items
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action

# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution

# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action
# from aiva.state_machine.types import SessionState, KitchenSnapshot

# from aiva.orchestration.helpers import (
#     load_order_taker_prompt,
#     render_menu_context,
#     resolve_menu_item,
#     consume_tool_budget,
# )


# def golden_loop(
#     *,
#     session: SessionState,
#     user_input: str,
#     kitchen: KitchenSnapshot,
# ):
#     """
#     The Golden Loop is the authoritative orchestration boundary.
#     It coordinates — it does NOT decide.
#     """

#     # 1️⃣ Load real-world data (Reality Injection)
#     menu_items = get_menu_items()

#     # 2️⃣ Build system prompt
#     prompt_template = load_order_taker_prompt()
#     system_prompt = render_menu_context(
#         prompt_template=prompt_template,
#         menu_items=menu_items,
#     )

#     # 3️⃣ LLM reasoning boundary
#     raw_output = call_llm(system_prompt, user_input)
#     action = parse_action(raw_output)

#     # 4️⃣ Log intent (immutable audit)
#     log_intent(
#         session_id=session.session_id,
#         raw_input=user_input,
#         action=action,
#     )

#     # 5️⃣ Consume tool budget (mutation only)
#     consume_tool_budget(session)

#     # 6️⃣ Resolve referenced entities
#     menu_item = resolve_menu_item(menu_items, action.sku)

#     # 7️⃣ Authority check (ONLY decision point)
#     result = evaluate_action(
#         action=action,
#         session=session,
#         menu_item=menu_item,
#         kitchen=kitchen,
#     )

#     # 8️⃣ Execution log (post-decision)
#     log_execution(
#         session_id=session.session_id,
#         action=action,
#         status="approved" if result.approved else "rejected",
#         rejection_code=result.rejection_code,
#     )

#     # 9️⃣ Natural language response
#     return generate_response(
#         action=action,
#         result=result,
#     )








# # 1.2 Final version for step 1-4.
# # aiva/orchestration/golden_loop
# from aiva.tools.registry import get_menu_items
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action

# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution

# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.helpers import (
#     consume_tool_budget,
#     resolve_menu_item,
#     load_order_taker_prompt,
#     render_menu_context,
# )
# from aiva.orchestration.ambiguity_gate import AmbiguityGate
# from aiva.validation.schemas import ActionType


# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot):
#     # 1️⃣ Load real-world data
#     menu_items = get_menu_items()

#     # 2️⃣ Build system prompt
#     prompt_template = load_order_taker_prompt()
#     menu_string = render_menu_context(menu_items=menu_items)
#     system_prompt = prompt_template.replace("{{MENU_CONTEXT}}", menu_string)

#     # 3️⃣ LLM reasoning
#     raw_output = call_llm(system_prompt, user_input)
#     action = parse_action(raw_output)

#     # 4️⃣ Log intent
#     log_intent(session.session_id, user_input, action)

#     # 4.5️⃣ Ambiguity Gate (pre-authority, pre-budget)
#     action = AmbiguityGate.process(
#         session=session,
#         action=action,
#         menu_items=menu_items,
#         user_input=user_input,
#     )

#     # 🚨 EARLY EXIT: Clarification (NO authority, NO budget)
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         log_execution(
#             session_id=session.session_id,
#             action=action,
#             status="clarification_requested",
#             rejection_code=None,
#         )
#         return generate_response(action=action, result=None)

#     # 5️⃣ Resolve referenced entities
#     menu_item = resolve_menu_item(menu_items, action.sku)

#     # 6️⃣ Authority check (budget validation happens here)
#     result = evaluate_action(action, session, menu_item, kitchen)

#     # 6.5️⃣ Consume budget ONLY if authority approved
#     if result.approved:
#         consume_tool_budget(session)

#     # 7️⃣ Execution log
#     log_execution(
#         session_id=session.session_id,
#         action=action,
#         status="approved" if result.approved else "rejected",
#         rejection_code=result.rejection_code,
#     )

#     # 8️⃣ Final response
#     return generate_response(action=action, result=result)




# step 5
# aiva/orchestration/golden_loop
# from aiva.tools.registry import get_menu_items
# from aiva.llm.client import call_llm
# from aiva.llm.response_parser import parse_action
# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution
# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.helpers import (
#     consume_tool_budget,
#     resolve_menu_item,
#     load_order_taker_prompt,
#     render_menu_context,
# )
# from aiva.orchestration.ambiguity_gate import AmbiguityGate
# from aiva.validation.schemas import ActionType

# # STEP 5 NEW IMPORTS
# from aiva.tools.search.hybrid import hybrid_search
# from aiva.tools.search.bm25 import MenuBM25
# from aiva.tools.search.vector import sync_menu_to_vector
# from aiva.orchestration.memory_manager import MemoryManager

# # --- SEARCH INITIALIZATION ---
# all_menu_items = get_menu_items()
# _search_initialized = False
# bm25_engine = None

# def initialize_search():
#     """Initializes search engines once. This prevents crashes during test imports."""
#     global _search_initialized, bm25_engine
#     if not _search_initialized:
#         sync_menu_to_vector(all_menu_items)
#         bm25_engine = MenuBM25(all_menu_items)
#         _search_initialized = True

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     """
#     Main orchestration loop.
#     """
#     # Ensure search engines are ready before proceeding
#     initialize_search()
    
#     # 1️⃣ HYBRID SEARCH
#     relevant_menu_items = hybrid_search(user_input, all_menu_items, bm25_engine)
#     menu_string = render_menu_context(menu_items=relevant_menu_items)
#     print("MENU_CONTEXT------------------", menu_string)    

#     # 2️⃣ MEMORY RETRIEVAL
#     history_str = memory.get_context(user_input)
#     print("CHAT_HISTORY------------------", history_str)    


#     # 3️⃣ PROMPT ASSEMBLY
#     prompt_template = load_order_taker_prompt()
#     system_prompt = prompt_template.replace("{{MENU_CONTEXT}}", menu_string)
#     system_prompt = system_prompt.replace("{{CHAT_HISTORY}}", history_str)

#     # 4️⃣ LLM REASONING
#     raw_output = call_llm(system_prompt, user_input)
#     action = parse_action(raw_output)

#     # 5️⃣ LOG INTENT
#     log_intent(session.session_id, user_input, action)

#     # 6️⃣ AMBIGUITY GATE
#     action = AmbiguityGate.process(
#         session=session,
#         action=action,
#         menu_items=all_menu_items,
#         user_input=user_input,
#         bm25_engine=bm25_engine
#     )

#     # 🚨 EARLY EXIT: Clarification Required
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         log_execution(
#             session_id=session.session_id,
#             action=action,
#             status="clarification_requested",
#             rejection_code=None,
#         )
#         response_text = generate_response(action=action, result=None)
        
#         # ✅ FIXED: Included agent_name
#         memory.update(user_input, response_text, agent_name=session.active_agent)
#         return response_text

#     # 7️⃣ RESOLVE ENTITIES
#     menu_item = resolve_menu_item(all_menu_items, action.sku)

#     # 8️⃣ AUTHORITY LAYER
#     result = evaluate_action(action, session, menu_item, kitchen)

#     # 9️⃣ BUDGET CONSUMPTION
#     if result.approved:
#         consume_tool_budget(session)

#     # 🔟 LOG EXECUTION
#     log_execution(
#         session_id=session.session_id,
#         action=action,
#         status="approved" if result.approved else "rejected",
#         rejection_code=result.rejection_code,
#     )

#     # 11. FINAL RESPONSE GENERATION
#     final_response = generate_response(action=action, result=result)
    
#     # 12. MEMORY UPDATE
#     memory.update(user_input, final_response, agent_name=session.active_agent)

#     return final_response







# aiva/orchestration/golden_loop.py
# from aiva.agents.router import IntentRouter
# from aiva.agents.order_taker import OrderTakerAgent
# from aiva.tools.registry import get_menu_items
# from aiva.tools.search.bm25 import MenuBM25
# from aiva.tools.search.vector import sync_menu_to_vector  # ⬅️ RE-ADDED
# from aiva.validation.schemas import ActionType
# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution
# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action
# from aiva.orchestration.helpers import (
#     consume_tool_budget,
#     resolve_menu_item,
# )
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.memory_manager import MemoryManager

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items) # ⬅️ CRITICAL: Syncs menu to Vector DB
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once (Improvement 5)
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     # "Greeter": GreeterAgent(),  <- Next step
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1. ROUTING
#     routing_action = router.route(user_input, session.active_agent)
    
#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"
    
#     # 2. AGENT EXECUTION
#     agent = AGENT_REGISTRY[session.active_agent]
#     action = agent.run(user_input, session, memory)

#     # 3. LOGGING (Intent)
#     log_intent(session.session_id, user_input, action)

#     # 4. ⚡ POLISHED SHORT-CIRCUIT: Greeter / Social
#     if action.action_type == ActionType.NO_OP:
#         # 🛡️ OPTIONAL 1: Defensive check for missing message
#         response = action.message or "I'm here to help! What can I get for you?"
        
#         # 🛡️ OPTIONAL 2: Log execution for NO_OP (for metrics/analytics)
#         log_execution(
#             session_id=session.session_id,
#             action=action,
#             status="noop",
#             rejection_code=None
#         )
        
#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 5. EARLY EXIT: Clarifications
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None)
#         memory.update(user_input, response_text, agent_name=session.active_agent)
#         return response_text

#     # 6. GOVERNANCE: Authority & Budget
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen)

#     if result.approved:
#         consume_tool_budget(session)

#     log_execution(session.session_id, action, "approved" if result.approved else "rejected", result.rejection_code)

#     # 7. FINAL RESPONSE & MEMORY
#     final_response = generate_response(action=action, result=result)
#     memory.update(user_input, final_response, agent_name=session.active_agent)

#     return final_response



# fixing issue
# aiva/orchestration/golden_loop.py
# from aiva.agents.router import IntentRouter
# from aiva.agents.order_taker import OrderTakerAgent
# from aiva.agents.greeter import GreeterAgent  # ⬅️ FIXED: Added import
# from aiva.agents.menu_expert import MenuExpertAgent  # ⬅️ FIXED: Added import
# from aiva.tools.registry import get_menu_items
# from aiva.tools.search.bm25 import MenuBM25
# from aiva.tools.search.vector import sync_menu_to_vector
# from aiva.validation.schemas import ActionType
# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution
# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action
# from aiva.orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.memory_manager import MemoryManager

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),  
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1. ROUTING
#     routing_action = router.route(user_input, session.active_agent)
    
#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         # Update session state with the new agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"
    
#     # 2. AGENT EXECUTION
#     # ⬅️ FIXED: Ensure we fetch the agent AFTER the session state has been updated
#     current_agent_name = session.active_agent
#     agent = AGENT_REGISTRY[current_agent_name]
#     action = agent.run(user_input, session, memory)

#     # 3. LOGGING (Intent)
#     log_intent(session.session_id, user_input, action)

#     # 4. ⚡ SHORT-CIRCUIT: Greeter / MenuExpert (NO_OP handlers)
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
        
#         log_execution(
#             session_id=session.session_id,
#             action=action,
#             status="noop",
#             rejection_code=None
#         )
        
#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 5. EARLY EXIT: Clarifications
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None)
#         memory.update(user_input, response_text, agent_name=session.active_agent)
#         return response_text

#     # 6. GOVERNANCE: Authority & Budget
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen)

#     if result.approved:
#         consume_tool_budget(session)
#         # 🆕 Apply the changes to the cart!
#         apply_approved_action(session, action)

#     log_execution(session.session_id, action, "approved" if result.approved else "rejected", result.rejection_code)

#     # 7. FINAL RESPONSE & MEMORY
#     final_response = generate_response(action=action, result=result)
#     memory.update(user_input, final_response, agent_name=session.active_agent)

#     return final_response







# # aiva/orchestration/golden_loop.py
# from aiva.agents.router import IntentRouter
# from aiva.agents.order_taker import OrderTakerAgent
# from aiva.agents.greeter import GreeterAgent
# from aiva.agents.menu_expert import MenuExpertAgent
# from aiva.tools.registry import get_menu_items
# from aiva.tools.search.bm25 import MenuBM25
# from aiva.tools.search.vector import sync_menu_to_vector
# from aiva.validation.schemas import ActionType
# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution
# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action
# from aiva.orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.memory_manager import MemoryManager

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),  
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1. ROUTING
#     routing_action = router.route(user_input, session.active_agent)
    
#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"
    
#     # 2. AGENT EXECUTION
#     current_agent_name = session.active_agent
#     agent = AGENT_REGISTRY[current_agent_name]
#     action = agent.run(user_input, session, memory)

#     # 3. LOGGING (Intent)
#     log_intent(session.session_id, user_input, action)

#     # 4. ⚡ SHORT-CIRCUIT: Greeter / MenuExpert (NO_OP handlers)
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
        
#         log_execution(
#             session_id=session.session_id,
#             action=action,
#             status="noop",
#             rejection_code=None
#         )
        
#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 5. EARLY EXIT: Clarifications
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         # 🔧 FIX: Pass menu_items for better clarification messages (optional)
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         memory.update(user_input, response_text, agent_name=session.active_agent)
#         return response_text

#     # 6. GOVERNANCE: Authority & Budget
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen)

#     if result.approved:
#         consume_tool_budget(session)
#         apply_approved_action(session, action)  # 🔧 Now handles REMOVE quantity properly

#     log_execution(session.session_id, action, "approved" if result.approved else "rejected", result.rejection_code)

#     # 7. FINAL RESPONSE & MEMORY
#     # 🔧 FIX: Pass menu_items to resolve item names in responses
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)

#     return final_response







# claud gives this
# aiva/orchestration/golden_loop.py
# from aiva.agents.router import IntentRouter
# from aiva.agents.order_taker import OrderTakerAgent
# from aiva.agents.greeter import GreeterAgent
# from aiva.agents.menu_expert import MenuExpertAgent
# from aiva.tools.registry import get_menu_items
# from aiva.tools.search.bm25 import MenuBM25
# from aiva.tools.search.vector import sync_menu_to_vector
# from aiva.validation.schemas import ActionType, ActionRequest  # 🔧 Added ActionRequest import
# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution
# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action
# from aiva.orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.memory_manager import MemoryManager

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),  
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1. ROUTING
#     routing_action = router.route(user_input, session.active_agent)
    
#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"
    
#     # 2. AGENT EXECUTION
#     current_agent_name = session.active_agent
#     agent = AGENT_REGISTRY[current_agent_name]
#     action = agent.run(user_input, session, memory)

#     # 3. LOGGING (Intent)
#     log_intent(session.session_id, user_input, action)

#     # 4. ⚡ SHORT-CIRCUIT: Greeter / MenuExpert (NO_OP handlers)
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
        
#         log_execution(
#             session_id=session.session_id,
#             action=action,
#             status="noop",
#             rejection_code=None
#         )
        
#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 🔧 FIX: ASK_CLARIFICATION short-circuit BEFORE Authority to prevent budget consumption
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "clarification", None)
#         memory.update(user_input, response_text, agent_name=session.active_agent)
#         return response_text

#     # 6. GOVERNANCE: Authority & Budget
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
    
#     # Pass full menu to Authority for ambiguity detection
#     result = evaluate_action(action, session, menu_item, kitchen, all_menu_items)

#     # 7. Handle RECOVERABLE violations (convert to ASK_CLARIFICATION)
#     if not result.approved and result.requires_clarification:
#         # Authority says this needs clarification - create ASK_CLARIFICATION action
#         clarification_action = ActionRequest(
#             action_type=ActionType.ASK_CLARIFICATION,
#             clarification_payload=result.user_message or "Could you please clarify?",
#             confidence=1.0,
#             meta={"authority_violation": result.violation_type}
#         )
        
#         response_text = generate_response(action=clarification_action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, clarification_action, "clarification_required", result.violation_type)
#         memory.update(user_input, response_text, agent_name=session.active_agent)
#         return response_text

#     # 8. Apply approved actions (ONLY consumes budget for actual mutations)
#     if result.approved:
#         consume_tool_budget(session)
#         apply_approved_action(session, action)

#     log_execution(session.session_id, action, "approved" if result.approved else "rejected", result.rejection_code)

#     # 9. FINAL RESPONSE & MEMORY
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)

#     return final_response






# gemini gives the claud verson with fixes (testing)
# # aiva/orchestration/golden_loop.py
# from aiva.agents.router import IntentRouter
# from aiva.agents.order_taker import OrderTakerAgent
# from aiva.agents.greeter import GreeterAgent
# from aiva.agents.menu_expert import MenuExpertAgent
# from aiva.tools.registry import get_menu_items
# from aiva.tools.search.bm25 import MenuBM25
# from aiva.tools.search.vector import sync_menu_to_vector
# from aiva.validation.schemas import ActionType, ActionRequest
# from aiva.logging.intent_logger import log_intent
# from aiva.logging.execution_logger import log_execution
# from aiva.response.generator import generate_response
# from aiva.state_machine.authority import evaluate_action, decide_context_scope
# from aiva.orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.memory_manager import MemoryManager
# from aiva.validation.errors import ViolationType

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),  
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1. ROUTING
#     routing_action = router.route(user_input, session.active_agent)
#     # 🆕 Persist intent at session level
#     if routing_action.intent:
#         session.active_intent = routing_action.intent
    
#     # ✅ SYSTEMIC FIX: Always sync session intent with latest routing decision 
#     # to prevent stale 'ORDERING' intent from lingering during inquiries.
#     session.active_intent = routing_action.intent

#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"
    
#     # 2. AGENT EXECUTION
#     current_agent_name = session.active_agent
#     agent = AGENT_REGISTRY[current_agent_name]
#     action = agent.run(user_input, session, memory)

#     # 3. LOGGING (Intent)
#     log_intent(session.session_id, user_input, action)

#     # 4. ⚡ SHORT-CIRCUIT: Greeter / MenuExpert (NO_OP handlers)
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
        
#         log_execution(
#             session_id=session.session_id,
#             action=action,
#             status="noop",
#             rejection_code=None
#         )
        
#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 5. ⚡ SHORT-CIRCUIT: Explicit Agent Clarification
#     # If the agent itself realizes it's confused before Authority even looks at it.
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "agent_clarification", None)
#         memory.update(user_input, response_text, agent_name=session.active_agent)
#         return response_text

#     # 6. GOVERNANCE: Authority & Validation
#     # ✅ SYSTEMIC FIX: Resolve Policy and Context Scope immediately before evaluation
#     # to ensure Inquiry Suppressor and Intent signals are fresh.
#     policy = decide_context_scope(session)
#     session.context_scope = policy["context_scope"]
#     session.authority_hint = policy["system_hint"]
#     # Resolve the specific item if a SKU exists to provide context to the Authority
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
    
#     # Pass full menu to Authority for Step 11 Ambiguity detection
#     result = evaluate_action(action, session, menu_item, kitchen, all_menu_items, memory)

#     # Apply hint from the pre-authorized policy to the final result
#     result.system_hint = session.authority_hint

#     # 7. ⚖️ Handle RECOVERABLE Violations (Self-Healing)
#     # If Authority detects ambiguity (e.g. "add pizza") or low confidence.
#     if not result.approved and result.requires_clarification:
#         # ✅ SYSTEMIC FIX: Jurisdiction Correction
#         # If OrderTaker incorrectly handles an Inquiry, Authority reassigns the agent.
#         if result.violation_type == ViolationType.INVALID_STATE:
#             session.active_agent = "MenuExpert"

#         # Transform the failed action into a clarification request
#         recovery_action = ActionRequest(
#             action_type=ActionType.ASK_CLARIFICATION,
#             clarification_payload=result.user_message or "Could you please clarify?",
#             confidence=1.0,
#             meta={"violation": result.violation_type, "original_action": action.action_type}
#         )
        
#         response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "recovery_triggered", result.violation_type)
#         memory.update(user_input, response_text, agent_name=session.active_agent)
#         return response_text

#     # 8. 🛑 Handle FATAL Violations (Hard Rejection)
#     if not result.approved:
#         log_execution(session.session_id, action, "rejected", result.rejection_code)
#         final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#         memory.update(user_input, final_response, agent_name=session.active_agent)
#         return final_response

#     # 9. ✅ Apply Approved Actions
#     # Only consume budget for mutations (ADD/REMOVE/MODIFY/CHECKOUT)
#     consume_tool_budget(session)
#     apply_approved_action(session, action)

#     log_execution(session.session_id, action, "approved", None)

#     # 10. FINAL SUCCESS RESPONSE & MEMORY
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)

#     return final_response










# # DineFlow/orchestration/golden_loop.py
# from agents.router import IntentRouter
# from agents.order_taker import OrderTakerAgent
# from agents.greeter import GreeterAgent
# from agents.menu_expert import MenuExpertAgent
# from tools.registry import get_menu_items
# from tools.search.bm25 import MenuBM25
# from tools.search.vector import sync_menu_to_vector
# from validation.schemas import ActionType, ActionRequest
# from log_system.intent_logger import log_intent
# from log_system.execution_logger import log_execution
# from response.generator import generate_response
# from state_machine.authority import evaluate_action, decide_context_scope
# from orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from state_machine.types import SessionState, KitchenSnapshot
# from orchestration.memory_manager import MemoryManager
# from validation.errors import ViolationType, Severity

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1️⃣ ROUTING
#     routing_action = router.route(user_input, session.active_agent)
#     if routing_action.intent:
#         session.active_intent = routing_action.intent
#     session.active_intent = routing_action.intent  # ensure always up-to-date

#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"

#     # 2️⃣ AGENT EXECUTION
#     agent = AGENT_REGISTRY[session.active_agent]
#     action = agent.run(user_input, session, memory)

#     # 3️⃣ LOG INTENT
#     log_intent(session.session_id, user_input, action)

#     # 4️⃣ SHORT-CIRCUIT: NO_OP
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
#         log_execution(session.session_id, action, "noop", None)
#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 5️⃣ SHORT-CIRCUIT: Agent Clarification
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "agent_clarification", None)
#         memory.update(user_input, response_text, agent_name=session.active_agent, status="agent_clarification", action_type=action.action_type)
#         return response_text

#     # 6️⃣ GOVERNANCE: Authority & Context Scope
#     policy = decide_context_scope(session)
#     session.context_scope = policy["context_scope"]
#     session.authority_hint = policy["system_hint"]
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen, all_menu_items, memory)
#     result.system_hint = session.authority_hint

#     # 7️⃣ ⚖️ HANDLE RECOVERABLE VIOLATIONS & AUTO-HANDOFF
#     if not result.approved:
#         # 🔴 FATAL PATH (Hard Stop: Budget or Confirmed Order)
#         # Prevents infinite loops by killing the execution if Authority flags a Fatal state.
#         if result.severity == Severity.FATAL:
#             final_resp = result.user_message or "System Error."
#             memory.update(user_input, final_resp, agent_name=session.active_agent)
#             return final_resp

#         # 🟢 7a️⃣ Jurisdiction mismatch → SILENT AUTO-HANDOFF (Recursion)
#         # If the wrong agent was talking, we swap and RE-RUN the loop immediately.
#         if result.violation_type == ViolationType.INVALID_STATE and result.severity == Severity.RECOVERABLE:
#             target_agent = result.meta.get("target_agent") if result.meta else None
#             if target_agent:
#                 session.active_agent = target_agent
#                 # 🚀 Instant retry with the correct agent
#                 return golden_loop(
#                     session=session, 
#                     user_input=user_input, 
#                     kitchen=kitchen, 
#                     memory=memory
#                 )

#         # 🟡 7b️⃣ Deferred capabilities → Attach to meta for orchestrator/UI
#         # Used for things like Age Verification where an external system/UI must trigger.
#         if result.severity == Severity.DEFERRED:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "This action requires verification.",
#                 confidence=1.0,
#                 meta=result.meta or {}
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "deferred_triggered", result.violation_type)
#             memory.update(user_input, response_text, agent_name=session.active_agent)
#             return response_text

#         # 🔵 7c️⃣ General recoverable clarification
#         # Used for SKU ambiguity, missing quantities, etc.
#         if result.requires_clarification:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "Could you please clarify?",
#                 confidence=1.0,
#                 meta={
#                     "violation": result.violation_type,
#                     "original_action": action.action_type
#                 }
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "recovery_triggered", result.violation_type)
#             memory.update(user_input, response_text, agent_name=session.active_agent, status="authority_clarification", action_type=action.action_type)
#             return response_text
    
#     # 8️⃣ HANDLE UNCATEGORIZED VIOLATIONS (DEFENSIVE GUARD)
#     if not result.approved:
#         # If we reached here, a rejection happened but wasn't caught by the logic in Step 7.
#         # This is a safety net to prevent unapproved actions from reaching Step 9.
#         log_execution(session.session_id, action, "rejected_uncategorized", result.rejection_code)
        
#         # We ensure the system_hint reflects that this was a fallback path
#         result.system_hint = f"FALLBACK_REJECTION: {result.system_hint or 'No hint provided'}"
        
#         final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#         memory.update(user_input, final_response, agent_name=session.active_agent)
#         return final_response

#     # 9️⃣ APPLY APPROVED ACTIONS
#     consume_tool_budget(session)
#     apply_approved_action(session, action)
#     log_execution(session.session_id, action, "approved", None)

#     # 🔟 FINAL RESPONSE & MEMORY UPDATE
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)
#     return final_response






# claud recent version testing.......

# DineFlow/orchestration/golden_loop.py
# from agents.router import IntentRouter
# from agents.order_taker import OrderTakerAgent
# from agents.greeter import GreeterAgent
# from agents.menu_expert import MenuExpertAgent
# from tools.registry import get_menu_items
# from tools.search.bm25 import MenuBM25
# from tools.search.vector import sync_menu_to_vector
# from validation.schemas import ActionType, ActionRequest
# from log_system.intent_logger import log_intent
# from log_system.execution_logger import log_execution
# from response.generator import generate_response
# from state_machine.authority import evaluate_action, decide_context_scope
# from orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from state_machine.types import SessionState, KitchenSnapshot
# from orchestration.memory_manager import MemoryManager
# from validation.errors import ViolationType, Severity

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1️⃣ ROUTING
#     routing_action = router.route(user_input, session.active_agent)
#     if routing_action.intent:
#         session.active_intent = routing_action.intent
#     session.active_intent = routing_action.intent  # ensure always up-to-date

#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"

#     # 2️⃣ GOVERNANCE: Context Scope Decision (MOVED BEFORE AGENT EXECUTION)
#     #
#     # ⚠️  CRITICAL FIX — Two problems existed in the original:
#     #
#     #   Problem A (Wrong Order): decide_context_scope was called at Step 6, AFTER the agent
#     #   already ran at Step 2. The MenuExpert executed with a stale/default context_scope,
#     #   meaning it searched with FILTERED_SEARCH when it needed FULL_CATALOG. By the time
#     #   the scope was corrected, the agent had already produced its (wrong) response.
#     #
#     #   Problem B (Missing Argument): decide_context_scope(session) was called without
#     #   user_input, so the QueryClassifier inside it never saw the query. It could not
#     #   classify "anything spicy?" as ATTRIBUTE_BOUND and could never elevate the scope.
#     #   Passing user_input here fixes that.
#     #
#     # Fix: Move governance BEFORE agent execution and pass user_input so the
#     # QueryClassifier can structurally classify the query and set the correct scope
#     # on the session object BEFORE the agent reads session.context_scope.
#     policy = decide_context_scope(session, user_input)   # <-- user_input now passed
#     session.context_scope = policy["context_scope"]
#     session.authority_hint = policy["system_hint"]

#     # 3️⃣ AGENT EXECUTION
#     # The agent now reads session.context_scope which is already correctly set above.
#     # MenuExpert will receive FULL_CATALOG for "anything spicy?" and FILTERED_SEARCH
#     # for "tell me about the Pepperoni Pizza" — no changes needed inside the agent.
#     agent = AGENT_REGISTRY[session.active_agent]
#     action = agent.run(user_input, session, memory)

#     # 4️⃣ LOG INTENT
#     log_intent(session.session_id, user_input, action)

#     # 5️⃣ SHORT-CIRCUIT: NO_OP
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
#         log_execution(session.session_id, action, "noop", None)
#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 6️⃣ SHORT-CIRCUIT: Agent Clarification
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "agent_clarification", None)
#         memory.update(user_input, response_text, agent_name=session.active_agent, status="agent_clarification", action_type=action.action_type)
#         return response_text

#     # 7️⃣ AUTHORITY EVALUATION
#     # scope and hint are already on session from Step 2.
#     # evaluate_action handles budget, kitchen load, alcohol rules, jurisdiction, etc.
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen, all_menu_items, memory)
#     result.system_hint = session.authority_hint

#     # 8️⃣ ⚖️ HANDLE RECOVERABLE VIOLATIONS & AUTO-HANDOFF
#     if not result.approved:
#         # 🔴 FATAL PATH (Hard Stop: Budget or Confirmed Order)
#         # Prevents infinite loops by killing the execution if Authority flags a Fatal state.
#         if result.severity == Severity.FATAL:
#             final_resp = result.user_message or "System Error."
#             memory.update(user_input, final_resp, agent_name=session.active_agent)
#             return final_resp

#         # 🟢 8a️⃣ Jurisdiction mismatch → SILENT AUTO-HANDOFF (Recursion)
#         # If the wrong agent was talking, we swap and RE-RUN the loop immediately.
#         # Note: scope is re-evaluated at the top of the recursive call, so no
#         # stale state is carried into the retry.
#         if result.violation_type == ViolationType.INVALID_STATE and result.severity == Severity.RECOVERABLE:
#             target_agent = result.meta.get("target_agent") if result.meta else None
#             if target_agent:
#                 session.active_agent = target_agent
#                 # 🚀 Instant retry with the correct agent
#                 return golden_loop(
#                     session=session,
#                     user_input=user_input,
#                     kitchen=kitchen,
#                     memory=memory
#                 )

#         # 🟡 8b️⃣ Deferred capabilities → Attach to meta for orchestrator/UI
#         # Used for things like Age Verification where an external system/UI must trigger.
#         if result.severity == Severity.DEFERRED:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "This action requires verification.",
#                 confidence=1.0,
#                 meta=result.meta or {}
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "deferred_triggered", result.violation_type)
#             memory.update(user_input, response_text, agent_name=session.active_agent)
#             return response_text

#         # 🔵 8c️⃣ General recoverable clarification
#         # Used for SKU ambiguity, missing quantities, etc.
#         if result.requires_clarification:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "Could you please clarify?",
#                 confidence=1.0,
#                 meta={
#                     "violation": result.violation_type,
#                     "original_action": action.action_type
#                 }
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "recovery_triggered", result.violation_type)
#             memory.update(user_input, response_text, agent_name=session.active_agent, status="authority_clarification", action_type=action.action_type)
#             return response_text

#     # 9️⃣ HANDLE UNCATEGORIZED VIOLATIONS (DEFENSIVE GUARD)
#     if not result.approved:
#         # If we reached here, a rejection happened but wasn't caught by the logic in Step 8.
#         # This is a safety net to prevent unapproved actions from reaching Step 10.
#         log_execution(session.session_id, action, "rejected_uncategorized", result.rejection_code)

#         # We ensure the system_hint reflects that this was a fallback path
#         result.system_hint = f"FALLBACK_REJECTION: {result.system_hint or 'No hint provided'}"

#         final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#         memory.update(user_input, final_response, agent_name=session.active_agent)
#         return final_response

#     # 🔟 APPLY APPROVED ACTIONS
#     consume_tool_budget(session)
#     apply_approved_action(session, action)
#     log_execution(session.session_id, action, "approved", None)

#     # 1️⃣1️⃣ FINAL RESPONSE & MEMORY UPDATE
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)
#     return final_response


# # DineFlow/orchestration/golden_loop.py
# from agents.router import IntentRouter
# from agents.order_taker import OrderTakerAgent
# from agents.greeter import GreeterAgent
# from agents.menu_expert import MenuExpertAgent
# from tools.registry import get_menu_items
# from tools.search.bm25 import MenuBM25
# from tools.search.vector import sync_menu_to_vector
# from validation.schemas import ActionType, ActionRequest
# from log_system.intent_logger import log_intent
# from log_system.execution_logger import log_execution
# from response.generator import generate_response
# from state_machine.authority import evaluate_action, decide_context_scope
# from orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from state_machine.types import SessionState, KitchenSnapshot
# from orchestration.memory_manager import MemoryManager
# from validation.errors import ViolationType, Severity

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1️⃣ ROUTING
#     routing_action = router.route(user_input, session.active_agent)
#     if routing_action.intent:
#         session.active_intent = routing_action.intent
#     session.active_intent = routing_action.intent  # ensure always up-to-date

#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"

#     # 2️⃣ GOVERNANCE: Context Scope Decision (BEFORE AGENT EXECUTION)
#     policy = decide_context_scope(session, user_input, all_menu_items)
#     session.context_scope = policy["context_scope"]
#     session.authority_hint = policy["system_hint"]

#     # 3️⃣ AGENT EXECUTION
#     agent = AGENT_REGISTRY[session.active_agent]
#     action = agent.run(user_input, session, memory)

#     # 4️⃣ LOG INTENT
#     log_intent(session.session_id, user_input, action)

#     # 5️⃣ SHORT-CIRCUIT: NO_OP
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
#         log_execution(session.session_id, action, "noop", None)
#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 6️⃣ SHORT-CIRCUIT: Agent Clarification
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "agent_clarification", None)
#         memory.update(
#             user_input, response_text,
#             agent_name=session.active_agent,
#             status="agent_clarification",
#             action_type=action.action_type,
#             # Store the pending SKU if the agent already resolved one.
#             # This allows the clarification hint to name the item explicitly
#             # rather than asking the LLM to infer it from the question text.
#             pending_sku=action.sku,
#         )
#         return response_text

#     # 7️⃣ AUTHORITY EVALUATION
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen, all_menu_items, memory)
#     result.system_hint = session.authority_hint

#     # 8️⃣ ⚖️ HANDLE RECOVERABLE VIOLATIONS & AUTO-HANDOFF
#     if not result.approved:
#         # 🔴 FATAL PATH
#         if result.severity == Severity.FATAL:
#             final_resp = result.user_message or "System Error."
#             memory.update(user_input, final_resp, agent_name=session.active_agent)
#             return final_resp

#         # 🟢 8a️⃣ Jurisdiction mismatch → SILENT AUTO-HANDOFF (Recursion)
#         if result.violation_type == ViolationType.INVALID_STATE and result.severity == Severity.RECOVERABLE:
#             target_agent = result.meta.get("target_agent") if result.meta else None
#             if target_agent:
#                 session.active_agent = target_agent
#                 return golden_loop(
#                     session=session,
#                     user_input=user_input,
#                     kitchen=kitchen,
#                     memory=memory
#                 )

#         # 🟡 8b️⃣ Deferred capabilities
#         if result.severity == Severity.DEFERRED:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "This action requires verification.",
#                 confidence=1.0,
#                 meta=result.meta or {}
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "deferred_triggered", result.violation_type)
#             memory.update(user_input, response_text, agent_name=session.active_agent)
#             return response_text

#         # 🔵 8c️⃣ General recoverable clarification (LOW_CONFIDENCE, ambiguous SKU, etc.)
#         if result.requires_clarification:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "Could you please clarify?",
#                 confidence=1.0,
#                 meta={
#                     "violation": result.violation_type,
#                     "original_action": action.action_type
#                 }
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "recovery_triggered", result.violation_type)
#             memory.update(
#                 user_input, response_text,
#                 agent_name=session.active_agent,
#                 status="authority_clarification",
#                 action_type=action.action_type,
#                 # ✅ KEY FIX: Store the SKU the agent resolved so the clarification
#                 # hint can name the item explicitly on the next turn.
#                 # Without this, the hint says "produce the action implied by the
#                 # question" and the LLM must infer the SKU from natural language —
#                 # which fails for vague confirmations like "add this" or "yes".
#                 pending_sku=action.sku,
#             )
#             return response_text

#     # 9️⃣ HANDLE UNCATEGORIZED VIOLATIONS (DEFENSIVE GUARD)
#     if not result.approved:
#         log_execution(session.session_id, action, "rejected_uncategorized", result.rejection_code)
#         result.system_hint = f"FALLBACK_REJECTION: {result.system_hint or 'No hint provided'}"
#         final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#         memory.update(user_input, final_response, agent_name=session.active_agent)
#         return final_response

#     # 🔟 APPLY APPROVED ACTIONS
#     consume_tool_budget(session)
#     apply_approved_action(session, action)
#     log_execution(session.session_id, action, "approved", None)

#     # 1️⃣1️⃣ FINAL RESPONSE & MEMORY UPDATE
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)
#     return final_response



# # DineFlow/orchestration/golden_loop.py
# from agents.router import IntentRouter
# from agents.order_taker import OrderTakerAgent
# from agents.greeter import GreeterAgent
# from agents.menu_expert import MenuExpertAgent
# from tools.registry import get_menu_items
# from tools.search.bm25 import MenuBM25
# from tools.search.vector import sync_menu_to_vector
# from validation.schemas import ActionType, ActionRequest
# from log_system.intent_logger import log_intent
# from log_system.execution_logger import log_execution
# from response.generator import generate_response
# from state_machine.authority import evaluate_action, decide_context_scope
# from orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from state_machine.types import SessionState, KitchenSnapshot
# from orchestration.memory_manager import MemoryManager
# from validation.errors import ViolationType, Severity

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 1️⃣ ROUTING
#     routing_action = router.route(user_input, session.active_agent)
#     if routing_action.intent:
#         session.active_intent = routing_action.intent
#     session.active_intent = routing_action.intent  # ensure always up-to-date

#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"

#     # 2️⃣ GOVERNANCE: Context Scope Decision (BEFORE AGENT EXECUTION)
#     policy = decide_context_scope(session, user_input, all_menu_items)
#     session.context_scope = policy["context_scope"]
#     session.authority_hint = policy["system_hint"]

#     # 3️⃣ AGENT EXECUTION
#     agent = AGENT_REGISTRY[session.active_agent]
#     action = agent.run(user_input, session, memory)

#     # 4️⃣ LOG INTENT
#     log_intent(session.session_id, user_input, action)

#     # 5️⃣ SHORT-CIRCUIT: NO_OP
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
#         log_execution(session.session_id, action, "noop", None)

#         # PENDING CLARIFICATION GUARD
#         # Do NOT overwrite the window record if the previous turn was a pending
#         # clarification (authority_clarification or agent_clarification).
#         #
#         # Without this guard:
#         #   Turn N:   authority asks "Would you like to add Fancy Truffle Pizza?"
#         #             → window[-1] = {status: "authority_clarification", pending_sku: "PZ-FANCY"}
#         #   Turn N+1: user types "add pleaes" (typo) → LLM produces NO_OP
#         #             → memory.update() appends a noop record (no status field)
#         #             → window[-1] is now the noop record
#         #   Turn N+2: user types "add this pizza"
#         #             → pending_clarification() checks window[-1] → no status → returns None
#         #             → hint never built → LLM asks for clarification again
#         #
#         # With this guard:
#         #   Turn N+1 NO_OP does NOT update the window → window[-1] stays as
#         #   the authority_clarification record → Turn N+2 finds it correctly.
#         if not memory.pending_clarification():
#             memory.update(user_input, response, agent_name=session.active_agent)

#         return response

#     # 6️⃣ SHORT-CIRCUIT: Agent Clarification
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "agent_clarification", None)
#         memory.update(
#             user_input, response_text,
#             agent_name=session.active_agent,
#             status="agent_clarification",
#             action_type=action.action_type,
#             pending_sku=action.sku,
#         )
#         return response_text

#     # 7️⃣ AUTHORITY EVALUATION
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen, all_menu_items, memory)
#     result.system_hint = session.authority_hint

#     # 8️⃣ ⚖️ HANDLE RECOVERABLE VIOLATIONS & AUTO-HANDOFF
#     if not result.approved:
#         # 🔴 FATAL PATH
#         if result.severity == Severity.FATAL:
#             final_resp = result.user_message or "System Error."
#             memory.update(user_input, final_resp, agent_name=session.active_agent)
#             return final_resp

#         # 🟢 8a️⃣ Jurisdiction mismatch → SILENT AUTO-HANDOFF (Recursion)
#         if result.violation_type == ViolationType.INVALID_STATE and result.severity == Severity.RECOVERABLE:
#             target_agent = result.meta.get("target_agent") if result.meta else None
#             if target_agent:
#                 session.active_agent = target_agent
#                 return golden_loop(
#                     session=session,
#                     user_input=user_input,
#                     kitchen=kitchen,
#                     memory=memory
#                 )

#         # 🟡 8b️⃣ Deferred capabilities
#         if result.severity == Severity.DEFERRED:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "This action requires verification.",
#                 confidence=1.0,
#                 meta=result.meta or {}
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "deferred_triggered", result.violation_type)
#             memory.update(user_input, response_text, agent_name=session.active_agent)
#             return response_text

#         # 🔵 8c️⃣ General recoverable clarification (LOW_CONFIDENCE, ambiguous SKU, etc.)
#         if result.requires_clarification:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "Could you please clarify?",
#                 confidence=1.0,
#                 meta={
#                     "violation": result.violation_type,
#                     "original_action": action.action_type
#                 }
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "recovery_triggered", result.violation_type)
#             memory.update(
#                 user_input, response_text,
#                 agent_name=session.active_agent,
#                 status="authority_clarification",
#                 action_type=action.action_type,
#                 pending_sku=action.sku,
#             )
#             return response_text

#     # 9️⃣ HANDLE UNCATEGORIZED VIOLATIONS (DEFENSIVE GUARD)
#     if not result.approved:
#         log_execution(session.session_id, action, "rejected_uncategorized", result.rejection_code)
#         result.system_hint = f"FALLBACK_REJECTION: {result.system_hint or 'No hint provided'}"
#         final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#         memory.update(user_input, final_response, agent_name=session.active_agent)
#         return final_response

#     # 🔟 APPLY APPROVED ACTIONS
#     consume_tool_budget(session, action, result)
#     apply_approved_action(session, action)
#     log_execution(session.session_id, action, "approved", None)

#     # 1️⃣1️⃣ FINAL RESPONSE & MEMORY UPDATE
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)
#     return final_response


# # DineFlow/orchestration/golden_loop.py
# from agents.router import IntentRouter
# from agents.order_taker import OrderTakerAgent
# from agents.greeter import GreeterAgent
# from agents.menu_expert import MenuExpertAgent
# from tools.registry import get_menu_items
# from tools.search.bm25 import MenuBM25
# from tools.search.vector import sync_menu_to_vector
# from validation.schemas import ActionType, ActionRequest
# from log_system.intent_logger import log_intent
# from log_system.execution_logger import log_execution
# from response.generator import generate_response
# from state_machine.authority import evaluate_action, decide_context_scope
# from orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from state_machine.types import SessionState, KitchenSnapshot
# from orchestration.memory_manager import MemoryManager
# from validation.errors import ViolationType, Severity

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# _AGE_CONFIRMATION_PHRASES = {
#     "yes", "i am", "i'm over 18", "over 18", "i'm 18", "i am 18",
#     "yes i am", "confirmed", "i'm of age", "of age",
#     "18+", "adult", "yes i'm over 18", "i am over 18"
# }


# def _is_age_confirmation(text: str) -> bool:
#     normalized = text.lower().strip()
#     if normalized in _AGE_CONFIRMATION_PHRASES:
#         return True
#     age_keywords = {"over 18", "18 years", "i'm 18", "i am 18", "old enough", "of age"}
#     return any(kw in normalized for kw in age_keywords)


# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):
#     # 0️⃣ PRE-ROUTING: DEFERRED CAPABILITY RESOLUTION
#     # Intercept age confirmation before routing so the router never
#     # misclassifies "I'm over 18" as a greeting and loses the pending order.
#     if session.pending_deferred_sku and _is_age_confirmation(user_input):
#         session.age_verified = True
#         retry_sku = session.pending_deferred_sku
#         session.pending_deferred_sku = None

#         synthetic_action = ActionRequest(
#             action_type=ActionType.ADD_TO_CART,
#             sku=retry_sku,
#             quantity=1,
#             confidence=1.0,
#             meta={"deferred_retry": True}
#         )
#         menu_item = resolve_menu_item(all_menu_items, retry_sku)
#         result = evaluate_action(synthetic_action, session, menu_item, kitchen, all_menu_items, memory)
#         response = generate_response(action=synthetic_action, result=result, menu_items=all_menu_items)

#         if result.approved:
#             consume_tool_budget(session, synthetic_action, result)
#             apply_approved_action(session, synthetic_action)
#             log_execution(session.session_id, synthetic_action, "approved", None)

#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # 1️⃣ ROUTING
#     routing_action = router.route(user_input, session.active_agent)
#     if routing_action.intent:
#         session.active_intent = routing_action.intent
#     session.active_intent = routing_action.intent  # ensure always up-to-date

#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"

#     # 2️⃣ GOVERNANCE: Context Scope Decision (BEFORE AGENT EXECUTION)
#     policy = decide_context_scope(session, user_input, all_menu_items)
#     session.context_scope = policy["context_scope"]
#     session.authority_hint = policy["system_hint"]

#     # 3️⃣ AGENT EXECUTION
#     agent = AGENT_REGISTRY[session.active_agent]
#     action = agent.run(user_input, session, memory)

#     # 4️⃣ LOG INTENT
#     log_intent(session.session_id, user_input, action)

#     # 5️⃣ SHORT-CIRCUIT: NO_OP
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
#         log_execution(session.session_id, action, "noop", None)

#         # PENDING CLARIFICATION GUARD
#         # Do NOT overwrite the window record if the previous turn was a pending
#         # clarification (authority_clarification or agent_clarification).
#         #
#         # Without this guard:
#         #   Turn N:   authority asks "Would you like to add Fancy Truffle Pizza?"
#         #             → window[-1] = {status: "authority_clarification", pending_sku: "PZ-FANCY"}
#         #   Turn N+1: user types "add pleaes" (typo) → LLM produces NO_OP
#         #             → memory.update() appends a noop record (no status field)
#         #             → window[-1] is now the noop record
#         #   Turn N+2: user types "add this pizza"
#         #             → pending_clarification() checks window[-1] → no status → returns None
#         #             → hint never built → LLM asks for clarification again
#         #
#         # With this guard:
#         #   Turn N+1 NO_OP does NOT update the window → window[-1] stays as
#         #   the authority_clarification record → Turn N+2 finds it correctly.
#         if not memory.pending_clarification():
#             memory.update(user_input, response, agent_name=session.active_agent)

#         return response

#     # 6️⃣ SHORT-CIRCUIT: Agent Clarification
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "agent_clarification", None)
#         memory.update(
#             user_input, response_text,
#             agent_name=session.active_agent,
#             status="agent_clarification",
#             action_type=action.action_type,
#             pending_sku=action.sku,
#         )
#         return response_text

#     # 7️⃣ AUTHORITY EVALUATION
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen, all_menu_items, memory)
#     result.system_hint = session.authority_hint

#     # 8️⃣ ⚖️ HANDLE RECOVERABLE VIOLATIONS & AUTO-HANDOFF
#     if not result.approved:
#         # 🔴 FATAL PATH
#         if result.severity == Severity.FATAL:
#             final_resp = result.user_message or "System Error."
#             memory.update(user_input, final_resp, agent_name=session.active_agent)
#             return final_resp

#         # 🟢 8a️⃣ Jurisdiction mismatch → SILENT AUTO-HANDOFF (Recursion)
#         if result.violation_type == ViolationType.INVALID_STATE and result.severity == Severity.RECOVERABLE:
#             target_agent = result.meta.get("target_agent") if result.meta else None
#             if target_agent:
#                 session.active_agent = target_agent
#                 return golden_loop(
#                     session=session,
#                     user_input=user_input,
#                     kitchen=kitchen,
#                     memory=memory
#                 )

#         # 🟡 8b️⃣ Deferred capabilities
#         if result.severity == Severity.DEFERRED:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "This action requires verification.",
#                 confidence=1.0,
#                 meta=result.meta or {}
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "deferred_triggered", result.violation_type)

#             # Store the pending SKU on the session so the next turn can
#             # retry the action after the capability is resolved.
#             # Without this, "I'm over 18" arrives with no context about
#             # which item was waiting for verification.
#             session.pending_deferred_sku = action.sku

#             memory.update(
#                 user_input, response_text,
#                 agent_name=session.active_agent,
#                 status="authority_clarification",
#                 pending_sku=action.sku,
#             )
#             return response_text

#         # 🔵 8c️⃣ General recoverable clarification (LOW_CONFIDENCE, ambiguous SKU, etc.)
#         if result.requires_clarification:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "Could you please clarify?",
#                 confidence=1.0,
#                 meta={
#                     "violation": result.violation_type,
#                     "original_action": action.action_type
#                 }
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "recovery_triggered", result.violation_type)
#             memory.update(
#                 user_input, response_text,
#                 agent_name=session.active_agent,
#                 status="authority_clarification",
#                 action_type=action.action_type,
#                 pending_sku=action.sku,
#             )
#             return response_text

#     # 9️⃣ HANDLE UNCATEGORIZED VIOLATIONS (DEFENSIVE GUARD)
#     if not result.approved:
#         log_execution(session.session_id, action, "rejected_uncategorized", result.rejection_code)
#         result.system_hint = f"FALLBACK_REJECTION: {result.system_hint or 'No hint provided'}"
#         final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#         memory.update(user_input, final_response, agent_name=session.active_agent)
#         return final_response

#     # 🔟 APPLY APPROVED ACTIONS
#     consume_tool_budget(session, action, result)
#     apply_approved_action(session, action)
#     log_execution(session.session_id, action, "approved", None)

#     # 1️⃣1️⃣ FINAL RESPONSE & MEMORY UPDATE
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)
#     return final_response





# # DineFlow/orchestration/golden_loop.py
# from agents.router import IntentRouter
# from agents.order_taker import OrderTakerAgent
# from agents.greeter import GreeterAgent
# from agents.menu_expert import MenuExpertAgent
# from tools.registry import get_menu_items
# from tools.search.bm25 import MenuBM25
# from tools.search.vector import sync_menu_to_vector
# from validation.schemas import ActionType, ActionRequest
# from log_system.intent_logger import log_intent
# from log_system.execution_logger import log_execution
# from response.generator import generate_response
# from state_machine.authority import evaluate_action, decide_context_scope
# from orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
# from state_machine.types import SessionState, KitchenSnapshot, ContextItem
# from orchestration.memory_manager import MemoryManager
# from orchestration.semantic_resolver import resolve, ReferenceIntent
# from validation.errors import ViolationType, Severity

# # --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
# all_menu_items = get_menu_items()
# sync_menu_to_vector(all_menu_items)
# bm25_engine = MenuBM25(all_menu_items)

# # Instantiate agents once
# router = IntentRouter()
# AGENT_REGISTRY = {
#     "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
#     "Greeter": GreeterAgent(),
#     "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
# }

# _AGE_CONFIRMATION_PHRASES = {
#     "yes", "i am", "i'm over 18", "over 18", "i'm 18", "i am 18",
#     "yes i am", "confirmed", "i'm of age", "of age",
#     "18+", "adult", "yes i'm over 18", "i am over 18"
# }


# def _is_age_confirmation(text: str) -> bool:
#     normalized = text.lower().strip()
#     if normalized in _AGE_CONFIRMATION_PHRASES:
#         return True
#     age_keywords = {"over 18", "18 years", "i'm 18", "i am 18", "old enough", "of age"}
#     return any(kw in normalized for kw in age_keywords)


# def _populate_context_from_response(response_text: str, session: SessionState) -> None:
#     """
#     Extracts menu item names from a system response and marks them as
#     mentioned=True in session.active_context.

#     CRITICAL PRINCIPLE: Context is built from SYSTEM OUTPUTS, not user input.
#     This function must only be called with text that the system produced
#     (clarification messages, MenuExpert responses) — never with user input.

#     Matching strategy: BM25 scoring against item names.

#     Why BM25 instead of token overlap:
#         Token overlap (e.g. "50% of tokens must match") breaks on menus with
#         similar item names. Example: "Spicy Chicken Burger" and "Chicken Burger"
#         both share 2/2 and 2/3 tokens with "Chicken Burger" respectively — the
#         overlap threshold cannot distinguish them reliably.

#         BM25's IDF component solves this: tokens that appear in many items
#         (like "pizza" or "burger") get low weight, while discriminating tokens
#         that appear in only one item (like "truffle", "margherita", "heineken")
#         get high weight. This makes matching menu-agnostic — it works correctly
#         whether the menu has 5 items or 500, and regardless of naming similarity.

#     Threshold strategy:
#         We use a RELATIVE threshold: only items whose BM25 score is >= 30% of
#         the top-scoring item's score are included. This is more robust than an
#         absolute threshold because BM25 scores vary by corpus size and query
#         length. A short response mentioning one item produces different absolute
#         scores than a long response listing many items — the relative threshold
#         adapts automatically.

#         Minimum score guard: items with score=0 are always excluded, even if
#         all items score 0 (in which case nothing is added to context).
#     """
#     if not response_text.strip():
#         return

#     scored = bm25_engine.score_all(response_text)

#     if not scored:
#         return

#     top_score = scored[0][1]

#     # Nothing matched at all — response contains no menu-relevant tokens
#     if top_score <= 0:
#         return

#     # Relative threshold: include items scoring >= 30% of the top score.
#     # This adapts to corpus size and response length automatically.
#     threshold = top_score * 0.30

#     for item, score in scored:
#         if score < threshold:
#             break  # sorted descending — no point checking further
#         if item.sku in session.active_context:
#             session.active_context[item.sku].mentioned = True
#             session.active_context[item.sku].last_mentioned_turn = session.turn_id
#         else:
#             session.active_context[item.sku] = ContextItem(
#                 sku=item.sku,
#                 name=item.name,
#                 mentioned=True,
#                 last_mentioned_turn=session.turn_id,
#             )


# def _mark_selected(sku: str, session: SessionState, turn_offset: int = 0) -> None:
#     """
#     Marks an item as selected (confirmed/ordered) in active_context.

#     turn_offset: used during bulk adds to preserve insertion order within
#     a single turn. Items added in the same turn get turn_id * 100 + offset
#     so that _last_selected() can correctly resolve which was added last.
#     """
#     effective_turn = session.turn_id * 100 + turn_offset
#     if sku in session.active_context:
#         session.active_context[sku].selected = True
#         session.active_context[sku].last_mentioned_turn = effective_turn
#     else:
#         item = resolve_menu_item(all_menu_items, sku)
#         if item:
#             session.active_context[sku] = ContextItem(
#                 sku=sku,
#                 name=item.name,
#                 mentioned=True,
#                 selected=True,
#                 last_mentioned_turn=effective_turn,
#             )


# def _execute_bulk_add(skus: list, session: SessionState, kitchen: KitchenSnapshot,
#                       memory: MemoryManager, user_input: str) -> str:
#     """
#     Adds multiple items to cart. Used by ADD_ALL and ADD_THAT resolver intents.
#     Returns the user-facing response string.
#     """
#     responses = []
#     added_skus = []

#     for idx, sku in enumerate(skus):
#         add_action = ActionRequest(
#             action_type=ActionType.ADD_TO_CART,
#             sku=sku,
#             quantity=1,
#             confidence=1.0,
#             meta={"bulk_add": True}
#         )
#         menu_item = resolve_menu_item(all_menu_items, sku)
#         result = evaluate_action(add_action, session, menu_item, kitchen, all_menu_items, memory)
#         if result.approved:
#             consume_tool_budget(session, add_action, result)
#             apply_approved_action(session, add_action)
#             log_execution(session.session_id, add_action, "approved", None)
#             # Use session.turn_id * 100 + idx so items added in the same turn
#             # have distinct last_mentioned_turn values preserving insertion order.
#             # "cancel that" after "add all" will then correctly resolve to the
#             # last-added item, not a random one from the same-turn group.
#             _mark_selected(sku, session, turn_offset=idx)
#             item_name = menu_item.name if menu_item else sku
#             responses.append(item_name)
#             added_skus.append(sku)

#     # Clear pending_items after bulk add (legacy fallback cleanup)
#     session.pending_items = []

#     if responses:
#         session.last_action_sku = added_skus[-1]
#         session.last_action_type = ActionType.ADD_TO_CART.value
#         session.last_quantity = 1
#         items_str = ", ".join(responses)
#         return f"Excellent! I've added {items_str} to your order. Anything else?"
#     else:
#         return "I wasn't able to add those items. Please try ordering them individually."


# def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot, memory: MemoryManager):

#     # ── TURN COUNTER ──────────────────────────────────────────────────────────
#     # Incremented first so all context writes in this turn use the correct turn_id.
#     session.turn_id += 1

#     # 0️⃣ PRE-ROUTING: DETERMINISTIC STATE RESOLUTION
#     #
#     # Two interceptors run before routing:
#     #
#     # A) Age confirmation — domain-specific, not a semantic reference.
#     #    Handled separately because it requires session.pending_deferred_sku
#     #    and sets session.age_verified — outside SemanticResolver's scope.
#     #
#     # B) SemanticResolver — resolves reference intents using active_context.
#     #    Handles: "all", "that", "same", "2", "cancel that".
#     #    Returns None for non-references → golden_loop proceeds to router.

#     # ── 0A: AGE CONFIRMATION ──────────────────────────────────────────────────
#     if session.pending_deferred_sku and _is_age_confirmation(user_input):
#         session.age_verified = True
#         retry_sku = session.pending_deferred_sku
#         session.pending_deferred_sku = None

#         synthetic_action = ActionRequest(
#             action_type=ActionType.ADD_TO_CART,
#             sku=retry_sku,
#             quantity=1,
#             confidence=1.0,
#             meta={"deferred_retry": True}
#         )
#         menu_item = resolve_menu_item(all_menu_items, retry_sku)
#         result = evaluate_action(synthetic_action, session, menu_item, kitchen, all_menu_items, memory)
#         response = generate_response(action=synthetic_action, result=result, menu_items=all_menu_items)

#         if result.approved:
#             consume_tool_budget(session, synthetic_action, result)
#             apply_approved_action(session, synthetic_action)
#             log_execution(session.session_id, synthetic_action, "approved", None)
#             session.last_action_sku = retry_sku
#             session.last_quantity = synthetic_action.quantity
#             session.last_action_type = ActionType.ADD_TO_CART.value
#             _mark_selected(retry_sku, session)

#         memory.update(user_input, response, agent_name=session.active_agent)
#         return response

#     # ── 0B: SEMANTIC RESOLVER ─────────────────────────────────────────────────
#     # Resolves reference intents using the Active Context Graph.
#     # active_context is populated from SYSTEM OUTPUTS only (see Point 2 in
#     # the locked design). The resolver is thin: it classifies the reference
#     # type and queries the context — it never executes actions directly.
#     resolved = resolve(user_input, session)

#     if resolved is not None:

#         if resolved.intent == ReferenceIntent.CANCEL:
#             sku = resolved.skus[0] if resolved.skus else None
#             if sku and session.last_action_type == ActionType.ADD_TO_CART.value:
#                 cancel_action = ActionRequest(
#                     action_type=ActionType.REMOVE_FROM_CART,
#                     sku=sku,
#                     quantity=resolved.quantity or 1,
#                     confidence=1.0,
#                     meta={"cancellation": True, "resolver_source": resolved.source}
#                 )
#                 menu_item = resolve_menu_item(all_menu_items, sku)
#                 result = evaluate_action(cancel_action, session, menu_item, kitchen, all_menu_items, memory)
#                 if result.approved:
#                     apply_approved_action(session, cancel_action)
#                     log_execution(session.session_id, cancel_action, "approved", None)
#                     # Clear focus — no item in focus after cancellation
#                     if sku in session.active_context:
#                         session.active_context[sku].selected = False
#                     session.last_action_sku = None
#                     session.last_action_type = None
#                     session.last_quantity = None
#                     item_name = menu_item.name if menu_item else sku
#                     response = f"No problem. I've removed {item_name} from your cart."
#                 else:
#                     response = result.user_message or "I couldn't undo that action."
#                 memory.update(user_input, response, agent_name=session.active_agent)
#                 return response

#         elif resolved.intent in {ReferenceIntent.ADD_ALL, ReferenceIntent.ADD_THAT}:
#             response = _execute_bulk_add(
#                 resolved.skus, session, kitchen, memory, user_input
#             )
#             memory.update(user_input, response, agent_name=session.active_agent)
#             return response

#         elif resolved.intent == ReferenceIntent.REPEAT:
#             sku = resolved.skus[0] if resolved.skus else None
#             if sku:
#                 repeat_action = ActionRequest(
#                     action_type=ActionType.ADD_TO_CART,
#                     sku=sku,
#                     quantity=resolved.quantity or 1,
#                     confidence=1.0,
#                     meta={"repeat": True, "resolver_source": resolved.source}
#                 )
#                 menu_item = resolve_menu_item(all_menu_items, sku)
#                 result = evaluate_action(repeat_action, session, menu_item, kitchen, all_menu_items, memory)
#                 response = generate_response(action=repeat_action, result=result, menu_items=all_menu_items)
#                 if result.approved:
#                     consume_tool_budget(session, repeat_action, result)
#                     apply_approved_action(session, repeat_action)
#                     log_execution(session.session_id, repeat_action, "approved", None)
#                     session.last_action_sku = sku
#                     session.last_quantity = repeat_action.quantity
#                     session.last_action_type = ActionType.ADD_TO_CART.value
#                     _mark_selected(sku, session)
#                 memory.update(user_input, response, agent_name=session.active_agent)
#                 return response

#         elif resolved.intent == ReferenceIntent.QUANTITY:
#             sku = resolved.skus[0] if resolved.skus else None
#             if sku:
#                 qty_action = ActionRequest(
#                     action_type=ActionType.ADD_TO_CART,
#                     sku=sku,
#                     quantity=resolved.quantity or 1,
#                     confidence=1.0,
#                     meta={"quantity_update": True, "resolver_source": resolved.source}
#                 )
#                 menu_item = resolve_menu_item(all_menu_items, sku)
#                 result = evaluate_action(qty_action, session, menu_item, kitchen, all_menu_items, memory)
#                 response = generate_response(action=qty_action, result=result, menu_items=all_menu_items)
#                 if result.approved:
#                     consume_tool_budget(session, qty_action, result)
#                     apply_approved_action(session, qty_action)
#                     log_execution(session.session_id, qty_action, "approved", None)
#                     session.last_action_sku = sku
#                     session.last_quantity = qty_action.quantity
#                     session.last_action_type = ActionType.ADD_TO_CART.value
#                     _mark_selected(sku, session)
#                 memory.update(user_input, response, agent_name=session.active_agent)
#                 return response

#         # Resolved but could not execute (no SKU found) — fall through to router

#     # 1️⃣ ROUTING
#     routing_action = router.route(user_input, session.active_agent)
#     if routing_action.intent:
#         session.active_intent = routing_action.intent
#     session.active_intent = routing_action.intent

#     if routing_action.confidence >= 0.6:
#         target = routing_action.target_agent
#         session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"

#     # 2️⃣ GOVERNANCE: Context Scope Decision (BEFORE AGENT EXECUTION)
#     policy = decide_context_scope(session, user_input, all_menu_items)
#     session.context_scope = policy["context_scope"]
#     session.authority_hint = policy["system_hint"]

#     # 3️⃣ AGENT EXECUTION
#     agent = AGENT_REGISTRY[session.active_agent]
#     action = agent.run(user_input, session, memory)

#     # 4️⃣ LOG INTENT
#     log_intent(session.session_id, user_input, action)

#     # 5️⃣ SHORT-CIRCUIT: NO_OP
#     if action.action_type == ActionType.NO_OP:
#         response = action.message or "I'm here to help! What can I get for you?"
#         log_execution(session.session_id, action, "noop", None)

#         # CONTEXT UPDATE FROM MENUEXPERT RESPONSE
#         # MenuExpert delegates context writes to golden_loop so that only
#         # items actually mentioned in the LLM's reply enter active_context.
#         # Writing from relevant_items (what was searched) would pollute context
#         # with all FULL_CATALOG items even when only one was relevant.
#         # BM25 scoring against the response text gives us precise extraction.
#         if session.active_agent == "MenuExpert" and response:
#             _populate_context_from_response(response, session)

#         # PENDING CLARIFICATION GUARD
#         # Do NOT overwrite the window record if the previous turn was a pending
#         # clarification. This keeps window[-1] as the clarification record so
#         # the next turn's hint fires correctly.
#         if not memory.pending_clarification():
#             memory.update(user_input, response, agent_name=session.active_agent)

#         return response

#     # 6️⃣ SHORT-CIRCUIT: Agent Clarification
#     if action.action_type == ActionType.ASK_CLARIFICATION:
#         response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
#         log_execution(session.session_id, action, "agent_clarification", None)

#         # POPULATE ACTIVE CONTEXT FROM SYSTEM OUTPUT (not user input)
#         # The clarification response_text is what the system said — it may
#         # list specific items ("You mentioned Pepperoni, Truffle, Margherita").
#         # We extract those item names from the response and mark them mentioned.
#         # This is the correct source: context = what system showed, not user typed.
#         _populate_context_from_response(response_text, session)

#         # Legacy fallback: also populate pending_items for backward compatibility
#         # during transition. Remove this block in Phase 2.
#         mentioned_in_context = [
#             sku for sku, item in session.active_context.items()
#             if item.mentioned
#         ]
#         if len(mentioned_in_context) > 1:
#             session.pending_items = mentioned_in_context

#         memory.update(
#             user_input, response_text,
#             agent_name=session.active_agent,
#             status="agent_clarification",
#             action_type=action.action_type,
#             pending_sku=action.sku,
#         )
#         return response_text

#     # 7️⃣ AUTHORITY EVALUATION
#     menu_item = resolve_menu_item(all_menu_items, action.sku)
#     result = evaluate_action(action, session, menu_item, kitchen, all_menu_items, memory)
#     result.system_hint = session.authority_hint

#     # 8️⃣ ⚖️ HANDLE RECOVERABLE VIOLATIONS & AUTO-HANDOFF
#     if not result.approved:
#         # 🔴 FATAL PATH
#         if result.severity == Severity.FATAL:
#             final_resp = result.user_message or "System Error."
#             memory.update(user_input, final_resp, agent_name=session.active_agent)
#             return final_resp

#         # 🟢 8a️⃣ Jurisdiction mismatch → SILENT AUTO-HANDOFF
#         if result.violation_type == ViolationType.INVALID_STATE and result.severity == Severity.RECOVERABLE:
#             target_agent = result.meta.get("target_agent") if result.meta else None
#             if target_agent:
#                 session.active_agent = target_agent
#                 return golden_loop(
#                     session=session,
#                     user_input=user_input,
#                     kitchen=kitchen,
#                     memory=memory
#                 )

#         # 🟡 8b️⃣ Deferred capabilities (age verification etc.)
#         if result.severity == Severity.DEFERRED:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "This action requires verification.",
#                 confidence=1.0,
#                 meta=result.meta or {}
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "deferred_triggered", result.violation_type)
#             session.pending_deferred_sku = action.sku
#             memory.update(
#                 user_input, response_text,
#                 agent_name=session.active_agent,
#                 status="authority_clarification",
#                 pending_sku=action.sku,
#             )
#             return response_text

#         # 🔵 8c️⃣ General recoverable clarification (LOW_CONFIDENCE etc.)
#         if result.requires_clarification:
#             recovery_action = ActionRequest(
#                 action_type=ActionType.ASK_CLARIFICATION,
#                 clarification_payload=result.user_message or "Could you please clarify?",
#                 confidence=1.0,
#                 meta={
#                     "violation": result.violation_type,
#                     "original_action": action.action_type
#                 }
#             )
#             response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
#             log_execution(session.session_id, action, "recovery_triggered", result.violation_type)

#             # Populate context from the recovery response text
#             _populate_context_from_response(response_text, session)

#             memory.update(
#                 user_input, response_text,
#                 agent_name=session.active_agent,
#                 status="authority_clarification",
#                 action_type=action.action_type,
#                 pending_sku=action.sku,
#             )
#             return response_text

#     # 9️⃣ HANDLE UNCATEGORIZED VIOLATIONS (DEFENSIVE GUARD)
#     if not result.approved:
#         log_execution(session.session_id, action, "rejected_uncategorized", result.rejection_code)
#         result.system_hint = f"FALLBACK_REJECTION: {result.system_hint or 'No hint provided'}"
#         final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#         memory.update(user_input, final_response, agent_name=session.active_agent)
#         return final_response

#     # 🔟 APPLY APPROVED ACTIONS
#     consume_tool_budget(session, action, result)
#     apply_approved_action(session, action)
#     log_execution(session.session_id, action, "approved", None)

#     # Update focus, action tracking, and active_context
#     if action.action_type == ActionType.ADD_TO_CART and action.sku:
#         session.last_action_sku = action.sku
#         session.last_quantity = action.quantity
#         session.last_action_type = ActionType.ADD_TO_CART.value
#         _mark_selected(action.sku, session)
#     elif action.action_type == ActionType.REMOVE_FROM_CART and action.sku:
#         session.last_action_type = ActionType.REMOVE_FROM_CART.value
#         if action.sku in session.active_context:
#             session.active_context[action.sku].selected = False

#     # 1️⃣1️⃣ FINAL RESPONSE & MEMORY UPDATE
#     final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
#     memory.update(user_input, final_response, agent_name=session.active_agent)
#     return final_response






# DineFlow/orchestration/golden_loop.py
from agents.router import IntentRouter
from agents.order_taker import OrderTakerAgent
from agents.greeter import GreeterAgent
from agents.menu_expert import MenuExpertAgent
from tools.registry import get_menu_items
from tools.search.bm25 import MenuBM25
from tools.search.vector import sync_menu_to_vector
from validation.schemas import ActionType, ActionRequest
from log_system.intent_logger import log_intent
from log_system.execution_logger import log_execution
from response.generator import generate_response
from state_machine.authority import evaluate_action, decide_context_scope
from orchestration.helpers import consume_tool_budget, resolve_menu_item, apply_approved_action
from state_machine.types import SessionState, KitchenSnapshot, ContextItem
from orchestration.memory_manager import MemoryManager
from orchestration.semantic_resolver import resolve, ReferenceIntent
from validation.errors import ViolationType, Severity

# --- SEARCH & INFRASTRUCTURE BOOTSTRAP ---
all_menu_items = get_menu_items()
sync_menu_to_vector(all_menu_items)
bm25_engine = MenuBM25(all_menu_items)

# Instantiate agents once
router = IntentRouter()
AGENT_REGISTRY = {
    "OrderTaker": OrderTakerAgent(all_menu_items, bm25_engine),
    "Greeter": GreeterAgent(),
    "MenuExpert": MenuExpertAgent(all_menu_items, bm25_engine),
}

_AGE_CONFIRMATION_PHRASES = {
    "yes", "i am", "i'm over 18", "over 18", "i'm 18", "i am 18",
    "yes i am", "confirmed", "i'm of age", "of age",
    "18+", "adult", "yes i'm over 18", "i am over 18"
}


def _is_age_confirmation(text: str) -> bool:
    normalized = text.lower().strip()
    if normalized in _AGE_CONFIRMATION_PHRASES:
        return True
    age_keywords = {"over 18", "18 years", "i'm 18", "i am 18", "old enough", "of age"}
    return any(kw in normalized for kw in age_keywords)

def _llm_detect_age_confirmation(user_input: str) -> bool:
    from llm.client import call_llm
    import json as _json
    prompt = (
        "You are a compliance checker for a restaurant ordering system. "
        "The user was asked to confirm they are 18 or older before receiving alcohol. "
        f"User response: \"{user_input}\" "
        "Is the user confirming they are 18 or older? "
        "Return ONLY valid JSON with no explanation: {\"confirmed\": true} or {\"confirmed\": false}"
    )
    try:
        raw = call_llm(prompt, user_input)
        raw = raw.strip().strip("`").strip()
        data = _json.loads(raw)
        return bool(data.get("confirmed", False))
    except Exception:
        return False


def _populate_context_from_response(response_text: str, session: SessionState) -> None:
    """
    Extracts menu item names from a system response and marks them as
    mentioned=True in session.active_context.

    CRITICAL PRINCIPLE: Context is built from SYSTEM OUTPUTS, not user input.
    This function must only be called with text that the system produced
    (clarification messages, MenuExpert responses) — never with user input.

    Matching strategy: BM25 scoring against item names.

    Why BM25 instead of token overlap:
        Token overlap (e.g. "50% of tokens must match") breaks on menus with
        similar item names. Example: "Spicy Chicken Burger" and "Chicken Burger"
        both share 2/2 and 2/3 tokens with "Chicken Burger" respectively — the
        overlap threshold cannot distinguish them reliably.

        BM25's IDF component solves this: tokens that appear in many items
        (like "pizza" or "burger") get low weight, while discriminating tokens
        that appear in only one item (like "truffle", "margherita", "heineken")
        get high weight. This makes matching menu-agnostic — it works correctly
        whether the menu has 5 items or 500, and regardless of naming similarity.

    Threshold strategy:
        We use a RELATIVE threshold: only items whose BM25 score is >= 30% of
        the top-scoring item's score are included. This is more robust than an
        absolute threshold because BM25 scores vary by corpus size and query
        length. A short response mentioning one item produces different absolute
        scores than a long response listing many items — the relative threshold
        adapts automatically.

        Minimum score guard: items with score=0 are always excluded, even if
        all items score 0 (in which case nothing is added to context).
    """
    if not response_text.strip():
        return

    scored = bm25_engine.score_all(response_text)

    if not scored:
        return

    top_score = scored[0][1]

    # Nothing matched at all — response contains no menu-relevant tokens
    if top_score <= 0:
        return

    # Two-stage matching: BM25 score + name presence confirmation.
    #
    # BM25 alone is insufficient for context population because items sharing
    # common tokens (e.g. all pizzas share "pizza", "mozzarella", "tomato")
    # score above the relative threshold even when only one item was named.
    #
    # Strategy:
    #   Stage 1 — BM25 relative threshold (50%) narrows candidates to items
    #             that are clearly relevant to the response text.
    #   Stage 2 — Name presence check confirms the item's significant tokens
    #             (words > 3 chars) actually appear in the response. This
    #             prevents items that merely share common words from entering
    #             context when they weren't mentioned by name.
    #
    # Example:
    #   Response: "the Pepperoni Pizza is our only spicy option"
    #   PZ-PEP: BM25 high ✓, "pepperoni" in response ✓ → added
    #   PZ-MARG: BM25 medium (shares "pizza"), "margherita" NOT in response ✗ → skipped
    threshold = top_score * 0.50
    MAX_CONTEXT_ITEMS = 5
    items_added = 0
    response_lower = response_text.lower()

    for item, score in scored:
        if score < threshold or items_added >= MAX_CONTEXT_ITEMS:
            break
        # Stage 2: confirm item's significant name tokens appear in response
        significant_tokens = [t for t in item.name.lower().split() if len(t) > 3]
        if significant_tokens and not any(t in response_lower for t in significant_tokens):
            continue
        if item.sku in session.active_context:
            session.active_context[item.sku].mentioned = True
            session.active_context[item.sku].last_mentioned_turn = session.turn_id
        else:
            session.active_context[item.sku] = ContextItem(
                sku=item.sku,
                name=item.name,
                mentioned=True,
                last_mentioned_turn=session.turn_id,
            )
        items_added += 1


def _mark_selected(sku: str, session: SessionState, turn_offset: int = 0) -> None:
    """
    Marks an item as selected (confirmed/ordered) in active_context.

    turn_offset: used during bulk adds to preserve insertion order within
    a single turn. Items added in the same turn get turn_id * 100 + offset
    so that _last_selected() can correctly resolve which was added last.
    """
    effective_turn = session.turn_id * 100 + turn_offset
    if sku in session.active_context:
        session.active_context[sku].selected = True
        session.active_context[sku].last_mentioned_turn = effective_turn
    else:
        item = resolve_menu_item(all_menu_items, sku)
        if item:
            session.active_context[sku] = ContextItem(
                sku=sku,
                name=item.name,
                mentioned=True,
                selected=True,
                last_mentioned_turn=effective_turn,
            )


def _execute_bulk_add(skus: list, session: SessionState, kitchen: KitchenSnapshot,
                      memory: MemoryManager, user_input: str) -> str:
    """
    Adds multiple items to cart. Used by ADD_ALL and ADD_THAT resolver intents.
    Returns the user-facing response string.
    """
    responses = []
    added_skus = []

    for idx, sku in enumerate(skus):
        add_action = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku=sku,
            quantity=1,
            confidence=1.0,
            meta={"bulk_add": True}
        )
        menu_item = resolve_menu_item(all_menu_items, sku)
        result = evaluate_action(add_action, session, menu_item, kitchen, all_menu_items, memory)
        if result.approved:
            consume_tool_budget(session, add_action, result)
            apply_approved_action(session, add_action)
            log_execution(session.session_id, add_action, "approved", None)
            # Use session.turn_id * 100 + idx so items added in the same turn
            # have distinct last_mentioned_turn values preserving insertion order.
            # "cancel that" after "add all" will then correctly resolve to the
            # last-added item, not a random one from the same-turn group.
            _mark_selected(sku, session, turn_offset=idx)
            item_name = menu_item.name if menu_item else sku
            responses.append(item_name)
            added_skus.append(sku)

    # Clear pending_items after bulk add (legacy fallback cleanup)
    session.pending_items = []

    if responses:
        session.last_action_sku = added_skus[-1]
        session.last_action_type = ActionType.ADD_TO_CART.value
        session.last_quantity = 1
        items_str = ", ".join(responses)
        return f"Excellent! I've added {items_str} to your order. Anything else?"
    else:
        return "I wasn't able to add those items. Please try ordering them individually."


# Maximum recursion depth for jurisdiction handoffs.
# Prevents infinite loops when INVALID_STATE keeps firing after handoff.
_MAX_HANDOFF_DEPTH = 3


def golden_loop(*, session: SessionState, user_input: str, kitchen: KitchenSnapshot,
                memory: MemoryManager, _handoff_depth: int = 0):

    # ── TURN COUNTER ──────────────────────────────────────────────────────────
    # Incremented first so all context writes in this turn use the correct turn_id.
    session.turn_id += 1

    # 0️⃣ PRE-ROUTING: DETERMINISTIC STATE RESOLUTION
    #
    # Two interceptors run before routing:
    #
    # A) Age confirmation — domain-specific, not a semantic reference.
    #    Handled separately because it requires session.pending_deferred_sku
    #    and sets session.age_verified — outside SemanticResolver's scope.
    #
    # B) SemanticResolver — resolves reference intents using active_context.
    #    Handles: "all", "that", "same", "2", "cancel that".
    #    Returns None for non-references → golden_loop proceeds to router.

    # ── 0A: AGE CONFIRMATION ──────────────────────────────────────────────────
    # Two-tier check: deterministic phrase set (fast, English) then LLM
    # fallback (multilingual). The LLM tier only runs when:
    #   - pending_deferred_sku is set (something is waiting for age confirmation)
    #   - the phrase set didn't already match (avoid double-spend)
    # Age verification is a legal/compliance check — we keep the phrase set
    # as the primary gate for reliability and use LLM only for languages
    # not covered by the English set.
    _age_confirmed = _is_age_confirmation(user_input)
    if session.pending_deferred_sku and not _age_confirmed:
        _age_confirmed = _llm_detect_age_confirmation(user_input)

    if session.pending_deferred_sku and _age_confirmed:
        session.age_verified = True
        retry_sku = session.pending_deferred_sku
        session.pending_deferred_sku = None

        synthetic_action = ActionRequest(
            action_type=ActionType.ADD_TO_CART,
            sku=retry_sku,
            quantity=1,
            confidence=1.0,
            meta={"deferred_retry": True}
        )
        menu_item = resolve_menu_item(all_menu_items, retry_sku)
        result = evaluate_action(synthetic_action, session, menu_item, kitchen, all_menu_items, memory)
        response = generate_response(action=synthetic_action, result=result, menu_items=all_menu_items)

        if result.approved:
            consume_tool_budget(session, synthetic_action, result)
            apply_approved_action(session, synthetic_action)
            log_execution(session.session_id, synthetic_action, "approved", None)
            session.last_action_sku = retry_sku
            session.last_quantity = synthetic_action.quantity
            session.last_action_type = ActionType.ADD_TO_CART.value
            _mark_selected(retry_sku, session)

        memory.update(user_input, response, agent_name=session.active_agent)
        return response

    # ── 0B: SEMANTIC RESOLVER ─────────────────────────────────────────────────
    # Resolves reference intents using the Active Context Graph.
    # active_context is populated from SYSTEM OUTPUTS only.
    #
    # Gate: only attempt resolution when both conditions hold:
    #
    #   1. RESOLVABLE STATE EXISTS — there is something in session to resolve
    #      against (active_context, last_action_sku, pending_items, or a
    #      deferred item). Without state, references like "all" or "that"
    #      have no anchor — the resolver would return None anyway, so skip
    #      the call entirely. This check is language-agnostic.
    #
    #   2. INPUT IS SHORT — long inputs (> 6 tokens) are almost certainly
    #      normal orders or questions, not references. A user typing
    #      "add 2 pepperoni pizzas and a margherita" is ordering, not
    #      referencing context. Short inputs (≤ 6 tokens) may be references
    #      in any language: "2", "all", "sab", "todo", "همه", "same again".
    #      Token count is language-agnostic — it works the same in Urdu,
    #      Spanish, Arabic, or English.
    #
    # Why no word-list gate:
    #      A word list ("all", "that", "same"...) is English-only and would
    #      miss multilingual references entirely. State + length is sufficient
    #      to filter obvious non-references without language assumptions.
    #
    # The resolver itself handles the rest: if the short input is not a
    # reference (e.g. "no thanks"), _classify returns NOT_RESOLVED and
    # resolve() returns None — golden_loop proceeds to router normally.

    _has_resolvable_state = (
        bool(session.active_context)
        or bool(session.last_action_sku)
        or bool(session.pending_items)
        or bool(session.pending_deferred_sku)
    )
    # Use normalized token count so politeness words ("please", "thanks") don't
    # inflate the count. "all please" = 2 raw tokens but 1 meaningful token.
    # We inline a minimal normalization here rather than importing from
    # semantic_resolver to avoid circular dependency risk.
    _clean_for_gate = ''.join(c if c.isalnum() or c == ' ' else ' ' for c in user_input.lower()).split()
    _is_short_input = len(_clean_for_gate) <= 6

    # EXPLICIT ORDER BYPASS
    # If the input names a specific menu item, it is an explicit order —
    # not a vague reference to context. Skip the resolver and let the
    # router send it to OrderTaker which handles explicit SKU resolution.
    #
    # Without this: "add Pepperoni Pizza" with PZ-PEP in active_context
    # gets confidence=0.3 (weak "add" signal) → LLM called → ADD_THAT
    # returned → item added via resolver instead of OrderTaker. This
    # bypasses the LLM prompt's SKU-matching logic and produces incorrect
    # quantity handling.
    #
    # Detection: all significant tokens (>3 chars) of any item name must
    # appear in the input. Case-insensitive. Ignores short words ("and",
    # "the") to avoid false negatives on partial matches.
    _input_lower = user_input.lower()
    _has_named_item = any(
        all(tok in _input_lower for tok in item.name.lower().split() if len(tok) > 3)
        for item in all_menu_items
        if any(len(tok) > 3 for tok in item.name.lower().split())
    )

    resolved = (
        resolve(user_input, session)
        if (_has_resolvable_state and _is_short_input and not _has_named_item)
        else None
    )

    if resolved is not None:

        # Guard: if resolver returned an intent but no SKUs, it means
        # context existed but no item could be identified — ask for
        # clarification rather than silently falling through to the router
        # which would produce a confusing generic response.
        if not resolved.skus and resolved.intent != ReferenceIntent.NOT_RESOLVED:
            response = "Could you clarify which item you mean?"
            memory.update(user_input, response, agent_name=session.active_agent)
            return response

        if resolved.intent == ReferenceIntent.CANCEL:
            sku = resolved.skus[0] if resolved.skus else None
            # Guard: item must exist in cart — not last_action_type.
            # last_action_type can be None (cleared after previous cancel),
            # or something else entirely (browse, greeting) especially in
            # voice/multi-agent flows. Cart presence is the correct check.
            if sku and (sku in session.cart or session.last_action_type == ActionType.ADD_TO_CART.value):
                cancel_action = ActionRequest(
                    action_type=ActionType.REMOVE_FROM_CART,
                    sku=sku,
                    quantity=resolved.quantity or 1,
                    confidence=1.0,
                    meta={"cancellation": True, "resolver_source": resolved.source}
                )
                menu_item = resolve_menu_item(all_menu_items, sku)
                result = evaluate_action(cancel_action, session, menu_item, kitchen, all_menu_items, memory)
                if result.approved:
                    apply_approved_action(session, cancel_action)
                    log_execution(session.session_id, cancel_action, "approved", None)
                    # Clear focus — no item in focus after cancellation
                    if sku in session.active_context:
                        session.active_context[sku].selected = False
                    session.last_action_sku = None
                    session.last_action_type = None
                    session.last_quantity = None
                    item_name = menu_item.name if menu_item else sku
                    response = f"No problem. I've removed {item_name} from your cart."
                else:
                    response = result.user_message or "I couldn't undo that action."
                memory.update(user_input, response, agent_name=session.active_agent)
                return response

        elif resolved.intent in {ReferenceIntent.ADD_ALL, ReferenceIntent.ADD_THAT}:
            response = _execute_bulk_add(
                resolved.skus, session, kitchen, memory, user_input
            )
            memory.update(user_input, response, agent_name=session.active_agent)
            return response

        elif resolved.intent == ReferenceIntent.REPEAT:
            sku = resolved.skus[0] if resolved.skus else None
            if sku:
                repeat_action = ActionRequest(
                    action_type=ActionType.ADD_TO_CART,
                    sku=sku,
                    quantity=resolved.quantity or 1,
                    confidence=1.0,
                    meta={"repeat": True, "resolver_source": resolved.source}
                )
                menu_item = resolve_menu_item(all_menu_items, sku)
                result = evaluate_action(repeat_action, session, menu_item, kitchen, all_menu_items, memory)
                response = generate_response(action=repeat_action, result=result, menu_items=all_menu_items)
                if result.approved:
                    consume_tool_budget(session, repeat_action, result)
                    apply_approved_action(session, repeat_action)
                    log_execution(session.session_id, repeat_action, "approved", None)
                    session.last_action_sku = sku
                    session.last_quantity = repeat_action.quantity
                    session.last_action_type = ActionType.ADD_TO_CART.value
                    _mark_selected(sku, session)
                memory.update(user_input, response, agent_name=session.active_agent)
                return response

        elif resolved.intent == ReferenceIntent.QUANTITY:
            sku = resolved.skus[0] if resolved.skus else None
            if sku:
                qty_action = ActionRequest(
                    action_type=ActionType.ADD_TO_CART,
                    sku=sku,
                    quantity=resolved.quantity or 1,
                    confidence=1.0,
                    meta={"quantity_update": True, "resolver_source": resolved.source}
                )
                menu_item = resolve_menu_item(all_menu_items, sku)
                result = evaluate_action(qty_action, session, menu_item, kitchen, all_menu_items, memory)
                response = generate_response(action=qty_action, result=result, menu_items=all_menu_items)
                if result.approved:
                    consume_tool_budget(session, qty_action, result)
                    apply_approved_action(session, qty_action)
                    log_execution(session.session_id, qty_action, "approved", None)
                    session.last_action_sku = sku
                    session.last_quantity = qty_action.quantity
                    session.last_action_type = ActionType.ADD_TO_CART.value
                    _mark_selected(sku, session)
                memory.update(user_input, response, agent_name=session.active_agent)
                return response

        # Resolved but could not execute (no SKU found) — fall through to router

    # 1️⃣ ROUTING
    routing_action = router.route(user_input, session.active_agent)
    if routing_action.intent:
        session.active_intent = routing_action.intent

    if routing_action.confidence >= 0.6:
        target = routing_action.target_agent
        session.active_agent = target if target in AGENT_REGISTRY else "OrderTaker"

    # 2️⃣ GOVERNANCE: Context Scope Decision (BEFORE AGENT EXECUTION)
    policy = decide_context_scope(session, user_input, all_menu_items)
    session.context_scope = policy["context_scope"]
    session.authority_hint = policy["system_hint"]

    # 3️⃣ AGENT EXECUTION
    agent = AGENT_REGISTRY[session.active_agent]
    action = agent.run(user_input, session, memory)

    # 4️⃣ LOG INTENT
    log_intent(session.session_id, user_input, action)

    # 5️⃣ SHORT-CIRCUIT: NO_OP
    if action.action_type == ActionType.NO_OP:
        response = action.message or "I'm here to help! What can I get for you?"
        log_execution(session.session_id, action, "noop", None)

        # CONTEXT UPDATE FROM MENUEXPERT RESPONSE
        # MenuExpert delegates context writes to golden_loop so that only
        # items actually mentioned in the LLM's reply enter active_context.
        # Writing from relevant_items (what was searched) would pollute context
        # with all FULL_CATALOG items even when only one was relevant.
        # BM25 scoring against the response text gives us precise extraction.
        if session.active_agent == "MenuExpert" and response:
            _populate_context_from_response(response, session)

        # PENDING CLARIFICATION GUARD
        # Do NOT overwrite the window record if the previous turn was a pending
        # clarification. This keeps window[-1] as the clarification record so
        # the next turn's hint fires correctly.
        if not memory.pending_clarification():
            memory.update(user_input, response, agent_name=session.active_agent)

        return response

    # 6️⃣ SHORT-CIRCUIT: Agent Clarification
    if action.action_type == ActionType.ASK_CLARIFICATION:
        response_text = generate_response(action=action, result=None, menu_items=all_menu_items)
        log_execution(session.session_id, action, "agent_clarification", None)

        # POPULATE ACTIVE CONTEXT FROM SYSTEM OUTPUT (not user input)
        # The clarification response_text is what the system said — it may
        # list specific items ("You mentioned Pepperoni, Truffle, Margherita").
        # We extract those item names from the response and mark them mentioned.
        # This is the correct source: context = what system showed, not user typed.
        _populate_context_from_response(response_text, session)

        # Legacy fallback: also populate pending_items for backward compatibility
        # during transition. Remove this block in Phase 2.
        mentioned_in_context = [
            sku for sku, item in session.active_context.items()
            if item.mentioned
        ]
        if len(mentioned_in_context) > 1:
            session.pending_items = mentioned_in_context

        memory.update(
            user_input, response_text,
            agent_name=session.active_agent,
            status="agent_clarification",
            action_type=action.action_type,
            pending_sku=action.sku,
        )
        return response_text

    # 7️⃣ AUTHORITY EVALUATION
    menu_item = resolve_menu_item(all_menu_items, action.sku)
    result = evaluate_action(action, session, menu_item, kitchen, all_menu_items, memory)
    result.system_hint = session.authority_hint

    # 8️⃣ ⚖️ HANDLE RECOVERABLE VIOLATIONS & AUTO-HANDOFF
    if not result.approved:
        # 🔴 FATAL PATH
        if result.severity == Severity.FATAL:
            final_resp = result.user_message or "System Error."
            memory.update(user_input, final_resp, agent_name=session.active_agent)
            return final_resp

        # 🟢 8a️⃣ Jurisdiction mismatch → SILENT AUTO-HANDOFF
        if result.violation_type == ViolationType.INVALID_STATE and result.severity == Severity.RECOVERABLE:
            target_agent = result.meta.get("target_agent") if result.meta else None
            if target_agent:
                # Recursion guard: prevent infinite handoff loops.
                # If the correct agent still can't handle the request after
                # _MAX_HANDOFF_DEPTH retries, fail gracefully rather than
                # looping indefinitely.
                if _handoff_depth >= _MAX_HANDOFF_DEPTH:
                    final_resp = "I'm having trouble routing your request. Please try rephrasing."
                    memory.update(user_input, final_resp, agent_name=session.active_agent)
                    return final_resp
                session.active_agent = target_agent
                return golden_loop(
                    session=session,
                    user_input=user_input,
                    kitchen=kitchen,
                    memory=memory,
                    _handoff_depth=_handoff_depth + 1
                )

        # 🟡 8b️⃣ Deferred capabilities (age verification etc.)
        if result.severity == Severity.DEFERRED:
            recovery_action = ActionRequest(
                action_type=ActionType.ASK_CLARIFICATION,
                clarification_payload=result.user_message or "This action requires verification.",
                confidence=1.0,
                meta=result.meta or {}
            )
            response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
            log_execution(session.session_id, action, "deferred_triggered", result.violation_type)
            session.pending_deferred_sku = action.sku
            memory.update(
                user_input, response_text,
                agent_name=session.active_agent,
                status="authority_clarification",
                pending_sku=action.sku,
            )
            return response_text

        # 🔵 8c️⃣ General recoverable clarification (LOW_CONFIDENCE etc.)
        if result.requires_clarification:
            recovery_action = ActionRequest(
                action_type=ActionType.ASK_CLARIFICATION,
                clarification_payload=result.user_message or "Could you please clarify?",
                confidence=1.0,
                meta={
                    "violation": result.violation_type,
                    "original_action": action.action_type
                }
            )
            response_text = generate_response(action=recovery_action, result=result, menu_items=all_menu_items)
            log_execution(session.session_id, action, "recovery_triggered", result.violation_type)

            # Populate context from the recovery response text
            _populate_context_from_response(response_text, session)

            memory.update(
                user_input, response_text,
                agent_name=session.active_agent,
                status="authority_clarification",
                action_type=action.action_type,
                pending_sku=action.sku,
            )
            return response_text

    # 9️⃣ HANDLE UNCATEGORIZED VIOLATIONS (DEFENSIVE GUARD)
    if not result.approved:
        log_execution(session.session_id, action, "rejected_uncategorized", result.rejection_code)
        result.system_hint = f"FALLBACK_REJECTION: {result.system_hint or 'No hint provided'}"
        final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
        memory.update(user_input, final_response, agent_name=session.active_agent)
        return final_response

    # 🔟 APPLY APPROVED ACTIONS
    consume_tool_budget(session, action, result)
    apply_approved_action(session, action)
    log_execution(session.session_id, action, "approved", None)

    # Update focus, action tracking, and active_context
    if action.action_type == ActionType.ADD_TO_CART and action.sku:
        session.last_action_sku = action.sku
        session.last_quantity = action.quantity
        session.last_action_type = ActionType.ADD_TO_CART.value
        _mark_selected(action.sku, session)
    elif action.action_type == ActionType.REMOVE_FROM_CART and action.sku:
        session.last_action_type = ActionType.REMOVE_FROM_CART.value
        if action.sku in session.active_context:
            session.active_context[action.sku].selected = False

    # 1️⃣1️⃣ FINAL RESPONSE & MEMORY UPDATE
    final_response = generate_response(action=action, result=result, menu_items=all_menu_items)
    memory.update(user_input, final_response, agent_name=session.active_agent)
    return final_response