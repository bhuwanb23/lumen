"""Shared fixtures and helpers for the Lumen backend test suite.

Existing tests still construct their own clients (they use ``asyncio.run``
with ``httpx.ASGITransport``); these fixtures are available for new tests
and for the full-stack integration tests added alongside the evaluation
harness.
"""

import asyncio
from collections.abc import Sequence
from typing import Any

import httpx
import pytest
import pytest_asyncio

from app.main import app
from app.schemas import (
    ALL_FACT_FIELDS,
    ClaimCitationDraft,
    ClaimDraft,
    ClaimVerificationResult,
    ExplanationDraft,
    FactDraft,
    FactExtractionDraft,
    FactVerificationResult,
)

REPORT = "Synthetic final pathology report. Histology: invasive ductal carcinoma. Grade: 2."


def run_async(coro: Any) -> Any:
    """Run a coroutine to completion from a synchronous test."""
    return asyncio.run(coro)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _find_rate_limiters(stack: Any) -> list[Any]:
    """Walk an ASGI middleware stack and return every RateLimitMiddleware instance."""
    from app.ratelimit import RateLimitMiddleware

    found: list[Any] = []
    seen: set[int] = set()
    node = stack
    while node is not None and id(node) not in seen:
        seen.add(id(node))
        if isinstance(node, RateLimitMiddleware):
            found.append(node)
        node = getattr(node, "app", None)
    return found


@pytest.fixture(autouse=True)
def _relax_rate_limit() -> Any:
    """Neutralize the shared app's rate limiter for the test session.

    The production app registers RateLimitMiddleware (30 req / 60 s by default).
    The suite posts to /analyze far more often than that within a single run,
    so the shared limiter would start returning 429 and break unrelated tests.
    Dedicated rate-limit tests build their own isolated apps and are unaffected.
    """
    from app.main import app as _app

    limiters = _find_rate_limiters(getattr(_app, "middleware_stack", None))
    originals = [(rl, rl.limit, rl.window_seconds) for rl in limiters]
    for rl in limiters:
        rl.limit = 10_000_000  # effectively unlimited for the test session
    yield
    for rl, limit, window in originals:
        rl.limit = limit
        rl.window_seconds = window


def make_client(**kwargs: Any) -> httpx.AsyncClient:
    """Return an ASGI test client bound to the FastAPI app.

    Callers must close the client (use it as an async context manager).
    """
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver", **kwargs)


@pytest_asyncio.fixture
async def client() -> Any:
    async with make_client() as c:
        yield c


def valid_payload(**changes: Any) -> dict[str, Any]:
    """A minimal, valid POST /analyze payload with optional overrides."""
    payload: dict[str, Any] = {
        "report_text": REPORT,
        "user_question": None,
        "language": "en",
        "reading_level": "simple",
        "data_is_synthetic_or_deidentified": True,
        "external_processing_acknowledged": True,
    }
    payload.update(changes)
    return payload


def make_extraction(
    report: str = REPORT,
    *,
    overrides: dict[str, FactDraft] | None = None,
) -> FactExtractionDraft:
    """Build a FactExtractionDraft covering every allowed field."""
    override_map = overrides or {}
    defaults = {
        "report_type": FactDraft(
            field="report_type",
            value="final pathology report",
            status="stated",
            evidence_quote="final pathology report",
        ),
        "histology": FactDraft(
            field="histology",
            value="invasive ductal carcinoma",
            status="stated",
            evidence_quote="invasive ductal carcinoma",
        ),
        "grade": FactDraft(
            field="grade",
            value="Grade 2",
            status="stated",
            evidence_quote="Grade: 2",
        ),
    }
    defaults.update(override_map)
    items = []
    for field in ALL_FACT_FIELDS:
        if field in defaults:
            items.append(defaults[field])
        else:
            items.append(
                FactDraft(field=field, value=None, status="not_stated", evidence_quote=None)
            )
    return FactExtractionDraft(facts=items)


class FakeProvider:
    """Deterministic provider double recording every call for assertions."""

    def __init__(self, results: dict[str, Any]) -> None:
        self.results = results
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def complete(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        output_model: type[Any],
        tool_name: str,
    ) -> Any:
        self.calls.append((tool_name, user_payload))
        result = self.results[tool_name]
        if isinstance(result, Exception):
            raise result
        return result


def fake_provider(
    *,
    extraction: FactExtractionDraft | None = None,
    fact_ids: Sequence[str] | None = None,
    explanation: ExplanationDraft | None = None,
    claim_ids: Sequence[str] | None = None,
) -> FakeProvider:
    """Build a FakeProvider that whitelists all stated facts by default."""
    extraction = extraction or make_extraction()
    known_fact_ids = [f"fact_{field}" for field in ALL_FACT_FIELDS]
    return FakeProvider(
        {
            "fact_extraction": extraction,
            "fact_verification": FactVerificationResult(
                supported_fact_ids=list(fact_ids if fact_ids is not None else known_fact_ids)
            ),
            "report_explanation": explanation or ExplanationDraft(claims=[]),
            "claim_verification": ClaimVerificationResult(
                supported_claim_ids=list(claim_ids or [])
            ),
        }
    )


def claim_draft(text: str, fact_id: str, evidence_quote: str) -> ClaimDraft:
    """Build a ClaimDraft citing a single fact with a matching evidence quote."""
    return ClaimDraft(
        text=text,
        citations=[ClaimCitationDraft(fact_id=fact_id, evidence_quote=evidence_quote)],
    )
