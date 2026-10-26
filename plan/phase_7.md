# Phase 7 — Finals and judge-demo readiness

**Window:** 28 Oct–1 Nov 2026, conditional on official schedule · **Status:** Pitch preparation drafted; finals readiness blocked pending Phase 6 · **Depends on:** Phase 6.

## Objective
Defend product and safety choices with clarity and demonstrate the submitted build. Do not use this period for uncontrolled feature expansion.

## Current status

- Phase 6 is on hold by user decision pending Gate 2; no submission, receipt, release tag, official event, or exact judging build is confirmed.
- The event name/URL, official schedule, pitch limits, room/network and demo environment remain unknown.
- `docs/phase_7_pitch_pack.md` now contains 60-second, 3-minute and 5-minute drafts, judge Q&A, and a disclosure-first demo checklist. Drafts were not spoken aloud or timed.
- The local model provider remains disabled. Live same-origin analysis returns a generic unavailable response; a positive source-panel UI is only a labeled synthetic Playwright fixture. No offline video exists.
- Metrics and claims in the pitch pack match `eval/phase_5_report.md`; model quality, unsupported-claim rates, and clinical outcomes are explicitly not measured.

## Required next steps (only after Phase 6 clears)

1. Confirm the event and official schedule; obtain judging format, room/network, pitch time, and permitted materials.
2. Rehearse each draft against a timer and on the exact submitted release build/commit.
3. Test live demo and a clearly labeled synthetic/video fallback on the actual environment. Never imply fixture output is AI output.
4. Keep the stable tested build; if a bug appears, assess safety and avoid an untested hotfix.
5. Capture judge feedback without promising a pilot, provider retention terms, or unsupported features.

## Acceptance

- [ ] All pitch versions rehearsed on time.
- [x] Draft metrics and implementation claims are defensible and explicitly distinguish fixture integrity from model evaluation.
- [ ] Live and backup demo tested on the confirmed judging environment.
- [x] “Not measured/not known” is stated where evidence is absent.
- [x] No feature was added to bypass safety or evaluation gates.

**Exit:** not met. Do not claim finals readiness until Phase 6, Gate 2, and event confirmation are resolved.
