from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import agent as agent_module
from app.main import app


class MockTracingClient:
    def __init__(self) -> None:
        self.span_updates: list[dict] = []
        self.generation_updates: list[dict] = []
        self.flushed = False

    def update_current_span(self, **kwargs) -> None:
        self.span_updates.append(kwargs)

    def update_current_generation(self, **kwargs) -> None:
        self.generation_updates.append(kwargs)

    def flush(self) -> None:
        self.flushed = True


def test_three_way_correlation_id_interoperability(monkeypatch, tmp_path):
    """Kiểm tra REQ-NFR-03: Đồng bộ 3 chiều Correlation ID giữa HTTP Header, Structured Log và Trace Metadata."""
    # 1. Cấu hình log file tạm để kiểm tra
    test_log_path = tmp_path / "test_interop_logs.jsonl"
    monkeypatch.setenv("LOG_PATH", str(test_log_path))
    monkeypatch.setattr("app.logging_config.LOG_PATH", test_log_path)

    # 2. Mock Langfuse Tracing Client và bắt propagate_attributes
    client_mock = MockTracingClient()
    monkeypatch.setattr(agent_module, "get_langfuse_client", lambda: client_mock)
    monkeypatch.setattr(agent_module, "tracing_enabled", lambda: True)

    propagated_contexts: list[dict] = []

    @contextmanager
    def mock_propagate(**kwargs):
        propagated_contexts.append(kwargs)
        yield

    monkeypatch.setattr(agent_module, "propagate_attributes", mock_propagate)

    test_client = TestClient(app)
    client_cid = "req-faceb00c"

    # 3. Gửi HTTP Request kèm x-request-id hợp lệ
    response = test_client.post(
        "/chat",
        headers={"x-request-id": client_cid},
        json={
            "user_id": "student_interop_test",
            "session_id": "session-interop-99",
            "feature": "qa",
            "message": "Testing 3-way correlation ID interoperability",
        },
    )

    assert response.status_code == 200
    res_data = response.json()

    # Kênh 1: Kiểm tra HTTP Layer (Header & Body)
    assert response.headers.get("x-request-id") == client_cid
    assert res_data["correlation_id"] == client_cid

    # Kênh 2: Kiểm tra Langfuse Distributed Trace Metadata
    assert len(propagated_contexts) == 1
    trace_context = propagated_contexts[0]
    assert trace_context["metadata"]["correlation_id"] == client_cid
    assert trace_context["session_id"] == "session-interop-99"

    # Kênh 3: Kiểm tra Structured Logs trong logs.jsonl
    assert test_log_path.exists(), "File log JSONL phải được tạo ra!"
    log_lines = test_log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(log_lines) >= 2, "Phải có ít nhất 2 sự kiện log (request_received và response_sent)"

    for line in log_lines:
        record = json.loads(line)
        # Bắt buộc mọi log record phát sinh trong request phải gắn correlation_id đồng bộ
        assert record.get("correlation_id") == client_cid, (
            f"Log event {record.get('event')} có correlation_id không khớp: {record.get('correlation_id')}"
        )


def test_interoperability_with_auto_generated_correlation_id(monkeypatch, tmp_path):
    """Kiểm tra REQ-NFR-03: Khi client không gửi x-request-id, ID tự sinh phải đồng bộ trên cả 3 kênh."""
    test_log_path = tmp_path / "test_autogen_logs.jsonl"
    monkeypatch.setenv("LOG_PATH", str(test_log_path))
    monkeypatch.setattr("app.logging_config.LOG_PATH", test_log_path)

    propagated_contexts: list[dict] = []

    @contextmanager
    def mock_propagate(**kwargs):
        propagated_contexts.append(kwargs)
        yield

    monkeypatch.setattr(agent_module, "propagate_attributes", mock_propagate)

    test_client = TestClient(app)

    # Gửi request KHÔNG có header x-request-id
    response = test_client.post(
        "/chat",
        json={
            "user_id": "student_autogen",
            "session_id": "session-autogen",
            "feature": "chat",
            "message": "Auto generation test",
        },
    )

    assert response.status_code == 200
    generated_cid = response.headers.get("x-request-id")
    assert generated_cid is not None
    assert generated_cid.startswith("req-")
    assert len(generated_cid) == 12  # 'req-' + 8 hex chars

    # Khớp với body
    assert response.json()["correlation_id"] == generated_cid

    # Khớp với trace metadata
    assert len(propagated_contexts) == 1
    assert propagated_contexts[0]["metadata"]["correlation_id"] == generated_cid

    # Khớp với tất cả logs
    log_lines = test_log_path.read_text(encoding="utf-8").strip().splitlines()
    for line in log_lines:
        record = json.loads(line)
        assert record.get("correlation_id") == generated_cid


def test_concurrent_requests_context_isolation(monkeypatch, tmp_path):
    """Kiểm tra REQ-NFR-03: Đảm bảo không bị rò rỉ correlation_id giữa các request kế tiếp nhau."""
    test_log_path = tmp_path / "test_isolation_logs.jsonl"
    monkeypatch.setenv("LOG_PATH", str(test_log_path))
    monkeypatch.setattr("app.logging_config.LOG_PATH", test_log_path)

    propagated_cids: list[str] = []

    @contextmanager
    def mock_propagate(**kwargs):
        propagated_cids.append(kwargs["metadata"]["correlation_id"])
        yield

    monkeypatch.setattr(agent_module, "propagate_attributes", mock_propagate)

    test_client = TestClient(app)
    cid_1 = "req-11111111"
    cid_2 = "req-22222222"

    res_1 = test_client.post(
        "/chat",
        headers={"x-request-id": cid_1},
        json={"user_id": "u1", "session_id": "s1", "feature": "qa", "message": "msg1"},
    )
    res_2 = test_client.post(
        "/chat",
        headers={"x-request-id": cid_2},
        json={"user_id": "u2", "session_id": "s2", "feature": "qa", "message": "msg2"},
    )

    assert res_1.headers.get("x-request-id") == cid_1
    assert res_2.headers.get("x-request-id") == cid_2
    assert propagated_cids == [cid_1, cid_2]
