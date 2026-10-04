from __future__ import annotations

import httpx
import pytest

from app.main import app


@pytest.mark.anyio
async def test_dashboard_endpoints():
    """Kiểm tra REQ-FR-06: Endpoint /dashboard và /dashboard/data phục vụ Observability Dashboard."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Kiểm tra HTML Dashboard UI
        html_resp = await client.get("/dashboard")
        assert html_resp.status_code == 200
        assert "text/html" in html_resp.headers["content-type"]
        assert "Latency percentiles and TTFT" in html_resp.text
        assert "Request traffic" in html_resp.text
        assert "Error rate and retrieval success" in html_resp.text
        assert "Cost over time" in html_resp.text
        assert "Input and output tokens" in html_resp.text
        assert "Quality proxy" in html_resp.text

        # 2. Kiểm tra JSON API dữ liệu cho 6 panel
        data_resp = await client.get("/dashboard/data")
        assert data_resp.status_code == 200
        data = data_resp.json()
        assert data["time_range_minutes"] == 60
        assert data["refresh_seconds"] == 30
        assert "updated_at" in data

        panels = data["panels"]
        expected_panels = {"latency", "traffic", "errors", "cost", "tokens", "quality"}
        assert set(panels.keys()) == expected_panels

        # Kiểm tra chi tiết từng panel
        assert "p50_ms" in panels["latency"]
        assert "p95_ms" in panels["latency"]
        assert "p99_ms" in panels["latency"]
        assert "ttft_p95_ms" in panels["latency"]

        assert "requests" in panels["traffic"]
        assert "requests_per_minute" in panels["traffic"]

        assert "error_rate_pct" in panels["errors"]
        assert "retrieval_success_rate_pct" in panels["errors"]

        assert "total_usd" in panels["cost"]
        assert "input" in panels["tokens"]
        assert "output" in panels["tokens"]

        assert "mean" in panels["quality"]
