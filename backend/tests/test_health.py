import asyncio

import httpx

from app.main import app


def request(method: str, path: str, headers: dict[str, str] | None = None) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, headers=headers)

    return asyncio.run(send())


def test_health_is_minimal_and_not_cached() -> None:
    response = request("GET", "/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "no-store" in response.headers["cache-control"]
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_cors_allows_only_configured_frontend_origin() -> None:
    headers = {"Access-Control-Request-Method": "GET"}
    allowed = request("OPTIONS", "/health", {**headers, "Origin": "http://localhost:3000"})
    rejected = request("OPTIONS", "/health", {**headers, "Origin": "https://not-the-app.example"})
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "access-control-allow-origin" not in rejected.headers


def test_root_makes_bootstrap_only_state_explicit() -> None:
    response = request("GET", "/")
    assert response.json() == {
        "service": "lumen-api",
        "status": "bootstrap-only",
        "analysis_available": False,
    }
