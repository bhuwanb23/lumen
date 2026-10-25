# 03 — Proposed architecture

## Data flow
```text
Browser → Next.js UI and same-origin route → FastAPI validation/orchestrator
  → optional Presidio adapter → configured model adapter (Anthropic/OpenRouter/Ollama) → fact-only explanation
  → deterministic quote/span check → separate semantic verifier → scope filter
  → response with supported claims and citations
Optional after gate: NCI exact lookup, ClinicalTrials.gov, WeasyPrint prep card.
```

## Trust boundaries
- **Browser:** shared-device risk. No localStorage/IndexedDB report storage, analytics replay, URL payload, console logging, or service-worker caching of reports.
- **Next.js server route:** same-origin proxy; holds no provider credential; enforce body cap, timeout, no-store, generic errors.
- **FastAPI:** strict schemas/size checks; no report database; metadata-only logs.
- **Model provider:** an explicitly selected Anthropic, OpenRouter, or Ollama adapter may receive report content only after implemented and deliberately enabled. No automatic provider failover; switching providers can change data recipients. Stateless application does not guarantee provider-side non-retention. Verify and disclose terms per provider. Ollama is only “local” if its network endpoint is actually on a trusted local machine.
- **Public integrations:** send only minimum extracted criteria, not report text or identifiers. Caches store public glossary/trial data only, never user requests.

## Pipeline contract
1. **Intake:** preserve original text; no destructive Unicode normalization unless reversible offset map exists. P0 only accepts text.
2. **Extract:** allowlisted fields (report type, cancer type, site, grade, stage, margins, nodes, biomarkers, findings). Each fact has value, status (`stated` / `not_stated` / `unclear`), exact quote, and verified offsets. Absence must never become “negative.”
3. **Explain:** short claims from validated facts only. Cite stable fact IDs/quotes; no general knowledge to fill gaps.
4. **Verify:** schema validation; exact substring and offset checks; separate verifier judges whole-claim support. Any failed check or verifier outage suppresses the claim. Verifier is not a proof; benchmark it.
5. **Safety:** enforce refusals for diagnosis, prognosis/survival, treatment/dose, eligibility, urgent triage; do not rely on prompt alone.
6. **Respond:** disclaimer, supported claims, citations, neutral questions, locale/readability, omitted count and safe status. No generated fallback claims.

## API boundary
- `GET /health`: liveness only, no secret/config disclosure.
- `POST /api/v1/analyze`: strict JSON request (`report_text`, approved locale, reading level); enforce max length.
- Future `POST /api/v1/analyze-file`: multipart, only after type/page/size/OCR/source-map tests.
- No request/response body logs, cache, or content-bearing trace. Provider errors are generic and not echoed.

## Reliability and security
Bounded timeouts; capped backoff only for transient failures; no retry of malformed deterministic requests; safe unavailable message; CORS allowlist; rate limiting; security headers; body/file limits; HTTPS in deployment; least-privilege containers; secret scanning. JSON logs include fixed event, duration, status class, anonymous request ID only. No report, quote, prompt, completion, filename, identifier, exception text, or key. Langfuse/tracing off until content redaction is proven.

## Evidence offset warning
Python string indices and JS UTF-16 indices differ for some Unicode. Preserve canonical source and mapping, test Tamil/Devanagari combining marks, line endings and non-BMP characters. Do not highlight offsets until round-trip tests pass; rendering the exact cited quote is safer than slicing with unvalidated cross-language offsets.
