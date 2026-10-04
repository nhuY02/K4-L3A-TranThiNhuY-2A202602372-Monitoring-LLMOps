from __future__ import annotations

import time
import pytest
from starlette.requests import Request

from app.logging_config import scrub_event
from app.middleware import CorrelationIdMiddleware, CORRELATION_ID_REGEX
from app.pii import scrub_text, hash_user_id


def test_pii_scrubber_throughput_and_latency():
    """Kiểm tra REQ-NFR-04: Đo đạc độ trễ PII Scrubber đảm bảo trung bình < 0.5ms / payload."""
    sample_text = (
        "Xin chào, email tôi là student.test@vinuni.edu.vn, "
        "SĐT: 0912 345 678 hoặc +84-987-654-321. "
        "CCCD: 012345678901 và thẻ thanh toán: 4111 2222 3333 4444."
    )

    iterations = 500
    start = time.perf_counter()
    for _ in range(iterations):
        scrubbed = scrub_text(sample_text)
    total_time = time.perf_counter() - start

    avg_ms = (total_time / iterations) * 1000
    # Kỳ vọng độ trễ trung bình của regex pre-compiled < 0.5ms (thường ~0.05ms)
    assert avg_ms < 0.5, f"PII Scrubber quá chậm: trung bình {avg_ms:.4f}ms/lần"
    assert "[REDACTED_EMAIL]" in scrubbed
    assert "[REDACTED_PHONE_VN]" in scrubbed


def test_scrub_event_nested_structure_latency():
    """Kiểm tra REQ-NFR-04: Độ trễ xử lý đệ quy cấu trúc log dict phức tạp < 1.0ms."""
    complex_event = {
        "event": "response_sent",
        "service": "api",
        "user_email": "user@example.com",
        "payload": {
            "query": "Liên hệ 0901234567",
            "meta": {
                "card": "4111 2222 3333 4444",
                "nested_list": ["cccd: 012345678901", "normal text"],
            },
        },
    }

    iterations = 500
    start = time.perf_counter()
    for _ in range(iterations):
        _ = scrub_event(None, "info", complex_event)
    total_time = time.perf_counter() - start

    avg_ms = (total_time / iterations) * 1000
    assert avg_ms < 1.0, f"scrub_event đệ quy quá chậm: trung bình {avg_ms:.4f}ms/lần"


def test_correlation_id_regex_precompiled_performance():
    """Kiểm tra REQ-NFR-04: Regex pre-compiled kiểm tra Correlation ID cực nhanh (< 0.05ms/lần)."""
    valid_id = "req-12345678"
    invalid_id = "invalid-correlation-id"

    iterations = 2000
    start = time.perf_counter()
    for _ in range(iterations):
        _ = bool(CORRELATION_ID_REGEX.match(valid_id))
        _ = bool(CORRELATION_ID_REGEX.match(invalid_id))
    total_time = time.perf_counter() - start

    avg_ms = (total_time / (iterations * 2)) * 1000
    assert avg_ms < 0.05, f"Correlation ID regex match quá chậm: {avg_ms:.5f}ms"


def test_hash_user_id_performance():
    """Kiểm tra REQ-NFR-04: Hàm băm SHA-256 user ID đảm bảo tốc độ cực cao (< 0.05ms/lần)."""
    user_id = "student_nhu_y_2A202602372"

    iterations = 2000
    start = time.perf_counter()
    for _ in range(iterations):
        _ = hash_user_id(user_id)
    total_time = time.perf_counter() - start

    avg_ms = (total_time / iterations) * 1000
    assert avg_ms < 0.05, f"hash_user_id quá chậm: {avg_ms:.5f}ms"
