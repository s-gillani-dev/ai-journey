#!/usr/bin/env python3
"""
FastAPI RAG server — exposes POST /api/search for the Gemini Live frontend.
Start with: uvicorn server:app --port 8000 --reload
"""
from pathlib import Path
import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CHROMA_PATH = Path(__file__).parent / "chroma_db"

app = FastAPI(title="NexarAI Knowledge Base API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Initialise ChromaDB client at startup
try:
    _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    _collection = _client.get_collection("nexarai_kb")
    print(f"Loaded collection with {_collection.count()} chunks")
except Exception as e:
    _collection = None
    print(f"WARNING: ChromaDB not ready — run ingest.py first. ({e})")


class SearchRequest(BaseModel):
    query: str
    n_results: int = 4


@app.get("/health")
def health():
    ready = _collection is not None
    return {"status": "ok" if ready else "not_ready", "chunks": _collection.count() if ready else 0}


@app.post("/api/search")
def search(req: SearchRequest):
    if _collection is None:
        raise HTTPException(503, "Knowledge base not ingested yet — run ingest.py first.")

    results = _collection.query(
        query_texts=[req.query],
        n_results=min(req.n_results, _collection.count()),
    )

    docs = results["documents"][0] if results["documents"] else []
    metas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results.get("distances") else [None] * len(docs)

    return {
        "results": [
            {"heading": m.get("heading", ""), "text": d, "score": round(1 - (dist or 0), 3)}
            for d, m, dist in zip(docs, metas, distances)
        ]
    }
