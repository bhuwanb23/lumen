# 10 — Demo and submission readiness

## Current state (26 Oct 2026)

This is a synthetic-only, English-only software prototype. `MODEL_PROVIDER=disabled` by default; no live model-generated explanation is available in the production demo path. The same-origin integration test deliberately submits to FastAPI with the provider disabled and expects a generic unavailable response. The positive source-panel rendering flow in Playwright uses a **synthetic UI-only test fixture**, not model output; label it clearly if shown. No model-quality metrics or clinical validation exist. See [`../eval/phase_5_report.md`](../eval/phase_5_report.md).

There is no project `LICENSE` file or recorded submission/video asset in the workspace. No external font file or external clinical dataset is bundled. Do not imply a license or third-party data clearance that has not been established. Hackathon/event identity and official cutoff/time zone still need confirmation. Phase 6 is blocked on Phase 5 Gate 2, which is not passed.

## 2–3 minute rehearsal outline (draft; not a recording)

1. **Context (0:00–0:20):** Lumen is a prototype for explaining wording in a pathology excerpt and preparing neutral questions—not medical advice, diagnosis, prognosis, treatment guidance, or clinical validation.
2. **Data boundary (0:20–0:40):** Use only the synthetic excerpt; explicitly state no real patient data is used and the model provider is disabled in this demo.
3. **Input flow (0:40–1:00):** Show labeled English text input, character bound, synthetic/de-identification and processing acknowledgements, and visible safety limits. Do not imply upload/OCR exists.
4. **Evidence interaction (1:00–1:35):** If showing the Playwright synthetic fixture, label it **“deterministic UI test fixture; not model output.”** Open a keyboard-accessible source panel and point out the exact quoted words. Do not portray the fixture as AI or a clinical answer.
5. **Missing fact / safe failure (1:35–2:00):** Show the fixture's missing-field and no-claims state, plus the live provider-disabled generic unavailable state. Explain that absent text stays “not stated”; no claim is made about the full medical record.
6. **Safety and evaluation (2:00–2:30):** Describe source checks, verifier fail-closed behavior, refusals, and synthetic regression coverage. State that 8 synthetic reports / 46 expected fact labels and 34/34 gold-span integrity checks are fixture checks—not model accuracy. Unsupported-claim and clinical metrics are not measured.
7. **Close (2:30–2:45):** No patient use. A clinician and privacy/security review would be required before any real-world pilot.

## Recording safety checklist (not yet recorded)

- [ ] Record only after the event/recipient approves a demo-only scope despite Gate 2 being blocked.
- [ ] Use a clean desktop/browser profile and synthetic excerpts. Close personal tabs/notifications; never show `.env`, credentials, or a real provider console.
- [ ] If the UI fixture is used, show an explicit on-screen/voice label that it is deterministic test data, not model output. Do not edit away errors or imply unsupported model performance.
- [ ] Inspect every frame/audio track for identifiers, secrets, personal notifications, report text, terminal environment output, and misleading claims before sharing.
- [ ] No backup video currently exists; no video or screenshot has been generated as a submission asset.

## Local run path

See the root README for backend and frontend setup. The production preview runs locally on port 3000 with FastAPI on port 8000; model processing remains disabled. Use the same-origin `/api/health` and `/api/analyze` routes. The browser-to-FastAPI test path uses a temporary backend and disabled provider. Do not enter real patient data.

## Submission checklist — not cleared

- Confirm event name, official deadline/time zone, allowed license/materials, and whether a synthetic-only demo with Gate 2 blocked is eligible.
- Resolve Gate 2 blockers before claiming a release candidate: provider/model evaluation, human claim-level review, manual screen-reader/zoom check, deployment/privacy/abuse review.
- The user/team must choose and provide a project license; none is present.
- User handles Git tag/commit/history and repository administration. These are intentionally not performed here.
- No Devpost submission, public URL, video upload, receipt/ID, clean-clone test, or Docker Compose test has been completed.
- Current dependency/security checks: frontend and Python dependency audits clean after pytest upgrade; credential-pattern scan found no matching key/private-key strings in the workspace, and only `.env.example` is present. Git history was not scanned.
- Accessibility/safety disclosures are visible and tested. No real report, live API key, or external provider call was used.

## Q&A anchors

- **Hallucination risk?** Exact source spans, separate verifier checks, fixed refusals, and fail-closed tests reduce some software risks; live model behavior was not evaluated, so residual model risk is unknown.
- **Privacy?** The demo uses synthetic data and has no report database; if an operator enables a provider, submitted text is sent to that configured service. Provider privacy/retention terms were not reviewed for a deployment.
- **Prompt injection?** Reports are treated as untrusted input; layered controls have synthetic tests, not a guarantee of immunity.
- **Languages?** English-only; no translation or additional language review is claimed.
- **Trial eligibility?** Not determined. No trial integration is implemented.
