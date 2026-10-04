from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from app import logging_config
from app.main import app
from app.pii import hash_user_id
from app.schemas import LogRecord


@pytest.mark.anyio
async def test_structured_logging_lifecycle_and_context(monkeypatch, tmp_path: Path):
    """Kiểm tra REQ-FR-02: Ghi log chuẩn JSON Lines và tự động gắn kèm đầy đủ metadata context."""
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    custom_id = "req-11223344"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/chat",
            headers={"x-request-id": custom_id},
            json={
                "user_id": "nhuy_student_01",
                "session_id": "sess_monitoring_01",
                "feature": "qa",
                "message": "Kiểm tra hệ thống logging và correlation ID",
            },
        )

    assert response.status_code == 200

    # Đọc và kiểm tra cấu trúc JSON Lines
    lines = [line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 2, "Phải có ít nhất 2 log events: request_received và response_sent"

    events: list[dict] = []
    for line in lines:
        data = json.loads(line)
        # Xác thực từng dòng log tuân thủ chặt chẽ LogRecord schema
        record = LogRecord(**data)
        assert record.service == "api"
        assert record.correlation_id == custom_id
        assert record.user_id_hash == hash_user_id("nhuy_student_01")
        assert record.session_id == "sess_monitoring_01"
        assert record.feature == "qa"
        assert record.env == "dev"
        events.append(data)

    # 1. Kiểm tra sự kiện request_received
    req_event = next(ev for ev in events if ev["event"] == "request_received")
    assert req_event["level"] == "info"
    assert "message_preview" in req_event["payload"]

    # 2. Kiểm tra sự kiện response_sent
    res_event = next(ev for ev in events if ev["event"] == "response_sent")
    assert res_event["level"] == "info"
    assert res_event["latency_ms"] >= 0
    assert res_event["ttft_ms"] >= 0
    assert res_event["tokens_in"] >= 0
    assert res_event["tokens_out"] >= 0
    assert res_event["cost_usd"] >= 0
    assert res_event["quality_score"] >= 0
