import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

import {
  FIXED_REFUSAL_RESULT,
  HAPPY_RESULT,
  NO_CLAIMS_RESULT,
  REJECTED_CLAIM_RESULT,
  SYNTHETIC_REPORT,
} from "./fixtures";

async function stubHealth(page: Page) {
  await page.route("**/api/health", (route) =>
    route.fulfill({ status: 200, json: { status: "ok" } }),
  );
}

async function prepareForm(page: Page) {
  await page.goto("/");
  await page.getByRole("textbox", { name: "Report excerpt" }).fill(SYNTHETIC_REPORT);
  const submit = page.getByRole("button", { name: "Explain excerpt" });
  await expect(submit).toBeDisabled();
  await page.getByRole("checkbox").nth(0).check();
  await page.getByRole("checkbox").nth(1).check();
  await expect(submit).toBeEnabled();
  return submit;
}

function installAnalysisResponse(
  page: Page,
  response: unknown,
  delayMs = 0,
  onRequest?: (postData: unknown) => void,
) {
  const observedRequests: string[] = [];
  page.on("request", (request) => observedRequests.push(request.url()));
  page.route("**/api/analyze", async (route) => {
    onRequest?.(route.request().postDataJSON());
    if (delayMs) await new Promise((resolve) => setTimeout(resolve, delayMs));
    await route.fulfill({ status: 200, json: response });
  });
  return observedRequests;
}

test("happy synthetic flow reveals exact source panels for every citation", async ({ page }) => {
  await stubHealth(page);
  let submittedPayload: unknown;
  const observedRequests = installAnalysisResponse(
    page,
    HAPPY_RESULT,
    150,
    (payload) => { submittedPayload = payload; },
  );
  const submit = await prepareForm(page);

  await submit.click();
  await expect(page.getByRole("status").filter({ hasText: "being checked" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Verifying report…" })).toBeDisabled();
  await expect(page.getByRole("heading", { name: "What the report says" })).toBeVisible();
  await expect(page.getByText("Questions you could ask your care team")).toBeVisible();
  await expect(page.getByText("Could you explain what the report's biomarker results line means?")).toBeVisible();

  const firstSource = page.getByRole("button", { name: "View source 1 for histology" });
  await expect(firstSource).toHaveAttribute("aria-expanded", "false");
  const firstPanelId = await firstSource.getAttribute("aria-controls");
  const firstButtonId = await firstSource.getAttribute("id");
  expect(firstPanelId).toBeTruthy();
  expect(firstButtonId).toBeTruthy();
  const firstPanel = page.locator(`#${firstPanelId}`);
  const firstSourceButton = page.locator(`#${firstButtonId}`);
  await firstSourceButton.focus();
  await page.keyboard.press("Enter");
  await expect(firstSourceButton).toHaveAttribute("aria-expanded", "true");
  await expect(firstPanel).toBeVisible();
  await expect(firstPanel).toContainText("Exact wording from the submitted excerpt");
  await expect(firstPanel).toContainText("Adenocarcinoma, acinar pattern");

  const secondSource = page.getByRole("button", { name: "View source 2 for biomarkers" });
  const secondPanelId = await secondSource.getAttribute("aria-controls");
  expect(secondPanelId).toBeTruthy();
  await secondSource.click();
  await expect(page.locator(`#${secondPanelId}`)).toContainText("PD-L1 tumor proportion score: 15%");
  const molecularSource = page.getByRole("button", { name: "View source 1 for molecular test status" });
  const molecularPanelId = await molecularSource.getAttribute("aria-controls");
  expect(molecularPanelId).toBeTruthy();
  await molecularSource.click();
  await expect(page.locator(`#${molecularPanelId}`))
    .toContainText("EGFR mutation testing: Not performed on this specimen.");

  expect(observedRequests.some((url) => new URL(url).pathname === "/api/analyze")).toBe(true);
  expect(observedRequests.every((url) => url.startsWith("http://localhost:3001/"))).toBe(true);
  expect(observedRequests.some((url) => /anthropic|openrouter|ollama/i.test(url))).toBe(false);
  expect(submittedPayload).toMatchObject({
    report_text: SYNTHETIC_REPORT,
    data_is_synthetic_or_deidentified: true,
    external_processing_acknowledged: true,
  });
  const scriptUrls = await page.locator("script[src]").evaluateAll((scripts) =>
    scripts.map((script) => (script as HTMLScriptElement).src),
  );
  for (const scriptUrl of scriptUrls) {
    const asset = await page.request.get(scriptUrl);
    expect(asset.ok()).toBe(true);
    const source = await asset.text();
    expect(source).not.toMatch(/ANTHROPIC_API_KEY|OPENROUTER_API_KEY|OLLAMA_VERIFIER_MODEL/);
  }
  expect(await page.locator('input[type="file"]').count()).toBe(0);
  expect(await page.evaluate(() => ({
    local: Object.keys(localStorage),
    session: Object.keys(sessionStorage),
  }))).toEqual({ local: [], session: [] });
  expect(new URL(page.url()).search).toBe("");
});

test("short text is blocked by native validation before the proxy is called", async ({ page }) => {
  await stubHealth(page);
  let called = false;
  await page.route("**/api/analyze", async (route) => {
    called = true;
    await route.fulfill({ status: 200, json: HAPPY_RESULT });
  });
  await page.goto("/");
  const report = page.getByRole("textbox", { name: "Report excerpt" });
  await expect(report).toHaveAttribute("minlength", "20");
  await expect(report).toHaveAttribute("maxlength", "50000");
  await report.fill("Too short");
  await page.getByRole("checkbox").nth(0).check();
  await page.getByRole("checkbox").nth(1).check();
  await page.getByRole("button", { name: "Explain excerpt" }).click();

  expect(await report.evaluate((element: HTMLTextAreaElement) => element.validity.tooShort)).toBe(true);
  expect(called).toBe(false);
});

test("missing report fields remain explicitly unstated and no-claim state is calm", async ({ page }) => {
  await stubHealth(page);
  installAnalysisResponse(page, NO_CLAIMS_RESULT);
  const submit = await prepareForm(page);
  await submit.click();

  await expect(page.getByRole("status").filter({ hasText: "No explanation statements passed" })).toBeVisible();
  await expect(page.getByText("2 proposed statement(s) were omitted.")).toBeVisible();
  await page.getByText("Extracted report fields and exact evidence").click();
  await expect(page.getByText("stage:")).toBeVisible();
  await expect(page.getByText("Not stated in this excerpt")).toBeVisible();
  await expect(page.getByText(/stage IV/i)).toHaveCount(0);
  await expect(page.getByRole("button", { name: /View source/ })).toHaveCount(0);
});

test("omitted-claim state reports filtering without rendering rejected text", async ({ page }) => {
  await stubHealth(page);
  installAnalysisResponse(page, REJECTED_CLAIM_RESULT);
  const submit = await prepareForm(page);
  await submit.click();

  await expect(page.getByText("1 proposed statement(s) were omitted by verification.", { exact: false })).toBeVisible();
  await expect(page.getByText(/unsupported demonstration claim/i)).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "What the report says" })).toBeVisible();
});

