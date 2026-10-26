# Phase 3 UI demo and E2E checks

`fixtures.ts` is a **UI-only, synthetic presentation fixture** based on the existing lung biopsy sample in `eval/datasets/synthetic/reports.json`. Its mock response is written solely to exercise rendering and source-panel controls. It is not an evaluation answer key, not a model output, and not clinician-reviewed. Hand-authored gold fields remain in the separate evaluation answer-key file.

## Automated browser test

From `frontend/` with Node.js and `uv` installed:

```bash
npm ci
npx playwright install chromium
npm run test:e2e
```

`npm run test:e2e` builds the frontend, starts a temporary FastAPI instance on port 8001 with `MODEL_PROVIDER=disabled`, and starts Next.js on port 3001. Playwright's Chromium system libraries must also be installed for the host OS (Playwright may offer `npx playwright install --with-deps chromium` on Linux; this can require administrator privileges). No API key or external model call is used. Synthetic analysis responses are intercepted for the UI scenarios; one separate test submits through Next.js to FastAPI and confirms the disabled-provider error is safely handled.

Tests cover:
- Consent-gated submit, busy state, labeled and bounded text input, native short-text validation, and no upload control.
- Multi-citation source buttons operable by keyboard, with each opened panel displaying the exact synthetic quote.
- Explicit `not stated` display and no-claim response.
- Omitted-claim messaging without showing rejected text.
- Fixed refusal display with no report facts or claims.
- Service-outage state with no stale result.
- Real same-origin browser → Next.js → disabled FastAPI path.
- Mobile viewport overflow at 390 px and 320 px, skip link, keyboard focus, and source-panel keyboard operation.
- Automated axe WCAG 2.1 A/AA scan on form and rendered-result states (zero violations in the tested desktop viewport; not certification and not a screen-reader substitute).
- Same-origin browser requests, no provider host request, no provider credential names in loaded scripts, and no local/session storage or query-string payload.
- Proxy rejection of wrong content type, malformed JSON, and >1 MB bodies; `no-store` and security-header checks.

The backend's separate unit/API/provider mock tests exercise extraction, evidence rejection, verifier failure, and server-side redaction. A live positive-model flow is not available until an operator deliberately configures and reviews a provider; no keys or live calls are used by this demo suite.

## Manual smoke checklist

Use synthetic text only. Do not use real patient information.

- [ ] Open the page at desktop and a 390 px mobile width; confirm the purpose, medical limitations, synthetic/de-identification warning, and provider-processing disclosure appear before submitting. Confirm there is no upload control.
- [ ] Leave each acknowledgement unchecked in turn; confirm submission stays disabled. Check both, paste a synthetic excerpt, and verify the character counter, input limit, and busy/disabled state.
- [ ] In browser DevTools, confirm the browser calls only the same-origin `/api/health` and `/api/analyze` routes; no provider host, keys, report text in URL, local/session storage, or console output.
- [ ] In the happy-path Playwright fixture, open every citation by keyboard and confirm each labeled panel displays the exact matching quote. Verify neutral care-team questions and the after-result limitation/confirmation notice; the fixture is not exposed as a production UI toggle.
- [ ] Use the missing-fact, omitted-claim, refusal, and service-outage test cases; confirm missing facts stay unstated, rejected text is not displayed, and errors do not leave stale claims on screen.
- [ ] Tab through the page and source controls; confirm visible focus and that source panels open/close. Recheck no horizontal overflow on mobile.
- [ ] Run the real proxy path with `MODEL_PROVIDER=disabled`; expect a generic unavailable message and no claims. Do not treat this as a positive provider test.

For local production preview, `npm run build && npm run start` uses the standalone Next server; the start helper copies build static assets into its standalone tree. Docker Compose is a separate deployment path and remains to be verified on the target machine.
