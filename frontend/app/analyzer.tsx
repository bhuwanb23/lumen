"use client";

import { useState, type FormEvent } from "react";

type EvidenceSpan = { quote: string; start: number; end: number };
type Citation = { fact_id: string; evidence: EvidenceSpan };
type Claim = {
  claim_id: string;
  text: string;
  citations: Citation[];
  verification: "supported";
};
type Fact = {
  fact_id: string;
  field: string;
  value: string | null;
  status: "stated" | "not_stated" | "unclear";
  evidence: EvidenceSpan | null;
};
type Question = {
  question_id: string;
  text: string;
  cited_fact_ids: string[];
  review_status: "approved";
};
type AnalysisResult = {
  status: "complete" | "no_supported_claims" | "refused";
  language: "en";
  reading_level: "simple" | "standard" | "detailed";
  disclaimer: string;
  facts: Fact[];
  claims: Claim[];
  questions_for_care_team: Question[];
  omitted_claim_count: number;
  query_notice: string | null;
  refusal_category: string | null;
  refusal_message: string | null;
};

const DISCLAIMER =
  "Lumen explains report wording; it is not medical advice. It does not diagnose, predict outcomes, or recommend treatment. Confirm meaning with your care team.";
const MISSING_INFORMATION_NOTICE =
  "I can't guess missing information. Fields marked 'Not stated in this excerpt' are absent from the submitted text; ask your care team to clarify.";
