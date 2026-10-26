# 03 — Architecture and current boundaries

## Current Phase 2 data flow
```text
Browser form
  → same-origin Next.js /api/analyze proxy
  → FastAPI /analyze request/acknowledgement/scope checks
  → explicitly configured generator model: strict extraction
  → deterministic exact-quote and source-offset validation
  → separately configured verifier model: fact whitelist
  → generator model: concise cited claims
  → verifier model: whole-claim support whitelist
  → deterministic quote/scope/question checks
  → response with supported claims, exact sources, fixed disclaimer/refusals
```

No OCR, PII detection, glossary, trials integration, or PDF card is present. `MODEL_PROVIDER=disabled` is the default. A configured provider requires distinct generator and verifier model IDs; no automatic fallback changes where data is sent.

## Trust boundaries
- **Browser:** no localStorage/IndexedDB report storage, analytics replay, URL payload, browser console logging, or service-worker caching of reports. The text is held in page memory while used.
- **Next.js server route:** same-origin proxy; no provider credentials; bounded request size, timeout, no-store responses, and generic error mapping.
- **FastAPI:** strict request/response schemas, configurable text limit, no report database, and no report-body logs. Validation errors are redacted.
- **Model provider:** receives report text only after the user acknowledges synthetic/de-identified text and processing by the operator-configured provider. Hosted provider processing can be external. Stateless app processing does not ensure provider-side non-retention. Verify terms and disclose per deployment. Ollama is not assumed local unless its network and host are controlled.
- **Public integrations:** none currently receive report data. Future services must receive only minimum necessary criteria and must never receive direct identifiers.

## Evidence-locked pipeline
1. **Intake:** text-only; bounded to 50,000 characters maximum (operator may lower). Preserve the exact source string; no Unicode normalization.
2. **Extract:** allowlisted fields; every field is marked `stated`, `not_stated`, or `unclear`. The model returns exact quotes only; server assigns deterministic fact IDs and computes zero-based Python Unicode-codepoint, end-exclusive offsets. Invalid/false quotes and instruction-like evidence lines are dropped.
3. **Fact verify:** distinct configured verifier model whitelists fully supported facts. An unknown ID, malformed result, provider failure, or timeout fails closed.
4. **Explain:** generator receives only verifier-approved facts and produces candidate claims with stable fact IDs and exact quote proposals. A deterministic check drops missing, mismatched, duplicate, or lexically out-of-scope candidates.
5. **Claim verify:** distinct verifier model assesses the complete claim against the original report and evidence. Only whitelisted claim IDs enter the public response; a verifier failure returns no claims.
6. **Safety/response:** deterministic scope refusals for diagnosis, prognosis/survival, treatment/ranking, dosing, trial eligibility, urgent symptoms, and policy evasion. Guess requests for missing values are neutralized; missing fields are explicitly marked. Questions come only from curated neutral English templates. No generated fallback claims.

The semantic verifier is a separate model role and call, not a proof of clinical correctness. Model identities are separately configurable but must be clinically and technically evaluated before real deployment.

## API boundary
- `GET /health`: liveness only, no provider/secret detail.
- `POST /analyze`: FastAPI JSON API; strict English-only schema, report text, optional question, reading level, and two required acknowledgements.
- Browser calls `POST /api/analyze` on the same origin; Next.js proxies server-to-server.
- No request/response body logs, caches, or content-bearing traces. Provider errors and validation errors are generic and not echoed.

## Reliability and security posture
Provider requests use configured timeouts, capped transient retries, and no redirects. Provider selection is explicit; malformed outputs and non-retryable errors do not trigger a fallback. CORS is allowlisted; browser responses are no-store and include baseline security headers. Production deployment still needs HTTPS, rate limiting, abuse controls, secret management, container review, and external provider/privacy review. Do not assume statelessness alone guarantees privacy.

## Offset warning
Python string indices and JavaScript UTF-16 indices differ for some Unicode. The current UI renders validated exact quotes instead of slicing the source by backend offsets. Extend locale/source highlighting only after codepoint/UTF-16 conversion and Tamil/Devanagari/non-BMP round-trip testing.
