# Phase 2 — Evidence-locked pipeline and safety refusals

**Window:** 25–26 Oct 2026 IST · **Status:** Implementation complete; mock-tested · **Depends on:** Phases 0–1.

## Objective
Implement the safety-critical backend path: extraction → facts-only explanation → deterministic quote validation → distinct verifier model → fixed refusal/scope filter. Phase 2 is an engineering implementation gate, **not** clinical validation or live-provider approval.

## Delivered

### 2.1 Provider boundary
- Implemented one async structured-output protocol plus Anthropic direct, OpenRouter-compatible, and Ollama adapters in `backend/app/providers.py`.
- `MODEL_PROVIDER=disabled` by default. No provider fallback; no redirects; server-side API keys; bounded timeouts and retry count.
- Generator and verifier model IDs are separately configured and required to differ. Anthropic/OpenRouter require server-side keys; Ollama is not presumed local and requires endpoint/network review.
- Mock HTTP tests exercise structured requests, credentials on server-side headers, timeout retries, malformed responses, and fail-closed configuration. No credential or live API call was used.

### 2.2 Extraction and evidence
- Strict Pydantic extraction requires exactly one result for each of 14 allowlisted fields and distinguishes `stated`, `not_stated`, and `unclear`.
- Models propose exact quotes only; server assigns stable field IDs and computes zero-based Python Unicode-codepoint, end-exclusive offsets against untouched input.
- False/missing quotes and instruction-like evidence lines are dropped. Exact span and downstream fact/citation relationships are checked deterministically.

### 2.3 Explanation and verification
- Generator receives only verifier-whitelisted facts; missing facts are excluded from claim generation and cannot support a citation.
- Candidate claims require existing stable fact IDs and exact matching quotes. Duplicate claims and lexical unsafe advice are omitted.
- A distinct configured verifier model whitelists facts and assesses complete claims. Unknown IDs, malformed results, semantic rejection, or verifier timeout produce no unsupported claims.
- Appointment questions are generated exclusively from reviewed-in-code, neutral English templates grounded in cited facts; freeform generated questions are not exposed.

### 2.4 Refusals, API, and UI
- Fixed refusal responses cover diagnosis beyond the report, prognosis/survival, treatment selection/ranking, dosing, trial eligibility, urgent symptoms, and policy evasion.
- Guess/assumption requests for missing fields are neutralized, mark absent fields, and show a fixed “can't guess” notice.
- FastAPI `/analyze` applies scope and acknowledgements before provider initialization. Validation/provider errors are generic; response does not expose raw provider bodies. A sanitized handler avoids echoing report text in Pydantic errors.
- Next.js `/api/analyze` is a same-origin server proxy; no provider key or direct browser-to-provider call. UI requires explicit synthetic/de-identified and provider-processing acknowledgements and renders only supported claims with exact source quotes.
- Requests/responses are no-store; no application report storage or report-body logging is implemented.

## Verification performed
- Backend: Ruff format/check, mypy, exported 17 Pydantic-derived JSON Schemas, **61 pytest tests passed** (pipeline, API, provider mocks, prior Phase 0/1 tests).
- Frontend: `npm ci`, ESLint, TypeScript, production build, `npm audit --omit=dev` (0 vulnerabilities).
- Local smoke: `/api/health` returned 200 through the Next.js proxy; out-of-scope prognosis request returned a fixed refusal without consent/provider use; acknowledged in-scope request with default-disabled provider returned generic 503 and no claims.
- No API key, external model, real report, or Docker Compose was used. Docker CLI is unavailable in this workspace.

## Acceptance / exit gate
- [x] Model processing disabled by default; enable requires explicit provider, distinct generator/verifier model IDs, and provider-required credentials.
- [x] No displayed claim without exact source quote and verifier pass.
- [x] Verifier failure/timeout returns no claims.
- [x] Injection, false/partial quotes, contradictions, duplicate claims, and unsupported paraphrase have mock regression tests.
- [x] Missing data is not turned negative; guess requests do not reach the explainer.
- [x] Fixed refusals cover prohibited topics; safe, neutral questions use static templates.
- [x] Request validation/provider errors do not echo report content; provider/error logs are tested for content redaction.
- [x] Mock tests run without external key/network.

## Explicit non-claims / remaining gates
- No clinical review of schemas, prompts, wording, synthetic fixtures, or red-team coverage has occurred.
- No selected live model's structured-output compatibility, semantics, safety performance, price, latency, retention, or terms are verified. Adapter success in mocks does not establish provider support.
- Production deployment still needs Docker/Compose smoke tests, HTTPS/rate limiting/abuse controls, provider privacy/terms review, and a clinician/privacy/security review before any real-patient use.
- Existing synthetic set remains a software regression asset, not a gold-standard clinical benchmark.
