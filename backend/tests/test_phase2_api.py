import asyncio
from typing import Never

import httpx
import pytest

from app.main import app
from app.providers import ProviderError

REPORT = "DO_NOT_LEAK_REPORT_CONTENT: Synthetic excerpt with enough characters."


def send(payload: dict[str, object]) -> httpx.Response:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/analyze", json=payload)

    return asyncio.run(run())


def valid_payload(**changes: object) -> dict[str, object]:
    return {
        "report_text": REPORT,
        "user_question": None,
        "language": "en",
        "reading_level": "simple",
        "data_is_synthetic_or_deidentified": True,
        "external_processing_acknowledged": True,
        **changes,
    }


def test_refusal_precedes_provider_setup_and_never_returns_report_content() -> None:
    response = send(
        valid_payload(
            user_question="How long do I have to live?",
            data_is_synthetic_or_deidentified=False,
            external_processing_acknowledged=False,
        )
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "refused"
    assert body["refusal_category"] == "prognosis"
    assert body["claims"] == [] and body["facts"] == []
    assert REPORT not in response.text


def test_request_validation_response_does_not_echo_report_or_invalid_locale() -> None:
    response = send(valid_payload(language="ta"))

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid analysis request."}
    assert REPORT not in response.text


def test_oversized_direct_api_body_is_rejected_without_echo() -> None:
    response = send({"report_text": "x" * 1_000_001})

    assert response.status_code == 413
    assert "x" * 100 not in response.text


def test_missing_acknowledgements_are_rejected_before_provider_initialization() -> None:
    response = send(
        valid_payload(
            data_is_synthetic_or_deidentified=False,
            external_processing_acknowledged=False,
        )
    )

    assert response.status_code == 400
    assert REPORT not in response.text
    assert "synthetic or de-identified" in response.json()["detail"]


def test_provider_failure_message_and_request_body_never_reach_response_or_logs(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    import app.main as main

    monkeypatch.setattr(
        main,
        "create_provider",
        lambda *args, **kwargs: (_ for _ in ()).throw(ProviderError(REPORT)),
    )
    app.state.http_client = object()

    response = send(valid_payload())

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Analysis is unavailable. No generated claims were returned."
    }
    assert REPORT not in response.text
    assert REPORT not in caplog.text


def test_unexpected_exception_logging_is_fixed_and_redacted(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    import app.main as main

    def fake_provider(*args: object, **kwargs: object) -> object:
        return object()

    async def fail_analysis(*args: object, **kwargs: object) -> Never:
        raise RuntimeError(REPORT)

    monkeypatch.setattr(main, "create_provider", fake_provider)
    monkeypatch.setattr(main, "analyze_report", fail_analysis)
    app.state.http_client = object()

    response = send(valid_payload())

    assert response.status_code == 500
    assert REPORT not in response.text
    assert REPORT not in caplog.text
    assert "analysis_failed; request content redacted" in caplog.text
