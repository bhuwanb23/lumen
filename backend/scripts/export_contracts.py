"""Regenerate checked-in JSON Schema contracts from the Pydantic source models."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.contracts_config import CONTRACT_VERSION, MODELS  # noqa: E402

OUT = ROOT / "contracts"


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
