# Clinical review packet

This packet supports future human review of Lumen's synthetic evaluation artifacts.
It is not clinical validation and does not authorize patient-facing use.

## Contents

- `review_checklist.md`: reviewer instructions and safety checks.
- `fact_review_template.csv`: field-level review template.
- `claim_review_template.csv`: claim-level review template.
- `question_review_template.csv`: care-team question review template.
- `provenance_template.json`: run and reviewer provenance template.

## Rules

- Keep the frozen synthetic dataset and answer keys unchanged during review.
- Record reviewer role, date, and disagreement/adjudication.
- Do not place real patient data in this repository.
- Report "not measured" where labels or review are unavailable.
