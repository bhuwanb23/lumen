"""Versioned Phase 1 contracts; no model pipeline uses them yet."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SupportedLanguage = Literal["en"]  # Expand only after end-to-end fluent review.
ReadingLevel = Literal["simple", "standard", "detailed"]
FactStatus = Literal["stated", "not_stated", "unclear"]
VerificationState = Literal["pending", "supported", "unsupported", "error"]

Disclaimer = Literal[
    "Lumen explains report wording; it is not medical advice. It does not diagnose, "
    "predict outcomes, or recommend treatment. Confirm meaning with your care team."
]
STANDARD_DISCLAIMER: Disclaimer = (
    "Lumen explains report wording; it is not medical advice. It does not diagnose, "
    "predict outcomes, or recommend treatment. Confirm meaning with your care team."
)

FactField = Literal[
    "report_type",
    "primary_site",
    "cancer_type",
    "histology",
    "grade",
    "stage",
    "margins",
    "lymph_nodes",
    "lymphovascular_invasion",
    "biomarkers",
    "molecular_test_status",
    "distant_metastasis",
    "tumor_size",
    "other_findings",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class AnalysisRequest(StrictModel):
    """Text-only request; preserve source text exactly without Unicode normalization."""

    report_text: str = Field(min_length=20, max_length=50_000)
    language: SupportedLanguage = "en"
    reading_level: ReadingLevel = "simple"

    @model_validator(mode="after")
    def report_must_contain_non_whitespace(self) -> AnalysisRequest:
        if not self.report_text.strip():
            raise ValueError("report_text must contain non-whitespace text")
        return self


class EvidenceSpan(StrictModel):
    """Zero-based Python Unicode-codepoint offsets; end is exclusive; no normalization."""

    quote: str = Field(min_length=1, max_length=2_000)
    start: int = Field(ge=0)
    end: int = Field(gt=0)

    @model_validator(mode="after")
    def offsets_match_quote_length(self) -> EvidenceSpan:
        if self.end <= self.start:
            raise ValueError("evidence span end must be greater than start")
        if self.end - self.start != len(self.quote):
            raise ValueError("span length must equal quote length in Python Unicode code points")
        return self


class ExtractedFact(StrictModel):
    """A report fact or an explicit absence/ambiguity marker with its provenance."""

    fact_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    field: FactField
    value: str | None = Field(max_length=500)
    status: FactStatus
    evidence: EvidenceSpan | None

    @model_validator(mode="after")
    def status_and_evidence_are_consistent(self) -> ExtractedFact:
        if self.status == "stated" and (not self.value or self.evidence is None):
            raise ValueError("stated facts require a value and exact evidence span")
        if self.status == "not_stated" and (self.value is not None or self.evidence is not None):
            raise ValueError("not_stated facts must have null value and evidence")
        if self.status == "unclear" and (not self.value or self.evidence is None):
            raise ValueError("unclear facts require a short ambiguity description and evidence")
        return self


class FactExtraction(StrictModel):
    facts: list[ExtractedFact] = Field(max_length=100)

    @model_validator(mode="after")
    def fact_ids_are_unique(self) -> FactExtraction:
        ids = [fact.fact_id for fact in self.facts]
        if len(ids) != len(set(ids)):
            raise ValueError("fact_id values must be unique")
        return self


class ClaimCitation(StrictModel):
    fact_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    evidence: EvidenceSpan


class ClaimCandidate(StrictModel):
    """Internal candidate: never display unless verification == supported."""

    claim_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    text: str = Field(min_length=1, max_length=500)
    citations: list[ClaimCitation] = Field(min_length=1, max_length=8)
    verification: VerificationState = "pending"


class QuestionCandidate(StrictModel):
    """Internal question candidate; only approved questions can appear in an API response."""

    question_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    text: str = Field(min_length=5, max_length=300, pattern=r"\?\s*$")
    cited_fact_ids: list[str] = Field(min_length=1, max_length=8)
    review_status: Literal["pending", "approved", "rejected"] = "pending"

    @model_validator(mode="after")
    def unique_cited_facts(self) -> QuestionCandidate:
        if len(self.cited_fact_ids) != len(set(self.cited_fact_ids)):
            raise ValueError("question cited_fact_ids must be unique")
        if not self.text.rstrip().endswith("?"):
            raise ValueError("English care-team questions must end with a question mark")
        return self


class SummaryDraft(StrictModel):
    claims: list[ClaimCandidate] = Field(max_length=20)
    questions_for_care_team: list[QuestionCandidate] = Field(max_length=12)


class SupportedClaim(StrictModel):
    """Public response form; unsupported/pending states are not representable here."""

    claim_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    text: str = Field(min_length=1, max_length=500)
    citations: list[ClaimCitation] = Field(min_length=1, max_length=8)
    verification: Literal["supported"] = "supported"


class ApprovedQuestion(StrictModel):
    question_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    text: str = Field(min_length=5, max_length=300, pattern=r"\?\s*$")
    cited_fact_ids: list[str] = Field(min_length=1, max_length=8)
    review_status: Literal["approved"] = "approved"

    @model_validator(mode="after")
    def question_is_punctuated_and_has_unique_citations(self) -> ApprovedQuestion:
        if not self.text.rstrip().endswith("?"):
            raise ValueError("English care-team questions must end with a question mark")
        if len(self.cited_fact_ids) != len(set(self.cited_fact_ids)):
            raise ValueError("question cited_fact_ids must be unique")
        return self


class AnalysisResponse(StrictModel):
    status: Literal["complete", "no_supported_claims"]
    language: SupportedLanguage
    reading_level: ReadingLevel
    disclaimer: Disclaimer = STANDARD_DISCLAIMER
    facts: list[ExtractedFact] = Field(max_length=100)
    claims: list[SupportedClaim] = Field(max_length=20)
    questions_for_care_team: list[ApprovedQuestion] = Field(max_length=8)
    omitted_claim_count: int = Field(ge=0)

    @model_validator(mode="after")
    def response_is_consistent_and_safe(self) -> AnalysisResponse:
        if self.status == "complete" and not self.claims:
            raise ValueError("complete status requires at least one supported claim")
        if self.status == "no_supported_claims" and self.claims:
            raise ValueError("no_supported_claims status requires an empty claims list")
        fact_ids = [fact.fact_id for fact in self.facts]
        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError("response fact_id values must be unique")
        claim_ids = [claim.claim_id for claim in self.claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("response claim_id values must be unique")
        question_ids = [question.question_id for question in self.questions_for_care_team]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("response question_id values must be unique")
        known = set(fact_ids)
        for claim in self.claims:
            if any(citation.fact_id not in known for citation in claim.citations):
                raise ValueError("claim citation references an unknown fact_id")
        for question in self.questions_for_care_team:
            if any(fact_id not in known for fact_id in question.cited_fact_ids):
                raise ValueError("question references an unknown fact_id")
        return self


def validate_evidence_links(
    source_text: str,
    facts: list[ExtractedFact],
    *,
    claims: Sequence[ClaimCandidate] | Sequence[SupportedClaim] = (),
    questions: Sequence[QuestionCandidate] | Sequence[ApprovedQuestion] = (),
) -> None:
    """Validate exact quote, offset, and fact-link integrity against the untouched source text."""
    fact_by_id = {fact.fact_id: fact for fact in facts}
    if len(fact_by_id) != len(facts):
        raise ValueError("fact_id values must be unique")

    def check_span(span: EvidenceSpan) -> None:
        if span.end > len(source_text) or source_text[span.start : span.end] != span.quote:
            raise ValueError("evidence quote/offset does not exactly match source text")

    for fact in facts:
        if fact.evidence is not None:
            check_span(fact.evidence)

    for claim in claims:
        for citation in claim.citations:
            cited_fact = fact_by_id.get(citation.fact_id)
            if (
                cited_fact is None
                or cited_fact.status == "not_stated"
                or cited_fact.evidence is None
            ):
                raise ValueError("claim cites a missing or not-stated fact")
            check_span(citation.evidence)
            if citation.evidence != cited_fact.evidence:
                raise ValueError("claim citation must match the cited fact's exact evidence span")

    for question in questions:
        for fact_id in question.cited_fact_ids:
            cited_fact = fact_by_id.get(fact_id)
            if (
                cited_fact is None
                or cited_fact.status == "not_stated"
                or cited_fact.evidence is None
            ):
                raise ValueError("question cites a missing or not-stated fact")
            check_span(cited_fact.evidence)