test("fixed refusal renders no report claims or source controls", async ({ page }) => {
  await stubHealth(page);
  installAnalysisResponse(page, FIXED_REFUSAL_RESULT);
  const submit = await prepareForm(page);
  await page.locator("#user-question").fill("How long do I have to live?");
  await submit.click();

  await expect(page.getByRole("status").filter({ hasText: "I can't estimate prognosis" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "What the report says" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /View source/ })).toHaveCount(0);
  await expect(page.getByText("No report interpretation was produced for this request.")).toBeVisible();
});

test("real same-origin proxy reaches FastAPI while models remain disabled", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => requests.push(request.url()));
  await page.goto("/");
  await expect(page.getByRole("status").filter({ hasText: "API reachable" })).toBeVisible();
  await page.getByRole("textbox", { name: "Report excerpt" }).fill(SYNTHETIC_REPORT);
  await page.getByRole("checkbox").nth(0).check();
  await page.getByRole("checkbox").nth(1).check();
  await page.getByRole("button", { name: "Explain excerpt" }).click();

  await expect(page.locator('p[role="alert"]')).toContainText("Analysis is unavailable");
  await expect(page.getByRole("heading", { name: "Result" })).toHaveCount(0);
  expect(requests.some((url) => new URL(url).pathname === "/api/analyze")).toBe(true);
  expect(requests.every((url) => url.startsWith("http://localhost:3001/"))).toBe(true);
  expect(requests.some((url) => /anthropic|openrouter|ollama/i.test(url))).toBe(false);
});

