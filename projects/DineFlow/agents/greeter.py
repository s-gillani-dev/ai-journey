# aiva/agents/greeter.py
# from aiva.llm.client import call_llm
# from aiva.validation.schemas import ActionRequest, ActionType

# class GreeterAgent:
#     def __init__(self):
#         self.prompt_path = "aiva/llm/prompts/greeter.md"

#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         with open(self.prompt_path, "r") as f:
#             system_prompt = f.read()

#         response_text = call_llm(system_prompt, user_input)

#         action = ActionRequest(
#             action_type=ActionType.NO_OP,
#             message=response_text,
#             confidence=1.0
#         )

#         # 🛡️ OPTIONAL 3: Freeze Greeter contract defensively
#         assert action.action_type == ActionType.NO_OP, "GreeterAgent violated contract: Must return NO_OP"
        
#         return action
    


# # DineFlow/agents/greeter.py
# import os
# from DineFlow.llm.client import call_llm
# from DineFlow.llm.response_parser import parse_action
# from DineFlow.validation.schemas import ActionRequest, ActionType

# class GreeterAgent:
#     def __init__(self):
#         self.prompt_path = "DineFlow/llm/prompts/greeter.md"
#         self.fallback_prompt = (
#             "You are DineFlow, a friendly restaurant greeter. "
#             "Greet users warmly in 1-2 sentences. "
#             "Return JSON: {\"message\": \"your greeting\"}"
#         )
    
#     def run(self, user_input: str, session, memory) -> ActionRequest:
#         # Load prompt with fallback
#         if os.path.exists(self.prompt_path):
#             with open(self.prompt_path, "r") as f:
#                 system_prompt = f.read()
#         else:
#             system_prompt = self.fallback_prompt
        
#         # Ensure JSON compliance
#         if "json" not in system_prompt.lower():
#             system_prompt += "\n\nRespond with JSON containing a 'message' field."
        
#         # Call LLM
#         response_text = call_llm(system_prompt, user_input)
        
#         # Parse response
#         try:
#             parsed = parse_action(response_text)
#             final_message = parsed.message or "Hello! Welcome to DineFlow."
#         except Exception as e:
#             print(f"⚠️ Greeter parse error: {e}")
#             final_message = response_text.strip() or "Hello! How can I help you?"
        
#         return ActionRequest(
#             action_type=ActionType.NO_OP,
#             message=final_message,
#             confidence=1.0
#         )




# DineFlow/agents/greeter.py
import os
from llm.client import call_llm
from llm.response_parser import parse_action
from validation.schemas import ActionRequest, ActionType, IntentType

class GreeterAgent:
    def __init__(self):
        self.prompt_path = "DineFlow/llm/prompts/greeter.md"
        self.fallback_prompt = (
            "You are DineFlow, a friendly restaurant greeter. "
            "Greet users warmly in 1-2 sentences. "
            "CRITICAL: You MUST return ONLY valid JSON with these exact fields: "
            '{"action_type": "NO_OP", "message": "your greeting", "confidence": 1.0}'
        )
    
    def run(self, user_input: str, session, memory) -> ActionRequest:
        # Load prompt with fallback
        if os.path.exists(self.prompt_path):
            with open(self.prompt_path, "r") as f:
                system_prompt = f.read()
        else:
            system_prompt = self.fallback_prompt
        
        # 🆕 STRONGER JSON ENFORCEMENT
        if "json" not in system_prompt.lower():
            system_prompt += (
                "\n\n## MANDATORY OUTPUT FORMAT ##\n"
                "Return ONLY valid JSON. Do not include any text before or after the JSON.\n"
                "Required fields: action_type, message, confidence\n"
                "Example: {\"action_type\": \"NO_OP\", \"message\": \"Hello!\", \"confidence\": 1.0}"
            )
        
        # Call LLM
        response_text = call_llm(system_prompt, user_input)
        
        # Parse response (parser now auto-fixes incomplete JSON)
        parsed = parse_action(response_text)
        
        # Ensure we have a valid message
        if not parsed.message or parsed.message.strip() == "":
            parsed.message = "Hello! Welcome to DineFlow. How can I help you today?"
        
        # Ensure correct action type and intent
        return ActionRequest(
            action_type=ActionType.NO_OP,
            intent=IntentType.GREETING,
            message=parsed.message,
            confidence=1.0
        )