"""Temporary diagnostic: bisect which JSON-schema construct breaks Ollama grammar parsing."""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.providers import inline_json_schema  # noqa: E402
from app.schemas import FactExtractionDraft  # noqa: E402

VARIANTS: dict[str, dict[str, Any]] = {
    "A_trivial": {"type": "object", "properties": {"ok": {"type": "boolean"}}},
    "B_enum": {
        "type": "object",
        "properties": {"field": {"type": "string", "enum": ["a", "b"]}},
        "required": ["field"],
    },
    "C_anyof_null": {
        "type": "object",
        "properties": {
            "value": {"anyOf": [{"type": "string", "maxLength": 5}, {"type": "null"}]}
        },
        "required": ["value"],
    },
    "D_extra_desc": {
        "type": "object",
        "description": "A description.",
        "properties": {"x": {"type": "string", "title": "X"}},
        "additionalProperties": False,
    },
    "E_array_bounds": {
        "type": "object",
        "properties": {
            "items": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 2}
        },
        "required": ["items"],
    },
    "F_default": {
        "type": "object",
        "properties": {"x": {"type": "string", "default": None}},
        "required": ["x"],
    },
    "G_full_schema": inline_json_schema(FactExtractionDraft),
}


async def main() -> None:
    settings = Settings()
    url = settings.ollama_base_url.rstrip("/") + "/api/chat"
    async with httpx.AsyncClient(timeout=httpx.Timeout(90.0)) as client:
        for name, schema in VARIANTS.items():
            payload = {
                "model": settings.ollama_model,
                "stream": False,
                "format": schema,
                "options": {"temperature": 0, "num_predict": 8},
                "messages": [{"role": "user", "content": "Reply with the required JSON."}],
            }
            start = time.perf_counter()
            try:
                response = await client.post(url, json=payload)
            except httpx.HTTPError as exc:
                print(f"{name}: HTTPError {type(exc).__name__} after {time.perf_counter() - start:.1f}s")
                continue
            elapsed = time.perf_counter() - start
            if response.status_code >= 400:
                body = response.text[:200]
                print(f"{name}: {response.status_code} after {elapsed:.1f}s  {body}")
            else:
                content = response.json().get("message", {}).get("content", "")
                print(f"{name}: 200 after {elapsed:.1f}s  content={content[:80]!r}")


if __name__ == "__main__":
    asyncio.run(main())
