"""Server-only structured-output adapters for Anthropic, OpenRouter, and Ollama."""

from __future__ import annotations

import asyncio
import copy
import json
import random
from typing import Any, Literal, Protocol, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.config import Settings

T = TypeVar("T", bound=BaseModel)
ProviderRole = Literal["generator", "verifier"]
_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


class ProviderError(RuntimeError):
    """Safe, non-payload-bearing provider failure."""


class ProviderConfigurationError(ProviderError):
    pass


class ProviderDisabledError(ProviderConfigurationError):
    pass


class ProviderOutputError(ProviderError):
    pass


class StructuredProvider(Protocol):
    async def complete(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        output_model: type[T],
        tool_name: str,
    ) -> T: ...


def inline_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Inline Pydantic local definitions for providers with limited `$ref` support."""
    schema = model.model_json_schema(mode="validation")
    definitions = schema.pop("$defs", {})

    def visit(value: Any) -> Any:
        if isinstance(value, list):
            return [visit(item) for item in value]
        if not isinstance(value, dict):
            return value
        if "$ref" in value:
            ref = value["$ref"]
            prefix = "#/$defs/"
            if not isinstance(ref, str) or not ref.startswith(prefix):
                raise ProviderConfigurationError("Output schema contains an unsupported reference")
            name = ref[len(prefix) :]
            if name not in definitions:
                raise ProviderConfigurationError("Output schema contains an unresolved reference")
            resolved = copy.deepcopy(definitions[name])
            resolved.update({key: item for key, item in value.items() if key != "$ref"})
            return visit(resolved)
        return {
            key: visit(item)
            for key, item in value.items()
            if key not in {"$defs", "$schema", "$id"}
        }

    result = visit(schema)
    if not isinstance(result, dict):
        raise ProviderConfigurationError("Output schema is not an object")
    return result


def _payload_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _strip_length_limits(value: Any) -> Any:
    """Drop `maxLength` constraints; Ollama's GBNF grammar converter rejects them."""
    if isinstance(value, list):
        return [_strip_length_limits(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _strip_length_limits(item) for key, item in value.items() if key != "maxLength"
        }
    return value


class _HttpStructuredProvider:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        max_retries: int,
        retry_base_delay: float = 0.08,
    ) -> None:
        self.client = client
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay

    async def _post_json(
        self,
        url: str,
        *,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(url, headers=headers, json=payload)
            except httpx.HTTPError:
                if attempt < self.max_retries:
                    delay = self.retry_base_delay * (2**attempt) + random.uniform(0, 0.025)
                    await asyncio.sleep(delay)
                    continue
                raise ProviderError("Configured model provider is unavailable") from None

            if response.status_code in _RETRYABLE_STATUSES and attempt < self.max_retries:
                delay = self.retry_base_delay * (2**attempt) + random.uniform(0, 0.025)
                await asyncio.sleep(delay)
                continue
            if response.status_code < 200 or response.status_code >= 300:
                # Never parse or attach provider error bodies; they may echo submitted content.
                raise ProviderError("Configured model provider returned an error") from None
            try:
                value = response.json()
            except (ValueError, UnicodeDecodeError):
                raise ProviderOutputError(
                    "Configured model provider returned invalid JSON"
                ) from None
            if not isinstance(value, dict):
                raise ProviderOutputError("Configured model provider returned an invalid response")
            return value
        raise ProviderError("Configured model provider is unavailable")

    @staticmethod
    def _validate_output(payload: Any, output_model: type[T]) -> T:
        try:
            return output_model.model_validate(payload)
        except (ValidationError, TypeError, ValueError):
            raise ProviderOutputError(
                "Configured model provider returned an invalid structured result"
            ) from None


class AnthropicProvider(_HttpStructuredProvider):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        api_key: str,
        model: str,
        base_url: str,
        max_retries: int,
    ) -> None:
        super().__init__(client=client, max_retries=max_retries)
        self.api_key = api_key
        self.model = model
        self.url = base_url.rstrip("/") + "/v1/messages"

    async def complete(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        output_model: type[T],
        tool_name: str,
    ) -> T:
        response = await self._post_json(
            self.url,
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            payload={
                "model": self.model,
                "max_tokens": 2500,
                "temperature": 0,
                "system": system_prompt,
                "messages": [{"role": "user", "content": _payload_text(user_payload)}],
                "tools": [
                    {
                        "name": tool_name,
                        "description": "Return only the requested schema-conforming object.",
                        "input_schema": inline_json_schema(output_model),
                    }
                ],
                "tool_choice": {"type": "tool", "name": tool_name},
            },
        )
        content = response.get("content")
        if not isinstance(content, list):
            raise ProviderOutputError("Configured model provider returned no structured result")
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") == tool_name
            ):
                return self._validate_output(block.get("input"), output_model)
        raise ProviderOutputError("Configured model provider returned no requested tool result")


