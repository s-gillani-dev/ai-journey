# final working version for step 1-4
# aiva/tools/search/bm25.py
# from typing import List
# from aiva.state_machine.types import MenuItemSnapshot

# def bm25_search(query: str, menu_items: List[MenuItemSnapshot]) -> List[MenuItemSnapshot]:
#     """
#     Lightweight BM25-like ranking for menu items (POC).
#     Ranks items by number of query words matching the item name.
#     """
#     query_words = set(query.lower().split())

#     def score(item: MenuItemSnapshot) -> int:
#         item_words = set(item.name.lower().split())
#         return len(query_words.intersection(item_words))

#     # Sort by score descending; higher overlap = higher relevance
#     return sorted(menu_items, key=score, reverse=True)







# # DineFlow/tools/search/bm25.py
# from rank_bm25 import BM25Okapi
# from typing import List
# from state_machine.types import MenuItemSnapshot

# class MenuBM25:
#     def __init__(self, menu_items: List[MenuItemSnapshot]):
#         self.items = menu_items
#         # Tokenize names and SKUs: "Pepperoni Pizza" -> ["pepperoni", "pizza", "pz-pep"]
#         self.corpus = [item.name.lower().split() + [item.sku.lower()] for item in menu_items]
#         self.bm25 = BM25Okapi(self.corpus)

#     def search(self, query: str, n: int = 3) -> List[str]:
#         """Returns SKUs ranked by BM25 keyword relevance."""
#         tokenized_query = query.lower().split()
#         scores = self.bm25.get_scores(tokenized_query)
#         # Pair items with scores and return SKUs of matches
#         ranked = sorted(zip(self.items, scores), key=lambda x: x[1], reverse=True)
#         return [item.sku for item, score in ranked if score > 0]




# claud recent version testing....

# # DineFlow/tools/search/bm25.py
# from rank_bm25 import BM25Okapi
# from typing import List
# from state_machine.types import MenuItemSnapshot


# class MenuBM25:
#     def __init__(self, menu_items: List[MenuItemSnapshot]):
#         self.items = menu_items

#         # ── Expanded Corpus ────────────────────────────────────────────────────
#         #
#         # v1 (old): Only tokenized item name + SKU.
#         #   "Pepperoni Pizza" → ["pepperoni", "pizza", "pz-pep"]
#         #   Problem: "spicy" does not appear → BM25 score = 0 → item never retrieved.
#         #
#         # v2 (new): Tokenizes name + description + tags + SKU.
#         #   "Pepperoni Pizza ... spicy pepperoni ... [spicy, hot, classic]"
#         #   → ["pepperoni", "pizza", ..., "spicy", "pepperoni", ..., "spicy", "hot", "classic", "pz-pep"]
#         #   Now "spicy" exists in the corpus → BM25 finds it → item retrieved.
#         #
#         # Tag tokens are deliberately repeated via join because BM25Okapi uses
#         # term frequency — a token appearing in both the description and tags
#         # gets a higher TF score, which is correct behaviour: if "spicy" is in
#         # both prose and the curated tag list, it is more relevant than if it
#         # appears in prose alone.
#         self.corpus = []
#         for item in menu_items:
#             tokens = (
#                 item.name.lower().split()
#                 + item.description.lower().split()
#                 + [tag.lower() for tag in item.tags]
#                 + [item.sku.lower()]
#             )
#             self.corpus.append(tokens)

#         self.bm25 = BM25Okapi(self.corpus)

#     def search(self, query: str, n: int = 3) -> List[str]:
#         """
#         Returns SKUs ranked by BM25 keyword relevance.

#         Only items with a positive score are returned — a score of 0 means
#         none of the query tokens appeared in that item's corpus document.
#         """
#         tokenized_query = query.lower().split()
#         scores = self.bm25.get_scores(tokenized_query)
#         ranked = sorted(zip(self.items, scores), key=lambda x: x[1], reverse=True)
#         return [item.sku for item, score in ranked if score > 0]




# DineFlow/tools/search/bm25.py
from rank_bm25 import BM25Okapi
from typing import List
from state_machine.types import MenuItemSnapshot


class MenuBM25:
    def __init__(self, menu_items: List[MenuItemSnapshot]):
        self.items = menu_items

        # ── Expanded Corpus ────────────────────────────────────────────────────
        #
        # v1 (old): Only tokenized item name + SKU.
        #   "Pepperoni Pizza" → ["pepperoni", "pizza", "pz-pep"]
        #   Problem: "spicy" does not appear → BM25 score = 0 → item never retrieved.
        #
        # v2 (new): Tokenizes name + description + tags + SKU.
        #   "Pepperoni Pizza ... spicy pepperoni ... [spicy, hot, classic]"
        #   → ["pepperoni", "pizza", ..., "spicy", "pepperoni", ..., "spicy", "hot", "classic", "pz-pep"]
        #   Now "spicy" exists in the corpus → BM25 finds it → item retrieved.
        #
        # Tag tokens are deliberately repeated via join because BM25Okapi uses
        # term frequency — a token appearing in both the description and tags
        # gets a higher TF score, which is correct behaviour: if "spicy" is in
        # both prose and the curated tag list, it is more relevant than if it
        # appears in prose alone.
        self.corpus = []
        for item in menu_items:
            tokens = (
                item.name.lower().split()
                + item.description.lower().split()
                + [tag.lower() for tag in item.tags]
                + [item.sku.lower()]
            )
            self.corpus.append(tokens)

        self.bm25 = BM25Okapi(self.corpus)

    def search(self, query: str, n: int = 3) -> List[str]:
        """
        Returns SKUs ranked by BM25 keyword relevance.

        Only items with a positive score are returned — a score of 0 means
        none of the query tokens appeared in that item's corpus document.
        """
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked = sorted(zip(self.items, scores), key=lambda x: x[1], reverse=True)
        return [item.sku for item, score in ranked if score > 0]

    def score_all(self, query: str) -> List[tuple]:
        """
        Returns (MenuItemSnapshot, float) pairs for ALL items, sorted by score
        descending. Unlike search(), this returns items with score=0 too, and
        exposes raw scores so the caller can apply their own threshold.

        Used by context population logic to distinguish truly matching items
        from items that merely share common words like "pizza" or "burger".
        BM25's IDF component naturally down-weights tokens that appear in many
        items (e.g. "pizza" when half the menu is pizza) and up-weights rare
        discriminating tokens (e.g. "truffle", "margherita", "heineken").

        This makes context population menu-agnostic — it works correctly
        whether the menu has 5 items or 500, and whether items have similar
        or distinct names.
        """
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked = sorted(zip(self.items, scores), key=lambda x: x[1], reverse=True)
        return ranked