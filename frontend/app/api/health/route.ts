import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  // Server-to-server only. The browser never contacts localhost or the backend directly.
  const backendUrl = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
  try {
    const upstream = await fetch(new URL("/health", backendUrl), {
      cache: "no-store",
      signal: AbortSignal.timeout(2500),
    });
    if (!upstream.ok) throw new Error("backend_unhealthy");
    const payload: unknown = await upstream.json();
    if (typeof payload !== "object" || payload === null || !("status" in payload) || payload.status !== "ok") {
      throw new Error("invalid_health_response");
    }
    return NextResponse.json({ status: "ok" }, { headers: { "Cache-Control": "no-store" } });
  } catch {
    // Do not expose upstream URL, environment values, or exception details.
    return NextResponse.json({ status: "unavailable" }, { status: 503, headers: { "Cache-Control": "no-store" } });
  }
}
