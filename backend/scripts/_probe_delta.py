"""Temporary diagnostic: delta-debug the full schema to find the grammar-breaking construct."""

from __future__ import annotations

import asyncio
import copy
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


def strip_keys(value: Any, keys: set[str]) -> Any:
    if isinstance(value, list):
        return [strip_keys(v, keys) for v in value]
    if isinstance(value, dict):
        return {k: strip_keys(v, keys) for k, v in value.items() if k not in keys}
    return value


def variants() -> dict[str, dict[str, Any]]:
    full = inline_json_schema(FactExtractionDraft)
    no_titles = strip_keys(full, {"title", "description"})
    no_defaults = strip_keys(full, {"default"})
    no_extra = strip_keys(full, {"additionalProperties"})
    no_limits = strip_keys(full, {"maxLength", "minItems", "maxItems"})
    flat = copy.deepcopy(no_titles)
    item = flat["properties"]["facts"]["items"]
    item["properties"]["value"] = {"type": "string"}
    item["properties"]["evidence_quote"] = {"type": "string"}
    no_anyof = flat
    no_enum = copy.deepcopy(no_titles)
    item = no_enum["properties"]["facts"]["items"]
    item["properties"]["field"] = {"type": "string"}
    item["properties"]["status"] = {"type": "string"}
    return {
        "G_full": full,
        "H_no_titles": no_titles,
        "I_no_defaults": no_defaults,
        "J_no_extra": no_extra,
        "K_no_limits": no_limits,
        "L_no_anyof": no_anyof,
        "M_no_enum": no_enum,
    }


async def main() -> None:
    settings = Settings()
    url = settings.ollama_base_url.rstrip("/") + "/api/chat"
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        for name, schema in variants().items():
            payload = {
                "model": settings.ollama_model,
                "stream": False,
                "format": schema,
                "think": False,
                "options": {"temperature": 0, "num_predict": 8},
                "messages": [{"role": "user", "content": "Reply with the required JSON."}],
            }
            start = time.perf_counter()
            try:
                response = await client.post(url, json=payload)
            except httpx.HTTPError as exc:
                print(f"{name}: HTTPError {type(exc).__name__} {time.perf_counter() - start:.1f}s")
                continue
            elapsed = time.perf_counter() - start
            verdict = "FAIL400" if response.status_code >= 400 else "ok200"
            print(f"{name}: {verdict} after {elapsed:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
