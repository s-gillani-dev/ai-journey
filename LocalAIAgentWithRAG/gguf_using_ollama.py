"""
APPROACH 2: Use Ollama with your own local GGUF model
=====================================================

In this approach, we:
1. Download a GGUF model (e.g. Llama-3.2-3B-Instruct-Q4_K_M.gguf).
2. Register it inside Ollama so we can call it as a model.
3. Use LangChain's OllamaLLM wrapper to connect to Ollama.

------------------------------------------------------
🔹 STEP 1 — Download the model (from HuggingFace)
------------------------------------------------------
Run this in your terminal inside `models/` directory:

    huggingface-cli download bartowski/Llama-3.2-3B-Instruct-GGUF \
      --include "Llama-3.2-3B-Instruct-Q4_K_M.gguf" \
      --local-dir .

This will download the quantized `.gguf` file locally.

------------------------------------------------------
🔹 STEP 2 — Create a Modelfile for Ollama
------------------------------------------------------
Inside your project root, create a file named `Modelfile`:

    FROM ./models/Llama-3.2-3B-Instruct-Q4_K_M.gguf

------------------------------------------------------
🔹 STEP 3 — Register the model in Ollama
------------------------------------------------------
Run this command to create a model inside Ollama named `llama3.2-3b-instruct`:

    ollama create llama3.2-3b-instruct -f Modelfile

✅ Now Ollama knows about your local GGUF model.

------------------------------------------------------
🔹 STEP 4 — Run this Python file
------------------------------------------------------
Start the Python app:

    python main_ollama_local.py

Now you can chat with your local GGUF model through Ollama.
"""

# === Imports ===
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

# === Initialize Ollama with our locally registered model ===
# Model name must match the one used in "ollama create"
model = OllamaLLM(model="llama3.2-3b-instruct", streaming=True)

# === Prompt template ===
template = """
You are an expert in answering questions about a pizza restaurant.

Here are some relevant reviews (summarized if too long):
{reviews}

Here is the question to answer:
{question}
"""
prompt = ChatPromptTemplate.from_template(template)

# === Chain: combine prompt + model ===
chain = prompt | model

# === Interactive loop ===
while True:
    question = input("\nAsk your question (q to quit): ").strip()
    if question.lower() in {"q", "quit"}:
        print("👋 Exiting...")
        break

    if not question:
        print("⚠️ Please enter a valid question.")
        continue

    # Retrieve top reviews related to the question
    reviews = retriever.invoke(question)

    # Stream model output token by token
    print("\n🤖 Answer:")
    for token in chain.stream({"reviews": reviews, "question": question}):
        print(token, end="", flush=True)
    print("\n")  # line break after answer
