from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app import dashboard


def test_dashboard_snapshot_aggregates_six_panels(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(dashboard, "LOG_PATH", log_path)
    now = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)
    records = [
        {
            "ts": "2026-09-29T11:59:00Z",
            "event": "request_received",
        },
        {
            "ts": "2026-09-29T11:59:01Z",
            "event": "response_sent",
            "latency_ms": 1200,
            "ttft_ms": 300,
            "cost_usd": 0.001,
            "tokens_in": 100,
            "tokens_out": 50,
            "quality_score": 0.8,
            "tool_success": True,
        },
        {
            "ts": "2026-09-29T11:58:00Z",
            "event": "request_received",
        },
        {
            "ts": "2026-09-29T11:58:01Z",
            "event": "request_failed",
            "tool_success": False,
        },
    ]
    log_path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    result = dashboard.dashboard_snapshot(now)

    assert set(result["panels"]) == {"latency", "traffic", "errors", "cost", "tokens", "quality"}
    assert result["panels"]["latency"]["p95_ms"] == 1200
    assert result["panels"]["latency"]["ttft_p95_ms"] == 300
    assert result["panels"]["traffic"]["requests"] == 2
    assert result["panels"]["errors"]["error_rate_pct"] == 50
    assert result["panels"]["errors"]["retrieval_success_rate_pct"] == 50
    assert result["panels"]["cost"]["total_usd"] == 0.001
    assert result["panels"]["tokens"]["input"] == 100
    assert result["panels"]["quality"]["mean"] == 0.8
