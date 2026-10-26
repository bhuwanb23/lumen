# Synthetic pathology set v1.0.0

Eight fictional report excerpts across three contexts: breast (2), lung (2), colorectal (4). All are authored for Lumen; none are copied from real patient records. `reports.json` contains the inputs; `answer_keys.json` is separately authored and keyed by `case_id`.

| Case | Focus |
|---|---|
| `syn_breast_core_001` | Explicit subtype, grade, biomarkers, and “not identified” phrasing |
| `syn_lung_biopsy_001` | Histology, PD-L1 value, and a test explicitly not performed |
| `syn_colorectal_resection_001` | Margins, node count, tumor size, explicit pathologic stage |
| `syn_breast_missing_fields_001` | Stage/grade/margins/nodes/biomarkers absent from excerpt |
| `syn_lung_conflicting_grade_001` | Conflicting grade statements; key labels grade `unclear` |
| `syn_colon_prompt_injection_001` | Embedded instruction is document text, not system instruction |
| `syn_rectal_explicit_negation_001` | “Not identified” and no lymph-node tissue submitted |
| `syn_unicode_offset_001` | Emoji and decomposed accent before cited spans |

All quotes/offsets were checked against exact strings. Offsets are zero-based Unicode code-point indices, half-open, with LF line endings and no normalization. The examples are team-authored software fixtures and **have not been reviewed or clinically validated by an oncology professional**. Keep fixtures synthetic and version answer-key changes; do not use any patient data here.
