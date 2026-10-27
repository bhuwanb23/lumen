"""Single source of truth for the exported JSON-contract version and model map.

Used by scripts/export_contracts.py and tests/test_json_contracts.py so the
version string and model registry cannot drift between exporter and test.
"""

from pydantic import BaseModel

from app.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ApprovedQuestion,
    ClaimCandidate,
    ClaimCitationDraft,
    ClaimDraft,
    ClaimVerificationResult,
    EvidenceSpan,
    ExplanationDraft,
    ExtractedFact,
    FactDraft,
    FactExtraction,
    FactExtractionDraft,
    FactVerificationResult,
    QuestionCandidate,
    SummaryDraft,
    SupportedClaim,
)

CONTRACT_VERSION = "2.0.0"

MODELS: dict[str, type[BaseModel]] = {
    "analysis_request": AnalysisRequest,
    "evidence_span": EvidenceSpan,
    "fact_draft": FactDraft,
    "fact_extraction_draft": FactExtractionDraft,
    "extracted_fact": ExtractedFact,
    "fact_extraction": FactExtraction,
    "fact_verification_result": FactVerificationResult,
    "claim_citation_draft": ClaimCitationDraft,
    "claim_draft": ClaimDraft,
    "explanation_draft": ExplanationDraft,
    "claim_candidate": ClaimCandidate,
    "claim_verification_result": ClaimVerificationResult,
    "question_candidate": QuestionCandidate,
    "summary_draft": SummaryDraft,
    "supported_claim": SupportedClaim,
    "approved_question": ApprovedQuestion,
    "analysis_response": AnalysisResponse,
}
