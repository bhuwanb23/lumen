import json
import re
from pathlib import Path
from typing import Any, cast

from app.schemas import ExtractedFact, validate_evidence_links

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "eval" / "datasets" / "synthetic"
PII_LIKE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:MRN|DOB|SSN|medical record number)\b",
        r"\b\d{3}-\d{2}-\d{4}\b",
        r"\b\d{2}/\d{2}/\d{4}\b",
    )
]


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def test_synthetic_reports_and_answer_keys_are_complete_and_linked() -> None:
    reports_doc = load_json(DATA_DIR / "reports.json")
    keys_doc = load_json(DATA_DIR / "answer_keys.json")
    reports = {item["case_id"]: item for item in reports_doc["cases"]}
    keys = {item["case_id"]: item for item in keys_doc["cases"]}

    assert reports_doc["synthetic_only"] is True
    assert reports_doc["medical_reviewed"] is False
    assert keys_doc["medical_reviewed"] is False
    assert keys_doc["version"] == reports_doc["version"] == "1.0.0"
    assert len(reports) == len(keys) == 8
    assert set(reports) == set(keys)
    assert set(reports_doc["report_genres"]) == {"pathology"}
    assert set(reports_doc["cancer_contexts"]) == {"breast", "lung", "colorectal"}

    for case_id, report in reports.items():
        key = keys[case_id]
        assert report["synthetic"] is True and key["synthetic"] is True
        text = report["report_text"]
        assert "\r" not in text, "fixtures use canonical LF line endings"
        assert not any(pattern.search(text) for pattern in PII_LIKE_PATTERNS)
        facts = [ExtractedFact.model_validate(fact) for fact in key["expected_facts"]]
        validate_evidence_links(text, facts)
        fact_by_id = {fact.fact_id: fact for fact in facts}
        assert len(fact_by_id) == len(facts)
        for example in key["allowed_claim_examples"]:
            assert example["text"] and example["cites"]
            assert example["expected_support_label"] == "entailed"
            for fact_id in example["cites"]:
                assert fact_id in fact_by_id
                assert fact_by_id[fact_id].status != "not_stated"
        assert key["forbidden_inferences"]
        assert key["ambiguity_notes"]


def test_missing_and_ambiguous_cases_are_distinct() -> None:
    reports_doc = load_json(DATA_DIR / "reports.json")
    keys_doc = load_json(DATA_DIR / "answer_keys.json")
    keys = {item["case_id"]: item for item in keys_doc["cases"]}

    missing = {
        fact["field"]: fact for fact in keys["syn_breast_missing_fields_001"]["expected_facts"]
    }
    assert missing["stage"]["status"] == "not_stated"
    assert missing["stage"]["value"] is None and missing["stage"]["evidence"] is None

    ambiguous = {
        fact["field"]: fact for fact in keys["syn_lung_conflicting_grade_001"]["expected_facts"]
    }
    grade = ambiguous["grade"]
    assert grade["status"] == "unclear"
    assert grade["evidence"]["quote"] == "Grade: 2.\nAddendum: Grade: 3."
    assert grade["value"] == "The excerpt lists conflicting grade values (2 and 3)."
    assert reports_doc["offset_convention"].startswith("Zero-based Python Unicode code-point")


def test_unicode_case_offsets_are_codepoint_offsets_not_normalized() -> None:
    reports_doc = load_json(DATA_DIR / "reports.json")
    keys_doc = load_json(DATA_DIR / "answer_keys.json")
    report = next(c for c in reports_doc["cases"] if c["case_id"] == "syn_unicode_offset_001")
    key = next(c for c in keys_doc["cases"] if c["case_id"] == "syn_unicode_offset_001")
    text = report["report_text"]
    assert "🧪" in text
    assert "e\u0301" in text
    assert "é" not in text
    fact = next(f for f in key["expected_facts"] if f["field"] == "tumor_size")
    span = fact["evidence"]
    assert text[span["start"] : span["end"]] == span["quote"] == "Tumor size: 1.4 cm."
