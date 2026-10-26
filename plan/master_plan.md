# Lumen master execution plan

**Planning date:** 25 October 2026, IST. **Working submission deadline assumption:** 28 October 2026. Confirm the organizer cutoff/time zone immediately; target submission on Oct 27 to leave buffer. **Status:** Phases 0–3 are implemented; Phase 4 deferred optional features. Phase 5 software hardening is complete for this pass (10 E2E, 64 backend tests), but Gate 2 is blocked because model evaluation/human claim labels and manual accessibility review are missing. Phase 6 local readiness prep is complete; submission is on hold pending Gate 2 per user decision. Gate 3 also needs event details, a project license, deployment review, and user-owned Git/submission steps.

## Critical path
| Phase | Focus | Planned window (IST) | Gate/outcome |
|---|---|---|---|
| 0 | Scope lock, repo/environment bootstrap, local health path | Oct 25, H1 (~1 hour) | Clean repo; frontend and API run; no secrets tracked |
| 1 | Synthetic fixtures, answer keys, schemas, safety cases | Oct 25, H2–H3 | Reviewed gold evidence and API contract |
| 2 | Extract → explain → verify and refusals | Oct 25, H3–H8 | Exact evidence, verifier approval, unsafe cases fail closed |
| 3 | UI and source-linked demo loop | Completed Oct 26 | **Gate 1:** passed; 8/8 Playwright E2E, safe disabled-provider flow |
| 4 | Conditional file input, privacy, one reviewed language | Completed Oct 26 | No-go on A–D; insufficient reviewer, mapping, terms, or feature-specific tests; all deferred |
| 5 | Evaluation, red team, accessibility, reliability | Software hardening pass: Oct 26 | Gate 2 **blocked**: automated tests green; model/human evaluation and manual accessibility review outstanding |
| 6 | Feature freeze, documentation, Devpost/video, submission | Local prep Oct 26; submission blocked | **Gate 3:** not passed; Gate 2, event details, license, deployment review and receipt outstanding |
| 7 | Finals/demo rehearsal/judging if scheduled | Oct 28–Nov 1 | Rehearsed stable demo; no scope creep |
| 8 | Post-event validation/pilot pathway | After event / from Nov 2 | Review and formal approval path; not deployment authorization |

“H1/H2” are effort blocks, not exact clock times. Rebase if the official cutoff differs or a gate slips. Elapsed time alone never passes a gate.

## Must ship
1. App/backend skeleton and local health.
2. Small synthetic report set + hand-authored answer keys.
3. Strict extraction, fact-only explanation, exact quote check, separate verifier, fixed scope refusals.
4. UI source links, visible safety notice, no-claims and failure state.
5. Reproducible eval/red-team tests with real measured outputs.
6. Docker, CI, clean setup docs, accurate submission.

## Optional order
Photo/PDF with OCR review → Presidio with validated mapping → one reviewed language → NCI exact lookup after legal/access check → ClinicalTrials.gov after query review → print card after fonts test → broader PWA/traces. Cut in reverse order if behind. Never cut safety, evidence checks, eval or truthful disclosure.

## Gates
- **Gate 0:** deadline confirmed; fresh app and API health; no credentials in git; scope agreed.
- **Gate 1:** clean synthetic text-to-result demo; source link exact; no missing-field inference; safe errors.
- **Gate 2:** tests/eval reproducible; semantic review conducted; accessibility basics; privacy/security checks pass.
- **Gate 3:** clean install, CI green, accurate README/demo/results, submission receipt saved.
- **Post-event:** no real patient use without clinical, privacy/legal, ethics as needed, translation, security, and monitoring review.

## Operating rules
- Build one vertical slice before broadening features.
- Each output field needs schema, evidence, UI, test, and failure state.
- If any phase slips >90 minutes, drop optional work and rebase.
- Freeze features by Oct 27 target; only fix release blockers afterward.
- Public demo, eval, screenshots and CI use synthetic data only.
- Status every item as planned/in progress/tested/blocked/done, with proof.

## Phase files
0. [Bootstrap and scope lock](phase_0.md)
1. [Synthetic data and contracts](phase_1.md)
2. [Safe analysis pipeline](phase_2.md)
3. [UI and vertical demo loop](phase_3.md)
4. [Conditional input/features](phase_4.md)
5. [Evaluation and hardening](phase_5.md)
6. [Freeze and submit](phase_6.md)
7. [Finals/demo readiness](phase_7.md)
8. [Post-event path](phase_8.md)
