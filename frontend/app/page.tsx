import Analyzer from "@/app/analyzer";
import HealthStatus from "@/app/health-status";

export default function Home() {
  return (
    <main id="main" className="mx-auto min-h-screen max-w-5xl px-5 py-8 sm:px-8">
      <a href="#main" className="sr-only focus:not-sr-only">Skip to main content</a>
      <header className="mb-12 flex flex-wrap items-center justify-between gap-4">
        <span className="text-xl font-bold tracking-tight" aria-label="Lumen">◉ Lumen</span>
        <span className="rounded-full border border-emerald-900/20 px-3 py-1 text-sm">Prototype · English · text only</span>
      </header>
      <section className="max-w-3xl">
        <p className="mb-3 font-semibold uppercase tracking-[.14em] text-emerald-800">Before your appointment</p>
        <h1 className="mb-5 text-4xl font-semibold leading-tight sm:text-6xl">A clearer conversation starts with understanding the report.</h1>
        <p className="text-lg text-slate-700">Lumen is a source-grounded prototype for explaining cancer pathology-report wording and preparing neutral questions for a care team.</p>
      </section>
      <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-5" aria-labelledby="status-heading">
        <h2 id="status-heading" className="text-lg font-semibold">Service status</h2>
        <p className="mt-1 text-sm text-slate-700">Model processing is disabled by default and works only when the operator explicitly configures a provider and required credentials.</p>
        <HealthStatus />
      </section>
      <Analyzer />
      <aside className="mt-8 rounded-2xl bg-amber-50 p-5 text-sm text-amber-950" aria-label="Medical safety notice">
        <strong>Important:</strong> This prototype is not a clinical tool or medical advice. It does not diagnose, predict outcomes, recommend or rank treatment, advise doses, decide trial eligibility, or triage urgent symptoms. It may omit information or return no claims. Do not use it to make care decisions; confirm the report with your clinician.
      </aside>
      <footer className="mt-12 border-t border-slate-300 pt-5 text-sm text-slate-600">English only · Synthetic or de-identified excerpts only · No report-body logging or application storage</footer>
    </main>
  );
}

