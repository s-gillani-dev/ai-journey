# # aiva/validation/schemas.py

# from pydantic import BaseModel, Field, model_validator
# from typing import Optional, Dict, Any
# from enum import Enum


# # -----------------------------
# # Action Vocabulary (Closed Set)
# # -----------------------------

# class ActionType(str, Enum):
#     ADD_TO_CART = "ADD_TO_CART"
#     REMOVE_FROM_CART = "REMOVE_FROM_CART"
#     MODIFY_ITEM = "MODIFY_ITEM"
#     CHECKOUT = "CHECKOUT"
#     ASK_CLARIFICATION = "ASK_CLARIFICATION"
#     NO_OP = "NO_OP"
#     UNKNOWN = "UNKNOWN"  # 🆕 Add this for ambiguous/unclear intents


# # -----------------------------
# # LLM → System Contract
# # -----------------------------

# class ActionRequest(BaseModel):
#     """
#     The ONLY allowed structure the LLM may emit.
#     Anything else is a contract violation.
#     """

#     action_type: ActionType

#     sku: Optional[str] = Field(
#         default=None,
#         description="Menu SKU. Required for item-level actions."
#     )

#     quantity: int = Field(
#         default=1,
#         ge=1,
#         description="Quantity must be >= 1"
#     )

#     notes: Optional[str] = Field(
#         default=None,
#         description="Special instructions (extra cheese, no onions, etc.)"
#     )

#     clarification_payload: Optional[str] = Field(
#         default=None,
#         description="Clarification question or options when intent is ambiguous"
#     )

#     confidence: float = Field(
#         default=1.0,
#         ge=0.0,
#         le=1.0,
#         description="LLM self-reported confidence (advisory only)"
#     )

#     meta: Optional[Dict[str, Any]] = Field(
#         default=None,
#         description="Non-operational hints (never trusted)"
#     )

#     # -----------------------------
#     # Cross-field deterministic checks
#     # -----------------------------
#     @model_validator(mode="after")
#     def enforce_action_requirements(self) -> "ActionRequest":
#         if self.action_type in {
#             ActionType.ADD_TO_CART,
#             ActionType.REMOVE_FROM_CART,
#             ActionType.MODIFY_ITEM,
#         } and not self.sku:
#             raise ValueError(f"SKU is required for {self.action_type}")

#         if self.action_type == ActionType.ASK_CLARIFICATION and not self.clarification_payload:
#             raise ValueError("clarification_payload required for ASK_CLARIFICATION")

#         return self


# # -----------------------------
# # Internal Authority Result
# # -----------------------------

# class ValidationResult(BaseModel):
#     """
#     Deterministic output after all guards & authority checks.
#     """

#     approved: bool
#     rejection_code: Optional[str] = None
#     rejection_reason: Optional[str] = None
#     user_message: Optional[str] = None



# # aiva/validation/schemas.py
# from pydantic import BaseModel, Field, model_validator
# from typing import Optional, Dict, Any, List
# from enum import Enum

# class ActionType(str, Enum):
#     ADD_TO_CART = "ADD_TO_CART"
#     REMOVE_FROM_CART = "REMOVE_FROM_CART"
#     MODIFY_ITEM = "MODIFY_ITEM"
#     CHECKOUT = "CHECKOUT"
#     ASK_CLARIFICATION = "ASK_CLARIFICATION"
#     TRANSFER = "TRANSFER" 
#     NO_OP = "NO_OP"
#     UNKNOWN = "UNKNOWN"

# class IntentType(str, Enum):
#     GREETING = "GREETING"
#     ORDERING = "ORDERING"
#     INQUIRY = "INQUIRY"
#     OUT_OF_SCOPE = "OUT_OF_SCOPE"

# class ActionRequest(BaseModel):
#     action_type: ActionType

#     # --- Transfer Logic ---
#     target_agent: Optional[str] = Field(default=None)

#     # --- Item Level Actions ---
#     sku: Optional[str] = Field(default=None)
#     quantity: int = Field(default=1, ge=1)
#     notes: Optional[str] = Field(default=None)

#     # --- Dialogue Actions ---
#     # 🆕 IMPROVEMENT 1: Dedicated field for agent speech (Social/Greeter)
#     message: Optional[str] = Field(
#         default=None, 
#         description="Text response for the user (used by Greeter/MenuExpert)"
#     )
    
#     # Strictly for OrderTaker ambiguity scenarios
#     clarification_payload: Optional[str] = Field(default=None)

#     confidence: float = Field(default=1.0, ge=0.0, le=1.0)
#     meta: Optional[Dict[str, Any]] = Field(default=None)

#     @model_validator(mode="after")
#     def enforce_action_requirements(self) -> "ActionRequest":
#         if self.action_type in {ActionType.ADD_TO_CART, ActionType.REMOVE_FROM_CART, ActionType.MODIFY_ITEM} and not self.sku:
#             raise ValueError(f"SKU is required for {self.action_type}")
#         if self.action_type == ActionType.ASK_CLARIFICATION and not self.clarification_payload:
#             raise ValueError("clarification_payload required for ASK_CLARIFICATION")
#         if self.action_type == ActionType.TRANSFER and not self.target_agent:
#             raise ValueError("target_agent required for TRANSFER action")
#         return self

