from __future__ import annotations

from app.logging_config import scrub_event
from app.pii import hash_user_id, scrub_text


def test_dict_keys_with_pii_are_scrubbed():
    """Kiểm tra REQ-NFR-01: Che giấu PII ngay cả khi PII nằm trong key của dictionary."""
    data = {
        "student@example.com": "email_value",
        "0901234567": "phone_value",
        "normal_key": "normal_value",
    }
    scrubbed = scrub_event(None, "info", data)
    assert "student@example.com" not in scrubbed
    assert "0901234567" not in scrubbed
    assert "[REDACTED_EMAIL]" in scrubbed
    assert "[REDACTED_PHONE_VN]" in scrubbed
    assert scrubbed["normal_key"] == "normal_value"


def test_set_and_nested_tuples_are_scrubbed():
    """Kiểm tra REQ-NFR-01: Che giấu PII trong set và nested tuple."""
    data = {
        "set_data": {"CCCD 012345678901", "normal text"},
        "tuple_data": ("Card 4111 2222 3333 4444", 999),
    }
    scrubbed = scrub_event(None, "info", data)
    assert "012345678901" not in str(scrubbed["set_data"])
    assert "[REDACTED_CCCD]" in str(scrubbed["set_data"])
    assert "4111 2222 3333 4444" not in scrubbed["tuple_data"][0]
    assert "[REDACTED_CREDIT_CARD]" in scrubbed["tuple_data"][0]


def test_exception_messages_with_pii_are_scrubbed():
    """Kiểm tra REQ-NFR-01: Chuỗi exception format chứa PII được scrub sạch trước khi render."""
    data = {
        "event": "request_failed",
        "exception": 'Traceback: Error processing user payment 4111 1111 1111 1111 for student@vinuni.edu.vn',
    }
    scrubbed = scrub_event(None, "error", data)
    assert "4111 1111 1111 1111" not in scrubbed["exception"]
    assert "student@vinuni.edu.vn" not in scrubbed["exception"]
    assert "[REDACTED_CREDIT_CARD]" in scrubbed["exception"]
    assert "[REDACTED_EMAIL]" in scrubbed["exception"]


def test_user_id_hashing_one_way():
    """Kiểm tra REQ-NFR-01: Băm một chiều User ID để bảo vệ thông tin nhận dạng người dùng."""
    raw_user = "user_nhu_y_2A202602372"
    hashed = hash_user_id(raw_user)
    assert raw_user not in hashed
    assert len(hashed) == 12
    # Tính chất tất định (deterministic)
    assert hash_user_id(raw_user) == hashed
