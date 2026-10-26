import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_REQUEST_BYTES = 1_000_000;
const noStore = { "Cache-Control": "no-store, max-age=0" };

async function readBoundedJson(request: Request): Promise<unknown> {
  if (!request.body) throw new Error("invalid_body");
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let totalBytes = 0;
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    totalBytes += value.byteLength;
    if (totalBytes > MAX_REQUEST_BYTES) {
      await reader.cancel().catch(() => undefined);
      throw new RangeError("body_too_large");
    }
    chunks.push(value);
  }
  const bytes = new Uint8Array(totalBytes);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return JSON.parse(new TextDecoder().decode(bytes)) as unknown;
}

export async function POST(request: Request) {
  if (!request.headers.get("content-type")?.toLowerCase().startsWith("application/json")) {
    return NextResponse.json({ detail: "Invalid analysis request." }, { status: 415, headers: noStore });
  }
  const declaredLength = Number(request.headers.get("content-length") ?? "0");
  if (Number.isFinite(declaredLength) && declaredLength > MAX_REQUEST_BYTES) {
    return NextResponse.json({ detail: "Submitted text exceeds the request limit." }, { status: 413, headers: noStore });
  }

  let body: unknown;
  try {
    body = await readBoundedJson(request);
  } catch (error) {
    if (error instanceof RangeError) {
      return NextResponse.json({ detail: "Submitted text exceeds the request limit." }, { status: 413, headers: noStore });
    }
    return NextResponse.json({ detail: "Invalid analysis request." }, { status: 400, headers: noStore });
  }

  // This server-side proxy is the only browser-facing path to FastAPI; provider keys stay server-side.
  const backendUrl = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
  try {
    const upstream = await fetch(new URL("/analyze", backendUrl), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(560_000),
    });

    if (!upstream.ok) {
      const messages: Record<number, string> = {
        400: "Required confirmations are missing or the request is invalid.",
        413: "Submitted text exceeds the configured limit.",
        422: "Invalid analysis request.",
        503: "Analysis is unavailable. No generated claims were returned.",
        500: "Analysis could not be completed. No generated claims were returned.",
      };
      const status = [400, 413, 422, 503, 500].includes(upstream.status) ? upstream.status : 503;
      return NextResponse.json(
        { detail: messages[status] ?? messages[503] },
        { status, headers: noStore },
      );
    }

    const result: unknown = await upstream.json();
    return NextResponse.json(result, { headers: noStore });
  } catch {
    // Do not log or relay upstream exceptions, request bodies, URLs, or provider error content.
    return NextResponse.json(
      { detail: "Analysis is unavailable. No generated claims were returned." },
      { status: 503, headers: noStore },
    );
  }
}
