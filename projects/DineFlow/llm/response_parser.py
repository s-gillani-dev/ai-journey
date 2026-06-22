# # llm/response_parser.py
# from aiva.validation.schemas import ActionRequest, ActionType

# def parse_action(raw_output: str) -> ActionRequest:
#     """
#     Safely parse the raw LLM output into ActionRequest.
#     On failure, return NO_OP action.
#     """
#     try:
#         return ActionRequest.model_validate_json(raw_output)
#     except Exception:
#         # Contract violation fallback
#         return ActionRequest(action_type=ActionType.NO_OP)




# # DineFlow/llm/response_parser.py
# import json
# import logging
# from validation.schemas import ActionRequest, ActionType

# logger = logging.getLogger(__name__)

# def parse_action(raw_output: str) -> ActionRequest:
#     """
#     Safely parse the raw LLM output. 
#     Handles common LLM formatting issues (like markdown backticks).
#     """
#     clean_output = raw_output.strip()
    
#     # 1. Strip Markdown JSON blocks if present
#     if clean_output.startswith("```"):
#         clean_output = clean_output.strip("`").replace("json", "", 1).strip()

#     try:
#         return ActionRequest.model_validate_json(clean_output)
#     except Exception as e:
#         # 2. Log the actual error for debugging
#         logger.error(f"Failed to parse LLM output: {clean_output} | Error: {e}")
        
#         # 3. Fallback to NO_OP but perhaps with a flag that it was a parser error
#         return ActionRequest(
#             action_type=ActionType.NO_OP,
#             meta={"parser_error": str(e)} 
#         )




# DineFlow/llm/response_parser.py
import json
import logging
import re
from validation.schemas import ActionRequest, ActionType  # ✅ Fixed import

logger = logging.getLogger(__name__)

def parse_action(raw_output: str) -> ActionRequest:
    """
    Safely parse raw LLM output into an ActionRequest.
    Uses Regex to extract JSON from Markdown and applies systematic auto-fixes
    for incomplete LLM responses.
    """
    # 1. Guard against empty/None input
    if not raw_output:
        logger.warning("Received empty LLM output")
        return ActionRequest(
            action_type=ActionType.NO_OP,
            message="I'm sorry, I encountered an empty response.",
            confidence=0.0,
            meta={"parser_error": "empty_input"}
        )
    
    # 2. 🆕 ROBUST REGEX EXTRACTION
    # Finds JSON even if LLM includes conversational text around code blocks
    clean_output = raw_output.strip()
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_output, re.DOTALL)
    
    if json_match:
        clean_output = json_match.group(1).strip()
    else:
        # Fallback: Strip backticks manually if no code block found
        clean_output = clean_output.strip("`").replace("json", "", 1).strip()
    
    try:
        # 3. Parse as Dictionary
        data = json.loads(clean_output)
        
        # 4. ✅ SYSTEMATIC AUTO-FIX: Complete missing schema fields
        if "action_type" not in data:
            if "message" in data:
                logger.warning("LLM returned incomplete JSON (missing action_type). Auto-fixing...")
                data["action_type"] = "NO_OP"  # ✅ Direct string (cleaner than .value)
                data["confidence"] = data.get("confidence", 1.0)
            else:
                # If no message either, this is severely broken
                logger.error(f"LLM returned invalid JSON structure: {data}")
                return ActionRequest(
                    action_type=ActionType.NO_OP,
                    message="I'm having trouble understanding. Could you rephrase?",
                    confidence=0.3,
                    meta={"parser_error": "missing_required_fields", "data": str(data)[:100]}
                )
        
        # 5. Validate against Pydantic schema
        return ActionRequest.model_validate(data)
    
    except json.JSONDecodeError as e:
        # 6. Handle non-JSON plain text responses
        logger.error(f"Failed to parse LLM output as JSON: {e}")
        
        return ActionRequest(
            action_type=ActionType.NO_OP,
            message=clean_output[:500],  # Use cleaned raw text as message
            confidence=0.5,
            meta={"parser_error": "invalid_json", "raw_chunk": clean_output[:100]}
        )
    
    except Exception as e:
        # 7. Handle Pydantic validation errors
        logger.error(f"Pydantic validation error: {e}")
        
        # Attempt to salvage the 'message' field
        try:
            salvaged_data = json.loads(clean_output)
            message = salvaged_data.get("message", "Hello! Welcome to DineFlow.")
        except:
            message = "Hello! I'm here to help, but I had trouble formatting my response."
        
        return ActionRequest(
            action_type=ActionType.NO_OP,
            message=message,
            confidence=1.0,
            meta={"parser_error": "validation_error", "error": str(e)[:200]}
        )