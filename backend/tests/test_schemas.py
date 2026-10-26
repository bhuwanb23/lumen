import pytest
from pydantic import ValidationError

from app.schemas import (
    STANDARD_DISCLAIMER,
    AnalysisRequest,
    AnalysisResponse,
    EvidenceSpan,
    ExtractedFact,
    FactExtraction,
)


def test_request_is_strict_and_bounded() -> None:
    valid = AnalysisRequest(report_text="Synthetic report text, sufficiently long.")
    assert valid.language == "en"
    assert valid.reading_level == "simple"
    with pytest.raises(ValidationError):
        AnalysisRequest.model_validate(
            {"report_text": "Synthetic report text, sufficiently long.", "unexpected": True}
        )
    with pytest.raises(ValidationError):
        AnalysisRequest(report_text="   " * 10)
    with pytest.raises(ValidationError):
        AnalysisRequest(report_text="x" * 50_001)
    with pytest.raises(ValidationError):
        AnalysisRequest.model_validate(
            {"report_text": "A sufficiently long report excerpt.", "language": "ta"}
        )


def test_evidence_span_uses_half_open_codepoint_offsets() -> None:
    source = "A😀e\u0301Z"
    start = source.index("Z")
    span = EvidenceSpan(quote="Z", start=start, end=start + 1)
    assert (span.start, span.end) == (4, 5)
    assert source[span.start : span.end] == span.quote
    with pytest.raises(ValidationError):
        EvidenceSpan(quote="😀", start=1, end=3)  # UTF-16 length is not the contract.


def test_fact_status_semantics_are_disjoint() -> None:
    stated = ExtractedFact(
        fact_id="fact_grade",
        field="grade",
        value="Grade 2",
        status="stated",
        evidence=EvidenceSpan(quote="Grade 2", start=0, end=7),
    )
    absent = ExtractedFact(
        fact_id="fact_stage",
        field="stage",
        value=None,
        status="not_stated",
        evidence=None,
    )
    unclear = ExtractedFact(
        fact_id="fact_grade_conflict",
        field="grade",
        value="Conflicting grades are listed.",
        status="unclear",
        evidence=EvidenceSpan(quote="Grade 2 / Grade 3", start=0, end=17),
    )
    assert stated.status == "stated"
    assert absent.value is None and absent.evidence is None
    assert unclear.status == "unclear" and unclear.evidence is not None
    with pytest.raises(ValidationError):
        ExtractedFact(
            fact_id="fact_stage",
            field="stage",
            value="Stage II",
            status="not_stated",
            evidence=None,
        )
    with pytest.raises(ValidationError):
        ExtractedFact(
            fact_id="fact_stage", field="stage", value=None, status="stated", evidence=None
        )


def test_fact_schema_forbids_unknown_fields_and_duplicate_ids() -> None:
    fact = {
        "fact_id": "fact_site",
        "field": "primary_site",
        "value": "lung",
        "status": "stated",
        "evidence": {"quote": "lung", "start": 0, "end": 4},
    }
    with pytest.raises(ValidationError):
        ExtractedFact.model_validate({**fact, "extra": "not allowed"})
    with pytest.raises(ValidationError):
        FactExtraction(
            facts=[ExtractedFact.model_validate(fact), ExtractedFact.model_validate(fact)]
        )


def test_response_requires_fixed_disclaimer_and_consistent_empty_state() -> None:
    base = {
        "status": "no_supported_claims",
        "language": "en",
        "reading_level": "simple",
        "disclaimer": STANDARD_DISCLAIMER,
        "facts": [],
        "claims": [],
        "questions_for_care_team": [],
        "omitted_claim_count": 0,
    }
    assert AnalysisResponse.model_validate(base).status == "no_supported_claims"
    with pytest.raises(ValidationError):
        AnalysisResponse.model_validate({**base, "disclaimer": "This is medical advice."})
    with pytest.raises(ValidationError):
        AnalysisResponse.model_validate({**base, "status": "complete"})
    with pytest.raises(ValidationError):
        AnalysisResponse.model_validate({**base, "extra": "no"})
