# 📖 Brochure & Web Content Summarization  

This project demonstrates multiple approaches to **scraping website content** and using **LLMs (OpenAI / Ollama)** to automatically generate **summaries** and **company brochures**.  

It contains three Jupyter notebooks, each implementing a specific workflow.  

---

## 📂 Project Structure  

- **`web_content_summarize.ipynb`**  
  Scrapes website content (ignoring scripts, styles, and images) and generates a **short Markdown summary**.  

- **`web_content_with_links.ipynb`**  
  Scrapes **content + links**, filters relevant ones (About, Careers, Products, Contact), and returns structured **JSON** for brochure generation.  

- **`brochure_generator.ipynb`**  
  End-to-end **brochure generation workflow**:  
  - Scrape landing page + relevant links  
  - Pass content to LLM (OpenAI/Ollama)  
  - Generate an **engaging Markdown brochure** in multiple languages  

---

## ⚙️ Requirements  

- Python **3.9+**  
- Jupyter Notebook  
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)  
- [requests](https://pypi.org/project/requests/)  
- [python-dotenv](https://pypi.org/project/python-dotenv/)  
- [OpenAI Python SDK](https://pypi.org/project/openai/)  
- [Ollama](https://ollama.com) (for local LLMs)  

---

## 🚀 Setup & Installation  

1. **Clone this repository**  
   ```bash
   git clone https://github.com/s-gillani-dev/ai-journey.git
   cd BrouchureAndSummaryGeneration
   ```

2. **Create a virtual environment**  
   ```bash
   python -m venv venv
   ```

3. **Activate the environment**  
   - **Linux / macOS**  
     ```bash
     source venv/bin/activate
     ```
   - **Windows**  
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**  
   Create a `.env` file in the project root and add:  
   ```env
   OPENAI_API_KEY=sk-xxxx
   ```

6. **Run Jupyter Notebook**  
   ```bash
   jupyter notebook
   ```

---

## 🧠 Features  

- ✅ Scrape website **text + links**  
- ✅ Automatic **summarization** using LLMs  
- ✅ **Brochure generation** in Markdown format  
- ✅ Works with **OpenAI GPT models** or **Ollama local models**  
- ✅ Supports **multi-language output**  

---

## 📸 Workflow Overview  

1. **Scraping** → Extract website text & links  
2. **Link Filtering** → Select only relevant links (About, Careers, Products, Contact)  
3. **Content Aggregation** → Gather text from selected pages  
4. **Brochure Generation** → LLM creates a **fun, engaging brochure**  

---

## 📄 License  

This project is licensed under the **MIT License**.  
Feel free to use, modify, and distribute.  
