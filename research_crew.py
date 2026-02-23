from __future__ import annotations

import os
from typing import Dict, Any

_env_backup_global = {}
for key in ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'ANTHROPIC_API_KEY']:
    if key in os.environ:
        _env_backup_global[key] = os.environ[key]
        del os.environ[key]

from crewai import Agent, Crew, Process, Task

from ..config import AppConfig
from ..knowledge.repository import KnowledgeRepository
from ..llm import build_crewai_llm
from ..tools.crewai_tools import build_crewai_tools


def build_research_crew(config: AppConfig, repository: KnowledgeRepository) -> Crew:
    llm = build_crewai_llm(config)
    tools = build_crewai_tools(config)

    researcher = Agent(
        role="Technology Researcher",
        goal=(
            "Conduct deep, multi-source research on technology topics, "
            "using the web and Kaggle datasets to gather accurate and current information."
        ),
        backstory=(
            "You are an experienced technology analyst. You know how to combine "
            "documentation, credible blogs, Medium articles, Kaggle datasets, and news "
            "to form a nuanced understanding of modern tech trends."
        ),
        llm=llm,
        tools=tools,
        verbose=True,
        allow_delegation=False,
    )

    writer = Agent(
        role="Research Synthesizer & Writer",
        goal=(
            "Transform raw research notes into a concise, well-structured markdown "
            "report with clear sections, bullet points, and practical insights."
        ),
        backstory=(
            "You are a senior technical writer who specializes in summarizing complex "
            "technology research into clear, actionable insights for engineers and "
            "decision makers."
        ),
        llm=llm,
        tools=[],
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description=(
            "Given the user's technology research query:\n"
            "1. Use the web_research tool to gather current information from multiple sources, "
            "   including docs, blogs, Medium articles, and news.\n"
            "2. Use the kaggle_datasets_overview tool to inspect available Kaggle datasets that "
            "   might provide quantitative or contextual backing.\n"
            "3. Produce detailed research notes that include references to the sources you used, "
            "   key findings, trade-offs, and any important metrics or data.\n"
        ),
        expected_output=(
            "Structured research notes in markdown with sections for: Sources, Key Findings, "
            "Data Insights (from Kaggle), Risks/Limitations, and Open Questions."
        ),
        agent=researcher,
    )

    writing_task = Task(
        description=(
            "Take the research notes produced by the Technology Researcher and craft a final "
            "markdown report tailored to a technology audience. The report should:\n"
            "- Start with a brief executive summary.\n"
            "- Include clear headings and bullet points.\n"
            "- Highlight the most important insights, data points, and trade-offs.\n"
            "- Suggest practical actions or next steps where appropriate.\n"
        ),
        expected_output=(
            "A polished markdown report ready to be saved in the knowledge repository."
        ),
        agent=writer,
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew


def run_research_flow(config: AppConfig, query: str, repository: KnowledgeRepository) -> Dict[str, Any]:
    try:
        crew = build_research_crew(config, repository)
        result = crew.kickoff(inputs={"topic": query})
        final_report = str(result)
        saved_path = repository.save_entry(query=query, summary_markdown=final_report)
        return {"report_path": str(saved_path), "report": final_report, "success": True}
    except Exception as e:
        error_msg = str(e)

        if "GROQ_API_KEY" in error_msg or "Error importing" in error_msg:
            helpful_msg = (
                "## ⚠️ Groq API Key Error\n\n"
                "Your Groq API key is missing or invalid.\n\n"
                "### 🟢 Fix Steps:\n\n"
                "1. **Get FREE Groq key**: https://console.groq.com/keys\n"
                "2. **Sign up** (free, no credit card needed)\n"
                "3. **Create API key** (starts with `gsk_...`)\n"
                "4. **Update `.env` file**:\n"
                "   ```env\n"
                "   GROQ_API_KEY=gsk_your_actual_key_here\n"
                "   ```\n"
                "5. **Restart** Streamlit\n"
                "6. **Done!** 🎉\n\n"
                f"**Technical Error**: {error_msg[:500]}"
            )
            return {
                "success": False,
                "error": helpful_msg,
                "error_type": "api_key_error"
            }

        elif "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            helpful_msg = (
                "## ⚠️ API Quota Error\n\n"
                "You've exceeded your Groq API quota (free tier limits).\n\n"
                "### 🟢 Solutions:\n\n"
                "1. **Wait a few minutes** and try again (rate limits reset)\n"
                "2. **Check your usage**: https://console.groq.com/\n"
                "3. **Upgrade to paid tier** if needed: https://console.groq.com/\n\n"
                f"**Technical Error**: {error_msg[:500]}"
            )
            return {
                "success": False,
                "error": helpful_msg,
                "error_type": "quota_error"
            }
        else:
            return {
                "success": False,
                "error": f"An error occurred: {error_msg}",
                "error_type": "general_error"
            }
