# 08 — Integrations and document handling

## Model-provider boundary (Phase 2)
The backend now has server-side structured-output adapters for Anthropic direct, OpenRouter, and Ollama. The provider is explicitly selected with `MODEL_PROVIDER`; it defaults to `disabled` and never silently switches data recipients. Anthropic and OpenRouter keys remain server-side. Every enabled configuration requires distinct generator and verifier model IDs; extraction/explanation use the generator, while fact and claim verification use the verifier model. CI uses mock HTTP transports and synthetic data only.

Adapters have not been exercised against live services. Verify current model availability, tool/schema support, context limits, latency/cost, retention/training terms, and failure behavior before enabling a deployment. Ollama is not considered local merely because the product is named Ollama: endpoint reachability, network controls, and host trust must be checked. Users are explicitly told the operator-configured model service processes submitted text and may be external. No provider payloads, outputs, keys, or error bodies are logged.

## Document handling currently supported
The prototype accepts pasted text only, bounded to 50,000 characters (and further configurable downward). The server preserves that string as supplied and computes zero-based Python Unicode-codepoint offsets with end-exclusive spans; it performs no normalization. Model-proposed offsets are not accepted. Each evidence quote is checked for exact occurrence before downstream use, and instruction-like lines are excluded by a deterministic backstop. The semantic verifier remains necessary because substring equality alone does not prove a claim.

The browser has no upload, OCR, PDF/image parsing, account, analytics, or report-storage path. Requests and responses are no-store. The API requires a synthetic/de-identified acknowledgement and a provider-processing acknowledgement; those controls do not constitute a de-identification service. Use synthetic or properly de-identified text only and never submit direct identifiers or real patient data to this prototype.

## Deferred integrations
No OCR/document upload, translation, glossary/NCI service, clinical trial search, PII detection, or PDF visit-preparation card is implemented. Those remain later-phase work and require separate privacy, safety, accessibility, licensing, and evaluation gates. Any future clinicalTrials.gov content can only be a clinician discussion starter—not an eligibility recommendation.
