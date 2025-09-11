"""
APPROACH 3: Use Ollama official hub model
(You pulled it via `ollama pull llama3.2`)
"""

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

# Directly use official Ollama model
model = OllamaLLM(model="llama3.2", streaming=True)

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
