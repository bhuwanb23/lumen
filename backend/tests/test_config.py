from typing import cast

import pytest
from pydantic import ValidationError

from app.config import ModelProvider, Settings


@pytest.mark.parametrize("provider", ["disabled", "anthropic", "openrouter", "ollama"])
def test_model_provider_setting_is_allowlisted(provider: str) -> None:
    settings = Settings.model_validate({"model_provider": provider})
    assert settings.model_provider == cast(ModelProvider, provider)


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"model_provider": "unknown-provider"})
