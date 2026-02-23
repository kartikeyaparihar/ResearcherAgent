from __future__ import annotations

import os

_env_backup_llm = {}
for key in ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'ANTHROPIC_API_KEY']:
    if key in os.environ:
        _env_backup_llm[key] = os.environ[key]
        del os.environ[key]

from crewai import LLM

from .config import AppConfig


def build_crewai_llm(config: AppConfig, temperature: float = 0.2):
    if not config.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is required. "
            "Get a FREE key at: https://console.groq.com/keys"
        )

    os.environ['GROQ_API_KEY'] = config.groq_api_key

    model_string = f"groq/{config.groq_model}" if not config.groq_model.startswith("groq/") else config.groq_model

    return LLM(
        model=model_string,
        temperature=temperature,
    )


