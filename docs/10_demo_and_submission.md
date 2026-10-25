# 10 — Demo and submission

## 2–3 minute narrative
1. Context: patients may see results before appointment; Lumen helps explain report wording, not advise.
2. Show a synthetic report and identify it as synthetic.
3. Submit in English or one reviewed locale; state that external model processing is enabled only with disclosure.
4. Open a claim's exact evidence, show a missing field stays unstated.
5. Show neutral care-team questions and safety boundary/refusal.
6. Show real evaluation N, method and limitations; explain it is not clinical validation.
7. Close with next step: clinician/patient advocate review before any real-world pilot.

## Demo resilience
Use one local synthetic fixture, not Wi-Fi-dependent real report. Have clearly labeled deterministic mock fallback if available; don't misrepresent mock output as live AI. Rehearse provider outage, missing key, poor input and no claims. Backup video/assets contain no PHI or secrets.

## Submission checklist
- Confirm official cutoff/time zone, materials/license/video rules.
- Freeze features by Oct 27 target; leave Oct 28 buffer.
- Clean clone/Docker run; CI green; dependency/secret scans clean.
- README accurately distinguishes implemented/planned/validated; metrics from actual harness only.
- Confirm license, attribution, font and public data terms.
- Review Devpost, video, screenshots, pitch claims and public URL in private browser.
- Check deployment/provider logs, retention, region, CORS, secrets; synthetic demo only.
- Submit early, save receipt/ID, verify link.

## Q&A anchors
- **No vector DB?** Exact authoritative lookup is more auditable for this narrow glossary use case.
- **Hallucination risk?** Source quotes, extraction contract, fact-only explanation, separate verifier, fail-closed checks; risk reduced, not eliminated.
- **Privacy?** No app report DB/logs, but model calls transmit content; synthetic-only demo and no compliance claim.
- **Prompt injection?** Documents are data; layered controls and red-team tests, not perfect immunity.
- **Trial eligibility?** Never decided; registry records are only discussion starters.
- **Languages?** Name only reviewed locales; model generation is not translation validation.
