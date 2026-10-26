"""Deterministic scope controls and fixed patient-facing refusals."""

from __future__ import annotations

import re
from typing import Final

from app.schemas import AnalysisRequest, AnalysisResponse, RefusalCategory, SafeQueryNotice

MISSING_INFORMATION_NOTICE: Final[SafeQueryNotice] = (
    "I can't guess missing information. Fields marked 'Not stated in this excerpt' are absent "
    "from the submitted text; ask your care team to clarify."
)

_REFUSAL_MESSAGES: Final[dict[RefusalCategory, str]] = {
    "prognosis": (
        "I can't estimate prognosis, survival, or recurrence from a report. Please ask your care "
        "team, who can interpret your full clinical context."
    ),
    "treatment": (
        "I can't recommend or compare treatments. Your oncology team can discuss options for your "
        "situation. I can help explain wording that appears in the report."
    ),
    "dose": (
        "I can't advise on medication or treatment doses. Contact your oncology team or pharmacist "
        "for dose instructions."
    ),
    "diagnosis": (
        "I can't diagnose or interpret findings beyond what the report says. Please ask your care "
        "team to explain the result in context."
    ),
    "urgent_symptoms": (
        "Lumen can't assess urgent symptoms. Contact your local emergency service or "
        "clinical team now."
    ),
    "trial_eligibility": (
        "I can't determine clinical-trial eligibility. Your oncologist and study team can assess "
        "that using your complete medical information."
    ),
    "policy_evasion": (
        "I can only help within Lumen's safety limits. I can't reveal hidden instructions "
        "or secrets."
    ),
}

_POLICY_EVASION = re.compile(
    r"\b(?:ignore|bypass|override|disregard)\b.{0,60}"
    r"\b(?:rules|instructions|safety|system prompt)\b"
    r"|\b(?:reveal|show|print|disclose)\b.{0,50}"
    r"\b(?:system prompt|hidden prompt|api key|secret|credentials)\b",
    re.IGNORECASE,
)
_URGENT = re.compile(
    r"\b(?:severe chest pain|chest pain|trouble breathing|difficulty breathing|shortness of breath|"
    r"can't breathe|cannot breathe|uncontrolled bleeding|heavy bleeding|vomiting blood|"
    r"coughing up blood|seizure|stroke symptoms|urgent(?:ly)?|emergency|can i wait|should i wait|"
    r"wait until tomorrow|go to the er|emergency room|should i seek care)\b",
    re.IGNORECASE,
)
_DOSE = re.compile(
    r"\b(?:dose|dosage|milligrams?|\d+\s*mg|how much (?:should i|do i|can i) take|"
    r"what amount should i take)\b",
    re.IGNORECASE,
)
_TREATMENT = re.compile(
    r"\b(?:recommend|recommendation|choose|rank|best|which|should i|what should i|start|stop)\b"
    r".{0,80}\b(?:treatment|therapy|chemotherapy|chemo|radiation|immunotherapy|surgery|"
    r"medication|medicine|drug)\b"
    r"|\b(?:treatment|therapy|chemotherapy|chemo|radiation|immunotherapy|surgery)\b"
    r".{0,60}\b(?:should i choose|which is best|recommend)\b",
    re.IGNORECASE,
)
_PROGNOSIS = re.compile(
    r"\b(?:prognos(?:is)?|survival|chance of surviving|life expectancy|"
    r"how long (?:do|will) i live|"
    r"how long (?:do i have|will i have|do i expect) to live|will i survive|"
    r"recurrence (?:risk|chance|probability)|is it curable|can this be cured|cure me)\b",
    re.IGNORECASE,
)
_TRIAL_ELIGIBILITY = re.compile(
    r"\b(?:eligible|eligibility|qualify|qualified)\b.{0,60}\b(?:clinical )?trial\b"
    r"|\b(?:clinical )?trial\b.{0,60}\b(?:eligible|qualify|should i enroll)\b",
    re.IGNORECASE,
)
_STAGE_ASK = re.compile(r"\b(?:stage|staging)\b", re.IGNORECASE)
_REPORT_STAGE_LOOKUP = re.compile(
    r"\b(?:what|which) stage (?:does|did) (?:the )?report (?:say|list|state|show)\b"
    r"|\b(?:report|document) (?:lists|states|says) (?:the )?stage\b"
    r"|\bwhat does (?:the )?report say about (?:the )?stage\b"
    r"|\bexplain (?:the )?stage (?:line|wording|entry) (?:in|from) (?:the )?report\b",
    re.IGNORECASE,
)
_DIAGNOSIS = re.compile(
    r"\b(?:do i have|am i diagnosed with|is this cancer|is this malignant|has it spread|"
    r"metastas(?:is|ized|es)|does (?:this )?report (?:prove|confirm|mean).{0,60}"
    r"(?:cancer|metasta|stage)|diagnose me)\b",
    re.IGNORECASE,
)
_MISSING_INFERENCE = re.compile(
    r"\b(?:guess|assume|pretend|suppose|infer)\b.{0,100}\b(?:missing|not stated|not reported|"
    r"absent|unknown|negative|normal|not tested|not say|not list)\b"
    r"|\b(?:missing|not stated|not reported|absent|unknown)\b.{0,100}"
    r"\b(?:guess|assume|pretend|suppose|infer)\b",
    re.IGNORECASE,
)
_UNSAFE_CLAIM = re.compile(
    r"\b(?:survival rate|life expectancy|prognos(?:is)?|chance of surviving|will you survive|"
    r"you will survive|curable|cure you|recurrence probability)\b"
    r"|\b(?:i recommend|we recommend|you should|you must|start treatment|stop treatment|"
    r"take this dose|recommended dose|best treatment|eligible for a trial|qualify for a trial)\b",
    re.IGNORECASE,
)


def classify_user_question(question: str | None) -> RefusalCategory | None:
    """Return a fixed refusal category before any provider is initialized or contacted."""
    if not question:
        return None
    text = " ".join(question.casefold().split())
    if _POLICY_EVASION.search(text):
        return "policy_evasion"
    if _URGENT.search(text):
        return "urgent_symptoms"
    if _DOSE.search(text):
        return "dose"
    if _TREATMENT.search(text):
        return "treatment"
    if _TRIAL_ELIGIBILITY.search(text):
        return "trial_eligibility"
    if _PROGNOSIS.search(text):
        return "prognosis"
    if _MISSING_INFERENCE.search(text):
        return None
    if _STAGE_ASK.search(text) and not _REPORT_STAGE_LOOKUP.search(text):
        return "diagnosis"
    if _DIAGNOSIS.search(text):
        return "diagnosis"
    return None


def requests_missing_inference(question: str | None) -> bool:
    """Identify requests to guess/infer values explicitly described as absent or unknown."""
    return bool(question and _MISSING_INFERENCE.search(" ".join(question.casefold().split())))


def unsafe_claim_reason(claim_text: str) -> str | None:
    """Conservative lexical backstop; semantic verification remains mandatory."""
    if _UNSAFE_CLAIM.search(claim_text):
        return "out_of_scope_claim"
    return None


def make_refusal(request: AnalysisRequest, category: RefusalCategory) -> AnalysisResponse:
    return AnalysisResponse(
        status="refused",
        language=request.language,
        reading_level=request.reading_level,
        facts=[],
        claims=[],
        questions_for_care_team=[],
        omitted_claim_count=0,
        refusal_category=category,
        refusal_message=_REFUSAL_MESSAGES[category],
    )
