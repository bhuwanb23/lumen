"""Temporary diagnostic: isolate prompt vs schema vs num_predict for the grammar failure."""

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
REPORT = next(
    c["report_text"]
    for c in json.loads(DATASET.read_text(encoding="utf-8"))["cases"]
    if c["case_id"] == "syn_breast_core_001"
)
FULL_SCHEMA = inline_json_schema(FactExtractionDraft)
TRIVIAL_SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
FULL_MESSAGES = [
    {"role": "system", "content": EXTRACTION_SYSTEM},
    {
        "role": "user",
        "content": json.dumps(
            {"allowed_fields": list(ALL_FACT_FIELDS), "report_text": REPORT},
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    },
]
TINY_MESSAGES = [{"role": "user", "content": "Reply with the required JSON."}]

CASES: list[tuple[str, dict, list, dict]] = [
    ("1_fullprompt_fullschema_npredict8", FULL_SCHEMA, FULL_MESSAGES, {"num_predict": 8}),
    ("2_fullprompt_trivialschema_default", TRIVIAL_SCHEMA, FULL_MESSAGES, {}),
    ("3_tinyprompt_fullschema_default", FULL_SCHEMA, TINY_MESSAGES, {}),
    ("4_fullprompt_fullschema_default", FULL_SCHEMA, FULL_MESSAGES, {}),
]


async def main() -> None:
    settings = Settings()
    url = settings.ollama_base_url.rstrip("/") + "/api/chat"
    async with httpx.AsyncClient(timeout=httpx.Timeout(400.0)) as client:
        for name, schema, messages, options in CASES:
            payload = {
                "model": settings.ollama_model,
                "stream": False,
                "format": schema,
                "messages": messages,
                "options": {"temperature": 0, **options},
            }
            start = time.perf_counter()
            try:
                response = await client.post(url, json=payload)
            except httpx.HTTPError as exc:
                print(f"{name}: HTTPError {type(exc).__name__} after {time.perf_counter() - start:.1f}s")
                continue
            elapsed = time.perf_counter() - start
            if response.status_code >= 400:
                print(f"{name}: {response.status_code} after {elapsed:.1f}s  {response.text[:200]}")
            else:
                content = response.json().get("message", {}).get("content", "")
                print(f"{name}: 200 after {elapsed:.1f}s  content_len={len(content)} head={content[:60]!r}")


if __name__ == "__main__":
    asyncio.run(main())
