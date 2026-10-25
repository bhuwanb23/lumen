# 02 — Scope and user journeys

## Priority levels
**P0 must ship** for a safe demo; **P1 should ship** only after P0 gate passes; **P2 stretch** is cut first. Code alone does not make a feature done: acceptance, error state, safety copy, and demo behavior must pass.

## P0 — must ship
- Text-first input, synthetic/de-identification warning, character limit.
- Strict structured extraction with exact source quotes and stated/not-stated/unclear distinction.
- Explanation derived only from validated facts; exact quote validation plus independent verifier; fail closed.
- Evidence-linked UI: each claim exposes source quote.
- Scope refusals for diagnosis beyond report, prognosis/survival, treatment, dose, eligibility, urgent triage.
- English; add one other language only if reviewed end to end by a fluent reviewer.
- Synthetic fixtures, hand-authored answer keys, unit/integration/red-team tests.
- Reproducible Docker setup, CI, health route, missing-key and provider-failure handling.
- No-claims, invalid input, and unavailable service states; visible not-medical-advice notice.

## P1 — conditional
Photo/PDF with text preview and correction; Presidio with citation-preserving mapping; NCI exact glossary lookup after access/licensing review; ClinicalTrials.gov matching framed strictly as discussion starter; print card after font tests; accessibility audit and Playwright e2e. Each can be dropped if it threatens safety/evaluation.

## P2 — after event/stretch
Full polished Tamil/Hindi/Spanish support; offline PWA; optional tracing (payload capture off); more cancer/report types; caregiver mode; formal comprehension study and reviewer panel.

## Main journey
1. Prominent prototype/non-medical notice; ask user to use synthetic or de-identified text.
2. Select input (P0 text only), optionally language/reading level actually supported.
3. Validate text length; submit; show calm progress state.
4. Render only claims that pass exact source and verification gates.
5. User opens each citation and sees exact report quotation in a visible accessible panel.
6. Clearly distinguish “not stated,” “unclear,” and “not processed.”
7. Show neutral questions for care team; no therapy suggestions.
8. No save/history/share in MVP; allow clearing the view.

## Out-of-scope request
For prognosis, diagnosis beyond text, treatment choice/dose, trial eligibility, or urgent symptoms, use a fixed, compassionate refusal and refer to care team/local emergency service as appropriate. Do not attempt symptom triage.

## Future file journey
Validate MIME/extension/size/pages/dimensions; extract OCR; show editable extracted text to patient; anchor evidence to reviewed transcription, not claim exact printed-line location unless verified. Low confidence, empty OCR, or lost mapping → stop and offer paste/manual correction. Files are untrusted prompt-injection sources.

## Demo fixtures
Use: straightforward synthetic report; missing stage/marker; ambiguous/contradictory wording; embedded malicious instruction; invalid/short input; model outage; quote that is verbatim but fails to support the whole claim.
