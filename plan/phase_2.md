# Phase 2 — Evidence-locked pipeline and safety refusals

**Window:** 25 Oct 2026, H3–H8 · **Status:** Planned · **Depends on:** Phases 0–1.

## Objective
Implement safety-critical backend: extraction → facts-only explanation → deterministic quote validation → independent semantic verifier → refusal/scope filter.

## Work breakdown
### 2.1 Provider boundary (45–60 min)
Define one server-side provider protocol and adapters for Anthropic direct, OpenRouter, and optional local Ollama. Keep `MODEL_PROVIDER=disabled` by default; selection is explicit, never silently fail over (a fallback provider could change where report data is sent). Use provider-specific model/base URL/key settings, timeouts and bounded retries for transient failures. Mock each adapter in CI; test structured-output compatibility separately because provider/model support differs. Ollama is only considered local when its host/network is actually controlled. No browser model calls; generic error mapping; never log payloads/errors.

### 2.2 Extraction (60–90 min)
Force strict structured output; report treated as untrusted evidence, not instruction; explicit facts only; distinguish stated/not-stated/unclear; require exact verbatim quote and deterministic offsets; reject invalid facts before downstream use.

### 2.3 Explanation (45–60 min)
Generate brief claims from valid facts only. Claims cite stable fact IDs/source quotes. No medical background inference. Questions remain neutral and clinician-directed; use reviewed static templates if free generation can't be made safe.

### 2.4 Verification and safety (60 min)
Exact quote check; independent verifier assesses entire claim; reject if either gate fails; fail closed on verifier outage. Match by stable index/ID, never sentence text alone. Fixed refusals cover diagnosis, prognosis/survival, treatment/ranking/dose, trial eligibility and urgent triage. Ensure no unverified text leaks through fallback/error.

### 2.5 Tests (45 min)
Valid extraction; unsupported value; false/partial quote; paraphrase beyond source; duplicate claim; contradiction; missing stage; provider timeout; malformed schema; unsupported language; embedded prompt injection; unsafe questions. Assert logs contain no payload.

## Deliverables
Pipeline modules, strict contracts, model abstraction/mock, quote/span checker, semantic verifier, refusal module, backend tests and API examples.

## Acceptance / exit gate
- [ ] External model disabled unless explicitly enabled and key supplied.
- [ ] No displayed claim without exact quote and verifier pass.
- [ ] Verification failure/timeout returns no claims.
- [ ] Injection does not override policy in test cases.
- [ ] Missing isn't turned into negative; no type-based inference.
- [ ] Forbidden topics refuse; questions are neutral.
- [ ] No text/quote/prompt/completion/identifier/raw error in logs.
- [ ] Mock tests run with no external key/network.

If not achieved by H8, stop optional work and continue pipeline hardening. A fluent but unsupported summary fails.
