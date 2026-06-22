# # final working version for step 1-4
# # aiva/tools/search/vector.py
# from typing import List
# from aiva.state_machine.types import MenuItemSnapshot
# import numpy as np

# # POC vector embeddings for menu items (replace with real embeddings later)
# def vectorize(text: str) -> np.ndarray:
#     """
#     Simple vectorizer: maps string to vector via character ordinals (POC)
#     """
#     vec = np.zeros(26)
#     for c in text.lower():
#         if 'a' <= c <= 'z':
#             vec[ord(c) - ord('a')] += 1
#     # normalize vector
#     norm = np.linalg.norm(vec)
#     return vec / (norm + 1e-8)

# def vector_search(query: str, menu_items: List[MenuItemSnapshot]) -> List[MenuItemSnapshot]:
#     """
#     Returns items sorted by cosine similarity between query and item name vectors
#     """
#     query_vec = vectorize(query)

#     def similarity(item: MenuItemSnapshot) -> float:
#         item_vec = vectorize(item.name)
#         return float(np.dot(query_vec, item_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(item_vec) + 1e-8))

#     return sorted(menu_items, key=similarity, reverse=True)






# # DineFlow/tools/search/vector.py
# import chromadb
# from chromadb.utils import embedding_functions
# from typing import List
# from state_machine.types import MenuItemSnapshot

# # 1. Local Embeddings (Fast & No Cost)
# local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# # 2. Persistent Client (Saves to disk)
# client = chromadb.PersistentClient(path="./chroma_db")

# # 3. Create Collections
# menu_coll = client.get_or_create_collection("menu", embedding_function=local_ef)
# memory_coll = client.get_or_create_collection("memory", embedding_function=local_ef)

# def sync_menu_to_vector(menu_items: List[MenuItemSnapshot]):
#     """Syncs the current registry to ChromaDB, ensuring unique IDs to prevent DuplicateIDError."""
#     # Deduplicate items by SKU using a dictionary
#     unique_map = {item.sku: item for item in menu_items}
#     unique_items = list(unique_map.values())

#     ids = [item.sku for item in unique_items]
#     docs = [f"{item.name} {item.sku}" for item in unique_items]
#     metadatas = [{"sku": item.sku} for item in unique_items]
    
#     # upsert handles both creation and updates
#     menu_coll.upsert(ids=ids, documents=docs, metadatas=metadatas)

# def vector_search(query: str, n_results: int = 3) -> List[str]:
#     """Returns top-k SKUs based on semantic similarity."""
#     results = menu_coll.query(query_texts=[query], n_results=n_results)
#     return results['ids'][0] if results['ids'] else []

# # def save_memory(session_id: str, agent_name: str, user_in: str, aiva_out: str):
# #     """Saves a turn into the vector memory with unique nanosecond IDs."""
# #     import time
# #     import uuid

# #     unique_suffix = str(uuid.uuid4())[:4]
# #     turn_id = f"{session_id}_{time.time_ns()}_{unique_suffix}"
    
# #     memory_coll.add(
# #         ids=[turn_id],
# #         documents=[f"[{agent_name}] User: {user_in}\n[{agent_name}] DineFlow: {aiva_out}"],
# #         metadatas=[{
# #             "session_id": session_id,
# #             "agent": agent_name
# #         }]
# #     )

# def save_memory(
#     session_id: str,
#     agent_name: str,
#     user_in: str,
#     aiva_out: str,
#     meta: dict | None = None
# ):
#     """Saves a turn into the vector memory with unique nanosecond IDs."""
#     import time
#     import uuid

#     unique_suffix = str(uuid.uuid4())[:4]
#     turn_id = f"{session_id}_{time.time_ns()}_{unique_suffix}"

#     # Base metadata (always present)
#     metadata = {
#         "session_id": session_id,
#         "agent": agent_name
#     }

#     # 🆕 Merge optional orchestration metadata
#     if meta and isinstance(meta, dict):
#         metadata.update(meta)

