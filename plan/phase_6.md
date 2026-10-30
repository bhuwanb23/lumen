# Phase 6 — Feature freeze, submission and backup demo

**Window:** 27 Oct (reserve into 28 Oct only if official cutoff requires) · **Status:** Submission on hold pending Gate 2 (user decision); event unconfirmed · **Depends on:** Gate 2.

## Objective
Package and submit the tested build early; only fix release blockers after feature freeze.

## Gate and decision
Phase 5 Gate 2 is **not passed**: no live model results/human claim labels, manual screen-reader/zoom review, provider/deployment validation, or public-abuse review. Phase 6 cannot truthfully declare a release candidate or submission-ready product. Do not submit as clinically validated or model-evaluated. This pass completes local checks and documentation, but does not bypass Gate 2.

## Completed local preparation (26 Oct)

- `npm ci` and `uv sync --locked --dev` both succeeded from the committed lock files; reran local tests afterward.
- Backend: 64 pytest tests, Ruff/format/mypy all passed. Frontend: lint/typecheck passed; production build and 10/10 Playwright tests passed. `npm audit` and backend `pip-audit` are clean after the pytest 8.4.2 advisory was fixed.
- The reproducible fixture-integrity script and Phase 5 metrics/limitations report are linked from `eval/README.md`. No model-quality or clinical metrics are invented.
- Updated `docs/10_demo_and_submission.md` with an explicitly labeled, synthetic-only rehearsal outline. It warns that the positive source-panel flow is an intercepted UI test fixture, not model output. No video or submission screenshot was generated.
- Reviewed docs for unsupported hackathon statistics: no project statistics requiring citation were found in README/docs/plan/eval text. Synthetic data is authored for this project; no external clinical dataset or font file is bundled. No `LICENSE` file exists; the team must choose and add a license before distribution.
- Credential-pattern scan found no matching provider/private-key strings in the scanned source workspace. Only `.env.example` is present; no screenshots/video/log files were found in the workspace. Git history was not scanned.

## Gate 3 checklist — not passed

- [ ] Official event and deadline/time zone confirmed (no event URL/name supplied; Oct 28 is only the planning assumption).
- [ ] Submission accepted; receipt/ID saved (not submitted).
- [x] Clean dependency installs and local automated checks green; recognized credential-pattern scan clean. This is **not** a clean clone or hosted CI run.
- [x] README and demo script reflect tested features and explicit limitations.
- [ ] Deployment logs/retention/region/CORS/provider settings checked — no public deployment; live provider disabled and deployment configuration unverified.
- [x] Safety/accessibility disclosures visible; automated axe, keyboard, and narrow viewport tests pass. Manual screen-reader/actual zoom review remains outstanding.
- [ ] Backup video ready — no recording exists. Local run path is documented; the positive explanation display is only available via a clearly labeled synthetic test fixture.

## Blockers / handoff

1. Gate 2 remains blocked; obtain model and human-review evidence plus manual accessibility review before calling this a release candidate.
2. Confirm the actual event URL, submission rules, official cutoff/time zone, and whether a clearly disclosed synthetic-only software demo is eligible despite Gate 2 being blocked.
3. Team must choose a project license and perform the Git tag/commit/history scan. Per standing instruction, no Git initialization, branch/commit/tag, Git checks, or repository administration were performed here.
4. Docker Compose configuration validates locally (docker compose config); image build/runtime was not executed because the local Docker daemon was unavailable. No clean clone, public URL, Devpost upload, video upload, or receipt has been tested or produced.
5. Before public exposure, review provider terms/retention/region, deployment logs, CORS, secret handling, and abuse/rate limits. There is no app-level public rate limiter.

**Exit:** not met. No submission or Gate 3 claim is made until the dependency, event, license, deployment, and submission blockers are resolved.

