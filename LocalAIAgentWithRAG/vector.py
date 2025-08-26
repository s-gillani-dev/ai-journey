from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# Path for Chroma vector DB
db_location = "./chrome_langchain_db"

# Use a lighter embedding model if you want faster response
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# Check if database already exists
add_documents = not os.path.exists(db_location)

if add_documents:
    print("📌 No existing DB found — generating embeddings (this may take time)...")
    df = pd.read_csv("realistic_restaurant_reviews.csv")
    documents = []
    ids = []

    for i, row in df.iterrows():
        document = Document(
            page_content=f"{row['Title']} {row['Review']}",
            metadata={"rating": row["Rating"], "date": row["Date"]},
            id=str(i)
        )
        ids.append(str(i))
        documents.append(document)

    vector_store = Chroma(
        collection_name="restaurant_reviews",
        persist_directory=db_location,
        embedding_function=embeddings
    )
    vector_store.add_documents(documents=documents, ids=ids)
    print("✅ Embeddings created and stored in Chroma DB.")
else:
    print("✅ Using existing Chroma DB.")
    vector_store = Chroma(
        collection_name="restaurant_reviews",
        persist_directory=db_location,
        embedding_function=embeddings
    )

# Use fewer docs for faster retrieval
retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}
)