#     memory_coll.add(
#         ids=[turn_id],
#         documents=[
#             f"[{agent_name}] User: {user_in}\n[{agent_name}] DineFlow: {aiva_out}"
#         ],
#         metadatas=[metadata]
#     )


# def retrieve_memories(session_id: str, query: str, n: int = 2) -> List[str]:
#     """Retrieves relevant past turns for this specific session."""
#     results = memory_coll.query(
#         query_texts=[query],
#         where={"session_id": session_id},
#         n_results=n
#     )
#     return results['documents'][0] if results['documents'] else []



# claud recent version testing....

# DineFlow/tools/search/vector.py
# import chromadb
# from chromadb.utils import embedding_functions
# from typing import List
# from state_machine.types import MenuItemSnapshot

# # 1. Local Embeddings (Fast & No Cost)
# local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# # 2. Persistent Client (Saves to disk)
# client = chromadb.PersistentClient(path="./chroma_db")

# # 3. Create Collections
# menu_coll = client.get_or_create_collection("menu", embedding_function=local_ef)
# memory_coll = client.get_or_create_collection("memory", embedding_function=local_ef)


# def sync_menu_to_vector(menu_items: List[MenuItemSnapshot]):
#     """
#     Syncs the current registry to ChromaDB.

#     ── Embedding Document Structure (v2) ─────────────────────────────────────
#     v1 (old): f"{item.name} {item.sku}"
#       Only the name and SKU were embedded. The vector space had no concept of
#       "spicy", "vegetarian", or any other attribute. Semantic queries like
#       "anything spicy?" found no meaningful neighbours.

#     v2 (new): Structured prose covering name, description, and tags.
#       The embedding model reads full sentences and encodes semantic meaning.
#       "spicy" in the query now maps close to "spicy pepperoni" in the embedding
#       space, so vector_search returns PZ-PEP as a top result.

#     Tag formatting: Tags are joined as a comma-separated phrase rather than
#     space-separated tokens. This produces better embeddings because sentence
#     transformers are trained on natural language — "Tags: spicy, hot, classic"
#     reads as a coherent phrase, while "spicy hot classic" reads as noise.

#     Deduplication: upsert by SKU prevents DuplicateIDError on re-sync.
#     """
#     unique_map = {item.sku: item for item in menu_items}
#     unique_items = list(unique_map.values())

#     ids = [item.sku for item in unique_items]

#     # Enriched documents: name + description + tags
#     docs = [
#         f"Name: {item.name}. {item.description} Tags: {', '.join(item.tags)}."
#         for item in unique_items
#     ]

#     # Metadata kept minimal — only what downstream filters need
#     metadatas = [{"sku": item.sku, "name": item.name} for item in unique_items]

#     menu_coll.upsert(ids=ids, documents=docs, metadatas=metadatas)


# def vector_search(query: str, n_results: int = 3) -> List[str]:
#     """Returns top-k SKUs based on semantic similarity."""
#     results = menu_coll.query(query_texts=[query], n_results=n_results)
#     return results['ids'][0] if results['ids'] else []


# def save_memory(
#     session_id: str,
#     agent_name: str,
#     user_in: str,
#     aiva_out: str,
#     meta: dict | None = None
# ):
#     """Saves a turn into the vector memory with unique nanosecond IDs."""
#     import time
#     import uuid

#     unique_suffix = str(uuid.uuid4())[:4]
#     turn_id = f"{session_id}_{time.time_ns()}_{unique_suffix}"

#     metadata = {
#         "session_id": session_id,
#         "agent": agent_name
#     }

#     if meta and isinstance(meta, dict):
#         metadata.update(meta)

#     memory_coll.add(
#         ids=[turn_id],
#         documents=[
#             f"[{agent_name}] User: {user_in}\n[{agent_name}] DineFlow: {aiva_out}"
#         ],
#         metadatas=[metadata]
#     )


# def retrieve_memories(session_id: str, query: str, n: int = 2) -> List[str]:
#     """Retrieves relevant past turns for this specific session."""
#     results = memory_coll.query(
#         query_texts=[query],
#         where={"session_id": session_id},
#         n_results=n
#     )
#     return results['documents'][0] if results['documents'] else []



