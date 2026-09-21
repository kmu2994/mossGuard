"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """All configuration is driven by environment variables."""

    # Moss credentials
    MOSS_PROJECT_ID: str = ""
    MOSS_PROJECT_KEY: str = ""
    MOSS_INDEX_NAME: str = "mossguard-kb"

    # LLM configuration — accepts GEMINI_KEY, GEMINI_API_KEY, or OPENAI_API_KEY
    GEMINI_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_BASE_URL: str | None = "https://llm.hidevs.xyz/v1"
    LLM_MODEL: str = "gemini-3.5-flash-lite"

    @property
    def api_key(self) -> str:
        """Returns GEMINI_KEY, GEMINI_API_KEY, or OPENAI_API_KEY."""
        return (
            self.GEMINI_KEY.strip()
            or self.GEMINI_API_KEY.strip()
            or self.OPENAI_API_KEY.strip()
            or "dummy_key"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
