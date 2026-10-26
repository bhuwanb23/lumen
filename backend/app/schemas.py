"""Versioned contracts for source-grounded report explanation; no schema is a medical validation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, model_validator

SupportedLanguage = Literal["en"]  # Expand only after end-to-end fluent review.
ReadingLevel = Literal["simple", "standard", "detailed"]
FactStatus = Literal["stated", "not_stated", "unclear"]
VerificationState = Literal["pending", "supported", "unsupported", "error"]
RefusalCategory = Literal[
    "prognosis",
    "treatment",
    "dose",
    "diagnosis",
    "urgent_symptoms",
    "trial_eligibility",
    "policy_evasion",
]

Disclaimer = Literal[
    "Lumen explains report wording; it is not medical advice. It does not diagnose, "
    "predict outcomes, or recommend treatment. Confirm meaning with your care team."
]
SafeQueryNotice = Literal[
    "I can't guess missing information. Fields marked 'Not stated in this excerpt' are absent "
    "from the submitted text; ask your care team to clarify."
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
ALL_FACT_FIELDS = get_args(FactField)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class AnalysisRequest(StrictModel):
    """Text-only request; preserve source text exactly without Unicode normalization."""

    report_text: str = Field(min_length=20, max_length=50_000)
    user_question: str | None = Field(default=None, max_length=500)
    language: SupportedLanguage = "en"
    reading_level: ReadingLevel = "simple"
    data_is_synthetic_or_deidentified: bool = False
    external_processing_acknowledged: bool = False

    @model_validator(mode="after")
    def request_text_is_valid(self) -> AnalysisRequest:
        if not self.report_text.strip():
            raise ValueError("report_text must contain non-whitespace text")
        if self.user_question is not None and not self.user_question.strip():
            raise ValueError("user_question must be omitted or contain non-whitespace text")
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


class FactDraft(StrictModel):
    """Model extraction form: exact quote only; offsets are calculated by the server."""

    field: FactField
    value: str | None = Field(max_length=500)
    status: FactStatus
    evidence_quote: str | None = Field(default=None, max_length=2_000)

    @model_validator(mode="after")
    def status_matches_quote_presence(self) -> FactDraft:
        if self.status == "stated" and (not self.value or not self.evidence_quote):
            raise ValueError("stated facts require a value and verbatim evidence_quote")
        if self.status == "not_stated" and (
            self.value is not None or self.evidence_quote is not None
        ):
            raise ValueError("not_stated facts must have null value and evidence_quote")
        if self.status == "unclear" and (not self.value or not self.evidence_quote):
            raise ValueError("unclear facts require an ambiguity description and evidence_quote")
        return self


class FactExtractionDraft(StrictModel):
    """The extraction model must account for every allowlisted field exactly once."""

    facts: list[FactDraft] = Field(min_length=14, max_length=14)

    @model_validator(mode="after")
    def all_fields_appear_once(self) -> FactExtractionDraft:
        fields = [fact.field for fact in self.facts]
        if len(fields) != len(set(fields)) or set(fields) != set(ALL_FACT_FIELDS):
            raise ValueError("extraction must contain each allowed field exactly once")
        return self


class ExtractedFact(StrictModel):
    """Canonical fact with deterministic ID and exact server-calculated source span."""

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


class FactVerificationResult(StrictModel):
    """Verifier whitelists fully supported facts; omitted IDs are rejected."""

    supported_fact_ids: list[str] = Field(max_length=14)

    @model_validator(mode="after")
    def unique_fact_ids(self) -> FactVerificationResult:
        if len(self.supported_fact_ids) != len(set(self.supported_fact_ids)):
            raise ValueError("supported_fact_ids must be unique")
        return self


class ClaimCitationDraft(StrictModel):
    fact_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    evidence_quote: str = Field(min_length=1, max_length=2_000)


class ClaimDraft(StrictModel):
    """Unverified model claim; IDs and offsets are assigned/checked by the server."""

    text: str = Field(min_length=1, max_length=500)
    citations: list[ClaimCitationDraft] = Field(min_length=1, max_length=8)


class ExplanationDraft(StrictModel):
    claims: list[ClaimDraft] = Field(max_length=20)


class ClaimCitation(StrictModel):
    fact_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    evidence: EvidenceSpan


class ClaimCandidate(StrictModel):
    """Internal candidate: never display unless verification == supported."""

    claim_id: str = Field(pattern=r"^[a-z][a-z0-9_]{1,47}$")
    text: str = Field(min_length=1, max_length=500)
    citations: list[ClaimCitation] = Field(min_length=1, max_length=8)
    verification: VerificationState = "pending"


class ClaimVerificationResult(StrictModel):
    """Verifier whitelists fully supported claim IDs; omitted IDs are rejected."""

    supported_claim_ids: list[str] = Field(max_length=20)

    @model_validator(mode="after")
    def unique_claim_ids(self) -> ClaimVerificationResult:
        if len(self.supported_claim_ids) != len(set(self.supported_claim_ids)):
            raise ValueError("supported_claim_ids must be unique")
        return self


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
    """General contract draft retained for compatibility; pipeline uses ExplanationDraft."""

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
    status: Literal["complete", "no_supported_claims", "refused"]
    language: SupportedLanguage
    reading_level: ReadingLevel
    disclaimer: Disclaimer = STANDARD_DISCLAIMER
    facts: list[ExtractedFact] = Field(max_length=100)
    claims: list[SupportedClaim] = Field(max_length=20)
    questions_for_care_team: list[ApprovedQuestion] = Field(max_length=8)
    omitted_claim_count: int = Field(ge=0)
    query_notice: SafeQueryNotice | None = None
    refusal_category: RefusalCategory | None = None
    refusal_message: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def response_is_consistent_and_safe(self) -> AnalysisResponse:
        if self.status == "complete" and not self.claims:
            raise ValueError("complete status requires at least one supported claim")
        if self.status == "no_supported_claims" and self.claims:
            raise ValueError("no_supported_claims status requires an empty claims list")
        if self.status == "refused":
            if (
                self.refusal_category is None
                or self.query_notice is not None
                or not self.refusal_message
                or self.facts
                or self.claims
                or self.questions_for_care_team
                or self.omitted_claim_count != 0
            ):
                raise ValueError("refusal responses must be fixed and contain no report analysis")
        elif self.refusal_category is not None or self.refusal_message is not None:
            raise ValueError("non-refusal response cannot contain refusal details")
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
    """Validate exact quote, offset, and fact-link integrity against untouched source text."""
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
