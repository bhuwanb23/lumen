# Phase 6 — Feature freeze, submission and backup demo

**Window:** 27 Oct (reserve into 28 Oct only if official cutoff requires) · **Status:** Planned · **Depends on:** Gate 2.

## Objective
Package and submit the tested build early; only fix release blockers after feature freeze.

## Work breakdown
1. **Freeze (30 min):** tag commit; freeze dependencies/prompts; rerun CI, clean clone, Compose, synthetic demo, secret/dependency scans. Search for real data in code, logs, assets, screenshots and history.
2. **Docs/claims (60 min):** README setup/config/data flow/safety/implemented-vs-planned; fill metrics only from Phase 5; verify citations for hackathon stats; check license, fonts and data terms.
3. **Demo assets (60–90 min):** rehearse 2–3 min; record backup if needed; inspect video for PHI, secrets, personal notifications, terminal env. Prepare architecture/safety explanation.
4. **Submit early:** complete Devpost/team/links; test public URL privately; upload video; save receipt/ID/screenshots.

## Checklist / Gate 3
- [ ] Official deadline/time zone confirmed.
- [ ] Submission accepted before cutoff; receipt saved.
- [ ] Clean install and CI green; no credentials or real reports.
- [ ] Claims/results/features match tested commit.
- [ ] Deployment logs/retention/region/CORS/provider settings checked; synthetic-only.
- [ ] Accessibility/safety disclosures visible.
- [ ] Backup video and local run path ready.

After submission, only blocking defect fixes; rerun impacted gates. Exit when receipt and stable release candidate exist.
