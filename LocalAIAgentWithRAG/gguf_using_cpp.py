"""
APPROACH 1: First download and then Run GGUF model directly with LlamaCpp (no Ollama)
"""

from langchain_community.llms import LlamaCpp
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

# Directly use the GGUF file in ./models
model = LlamaCpp(
    model_path="./models/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=8,
    streaming=True
)

template = """
You are an expert in answering questions about a pizza restaurant.
Reviews: {reviews}
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    question = input("\nAsk your question (q to quit): ").strip()
    if question.lower() in {"q", "quit"}: break
    reviews = retriever.invoke(question)
    print("\n🤖 Answer:")
    for token in chain.stream({"reviews": reviews, "question": question}):
        print(token, end="", flush=True)
    print()
