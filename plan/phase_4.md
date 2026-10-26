# Phase 4 — Conditional file input, privacy and reviewed language

**Window:** 26 Oct 2026 · **Status:** Complete — no-go on optional features; proceed to Phase 5 · **Depends on:** Gate 1 green.

## Objective
Ship at most one or two valuable P1 features only if evidence, time, and review capacity support them. This is a decision phase, not a mandate to build everything.

## Go/no-go checkpoint — 26 Oct 2026

| Check | Evidence/status | Decision impact |
|---|---|---|
| Core stability | Phase 3 Gate 1 passed; 8/8 Playwright E2E and 61 backend tests. | Green, but not sufficient by itself to expand scope. |
| Time remaining | The plan's assumed cutoff is 28 Oct; roughly two days remain. | Protect Phase 5 evaluation/hardening and submission buffer; avoid optional pipeline risk. |
| Fluent medical-language reviewer | None has been identified or supplied. | Blocks Candidate C; keep English-only. |
| Source mapping | Exact source spans are validated for pasted text. There is no OCR-to-reviewed-text mapping or reversible redaction mapping. | Blocks A and B until independently designed and tested. |
| Library/API terms | No OCR, Presidio, NCI, or ClinicalTrials.gov dependency has been selected or cleared. | Defer integrations; verify terms and data flow before selecting one. |
| Feature-specific testability | Current synthetic/browser suite does not exercise OCR/file safety, PHI-recognizer miss/false-positive rates, translation review, or external integration behavior. | Insufficient proof for a responsible feature release. |

## Candidate decisions

- **A — PDF/photo input: NO-GO / defer.** No OCR pipeline, file limits/cleanup proof, edited-text review step, or reviewed-text citation mapping exists. Keep paste-only input.
- **B — Presidio de-identification: NO-GO / defer.** No custom-recognizer evaluation, miss/false-positive measurements, or verified reversible source mapping exists. Do not represent the current acknowledgement as automated de-identification.
- **C — Additional language: NO-GO / defer.** No fluent medical reviewer is available; keep the interface and safety language English-only.
- **D — Integrations: NO-GO / defer.** No route, API, library, licensing, cache, or terms review was performed; make no integration call and do not guess API details.

No optional feature was added. Continue with Phase 5 evaluation, red-team, accessibility, reliability, and hardening. Re-run Gate 1 because no implementation changed; retain the existing synthetic-only, provider-disabled boundary.

## Gate 1 recheck and scope boundary

Gate 1 was re-run after the go/no-go decision: production build succeeded and E2E again passed **8/8**, including the real same-origin proxy to FastAPI with models disabled. The UI fixture covers exact source quotes, missing facts, omitted claims, refusals, and outage behavior. It demonstrates software behavior only. No live provider, real patient data, clinician review, translation review, or clinical efficacy evidence exists. Docker Compose is still unverified.

**Exit:** Phase 4 is complete as a documented no-go decision. No file, automated de-identification, extra language, or external integration feature is shipped.
