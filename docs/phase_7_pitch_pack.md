# Phase 7 — Finals/judge-demo pitch pack (draft)

**Prepared:** 26 Oct 2026 IST · **Status:** Draft only; event/judging format unconfirmed; Phase 6/Gate 2 not complete. These scripts are not rehearsed or timed aloud.

## Non-negotiable demo disclosure

Lumen is a synthetic-only, English-only software prototype—not medical advice, a diagnostic tool, a clinical product, or clinically validated. `MODEL_PROVIDER=disabled` in the demo. The actual browser → Next.js → FastAPI path returns a generic unavailable message with no claims. The positive source-panel scenario exists only as a deterministic synthetic Playwright UI fixture; it is not model output, an answer key, or clinical guidance. If displayed, label it visibly and say so aloud.

## 60-second version (~128 words)

Lumen is a narrow, English-only prototype for making cancer pathology-report wording easier to discuss with a care team. It does not diagnose, estimate outcomes, recommend treatment, or replace a clinician. The interface accepts synthetic text only and shows a clear external-processing disclosure. In the demo, the model provider is disabled: the real browser-to-API path safely returns an unavailable message and no claims. The source-linked result example is a deterministic synthetic UI test fixture—not a model answer. The software checks citation spans against the submitted text, exposes exact quotes, and has fixed refusals and fail-closed states. Our dataset contains eight fictional reports and 46 expected fact labels; 34 of 34 gold quote offsets match their fixture text. That is fixture integrity, not model accuracy. No model evaluation, human claim review, or clinical validation has been done. This is not ready for patient use.

## 3-minute version (~360 words)

**Opening.** A pathology report can contain unfamiliar wording that a person may want to discuss with their care team. Lumen is a small prototype for explaining wording from a report excerpt and helping prepare neutral questions. Its scope is intentionally narrow: English text only, no diagnosis, prognosis, treatment ranking, dose advice, clinical-trial eligibility decision, or urgent-symptom triage.

**Show the boundary first.** This demo uses fictional synthetic text. It asks for explicit acknowledgements and explains that an operator-configured model service may process the text. The provider is disabled here. When we submit through the actual browser-to-Next-to-FastAPI route, the service returns a generic unavailable response and no claims; we will not present that as a positive model result.

**Explain the evidence design.** In the separate, clearly labeled Playwright UI fixture, each supported statement has a keyboard-accessible source control. Opening it shows the exact quoted excerpt, and missing information remains “not stated.” That fixture tests rendering only; its answer was written to exercise the interface. It is not an evaluation answer, a live model output, or clinician-reviewed content. The backend code uses strict response contracts, exact evidence-span checks, a distinct verifier, deterministic scope refusals, and fail-closed errors. These are software controls—not proof that a model is clinically safe.

**State the measurements honestly.** The frozen synthetic corpus has eight fictional reports, 46 expected field labels, and 34 non-null gold evidence spans; the fixture-integrity check found 34/34 exact quote-and-offset matches. We have 64 backend tests and 10 browser E2E tests, including disabled-provider, invalid-input, outage, request-bound, keyboard, mobile and automated accessibility scenarios. We have not run a live model, collected human claim-support labels, or measured extraction quality, unsupported-claim rates, refusal performance, or model latency. There is no clinician review or clinical validation.

**Close.** The demo is a software prototype, not a patient service. Before any real-world use, the work would need clinician and patient review, human-labeled evaluation, privacy/security and deployment review, and manual accessibility testing. We will describe those as future prerequisites, not promise an unreviewed pilot.

## 5-minute version (~610 words)

**1. Problem and narrow use (0:00–0:40).** People may encounter technical pathology wording before they have a chance to discuss it with their care team. Lumen explores one limited task: helping a person read wording that is present in a pathology excerpt and prepare neutral questions. We are not making a claim about how common this is, and we are not trying to replace clinical interpretation. The interface is English-only and text-only.

**2. Safety boundary (0:40–1:20).** Lumen is not a clinical tool or medical advice. It cannot diagnose, predict survival or recurrence, choose or rank treatments, provide dosing, determine trial eligibility, or triage urgent symptoms. It asks users to submit only synthetic or properly de-identified text and discloses that, if an operator enables a model provider, submitted text may be sent to that service. In this demonstration the provider is disabled, and no credentials or live model requests are used. We have not reviewed a deployment provider's retention terms, data region, or legal suitability.

