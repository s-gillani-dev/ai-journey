#!/usr/bin/env python3
"""
Parse NexarAI_Knowledge_Base.docx, chunk it, and store in ChromaDB.
Run once before starting the server: python3 ingest.py
"""
from pathlib import Path
import docx
import chromadb

DOCX_PATH = Path(__file__).parent.parent / "public" / "NexarAI_Knowledge_Base.docx"
CHROMA_PATH = Path(__file__).parent / "chroma_db"
CHUNK_SIZE = 700  # characters before splitting a chunk


def is_heading(para) -> bool:
    style = (para.style.name or "").lower() if para.style else ""
    text = para.text.strip()
    return (
        "heading" in style
        or style == "title"
        or (len(text) < 90 and text and text[0].isdigit() and "." in text[:6])
    )


def chunk_document(path: Path) -> list[dict]:
    doc = docx.Document(str(path))
    chunks: list[dict] = []
    current_heading = "Overview"
    current_text = ""

    def flush():
        nonlocal current_text
        t = current_text.strip()
        if t:
            chunks.append(
                {
                    "id": f"chunk_{len(chunks)}",
                    "heading": current_heading,
                    "text": t,
                }
            )
        current_text = ""

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if is_heading(para):
            flush()
            current_heading = text
            current_text = text + "\n"
        else:
            current_text += text + "\n"
            if len(current_text) >= CHUNK_SIZE:
                flush()
                # Carry heading context into the next chunk
                current_text = current_heading + " (continued)\n"

    flush()
    return chunks


def main():
    print(f"Reading: {DOCX_PATH}")
    if not DOCX_PATH.exists():
        raise FileNotFoundError(f"Document not found: {DOCX_PATH}")

    chunks = chunk_document(DOCX_PATH)
    print(f"Created {len(chunks)} chunks")

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    try:
        client.delete_collection("nexarai_kb")
        print("Cleared existing collection")
    except Exception:
        pass

    collection = client.create_collection("nexarai_kb")
    collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"heading": c["heading"]} for c in chunks],
        ids=[c["id"] for c in chunks],
    )

    print(f"Stored {len(chunks)} chunks in {CHROMA_PATH}")
    print("Ingest complete — run server.py to start the search API.")


if __name__ == "__main__":
    main()
