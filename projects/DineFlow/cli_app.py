# final working version for step 1-4
# # cli_app.py
# from state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.golden_loop import golden_loop

# def run_aiva():
#     # 1. Initialize a "Real" Session
#     session = SessionState(
#         session_id="live-test-001",
#         active_agent="OrderTaker",
#         tool_budget_remaining=5,  # Give it 5 turns
#         age_verified=False        # Start with ID unverified
#     )

#     # 2. Simulate a Busy Kitchen
#     kitchen = KitchenSnapshot(load_percentage=80)

#     print("--- 🤖 AIVA Live CLI ---")
#     print("Type 'exit' to quit. Current Budget: 5\n")

#     while True:
#         user_input = input("You: ")
        
#         if user_input.lower() in ["exit", "quit"]:
#             break

#         # 3. Trigger the REAL Golden Loop (Calls actual LLM)
#         try:
#             response = golden_loop(
#                 session=session,
#                 user_input=user_input,
#                 kitchen=kitchen
#             )
            
#             print(f"AIVA: {response}")
#             print(
#             f"(Remaining Budget: {session.tool_budget_remaining}, "
#             f"Ambiguous Retries: {session.ambiguous_retries}, "
#             f"Active Agent: {session.active_agent})\n"
#         )

#             if session.tool_budget_remaining <= 0:
#                 print("--- 🛑 Session Budget Exhausted ---")
#                 break
                
#         except Exception as e:
#             print(f"Error: {e}")

# if __name__ == "__main__":
#     run_aiva()






# cli_app.py
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.golden_loop import golden_loop
# from aiva.orchestration.memory_manager import MemoryManager # 🆕

# def run_aiva():
#     session = SessionState(
#         session_id="live-test-001",
#         active_agent="OrderTaker",
#         tool_budget_remaining=5,
#         age_verified=False
#     )

#     # 🆕 Initialize the memory manager for this session
#     memory = MemoryManager(session_id=session.session_id)
#     kitchen = KitchenSnapshot(load_percentage=80)

#     print("--- 🤖 AIVA Live CLI (Memory Enabled) ---")
#     print("Type 'exit' to quit.\n")

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]: break

#         try:
#             # 🆕 Pass the memory object into the loop
#             response = golden_loop(
#                 session=session,
#                 user_input=user_input,
#                 kitchen=kitchen,
#                 memory=memory
#             )
            
#             print(f"AIVA: {response}")
#             print(f"(Budget: {session.tool_budget_remaining} | Retries: {session.ambiguous_retries})\n")

#             if session.tool_budget_remaining <= 0:
#                 print("--- 🛑 Session Budget Exhausted ---")
#                 break
                
#         except Exception as e:
#             print(f"Error: {e}")

# if __name__ == "__main__":
#     run_aiva()



# final working version for step 5
# cli_app.py
# import uuid
# import json
# import os
# from aiva.state_machine.types import SessionState, KitchenSnapshot
# from aiva.orchestration.golden_loop import golden_loop
# from aiva.orchestration.memory_manager import MemoryManager

# STATE_DB_PATH = "session_store.json"

# def get_session_for_user(user_id: str) -> SessionState:
#     """
#     Logic: 
#     1. Check DB for an active (DRAFT) session for this user.
#     2. If found, return it (Resume).
#     3. If not, create a brand new session (Start).
#     """
#     if os.path.exists(STATE_DB_PATH):
#         with open(STATE_DB_PATH, "r") as f:
#             data = json.load(f)
#             # Find any session belonging to this user that isn't 'COMPLETED'
#             for sess_id, state in data.items():
#                 if state.get("user_id") == user_id and state.get("order_status") == "DRAFT":
#                     return SessionState(**state)
    
#     # Otherwise, create NEW
#     return SessionState(
#         session_id=f"sess-{str(uuid.uuid4())[:4]}",
#         user_id=user_id,
#         active_agent="OrderTaker",
#         tool_budget_remaining=5
#     )

# def save_session_state(session: SessionState):
#     """Saves session state with a safeguard for the file existing."""
#     data = {}
#     try:
#         if os.path.exists(STATE_DB_PATH):
#             with open(STATE_DB_PATH, "r") as f:
#                 content = f.read()
#                 data = json.loads(content) if content else {}
        
