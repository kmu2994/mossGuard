"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """All configuration is driven by environment variables."""

    # Moss credentials
    MOSS_PROJECT_ID: str
    MOSS_PROJECT_KEY: str
    MOSS_INDEX_NAME: str = "mossguard-kb"

    # LLM configuration
    OPENAI_API_KEY: str
    LLM_BASE_URL: str | None = "https://llm.hidevs.xyz/v1"
    LLM_MODEL: str = "gemini-3.5-flash-lite"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
