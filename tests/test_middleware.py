from __future__ import annotations

import re
import pytest
import httpx
from fastapi import FastAPI, Request
from structlog.contextvars import get_contextvars

from app.middleware import CorrelationIdMiddleware


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/ping")
    async def ping(request: Request):
        ctx = get_contextvars()
        return {
            "state_correlation_id": getattr(request.state, "correlation_id", None),
            "context_correlation_id": ctx.get("correlation_id"),
        }

    return app


@pytest.mark.anyio
async def test_valid_incoming_request_id_preserved(test_app: FastAPI):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ping", headers={"x-request-id": "req-1234abcd"})

    assert resp.status_code == 200
    assert resp.headers["x-request-id"] == "req-1234abcd"
    assert "x-response-time-ms" in resp.headers
    assert "x-response-time" in resp.headers
    data = resp.json()
    assert data["state_correlation_id"] == "req-1234abcd"
    assert data["context_correlation_id"] == "req-1234abcd"


@pytest.mark.anyio
async def test_invalid_request_id_regenerated(test_app: FastAPI):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ping", headers={"x-request-id": "invalid-request-format"})

    assert resp.status_code == 200
    new_id = resp.headers["x-request-id"]
    assert new_id != "invalid-request-format"
    assert re.fullmatch(r"req-[0-9a-fA-F]{8}", new_id)
    data = resp.json()
    assert data["state_correlation_id"] == new_id
    assert data["context_correlation_id"] == new_id


@pytest.mark.anyio
async def test_missing_request_id_generated(test_app: FastAPI):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ping")

    assert resp.status_code == 200
    new_id = resp.headers["x-request-id"]
    assert re.fullmatch(r"req-[0-9a-fA-F]{8}", new_id)
    assert "x-response-time-ms" in resp.headers
    assert "x-response-time" in resp.headers
