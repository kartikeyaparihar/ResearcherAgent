import os
import sys
from pathlib import Path

_env_backup_streamlit = {}
for key in ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'ANTHROPIC_API_KEY']:
    if key in os.environ:
        _env_backup_streamlit[key] = os.environ[key]
        del os.environ[key]

import streamlit as st
from streamlit_option_menu import option_menu

sys.path.insert(0, str(Path(__file__).parent))

from src.config import load_config
from src.agents.research_crew import run_research_flow
from src.knowledge.repository import KnowledgeRepository


st.set_page_config(
    page_title="AI Technology Researcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    .stApp, [data-testid="stAppViewContainer"], section.main, 
    [data-testid="stHorizontalBlock"], [data-testid="block-container"] {
        background: #0a0a0a !important;
    }
    
    .main-header {
        font-family: 'Outfit', sans-serif;
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 35%, #a855f7 70%, #06b6d4 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        animation: gradient-shift 5s ease infinite;
    }
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 100% center; }
    }
    
    .sub-header {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 500;
    }
    
    .stMarkdown, .stMarkdown p, [data-testid="stVerticalBlock"] p, label {
        color: #e2e8f0 !important;
    }
    
    #MainMenu, footer {visibility: hidden;}
    
    .stButton > button {
        width: 100%;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.5) !important;
    }
    
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid rgba(99, 102, 241, 0.4) !important;
        background: rgba(30, 41, 59, 0.6) !important;
        color: #e2e8f0 !important;
        transition: all 0.3s !important;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #a5b4fc !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    [data-testid="stSidebar"] .stMarkdown { color: #e2e8f0 !important; }
    
    .hero-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .hero-card h3, .hero-card h4, .hero-card p {
        color: #e2e8f0 !important;
    }
    
    .report-container {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin: 1rem 0;
    }
    .report-container h3, .report-container p {
        color: #e2e8f0 !important;
    }
    
    .example-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        border-radius: 12px;
    }
    
    .streamlit-expanderHeader {
        border-radius: 10px;
        color: #e2e8f0 !important;
    }
    
    [data-testid="stAlert"], .stAlert {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #e2e8f0 !important;
    }
    
    code, pre {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #a5b4fc !important;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="stMarkdown"] {
        color: #e2e8f0 !important;
    }
    [data-testid="stMarkdown"] strong {
        color: #f8fafc !important;
    }
    
    [data-testid="stTextInput"] label, [data-testid="stTextArea"] label {
        color: #e2e8f0 !important;
    }
    
    .stTextInput input {
        background: rgba(30, 41, 59, 0.6) !important;
        color: #e2e8f0 !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(30, 41, 59, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)


def load_app_config():
    try:
        return load_config()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        st.info("Please make sure your `.env` file exists with GROQ_API_KEY set.")
        return None


def load_recent_reports(repository: KnowledgeRepository, limit: int = 10):
    base_dir = Path(repository._base)
    if not base_dir.exists():
        return []
    
    reports = []
    for file_path in sorted(base_dir.glob("*.md"), reverse=True)[:limit]:
        try:
            content = file_path.read_text(encoding="utf-8")
            # Extract query from filename or content
            query_match = content.split("**Query**:")[1].split("\n")[0].strip() if "**Query**:" in content else file_path.stem
            reports.append({
                "filename": file_path.name,
                "path": str(file_path),
                "query": query_match,
                "content": content[:500] + "..." if len(content) > 500 else content
            })
        except Exception:
            continue
    return reports


def main():
    st.markdown('<h1 class="main-header">🔬 AI Technology Researcher</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Autonomous Research Agent · LangChain · CrewAI · Groq</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.25rem;">🧠</div>
            <div style="font-weight: 600; color: #e2e8f0; font-size: 0.95rem;">AI Research Lab</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem;">Powered by Groq</div>
        </div>
        """, unsafe_allow_html=True)
        
        selected = option_menu(
            menu_title=None,
            options=["🔍 Research", "📚 Knowledge Base", "⚙️ Settings"],
            icons=["search", "book", "gear"],
            menu_icon="menu-down",
            default_index=0,
            styles={
                "container": {"padding": "0.5rem", "background-color": "rgba(15, 23, 42, 0.5)", "border-radius": "12px"},
                "icon": {"color": "#00d9ff", "font-size": "18px"},
                "nav-link": {"font-size": "15px", "text-align": "left", "margin": "2px 0", "padding": "0.6rem 1rem", "border-radius": "8px"},
                "nav-link-selected": {"background": "linear-gradient(135deg, #7c3aed, #6366f1)", "color": "white"},
            }
        )
    
    config = load_app_config()
    if config is None:
        st.stop()
    
    repository = KnowledgeRepository(config)
    
    if selected == "🔍 Research":
        show_research_page(config, repository)
    elif selected == "📚 Knowledge Base":
        show_knowledge_base_page(repository)
    elif selected == "⚙️ Settings":
        show_settings_page(config)


def show_research_page(config, repository: KnowledgeRepository):
    st.markdown("""
    <div class="hero-card">
        <h3 style="margin-top: 0; color: #a5b4fc;">🚀 Start Your Research</h3>
        <p style="color: #94a3b8; margin-bottom: 0; font-size: 1rem;">Ask any technology question. AI agents will search the web, analyze Kaggle data, and produce a detailed report.</p>
    </div>
    """, unsafe_allow_html=True)
    
    default_query = st.session_state.get("example_query", "")
    
    with st.form("research_form", clear_on_submit=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_area(
                "Enter your technology research question:",
                value=default_query,
                placeholder="e.g., Explain the latest trends in Generative AI for enterprises...",
                height=120,
                help="Ask any technology-related question. The AI will research the web, analyze Kaggle datasets, and generate a comprehensive report."
            )
        
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button(
                "🔍 Research",
                use_container_width=True,
                type="primary"
            )
    
    if submit_button and query:
        if "example_query" in st.session_state:
            del st.session_state["example_query"]
        if not query.strip():
            st.warning("⚠️ Please enter a research question.")
        else:
            with st.spinner("🤖 AI agents are researching... This may take 1-3 minutes."):
                result = run_research_flow(config, query, repository)
                
                if result.get("success"):
                    st.balloons()
                    st.success("✅ Research completed successfully!")
                    
                    st.markdown("---")
                    st.markdown("## 📄 Research Report")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Status", "✅ Complete", delta="Success")
                    with col2:
                        st.metric("Report Length", f"{len(result['report']):,} chars", delta="Markdown")
                    with col3:
                        st.metric("Saved To", "Knowledge Base", delta="Persisted")
                    
                    st.markdown('<div class="report-container">', unsafe_allow_html=True)
                    st.markdown("### Report Content")
                    st.markdown(result["report"])
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                    with col_dl2:
                        st.download_button(
                            label="📥 Download Report (Markdown)",
                            data=result["report"],
                            file_name=Path(result["report_path"]).name,
                            mime="text/markdown",
                            use_container_width=True,
                            type="primary"
                        )
                    
                    st.info(f"💾 Report saved to: `{result['report_path']}`")
                    
                else:
                    error_type = result.get("error_type", "general_error")
                    error_msg = result.get("error", "Unknown error")
                    
                    if error_type == "quota_error":
                        st.error("❌ API Quota Error")
                        st.markdown(error_msg)
                        st.markdown("---")
                        st.markdown("### 🔧 Quick Fix Guide")
                        st.markdown("""
                        1. Check your usage at [Groq Console](https://console.groq.com/)
                        2. Wait a few minutes for rate limits to reset
                        3. Try again or upgrade your plan if needed
                        """)
                    else:
                        st.error("❌ Error occurred")
                        st.code(error_msg)
    
    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    st.markdown("*Click to use any of these questions:*")
    example_queries = [
        "Explain the latest trends in Generative AI for enterprises",
        "Compare vector databases for semantic search systems",
        "What are the best practices for MLOps in 2025?",
        "Analyze the impact of LLM agents on software development",
        "Review cloud security trends and best practices"
    ]
    
    cols1 = st.columns(3)
    cols2 = st.columns(2)
    all_cols = cols1 + cols2
    for i, example in enumerate(example_queries):
        with all_cols[i]:
            label = f"📌 {example[:40]}{'...' if len(example) > 40 else ''}"
            if st.button(label, key=f"example_{i}", use_container_width=True):
                st.session_state.example_query = example
                st.rerun()
    
    if "example_query" in st.session_state:
        st.success(f"💡 **Pre-filled above** — adjust if needed and click Research!")


def show_knowledge_base_page(repository: KnowledgeRepository):
    st.markdown("## 📚 Knowledge Base")
    st.markdown("*Browse and search your saved research reports*")
    
    reports = load_recent_reports(repository, limit=20)
    
    if not reports:
        st.markdown("""
        <div class="hero-card">
            <h4 style="margin-top: 0; color: #a5b4fc;">📝 No reports yet</h4>
            <p style="color: #94a3b8; margin-bottom: 0;">Start a research query to build your knowledge base!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    search_term = st.text_input("🔍 Search reports", placeholder="Enter keywords to filter...", label_visibility="collapsed")
    
    filtered_reports = reports
    if search_term:
        filtered_reports = [
            r for r in reports
            if search_term.lower() in r["query"].lower() or search_term.lower() in r["content"].lower()
        ]
    
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Total Reports", len(reports), delta=None)
    with m2:
        st.metric("Filtered Results", len(filtered_reports), delta=None)
    
    for idx, report in enumerate(filtered_reports):
        with st.expander(f"📄 {report['query'][:80]}...", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Query**: {report['query']}")
                st.markdown(f"**File**: `{report['filename']}`")
            
            with col2:
                if st.button("📖 View Full", key=f"view_{idx}"):
                    try:
                        full_content = Path(report['path']).read_text(encoding="utf-8")
                        st.markdown("### Full Report")
                        st.markdown(full_content)
                    except Exception as e:
                        st.error(f"Error loading report: {e}")
            
            st.markdown("---")


def show_settings_page(config):
    st.markdown("## ⚙️ Settings & Configuration")
    
    st.markdown("""
    <div class="hero-card">
        <h4 style="margin-top: 0; color: #a5b4fc;">🤖 LLM Provider</h4>
        <p style="color: #e2e8f0; margin: 0; font-size: 1.05rem;"><strong>GROQ</strong> — Free tier, very fast inference</p>
        <p style="color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Get your API key: <a href="https://console.groq.com/keys" target="_blank" style="color: #a5b4fc;">console.groq.com/keys</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔑 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        groq_status = "✅ Configured" if config.groq_api_key else "❌ Not Set"
        st.info(f"**Groq API Key**: {groq_status}")
        st.info(f"**Groq Model**: `{config.groq_model}`")
        st.info(f"**Knowledge Base**: `{config.knowledge_base_dir}`")
    
    with col2:
        st.info(f"**Kaggle Data**: `{config.kaggle_data_dir}`")
        tavily_status = "✅ Configured" if config.tavily_api_key else "❌ Not Set"
        st.info(f"**Tavily API**: {tavily_status}")
    
    st.markdown("---")
    st.markdown("### 💡 Quick Setup")
    
    with st.expander("📄 View .env template", expanded=False):
        st.code("""GROQ_API_KEY=gsk_your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
KNOWLEDGE_BASE_DIR=knowledge_base_store
KAGGLE_DATA_DIR=./kaggle_data""", language="bash")
        st.markdown("**Get FREE Groq key**: [console.groq.com/keys](https://console.groq.com/keys)")
    
    st.markdown("### 📊 System Status")
    
    kb_exists = Path(config.knowledge_base_dir).exists()
    kaggle_exists = Path(config.kaggle_data_dir).exists()
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric("Knowledge Base", "Ready" if kb_exists else "Not Found", delta="✅" if kb_exists else "❌")
    
    with status_col2:
        kb_path = Path(config.knowledge_base_dir)
        report_count = len(list(kb_path.glob("*.md"))) if kb_path.exists() else 0
        st.metric("Saved Reports", report_count)
    
    with status_col3:
        kaggle_path = Path(config.kaggle_data_dir)
        dataset_count = len(list(kaggle_path.glob("**/*.csv"))) + len(list(kaggle_path.glob("**/*.parquet"))) if kaggle_path.exists() else 0
        st.metric("Kaggle Datasets", dataset_count)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Autonomous Technology Researcher Agent**
    
    | Component | Technology |
    |-----------|------------|
    | Framework | LangChain & CrewAI |
    | LLM | Groq (free tier) |
    | Web Search | Tavily |
    | Data | Kaggle Datasets |
    
    *Built for comprehensive, autonomous technology research.*
    """)


if __name__ == "__main__":
    main()
