# Phase 3 — Patient UI and vertical demo loop

**Window:** 25 Oct 2026, H8–H10 · **Status:** Complete on 26 Oct 2026 (one day after target) · **Depends on:** Phase 2.

## Objective
Build a responsive interface for report text, evidence, clinician questions and honest limitations.

## Delivered
- Accessible, responsive, English-only text interface with visible non-medical/synthetic-data/external-processing notices; no upload control.
- Bounded, consent-gated excerpt form with native validation, busy state, generic fail-closed errors, no report persistence in URL/browser storage/console, and same-origin API proxy with request-size cap, timeout and no-store behavior.
- Fail-closed response validation; cited source spans must match the submitted text. Each claim's keyboard-accessible source control opens an exact quote panel. Includes multiple citations, neutral care-team questions, explicit `not stated`, no-claims, omitted-claim, refusal and outage states.
- UI-only synthetic presentation fixture kept separate from evaluation answer keys, plus E2E and manual checklists in `frontend/e2e/README.md`.
- Standalone production Next server starts with static assets staged for local runs. Docker Compose remains untested in this workspace.

## Verification and Gate 1
All software-facing checks listed below passed. `npm run test:e2e` rebuilt production output and passed **8/8** Playwright tests after correcting the standalone server/static-asset setup. The real browser → same-origin Next proxy → FastAPI scenario ran with `MODEL_PROVIDER=disabled`; it verified safe handling of the unavailable-provider response, not a live model-powered positive result. No provider credentials, real patient data, clinician review, or clinical efficacy evidence were used.

- [x] Synthetic text submission through the UI to a rendered result; busy, disabled, and short-input validation states.
- [x] Citation source controls reveal exact matching source text; includes multiple citations and keyboard operation.
- [x] Missing fields remain explicitly unstated; no-claims and omitted-claim states are tested.
- [x] Purpose, non-medical limitations, synthetic/de-identification restriction, and configured-provider/external-processing disclosure are shown before analysis; results reiterate limitations and clinician confirmation.
- [x] No-claims, fixed-refusal, provider-disabled, and service-outage states are calm and fail-closed.
- [x] Mobile viewport width and keyboard navigation are tested.
- [x] No upload control; browser test checks same-origin requests, credential names absent from loaded scripts, empty local/session storage, and no query-string payload. Proxy source avoids logging report bodies/upstream errors; backend redaction is covered by tests.

Verification run: backend regression `python -m pytest -q` (61 passed); frontend `npm run lint`, `npm run typecheck`, `npm audit` (zero vulnerabilities), production `npm run build`, and `LD_LIBRARY_PATH=/tmp/lumen-playwright-libs/usr/lib/x86_64-linux-gnu npm run test:e2e` (8 passed). Production preview on port 3000 returned HTTP 200 for `/api/health`; the disabled-provider analyze smoke test returned a generic HTTP 503 with no claims.

**Scope boundary:** Gate 1 means the prototype UI and software checks are complete; it is not approval for patient-facing clinical use. Live provider compatibility/privacy, Docker Compose, clinician review, and clinical validation remain outstanding.
