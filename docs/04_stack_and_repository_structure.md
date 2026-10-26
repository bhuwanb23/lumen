# 04 — Stack and proposed repository structure

## Stack decisions
| Layer | Choice | Reason / guardrail |
|---|---|---|
| Web | Latest compatible stable Next.js, TypeScript, Tailwind, shadcn/ui | Polished typed UI; provider secrets server-side; pin versions and audit. |
| Mobile | Installable PWA/camera | Useful for paper reports; only after secure upload/OCR; never cache report offline. |
| Accessibility/i18n | next-intl, Noto Sans Tamil/Devanagari, large text, axe + manual WCAG AA checks | Language only considered supported after end-to-end fluent review. |
| Evidence UI | Custom React claim/source component | Exact quote discoverability, keyboard and screen-reader accessible. |
| API | FastAPI, Python 3.12, Pydantic v2, async httpx | Typed contracts and Python evaluation ecosystem. |
| LLM | Implemented server-side adapters for Anthropic direct, OpenRouter, and Ollama | `MODEL_PROVIDER=disabled` by default; no silent failover; server-side keys; distinct generator and verifier model IDs required. Mock-tested only. Live structured-output compatibility, terms/retention, cost, latency, and privacy remain to be reviewed per model/deployment. Ollama is not presumed local. |
| PII | Microsoft Presidio + custom recognizers | Best-effort detection; measure false negatives and preserve citation mapping. |
| Glossary | NCI Dictionary/Thesaurus + SQLite FTS5 cache | Deterministic source lookup; access/licensing/caching terms not yet confirmed. |
| Trials | ClinicalTrials.gov API v2, TTL/rate-limited cache | Public data; “ask clinician” only, never eligibility decision. |
| PDF | WeasyPrint | Candidate for script rendering; must test actual Tamil/Hindi fonts/glyphs. |
| Readability | textstat | Approximate English measure only; not translation quality. |
| Evaluation | pytest + custom harness + promptfoo | Reproducible synthetic and red-team tests; not clinical validation. |
| Observability | Structured JSON metadata logs; optional Langfuse | No payloads; traces off by default. |
| Gates | Ruff, mypy, ESLint, Playwright, pre-commit/detect-secrets | Engineering discipline, with each gate actually run in CI. |
| CI/deploy | GitHub Actions; Docker Compose; Vercel + Cloud Run/Fly.io/Render | Reproducible local demo; inspect logs/retention and provider terms. |

## Proposed tree (for future implementation)
```text
lumen/
├── README.md, .env.example, .gitignore, docker-compose.yml
├── frontend/
│   ├── app/ (routes/layout); app/api/analyze/route.ts (server proxy)
│   ├── components/ (accessible UI); i18n/; lib/; public/ (manifest/icons)
│   └── tests/e2e/ (Playwright)
├── backend/
│   ├── app/main.py; app/api/; app/core/; app/schemas/
│   ├── app/services/{ingest,deidentify,extract,explain,verify,safety,
│   │   translate,glossary,trials,prep_card}.py
│   ├── tests/; pyproject.toml; Dockerfile
├── eval/datasets/synthetic/; eval/redteam/; eval/run_eval.py; eval/results/
├── docs/; plan/; .github/workflows/
```

## Integration spikes before commitment
1. Confirm current NCI access mechanism, attribution/licence, caching permission, coverage and rate limits.
2. Test Presidio with synthetic English/Tamil/Hindi/mixed-script PHI and citation mapping; do not imply full detection.
3. Render a one-page WeasyPrint Tamil/Hindi synthetic card; inspect shaping, wrapping, font embedding/licensing.
4. Confirm Claude model structured-tool compatibility, image limits, terms/retention, cost and timeouts.
5. Validate ClinicalTrials.gov query fields/status/date/cache semantics with current API docs.

Listing an integration in this plan does not mean it is implemented or verified.
