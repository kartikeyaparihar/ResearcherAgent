from __future__ import annotations

from typing import Optional

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import Tool

from ..config import AppConfig


def build_web_search_tool(config: AppConfig) -> Tool:
    tavily = TavilySearchResults(
        max_results=5,
        include_answer=True,
        include_raw_content=False,
    )

    return Tool(
        name="web_research",
        description=(
            "Search the web for up-to-date information about technology topics, "
            "including documentation, Medium articles, blogs, and news. "
            "Always use this when you need current or multi-source information."
        ),
        func=tavily.run,
    )


