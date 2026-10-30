# Clinical review checklist

## Reviewer requirements

- [ ] Reviewer is a qualified clinician or supervised reviewer with relevant oncology/pathology familiarity.
- [ ] Reviewer independence and date are recorded.
- [ ] Synthetic-only scope is understood; no real patient data is used.

## Fact review

- [ ] Each stated fact is supported by its exact source quote.
- [ ] Each not_stated field is genuinely absent from the excerpt.
- [ ] Each unclear field preserves ambiguity without resolving it.
- [ ] No missing field is treated as negative/normal.
- [ ] Exact quote and code-point offsets are verified.

## Claim review

- [ ] Every claim is labeled entailed, partially_supported, unsupported, contradicted, or not_assessable.
- [ ] Every material number, polarity, qualifier, and relationship is checked.
- [ ] Claims cite every fact needed for their content.
- [ ] No diagnostic, prognostic, treatment, dosing, or eligibility claim is accepted.

## Question review

- [ ] Questions are neutral and do not embed treatment advice.
- [ ] Questions do not imply prognosis or eligibility.
- [ ] Questions cite at least one stated fact.

## Reporting

- [ ] Report N, reviewer count, disagreement, and adjudication method.
- [ ] Report before/after verifier metrics separately.
- [ ] Preserve model/prompt/provider provenance.
