# Phase 1 — Synthetic reports, answer keys and contracts

**Window:** 25 Oct 2026, H2–H3 · **Status:** Planned · **Depends on:** Phase 0.

## Objective
Define the evidence contract and benchmark before connecting a model.

## Work breakdown
1. **Choose narrow coverage (15 min):** 1–2 report genres and at most 2–3 cancer contexts; synthetic only. Add a missing-field, ambiguous/contradictory and adversarial-document case.
2. **Write fixtures/key (30–45 min):** report text; gold fields; exact evidence quote + offsets; stated/not-stated/unclear; expected claim limits; ambiguity notes; forbidden inference. Each fixture clearly marked synthetic and checked for accidental identifiers.
3. **Design schemas (20 min):** strict request (text, approved language, reading level); fact (stable ID, allowlisted field, value, status, quote, offsets); claim (text, cited fact IDs/quotes, verifier state); response (supported claims, neutral questions, disclaimer, omitted count/status). Reject unknown fields/oversize input.
4. **Safety suite (15 min):** embedded instruction, prognosis, treatment/dose, beyond-report diagnosis, urgent symptoms, eligibility, benign controls; expected behavior defined before test.

## Deliverables
Versioned fixtures/answer keys, Pydantic/JSON contract, prompt/scope tests, metric/annotation definitions.

## Acceptance
- [ ] Every stated gold fact has exact quote and valid offset.
- [ ] Missing is not negative; unclear is distinct from absent.
- [ ] Unicode and line-ending rules documented.
- [ ] All fixtures synthetic; schema strict.
- [ ] Adversarial plus benign controls included.

## Gate
A reviewer can apply the gold labels without guessing what support means. Resolve or explicitly mark ambiguous keys before Phase 2; do not let model output define its own ground truth.
