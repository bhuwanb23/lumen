"""Regenerate checked-in JSON Schema contracts from the Pydantic source models."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.schemas import (  # noqa: E402
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

OUT = ROOT / "contracts"
CONTRACT_VERSION = "2.0.0"
MODELS = {
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    expected_files = {f"{name}.schema.json" for name in MODELS}
    for stale in OUT.glob("*.schema.json"):
        if stale.name not in expected_files:
            stale.unlink()
    for name, model in MODELS.items():
        schema = model.model_json_schema(mode="validation")
        schema["$id"] = f"https://lumen.invalid/contracts/v{CONTRACT_VERSION}/{name}.schema.json"
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["x-contract-version"] = CONTRACT_VERSION
        (OUT / f"{name}.schema.json").write_text(
            json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(f"Wrote {len(MODELS)} Pydantic-derived JSON Schema files to {OUT}")


if __name__ == "__main__":
    main()
