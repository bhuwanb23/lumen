import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.mark.parametrize("provider", ["disabled", "anthropic", "openrouter", "ollama"])
def test_model_provider_setting_is_allowlisted(provider: str) -> None:
    settings = Settings(model_provider=provider, _env_file=None)
    assert settings.model_provider == provider


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(model_provider="unknown-provider", _env_file=None)  # type: ignore[arg-type]
