from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

# REQ-FR-04: Tích hợp Langfuse Python SDK v4 cho Distributed Tracing
try:
    from langfuse import get_client, observe, propagate_attributes

    LANGFUSE_SDK_AVAILABLE = True
except ImportError:  # pragma: no cover - chỉ dùng khi chưa cài requirements
    LANGFUSE_SDK_AVAILABLE = False

    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func

        return decorator

    class _DummyClient:
        def update_current_span(self, **kwargs: Any) -> None:
            return None

        def update_current_generation(self, **kwargs: Any) -> None:
            return None

        def start_as_current_observation(self, **kwargs: Any) -> None:
            return None

        def flush(self) -> None:
            return None

    def get_client():
        return _DummyClient()

    @contextmanager
    def propagate_attributes(**kwargs: Any):
        yield


def get_langfuse_client():
    """Lấy Langfuse client thể hiện hiện tại."""
    return get_client()


def tracing_enabled() -> bool:
    """Kiểm tra tính khả dụng của Langfuse SDK và cặp khóa xác thực trong biến môi trường."""
    return LANGFUSE_SDK_AVAILABLE and bool(
        os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
    )


def flush_traces() -> None:
    """Đẩy toàn bộ traces và spans đang chờ trong buffer lên Langfuse Cloud."""
    client = get_langfuse_client()
    if hasattr(client, "flush") and callable(client.flush):
        try:
            client.flush()
        except Exception:
            pass