# class ValidationResult(BaseModel):
#     approved: bool
#     rejection_code: Optional[str] = None
#     rejection_reason: Optional[str] = None 
#     user_message: Optional[str] = None



# claud gives this
# aiva/validation/schemas.py
# from pydantic import BaseModel, Field, model_validator
# from typing import Optional, Dict, Any
# from enum import Enum

# class ActionType(str, Enum):
#     ADD_TO_CART = "ADD_TO_CART"
#     REMOVE_FROM_CART = "REMOVE_FROM_CART"
#     MODIFY_ITEM = "MODIFY_ITEM"
#     CHECKOUT = "CHECKOUT"
#     ASK_CLARIFICATION = "ASK_CLARIFICATION"
#     TRANSFER = "TRANSFER" 
#     NO_OP = "NO_OP"
#     UNKNOWN = "UNKNOWN"

# class IntentType(str, Enum):
#     GREETING = "GREETING"
#     ORDERING = "ORDERING"
#     INQUIRY = "INQUIRY"
#     OUT_OF_SCOPE = "OUT_OF_SCOPE"

# class ActionRequest(BaseModel):
#     action_type: ActionType

#     # --- Transfer Logic ---
#     target_agent: Optional[str] = Field(default=None)

#     # --- Item Level Actions ---
#     sku: Optional[str] = Field(default=None)
#     quantity: int = Field(default=1)  # 🔧 REMOVED ge=1 - Authority will check this
#     notes: Optional[str] = Field(default=None)

#     # --- Dialogue Actions ---
#     message: Optional[str] = Field(
#         default=None, 
#         description="Text response for the user (used by Greeter/MenuExpert)"
#     )
    
#     clarification_payload: Optional[str] = Field(default=None)

#     confidence: float = Field(default=1.0, ge=0.0, le=1.0)
#     meta: Optional[Dict[str, Any]] = Field(default=None)

#     @model_validator(mode="after")
#     def enforce_action_requirements(self) -> "ActionRequest":
#         # 🔧 RELAXED: Only check required fields, NOT business logic
#         # Authority will validate business rules
        
#         if self.action_type == ActionType.ASK_CLARIFICATION and not self.clarification_payload:
#             raise ValueError("clarification_payload required for ASK_CLARIFICATION")
#         if self.action_type == ActionType.TRANSFER and not self.target_agent:
#             raise ValueError("target_agent required for TRANSFER action")
        
#         # 🔧 REMOVED: SKU requirement - Authority will check this
#         # This allows optimistic agents to send actions without SKUs
        
#         return self

# # 🆕 Step 11: Enhanced ValidationResult
# class ValidationResult(BaseModel):
#     approved: bool
    
#     # 🆕 New fields (Step 11)
#     violation_type: Optional[str] = None  # Using ViolationType enum values
#     severity: Optional[str] = None        # Using Severity enum values
#     requires_clarification: bool = False
#     system_hint: Optional[str] = None
    
#     # 🔴 Legacy fields (keep for backward compatibility)
#     rejection_code: Optional[str] = None
#     rejection_reason: Optional[str] = None 
#     user_message: Optional[str] = None






# gemini gives the claud verson with fixes (testing)
# DineFlow/validation/schemas.py
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any
from enum import Enum

class ActionType(str, Enum):
    ADD_TO_CART = "ADD_TO_CART"
    REMOVE_FROM_CART = "REMOVE_FROM_CART"
    MODIFY_ITEM = "MODIFY_ITEM"
    CHECKOUT = "CHECKOUT"
    ASK_CLARIFICATION = "ASK_CLARIFICATION"
    TRANSFER = "TRANSFER" 
    NO_OP = "NO_OP"
    UNKNOWN = "UNKNOWN"

class IntentType(str, Enum):
    GREETING = "GREETING"
    ORDERING = "ORDERING"
    INQUIRY = "INQUIRY"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"

class ActionRequest(BaseModel):
    action_type: ActionType
    # 🆕 NEW: Intent tagging for Authority Jurisdiction
    intent: Optional[IntentType] = Field(default=None) 
    
    target_agent: Optional[str] = Field(default=None)
    sku: Optional[str] = Field(default=None)
    quantity: int = Field(default=1)
    notes: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    clarification_payload: Optional[str] = Field(default=None)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    meta: Optional[Dict[str, Any]] = Field(default=None)

    @model_validator(mode="after")
    def enforce_action_requirements(self) -> "ActionRequest":
        if self.action_type == ActionType.ASK_CLARIFICATION and not self.clarification_payload:
            raise ValueError("clarification_payload required for ASK_CLARIFICATION")
        if self.action_type == ActionType.TRANSFER and not self.target_agent:
            raise ValueError("target_agent required for TRANSFER action")
        return self

class ValidationResult(BaseModel):
    approved: bool
    
    # 🆕 Step 11: Rich Taxonomy
    violation_type: Optional[str] = None  # Maps to ViolationType enum
    severity: Optional[str] = None        # Maps to Severity enum
    requires_clarification: bool = False
    system_hint: Optional[str] = None
    
    # 🔴 Legacy fields (Backward Compatibility)
    rejection_code: Optional[str] = None
    rejection_reason: Optional[str] = None 
    user_message: Optional[str] = None
    
    # 🆕 SYSTEMIC FIX: Metadata field for structured policy hand-off
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)