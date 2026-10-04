from __future__ import annotations

from contextlib import contextmanager

from app import agent as agent_module
from app.pii import hash_user_id


class MockPrompt:
    version = "1"
    name = "day13-chat"
    label = "production"
    source = "mock"
    fetch_error = None
    managed_prompt = None
    text = "Mock prompt text"


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


def test_trace_hierarchy_and_metadata_sanitization(monkeypatch):
    """Kiểm tra REQ-FR-04: Cây quan sát phân cấp Root Trace -> Retrieval Span -> LLM Generation."""
    client = MockTracingClient()
    monkeypatch.setattr(agent_module, "get_langfuse_client", lambda: client)
    monkeypatch.setattr(agent_module, "tracing_enabled", lambda: True)
    monkeypatch.setattr(agent_module, "resolve_prompt", lambda *args, **kwargs: MockPrompt())

    propagated_attrs: list[dict] = []

    @contextmanager
    def mock_propagate(**kwargs):
        propagated_attrs.append(kwargs)
        yield

    monkeypatch.setattr(agent_module, "propagate_attributes", mock_propagate)

    raw_user_id = "student_nhu_y_01"
    test_correlation_id = "req-aabbccdd"
    message_with_pii = "Contact me at test.user@vinuni.edu.vn or phone 0912345678"

    agent = agent_module.LabAgent()
    result = agent_module.LabAgent.run.__wrapped__(
        agent,
        user_id=raw_user_id,
        feature="qa",
        session_id="session-trace-01",
        message=message_with_pii,
        correlation_id=test_correlation_id,
    )

    assert result is not None
    assert result.latency_ms >= 0

    # 1. Kiểm tra Root Trace Context
    assert len(propagated_attrs) == 1
    root = propagated_attrs[0]
    assert root["user_id"] == hash_user_id(raw_user_id)
    assert raw_user_id not in root["user_id"]
    assert root["trace_name"] == "day13-agent-request"
    assert root["metadata"]["correlation_id"] == test_correlation_id
    assert root["metadata"]["feature"] == "qa"

    # 2. Kiểm tra Child Span: Retrieval
    # Retrieval span update
    retrieval_updates = [up for up in client.span_updates if "document_count" in up.get("metadata", {})]
    assert len(retrieval_updates) >= 1
    ret_meta = retrieval_updates[0]
    assert "test.user@vinuni.edu.vn" not in str(ret_meta)
    assert "0912345678" not in str(ret_meta)
    assert "[REDACTED_EMAIL]" in str(ret_meta) or "[REDACTED_PHONE_VN]" in str(ret_meta)

    # 3. Kiểm tra Child Span: LLM Generation
    assert len(client.generation_updates) >= 1
    gen = client.generation_updates[0]
    assert gen["model"] == "claude-sonnet-4-5"
    assert gen["usage_details"]["input"] > 0
    assert gen["usage_details"]["output"] > 0
    assert gen["cost_details"]["input"] > 0
    assert gen["cost_details"]["output"] > 0
    assert "ttft_ms" in gen["metadata"]
    assert "cost_usd" in gen["metadata"]
