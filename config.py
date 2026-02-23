import os
from dataclasses import dataclass

_env_backup_config = {}
for key in ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'ANTHROPIC_API_KEY']:
    if key in os.environ:
        _env_backup_config[key] = os.environ[key]
        del os.environ[key]

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    tavily_api_key: str | None = None
    knowledge_base_dir: str = "knowledge_base_store"
    kaggle_data_dir: str = "./kaggle_data"


def load_config() -> AppConfig:
    env_backup = {}
    for key in ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY']:
        if key in os.environ:
            env_backup[key] = os.environ[key]
            del os.environ[key]

    try:
        groq_api_key = os.getenv("GROQ_API_KEY")

        if not groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is required. "
                "Get a FREE key at: https://console.groq.com/keys\n\n"
                "Make sure your .env file contains:\n"
                "GROQ_API_KEY=gsk_your_key_here"
            )

        knowledge_base_dir = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base_store")
        kaggle_data_dir = os.getenv("KAGGLE_DATA_DIR", "./kaggle_data")
        tavily_api_key = os.getenv("TAVILY_API_KEY")

        groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        os.makedirs(knowledge_base_dir, exist_ok=True)
        os.makedirs(kaggle_data_dir, exist_ok=True)

        return AppConfig(
            groq_api_key=groq_api_key,
            groq_model=groq_model,
            tavily_api_key=tavily_api_key,
            knowledge_base_dir=knowledge_base_dir,
            kaggle_data_dir=kaggle_data_dir,
        )
    finally:
        for key, value in env_backup.items():
            os.environ[key] = value


