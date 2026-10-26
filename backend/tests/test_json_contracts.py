import json
from pathlib import Path

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

ROOT = Path(__file__).resolve().parents[1]
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


def test_checked_in_json_schemas_match_pydantic_source() -> None:
    for name, model in MODELS.items():
        path = ROOT / "contracts" / f"{name}.schema.json"
        committed = json.loads(path.read_text(encoding="utf-8"))
        generated = model.model_json_schema(mode="validation")
        generated["$id"] = f"https://lumen.invalid/contracts/v{CONTRACT_VERSION}/{name}.schema.json"
        generated["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        generated["x-contract-version"] = CONTRACT_VERSION
        assert committed == generated, (
            f"{name} JSON Schema is stale; run scripts/export_contracts.py"
        )
