# Lumen project documentation

This is the product, technical, safety, evaluation, accessibility, and demo reference. The execution plan is in `../plan/`. Phases 0–2 are implemented; Phase 2 is mock-tested only, not clinically validated, and no live model has been evaluated.

## Document map
1. [Product brief](01_product_brief.md)
2. [Scope and user journeys](02_scope_and_user_journeys.md)
3. [Architecture](03_architecture.md)
4. [Stack and repository structure](04_stack_and_repository_structure.md)
5. [Safety, privacy, security](05_safety_privacy_security.md)
6. [Evaluation and test strategy](06_evaluation_and_test_strategy.md)
7. [Accessibility and localization](07_accessibility_localization.md)
8. [Integrations and document handling](08_integrations_and_document_handling.md)
9. [Risks and decisions](09_risks_and_decisions.md)
10. [Demo and submission](10_demo_and_submission.md)
11. [Phase 0 decision record](phase_0_decisions.md)
12. [Phase 2 acceptance/status](../plan/phase_2.md)

## Product boundary
Lumen explains only what a submitted report explicitly says, helps prepare neutral questions for the care team, and may surface trials as discussion starters. It does not diagnose, infer missing findings, predict outcomes, recommend/rank treatment or dosage, or decide trial eligibility. It is a hackathon prototype, not a validated medical product.

## Canonical assumptions
- Hackathon: 2026 International CodeTheCure. Planning date: 25 Oct 2026, Asia/Kolkata.
- Working submission deadline assumption: 28 Oct 2026; confirm official cutoff and time zone immediately.
- Proposed stack: Next.js + TypeScript frontend; FastAPI + Python 3.12 backend.
- Public demo, test and evaluation data: synthetic only.
- No patient report database, accounts, analytics replay, or report-bearing logs.
- Prioritize evidence quality, safety, and evaluation over feature count.

## Current status
Phases 0–2 are implemented in this workspace. Phase 2 provides an English-only text analysis API, server-side Anthropic/OpenRouter/Ollama adapters, separate generator and verifier model roles, fail-closed evidence checking, fixed refusals, synthetic/de-identification and external-processing acknowledgements, a same-origin Next.js proxy, and a basic results UI. Backend unit/API/provider mocks, lint, type checks, JSON Schema export, and frontend lint/typecheck/build/audit have passed. No live provider call or clinical-quality evaluation has been performed; synthetic assets are not clinician-reviewed. Docker Compose remains unverified because Docker is unavailable in this execution workspace. See the [Phase 0 decision record](phase_0_decisions.md) and [phase plans](../plan/).