#         data[session.session_id] = session.model_dump()
        
#         with open(STATE_DB_PATH, "w") as f:
#             json.dump(data, f, indent=2)
#     except Exception as e:
#         print(f"Critical: Could not save session state: {e}")

# def run_aiva(user_id: str = "guest_user-8"):
    
#     # 1. Identity Resolution
#     session = get_session_for_user(user_id)
#     print("Identity Resolution----- session", session)
    
#     # 2. Setup
#     memory = MemoryManager(session_id=session.session_id)
#     kitchen = KitchenSnapshot(load_percentage=80)

#     print(f"--- 🤖 AIVA Session: {session.session_id} | User: {user_id} ---")
    
#     # Logic to greet differently if resuming
#     if session.ambiguous_retries > 0 or session.tool_budget_remaining < 5:
#         print("AIVA: Welcome back! Let's continue your order.")

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]: break

#         try:
#             response = golden_loop(
#                 session=session,
#                 user_input=user_input,
#                 kitchen=kitchen,
#                 memory=memory
#             )
            
#             save_session_state(session)
            
#             print(f"AIVA: {response}")
#             print(f"(Budget: {session.tool_budget_remaining} | Retries: {session.ambiguous_retries})\n")
                
#         except Exception as e:
#             print(f"Error: {e}")

# if __name__ == "__main__":
#     run_aiva()







# projects/DineFlow/cli_app.py
import uuid
import json
import warnings
import os
from state_machine.types import SessionState, KitchenSnapshot
from orchestration.golden_loop import golden_loop
from orchestration.memory_manager import MemoryManager
# Suppress HuggingFace warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DB_PATH = os.path.join(BASE_DIR, "session_store.json")

def get_session_for_user(user_id: str) -> SessionState:
    if os.path.exists(STATE_DB_PATH):
        with open(STATE_DB_PATH, "r") as f:
            try:
                data = json.load(f)
                for sess_id, state in data.items():
                    if state.get("user_id") == user_id and state.get("order_status") == "DRAFT":
                        return SessionState(**state)
            except json.JSONDecodeError:
                pass
    
    # 🆕 Starting as OrderTaker is fine as a default, 
    # but the Router will immediately move them to Greeter on first "Hi"
    return SessionState(
        session_id=f"sess-{str(uuid.uuid4())[:4]}",
        user_id=user_id,
        active_agent="OrderTaker",
        tool_budget_remaining=5
    )

def save_session_state(session: SessionState):
    """Saves session state with a safeguard for the file existing."""
    data = {}
    try:
        if os.path.exists(STATE_DB_PATH):
            with open(STATE_DB_PATH, "r") as f:
                content = f.read()
                data = json.loads(content) if content else {}
        
        data[session.session_id] = session.model_dump()
        
        with open(STATE_DB_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Critical: Could not save session state: {e}")

def run_dine_flow(user_id: str = "guest_user-77"):
    session = get_session_for_user(user_id)
    memory = MemoryManager(session_id=session.session_id)
    
    # We can simulate a varying kitchen load
    kitchen = KitchenSnapshot(load_percentage=40) 

    print(f"--- 🤖 DineFlow Session: {session.session_id} ---")
    print(f"--- 🕵️ Current Agent: {session.active_agent} ---")
    
    if session.tool_budget_remaining < 5:
        print(f"DineFlow: Welcome back! I see we were working on an order.")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]: break
            if not user_input.strip(): continue

            # The Golden Loop now handles the routing between Greeter, Expert, and OrderTaker
            response = golden_loop(
                session=session,
                user_input=user_input,
                kitchen=kitchen,
                memory=memory
            )
            
            save_session_state(session)
            
            # 🆕 UPDATED UI: Show which agent handled the request
            print(f"\n[{session.active_agent}] DineFlow: {response}")
            print(f"Budget: {session.tool_budget_remaining}/5 | Kitchen Load: {kitchen.load_percentage}%")
            print("-" * 40)
                
        except Exception as e:
            print(f"⚠️ Orchestration Error: {e}")

if __name__ == "__main__":
    run_dine_flow()