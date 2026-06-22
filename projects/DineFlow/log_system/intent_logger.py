# DineFlow/logging/intent_logger.py
from validation.schemas import ActionRequest

def log_intent(session_id: str, raw_input: str, action: ActionRequest):
    """
    Logs intent and raw user input for observability.
    """
    print(f"[INTENT] session={session_id} | input='{raw_input}' | action={action.action_type}")
    return "log_123"
