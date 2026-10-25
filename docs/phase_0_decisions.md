# Phase 0 — Constraint and bootstrap decision record

**Recorded:** 25 October 2026 (IST)  
**State:** Application bootstrap and local run path completed; remaining uncertainties are tracked below.  
**No clinical analysis code exists.**

## Known environment facts

| Item | Observed / decision |
|---|---|
| Workspace / user OS | Linux execution workspace; user confirms their development machine is Linux. |
| Node | Node 20.20.2, pinned in `.nvmrc` and frontend image. |
| Python | Python 3.12.15 installed via `uv` for this workspace; `.python-version` selects 3.12.15. |
| Docker | User confirms Docker is available on their Linux machine. Docker is not installed/available in this workspace, so Compose is prepared but could not be executed here. |
| Frontend dependency lock | `frontend/package-lock.json` generated and clean `npm ci` verified. |
| Backend dependency lock | `backend/uv.lock` generated and resolved for Python 3.12. |
| Model providers | User requests future support for Anthropic direct, OpenRouter, and optional local Ollama. Provider/model/base-URL/key configuration placeholders are added server-side; no provider adapter or call exists yet. No key was shared or is needed in Phase 0; keep `MODEL_PROVIDER=disabled`. |
| Database/user data | None. No database, report input, or report persistence. |
| Deployment | Not configured or attempted. Public deployment is out of Phase 0. |

## Locked product scope for first build

- **P0:** text-first, synthetic-only; strict fact extraction, source quotes, fact-only explanation, verification, refusals, source-linked UI, tests/evaluation, local reproducibility. This is the planned first product slice, not yet implemented.
- **P1:** photo/PDF only with OCR preview and source mapping; Presidio only with validated span mapping; one additional language only with fluent review; NCI/trials only after API/access/license validation; prep card only after font tests.
- **P2:** full Tamil/Hindi/Spanish polish, extra report types, tracing, broader PWA/offline, caregiver sharing and research/pilot.
- **Phase 0 implementation:** accessible status/placeholder page and health proxy only. No report submission or model calls.

## User/organizer decisions and remaining confirmation

| Question | Current status / safe assumption |
|---|---|
| Official submission cutoff and time zone? | User confirms Oct 28, 2026, IST; exact cutoff clock time and submission rules still need checking against the organizer page. |
| Team/solo and named owner? | User confirms solo build; user owns project decisions. |
| User development OS / Docker? | User confirms Linux and Docker available on their machine. This workspace is also Linux, but its execution container lacks Docker CLI. |
| Model providers / key / budget? | User requests Anthropic direct, OpenRouter, and optional Ollama. No key was shared; budget and chosen default provider are still to be confirmed. Keep calls disabled. |
| Fluent reviewer for which language? | A reviewer may be available for another language, but exact language/reviewer details are unspecified. Default to English-only until confirmed. |
| Deployment accounts/host? | **Unknown.** No deployment in Phase 0; use synthetic data only if later hosted. |

## Verification performed

- Backend: Python 3.12.15; `uv sync --frozen` lock path prepared; Ruff passes, mypy passes, 8 backend health/CORS/security-header/bootstrap/provider-config tests pass.
- Frontend: Node 20.20.2; clean `npm ci` passes; ESLint 10 + TypeScript + production `next build` pass; `npm audit` reports 0 vulnerabilities at verification time.
- Live local integration: API `/health` returns `{"status":"ok"}` with `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, and `X-Frame-Options: DENY`; Next page returns HTTP 200; same-origin `/api/health` successfully proxies to FastAPI.
- Browser-facing code calls only the relative `/api/health` route. `BACKEND_URL` is read only by the Next server route.
- No Docker executable was available; Docker Compose was not run. No Git commands or version-control setup were performed at user's request.
- No secret or actual report was provided. The model environment is disabled; no report data is accepted by the UI.

## Completion assessment

**Completed:** Phase 0's scope defaults and local application skeleton/health path in this workspace.  
**Pending user confirmation:** exact organizer cutoff time/rules, API budget/default provider, exact additional language/reviewer, and deployment host.  
**Unverified in this execution workspace:** Docker Compose clean run because Docker CLI is unavailable here. User confirms Docker is available on their Linux machine; run the documented Compose smoke test there to close this environment-specific item.
