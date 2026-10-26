import pytest
from pydantic import ValidationError

from app.schemas import QuestionCandidate


def test_question_contract_requires_question_form_and_citations() -> None:
    valid = QuestionCandidate(
        question_id="question_grade",
        text="Could you explain what the grade line means?",
        cited_fact_ids=["fact_grade"],
    )
    assert valid.review_status == "pending"
    with pytest.raises(ValidationError):
        QuestionCandidate(
            question_id="question_grade",
            text="The grade means this.",
            cited_fact_ids=["fact_grade"],
        )
    with pytest.raises(ValidationError):
        QuestionCandidate(
            question_id="question_grade",
            text="Could you explain the grade?",
            cited_fact_ids=[],
        )
    with pytest.raises(ValidationError):
        QuestionCandidate(
            question_id="question_grade",
            text="Could you explain the grade?",
            cited_fact_ids=["fact_grade", "fact_grade"],
        )
