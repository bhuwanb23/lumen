# 08 — Integrations and document handling

## Model providers: Anthropic direct, OpenRouter, optional Ollama
The user requests support for all three behind one server-side adapter boundary. Phase 0 only adds configuration placeholders; **no provider adapter, report analysis, or model call exists yet**. Keep `MODEL_PROVIDER=disabled` by default. In a later phase, implement/test each adapter separately: Anthropic's native API; OpenRouter's configured compatible endpoint/model; Ollama at a local base URL/model. Verify current model availability, structured-output/tool support, context/image limits, latency/cost, retention/training terms, and failure behavior for each selected model. Do not silently fail over between providers; that can change where report content is sent. Any hosted option sends report content outside the app when enabled; disclose explicitly. Ollama is local only if the user's deployment/network is actually local and correctly secured. Keep keys server-side; CI uses mocks; never log prompt/output.

## Presidio
Goal: detect/mask names, addresses, IDs, dates, facility/clinician names before provider calls. Before integration, test custom recognizers, English/mixed/Tamil/Hindi coverage, false negatives and false positives, and reversible source-span mapping. Masking must not break citations or leak originals in output. Best effort, never a guarantee. If mapping isn't solved, keep it off and disclose provider transmission.

## NCI Dictionary / Thesaurus
Only exact lookup with source attribution/retrieval date; never fill missing lookup from model memory. Before coding, confirm current access route, licensing/attribution, caching permission, versioning, locale coverage, rate limits, and stability. SQLite FTS5 cache may contain only approved public terms, no patient query history. If terms remain unclear, defer.

## ClinicalTrials.gov API v2
Query with minimum necessary explicit extracted criteria; cache public metadata with TTL and timestamp. Show registry link, NCT ID, recruiting status as retrieved, and search basis. Label “study to ask your oncologist about”; no suitability ranking, eligibility decision, or promise of completeness/currentness. Verify query syntax, status filters, rate limits and cache rules with current API docs.

## PDF/photo OCR
P0 is text-first. P1 upload requires strict MIME/extension, bytes/page count/image dimensions, safe temporary handling/cleanup, OCR preview/edit, poor-quality/empty/encrypted/corrupt paths, prompt-injection tests, and honest source anchors. Quote from patient-reviewed transcription; don't claim exact scan line provenance absent verified coordinates. If mapping/confidence fails, stop and offer paste.

## WeasyPrint prep card
Only after stable response contract. One page; accessible structure; source quotes; questions; locale; disclaimer; no patient name by default. Check sanitized HTML, font embedding/licensing, line wrapping, grayscale print, Tamil/Hindi glyph shaping. Browser print is fallback. No identifiers added by default.

## SQLite cache policy
Allowed only for public, approved glossary/trial metadata with TTL, provenance, version and size bounds. Never store reports, IDs, prompts, answers, patient-specific queries/history. Define invalidation before deployment.
