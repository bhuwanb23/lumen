# Lumen — evidence-locked prototype

Lumen is a cautious, source-linked prototype for explaining wording in cancer pathology reports and preparing neutral questions for a care team. Phase 2 adds a text-only analysis path with strict extraction contracts, a separately configured verifier model, deterministic source-quote validation, fixed safety refusals, and a same-origin web proxy.

## Current status and limitations

- Phases 0–3 are implemented. The responsive text-only UI and same-origin vertical demo loop pass 10/10 Playwright tests; the browser-to-FastAPI integration test deliberately runs with the model provider disabled. Backend regression suite: 69 passed.
- Phase 4 deferred PDF/photo, Presidio, additional language, and integrations. Phase 5 software hardening is documented, but **Gate 2 is not passed**: no model evaluation/human claim labels or manual screen-reader review; see `plan/phase_5.md` and `eval/phase_5_report.md`.
- Live provider smoke now passes with the configured Ollama `gemma4:12b` generator/verifier on synthetic case `syn_breast_core_001` (extraction, fact verification, and full analysis in about 113 seconds). This is a compatibility smoke test only; it is not model-quality, clinical, or efficacy evidence.
- Phase 6 local readiness prep is documented, but **Gate 3/submission is blocked** pending Gate 2, event/cutoff confirmation, license, deployment review, and user-owned Git/submission steps; see `plan/phase_6.md`. Phase 7 pitch drafts are prepared but un-rehearsed; no event schedule, submitted build, or backup video is confirmed (`docs/phase_7_pitch_pack.md`).
- The browser UI and FastAPI API support English-only, text-only analysis. No image/PDF/OCR, translation, trial search, or report storage is implemented.
- `MODEL_PROVIDER=disabled` is the default. Real provider use requires an explicit provider selection, server-side credentials when applicable, and two distinct model IDs (generator and verifier).
- Provider adapters are covered by mock tests only. Live API compatibility, selected-model quality, data retention/terms, cost, and latency have **not** been tested.
- Synthetic reports, keys, and red-team examples are hand-authored and **not reviewed by oncology clinicians**. No clinical validation or patient-outcome evidence exists.
- Use synthetic or properly de-identified excerpts only in this prototype. Never submit identifiable or real patient information. Do not use outputs to make care decisions; confirm meanings with a clinician.
- Docker Compose is documented but was not run in this workspace because Docker is unavailable here. The standalone Next.js production server and local production preview were smoke-tested; the Docker deployment remains unverified.

## Prerequisites

- Node.js 20.20.2 (`.nvmrc`)
- Python 3.12.15 (`.python-version`)
- `uv` for the backend
- Docker Compose for the optional containerized path

## Local development

```bash
cp .env.example .env
```

Keep credentials local and server-side; do not use `NEXT_PUBLIC_*` variables for keys.

Backend (terminal 1):

```bash
cd backend
uv sync --python 3.12 --dev
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (terminal 2):

```bash
cd frontend
npm ci
NEXT_TELEMETRY_DISABLED=1 BACKEND_URL=http://127.0.0.1:8000 npm run dev
```

Open http://localhost:3000. The browser calls relative `/api/health` and `/api/analyze` routes; Next.js proxies those requests server-to-server to FastAPI. Provider keys and provider URLs never enter browser code. The analysis screen requires explicit synthetic/de-identification and provider-processing acknowledgements before it submits text.

## API and safety behavior

`POST /analyze` accepts a bounded report excerpt, optional English question, reading level, and explicit acknowledgements. It returns source-linked facts, only claims whitelisted by a separate verifier, and neutral appointment questions from curated static templates. The server computes Unicode-codepoint quote offsets against the untouched source string. Fields absent from the excerpt remain `not_stated`; they are not treated as negative. Unsupported or malformed evidence is dropped, and verifier failure returns no claims.

Fixed refusal responses cover diagnosis beyond the report, prognosis/survival, treatment recommendations or ranking, dosing, trial eligibility, urgent symptoms, and policy-evasion requests. A request to guess missing information is neutralized; the response marks absent fields and includes a fixed “can't guess” notice. Refusals and provider errors do not expose generated claims or raw provider errors.

## Provider configuration

The backend supports three explicit adapter choices:

- **Anthropic direct:** `MODEL_PROVIDER=anthropic`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, and `ANTHROPIC_VERIFIER_MODEL`.
- **OpenRouter:** `MODEL_PROVIDER=openrouter`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and `OPENROUTER_VERIFIER_MODEL`.
- **Ollama:** `MODEL_PROVIDER=ollama`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `OLLAMA_VERIFIER_MODEL`.

The generator and verifier model IDs must both be configured and different. There is no silent failover. `MODEL_TIMEOUT_SECONDS`, `MODEL_MAX_RETRIES`, and `MAX_REPORT_CHARS` are bounded settings. Ollama is **not assumed local**: verify endpoint access, network controls, and privacy for the deployment. The user-facing acknowledgement states that the operator-configured model service processes submitted text and may be external. Do not enable a provider until its model/schema support, terms, privacy, and operational limits are reviewed.

## Checks

Backend (from `backend/`):

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy app tests
uv run pytest -q
uv run python scripts/export_contracts.py
```

Frontend (from `frontend/`):

```bash
npm ci
npm run lint
npm run typecheck
npm run build
npm audit
LD_LIBRARY_PATH=/tmp/lumen-playwright-libs/usr/lib/x86_64-linux-gnu npm run test:e2e
```

The `LD_LIBRARY_PATH` override above was needed only in the assistant sandbox, where Chromium system libraries were missing; on a normal workstation install the OS dependencies via Playwright's Linux instructions. `npm run start` launches the standalone production server and stages its static assets locally.

All CI-style adapter and pipeline tests are mock-only; no API key or network call is required.

## Docker Compose

```bash
cp .env.example .env
docker compose config
docker compose up --build
curl -i http://localhost:8000/health
curl -i http://localhost:3000/api/health
```

Compose defaults to `MODEL_PROVIDER=disabled`. It configures an Ollama host-gateway address for optional use, but that endpoint is not guaranteed to be local or trusted. Docker Compose has not been executed in this assistant workspace; run the above smoke test on the target machine.
