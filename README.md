### 🔹 Suggested Project Name

**StorySpark AI**
(short, catchy, and communicates that the app *sparks ideas for stories with AI assistance* — without referencing GoodSeeker)

---

### 🔹 README.md (GitHub-ready)

````markdown
# StorySpark AI ✨

AI-powered assistant that helps teams **capture better workplace stories**.  
Instead of writing for you, it provides **live suggestions, title ideas, and personalized recommendations** to make storytelling easier and more impactful.

---

## 🚀 Features
- **Inline Incident Suggestions**  
  While typing a story, get real-time prompts (e.g., “Highlight the collaboration angle”).
  
- **Brainstorming Mode**  
  Generate incident ideas separately for inspiration before writing.

- **AI Title Suggestions**  
  Get 3–5 catchy titles from your draft (offline heuristics or OpenAI GPT if enabled).

- **Story Recommender (Chatbot Beta)**  
  Ask which stories to read and receive recommendations based on past entries.

- **Personalization**  
  Role-based themes (Manager, HR, Customer Success, Engineering, Sales, New Hire) with matching stories.

- **Insights & Automation**  
  See tag frequency, average story length, and simulated weekly digest summaries.

---

## 📦 Installation

Clone the repo:
```bash
git clone https://github.com/YOUR-USERNAME/storyspark-ai.git
cd storyspark-ai
````

Create a virtual environment (Python 3.10 or 3.11 recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('vader_lexicon')"
```

---

## ▶️ Run the App

From the project root:

```bash
python -m streamlit run app/streamlit_app.py
```

---

## 🔑 Optional: Enable LLM Mode

For more natural title suggestions and chatbot answers, add your OpenAI API key:

```bash
# macOS/Linux
export OPENAI_API_KEY=sk-...

# Windows PowerShell
setx OPENAI_API_KEY "sk-..."
```

---

## 📂 Project Structure

```
storyspark-ai/
├── app/
│   ├── core/              # NLP + storage + optional LLM utilities
│   ├── streamlit_app.py   # Main Streamlit interface
├── data/
│   └── stories.jsonl      # Example seed stories
├── requirements.txt
├── README.md
```

---

## 🌟 Why StorySpark AI?

* **Not a content generator** — it guides *your authentic stories* with prompts and structure.
* **Hybrid design** — works offline with heuristics, improves with OpenAI if enabled.
* **Lightweight + Extensible** — built with Streamlit and Python for quick demos and iterations.

---

## 📜 License

MIT License. Use, modify, and adapt freely.

```

---

👉 Would you like me to also create a **GitHub Issues + Project board template** (so you can show roadmap/todos), or just keep it clean with README + code?
```
