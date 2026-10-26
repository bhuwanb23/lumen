/* UI-only synthetic fixture; not a clinical answer key or model-quality result. */
export const SYNTHETIC_REPORT =
  "Lung, right upper lobe, biopsy: Adenocarcinoma, acinar pattern.\n" +
  "PD-L1 tumor proportion score: 15%.\n" +
  "EGFR mutation testing: Not performed on this specimen.";

function span(quote: string) {
  const utf16Start = SYNTHETIC_REPORT.indexOf(quote);
  if (utf16Start < 0) throw new Error("Fixture evidence must occur in the synthetic report.");
  const start = Array.from(SYNTHETIC_REPORT.slice(0, utf16Start)).length;
  const length = Array.from(quote).length;
  return { quote, start, end: start + length };
}

const histologyEvidence = span("Adenocarcinoma, acinar pattern");
const biomarkerEvidence = span("PD-L1 tumor proportion score: 15%");
const molecularEvidence = span("EGFR mutation testing: Not performed on this specimen.");

export const HAPPY_RESULT = {
  status: "complete",
  language: "en",
  reading_level: "simple",
  disclaimer:
    "Lumen explains report wording; it is not medical advice. It does not diagnose, predict outcomes, or recommend treatment. Confirm meaning with your care team.",
  facts: [
    {
      fact_id: "fact_histology",
      field: "histology",
      value: "Adenocarcinoma, acinar pattern",
      status: "stated",
      evidence: histologyEvidence,
    },
    {
      fact_id: "fact_biomarkers",
      field: "biomarkers",
      value: "PD-L1 tumor proportion score: 15%",
      status: "stated",
      evidence: biomarkerEvidence,
    },
    {
      fact_id: "fact_molecular_test_status",
      field: "molecular_test_status",
      value: "Not performed on this specimen",
      status: "stated",
      evidence: molecularEvidence,
    },
    {
      fact_id: "fact_stage",
      field: "stage",
      value: null,
      status: "not_stated",
      evidence: null,
    },
  ],
  claims: [
    {
      claim_id: "claim_01",
      text: "The report names adenocarcinoma with an acinar pattern and lists a PD-L1 tumor proportion score of 15%.",
      citations: [
        { fact_id: "fact_histology", evidence: histologyEvidence },
        { fact_id: "fact_biomarkers", evidence: biomarkerEvidence },
      ],
      verification: "supported",
    },
    {
      claim_id: "claim_02",
      text: "The report says EGFR mutation testing was not performed on this specimen.",
      citations: [{ fact_id: "fact_molecular_test_status", evidence: molecularEvidence }],
      verification: "supported",
    },
  ],
  questions_for_care_team: [
    {
      question_id: "question_biomarkers",
      text: "Could you explain what the report's biomarker results line means?",
      cited_fact_ids: ["fact_biomarkers"],
      review_status: "approved",
    },
  ],
  omitted_claim_count: 0,
  query_notice: null,
  refusal_category: null,
  refusal_message: null,
} as const;

export const NO_CLAIMS_RESULT = {
  ...HAPPY_RESULT,
  status: "no_supported_claims",
  claims: [],
  omitted_claim_count: 2,
};

export const REJECTED_CLAIM_RESULT = {
  ...HAPPY_RESULT,
  omitted_claim_count: 1,
};

export const FIXED_REFUSAL_RESULT = {
  status: "refused",
  language: "en",
  reading_level: "simple",
  disclaimer: HAPPY_RESULT.disclaimer,
  facts: [],
  claims: [],
  questions_for_care_team: [],
  omitted_claim_count: 0,
  query_notice: null,
  refusal_category: "prognosis",
  refusal_message:
    "I can't estimate prognosis, survival, or recurrence from a report. Please ask your care team, who can interpret your full clinical context.",
};
