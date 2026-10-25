# Phase 3 — Patient UI and vertical demo loop

**Window:** 25 Oct 2026, H8–H10 · **Status:** Planned · **Depends on:** Phase 2.

## Objective
Build a responsive interface for report text, evidence, clinician questions and honest limitations.

## Work breakdown
1. **Layout/notices (20 min):** accessible page; Lumen identity; concise purpose; non-medical notice; synthetic/de-identification warning; explain external processing when enabled. Text only in this phase—no fake upload control.
2. **Input/states (20 min):** labeled textarea, helper text, character limit, validation, busy/disabled state, generic timeout/provider/input errors. No URL/localStorage/console persistence.
3. **Results/evidence (30 min):** each claim has a keyboard-accessible “view source” control; exact quote panel with label; handle multiple citations; neutral care-team questions; no-claims and omitted-message states.
4. **Proxy/E2E (30 min):** browser → same-origin Next route → FastAPI; server-to-server only; max body, timeout, no-store; verify provider key absent from assets/network.
5. Test happy fixture, missing fact, rejected claim, service outage.

## Deliverables
Responsive Next.js UI, secure same-origin proxy, core E2E/manual checklist and synthetic demo fixture.

## Gate 1 — by Oct 25 H10
- [ ] Clean text submission to result works.
- [ ] Every result opens the exact supporting quote.
- [ ] Missing fact remains unstated.
- [ ] User sees limitations before and after processing.
- [ ] No-claim/service-down states are calm and actionable.
- [ ] Mobile viewport and keyboard navigation work.
- [ ] No secret or payload logging/storage.

If any item fails, repair the vertical slice before expanding. Attractive output without traceability fails Gate 1.
