# Lumen project documentation

This is the product, technical, safety, evaluation, accessibility, and demo reference. The execution plan is in `../plan/`. Phase 0 application bootstrap has been created; report analysis has not.

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
Phases 0 and 1 are complete in this workspace: the Next.js status shell, same-origin health proxy, FastAPI health endpoint, provider config placeholders, typed Pydantic/JSON contracts, synthetic reports/answer keys, red-team cases, and evaluation annotation/metric definitions are present. Local lint/type/build/API and fixture checks pass. Docker Compose is prepared but not verified because Docker is unavailable in this execution workspace. The app still has no report input or clinical-analysis pipeline. See [Phase 0 decision record](phase_0_decisions.md), [Phase 0 plan/status](../plan/phase_0.md), and [Phase 1 plan/status](../plan/phase_1.md).
