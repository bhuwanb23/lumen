import pytest

from app.schemas import (
    ClaimCandidate,
    ClaimCitation,
    EvidenceSpan,
    ExtractedFact,
    validate_evidence_links,
)


def test_evidence_quote_and_offsets_must_match_source_exactly() -> None:
    source = "Finding: A😀B."
    fact = ExtractedFact(
        fact_id="fact_find",
        field="other_findings",
        value="A emoji B",
        status="stated",
        evidence=EvidenceSpan(quote="A😀B", start=9, end=12),
    )
    validate_evidence_links(source, [fact])
    wrong = fact.model_copy(update={"evidence": EvidenceSpan(quote="A B", start=9, end=12)})
    with pytest.raises(ValueError, match="does not exactly match"):
        validate_evidence_links(source, [wrong])


def test_claim_must_cite_a_matching_stated_fact() -> None:
    source = "Grade 2."
    fact = ExtractedFact(
        fact_id="fact_grade",
        field="grade",
        value="Grade 2",
        status="stated",
        evidence=EvidenceSpan(quote="Grade 2", start=0, end=7),
    )
    assert fact.evidence is not None
    claim = ClaimCandidate(
        claim_id="claim_grade",
        text="The report says Grade 2.",
        citations=[ClaimCitation(fact_id="fact_grade", evidence=fact.evidence)],
        verification="supported",
    )
    validate_evidence_links(source, [fact], claims=[claim])
    bad_quote_claim = claim.model_copy(
        update={
            "citations": [
                ClaimCitation(
                    fact_id="fact_grade", evidence=EvidenceSpan(quote="Grade 3", start=0, end=7)
                )
            ]
        }
    )
    with pytest.raises(ValueError):
        validate_evidence_links(source, [fact], claims=[bad_quote_claim])


def test_not_stated_fact_cannot_support_claim() -> None:
    fact = ExtractedFact(
        fact_id="fact_stage",
        field="stage",
        value=None,
        status="not_stated",
        evidence=None,
    )
    forged = ClaimCandidate.model_construct(
        claim_id="claim_stage",
        text="The report says stage II.",
        citations=[
            ClaimCitation.model_construct(
                fact_id="fact_stage",
                evidence=EvidenceSpan.model_construct(quote="stage", start=0, end=5),
            )
        ],
        verification="supported",
    )
    with pytest.raises(ValueError, match="not-stated"):
        validate_evidence_links("stage", [fact], claims=[forged])


def test_evidence_cannot_extend_past_source() -> None:
    fact = ExtractedFact(
        fact_id="fact_site",
        field="primary_site",
        value="colon",
        status="stated",
        evidence=EvidenceSpan(quote="colon", start=3, end=8),
    )
    with pytest.raises(ValueError, match="does not exactly match"):
        validate_evidence_links("colon", [fact])
