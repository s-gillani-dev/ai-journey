# # final working version for step 1-4
# # aiva/tools/search/hybrid.py
# # NOTE:
# # Linear rank fusion used for POC simplicity.
# # Can be upgraded to Reciprocal Rank Fusion (RRF) for large menus (>200 items).

# from typing import List
# from aiva.state_machine.types import MenuItemSnapshot
# from .bm25 import bm25_search
# from .vector import vector_search

# def hybrid_search(query: str, menu_items: List[MenuItemSnapshot], alpha: float = 0.5) -> List[MenuItemSnapshot]:
#     """
#     Combines BM25 and Vector search to rank menu items.
#     alpha=0.5: equal weight for BM25 and vector similarity
#     """
#     if not menu_items:
#         return []

#     # Get BM25 ranking scores
#     bm25_ranking = {item.sku: rank for rank, item in enumerate(bm25_search(query, menu_items))}
    
#     # Get vector similarity scores
#     vector_items = vector_search(query, menu_items)
#     vector_ranking = {item.sku: rank for rank, item in enumerate(vector_items)}

#     # Combine rankings
#     combined_scores = {}
#     for item in menu_items:
#         bm25_score = len(menu_items) - bm25_ranking.get(item.sku, len(menu_items))
#         vector_score = len(menu_items) - vector_ranking.get(item.sku, len(menu_items))
#         combined_scores[item.sku] = alpha * bm25_score + (1 - alpha) * vector_score

#     # Sort items by combined score descending
#     return sorted(menu_items, key=lambda x: combined_scores[x.sku], reverse=True)







# # DineFlow/tools/search/hybrid.py
# from typing import List
# from state_machine.types import MenuItemSnapshot
# from .vector import vector_search

# def hybrid_search(query: str, menu_items: List[MenuItemSnapshot], bm25_engine: any) -> List[MenuItemSnapshot]:
#     """Fuses BM25 and Vector results using RRF (Reciprocal Rank Fusion)."""
#     v_ids = vector_search(query)
#     b_ids = bm25_engine.search(query)

#     # RRF Score Calculation
#     scores = {item.sku: 0.0 for item in menu_items}
#     for rank, sku in enumerate(v_ids):
#         scores[sku] += 1.0 / (rank + 60)
#     for rank, sku in enumerate(b_ids):
#         scores[sku] += 1.0 / (rank + 60)

#     # Sort items by fused score
#     return sorted(menu_items, key=lambda x: scores[x.sku], reverse=True)





# claud recent version testing,,,
# DineFlow/tools/search/hybrid.py
from typing import List
from state_machine.types import MenuItemSnapshot
from .vector import vector_search


def hybrid_search(query: str, menu_items: List[MenuItemSnapshot], bm25_engine: any) -> List[MenuItemSnapshot]:
    """
    Fuses BM25 and Vector results using RRF (Reciprocal Rank Fusion).

    ── Why This File Required No Logic Changes ───────────────────────────────
    The RRF algorithm here is correct and unchanged. The "spicy" failure was
    never in the fusion logic — it was upstream:

      1. BM25 corpus only had name+SKU → "spicy" scored 0 → empty b_ids
      2. Vector docs only had name+SKU → embedding had no semantic signal
         for "spicy" → poor v_ids

    Both are now fixed in bm25.py and vector.py. This function receives better
    candidate lists and fuses them the same way — no change needed here.

    ── RRF Constant (k=60) ───────────────────────────────────────────────────
    The constant 60 is the standard RRF default from the original Cormack et al.
    paper. It controls how much weight rank position has vs. raw score.
    Increasing k flattens the curve (all ranks contribute more equally).
    Decreasing k sharpens it (top ranks dominate heavily).
    For a small menu (5–50 items), 60 is appropriate. Tune if catalog grows.

    ── Zero-Score Items ──────────────────────────────────────────────────────
    Items not present in either result list get a score of 0.0 and sort to
    the bottom. They are still returned in the list — callers are responsible
    for slicing to the desired top-k (menu_expert.py does [:5]).
    """
    v_ids = vector_search(query)
    b_ids = bm25_engine.search(query)

    # RRF Score Calculation
    scores = {item.sku: 0.0 for item in menu_items}
    for rank, sku in enumerate(v_ids):
        if sku in scores:
            scores[sku] += 1.0 / (rank + 60)
    for rank, sku in enumerate(b_ids):
        if sku in scores:
            scores[sku] += 1.0 / (rank + 60)

    return sorted(menu_items, key=lambda x: scores[x.sku], reverse=True)