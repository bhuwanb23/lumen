# 06 — Evaluation and test strategy

## Limits
Synthetic regression metrics do not establish clinical validity, safety on real reports, population performance, or translation quality. Publish metrics with N, method, model/prompt version, date and caveats. Never hand-fill results.

## Dataset
Begin with 8–12 entirely synthetic cases across a narrow declared set of report types/cancer contexts. Each case includes report, gold fields, exact quote/offset, expected missing/unclear fields, ambiguity notes, and forbidden inference. Include pathology and only limited radiology if schema is ready. Keep development cases separate from release regression set. No real or copied reports.

## Metrics
1. Field extraction precision/recall/F1; separate exact and normalized values.
2. Exact evidence quote validity and offset correctness.
3. Human-labeled unsupported-claim rate before/after verifier; define annotation protocol.
4. Abstention on missing/ambiguous information; absence must not count negative.
5. Scope-refusal success **and** false-refusal rate for prognosis, treatment, dose, beyond-report diagnosis, urgent triage, eligibility.
6. Prompt-injection resilience on adversarial document content.
7. English readability estimate via textstat; not comparable across languages and not a quality/safety measure.
8. Fluent medical-language review per locale: meaning, terminology, negation, tone, safety; record reviewer/date/sample.
9. Latency and availability under declared test environment, with no report payloads in metrics.

## Quality gates
- Unit: schemas, quote matching, Unicode offset mapping, safety filters, privacy/logging.
- Integration: mocked model, valid/invalid schemas, timeouts, rate limits; no live key in CI.
- E2E: submit → result → citation; errors/no claims; keyboard/narrow viewport.
- Red team: injected commands, false quote, partial support, unsafe question, locale mismatch.
- Static/security: Ruff, mypy, ESLint/TS, dependency audit, secret scan.
- CI runs deterministic tests and synthetic eval on every push.

## Release gates
**A — pipeline:** schemas pass; exact quotes checked; unsupported claims hidden; model/verifier failure is fail-closed; logs clean; scope tests pass agreed threshold.
**B — demo:** clean local end-to-end succeeds twice; exact source link; missing facts not inferred; error/no-claim paths work; copy and locale claims honest; CI green.
**C — submission:** README/results/demo reflect actual build; no fabricated metrics; dependency audit and privacy review done; submission receipt verified.

## Results template
| Measure | N / set | Result | Method / caveat |
|---|---:|---|---|
| Fact extraction F1 | — | Not measured until run | Synthetic only |
| Exact evidence validity | — | Not measured until run | Quote existence is not entailment |
| Unsupported claim rate before/after verifier | — | Not measured until human annotation | Annotator protocol required |
| Scope success / false refusal | — | Not measured until red-team run | Synthetic prompts |
| Translation review | — | Not measured | Reviewer/language required |
| Readability | — | Not measured | textstat approximate, English-centric |

Freeze versioned fixture set; report exact model ID, prompt version, decoding config, date, and failures. Favorable tiny score must not be called general accuracy.
