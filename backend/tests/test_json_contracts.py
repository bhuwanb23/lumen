import json
from pathlib import Path

from app.contracts_config import CONTRACT_VERSION, MODELS

ROOT = Path(__file__).resolve().parents[1]


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
