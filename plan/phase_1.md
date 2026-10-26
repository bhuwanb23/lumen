# Phase 1 — Synthetic reports, answer keys and contracts

**Window:** 25 Oct 2026, H2–H3 · **Status:** Complete · **Depends on:** Phase 0.  
**Implementation status:** contracts and synthetic assets authored before any model connection; model/pipeline remains unimplemented.

## Objective
Define a narrow evidence contract and benchmark before connecting a model. Keep the ground truth human-authored and structurally checked.

## Scope decisions
- One report genre: **pathology excerpts only**. Radiology is deliberately deferred; this avoids implying general report coverage.
- Three contexts: **breast, lung, colorectal**.
- Eight fully synthetic reports: three straightforward, a missing-fields case, conflicting-grade case, prompt-injection case, explicit-negation/sampling case, and Unicode-offset case.
- English is the only accepted API locale until a specific fluent reviewer and language are confirmed. Reading-level enum is simple/standard/detailed.
- No model calls or pipeline execution in Phase 1. The corpus and expected behavior were authored independently of model outputs.

## Deliverables completed

### Synthetic corpus and answer keys
- `eval/datasets/synthetic/reports.json`: dataset v1.0.0, 8 report excerpts.
- `eval/datasets/synthetic/answer_keys.json`: 46 hand-authored expected facts; exact quote + computed/verifiable offsets; `stated` / `not_stated` / `unclear`; claim examples with citation IDs and expected `entailed` label; ambiguity notes and forbidden inferences.
- `eval/annotation_guide.md`: annotation labels and review rules.
- `eval/metric_definitions.md`: formulas and denominator rules; explicitly no scores yet.
- `eval/README.md`: data and run instructions.

### Safety suite
- `eval/redteam/cases.json`: 16 synthetic cases, including embedded report instructions, prognosis/survival, treatment, dose, diagnosis beyond report, urgent symptoms, trial eligibility, missing/ambiguous information, and benign controls.
- `eval/redteam/README.md`: states that Phase 1 checks coverage only; no model refusal score exists.

### Typed contracts
- `backend/app/schemas.py`: strict Pydantic v2 request, evidence span, fact, extraction, claim candidate/citation, question candidate, summary draft, and response models. Unknown properties are rejected; request length is bounded; English-only locale is explicit; public claims can only have `verification="supported"`.
- `validate_evidence_links()` checks source substring, half-open offsets, citation-to-fact identity, and blocks citing `not_stated` fields.
- `backend/contracts/`: 8 generated JSON Schemas plus a regeneration guide; a test detects drift from Pydantic.
- Offset convention: zero-based Python Unicode code points, end-exclusive `[start,end)`, exact `report_text` including LF line endings, no Unicode normalization.

### Tests
- Dataset/key integrity, synthetic-only markers, report scope, PHI-like tokens/date patterns, quote/offset exactness, missing vs unclear semantics, red-team category coverage, strict schemas, request bounds, safe response states, evidence links, provider allowlist, and generated-schema drift.

## Acceptance / Gate 1
- [x] Every stated/unclear gold fact has an exact quote and valid offset; fixture tests validate `report[start:end] == quote`.
- [x] Missing facts have `status=not_stated`, null value, and null evidence; unclear conflicts have explicit evidence and are not resolved.
- [x] Unicode and LF line-ending rules documented and tested with a non-BMP emoji and decomposed accent.
- [x] All fixtures marked synthetic; no name/record-number/DOB/SSN-like fixture text; answer keys are hand-authored and separate from reports.
- [x] Pydantic contract rejects extras, bounds input, restricts fields/statuses, fixes the disclaimer, and constrains response claims to supported only.
- [x] Adversarial cases and benign controls have expected actions and `must_not` output criteria.
- [x] Metrics and annotation policy are defined before any model run; no result numbers have been fabricated.
- [x] Lint, type checks, schema-export check, and fixture/red-team tests pass.

## Verification run

- Python 3.12.15; Ruff passes; mypy passes for `app` and `tests`.
- **23 pytest tests pass** (Phase 0 plus Phase 1 contract/data tests).
- JSON Schema export regenerated and matches the Pydantic source in tests.
- No model/API was called. This validates fixture integrity and schema behavior, not model accuracy or clinical safety.

## Exit gate

A reviewer can distinguish stated, absent, and conflicting facts without guessing. Ambiguity is explicitly keyed, offsets are reproducible, and answer keys were not derived from model output. Phase 1 is complete; Phase 2 may now implement the pipeline against these frozen contracts and fixtures. Keep the dataset versioned; changes require a new/updated key and regression review.
