import json
from pathlib import Path

from pydantic import BaseModel

from app.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ClaimCandidate,
    EvidenceSpan,
    ExtractedFact,
    FactExtraction,
    QuestionCandidate,
    SummaryDraft,
)

ROOT = Path(__file__).resolve().parents[1]
MODELS: dict[str, type[BaseModel]] = {
    "analysis_request": AnalysisRequest,
    "evidence_span": EvidenceSpan,
    "extracted_fact": ExtractedFact,
    "fact_extraction": FactExtraction,
    "claim_candidate": ClaimCandidate,
    "question_candidate": QuestionCandidate,
    "summary_draft": SummaryDraft,
    "analysis_response": AnalysisResponse,
}


def test_checked_in_json_schemas_match_pydantic_source() -> None:
    for name, model in MODELS.items():
        path = ROOT / "contracts" / f"{name}.schema.json"
        committed = json.loads(path.read_text(encoding="utf-8"))
        generated = model.model_json_schema(mode="validation")
        generated["$id"] = f"https://lumen.invalid/contracts/v1.0.0/{name}.schema.json"
        generated["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        generated["x-contract-version"] = "1.0.0"
        assert committed == generated, (
            f"{name} JSON Schema is stale; run scripts/export_contracts.py"
        )
