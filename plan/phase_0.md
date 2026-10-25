# Phase 0 — Scope lock, application skeleton and local bootstrap

**Window:** 25 Oct 2026, H1 target · **Status:** Completed for the current workspace; organizer/user confirmations remain open · **Prerequisite:** none.

> **Scope adjustment at user's direction:** Git initialization, branches, commits, and version-control/repository administration are excluded. This phase created the application skeleton and local run path only. The workspace currently has docs/plans plus the Phase 0 frontend/backend files; it has no clinical analysis implementation.

## Objective

Lock safe initial scope and provide a clean, reproducible local skeleton: accessible Next.js shell → same-origin health proxy → FastAPI health route. No report analysis, report intake, or model calls are implemented.

## Work breakdown and completion

### 0.1 Confirm constraints
- **Completed with defaults:** P0 first slice is text-first and synthetic-only; P1 is conditional; P2 is deferred. See [decision record](../docs/phase_0_decisions.md).
- **Confirmed by user:** solo project, Linux machine with Docker available, and Oct 28, 2026 IST as the event deadline. Verify the organizer's exact cutoff time/requirements.
- **Still open:** model budget/credentials and default provider; reviewer identity and exact second language; deployment host.
- User requested future support for Anthropic, OpenRouter, and optional local Ollama. Server-side config placeholders were added; provider adapters/model calls are not part of Phase 0. English remains the only default until a reviewer/language is confirmed.

### 0.2 Repository hygiene
- **Excluded by user:** no Git init, branch/commit policy, or related repo administration performed.
- App structure, runtime pin files, dependency locks, and `.env.example` created.
- No `.env` with secrets, report uploads, or real report fixtures created.

### 0.3 App skeleton
- **Done:** Next.js 16.4.3 / TypeScript frontend; responsive, semantic setup-status screen; same-origin `/api/health` server proxy.
- **Done:** FastAPI health service, CORS allowlist, `no-store`, and baseline security headers.
- **Done:** Compose configuration prepared; provider configuration placeholders for Anthropic, OpenRouter, and Ollama are server-side; default is `MODEL_PROVIDER=disabled`; no key or model call is used.
- **Runtime:** Node 20.20.2 and Python 3.12.15 pinned/used in this workspace; Docker base tags use these exact runtime versions.

### 0.4 Clean run and verification
- Backend Ruff and mypy pass; 8 health, CORS, header, bootstrap-state and provider-config tests pass.
- Frontend ESLint, TypeScript, production build, and `npm audit` pass (0 vulnerabilities at check time).
- Live local API returned `{"status":"ok"}`; Next page returned HTTP 200; same-origin Next proxy reached the API and returned health successfully.
- Docker is not installed in this workspace, so Compose was not executed. Local development mode was used instead.
- No Git commands or `git status` inspection were performed, per user's instruction.

## Deliverables

- `frontend/` Next app shell and `/api/health` proxy.
- `backend/` FastAPI service and tests.
- `.nvmrc`, `.python-version`, `frontend/package-lock.json`, `backend/uv.lock`.
- `docker-compose.yml`, Dockerfiles, `.env.example`, root `README.md`.
- [Phase 0 decision record](../docs/phase_0_decisions.md) with known facts, assumptions, results, and remaining confirmations.

## Acceptance / gate 0

- [x] User confirmed Oct 28, 2026 IST; exact cutoff time/rules should still be checked on the organizer page.
- [x] User confirmed solo project, Linux and Docker availability on their machine; this workspace itself has no Docker CLI.
- [x] Frontend and API start in local development; frontend health page and API health pass.
- [x] Provider placeholders exist for Anthropic/OpenRouter/Ollama; default is disabled and no API key/call is used or exposed.
- [x] CORS is restricted to configured frontend origin; no-store/security headers are present and tested.
- [x] No report data or real `.env` file was created in this workspace.
- [x] P0/P1/P2 defaults recorded; current app explicitly says analysis is not implemented.
- [ ] Docker Compose clean startup: **not verified here** because Docker is unavailable in the execution workspace; user machine can run the documented smoke test.
- [ ] Model budget/default provider, deployment host, and exact second-language reviewer: **awaiting user**.
- [ ] Git-specific checks: **intentionally excluded at user's request**.

## Risks and stop conditions

- Do not enable model calls until user confirms access, budget, current provider terms, and model configuration.
- Do not add file intake before Phase 4 OCR review/source mapping requirements are settled.
- Do not advertise Tamil/Hindi/Spanish as supported without fluent review.
- Do not deploy until host/provider log and retention behavior is reviewed.
- If official deadline is earlier than Oct 28, cut P1 features first.

## Exit gate

The local app/API health path is working and the scope is recorded. Phase 0 implementation is complete in this workspace, but treat Docker Compose and user/organizer-specific confirmations as pending. No clinical analysis capability exists or is claimed.