class OpenRouterProvider(_HttpStructuredProvider):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        api_key: str,
        model: str,
        base_url: str,
        max_retries: int,
    ) -> None:
        super().__init__(client=client, max_retries=max_retries)
        self.api_key = api_key
        self.model = model
        self.url = base_url.rstrip("/") + "/chat/completions"

    async def complete(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        output_model: type[T],
        tool_name: str,
    ) -> T:
        response = await self._post_json(
            self.url,
            headers={
                "content-type": "application/json",
                "authorization": f"Bearer {self.api_key}",
            },
            payload={
                "model": self.model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": _payload_text(user_payload)},
                ],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "description": "Return only the requested schema-conforming object.",
                            "parameters": inline_json_schema(output_model),
                        },
                    }
                ],
                "tool_choice": {"type": "function", "function": {"name": tool_name}},
            },
        )
        try:
            message = response["choices"][0]["message"]
            calls = message["tool_calls"]
            call = next(
                item
                for item in calls
                if item["type"] == "function" and item["function"]["name"] == tool_name
            )
            raw = call["function"]["arguments"]
            parsed = json.loads(raw) if isinstance(raw, str) else raw
        except (KeyError, IndexError, StopIteration, TypeError, ValueError):
            raise ProviderOutputError(
                "Configured model provider returned no requested tool result"
            ) from None
        return self._validate_output(parsed, output_model)


class OllamaProvider(_HttpStructuredProvider):
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        model: str,
        base_url: str,
        max_retries: int,
    ) -> None:
        super().__init__(client=client, max_retries=max_retries)
        self.model = model
        self.url = base_url.rstrip("/") + "/api/chat"

    async def complete(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        output_model: type[T],
        tool_name: str,
    ) -> T:
        response = await self._post_json(
            self.url,
            headers={"content-type": "application/json"},
            payload={
                "model": self.model,
                "stream": False,
                "think": False,
                "format": _strip_length_limits(inline_json_schema(output_model)),
                "options": {"temperature": 0},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": _payload_text(user_payload)},
                ],
            },
        )
        try:
            raw = response["message"]["content"]
            parsed = json.loads(raw) if isinstance(raw, str) else raw
        except (KeyError, TypeError, ValueError):
            raise ProviderOutputError(
                "Configured model provider returned no structured result"
            ) from None
        return self._validate_output(parsed, output_model)


def create_provider(
    settings: Settings,
    client: httpx.AsyncClient,
    *,
    role: ProviderRole = "generator",
) -> StructuredProvider:
    """Build the explicitly selected model role; never switch provider or data recipient."""
    if settings.model_provider == "disabled":
        raise ProviderDisabledError("Model processing is disabled")

    if settings.model_provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ProviderConfigurationError("Anthropic provider configuration is incomplete")
        generator_model = settings.anthropic_model
        verifier_model = settings.anthropic_verifier_model
        base_url = settings.anthropic_base_url
        api_key = settings.anthropic_api_key
    elif settings.model_provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ProviderConfigurationError("OpenRouter provider configuration is incomplete")
        generator_model = settings.openrouter_model
        verifier_model = settings.openrouter_verifier_model
        base_url = settings.openrouter_base_url
        api_key = settings.openrouter_api_key
    elif settings.model_provider == "ollama":
        generator_model = settings.ollama_model
        verifier_model = settings.ollama_verifier_model
        base_url = settings.ollama_base_url
        api_key = None
    else:
        raise ProviderConfigurationError("Configured model provider is unsupported")

    if not generator_model or not verifier_model:
        raise ProviderConfigurationError("Generator and verifier models must both be configured")
    if generator_model.casefold() == verifier_model.casefold():
        raise ProviderConfigurationError("Verifier model must differ from the generator model")
    model = generator_model if role == "generator" else verifier_model
    if settings.model_provider == "anthropic":
        assert api_key is not None
        return AnthropicProvider(
            client=client,
            api_key=api_key,
            model=model,
            base_url=base_url,
            max_retries=settings.model_max_retries,
        )
    if settings.model_provider == "openrouter":
        assert api_key is not None
        return OpenRouterProvider(
            client=client,
            api_key=api_key,
            model=model,
            base_url=base_url,
            max_retries=settings.model_max_retries,
        )
    return OllamaProvider(
        client=client,
        model=model,
        base_url=base_url,
        max_retries=settings.model_max_retries,
    )
