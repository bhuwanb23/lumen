from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ModelProvider = Literal["disabled", "anthropic", "openrouter", "ollama"]


class Settings(BaseSettings):
    """Server-side configuration; provider keys must never reach the browser.

    Phase 0 only records provider settings. No provider adapter or model call exists yet.
    Keep `model_provider=disabled` until a later phase implements and tests an adapter.
    """

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"), extra="ignore", case_sensitive=False
    )

    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    model_provider: ModelProvider = "disabled"

    # Direct Anthropic API; server-side only.
    anthropic_api_key: str | None = None
    anthropic_model: str = ""

    # OpenRouter-compatible endpoint; server-side key only.
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = ""

    # Ollama is optional and should be bound to a trusted local interface/network.
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
