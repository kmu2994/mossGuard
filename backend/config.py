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

    # LiveKit credentials & WebRTC configuration
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secretsecretsecretsecretsecretsecret"
    LIVEKIT_URL: str = "wss://mossguard-livekit.example.com"

    # Security & Auth configuration
    JWT_SECRET: str = "mossguard-jwt-secret-key-2026-super-secure"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    RATE_LIMIT_PER_MINUTE: int = 60
    ENCRYPTION_AT_REST: str = "AES-256"
    ENCRYPTION_IN_TRANSIT: str = "TLS 1.3"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
