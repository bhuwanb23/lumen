from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.config import get_settings
from app.pipeline import analyze_report
from app.providers import ProviderError, create_provider
from app.safety import classify_user_question, make_refusal
from app.schemas import AnalysisRequest, AnalysisResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(settings.model_timeout_seconds),
        follow_redirects=False,
        trust_env=False,
    )
    try:
        yield
    finally:
        await app.state.http_client.aclose()


class AnalysisBodyLimitMiddleware:
    """Bound direct FastAPI POST bodies even when Content-Length is absent."""

    def __init__(self, app: ASGIApp, max_bytes: int = 1_000_000) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] != "/analyze":
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        content_length = headers.get(b"content-length")
        if (
            content_length is not None
            and content_length.isdigit()
            and int(content_length) > self.max_bytes
        ):
            response = JSONResponse(
                {"detail": "Submitted request exceeds the body limit."},
                status_code=413,
                headers={"Cache-Control": "no-store, max-age=0"},
            )
            await response(scope, receive, send)
            return

        messages: list[Message] = []
        total_bytes = 0
        while True:
            message = await receive()
            messages.append(message)
            if message["type"] == "http.request":
                total_bytes += len(message.get("body", b""))
                if total_bytes > self.max_bytes:
                    response = JSONResponse(
                        {"detail": "Submitted request exceeds the body limit."},
                        status_code=413,
                        headers={"Cache-Control": "no-store, max-age=0"},
                    )
                    await response(scope, receive, send)
                    return
                if not message.get("more_body", False):
                    break
            elif message["type"] == "http.disconnect":
                return

        async def replay() -> Message:
            if messages:
                return messages.pop(0)
            return {"type": "http.disconnect"}

        await self.app(scope, replay, send)


app = FastAPI(
    title="Lumen API",
    version="0.2.0",
    description=(
        "Source-grounded explanation API; model use is disabled unless explicitly configured."
    ),
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(AnalysisBodyLimitMiddleware, max_bytes=1_000_000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
    max_age=600,
)


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.exception_handler(RequestValidationError)
async def redact_validation_error(_: Request, __: RequestValidationError) -> JSONResponse:
    """Pydantic errors can echo input values; never include submitted report text."""
    return JSONResponse(status_code=422, content={"detail": "Invalid analysis request."})


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Liveness only: disclose no secret/configuration/provider status."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse, tags=["analysis"])
async def analyze(request: Request, body: AnalysisRequest) -> AnalysisResponse:
    if len(body.report_text) > settings.max_report_chars:
        raise HTTPException(status_code=413, detail="Submitted text exceeds the configured limit.")

    refusal_category = classify_user_question(body.user_question)
    if refusal_category is not None:
        return make_refusal(body, refusal_category)

    if not body.data_is_synthetic_or_deidentified:
        raise HTTPException(
            status_code=400,
            detail="Confirm the submitted text is synthetic or de-identified before analysis.",
        )
    if not body.external_processing_acknowledged:
        raise HTTPException(
            status_code=400,
            detail="Acknowledge processing by the configured model provider before analysis.",
        )

    try:
        client = request.app.state.http_client
        generator = create_provider(settings, client, role="generator")
        verifier = create_provider(settings, client, role="verifier")
        return await analyze_report(body, generator, verifier)
    except ProviderError:
        # Provider exception messages and bodies are deliberately not returned or logged.
        raise HTTPException(
            status_code=503,
            detail="Analysis is unavailable. No generated claims were returned.",
        ) from None
    except PermissionError:
        raise HTTPException(
            status_code=400, detail="Required processing acknowledgements are missing."
        ) from None
    except Exception:
        # Never attach exception text/traceback here: third-party errors may contain submitted data.
        import logging

        logging.getLogger("lumen.safety").error("analysis_failed; request content redacted")
        raise HTTPException(
            status_code=500,
            detail="Analysis could not be completed. No generated claims were returned.",
        ) from None


@app.get("/", include_in_schema=False)
async def root() -> dict[str, Any]:
    return {"service": "lumen-api", "status": "ready"}
