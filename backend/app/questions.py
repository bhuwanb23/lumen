"""Curated English appointment-question templates; no model-generated questions are exposed."""

from app.schemas import ApprovedQuestion, ExtractedFact

_FIELD_LABELS = {
    "report_type": "type of report",
    "primary_site": "site named in the report",
    "cancer_type": "cancer type named in the report",
    "histology": "histology wording",
    "grade": "grade wording",
    "stage": "stage wording",
    "margins": "margin wording",
    "lymph_nodes": "lymph-node wording",
    "lymphovascular_invasion": "lymphovascular-invasion wording",
    "biomarkers": "biomarker results",
    "molecular_test_status": "molecular-testing note",
    "distant_metastasis": "spread wording",
    "tumor_size": "tumor-size entry",
    "other_findings": "this finding",
}
_PRIORITY = [
    "grade",
    "stage",
    "margins",
    "lymph_nodes",
    "biomarkers",
    "molecular_test_status",
    "distant_metastasis",
    "lymphovascular_invasion",
    "histology",
    "primary_site",
    "cancer_type",
    "tumor_size",
    "other_findings",
    "report_type",
]


def build_care_team_questions(facts: list[ExtractedFact], limit: int = 5) -> list[ApprovedQuestion]:
    """Create neutral, reviewed questions only from facts with verified source evidence."""
    by_field = {
        fact.field: fact
        for fact in facts
        if fact.status in {"stated", "unclear"} and fact.evidence is not None
    }
    ordered = sorted(
        by_field.values(),
        key=lambda fact: (fact.status != "unclear", _PRIORITY.index(fact.field)),
    )
    questions: list[ApprovedQuestion] = []
    for fact in ordered[:limit]:
        label = _FIELD_LABELS[fact.field]
        if fact.status == "unclear":
            text = f"Could you clarify the conflicting {label} in this report?"
        else:
            text = f"Could you explain what the report's {label} line means?"
        questions.append(
            ApprovedQuestion(
                question_id=f"question_{fact.field}",
                text=text,
                cited_fact_ids=[fact.fact_id],
                review_status="approved",
            )
        )
    return questions
