"""In-memory sliding-window rate limiter for POST /analyze.

Bound per client so a single client cannot exhaust provider quota.
The key is the ASGI ``client`` host when available, otherwise the shared
``"unknown"`` bucket (all direct connections share one limit).
"""

import time

from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


def _client_key(scope: Scope) -> str:
    client = scope.get("client")
    if client and client[0]:
        return str(client[0])
    return "unknown"


class RateLimitMiddleware:
    """Sliding-window limiter: reject once `limit` requests arrive within `window` seconds."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        limit: int,
        window_seconds: float,
        path: str = "/analyze",
        method: str = "POST",
    ) -> None:
        self.app = app
        self.limit = limit
        self.window_seconds = window_seconds
        self.path = path
        self.method = method
        # key -> list of monotonic timestamps (oldest first)
        self._hits: dict[str, list[float]] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] != self.method or scope["path"] != self.path:
            await self.app(scope, receive, send)
            return

        key = _client_key(scope)
        now = time.monotonic()
        cutoff = now - self.window_seconds

        hits = self._hits.setdefault(key, [])
        # Drop expired timestamps from the front of the list.
        while hits and hits[0] < cutoff:
            hits.pop(0)

        if len(hits) >= self.limit:
            # Compute Retry-After from the oldest in-window hit.
            retry_after = max(1, int(self.window_seconds - (now - hits[0])))
            response = JSONResponse(
                {"detail": "Too many analysis requests. Please retry later."},
                status_code=429,
                headers={
                    "Retry-After": str(retry_after),
                    "Cache-Control": "no-store, max-age=0",
                },
            )
            await response(scope, receive, send)
            return

        hits.append(now)

        # Opportunistic cleanup: drop keys with no remaining hits.
        if len(self._hits) > 10_000:
            self._hits = {k: v for k, v in self._hits.items() if v and v[-1] >= cutoff}

        await self.app(scope, receive, send)
