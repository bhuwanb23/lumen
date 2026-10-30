"""Run the synthetic Lumen evaluation harness.

Live mode uses the explicitly configured server-side provider. Mock mode is deterministic
and is intended for CI/harness validation only; it is not a model-performance result.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(ROOT / "eval"))

import importlib.util  # noqa: E402

_scoring_spec = importlib.util.spec_from_file_location(
    "lumen_scoring", ROOT / "eval" / "scoring.py"
)
if _scoring_spec is None or _scoring_spec.loader is None:
    raise RuntimeError("Unable to load eval/scoring.py")
_scoring_module = importlib.util.module_from_spec(_scoring_spec)
_scoring_spec.loader.exec_module(_scoring_module)

_abstention_metrics = _scoring_module.abstention_metrics
_claim_citation_validity = _scoring_module.claim_citation_validity
_evidence_quote_validity = _scoring_module.evidence_quote_validity
_evidence_span_validity = _scoring_module.evidence_span_validity
_git_commit = _scoring_module.git_commit
_score_facts = _scoring_module.score_facts
_sha256_file = _scoring_module.sha256_file

abstention_metrics = _abstention_metrics
claim_citation_validity = _claim_citation_validity
evidence_quote_validity = _evidence_quote_validity
evidence_span_validity = _evidence_span_validity
git_commit = _git_commit
score_facts = _score_facts
sha256_file = _sha256_file

from app.config import get_settings  # noqa: E402
from app.pipeline import (  # noqa: E402
    EXTRACTION_SYSTEM,
    FACT_VERIFY_SYSTEM,
    _build_claim_candidates,
    _materialize_facts,
    _strict_supported_ids,
    analyze_report,
)
from app.providers import create_provider  # noqa: E402
from app.schemas import (  # noqa: E402
    ALL_FACT_FIELDS,
    AnalysisRequest,
    ClaimDraft,
    ClaimVerificationResult,
    ExplanationDraft,
    FactDraft,
    FactExtractionDraft,
    FactVerificationResult,
    validate_evidence_links,
)

REPORTS_PATH = ROOT / "eval" / "datasets" / "synthetic" / "reports.json"
ANSWER_KEYS_PATH = ROOT / "eval" / "datasets" / "synthetic" / "answer_keys.json"
RESULTS_DIR = ROOT / "eval" / "results"


class FakeProvider:
    """Deterministic provider used only for harness/CI validation."""

    def __init__(self, results: dict[str, Any]) -> None:
        self.results = results

    async def complete(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        output_model: type[Any],
        tool_name: str,
    ) -> Any:
        result = self.results[tool_name]
        if callable(result):
            result = result(user_payload)
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Lumen synthetic evaluation")
    parser.add_argument("--mode", choices=("auto", "live", "mock"), default="auto")
    parser.add_argument("--case", action="append", default=[], help="Case ID to run; repeatable")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=120.0)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return cast(dict[str, Any], value)


def validate_fixtures() -> None:
    reports_doc = load_json(REPORTS_PATH)
    keys_doc = load_json(ANSWER_KEYS_PATH)
    if not reports_doc.get("synthetic_only") or not all(
        case.get("synthetic") for case in keys_doc["cases"]
    ):
        raise ValueError("Evaluation fixtures must be explicitly synthetic")
    report_ids = {case["case_id"] for case in reports_doc["cases"]}
    key_ids = {case["case_id"] for case in keys_doc["cases"]}
    if report_ids != key_ids:
        raise ValueError("Report and answer-key case IDs do not match")
    if len(report_ids) != 8:
        raise ValueError("Expected 8 synthetic report cases")


def expected_fact_map(answer_case: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {fact["field"]: fact for fact in answer_case["expected_facts"]}


def mock_extraction(case: dict[str, Any], answer_case: dict[str, Any]) -> FactExtractionDraft:
    expected_by_field = expected_fact_map(answer_case)
    facts: list[FactDraft] = []
    for field in ALL_FACT_FIELDS:
        expected = expected_by_field.get(field)
        if expected is None:
            facts.append(
                FactDraft(field=field, value=None, status="not_stated", evidence_quote=None)
            )
            continue
        evidence = expected.get("evidence")
        quote = evidence["quote"] if isinstance(evidence, dict) else None
        facts.append(
            FactDraft(
                field=field,
                value=expected["value"],
                status=expected["status"],
                evidence_quote=quote,
            )
        )
    return FactExtractionDraft(facts=facts)


def mock_explanation(answer_case: dict[str, Any]) -> ExplanationDraft:
    from app.schemas import ClaimCitationDraft

    claims: list[ClaimDraft] = []
    facts_by_id = {fact["fact_id"]: fact for fact in answer_case["expected_facts"]}
    for example in answer_case.get("allowed_claim_examples", []):
        citations = []
        for fact_id in example["cites"]:
            expected_fact = facts_by_id.get(fact_id)
            if expected_fact is None or not isinstance(expected_fact.get("evidence"), dict):
                continue
            citations.append(
                ClaimCitationDraft(
                    fact_id=f"fact_{expected_fact['field']}",
                    evidence_quote=expected_fact["evidence"]["quote"],
                )
            )
        if citations:
            claims.append(ClaimDraft(text=example["text"], citations=citations))
    return ExplanationDraft(claims=claims)


def make_mock_provider(
    case: dict[str, Any], answer_case: dict[str, Any], report_text: str
) -> FakeProvider:
    expected_facts = answer_case["expected_facts"]
    fact_ids = [f"fact_{fact['field']}" for fact in expected_facts]
    explanation = mock_explanation(answer_case)
    claim_ids = [f"claim_{index:02d}" for index, _ in enumerate(explanation.claims, start=1)]

    def extraction(_: dict[str, Any]) -> FactExtractionDraft:
        return mock_extraction(case, answer_case)

    def fact_verification(_: dict[str, Any]) -> FactVerificationResult:
        return FactVerificationResult(supported_fact_ids=fact_ids)

    def report_explanation(_: dict[str, Any]) -> ExplanationDraft:
        return explanation

    def claim_verification(_: dict[str, Any]) -> ClaimVerificationResult:
        return ClaimVerificationResult(supported_claim_ids=claim_ids)

    return FakeProvider(
        {
            "fact_extraction": extraction,
            "fact_verification": fact_verification,
            "report_explanation": report_explanation,
            "claim_verification": claim_verification,
        }
    )


async def evaluate_case(
    case: dict[str, Any],
    answer_case: dict[str, Any],
    report_text: str,
    mode: str,
    settings: Any,
) -> dict[str, Any]:
    started = time.perf_counter()
    case_id = case["case_id"]
    request = AnalysisRequest(
        report_text=report_text,
        user_question=None,
        language="en",
        reading_level="simple",
        data_is_synthetic_or_deidentified=True,
        external_processing_acknowledged=True,
    )

    generator: Any
    verifier: Any
    if mode == "mock":
        generator = make_mock_provider(case, answer_case, report_text)
        verifier = generator
    else:
        import httpx

        client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.model_timeout_seconds),
            follow_redirects=False,
            trust_env=False,
        )
        try:
            generator = create_provider(settings, client, role="generator")
            verifier = create_provider(settings, client, role="verifier")
        except Exception:
            await client.aclose()
            raise

    extraction_started = time.perf_counter()
    try:
        extraction_draft = await generator.complete(
            system_prompt=EXTRACTION_SYSTEM,
            user_payload={"allowed_fields": list(ALL_FACT_FIELDS), "report_text": report_text},
            output_model=FactExtractionDraft,
            tool_name="fact_extraction",
        )
        extraction_elapsed = time.perf_counter() - extraction_started
        materialized_facts, dropped_fact_count = _materialize_facts(extraction_draft, report_text)
        validate_evidence_links(report_text, materialized_facts)

        fact_verdict = await verifier.complete(
            system_prompt=FACT_VERIFY_SYSTEM,
            user_payload={
                "report_text": report_text,
                "facts": [fact.model_dump(mode="json") for fact in materialized_facts],
            },
            output_model=FactVerificationResult,
            tool_name="fact_verification",
        )
        fact_ids = {fact.fact_id for fact in materialized_facts}
        accepted_fact_ids = _strict_supported_ids(fact_verdict.supported_fact_ids, fact_ids)
        if accepted_fact_ids is None:
            verified_facts = []
        else:
            verified_facts = [
                fact for fact in materialized_facts if fact.fact_id in accepted_fact_ids
            ]
        validate_evidence_links(report_text, verified_facts)

        explainer_facts = [fact for fact in verified_facts if fact.evidence is not None]
        if explainer_facts:
            explanation = await generator.complete(
                system_prompt=__import__(
                    "app.pipeline", fromlist=["EXPLANATION_SYSTEM"]
                ).EXPLANATION_SYSTEM,
                user_payload={
                    "language": request.language,
                    "reading_level": request.reading_level,
                    "verified_facts": [fact.model_dump(mode="json") for fact in explainer_facts],
                    "user_question": None,
                },
                output_model=ExplanationDraft,
                tool_name="report_explanation",
            )
            candidates, invalid_candidate_count = _build_claim_candidates(
                explanation, verified_facts
            )
            if candidates:
                claim_verdict = await verifier.complete(
                    system_prompt=__import__(
                        "app.pipeline", fromlist=["CLAIM_VERIFY_SYSTEM"]
                    ).CLAIM_VERIFY_SYSTEM,
                    user_payload={
                        "report_text": report_text,
                        "claims": [
                            {
                                "claim_id": claim.claim_id,
                                "text": claim.text,
                                "citations": [
                                    {"fact_id": citation.fact_id, "quote": citation.evidence.quote}
                                    for citation in claim.citations
                                ],
                            }
                            for claim in candidates
                        ],
                    },
                    output_model=ClaimVerificationResult,
                    tool_name="claim_verification",
                )
                allowed_claim_ids = {claim.claim_id for claim in candidates}
                supported_ids = _strict_supported_ids(
                    claim_verdict.supported_claim_ids, allowed_claim_ids
                )
                if supported_ids is None:
                    supported_claims = []
                else:
                    supported_claims = [
                        claim for claim in candidates if claim.claim_id in supported_ids
                    ]
            else:
                supported_claims = []
        else:
            supported_claims = []

        response = await analyze_report(request, generator, verifier)
        total_elapsed = time.perf_counter() - started

        extraction_score = score_facts(extraction_draft.facts, answer_case["expected_facts"])
        abstention = abstention_metrics(extraction_draft.facts, answer_case["expected_facts"])
        quote_validity = evidence_quote_validity(extraction_draft.facts, report_text)
        span_validity = evidence_span_validity(materialized_facts, report_text)
        citation_metrics = claim_citation_validity(response.claims, response.facts, report_text)

        result = {
            "case_id": case_id,
            "cancer_context": case.get("cancer_context"),
            "status": "ok",
            "response_status": response.status,
            "extraction": {
                "predicted_fact_count": len(extraction_draft.facts),
                "expected_fact_count": len(answer_case["expected_facts"]),
                **extraction_score,
                "abstention": abstention,
                "evidence_quote_validity": quote_validity,
            },
            "verified_facts": {
                "count": len(verified_facts),
                **score_facts(verified_facts, answer_case["expected_facts"]),
            },
            "materialized_fact_count": len(materialized_facts),
            "dropped_fact_count": dropped_fact_count,
            "response": {
                "fact_count": len(response.facts),
                "claim_count": len(response.claims),
                "omitted_claim_count": response.omitted_claim_count,
                "query_notice": response.query_notice,
                "citation_validity": citation_metrics,
            },
            "latency_seconds": {
                "extraction": extraction_elapsed,
                "total": total_elapsed,
            },
            "error": None,
        }
        if mode != "mock":
            await client.aclose()
        return result
    except Exception as exc:  # noqa: BLE001
        total_elapsed = time.perf_counter() - started
        if mode != "mock" and "client" in locals():
            await client.aclose()
        return {
            "case_id": case_id,
            "cancer_context": case.get("cancer_context"),
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "latency_seconds": {"total": total_elapsed},
        }


async def main_async(args: argparse.Namespace) -> int:
    validate_fixtures()
    if args.dry_run:
        print(
            json.dumps(
                {"status": "dry_run", "report_count": 8, "claim_support_rate": "not_measured"},
                indent=2,
            )
        )
        return 0

    reports_doc = load_json(REPORTS_PATH)
    keys_doc = load_json(ANSWER_KEYS_PATH)
    reports = {case["case_id"]: case for case in reports_doc["cases"]}
    keys = {case["case_id"]: case for case in keys_doc["cases"]}

    selected_ids = args.case or list(reports)
    if args.max_cases is not None:
        selected_ids = selected_ids[: args.max_cases]
    unknown = [case_id for case_id in selected_ids if case_id not in reports]
    if unknown:
        raise ValueError(f"Unknown case IDs: {', '.join(unknown)}")

    if args.mode == "live":
        mode = "live"
    elif args.mode == "mock":
        mode = "mock"
    else:
        settings = get_settings()
        mode = "mock" if settings.model_provider == "disabled" else "live"

    if mode == "live":
        os.environ.setdefault("MODEL_TIMEOUT_SECONDS", str(min(args.timeout, 120.0)))
        settings = get_settings()
    else:
        settings = get_settings()

    started = time.perf_counter()
    results = []
    for case_id in selected_ids:
        result = await evaluate_case(
            reports[case_id],
            keys[case_id],
            reports[case_id]["report_text"],
            mode,
            settings,
        )
        results.append(result)
        print(f"{case_id}: {result['status']}")

    aggregate_tp = sum(
        item.get("extraction", {}).get("true_positives", 0)
        for item in results
        if item["status"] == "ok"
    )
    aggregate_fp = sum(
        item.get("extraction", {}).get("false_positives", 0)
        for item in results
        if item["status"] == "ok"
    )
    aggregate_fn = sum(
        item.get("extraction", {}).get("false_negatives", 0)
        for item in results
        if item["status"] == "ok"
    )
    precision = aggregate_tp / (aggregate_tp + aggregate_fp) if aggregate_tp + aggregate_fp else 0.0
    recall = aggregate_tp / (aggregate_tp + aggregate_fn) if aggregate_tp + aggregate_fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    payload = {
        "run_id": str(uuid.uuid4()),
        "started_at": datetime.now(UTC).isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "wall_time_seconds": time.perf_counter() - started,
        "evaluation_mode": mode,
        "synthetic_only": True,
        "clinical_validation": False,
        "not_model_performance": mode == "mock",
        "dataset": {
            "reports_version": reports_doc["version"],
            "answer_key_version": keys_doc["version"],
            "report_count": len(reports),
            "evaluated_case_count": len(results),
        },
        "dataset_hashes": {
            "reports.json": sha256_file(str(REPORTS_PATH)),
            "answer_keys.json": sha256_file(str(ANSWER_KEYS_PATH)),
        },
        "provenance": {
            "code_commit": git_commit(),
            "prompt_version": "lumen_prompts_v1",
            "provider": settings.model_provider,
            "generator_model": settings.ollama_model
            if settings.model_provider == "ollama"
            else settings.anthropic_model
            if settings.model_provider == "anthropic"
            else settings.openrouter_model,
            "verifier_model": settings.ollama_verifier_model
            if settings.model_provider == "ollama"
            else settings.anthropic_verifier_model
            if settings.model_provider == "anthropic"
            else settings.openrouter_verifier_model,
            "model_timeout_seconds": settings.model_timeout_seconds,
            "model_max_retries": settings.model_max_retries,
            "max_report_chars": settings.max_report_chars,
            "python_version": sys.version,
        },
        "summary": {
            "cases": len(results),
            "successful_cases": sum(item["status"] == "ok" for item in results),
            "failed_cases": sum(item["status"] == "error" for item in results),
            "extraction": {
                "true_positives": aggregate_tp,
                "false_positives": aggregate_fp,
                "false_negatives": aggregate_fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            },
            "claim_support_rate": "not_measured_requires_human_review",
        },
        "cases": results,
    }

    output = args.output
    if output is None:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        output = RESULTS_DIR / f"eval_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"output": str(output), "mode": mode, "cases": len(results), "extraction_f1": f1},
            indent=2,
        )
    )
    return 0 if not any(item["status"] == "error" for item in results) else 1


def main() -> int:
    args = parse_args()
    if args.timeout and args.mode in {"auto", "live"}:
        os.environ.setdefault("MODEL_TIMEOUT_SECONDS", str(min(args.timeout, 120.0)))
    validate_fixtures()
    if args.dry_run:
        print(
            json.dumps(
                {"status": "dry_run", "report_count": 8, "claim_support_rate": "not_measured"},
                indent=2,
            )
        )
        return 0
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())

