import json

import httpx
import pytest

from app.config import Settings
from app.providers import (
    AnthropicProvider,
    OllamaProvider,
    OpenRouterProvider,
    ProviderConfigurationError,
    ProviderDisabledError,
    ProviderError,
    ProviderOutputError,
    create_provider,
    inline_json_schema,
)
from app.schemas import FactVerificationResult


@pytest.mark.asyncio
async def test_anthropic_adapter_uses_structured_tool_and_server_side_key() -> None:
    captured: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={
                "content": [
                    {
                        "type": "tool_use",
                        "name": "fact_verification",
                        "input": {"supported_fact_ids": ["fact_grade"]},
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = AnthropicProvider(
            client=client,
            api_key="server-secret",
            model="generator-model",
            base_url="https://anthropic.invalid",
            max_retries=0,
        )
        result = await provider.complete(
            system_prompt="Verify only.",
            user_payload={"report_text": "synthetic excerpt"},
            output_model=FactVerificationResult,
            tool_name="fact_verification",
        )

    assert result.supported_fact_ids == ["fact_grade"]
    assert captured[0].url.path == "/v1/messages"
    assert captured[0].headers["x-api-key"] == "server-secret"
    body = json.loads(captured[0].content)
    assert body["model"] == "generator-model"
    assert body["tool_choice"]["name"] == "fact_verification"
    assert "report_text" in body["messages"][0]["content"]


@pytest.mark.asyncio
async def test_openrouter_adapter_forces_named_function_schema() -> None:
    captured: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "tool_calls": [
                                {
                                    "type": "function",
                                    "function": {
                                        "name": "fact_verification",
                                        "arguments": '{"supported_fact_ids": []}',
                                    },
                                }
                            ]
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = OpenRouterProvider(
            client=client,
            api_key="server-secret",
            model="generator-model",
            base_url="https://router.invalid/api/v1",
            max_retries=0,
        )
        result = await provider.complete(
            system_prompt="Verify only.",
            user_payload={"report_text": "synthetic excerpt"},
            output_model=FactVerificationResult,
            tool_name="fact_verification",
        )

    assert result.supported_fact_ids == []
    assert captured[0].url.path == "/api/v1/chat/completions"
    assert captured[0].headers["authorization"] == "Bearer server-secret"
    body = json.loads(captured[0].content)
    assert body["tool_choice"]["function"]["name"] == "fact_verification"
    assert body["tools"][0]["function"]["parameters"]["additionalProperties"] is False


@pytest.mark.asyncio
async def test_ollama_adapter_requests_schema_constrained_nonstreaming_output() -> None:
    captured: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={"message": {"content": '{"supported_fact_ids": []}'}},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = OllamaProvider(
            client=client,
            model="verifier-model",
            base_url="http://ollama.invalid:11434",
            max_retries=0,
        )
        result = await provider.complete(
            system_prompt="Verify only.",
            user_payload={"report_text": "synthetic excerpt"},
            output_model=FactVerificationResult,
            tool_name="fact_verification",
        )

    assert result.supported_fact_ids == []
    assert captured[0].url.path == "/api/chat"
    body = json.loads(captured[0].content)
    assert body["stream"] is False
    assert body["model"] == "verifier-model"
    assert body["format"]["type"] == "object"


def test_provider_factory_requires_distinct_generator_and_verifier_models() -> None:
    settings = Settings(
        model_provider="anthropic",
        anthropic_api_key="configured-server-key",
        anthropic_model="model-a",
        anthropic_verifier_model="model-b",
    )
    async_client = httpx.AsyncClient()
    try:
        generator = create_provider(settings, async_client, role="generator")
        verifier = create_provider(settings, async_client, role="verifier")
        assert isinstance(generator, AnthropicProvider)
        assert isinstance(verifier, AnthropicProvider)
        assert generator.model == "model-a"
        assert verifier.model == "model-b"
    finally:
        import asyncio

        asyncio.run(async_client.aclose())


def test_provider_factory_fails_closed_when_disabled_or_verifier_missing() -> None:
    client = httpx.AsyncClient()
    try:
        with pytest.raises(ProviderDisabledError):
            create_provider(Settings(), client)
        missing = Settings(
            model_provider="openrouter",
            openrouter_api_key="configured-server-key",
            openrouter_model="generator",
        )
        with pytest.raises(ProviderConfigurationError):
            create_provider(missing, client)
        same = Settings(
            model_provider="ollama",
            ollama_model="same-model",
            ollama_verifier_model="SAME-MODEL",
        )
        with pytest.raises(ProviderConfigurationError):
            create_provider(same, client, role="verifier")
    finally:
        import asyncio

        asyncio.run(client.aclose())


@pytest.mark.asyncio
async def test_transient_provider_timeout_retries_only_within_configured_bound() -> None:
    calls = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ConnectTimeout("private transport failure")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = AnthropicProvider(
            client=client,
            api_key="server-secret",
            model="generator-model",
            base_url="https://anthropic.invalid",
            max_retries=1,
        )
        with pytest.raises(ProviderError) as error:
            await provider.complete(
                system_prompt="Verify only.",
                user_payload={"report_text": "DO_NOT_LEAK_REPORT_CONTENT"},
                output_model=FactVerificationResult,
                tool_name="fact_verification",
            )

    assert calls == 2
    assert "DO_NOT_LEAK_REPORT_CONTENT" not in str(error.value)
    assert "private transport failure" not in str(error.value)


@pytest.mark.parametrize("transient_status", [429, 503])
@pytest.mark.asyncio
async def test_rate_limit_and_server_errors_retry_only_within_configured_bound(
    transient_status: int,
) -> None:
    calls = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(transient_status, json={"error": "DO_NOT_LEAK_PROVIDER_BODY"})
        return httpx.Response(
            200,
            json={
                "content": [
                    {
                        "type": "tool_use",
                        "name": "fact_verification",
                        "input": {"supported_fact_ids": []},
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = AnthropicProvider(
            client=client,
            api_key="server-secret",
            model="verifier-model",
            base_url="https://anthropic.invalid",
            max_retries=1,
        )
        provider.retry_base_delay = 0
        result = await provider.complete(
            system_prompt="Verify only.",
            user_payload={"report_text": "synthetic excerpt"},
            output_model=FactVerificationResult,
            tool_name="fact_verification",
        )

    assert calls == 2
    assert result.supported_fact_ids == []


@pytest.mark.asyncio
async def test_invalid_provider_key_response_is_generic_and_not_retried() -> None:
    calls = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(401, json={"error": "DO_NOT_LEAK_BAD_KEY_OR_REPORT_CONTENT"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = AnthropicProvider(
            client=client,
            api_key="server-secret",
            model="generator-model",
            base_url="https://anthropic.invalid",
            max_retries=2,
        )
        provider.retry_base_delay = 0
        with pytest.raises(ProviderError) as error:
            await provider.complete(
                system_prompt="Explain only supported facts.",
                user_payload={"report_text": "synthetic excerpt"},
                output_model=FactVerificationResult,
                tool_name="fact_verification",
            )

    assert calls == 1
    assert "DO_NOT_LEAK" not in str(error.value)


@pytest.mark.asyncio
async def test_malformed_provider_schema_fails_closed_without_raw_output() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "content": [
                    {
                        "type": "tool_use",
                        "name": "fact_verification",
                        "input": {"supported_fact_ids": "not-a-list", "report": "DO_NOT_LEAK"},
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = AnthropicProvider(
            client=client,
            api_key="server-secret",
            model="generator-model",
            base_url="https://anthropic.invalid",
            max_retries=0,
        )
        with pytest.raises(ProviderOutputError) as error:
            await provider.complete(
                system_prompt="Verify only.",
                user_payload={"report_text": "synthetic excerpt"},
                output_model=FactVerificationResult,
                tool_name="fact_verification",
            )

    assert "DO_NOT_LEAK" not in str(error.value)


def test_schema_inliner_removes_local_references_and_defs() -> None:
    schema = inline_json_schema(FactVerificationResult)
    assert "$defs" not in schema
    assert "$ref" not in json.dumps(schema)
    assert schema["type"] == "object"