test("proxy and health routes enforce bounds, no-store, and security headers", async ({ request }) => {
  const health = await request.get("http://localhost:3001/api/health");
  expect(health.status()).toBe(200);
  expect(health.headers()["cache-control"]).toContain("no-store");

  const wrongType = await request.post("http://localhost:3001/api/analyze", {
    data: "{}",
    headers: { "Content-Type": "text/plain" },
  });
  expect(wrongType.status()).toBe(415);
  const headers = wrongType.headers();
  expect(headers["cache-control"]).toContain("no-store");
  expect(headers["x-content-type-options"]).toBe("nosniff");
  expect(headers["x-frame-options"]).toBe("DENY");
  expect(headers["referrer-policy"]).toBe("no-referrer");
  expect(headers["permissions-policy"]).toBe("camera=(), microphone=(), geolocation=()");
  expect(headers["x-powered-by"]).toBeUndefined();

  const malformed = await request.post("http://localhost:3001/api/analyze", {
    data: Buffer.from("{not json"),
    headers: { "Content-Type": "application/json" },
  });
  expect(malformed.status()).toBe(400);
  expect(malformed.headers()["cache-control"]).toContain("no-store");
  expect(await malformed.text()).not.toContain("not json");

  const oversized = await request.post("http://localhost:3001/api/analyze", {
    data: JSON.stringify({ report_text: "x".repeat(1_000_100) }),
    headers: { "Content-Type": "application/json" },
  });
  expect(oversized.status()).toBe(413);
  expect(oversized.headers()["cache-control"]).toContain("no-store");
  expect(await oversized.text()).not.toContain("x".repeat(100));
});

test("service outage clears claims and offers a generic actionable error", async ({ page }) => {
  await stubHealth(page);
  await page.route("**/api/analyze", (route) =>
    route.fulfill({
      status: 503,
      json: { detail: "Analysis is unavailable. No generated claims were returned." },
    }),
  );
  const submit = await prepareForm(page);
  await submit.click();

  await expect(page.locator('p[role="alert"]')).toContainText("Analysis is unavailable");
  await expect(page.locator('p[role="alert"]')).toContainText("No generated claims were returned.");
  await expect(page.getByRole("heading", { name: "Result" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /View source/ })).toHaveCount(0);
});

test("axe WCAG 2.1 A/AA scan passes on form and rendered results", async ({ page }) => {
  await stubHealth(page);
  installAnalysisResponse(page, HAPPY_RESULT);
  const documentResponse = await page.goto("/");
  const headers = documentResponse?.headers() ?? {};
  expect(headers["x-content-type-options"]).toBe("nosniff");
  expect(headers["x-frame-options"]).toBe("DENY");
  expect(headers["referrer-policy"]).toBe("no-referrer");
  expect(headers["permissions-policy"]).toBe("camera=(), microphone=(), geolocation=()");
  expect(headers["x-powered-by"]).toBeUndefined();

  const scan = () => new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  const formResults = await scan();
  expect(formResults.violations).toEqual([]);

  await page.getByRole("textbox", { name: "Report excerpt" }).fill(SYNTHETIC_REPORT);
  await page.getByRole("checkbox").nth(0).check();
  await page.getByRole("checkbox").nth(1).check();
  await page.getByRole("button", { name: "Explain excerpt" }).click();
  await expect(page.getByRole("heading", { name: "Result" })).toBeVisible();

  const resultResults = await scan();
  expect(resultResults.violations).toEqual([]);
});

test("mobile layout stays within viewport and keyboard reaches form and source controls", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await stubHealth(page);
  installAnalysisResponse(page, HAPPY_RESULT);
  await page.goto("/");

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to main content" })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("textbox", { name: "Report excerpt" })).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

  await page.getByRole("textbox", { name: "Report excerpt" }).fill(SYNTHETIC_REPORT);
  await page.getByRole("checkbox").nth(0).check();
  await page.getByRole("checkbox").nth(1).check();
  await page.getByRole("button", { name: "Explain excerpt" }).click();
  const source = page.getByRole("button", { name: "View source 1 for histology" });
  const sourcePanelId = await source.getAttribute("aria-controls");
  const sourceButtonId = await source.getAttribute("id");
  expect(sourcePanelId).toBeTruthy();
  expect(sourceButtonId).toBeTruthy();
  const sourceButton = page.locator(`#${sourceButtonId}`);
  await sourceButton.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(`#${sourcePanelId}`)).toContainText("Adenocarcinoma, acinar pattern");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.setViewportSize({ width: 320, height: 800 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
