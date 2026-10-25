"use client";

import { useEffect, useState } from "react";

type State = "checking" | "online" | "offline";

export default function HealthStatus() {
  const [state, setState] = useState<State>("checking");
  useEffect(() => {
    let active = true;
    fetch("/api/health", { cache: "no-store" })
      .then((response) => {
        if (!response.ok) throw new Error("unavailable");
        return response.json() as Promise<{ status: string }>;
      })
      .then((data) => { if (active) setState(data.status === "ok" ? "online" : "offline"); })
      .catch(() => { if (active) setState("offline"); });
    return () => { active = false; };
  }, []);
  const label = state === "checking" ? "Checking API…" : state === "online" ? "API reachable" : "API unavailable";
  return <p className="mt-5 flex items-center gap-2 text-sm" role="status" aria-live="polite">
    <span aria-hidden="true" className={`inline-block h-2.5 w-2.5 rounded-full ${state === "online" ? "bg-emerald-700" : state === "offline" ? "bg-rose-700" : "bg-amber-500"}`} />
    {label}
  </p>;
}
