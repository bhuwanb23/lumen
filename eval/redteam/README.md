# Red-team prompt suite

`cases.json` contains 16 synthetic-only safety and benign-control cases with expected action and prohibited output categories written before any model run. Categories include embedded document instructions, prognosis/survival, treatment choice, dosage, diagnosis beyond the report, urgent symptoms, trial eligibility, missing fields, ambiguity, and benign source-grounded requests.

Phase 1 tests only validate suite structure/coverage. No LLM was run and no refusal-performance score exists. In Phase 2, run these through the pipeline using synthetic report text, inspect the exact transcript and citations, and label correct refusal, safe answer, safe abstention, over-refusal, or unsafe compliance using `../annotation_guide.md`.

Never submit real reports to promptfoo or a hosted red-team service. Do not treat passing a small prompt list as proof of prompt-injection immunity.
