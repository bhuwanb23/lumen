import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "eval" / "redteam" / "cases.json"
REQUIRED_CATEGORIES = {
    "embedded_instruction",
    "prognosis",
    "treatment_recommendation",
    "dose",
    "diagnosis_beyond_report",
    "urgent_symptoms",
    "trial_eligibility",
    "missing_information",
    "benign_control",
}


def test_redteam_suite_covers_required_scope_and_controls() -> None:
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    cases = suite["cases"]
    categories = {case["category"] for case in cases}
    assert suite["synthetic_only"] is True
    assert len(cases) >= 12
    assert REQUIRED_CATEGORIES <= categories
    assert any(case["category"] == "missing_information" for case in cases)
    assert any(case["is_control"] for case in cases)
    assert any(not case["is_control"] for case in cases)
    for case in cases:
        assert case["case_id"] and case["expected_action"] and case["must_not"]
        assert case["severity"] in {"critical", "high", "control"}
        assert "real" not in case.get("report_text", "").lower()
