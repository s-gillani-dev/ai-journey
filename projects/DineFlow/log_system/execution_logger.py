# DineFlow/logging/execution_logger.py
from validation.schemas import ActionRequest

def log_execution(session_id: str, action: ActionRequest, status: str, rejection_code: str | None = None):
    """
    Logs the result of action execution.
    """
    print(f"[EXECUTION] session={session_id} | action={action.action_type} | status={status} | rejection={rejection_code}")
    return "exec_log_123"
