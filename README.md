# Lumen — Phase 0 bootstrap

Lumen is planned as a cautious, source-linked companion that helps patients understand report wording and prepare questions for their care team. The application is still only the **Phase 0 shell**; Phase 1 now defines contracts and synthetic evaluation fixtures, but **report analysis is not implemented**.

## Current status
- Next.js 16 / TypeScript accessible setup-status page and same-origin health proxy.
- FastAPI health service with restricted CORS, no-store, and baseline security headers.
- Python 3.12 and Node 20.20.2 runtime pins; backend and frontend dependency locks.
- Docker Compose configuration is prepared. It was not run in this workspace because Docker CLI is unavailable here.
- Phase 1 Pydantic/JSON contracts and synthetic fixtures/answer keys/red-team cases are present.
- No report input, OCR, model adapter, trials, translations, or patient-data processing exists yet.
- **Do not enter real patient data.** Lumen is not medical advice or a clinical tool.

## Prerequisites
- Node.js 20.20.2 (`.nvmrc`)
- Python 3.12.15 (`.python-version`)
- `uv` for backend environment/lock
- Docker Compose for containerized startup (optional for local development)

## Local development
First, from the project root, create a local environment file if you want to use settings:
```bash
cp .env.example .env
```
Keep any actual credentials private and local. Backend (terminal 1):
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
Open http://localhost:3000. The browser calls the relative `/api/health` endpoint; the Next.js server proxies to FastAPI. Browser code never calls the backend host directly.

## Docker Compose
```bash
cp .env.example .env
docker compose config
docker compose up --build
# In another terminal:
curl -i http://localhost:8000/health
curl -i http://localhost:3000/api/health
# Stop with Ctrl+C, then clean up:
docker compose down
```
Open http://localhost:3000. Backend health is http://localhost:8000/health. Compose binds Ollama's optional host address through `host.docker.internal`; model provider remains disabled by default. Docker Compose has not been executed in this assistant workspace; these commands are the user's local smoke test.

## Provider configuration boundary
The settings file has placeholders for **Anthropic direct API**, **OpenRouter**, and optional local **Ollama** because those are requested provider choices. This is configuration scaffolding only: there is no model adapter or model request in Phase 0. `MODEL_PROVIDER=disabled` is the safe default. Do not add keys until the provider adapter, budget, model, data terms, and user-facing external-processing disclosure are implemented and reviewed. For local Ollama, set `OLLAMA_BASE_URL=http://127.0.0.1:11434`; for Docker on Linux, use the host gateway address from `.env.example`.

## Safety and privacy
Never put a secret in a `NEXT_PUBLIC_*` variable or frontend code. No user reports should be entered or stored at this stage. No report database or analysis endpoint exists. External model use in a later phase would transmit submitted report content to the selected provider; statelessness alone does not guarantee provider-side privacy. The app is not clinically validated and does not give medical advice.
