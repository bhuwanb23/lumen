import HealthStatus from "@/app/health-status";

export default function Home() {
  return (
    <main id="main" className="mx-auto min-h-screen max-w-5xl px-5 py-8 sm:px-8">
      <a href="#main" className="sr-only focus:not-sr-only">Skip to main content</a>
      <header className="mb-16 flex flex-wrap items-center justify-between gap-4">
        <span className="text-xl font-bold tracking-tight" aria-label="Lumen">◉ Lumen</span>
        <span className="rounded-full border border-emerald-900/20 px-3 py-1 text-sm">Prototype · setup phase</span>
      </header>
      <section className="max-w-3xl">
        <p className="mb-3 font-semibold uppercase tracking-[.14em] text-emerald-800">Before your appointment</p>
        <h1 className="mb-5 text-4xl font-semibold leading-tight sm:text-6xl">A clearer conversation starts with understanding the report.</h1>
        <p className="text-lg text-slate-700">Lumen is being built to explain what a cancer report says and help people prepare questions for their care team.</p>
      </section>
      <section className="mt-10 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8" aria-labelledby="status-heading">
        <h2 id="status-heading" className="text-2xl font-semibold">Project status</h2>
        <p className="mt-2 text-slate-700">The application shell is running. Report analysis, uploads, trials, translations and PDF cards are not implemented yet.</p>
        <HealthStatus />
      </section>
      <aside className="mt-8 rounded-2xl bg-amber-50 p-5 text-sm text-amber-950" aria-label="Medical safety notice">
        <strong>Important:</strong> Lumen is a prototype, not medical advice or a clinical tool. It does not diagnose, predict outcomes, or recommend treatment. No report analysis is available in this setup phase. Do not enter real patient information.
      </aside>
      <footer className="mt-12 border-t border-slate-300 pt-5 text-sm text-slate-600">Synthetic data only · No report storage · Model calls disabled</footer>
    </main>
  );
}
