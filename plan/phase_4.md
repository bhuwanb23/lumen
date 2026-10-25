# Phase 4 — Conditional file input, privacy and reviewed language

**Window:** 26 Oct 2026 · **Status:** Conditional/P1 · **Depends on:** Gate 1 green.

## Objective
Ship at most one or two valuable P1 features only if evidence, time, and review capacity support them. This is a decision phase, not a mandate to build everything.

## Go/no-go checkpoint (20 min)
Check core stability, time remaining, fluent reviewer, source mapping, library/API terms, and testability. If any critical condition is missing, defer candidate and spend time in Phase 5.

## Candidate A: PDF/photo (2–3 hours)
Validate file type/MIME, extension, byte cap, dimensions/pages; process ephemerally and clean up; OCR/vision; show/edit extracted text before analysis; cite reviewed OCR text; test blur/skew/empty/encrypted/corrupt and embedded injection; graceful paste fallback. **No-go** if text review, limits, cleanup, or citation mapping unproven.

## Candidate B: Presidio (1–2 hours)
Test custom recognizers on synthetic report PHI; measure misses/false positives; verify script coverage; define reversible mapping from redacted model input to original-source citation; disclose best effort. **No-go** if masking breaks citations or outputs expose identifiers unexpectedly.

## Candidate C: one additional language (1–2 hours plus reviewer)
Select by reviewer availability; translate UI and fixed refusals; keep original source quote; review negation, values, biomarkers, uncertainty, layout, accessibility. **No-go** without fluent medical review: disable locale and state English-only.

## Candidate D: integrations
Verify NCI route/licensing/cache before glossary implementation. Verify ClinicalTrials.gov syntax/status/terms before querying. No guessed API details.

## Deliverables and gate
A feature counts only with tests, privacy/data flow, failure state, patient disclosure and demo proof. Otherwise record defer decision. Re-run Gate 1 afterward. No feature may regress source accuracy, safety or CI.
