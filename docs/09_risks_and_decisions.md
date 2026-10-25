# 09 — Risks and decisions

## Risk register
| Risk | Impact | Mitigation / trigger |
|---|---|---|
| Unsupported or overconfident medical claim | Critical | Source quotes + verifier + fail closed + red-team; any critical output blocks release. |
| Exact quote does not entail whole claim | High | Separate semantic review and human eval; quote existence alone never proves support. |
| Prompt injection in uploaded report | High | Untrusted data, delimiters, strict tools, verifier, adversarial tests; no immunity claim. |
| OCR loses a negation/number/marker | Critical | Show/edit transcription, quality gate; defer upload if mapping isn't safe. |
| PII sent externally despite masking | Critical | Explicit provider disclosure/opt-in, synthetic demo only, provider/terms review, de-identification tests. |
| Translation changes clinical meaning | High | One reviewed language; original quote; fixed reviewed refusal strings; otherwise disable. |
| Sensitive payload in logs/traces | Critical | Fixed event logs, no raw exceptions, tracing off, test error paths. |
| Scope creep misses deadline | High | P0/P1/P2, feature freeze, cut optional features before eval/safety. |
| NCI access/licensing uncertain | Medium | Verify before build; defer if unclear. |
| Tamil/Hindi PDF rendering broken | Medium | Minimal real PDF test; disable locale/card if failure. |
| Trial output mistaken as recommendation | High | “Ask clinician” language, exact source/date, no eligibility. |
| Research statistic misquoted | Medium | Verify primary source; remove unsupported claims. |
| Host/provider retention undermines privacy claim | Critical | Inspect configuration/terms, synthetic demo, precise privacy copy. |
| Dependency/API change | Medium | Lockfiles, audits, CI, clean install. |

## Decisions
1. **Stateless:** no patient accounts or report database; lowers stored-data risk but not external provider processing.
2. **No vector DB:** exact authoritative lookups are easier to audit for glossary terms; avoid retrieval complexity where determinism matters.
3. **Next.js + FastAPI:** typed UI/server proxy plus Python pipeline/evaluation.
4. **Text-first MVP:** upload only after OCR review and source mapping.
5. **Verifier is not truth oracle:** independent pass plus deterministic checks; never claim hallucination-free.
6. **Language quality over count:** only reviewed languages advertised.
7. **Synthetic-only public demo/eval.**
8. **NCI/trials gated:** validate current access and semantics before implementation.

## Decisions to resolve in Phase 0
Official cutoff/time zone and judging dates; narrow report/cancer scope; fluent reviewer; model ID/cost/retention; feasibility of photo/OCR; whether glossary/trials/card justify integration risk.
