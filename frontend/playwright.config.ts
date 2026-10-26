import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  reporter: "list",
  outputDir: "/tmp/lumen-phase3-playwright-results",
  use: {
    baseURL: "http://localhost:3001",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    ...devices["Desktop Chrome"],
  },
  webServer: [
    {
      command: "uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8001",
      cwd: "../backend",
      url: "http://127.0.0.1:8001/health",
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        PATH: `${process.env.HOME ?? ""}/.local/bin:${process.env.PATH ?? ""}`,
        APP_ENV: "test",
        MODEL_PROVIDER: "disabled",
        CORS_ORIGINS: "http://localhost:3001",
      },
    },
    {
      command: "npm run start",
      url: "http://localhost:3001",
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        BACKEND_URL: "http://127.0.0.1:8001",
        HOSTNAME: "0.0.0.0",
        PORT: "3001",
        NEXT_TELEMETRY_DISABLED: "1",
      },
    },
  ],
});
