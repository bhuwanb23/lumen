# Phase 5 — Evaluation, accessibility, reliability and hardening

**Window:** 26 Oct evening–27 Oct morning · **Status:** Planned · **Depends on:** Gate 1 and frozen optional work.

## Objective
Measure the system, fix critical defects, and produce an honest release candidate. No broad new features.

## Work breakdown
1. **Synthetic eval (1–2 h):** freeze gold set; run mock and model modes separately; calculate extraction precision/recall/F1, quote/span validity, human-labeled unsupported rate before/after verifier, abstention, refusal/false refusal, latency. Record N, exact model/prompt/version/date/config. Unknown metric = “not measured.”
2. **Red-team (45 min):** injection; missing/ambiguous facts; false reassurance; treatment, prognosis, dose, eligibility, urgent symptoms. Inspect examples, fix, rerun all regressions. Any critical unsafe output blocks release.
3. **Accessibility/localization (45 min):** axe scan + keyboard/screen reader smoke test, mobile, zoom, focus, contrast, announcements; remove unsupported locale if review incomplete.
4. **Reliability/security (45 min):** no/invalid key, timeout, rate limit/5xx, malformed payload, bad requests, CORS/body limits, no-store/security headers, upload limits if present, no-payload logs, secret and dependency scan.
5. **Report (30 min):** reproducible measured table; dataset size and review protocol; separate fixture checks from model eval and human language review.

## Gate 2 — by Oct 27 morning
- [ ] CI and all critical tests green.
- [ ] No unresolved critical unsafe result.
- [ ] Claims source-linked and verifier failures hidden.
- [ ] Results reproducible/provenanced; no guessed metrics.
- [ ] Accessibility blockers fixed; locale claims reflect actual review.
- [ ] Provider errors and data flow safe; logs clean.
- [ ] Optional features cut if they block any item.

## Exit
A clean release candidate has defensible measured results and written limitations. Freeze feature work before Phase 6.
