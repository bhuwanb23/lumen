# Phase 5 — Evaluation, accessibility, reliability and hardening report

**Run date:** 2026-10-26 (IST)  
**Status:** Software hardening complete for this pass; **Gate 2 is not passed**.  
**Product boundary:** synthetic-only prototype; provider disabled; no clinical or patient-use approval.

## Executive result

The repeatable software checks are green: 64 backend tests, 10 Playwright E2E tests, frontend lint/typecheck/build, Ruff/mypy, axe scans, and frontend/backend dependency audits. The backend dependency audit found a pytest advisory; pytest was upgraded and the re-audit is clean. The frozen synthetic corpus is internally span-consistent. **No live model evaluation or human claim review was run**, so model quality/safety metrics remain unmeasured and Gate 2 cannot establish clinical safety or model readiness.

## Frozen synthetic assets and provenance

| Asset | Version / N | SHA-256 |
|---|---:|---|
| `eval/datasets/synthetic/reports.json` | 1.0.0 / 8 fictional reports | `a0d9ca524c8f99e21d5096299161c3227145c7be94317168684dfeffd8d10ca0` |
| `eval/datasets/synthetic/answer_keys.json` | 1.0.0 / 8 hand-authored keys | `1ff159f761e579412100aaced680f791d15d1dd9b2627d0d08912feb9cd7fbda` |
| `eval/redteam/cases.json` | v1 / 16 synthetic cases | `4f130cb590586a0ad032031cf83411e1095a53f0a7cf94fbcee3244794af5ab7` |

The 8-case corpus has 46 expected fact labels: 33 `stated`, 12 `not_stated`, and 1 `unclear`. It includes 34 non-null evidence spans; every gold span exactly matched its quoted substring and `[start,end)` offsets (**34/34**). This is a fixture-integrity check only—not extraction accuracy, semantic support, or clinical validation. Reproduce the counts and hashes with `python eval/scripts/fixture_integrity.py` from the repository root. The 16 red-team fixtures comprise 8 critical cases, 3 high-severity cases, and 5 benign controls across 9 categories. Static case inventory is not a model-output evaluation.

## Model and clinical evaluation metrics

| Metric | Result | Why / scope |
|---|---|---|
| Extraction precision / recall / F1 | **Not measured** | No generator model was configured or called. |
| Predicted quote/span validity | **Not measured** | Gold fixture spans were validated 34/34; there are no model predictions to score. |
| Claim unsupported rate before/after verifier | **Not measured** | No model claims or human entailment labels; reviewer count 0. |
| Missing-field abstention / ambiguity preservation | **Not measured for a model** | UI and deterministic pipeline behavior are covered by synthetic/mock tests only. |
| Refusal success / benign false-refusal rate | **Not measured for a model** | Deterministic fixed refusals and classifier paths have unit tests; no generated answers were adjudicated. |
| Provider/model latency and failure rate | **Not measured** | No live provider calls; test runtime is not model latency. |
| Translation/readability/clinical review | **Not measured** | English-only; no fluent medical-language reviewer supplied. |

**Model run provenance:** provider `disabled`; generator/verifier model IDs `none`; prompt/model evaluation version `not applicable`; model run N=0. No API credentials, external model requests, real patient data, or clinician reviews were used.

## Red-team, safety and reliability checks

- The red-team case file and expected-action labels were inspected. Automated regression coverage includes embedded prompt-injection text, deterministic refusals for prognosis/treatment/dose/trial eligibility/urgent symptoms/policy evasion, missing-information handling, verifier rejection, timeout/failure behavior, and safe redaction.
- Added provider-adapter mock tests verify bounded retries for upstream HTTP 429/503, no retry for a simulated invalid-key 401, generic errors without provider-body leakage, and timeout retry bounds. These are mocks, not live credential/provider tests.
- Existing backend API tests cover malformed/oversized input and redacted failure responses. CORS tests allow only configured frontend origins.
- Added Next proxy E2E checks: wrong content type → 415, malformed JSON → 400, >1 MB body → 413; errors are no-store and do not echo the submitted payload. The health route is no-store; security headers (`nosniff`, `DENY`, `no-referrer`, restrictive Permissions-Policy) are asserted; `X-Powered-By` is absent.
- Browser checks confirm same-origin requests only, no provider host requests or provider key names in loaded scripts, no local/session storage or query-string payload, and no stale claims on outage. Source inspection and backend tests cover log redaction; no report-body logging was found in frontend code.
- Provider-specific upstream 429/5xx behavior is tested; there is **no application-level public request rate limiter**. Do not expose this demo to untrusted public traffic without an abuse/rate-limit review.

## Accessibility and localization

- `@axe-core/playwright` WCAG 2.1 A/AA scans found **0 violations** on the form and rendered synthetic result states at the tested desktop viewport.
- Playwright covers skip-link and keyboard focus, Enter activation of source controls, the mobile view at 390 px and 320 px, and no horizontal overflow.
- This is not WCAG certification. A manual screen-reader pass, actual browser zoom/reflow check, and broader assistive-technology review remain outstanding. Keep English-only; no locale is represented as reviewed.

## Verification results

| Check | Result |
|---|---|
| Backend tests (Python 3.12.15; pytest 9.1.1) | **64 passed** |
| Ruff check + format, mypy | **Passed** |
| Frontend Playwright E2E | **10 passed**, including production build and disabled-provider browser → Next → FastAPI flow |
| Frontend ESLint + TypeScript | **Passed** |
| `npm audit` | **0 vulnerabilities** |
| `pip-audit 2.10.1 --path .venv/lib/python3.12/site-packages` | **No known vulnerabilities after pytest upgrade** |
| Production preview health | **HTTP 200**; disabled-provider analysis returns generic 503/no claims |
| Docker Compose | **Not run** in this workspace |

Dependency note: `pip-audit` found `pytest 8.4.2` affected by `PYSEC-2026-1845` / `CVE-2025-71176` (duplicate advisory entries). The dev constraint was raised to `pytest>=9.0.3,<10.0`; `uv.lock` now resolves pytest 9.1.1. Regression tests passed after the update and the Python environment re-audit was clean.

## Gate 2 decision

- [x] Core automated tests and static checks green locally.
- [ ] No unresolved critical unsafe **model** result — **not assessable** because no model output was run.
- [x] Source-linked claims and verifier fail-closed behavior covered by software tests.
- [ ] Reproducible model results and human claim-support metrics — **not available**; all model metrics are “not measured.”
- [ ] Accessibility blockers/manual assistive-technology review — automated axe and keyboard/mobile checks pass; screen-reader/actual zoom review remains outstanding.
- [x] Mocked provider failures and data-flow/log-redaction behavior pass software tests; live provider and deployment paths remain unverified.
- [x] Optional Phase 4 features remain deferred.

**Decision:** Gate 2 is **blocked / not passed**. The current evidence supports a synthetic software demo only, not a model-quality claim, clinical release, or public deployment. To reconsider Gate 2, configure an explicitly approved provider and distinct reviewed model IDs, run the frozen synthetic suite without using model output to alter keys, obtain human claim-level labels (preferably independent review/adjudication), complete manual screen-reader/zoom checks, and validate the intended deployment including abuse controls and Docker if used.

