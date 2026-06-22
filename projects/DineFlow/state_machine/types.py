# # DineFlow/state_machine/types.py

# from pydantic import BaseModel, Field
# from typing import Dict, Optional
# from enum import Enum


# class ContextScope(str, Enum):
#     FULL_CATALOG = "FULL_CATALOG"
#     FILTERED_SEARCH = "FILTERED_SEARCH"

# class SessionState(BaseModel):
#     user_id: str
#     session_id: str
#     active_agent: str
#     age_verified: bool = False
#     tool_budget_remaining: int = 3
#     order_status: str = "DRAFT"
#      # Ambiguity Gate state
#     last_ambiguous_intent: Optional[str] = None
#     ambiguous_retries: int = 0
#     # Initialize as an empty dict by default
#     cart: Dict[str, int] = Field(default_factory=dict)
#      # 🆕 Persistent semantic state
#     active_intent: Optional[str] = None
#     context_scope: Optional[ContextScope] = None
#     # 🆕 Temporary storage for Authority reasoning
#     # This bridges the gap between pre-execution and final validation
#     authority_hint: Optional[str] = None


# class MenuItemSnapshot(BaseModel):
#     sku: str
#     name: str
#     price: float
#     in_stock: bool
#     is_alcohol: bool = False
#     complexity_score: int = 1  # 1 = simple, 5 = complex


# class KitchenSnapshot(BaseModel):
#     load_percentage: int  # 0–100



# # DineFlow/state_machine/types.py

# from pydantic import BaseModel, Field
# from typing import Dict, List, Optional
# from enum import Enum


# class ContextScope(str, Enum):
#     FULL_CATALOG = "FULL_CATALOG"
#     FILTERED_SEARCH = "FILTERED_SEARCH"


# class SessionState(BaseModel):
#     user_id: str
#     session_id: str
#     active_agent: str
#     age_verified: bool = False
#     tool_budget_remaining: int = 3
#     order_status: str = "DRAFT"
#     # Ambiguity Gate state
#     last_ambiguous_intent: Optional[str] = None
#     ambiguous_retries: int = 0
#     # Initialize as an empty dict by default
#     cart: Dict[str, int] = Field(default_factory=dict)
#     # 🆕 Persistent semantic state
#     active_intent: Optional[str] = None
#     context_scope: Optional[ContextScope] = None
#     # 🆕 Temporary storage for Authority reasoning
#     # This bridges the gap between pre-execution and final validation
#     authority_hint: Optional[str] = None


# class MenuItemSnapshot(BaseModel):
#     sku: str
#     name: str
#     price: float
#     in_stock: bool
#     is_alcohol: bool = False
#     complexity_score: int = 1  # 1 = simple, 5 = complex

#     # ── Search & LLM Context Fields ──────────────────────────────────────────
#     #
#     # description: Natural language prose fed into {{MENU_CONTEXT}} in the
#     #   MenuExpert prompt. The LLM reasons from this text to answer attribute
#     #   questions ("Is it spicy?", "What's the base?", "Does it pair with beer?").
#     #   Without this field, the LLM receives no semantic content and correctly
#     #   triggers its "I don't have that information" fallback.
#     #
#     # tags: Keyword tokens fed into BM25 corpus and vector embedding documents.
#     #   Cover three layers: flavor ("spicy", "mild"), dietary ("vegetarian"),
#     #   and category ("beer", "lager"). BM25 cannot handle negation, so
#     #   negative attributes like "non-spicy" must be explicit positive tokens.
#     #   Without this field, hybrid_search returns 0 results for attribute
#     #   queries regardless of context scope.
#     #
#     # Both fields default to empty so existing code that builds MenuItemSnapshot
#     # without them (tests, fixtures, legacy paths) does not break.
#     description: str = ""
#     tags: List[str] = Field(default_factory=list)


# class KitchenSnapshot(BaseModel):
#     load_percentage: int  # 0–100


# DineFlow/state_machine/types.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class ContextScope(str, Enum):
    FULL_CATALOG = "FULL_CATALOG"
    FILTERED_SEARCH = "FILTERED_SEARCH"


class ContextItem(BaseModel):
    """
    Represents a single menu item that is currently "in focus" in the conversation.

    Items enter active_context when:
      - The system lists them in a clarification response
      - MenuExpert shows them in a menu browse response

    Items are never added from raw user input — context is built from
    what the system *showed*, not what the user *typed*.

    Fields:
        sku:                  Menu item identifier (matches MenuItemSnapshot.sku)
        name:                 Human-readable name for display
        mentioned:            True when the system has shown this item to the user
        selected:             True when the user has confirmed or ordered this item
        last_mentioned_turn:  session.turn_id when this item was last shown
        confidence:           How confidently the system matched this item (0.0–1.0)
    """
    sku: str
    name: str
    mentioned: bool = False
    selected: bool = False
    last_mentioned_turn: int = 0
    confidence: float = 1.0


class SessionState(BaseModel):
    user_id: str
    session_id: str
    active_agent: str
    age_verified: bool = False
    tool_budget_remaining: int = 3
    order_status: str = "DRAFT"
    # Ambiguity Gate state
    last_ambiguous_intent: Optional[str] = None
    ambiguous_retries: int = 0
    # Initialize as an empty dict by default
    cart: Dict[str, int] = Field(default_factory=dict)
    # 🆕 Persistent semantic state
    active_intent: Optional[str] = None
    context_scope: Optional[ContextScope] = None
    # 🆕 Temporary storage for Authority reasoning
    authority_hint: Optional[str] = None
    # 🆕 DEFERRED CAPABILITY STATE
    pending_deferred_sku: Optional[str] = None
    # 🆕 CONVERSATIONAL FOCUS — last successfully added item
    last_action_sku: Optional[str] = None
    last_quantity: Optional[int] = None
    last_action_type: Optional[str] = None
    # 🆕 PENDING ITEMS — legacy fallback for "add all"
    # Kept as safety net while active_context stabilises.
    # SemanticResolver prefers active_context; falls back to this.
    # Remove in Phase 2 once active_context is fully trusted.
    pending_items: List[str] = Field(default_factory=list)
    # 🆕 TURN COUNTER
    # Incremented at the start of every golden_loop call.
    # Used by ContextItem.last_mentioned_turn for context expiry.
    turn_id: int = 0
    # 🆕 ACTIVE CONTEXT GRAPH
    # Maps SKU → ContextItem for items currently in conversational focus.
    # Populated ONLY from system outputs (clarification text, MenuExpert results).
    # Read by SemanticResolver to resolve "all", "that", "same", bare numbers.
    active_context: Dict[str, ContextItem] = Field(default_factory=dict)


class MenuItemSnapshot(BaseModel):
    sku: str
    name: str
    price: float
    in_stock: bool
    is_alcohol: bool = False
    complexity_score: int = 1
    description: str = ""
    tags: List[str] = Field(default_factory=list)


class KitchenSnapshot(BaseModel):
    load_percentage: int  # 0–100