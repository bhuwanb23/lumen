"""Smoke-test the configured structured-output provider against a synthetic fixture.

Run from backend/:  uv run python scripts/smoke_provider.py [--full]
Requires an enabled provider in .env or the environment, e.g.:
  MODEL_PROVIDER=ollama OLLAMA_MODEL=gemma4:12b OLLAMA_VERIFIER_MODEL=gemma4:12b-verifier

Default mode runs one generator call (fact extraction) and one verifier call
(fact verification). --full additionally runs the complete four-stage
analyze_report pipeline. Synthetic fixture data only; no real patient text.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.pipeline import (  # noqa: E402
    EXTRACTION_SYSTEM,
    FACT_VERIFY_SYSTEM,
    _materialize_facts,
    analyze_report,
)
from app.providers import ProviderError, create_provider  # noqa: E402
from app.schemas import (  # noqa: E402
    ALL_FACT_FIELDS,
    AnalysisRequest,
    FactExtractionDraft,
    FactVerificationResult,
)

REPO_ROOT = ROOT.parent
SYNTHETIC_DATASET = REPO_ROOT / "eval" / "datasets" / "synthetic" / "reports.json"
DEFAULT_CASE_ID = "syn_breast_core_001"


def load_report_text(case_id: str) -> str:
    payload = json.loads(SYNTHETIC_DATASET.read_text(encoding="utf-8"))
    for case in payload.get("cases", []):
        if case.get("case_id") == case_id:
            text = case.get("report_text")
            if isinstance(text, str) and text.strip():
                return text
    raise SystemExit(f"Synthetic case {case_id!r} not found in {SYNTHETIC_DATASET}")


def configured_models(settings: Settings) -> tuple[str, str]:
    if settings.model_provider == "anthropic":
        return settings.anthropic_model, settings.anthropic_verifier_model
    if settings.model_provider == "openrouter":
        return settings.openrouter_model, settings.openrouter_verifier_model
    return settings.ollama_model, settings.ollama_verifier_model


def _print_stage(label: str, elapsed: float) -> None:
    print(f"  {label}: ok ({elapsed:.1f}s)")


# Per-stage elapsed time, set by the runner around each provider call.
_LAST: list[float] = [0.0]


async def timed(coro: Any) -> Any:
    start = time.perf_counter()
    result = await coro
    _LAST[0] = time.perf_counter() - start
    return result


async def run(args: argparse.Namespace) -> int:
    if args.provider:
        os.environ["MODEL_PROVIDER"] = args.provider
    if args.model:
        os.environ["OLLAMA_MODEL"] = args.model
    if args.verifier:
        os.environ["OLLAMA_VERIFIER_MODEL"] = args.verifier
    if args.base_url:
        os.environ["OLLAMA_BASE_URL"] = args.base_url

    settings = Settings()
    if settings.model_provider == "disabled":
        print("FAIL: MODEL_PROVIDER=disabled; configure a provider (see .env.example)")
        return 1

    gen_model, ver_model = configured_models(settings)
    base_url = settings.ollama_base_url if settings.model_provider == "ollama" else "(default)"
    print(
        f"provider={settings.model_provider} "
        f"generator={gen_model or '(unset)'} verifier={ver_model or '(unset)'} "
        f"base_url={base_url}"
    )

    report_text = load_report_text(args.case)
    print(f"fixture={args.case} report_chars={len(report_text)}")

    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(args.timeout)) as client:
            generator = create_provider(settings, client, role="generator")
            verifier = create_provider(settings, client, role="verifier")

            draft = await timed(
                generator.complete(
                    system_prompt=EXTRACTION_SYSTEM,
                    user_payload={
                        "allowed_fields": list(ALL_FACT_FIELDS),
                        "report_text": report_text,
                    },
                    output_model=FactExtractionDraft,
                    tool_name="fact_extraction",
                )
            )
            counts: dict[str, int] = {}
            for item in draft.facts:
                counts[item.status] = counts.get(item.status, 0) + 1
            summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
            _print_stage(f"fact_extraction: {len(draft.facts)} facts ({summary})", _LAST[0])

            facts, dropped = _materialize_facts(draft, report_text)
            if dropped:
                print(f"  note: {dropped} draft fact(s) dropped by deterministic span checks")
            verdict = await timed(
                verifier.complete(
                    system_prompt=FACT_VERIFY_SYSTEM,
                    user_payload={
                        "report_text": report_text,
                        "facts": [fact.model_dump(mode="json") for fact in facts],
                    },
                    output_model=FactVerificationResult,
                    tool_name="fact_verification",
                )
            )
            supported = len(verdict.supported_fact_ids)
            _print_stage(
                f"fact_verification: {supported}/{len(facts)} facts supported",
                _LAST[0],
            )

            if args.full:
                request = AnalysisRequest(
                    report_text=report_text,
                    user_question="What does this report say?",
                    data_is_synthetic_or_deidentified=True,
                    external_processing_acknowledged=True,
                )
                response = await timed(analyze_report(request, generator, verifier))
                _print_stage(
                    f"analyze_report: status={response.status} "
                    f"facts={len(response.facts)} claims={len(response.claims)} "
                    f"questions={len(response.questions_for_care_team)}",
                    _LAST[0],
                )
    except ProviderError as exc:
        print(f"FAIL: {exc}")
        return 1

    print(f"PASS: provider smoke completed in {time.perf_counter() - started:.1f}s")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--full", action="store_true", help="also run analyze_report end to end")
    parser.add_argument("--provider", help="override MODEL_PROVIDER")
    parser.add_argument("--model", help="override OLLAMA_MODEL")
    parser.add_argument("--verifier", help="override OLLAMA_VERIFIER_MODEL")
    parser.add_argument("--base-url", help="override OLLAMA_BASE_URL")
    parser.add_argument("--case", default=DEFAULT_CASE_ID, help="synthetic fixture case_id")
    parser.add_argument(
        "--timeout", type=float, default=600.0, help="per-request timeout seconds (cold model load)"
    )
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