const FIXED_REFUSALS: Record<string, string> = {
  prognosis: "I can't estimate prognosis, survival, or recurrence from a report. Please ask your care team, who can interpret your full clinical context.",
  treatment: "I can't recommend or compare treatments. Your oncology team can discuss options for your situation. I can help explain wording that appears in the report.",
  dose: "I can't advise on medication or treatment doses. Contact your oncology team or pharmacist for dose instructions.",
  diagnosis: "I can't diagnose or interpret findings beyond what the report says. Please ask your care team to explain the result in context.",
  urgent_symptoms: "Lumen can't assess urgent symptoms. Contact your local emergency service or clinical team now.",
  trial_eligibility: "I can't determine clinical-trial eligibility. Your oncologist and study team can assess that using your complete medical information.",
  policy_evasion: "I can only help within Lumen's safety limits. I can't reveal hidden instructions or secrets.",
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isEvidenceSpan(value: unknown): value is EvidenceSpan {
  return isRecord(value)
    && typeof value.quote === "string"
    && value.quote.length > 0
    && Number.isInteger(value.start)
    && Number.isInteger(value.end)
    && Number(value.start) >= 0
    && Number(value.end) > Number(value.start);
}

function isFact(value: unknown): value is Fact {
  return isRecord(value)
    && typeof value.fact_id === "string"
    && typeof value.field === "string"
    && (typeof value.value === "string" || value.value === null)
    && ["stated", "not_stated", "unclear"].includes(String(value.status))
    && (value.evidence === null || isEvidenceSpan(value.evidence))
    && (value.status !== "not_stated" || (value.value === null && value.evidence === null))
    && (value.status === "not_stated" || (typeof value.value === "string" && isEvidenceSpan(value.evidence)));
}

function isCitation(value: unknown): value is Citation {
  return isRecord(value)
    && typeof value.fact_id === "string"
    && isEvidenceSpan(value.evidence);
}

function isClaim(value: unknown): value is Claim {
  return isRecord(value)
    && typeof value.claim_id === "string"
    && typeof value.text === "string"
    && value.text.length > 0
    && value.verification === "supported"
    && Array.isArray(value.citations)
    && value.citations.length > 0
    && value.citations.every(isCitation);
}

function isQuestion(value: unknown): value is Question {
  return isRecord(value)
    && typeof value.question_id === "string"
    && typeof value.text === "string"
    && value.text.endsWith("?")
    && value.review_status === "approved"
    && Array.isArray(value.cited_fact_ids)
    && value.cited_fact_ids.length > 0
    && value.cited_fact_ids.every((id) => typeof id === "string");
}

function spanMatchesSource(span: EvidenceSpan, sourceCodepoints: string[]): boolean {
  return span.end <= sourceCodepoints.length
    && sourceCodepoints.slice(span.start, span.end).join("") === span.quote;
}

/** Fail closed if the API response is malformed, unverified, or detached from the submitted source. */
function isAnalysisResult(value: unknown, sourceText: string): value is AnalysisResult {
  if (!isRecord(value)) return false;
  if (!["complete", "no_supported_claims", "refused"].includes(String(value.status))) return false;
  if (value.language !== "en" || !["simple", "standard", "detailed"].includes(String(value.reading_level))) return false;
  if (value.disclaimer !== DISCLAIMER) return false;
  if (!Array.isArray(value.facts) || !value.facts.every(isFact)) return false;
  if (!Array.isArray(value.claims) || !value.claims.every(isClaim)) return false;
  if (!Array.isArray(value.questions_for_care_team) || !value.questions_for_care_team.every(isQuestion)) return false;
  if (!Number.isInteger(value.omitted_claim_count) || Number(value.omitted_claim_count) < 0) return false;
  if (!(value.query_notice === null || value.query_notice === MISSING_INFORMATION_NOTICE)) return false;
  if (!(value.refusal_category === null || typeof value.refusal_category === "string")) return false;
  if (!(value.refusal_message === null || typeof value.refusal_message === "string")) return false;

  if (value.status === "complete" && value.claims.length === 0) return false;
  if (value.status === "no_supported_claims" && value.claims.length !== 0) return false;
  if (value.status === "refused") {
    const refusalCategory = value.refusal_category;
    return typeof refusalCategory === "string"
      && Object.hasOwn(FIXED_REFUSALS, refusalCategory)
      && value.refusal_message === FIXED_REFUSALS[refusalCategory]
      && value.facts.length === 0
      && value.claims.length === 0
      && value.questions_for_care_team.length === 0
      && value.omitted_claim_count === 0
      && value.query_notice === null;
  }
  if (value.refusal_category !== null || value.refusal_message !== null) return false;

  const sourceCodepoints = Array.from(sourceText);
  const facts = value.facts as Fact[];
  const factIds = new Set(facts.map((fact) => fact.fact_id));
  if (factIds.size !== facts.length) return false;
  for (const fact of facts) {
    if (fact.evidence && !spanMatchesSource(fact.evidence, sourceCodepoints)) return false;
  }

  const claimIds = new Set((value.claims as Claim[]).map((claim) => claim.claim_id));
  if (claimIds.size !== value.claims.length) return false;
  for (const claim of value.claims as Claim[]) {
    for (const citation of claim.citations) {
      const fact = facts.find((candidate) => candidate.fact_id === citation.fact_id);
      if (!fact || fact.status === "not_stated" || !fact.evidence) return false;
      if (
        citation.evidence.quote !== fact.evidence.quote
        || citation.evidence.start !== fact.evidence.start
        || citation.evidence.end !== fact.evidence.end
        || !spanMatchesSource(citation.evidence, sourceCodepoints)
      ) return false;
    }
  }
  const questionIds = new Set((value.questions_for_care_team as Question[]).map((question) => question.question_id));
  if (questionIds.size !== value.questions_for_care_team.length) return false;
  for (const question of value.questions_for_care_team as Question[]) {
    if (question.cited_fact_ids.some((id) => !factIds.has(id))) return false;
    if (question.cited_fact_ids.some((id) => {
      const fact = facts.find((candidate) => candidate.fact_id === id);
      return !fact || fact.status === "not_stated" || fact.evidence === null;
    })) return false;
  }
  return true;
}

function fieldLabel(field: string): string {
  return field.replaceAll("_", " ");
}

export default function Analyzer() {
  const [reportText, setReportText] = useState("");
  const [question, setQuestion] = useState("");
  const [readingLevel, setReadingLevel] = useState<"simple" | "standard" | "detailed">("simple");
  const [syntheticConfirmed, setSyntheticConfirmed] = useState(false);
  const [processingConfirmed, setProcessingConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [openSources, setOpenSources] = useState<Record<string, boolean>>({});

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setOpenSources({});
    setBusy(true);
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({
          report_text: reportText,
          ...(question.trim() ? { user_question: question.trim() } : {}),
          language: "en",
          reading_level: readingLevel,
          data_is_synthetic_or_deidentified: syntheticConfirmed,
          external_processing_acknowledged: processingConfirmed,
        }),
      });
      const payload: unknown = await response.json();
      if (!response.ok) {
        const detail = isRecord(payload) && typeof payload.detail === "string"
          ? payload.detail
          : "Analysis is unavailable. No generated claims were returned.";
        setError(detail);
      } else if (!isAnalysisResult(payload, reportText)) {
        setError("The service returned a result that could not be safely verified. No claims are displayed.");
      } else {
        setResult(payload);
      }
    } catch {
      setError("Analysis is unavailable or timed out. No generated claims were returned. Please try again later or review the report with your care team.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mt-10 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8" aria-labelledby="analyzer-heading">
      <h2 id="analyzer-heading" className="text-2xl font-semibold">Explain a report excerpt</h2>
      <p className="mt-2 text-slate-700">Text only, English only. Lumen returns source-linked statements that pass two verification steps; it may return no claims.</p>

      <div className="mt-5 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950" aria-label="Before you continue">
        <strong>Prototype safety:</strong> Use synthetic or de-identified text only; do not submit real patient information, names, dates of birth, record numbers, or contact details. When analysis is enabled, the text is sent to the service operator&apos;s configured model provider, which may be an external service. Check your deployment&apos;s provider and privacy terms before continuing. This is not medical advice; confirm report meaning with your care team.
      </div>

      <form className="mt-6 space-y-5" onSubmit={submit} aria-busy={busy}>
        <fieldset disabled={busy} className="space-y-5 disabled:opacity-80">
          <div>
            <label htmlFor="report-text" className="block font-semibold">Report excerpt</label>
            <textarea
              id="report-text"
              name="report_text"
              required
              minLength={20}
              maxLength={50_000}
              rows={10}
              value={reportText}
              onChange={(event) => setReportText(event.target.value)}
              aria-describedby="report-help report-count"
              className="mt-2 min-h-48 w-full resize-y rounded-xl border border-slate-400 bg-white p-3 font-mono text-base leading-6 sm:text-sm"
              placeholder="Paste a synthetic or de-identified report excerpt here."
            />
            <p id="report-help" className="mt-1 text-sm text-slate-600">Paste report text only. Do not include identifiers. Minimum 20 characters.</p>
            <p id="report-count" className="text-sm text-slate-600" aria-live="polite" aria-atomic="true">
              {reportText.length.toLocaleString()} / 50,000 characters · Text is not stored by this prototype.
            </p>
          </div>

          <div>
            <label htmlFor="user-question" className="block font-semibold">What wording would you like explained? <span className="font-normal text-slate-600">(optional)</span></label>
            <input
              id="user-question"
              type="text"
              maxLength={500}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              aria-describedby="question-help"
              className="mt-2 min-h-12 w-full rounded-xl border border-slate-400 bg-white p-3 text-base"
              placeholder="For example: What does the grade line say?"
            />
            <p id="question-help" className="mt-1 text-sm text-slate-600">Lumen cannot answer diagnosis, prognosis, treatment, dose, trial eligibility, or urgent symptom questions.</p>
          </div>

          <div>
            <label htmlFor="reading-level" className="block font-semibold">Reading style</label>
            <select id="reading-level" value={readingLevel} onChange={(event) => setReadingLevel(event.target.value as typeof readingLevel)} className="mt-2 min-h-12 rounded-xl border border-slate-400 bg-white p-3 text-base">
              <option value="simple">Simple</option>
              <option value="standard">Standard</option>
              <option value="detailed">Detailed</option>
            </select>
          </div>

          <div className="space-y-3 rounded-xl bg-slate-50 p-4">
            <label className="flex min-h-11 cursor-pointer items-start gap-3 py-2">
              <input type="checkbox" required checked={syntheticConfirmed} onChange={(event) => setSyntheticConfirmed(event.target.checked)} className="mt-1 h-5 w-5 shrink-0 accent-emerald-800" />
              <span>I confirm this excerpt is synthetic or properly de-identified and contains no direct identifiers.</span>
            </label>
            <label className="flex min-h-11 cursor-pointer items-start gap-3 py-2">
              <input type="checkbox" required checked={processingConfirmed} onChange={(event) => setProcessingConfirmed(event.target.checked)} className="mt-1 h-5 w-5 shrink-0 accent-emerald-800" />
              <span>I understand the service operator&apos;s configured model provider will process the excerpt, potentially outside my device.</span>
            </label>
          </div>
        </fieldset>

        <button type="submit" disabled={busy || !syntheticConfirmed || !processingConfirmed} className="min-h-12 rounded-xl bg-emerald-900 px-5 py-3 font-semibold text-white hover:bg-emerald-800 focus-visible:outline-offset-4 disabled:cursor-not-allowed disabled:opacity-50">
          {busy ? "Verifying report…" : "Explain excerpt"}
        </button>
        {!syntheticConfirmed || !processingConfirmed ? <p className="text-sm text-slate-600">Confirm both statements above to enable analysis.</p> : null}
      </form>

      {busy && <p className="mt-5 rounded-xl bg-slate-50 p-4 text-slate-800" role="status" aria-live="polite">The excerpt is being checked. This may take a little time. Please keep this page open.</p>}
      {error && <p className="mt-6 rounded-xl border border-rose-300 bg-rose-50 p-4 text-rose-950" role="alert">{error}</p>}

      {result && <section className="mt-8 border-t border-slate-200 pt-6" aria-labelledby="result-heading" aria-live="polite">
        <h3 id="result-heading" className="text-xl font-semibold">Result</h3>
        <p className="mt-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-950">{result.disclaimer}</p>
        {result.query_notice && <p className="mt-4 rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-950">{result.query_notice}</p>}

        {result.status === "refused" ? (
          <p className="mt-4 rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-950" role="status">{result.refusal_message}</p>
        ) : result.status === "no_supported_claims" ? (
          <p className="mt-4 rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-950" role="status">
            No explanation statements passed the source and safety checks. Please review the original report with your care team.
            {result.omitted_claim_count > 0 ? ` ${result.omitted_claim_count} proposed statement(s) were omitted.` : ""}
          </p>
        ) : (
          <>
            <h4 className="mt-5 font-semibold">What the report says</h4>
            <ul className="mt-3 space-y-4">
              {result.claims.map((claim) => <li key={claim.claim_id} className="rounded-xl border border-slate-200 p-4">
                <p>{claim.text}</p>
                <div className="mt-4 space-y-3">
                  {claim.citations.map((citation, citationIndex) => {
                    const sourceKey = `${claim.claim_id}-${citation.fact_id}-${citationIndex}`;
                    const sourceId = `source-${sourceKey}`;
                    const buttonId = `source-button-${sourceKey}`;
                    const expanded = Boolean(openSources[sourceKey]);
                    return <div key={sourceKey}>
                      <button
                        id={buttonId}
                        type="button"
                        aria-expanded={expanded}
                        aria-controls={sourceId}
                        aria-label={`${expanded ? "Hide" : "View"} source ${citationIndex + 1} for ${fieldLabel(citation.fact_id.replace(/^fact_/, ""))}`}
                        onClick={() => setOpenSources((current) => ({ ...current, [sourceKey]: !current[sourceKey] }))}
                        className="min-h-11 rounded-lg border border-emerald-800 px-3 py-2 text-sm font-semibold text-emerald-950 hover:bg-emerald-50"
                      >
                        {expanded ? "Hide source" : "View source"} <span className="font-normal">({citationIndex + 1} of {claim.citations.length})</span>
                      </button>
                      <blockquote
                        id={sourceId}
                        role="region"
                        aria-labelledby={buttonId}
                        hidden={!expanded}
                        className="mt-3 rounded-lg border-l-4 border-emerald-700 bg-emerald-50 p-4 text-sm text-slate-800"
                      >
                        <p className="mb-2 font-semibold">Exact wording from the submitted excerpt · {citation.fact_id}</p>
                        <q>{citation.evidence.quote}</q>
                      </blockquote>
                    </div>;
                  })}
                </div>
              </li>)}
            </ul>
          </>
        )}

        {result.status !== "refused" && result.questions_for_care_team.length > 0 && <div className="mt-6 rounded-xl bg-slate-50 p-4">
          <h4 className="font-semibold">Questions you could ask your care team</h4>
          <ul className="mt-2 list-disc space-y-2 pl-6">
            {result.questions_for_care_team.map((item) => <li key={item.question_id}>{item.text}</li>)}
          </ul>
        </div>}

        {result.status !== "refused" && <details className="mt-6 rounded-xl bg-slate-50 p-4">
          <summary className="min-h-11 cursor-pointer py-2 font-semibold">Extracted report fields and exact evidence</summary>
          <ul className="mt-3 space-y-3">
            {result.facts.map((fact) => <li key={fact.fact_id} className="border-t border-slate-200 pt-3">
              <span className="font-semibold capitalize">{fieldLabel(fact.field)}:</span> {fact.status === "not_stated" ? "Not stated in this excerpt" : fact.status === "unclear" ? "Unclear in this excerpt" : fact.value}
              {fact.evidence && <blockquote className="mt-1 border-l-2 border-slate-400 pl-3 text-sm text-slate-700"><q>{fact.evidence.quote}</q></blockquote>}
            </li>)}
          </ul>
        </details>}

        <p className="mt-6 text-sm text-slate-600">
          {result.status === "refused"
            ? "No report interpretation was produced for this request."
            : result.status === "no_supported_claims"
              ? "No claim was displayed. Confirm the report with your care team."
              : result.omitted_claim_count > 0
                ? `${result.omitted_claim_count} proposed statement(s) were omitted by verification. Only verified statements are shown.`
                : "Only statements that passed source and safety checks are shown."}
          {" "}Confirm all meanings with your care team.
        </p>
      </section>}
    </section>
  );
}
