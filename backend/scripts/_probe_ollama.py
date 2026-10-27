"""Temporary diagnostic: surface the raw httpx error for an Ollama extraction call."""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.pipeline import EXTRACTION_SYSTEM  # noqa: E402
from app.providers import inline_json_schema  # noqa: E402
from app.schemas import ALL_FACT_FIELDS, FactExtractionDraft  # noqa: E402

REPO_ROOT = ROOT.parent
DATASET = REPO_ROOT / "eval" / "datasets" / "synthetic" / "reports.json"


def main() -> None:
    settings = Settings()
    report_text = next(
        c["report_text"]
        for c in json.loads(DATASET.read_text(encoding="utf-8"))["cases"]
        if c["case_id"] == "syn_breast_core_001"
    )
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "format": inline_json_schema(FactExtractionDraft),
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": EXTRACTION_SYSTEM},
            {
                "role": "user",
                "content": json.dumps(
                    {"allowed_fields": list(ALL_FACT_FIELDS), "report_text": report_text},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            },
        ],
    }
    url = settings.ollama_base_url.rstrip("/") + "/api/chat"
    print(f"url={url} model={settings.ollama_model} schema_bytes={len(payload['format'])}")

    async def probe() -> None:
        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
            start = time.perf_counter()
            try:
                response = await client.post(
                    url, headers={"content-type": "application/json"}, json=payload
                )
            except httpx.HTTPError as exc:
                elapsed = time.perf_counter() - start
                print(f"HTTPError after {elapsed:.1f}s: {type(exc).__name__}: {exc!r}")
                return
            elapsed = time.perf_counter() - start
            print(f"status={response.status_code} elapsed={elapsed:.1f}s")
            if response.status_code >= 400:
                print(f"error_body={response.text[:500]}")
                return
            body = response.json()
            content = body.get("message", {}).get("content", "")
            parsed = json.loads(content)
            facts = parsed.get("facts", [])
            print(f"facts={len(facts)} valid={len(FactExtractionDraft.model_validate(parsed).facts)}")

    asyncio.run(probe())


if __name__ == "__main__":
    main()
