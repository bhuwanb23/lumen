"""Deterministic scoring helpers for Lumen synthetic evaluation.

These helpers compare model output to frozen answer keys. They do not imply clinical
validity and do not label claim support, which requires human review.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable
from typing import Any

ABSTAIN_STATUSES = {"not_stated", "unclear"}


def _attr(item: Any, name: str) -> Any:
    if isinstance(item, dict):
        return item.get(name)
    return getattr(item, name, None)


def normalize_text(value: Any) -> str | None:
    """Conservative normalization for comparing short extracted values."""
    if value is None:
        return None
    text = " ".join(str(value).casefold().split())
    return text.strip(" .,:;!?") or None


def fact_key(fact: Any) -> tuple[str, str, str | None]:
    return (
        str(_attr(fact, "field")),
        str(_attr(fact, "status")),
        normalize_text(_attr(fact, "value")),
    )


def score_facts(predicted: Iterable[Any], expected: Iterable[Any]) -> dict[str, Any]:
    """Score predicted facts against frozen expected facts by field and normalized value."""
    predicted_list = list(predicted)
    expected_list = list(expected)
    expected_by_field = {str(_attr(item, "field")): item for item in expected_list}
    predicted_by_field: dict[str, Any] = {}
    for item in predicted_list:
        predicted_by_field.setdefault(str(_attr(item, "field")), item)

    true_positives = 0
    field_results: list[dict[str, Any]] = []
    for expected_fact in expected_list:
        field = str(_attr(expected_fact, "field"))
        predicted_fact = predicted_by_field.get(field)
        matched = predicted_fact is not None and fact_key(predicted_fact) == fact_key(expected_fact)
        if matched:
            true_positives += 1
        field_results.append(
            {
                "field": field,
                "expected_status": _attr(expected_fact, "status"),
                "predicted_status": _attr(predicted_fact, "status") if predicted_fact else None,
                "expected_value": _attr(expected_fact, "value"),
                "predicted_value": _attr(predicted_fact, "value") if predicted_fact else None,
                "match": matched,
            }
        )

    false_positives = 0
    for predicted_fact in predicted_list:
        field = str(_attr(predicted_fact, "field"))
        expected_fact = expected_by_field.get(field)
        if expected_fact is None or fact_key(predicted_fact) != fact_key(expected_fact):
            false_positives += 1
    false_negatives = len(expected_list) - true_positives

    precision = (
        true_positives / (true_positives + false_positives)
        if true_positives + false_positives
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if true_positives + false_negatives
        else 0.0
    )
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "field_results": field_results,
    }


def abstention_metrics(predicted: Iterable[Any], expected: Iterable[Any]) -> dict[str, Any]:
    """Measure preservation of not_stated and unclear field states."""
    predicted_by_field = {str(_attr(item, "field")): item for item in predicted}
    expected_absent = [item for item in expected if _attr(item, "status") in ABSTAIN_STATUSES]
    preserved = 0
    for expected_fact in expected_absent:
        field = str(_attr(expected_fact, "field"))
        predicted_fact = predicted_by_field.get(field)
        if predicted_fact is not None and _attr(predicted_fact, "status") == _attr(
            expected_fact, "status"
        ):
            preserved += 1
    total = len(expected_absent)
    return {
        "expected_absent_fields": total,
        "preserved_absent_fields": preserved,
        "abstention_recall": preserved / total if total else 1.0,
    }


def evidence_quote_validity(facts: Iterable[Any], report_text: str) -> dict[str, Any]:
    """Validate exact quote substrings for stated or unclear facts."""
    total = 0
    valid = 0
    invalid: list[str] = []
    for fact in facts:
        status = _attr(fact, "status")
        if status not in {"stated", "unclear"}:
            continue
        total += 1
        quote = _attr(fact, "evidence_quote")
        if quote is None:
            evidence = _attr(fact, "evidence")
            quote = _attr(evidence, "quote") if evidence is not None else None
        if isinstance(quote, str) and quote and quote in report_text:
            valid += 1
        else:
            invalid.append(str(_attr(fact, "field")))
    return {
        "required_spans": total,
        "valid_quote_substrings": valid,
        "invalid_fields": invalid,
        "quote_validity": valid / total if total else 1.0,
    }


def evidence_span_validity(facts: Iterable[Any], report_text: str) -> dict[str, Any]:
    """Validate exact quote and zero-based code-point offsets."""
    total = 0
    valid = 0
    invalid: list[str] = []
    for fact in facts:
        status = _attr(fact, "status")
        if status not in {"stated", "unclear"}:
            continue
        evidence = _attr(fact, "evidence")
        if evidence is None:
            total += 1
            invalid.append(str(_attr(fact, "field")))
            continue
        quote = _attr(evidence, "quote")
        start = _attr(evidence, "start")
        end = _attr(evidence, "end")
        total += 1
        if (
            isinstance(quote, str)
            and isinstance(start, int)
            and isinstance(end, int)
            and 0 <= start < end <= len(report_text)
            and end - start == len(quote)
            and report_text[start:end] == quote
        ):
            valid += 1
        else:
            invalid.append(str(_attr(fact, "field")))
    return {
        "required_spans": total,
        "valid_exact_spans": valid,
        "invalid_fields": invalid,
        "span_validity": valid / total if total else 1.0,
    }


def claim_citation_validity(
    claims: Iterable[Any], facts: Iterable[Any], report_text: str
) -> dict[str, Any]:
    """Validate that every claim citation points to a stated fact and exact source span."""
    facts_by_id = {str(_attr(fact, "fact_id")): fact for fact in facts}
    total = 0
    valid = 0
    invalid: list[dict[str, Any]] = []
    for claim in claims:
        for citation in _attr(claim, "citations") or []:
            total += 1
            fact_id = str(_attr(citation, "fact_id"))
            evidence = _attr(citation, "evidence")
            fact = facts_by_id.get(fact_id)
            quote = _attr(evidence, "quote")
            start = _attr(evidence, "start")
            end = _attr(evidence, "end")
            citation_ok = (
                fact is not None
                and _attr(fact, "status") != "not_stated"
                and _attr(fact, "evidence") is not None
                and isinstance(quote, str)
                and isinstance(start, int)
                and isinstance(end, int)
                and 0 <= start < end <= len(report_text)
                and end - start == len(quote)
                and report_text[start:end] == quote
            )
            fact_evidence = _attr(fact, "evidence") if fact is not None else None
            if citation_ok and fact_evidence is not None:
                citation_ok = (
                    _attr(fact_evidence, "quote") == quote
                    and _attr(fact_evidence, "start") == start
                    and _attr(fact_evidence, "end") == end
                )
            if citation_ok:
                valid += 1
            else:
                invalid.append({"claim_id": _attr(claim, "claim_id"), "fact_id": fact_id})
    return {
        "citation_count": total,
        "valid_citations": valid,
        "invalid_citations": invalid,
        "citation_validity": valid / total if total else 1.0,
    }


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def latency_summary(values: list[float]) -> dict[str, float | None]:
    return {
        "count": len(values),
        "median_seconds": statistics.median(values) if values else None,
        "p95_seconds": percentile(values, 0.95),
        "min_seconds": min(values) if values else None,
        "max_seconds": max(values) if values else None,
    }


def sha256_file(path: str) -> str:
    import hashlib
    from pathlib import Path

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_commit() -> str | None:
    import subprocess
    from pathlib import Path

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[1]),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None
