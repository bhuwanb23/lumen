"use client";

import { FormEvent, useState } from "react";

type Citation = { fact_id: string; evidence: { quote: string; start: number; end: number } };
type Claim = { claim_id: string; text: string; citations: Citation[]; verification: "supported" };
type Fact = {
  fact_id: string;
  field: string;
  value: string | null;
  status: "stated" | "not_stated" | "unclear";
  evidence: { quote: string; start: number; end: number } | null;
};
type Question = { question_id: string; text: string; cited_fact_ids: string[]; review_status: "approved" };
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

function isAnalysisResult(value: unknown): value is AnalysisResult {
  if (typeof value !== "object" || value === null) return false;
  const data = value as Record<string, unknown>;
  return ["complete", "no_supported_claims", "refused"].includes(String(data.status))
    && Array.isArray(data.facts)
    && Array.isArray(data.claims)
    && Array.isArray(data.questions_for_care_team)
    && typeof data.disclaimer === "string";
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

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);
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
        const detail = typeof payload === "object" && payload !== null && "detail" in payload
          ? String((payload as { detail: unknown }).detail)
          : "Analysis is unavailable. No generated claims were returned.";
        setError(detail);
      } else if (!isAnalysisResult(payload)) {
        setError("The service returned an invalid response. No claims are displayed.");
      } else {
        setResult(payload);
      }
    } catch {
      setError("Analysis is unavailable. No generated claims were returned.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mt-10 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8" aria-labelledby="analyzer-heading">
      <h2 id="analyzer-heading" className="text-2xl font-semibold">Explain a report excerpt</h2>
      <p className="mt-2 text-slate-700">Text only, English only. Lumen returns source-linked statements that pass two verification steps; it may return no claims.</p>

      <div className="mt-5 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-950">
        <strong>Prototype safety:</strong> Use synthetic or de-identified text only; do not submit real patient information, names, dates of birth, record numbers, or contact details. The text is sent to the service operator&apos;s configured model provider, which may be an external service. Check your deployment&apos;s provider and privacy terms before continuing. This is not medical advice; confirm report meaning with your care team.
      </div>

      <form className="mt-6 space-y-5" onSubmit={submit}>
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
            className="mt-2 w-full rounded-xl border border-slate-400 bg-white p-3 font-mono text-sm leading-6"
            placeholder="Paste a synthetic or de-identified report excerpt here."
          />
          <p className="mt-1 text-sm text-slate-600">{reportText.length.toLocaleString()} / 50,000 characters · Text is not stored by this prototype.</p>
        </div>

        <div>
          <label htmlFor="user-question" className="block font-semibold">What wording would you like explained? <span className="font-normal text-slate-600">(optional)</span></label>
          <input
            id="user-question"
            type="text"
            maxLength={500}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            className="mt-2 w-full rounded-xl border border-slate-400 bg-white p-3"
            placeholder="For example: What does the grade line say?"
          />
          <p className="mt-1 text-sm text-slate-600">Lumen cannot answer diagnosis, prognosis, treatment, dose, trial eligibility, or urgent symptom questions.</p>
        </div>

        <div>
          <label htmlFor="reading-level" className="block font-semibold">Reading style</label>
          <select id="reading-level" value={readingLevel} onChange={(event) => setReadingLevel(event.target.value as typeof readingLevel)} className="mt-2 rounded-xl border border-slate-400 bg-white p-3">
            <option value="simple">Simple</option>
            <option value="standard">Standard</option>
            <option value="detailed">Detailed</option>
          </select>
        </div>

        <div className="space-y-3 rounded-xl bg-slate-50 p-4">
          <label className="flex items-start gap-3">
            <input type="checkbox" required checked={syntheticConfirmed} onChange={(event) => setSyntheticConfirmed(event.target.checked)} className="mt-1 h-5 w-5 accent-emerald-800" />
            <span>I confirm this excerpt is synthetic or properly de-identified and contains no direct identifiers.</span>
          </label>
          <label className="flex items-start gap-3">
            <input type="checkbox" required checked={processingConfirmed} onChange={(event) => setProcessingConfirmed(event.target.checked)} className="mt-1 h-5 w-5 accent-emerald-800" />
            <span>I understand the service operator&apos;s configured model provider will process the excerpt, potentially outside my device.</span>
          </label>
        </div>

        <button type="submit" disabled={busy || !syntheticConfirmed || !processingConfirmed} className="rounded-xl bg-emerald-900 px-5 py-3 font-semibold text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-50">
          {busy ? "Verifying report…" : "Explain excerpt"}
        </button>
      </form>

      {error && <p className="mt-6 rounded-xl border border-rose-300 bg-rose-50 p-4 text-rose-950" role="alert">{error}</p>}

      {result && <section className="mt-8 border-t border-slate-200 pt-6" aria-labelledby="result-heading" aria-live="polite">
        <h3 id="result-heading" className="text-xl font-semibold">Result</h3>
        <p className="mt-2 text-sm text-slate-700">{result.disclaimer}</p>
        {result.query_notice && <p className="mt-4 rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-950">{result.query_notice}</p>}

        {result.status === "refused" ? (
          <p className="mt-4 rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-950">{result.refusal_message}</p>
        ) : result.status === "no_supported_claims" ? (
          <p className="mt-4 rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-950">No explanation statements passed the source and safety checks. Please review the original report with your care team.</p>
        ) : (
          <>
            <h4 className="mt-5 font-semibold">What the report says</h4>
            <ul className="mt-3 space-y-4">
              {result.claims.map((claim) => <li key={claim.claim_id} className="rounded-xl border border-slate-200 p-4">
                <p>{claim.text}</p>
                {claim.citations.map((citation) => <blockquote key={`${claim.claim_id}-${citation.fact_id}`} className="mt-3 border-l-4 border-emerald-700 pl-3 text-sm text-slate-700">
                  <span className="font-semibold">Source quote · {citation.fact_id}</span><br />
                  <q>{citation.evidence.quote}</q>
                </blockquote>)}
              </li>)}
            </ul>
          </>
        )}

        {result.status !== "refused" && result.questions_for_care_team.length > 0 && <div className="mt-6">
          <h4 className="font-semibold">Questions you could ask your care team</h4>
          <ul className="mt-2 list-disc space-y-2 pl-6">
            {result.questions_for_care_team.map((item) => <li key={item.question_id}>{item.text}</li>)}
          </ul>
        </div>}

        {result.status !== "refused" && <details className="mt-6 rounded-xl bg-slate-50 p-4">
          <summary className="cursor-pointer font-semibold">Extracted report fields and exact evidence</summary>
          <ul className="mt-3 space-y-3">
            {result.facts.map((fact) => <li key={fact.fact_id} className="border-t border-slate-200 pt-3">
              <span className="font-semibold capitalize">{fieldLabel(fact.field)}:</span> {fact.status === "not_stated" ? "Not stated in this excerpt" : fact.status === "unclear" ? "Unclear in this excerpt" : fact.value}
              {fact.evidence && <blockquote className="mt-1 border-l-2 border-slate-400 pl-3 text-sm text-slate-700"><q>{fact.evidence.quote}</q></blockquote>}
            </li>)}
          </ul>
        </details>}

        <p className="mt-6 text-sm text-slate-600">{result.omitted_claim_count > 0 ? `${result.omitted_claim_count} proposed statement(s) were omitted by verification.` : "Only statements that passed verification are shown."} Confirm all meanings with your care team.</p>
      </section>}
    </section>
  );
}
