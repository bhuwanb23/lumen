"""Print reproducible synthetic-corpus integrity counts; never scores model quality."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS_PATH = ROOT / "eval" / "datasets" / "synthetic" / "reports.json"
ANSWER_KEYS_PATH = ROOT / "eval" / "datasets" / "synthetic" / "answer_keys.json"
REDTEAM_PATH = ROOT / "eval" / "redteam" / "cases.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path.name}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    reports = load(REPORTS_PATH)
    answer_keys = load(ANSWER_KEYS_PATH)
    redteam = load(REDTEAM_PATH)

    report_cases = reports["cases"]
    keyed_cases = answer_keys["cases"]
    report_by_id = {case["case_id"]: case for case in report_cases}
    if set(report_by_id) != {case["case_id"] for case in keyed_cases}:
        raise ValueError("Report and answer-key case IDs do not match")
    if not reports["synthetic_only"] or not all(case["synthetic"] for case in report_cases):
        raise ValueError("Dataset must be explicitly synthetic")

    fact_statuses: Counter[str] = Counter()
    evidence_spans = 0
    exact_matches = 0
    for answer_case in keyed_cases:
        source = report_by_id[answer_case["case_id"]]["report_text"]
        for fact in answer_case["expected_facts"]:
            status = fact["status"]
            fact_statuses[status] += 1
            evidence = fact.get("evidence")
            if status == "not_stated" and evidence is not None:
                raise ValueError(f"not_stated fact unexpectedly has evidence: {fact['fact_id']}")
            if evidence is not None:
                evidence_spans += 1
                start, end, quote = evidence["start"], evidence["end"], evidence["quote"]
                if (
                    not isinstance(start, int)
                    or not isinstance(end, int)
                    or source[start:end] != quote
                ):
                    raise ValueError(
                        f"Gold evidence span mismatch: {answer_case['case_id']} {fact['fact_id']}"
                    )
                exact_matches += 1

    redteam_cases = redteam["cases"]
    summary = {
        "scope": "synthetic fixture integrity only; no model-quality score",
        "reports_version": reports["version"],
        "answer_key_version": answer_keys["version"],
        "report_count": len(report_cases),
        "keyed_case_count": len(keyed_cases),
        "expected_fact_count": sum(fact_statuses.values()),
        "fact_status_counts": dict(sorted(fact_statuses.items())),
        "gold_evidence_span_count": evidence_spans,
        "exact_gold_quote_offset_matches": exact_matches,
        "redteam_case_count": len(redteam_cases),
        "redteam_severity_counts": dict(
            sorted(Counter(case["severity"] for case in redteam_cases).items())
        ),
        "sha256": {
            REPORTS_PATH.name: digest(REPORTS_PATH),
            ANSWER_KEYS_PATH.name: digest(ANSWER_KEYS_PATH),
            REDTEAM_PATH.name: digest(REDTEAM_PATH),
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
