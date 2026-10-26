# Phase 5 — Evaluation, accessibility, reliability and hardening

**Window:** 26 Oct evening–27 Oct morning · **Status:** Software hardening complete for this pass; Gate 2 blocked · **Depends on:** Gate 1 and frozen optional work.

## Objective
Measure the system, fix critical defects, and produce an honest release candidate. No broad new features.

## Completed this pass

1. **Synthetic evaluation baseline:** kept the v1.0.0 hand-authored dataset/answer keys frozen. Verified 8 reports, 46 expected field labels, and exact gold evidence substring/offset validity for 34/34 non-null spans. Metrics requiring generated model outputs or human review are reported as **not measured**. Reproducible counts/hashes: `python eval/scripts/fixture_integrity.py`; full details: [`eval/phase_5_report.md`](../eval/phase_5_report.md).
2. **Red-team and fail-closed behavior:** inspected the 16 synthetic red-team cases (8 critical, 3 high, 5 controls). Added mock-provider coverage for bounded 429/503 retries and a generic, non-retried 401 response. Existing injection, refusal, missing/ambiguous fact, verifier, timeout and redaction tests remain green. No live model was used; model-specific outcomes are unknown.
3. **Accessibility/localization:** added axe-core Playwright scans of the form and synthetic rendered result; 0 WCAG 2.1 A/AA violations in tested desktop states. Keyboard source interaction, skip link, mobile 390/320 px reflow are tested. English-only remains accurate. Manual screen-reader and actual browser zoom review remain outstanding.
4. **Reliability/security:** added E2E checks for 415/400/413, no-store, response non-echo, health behavior and security headers. Backend tests cover CORS, body limits, provider timeouts, mocked invalid key, 429/503 and redaction. Added axe dependency. `npm audit` is clean. `pip-audit` found vulnerable pytest 8.4.2 (`PYSEC-2026-1845` / `CVE-2025-71176`), so the dev constraint and `uv.lock` were updated; pytest 9.1.1 passes and Python re-audit is clean. No application-level public rate limiter exists; avoid untrusted public exposure until reviewed.
5. **Report:** [`eval/phase_5_report.md`](../eval/phase_5_report.md) records dataset hashes, test counts, measured fixture-integrity results, unknown model metrics, limitations and Gate 2 decision.

## Verification

- Backend: **64 pytest tests passed**; Ruff check/format and mypy passed.
- Frontend: lint/typecheck passed; production build passed as part of E2E; **10/10 Playwright tests passed**.
- Dependency scans: `npm audit` zero vulnerabilities; `pip-audit` found no known vulnerabilities after pytest upgrade.
- Axe: zero automated WCAG 2.1 A/AA violations on tested form/result states.
- Live-provider calls: none. Docker Compose: not tested.

## Gate 2 — not passed

- [x] Critical automated tests and static checks green locally.
- [ ] No unresolved critical unsafe model result — **not assessable; no model output exists**.
- [x] Source-link checks and verifier failure hiding covered by tests.
- [ ] Reproducible model results/human unsupported-claim labels — **not measured**.
- [ ] Accessibility blockers/manual screen-reader/actual zoom check — automated checks pass; manual review remains.
- [x] Mocked provider errors, data flow, bounds and redaction pass software tests; live provider/deployment not validated.
- [x] Optional features cut where evidence/review capacity was missing.

## Blockers and next steps

Do not claim a model-evaluated or clinical release candidate. Gate 2 remains blocked until a deliberately configured and reviewed provider/model run is available, frozen-set outputs receive human claim-level review (preferably independent review/adjudication), manual screen-reader/zoom checks are completed, and the intended deployment/abuse controls are assessed. Preserve all metrics as “not measured” until that evidence exists. No clinical validation or efficacy claim is supported.
