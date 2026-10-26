# Phase 1 evaluation assets

## Scope and status

- Dataset: `datasets/synthetic/reports.json` + hand-authored `datasets/synthetic/answer_keys.json`, version 1.0.0.
- Safety prompts: `redteam/cases.json`, version 1.0.0.
- All report text is fictional and created for this project. There is no real or copied patient text. The content has not been reviewed or clinically validated by an oncology professional.
- Coverage is intentionally narrow: pathology excerpts only; breast, lung, colorectal contexts; eight examples. This is fixture/contract validation, not a representative clinical benchmark.
- **No model evaluation has been run** (Phase 5, 26 Oct 2026). Fixture span integrity is measured separately in [`phase_5_report.md`](phase_5_report.md); no output-quality metric is populated.

## Run fixture and schema checks

```bash
cd backend
uv sync --python 3.12.15 --dev
uv run pytest -q
uv run python scripts/export_contracts.py
```

Tests verify case/key alignment, exact quotes and offsets, status distinctions, strict schema behavior, red-team category coverage, and provider configuration allowlisting. They do not test model accuracy.

## Dataset conventions

Offsets are zero-based Python Unicode-code-point indices into the exact `report_text` value, with end exclusive. Report strings use LF line endings. Do not normalize Unicode or line endings before checking evidence. Each stated/unclear fact has a verbatim quote; not-stated facts have null value and null evidence.

`allowed_claim_examples` are human-authored examples of claims that may be supportable when cited facts are present; they are not model outputs and do not replace claim-level entailment review. `forbidden_inferences` record known traps per case.

Annotation and metric definitions are in [`annotation_guide.md`](annotation_guide.md) and [`metric_definitions.md`](metric_definitions.md).

## Metrics status

Reproduce synthetic fixture counts, gold quote/offset integrity, red-team case counts, and asset hashes with `python eval/scripts/fixture_integrity.py` from the repository root. This script does not call a model or produce quality scores.

Phase 1 tests validate fixture integrity. The Phase 5 report records the frozen fixture counts and exact gold-span checks, while extraction precision/recall, unsupported-claim rate, verifier benefit, refusal success, false refusals, readability, translation quality, and provider latency remain **not measured**. Those require model outputs, human annotation, and run provenance. Never report fixture-integrity checks as model or clinical accuracy.