# DineFlow/tools/search/vector.py
import chromadb
from chromadb.utils import embedding_functions
from typing import List
from state_machine.types import MenuItemSnapshot

# 1. Local Embeddings (Fast & No Cost)
local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 2. Persistent Client (Saves to disk)
client = chromadb.PersistentClient(path="./chroma_db")

# 3. Create Collections
menu_coll = client.get_or_create_collection("menu", embedding_function=local_ef)
memory_coll = client.get_or_create_collection("memory", embedding_function=local_ef)


def sync_menu_to_vector(menu_items: List[MenuItemSnapshot]):
    """
    Syncs the current registry to ChromaDB.

    Embedding Document Structure (v2):
      Structured prose covering name, description, and tags.
      "spicy" in the query maps close to "spicy pepperoni" in the embedding
      space, so vector_search returns PZ-PEP as a top result.

    Tag formatting: comma-separated phrase — sentence transformers handle
    "Tags: spicy, hot, classic" better than "spicy hot classic" as noise.

    Deduplication: upsert by SKU prevents DuplicateIDError on re-sync.
    """
    unique_map = {item.sku: item for item in menu_items}
    unique_items = list(unique_map.values())

    ids = [item.sku for item in unique_items]

    docs = [
        f"Name: {item.name}. {item.description} Tags: {', '.join(item.tags)}."
        for item in unique_items
    ]

    metadatas = [{"sku": item.sku, "name": item.name} for item in unique_items]

    menu_coll.upsert(ids=ids, documents=docs, metadatas=metadatas)


def vector_search(query: str, n_results: int = 3) -> List[str]:
    """Returns top-k SKUs based on semantic similarity."""
    results = menu_coll.query(query_texts=[query], n_results=n_results)
    return results['ids'][0] if results['ids'] else []


def _sanitize_metadata(meta: dict) -> dict:
    """
    Converts a metadata dict to ChromaDB-compatible values.

    ChromaDB only accepts str, int, float, and bool as metadata values.
    Anything else — enums, None, nested dicts, lists — causes:
        "Cannot convert Python object to MetadataValue"

    Rules:
        None         → dropped (absent key is cleaner than a null string)
        bool         → kept as-is (checked before int — bool is int subclass)
        int / float  → kept as-is
        str          → kept as-is
        Enum         → str(value.value) using the enum's own string value
        everything else → str() as a safe fallback
    """
    sanitized = {}
    for key, value in meta.items():
        if value is None:
            continue
        elif isinstance(value, bool):
            sanitized[key] = value
        elif isinstance(value, (int, float)):
            sanitized[key] = value
        elif isinstance(value, str):
            sanitized[key] = value
        elif hasattr(value, "value"):
            # Enum — .value is already the underlying str/int
            sanitized[key] = str(value.value)
        else:
            sanitized[key] = str(value)
    return sanitized


def save_memory(
    session_id: str,
    agent_name: str,
    user_in: str,
    dine_flow: str,
    meta: dict | None = None
):
    """Saves a turn into the vector memory with unique nanosecond IDs."""
    import time
    import uuid

    unique_suffix = str(uuid.uuid4())[:4]
    turn_id = f"{session_id}_{time.time_ns()}_{unique_suffix}"

    metadata = {
        "session_id": session_id,
        "agent": agent_name
    }

    if meta and isinstance(meta, dict):
        metadata.update(meta)

    # Sanitize before passing to ChromaDB — enums, None, and other
    # non-primitive types cause "Cannot convert Python object to MetadataValue"
    metadata = _sanitize_metadata(metadata)

    memory_coll.add(
        ids=[turn_id],
        documents=[
            f"[{agent_name}] User: {user_in}\n[{agent_name}] DineFlow: {dine_flow}"
        ],
        metadatas=[metadata]
    )


def retrieve_memories(session_id: str, query: str, n: int = 2) -> List[str]:
    """Retrieves relevant past turns for this specific session."""
    results = memory_coll.query(
        query_texts=[query],
        where={"session_id": session_id},
        n_results=n
    )
    return results['documents'][0] if results['documents'] else []