# # # aiva/state_machine/errors.py
# # from enum import Enum

# # class RejectionCode(str, Enum):
# #     ERR_ITEM_NOT_FOUND = "ERR_ITEM_NOT_FOUND"
# #     ERR_OUT_OF_STOCK = "ERR_OUT_OF_STOCK"
# #     ERR_AGE_RESTRICTION = "ERR_AGE_RESTRICTION"
# #     ERR_KITCHEN_OVERLOAD = "ERR_KITCHEN_OVERLOAD"
# #     ERR_INVALID_STATE = "ERR_INVALID_STATE"
# #     BUDGET_EXCEEDED = "BUDGET_EXCEEDED"



# # aiva/validation/errors.py
# from enum import Enum

# class RejectionCode(str, Enum):
#     ERR_ITEM_NOT_FOUND = "ERR_ITEM_NOT_FOUND"
#     ERR_OUT_OF_STOCK = "ERR_OUT_OF_STOCK"
#     ERR_AGE_RESTRICTION = "ERR_AGE_RESTRICTION"
#     ERR_KITCHEN_OVERLOAD = "ERR_KITCHEN_OVERLOAD"
#     ERR_INVALID_STATE = "ERR_INVALID_STATE"
#     BUDGET_EXCEEDED = "BUDGET_EXCEEDED"

# # 🆕 Custom Exception for the Golden Loop
# class ToolBudgetExceeded(Exception):
#     """Raised when the session budget reaches zero."""
#     def __init__(self, message="Tool budget exceeded for this session"):
#         self.message = message
#         super().__init__(self.message)



# DineFlow/validation/errors.py
from enum import Enum

# 🔴 Legacy RejectionCode (Keep for backward compatibility)
class RejectionCode(str, Enum):
    ERR_ITEM_NOT_FOUND = "ERR_ITEM_NOT_FOUND"
    ERR_OUT_OF_STOCK = "ERR_OUT_OF_STOCK"
    ERR_AGE_RESTRICTION = "ERR_AGE_RESTRICTION"
    ERR_KITCHEN_OVERLOAD = "ERR_KITCHEN_OVERLOAD"
    ERR_INVALID_STATE = "ERR_INVALID_STATE"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    ERR_INVALID_QUANTITY = "ERR_INVALID_QUANTITY"
    ERR_ITEM_NOT_IN_CART = "ERR_ITEM_NOT_IN_CART"
    ERR_AMBIGUOUS_CATEGORY = "ERR_AMBIGUOUS_CATEGORY"
    ERR_LOW_CONFIDENCE = "ERR_LOW_CONFIDENCE"

# 🆕 Step 11: Violation Taxonomy (New Standard)
class ViolationType(str, Enum):
    # 🔴 FATAL - Cannot proceed, must reject
    INVALID_SKU = "INVALID_SKU"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    AGE_RESTRICTION = "AGE_RESTRICTION"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    INVALID_STATE = "INVALID_STATE"
    KITCHEN_OVERLOAD = "KITCHEN_OVERLOAD"
    INVALID_QUANTITY = "INVALID_QUANTITY"
    ITEM_NOT_IN_CART = "ITEM_NOT_IN_CART"
    
    # 🟡 RECOVERABLE - Can be fixed with user input
    AMBIGUOUS_CATEGORY = "AMBIGUOUS_CATEGORY"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    MISSING_CONTEXT = "MISSING_CONTEXT"
    
    # 🟢 DEFERRED - Needs confirmation but allowed
    HIGH_COMPLEXITY_CONFIRM = "HIGH_COMPLEXITY_CONFIRM"
    LARGE_QUANTITY_CONFIRM = "LARGE_QUANTITY_CONFIRM"

class Severity(str, Enum):
    FATAL = "FATAL"              # Hard block, cannot proceed
    RECOVERABLE = "RECOVERABLE"  # Can be fixed with clarification
    DEFERRED = "DEFERRED"        # Needs confirmation, but can proceed

# 🆕 Custom Exception for the Golden Loop
class ToolBudgetExceeded(Exception):
    """Raised when the session budget reaches zero."""
    def __init__(self, message="Tool budget exceeded for this session"):
        self.message = message
        super().__init__(self.message)