**3. What is actually running (1:20–2:00).** The browser calls same-origin Next.js routes; the server-side proxy sends bounded, no-store requests to FastAPI. Provider credentials are kept server-side. With the model disabled, the live vertical flow returns a generic unavailable state and no claims. We will show that safe failure rather than imply that the prototype currently produces a live explanation. The positive source-panel screen is from a deterministic, synthetic Playwright UI fixture. If shown, it is labeled as a UI test fixture and not model output.

**4. Evidence and failure controls (2:00–3:05).** The intended result path uses constrained schemas, exact source-span validation, a separately configured verifier, fixed refusals for prohibited requests, and no-claim behavior when evidence does not pass checks. In the UI, source buttons work by keyboard and open a labeled quote panel. Missing facts are shown as not stated in this excerpt, not as normal or negative. The app does not store reports in its URL, browser storage, or application database; provider processing and retention would still depend on the operator's configuration. The checks reduce some software failure modes, but they do not establish model reliability or eliminate prompt-injection risk.

**5. Evidence we have—and do not have (3:05–4:10).** The frozen synthetic set contains eight fictional reports, 46 expected fact labels, and 34 non-null gold spans. A reproducible integrity script confirms all 34 quote-and-offset pairs point to the exact fixture text. That verifies the authored test assets, not a model. The current test suite has 64 backend tests and 10 Playwright flows. Automated axe WCAG 2.1 A/AA scans report zero violations in the tested form/result states; keyboard and 320/390-pixel viewport checks pass. We have not done live model evaluation, human claim-level labeling, clinician review, screen-reader testing, or clinical validation. Extraction scores, unsupported-claim rates, refusal rates, and latency are not measured. We will say “not measured,” not infer a score from passing software tests.

**6. Next step and close (4:10–5:00).** The responsible next step is independent clinician and patient review of the task, examples, safety language and evaluation protocol, alongside privacy, security, accessibility and deployment review. Only then could a carefully scoped next evaluation be considered. No real patient information is accepted for this demo, and there is no promise of a pilot or clinical benefit. Lumen remains a synthetic-only prototype.

## Judge Q&A: short, defensible answers

- **Does it improve clinical outcomes?** Unknown. No clinical study or patient-outcome evaluation was performed.
- **How accurate is it?** Not measured. The 34/34 result is exact-span integrity for authored gold fixtures, not model accuracy; no model was run.
- **Why should users trust the answer?** They should not treat it as a clinical answer. The design exposes source quotes and fails closed, but these software checks do not prove clinical correctness.
- **How do you handle privacy?** The demo uses synthetic text and the provider is disabled. There is no app-side report database or browser storage. If enabled, an operator-selected provider may process text; its retention/region terms have not been validated for deployment.
- **Does it accept PDFs or images?** No. File/OCR support was deferred because text review, limits, cleanup and citation mapping were unproven.
- **Does it support Tamil or another language?** No; English only. No fluent medical reviewer was supplied.
- **What about prompt injection?** The system treats report text as untrusted and has synthetic tests, but this is not a guarantee against all attacks; no live model red-team evaluation was run.
- **Can it assess trial eligibility or recommend treatment?** No. Those are out of scope and trigger fixed refusals.
- **Is the submission/demo schedule confirmed?** Not yet. The event and official deadline are unknown, and Phase 6 is on hold pending Gate 2.

## Rehearsal/demo checklist

- [ ] Confirm event, format, room/network, time limits, permitted materials, and official deadline.
- [ ] Rehearse each version with a timer; these drafts have not been spoken aloud or time-validated.
- [ ] Use only the tested build; no feature toggles or unreviewed hotfixes.
- [ ] If showing the fixture, keep “synthetic UI test fixture — not model output” visible and spoken.
- [ ] Test the actual judging machine and network; provider-disabled failure and local dependencies are explicit constraints.
- [ ] No offline video exists. If one is later recorded, inspect every frame/audio track for identifiers, secrets, personal notifications, and misleading model/clinical claims.
- [ ] Collect judge feedback without promising clinical pilots, data processing terms, or unsupported features.
