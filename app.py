from __future__ import annotations

import os
import argparse
import sys

_env_backup_app = {}
for key in ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'ANTHROPIC_API_KEY']:
    if key in os.environ:
        _env_backup_app[key] = os.environ[key]
        del os.environ[key]

from rich.console import Console
from rich.panel import Panel

from .agents.research_crew import run_research_flow
from .config import load_config
from .knowledge.repository import KnowledgeRepository


console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Autonomous Technology Researcher Agent (LangChain + CrewAI + Groq)",
    )
    parser.add_argument(
        "query",
        type=str,
        help="Technology research question or topic (in quotes).",
    )

    args = parser.parse_args(argv)
    query: str = args.query

    console.print(Panel.fit(f"[bold cyan]Query[/bold cyan]: {query}"))

    try:
        config = load_config()
    except Exception as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        return 1

    repo = KnowledgeRepository(config)

    console.print("[bold green]Running autonomous research crew...[/bold green]")
    result = run_research_flow(config, query, repo)

    console.print("\n[bold green]Final report:[/bold green]\n")
    console.print(result["report"])
    console.print(
        f"\n[bold blue]Saved to knowledge base:[/bold blue] {result['report_path']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


