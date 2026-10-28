"""Unit tests for RateLimitMiddleware plus a wiring check on the FastAPI app."""

import asyncio
from typing import Any

import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.main import app as real_app
from app.ratelimit import RateLimitMiddleware


async def _echo(_: httpx.Request) -> JSONResponse:
    return JSONResponse({"ok": True})


def _limited_app(limit: int, window_seconds: float) -> Any:
    """Build a minimal ASGI app with RateLimitMiddleware in front of an echo endpoint."""

    class Wrap:
        def __init__(self, inner: Any) -> None:
            self.rl = RateLimitMiddleware(inner, limit=limit, window_seconds=window_seconds)

        async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
            await self.rl(scope, receive, send)

    inner = Starlette(routes=[Route("/analyze", _echo, methods=["POST"])])
    return Wrap(inner)


def test_rate_limiter_returns_429_with_retry_after() -> None:
    app = _limited_app(limit=2, window_seconds=60.0)

    async def run() -> tuple[list[int], str | None]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
            s1 = await c.post("/analyze", json={})
            s2 = await c.post("/analyze", json={})
            s3 = await c.post("/analyze", json={})
            return [s1.status_code, s2.status_code, s3.status_code], s3.headers.get("retry-after")

    statuses, retry_after = asyncio.run(run())
    assert statuses == [200, 200, 429]
    assert retry_after is not None and int(retry_after) >= 1


def test_rate_limiter_window_expires() -> None:
    app = _limited_app(limit=1, window_seconds=0.05)

    async def run() -> list[int]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
            a = await c.post("/analyze", json={})
            b = await c.post("/analyze", json={})  # within window -> 429
            await asyncio.sleep(0.1)  # window expires
            d = await c.post("/analyze", json={})  # after expiry -> 200
            return [a.status_code, b.status_code, d.status_code]

    statuses = asyncio.run(run())
    assert statuses == [200, 429, 200]


def test_rate_limiter_ignores_non_analyze_paths() -> None:
    class Wrap:
        def __init__(self, inner: Any) -> None:
            self.rl = RateLimitMiddleware(inner, limit=1, window_seconds=60.0)

        async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
            await self.rl(scope, receive, send)

    inner = Starlette(
        routes=[
            Route("/health", _echo, methods=["GET"]),
            Route("/analyze", _echo, methods=["POST"]),
        ]
    )
    app = Wrap(inner)

    async def run() -> list[int]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
            a = await c.post("/analyze", json={})
            b = await c.post("/analyze", json={})  # 429
            h1 = await c.get("/health")
            h2 = await c.get("/health")  # not limited
            return [a.status_code, b.status_code, h1.status_code, h2.status_code]

    statuses = asyncio.run(run())
    assert statuses == [200, 429, 200, 200]


def test_rate_limiter_shares_unknown_bucket_when_client_missing() -> None:
    """Requests without an ASGI client share the 'unknown' bucket."""
    app = _limited_app(limit=1, window_seconds=60.0)

    async def run() -> list[int]:
        # httpx ASGITransport sets client=("127.0.0.1", 123); force unknown via raw scope.
        statuses: list[int] = []
        for _ in range(2):
            send_calls: list[Any] = []

            async def send(message: Any, calls: list[Any] = send_calls) -> None:
                calls.append(message)

            async def receive() -> Any:
                return {"type": "http.request", "body": b"{}", "more_body": False}

            scope: dict[str, Any] = {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "path": "/analyze",
                "raw_path": b"/analyze",
                "query_string": b"",
                "root_path": "",
                "headers": [(b"content-type", b"application/json")],
                "client": None,
                "server": ("t", 80),
            }
            await app(scope, receive, send)
            status_line = next(m for m in send_calls if m["type"] == "http.response.start")
            statuses.append(status_line["status"])
        return statuses

    statuses = asyncio.run(run())
    assert statuses == [200, 429]


def test_real_app_has_rate_limiter_registered() -> None:
    registered = [m.cls for m in real_app.user_middleware]
    assert any(str(cls) == str(RateLimitMiddleware) for cls in registered)
