# Lumen master execution plan

**Planning date:** 25 October 2026, IST. **Working submission deadline assumption:** 28 October 2026. Confirm the organizer cutoff/time zone immediately; target submission on Oct 27 to leave buffer. **Status:** Phase 0 bootstrap complete in the current workspace; Phase 1 has not started. The analysis pipeline is not implemented.

## Critical path
| Phase | Focus | Planned window (IST) | Gate/outcome |
|---|---|---|---|
| 0 | Scope lock, repo/environment bootstrap, local health path | Oct 25, H1 (~1 hour) | Clean repo; frontend and API run; no secrets tracked |
| 1 | Synthetic fixtures, answer keys, schemas, safety cases | Oct 25, H2–H3 | Reviewed gold evidence and API contract |
| 2 | Extract → explain → verify and refusals | Oct 25, H3–H8 | Exact evidence, verifier approval, unsafe cases fail closed |
| 3 | UI and source-linked demo loop | Oct 25, H8–H10 | **Gate 1:** synthetic end-to-end path works; safe errors |
| 4 | Conditional file input, privacy, one reviewed language | Oct 26 | OCR review and evidence mapping or defer; never add unsafe upload |
| 5 | Evaluation, red team, accessibility, reliability | Oct 26 evening–Oct 27 morning | **Gate 2:** measured results; tests green; limits honest |
| 6 | Feature freeze, documentation, Devpost/video, submission | Oct 27 (reserve through Oct 28 only if needed) | **Gate 3:** submission accepted and receipt saved |
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
