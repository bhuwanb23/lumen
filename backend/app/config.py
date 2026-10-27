from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ModelProvider = Literal["disabled", "anthropic", "openrouter", "ollama"]


class Settings(BaseSettings):
    """Server-side configuration; provider keys must never reach the browser."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"), extra="ignore", case_sensitive=False
    )

    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    model_provider: ModelProvider = "disabled"
    max_report_chars: int = Field(default=50_000, ge=100, le=50_000)
    model_timeout_seconds: float = Field(default=45.0, gt=0, le=120)
    model_max_retries: int = Field(default=2, ge=0, le=3)

    # In-memory sliding-window rate limit applied to POST /analyze per client IP.
    rate_limit_requests: int = Field(default=30, ge=1, le=10_000)
    rate_limit_window_seconds: float = Field(default=60.0, gt=0, le=3600)

    # Direct Anthropic API; server-side only.
    anthropic_api_key: str | None = None
    anthropic_model: str = ""
    anthropic_verifier_model: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"

    # OpenRouter-compatible endpoint; server-side key only.
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = ""
    openrouter_verifier_model: str = ""

    # Ollama endpoint; do not assume it is local unless network is controlled.
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = ""
    ollama_verifier_model: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
