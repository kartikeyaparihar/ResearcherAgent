## Autonomous Technology Researcher Agent

This project is an LLM-powered **autonomous technology researcher** built with **Python**, **LangChain**, **CrewAI**, **Groq**, and **LiteLLM**.  
It can:

- **Accept a user query** about technology topics
- **Autonomously research the web** using integrated search tools (Tavily)
- **Leverage Kaggle datasets** (CSV/Parquet) as structured background data
- **Pull and analyze Medium articles** as part of web research
- **Synthesize findings** into a structured summary
- **Persist the final report** into a simple text/markdown knowledge repository for future reference

### 1. Setup

1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key   # optional but recommended
KNOWLEDGE_BASE_DIR=knowledge_base_store
KAGGLE_DATA_DIR=./kaggle_data        # where you download Kaggle datasets locally
```

**Get FREE Groq API key**: https://console.groq.com/keys (no billing needed!)

> You must separately download any Kaggle datasets you want to use (via Kaggle UI or API) into `KAGGLE_DATA_DIR`.

### 2. Running the agent

#### Option A: Streamlit Web Interface (Recommended) 🎨

Launch the beautiful web interface:

```bash
# Windows
run_streamlit.bat

# Linux/Mac
chmod +x run_streamlit.sh
./run_streamlit.sh

# Or manually:
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501` and use the interactive UI!

#### Option B: Command Line Interface

```bash
python -m src.app "impact of LLM-based agents on MLOps tooling in 2025"
```

The system will:

1. Use a **Researcher** agent (CrewAI + LangChain tools) with Gemini to search the web (Tavily) and inspect any relevant Kaggle CSVs.
2. Use a **Writer**/Synthesizer agent to structure the findings.
3. Write a timestamped markdown report into the configured knowledge base directory.

### 3. Kaggle and Medium integration

- **Kaggle**: Place downloaded CSV/Parquet files into `KAGGLE_DATA_DIR`. The agent will scan metadata, basic statistics, and sampled rows to enrich its technology research.
- **Medium**: Medium articles are discovered via the **web search tool** (Tavily/LLM-based search). The researcher agent will fetch and parse article content to use as part of its multi-source synthesis.

### 4. Project layout

- `streamlit_app.py` – **Streamlit web frontend** (beautiful UI)
- `src/config.py` – configuration and environment handling
- `src/llm.py` – Gemini model setup for LangChain and CrewAI
- `src/tools/web_search_tool.py` – Tavily/LLM-based web search tools
- `src/tools/kaggle_dataset_tool.py` – simple loader/inspector for Kaggle datasets
- `src/knowledge/repository.py` – text-based knowledge repository writer/reader
- `src/agents/research_crew.py` – CrewAI-based multi-agent definition (researcher + writer)
- `src/app.py` – CLI entry point to run the autonomous researcher

### 5. Features

✨ **Modern Streamlit Frontend**:
- Beautiful, gradient-based UI design
- Interactive research interface
- Knowledge base browser with search
- Settings and system status
- Download reports as Markdown

🔧 **Error Handling**:
- Graceful quota error messages with helpful fix guides
- Clear error reporting for API issues
- User-friendly error displays


