# 05 — Safety, privacy, and security

## Intended use / prohibited use
Lumen is a hackathon prototype, not clinically validated. It may explain wording explicitly present in a report, define reviewed terms, state that something is not mentioned, offer neutral care-team questions, and surface public trials as discussion starters. It must never diagnose, restage, fill omissions, forecast survival/prognosis/recurrence, recommend/rank treatment or dose, determine trial eligibility, or triage symptoms.

## Fail-closed requirements
- Invalid schema, missing credentials, API outage, malformed output, unsupported language, failed quote, verifier timeout, or failed source mapping → no speculative summary.
- Claims shown only when exact cited source text is present and the whole claim passes separate semantic verification.
- Empty result → neutral “could not verify” state and clinician referral.
- OCR must be shown for review before model analysis.
- Model-generated questions require scope validation; if unsafe or uncertain, suppress or use reviewed static templates.
- Documents are untrusted input: delimit; instruct model to treat as evidence, not commands; constrain schema; verify output; include injection tests. This reduces risk but does not guarantee immunity.

## Refusal copy (draft)
- Treatment: “I can’t recommend or compare treatments. Your oncology team can discuss options for your situation. I can help point to wording in your report.”
- Prognosis: “I can’t estimate prognosis or survival from a report. Please ask your care team, who can interpret your full clinical context.”
- Beyond-report diagnosis: “I can explain what the document says, but I can’t diagnose or interpret findings beyond it.”
- Urgent symptoms: “Lumen can’t assess urgent symptoms. Contact local emergency services or your clinical team now.” No symptom triage logic.

## Privacy rules
- Stateless request handling; no report database, account, or history.
- Never log raw text, prompts, quotes, answers, filenames, IDs, or exception bodies; no session replay/analytics on report pages.
- No report in browser storage, service-worker cache, URL, test artifact, screenshot, or public demo.
- Disclose that model processing transmits submitted content to configured provider; statelessness does not remove provider processing/retention.
- Public demos, CI, and eval use synthetic data only.
- De-identification is best effort, not a guarantee. Real-data pilot requires qualified legal/privacy/security/clinical review, suitable provider terms/DPA, applicable compliance assessment, and formal safety review. Do not claim HIPAA/other compliance based on architecture alone.

## Security checklist
Server-side env/secret manager; no `NEXT_PUBLIC_` secrets; CORS allowlist; content type and request limits; rate limit; timeout/backoff; generic errors; standard security headers; HTTPS; dependency audit; secret scan; least privilege; safe upload handling; temporary-file cleanup; strict PDF/image bounds; sanitized HTML to PDF; no report-bearing telemetry. Inspect Vercel/backend/provider logs/retention before public deployment.

## Tests
Prompt injection in report; malicious instructions in image/PDF; oversized/malformed/MIME-spoofed/encrypted/corrupt files; huge page count/decompression bomb; missing/false quotes; contradictory findings; verifier failure; CORS/cache/security headers; rate limits; no-body logging; leaked secrets. Any critical unsafe output blocks release.

## Human factors
Neutral language; no fear-inducing “good/bad” labels; don't equate “positive” with a lay conclusion; don't imply reassurance. Persistent clinician-confirmation notice. No suggestion to delay care.
