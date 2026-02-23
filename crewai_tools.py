from __future__ import annotations

import glob
import os
from typing import List, Type

import pandas as pd
from pydantic import BaseModel, Field

from crewai.tools import BaseTool

from ..config import AppConfig


class WebResearchArgs(BaseModel):
    query: str = Field(..., description="The search query to look up on the web.")


class WebResearchTool(BaseTool):
    name: str = "web_research"
    description: str = (
        "Search the web for up-to-date information about technology topics, including "
        "documentation, Medium articles, blogs, and news. "
        "Use this to gather multiple sources."
    )
    args_schema: Type[BaseModel] = WebResearchArgs

    def __init__(self, config: AppConfig):
        super().__init__()
        self._api_key = config.tavily_api_key

    def _run(self, query: str) -> str:
        if not self._api_key:
            return (
                "TAVILY_API_KEY is not set. Add it to your .env to enable web search.\n"
                "Example:\n"
                "TAVILY_API_KEY=your_key_here"
            )

        from tavily import TavilyClient

        client = TavilyClient(api_key=self._api_key)
        data = client.search(
            query=query,
            max_results=6,
            include_answer=True,
            include_raw_content=False,
        )

        lines: List[str] = [f"## Web research results for: {query}", ""]
        answer = data.get("answer")
        if answer:
            lines.append("### Quick answer (from search tool)")
            lines.append(answer)
            lines.append("")

        results = data.get("results", []) or []
        lines.append("### Sources")
        for i, r in enumerate(results, start=1):
            title = r.get("title") or "Untitled"
            url = r.get("url") or ""
            content = (r.get("content") or "").strip()
            lines.append(f"{i}. {title}")
            if url:
                lines.append(f"   - URL: {url}")
            if content:
                # Keep it short so it fits context windows
                snippet = content[:600] + ("…" if len(content) > 600 else "")
                lines.append(f"   - Snippet: {snippet}")
        lines.append("")

        return "\n".join(lines)


class KaggleOverviewArgs(BaseModel):
    query: str = Field(..., description="User query to help decide which datasets matter.")


class KaggleDatasetsOverviewTool(BaseTool):
    name: str = "kaggle_datasets_overview"
    description: str = (
        "Inspect locally stored Kaggle datasets (CSV/Parquet) to extract schema and sample rows. "
        "Use this for quantitative or structured context relevant to the user's question."
    )
    args_schema: Type[BaseModel] = KaggleOverviewArgs

    def __init__(self, config: AppConfig):
        super().__init__()
        self._base_dir = config.kaggle_data_dir

    def _run(self, query: str) -> str:
        base_dir = self._base_dir
        if not os.path.isdir(base_dir):
            return f"No Kaggle data directory found at {base_dir}."

        patterns = ["**/*.csv", "**/*.parquet"]
        files: List[str] = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(base_dir, pattern), recursive=True))

        if not files:
            return f"No CSV or Parquet files found under {base_dir}."

        lines: List[str] = [
            f"## Kaggle dataset inspection for query: {query}",
            f"Base directory: {base_dir}",
            f"Found {len(files)} file(s).",
            "",
        ]

        max_files = 3
        for i, path in enumerate(files[:max_files]):
            rel = os.path.relpath(path, base_dir)
            lines.append(f"### File {i+1}: {rel}")
            try:
                if path.endswith(".csv"):
                    df = pd.read_csv(path, nrows=50)
                else:
                    df = pd.read_parquet(path)
            except Exception as exc:  # pragma: no cover
                lines.append(f"  Could not read file due to error: {exc}")
                lines.append("")
                continue

            lines.append(
                f"  Shape (loaded sample): {df.shape[0]} rows x {df.shape[1]} columns"
            )
            lines.append(f"  Columns: {', '.join(df.columns.astype(str)[:30])}")
            lines.append("  Sample rows:")
            lines.append(df.head(5).to_markdown(index=False))
            lines.append("")

        lines.append(
            "Use these datasets as quantitative or contextual background where relevant. "
            "Do not fabricate numeric results."
        )
        return "\n".join(lines)


def build_crewai_tools(config: AppConfig) -> list[BaseTool]:
    return [WebResearchTool(config), KaggleDatasetsOverviewTool(config)]

