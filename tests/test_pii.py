from app.pii import hash_user_id, scrub_text, summarize_text
from app.logging_config import scrub_event


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out

    # Test uppercase and subdomains
    out_upper = scrub_text("SUPPORT: ADMIN.TECH@COMPANY.COM.VN")
    assert "ADMIN.TECH" not in out_upper
    assert "REDACTED_EMAIL" in out_upper


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
        "+84-90-123-4567",
        "+84.901.234.567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd() -> None:
    out = scrub_text("CCCD: 012345678901")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out

    out_grouped = scrub_text("So can cuoc: 012 345 678 901")
    assert "012 345 678 901" not in out_grouped
    assert "REDACTED_CCCD" in out_grouped


def test_scrub_payment_card() -> None:
    cards = (
        "4111 1111 1111 1111",
        "4111-1111-1111-1111",
        "4111111111111111",
        "3782 822463 10005",
    )
    for card in cards:
        out = scrub_text(f"Card: {card}")
        assert card not in out
        assert "REDACTED_CREDIT_CARD" in out


def test_summarize_text_masks_pii() -> None:
    raw = "Vui lòng hoàn tiền cho email customer@example.com và số thẻ 4111 2222 3333 4444 ngay lập tức!"
    summary = summarize_text(raw, max_len=60)
    assert "customer@example.com" not in summary
    assert "4111 2222 3333 4444" not in summary
    assert "REDACTED_EMAIL" in summary
    assert len(summary) <= 63  # 60 + '...'


def test_hash_user_id() -> None:
    user_id = "student_tran_thi_nhu_y"
    hashed = hash_user_id(user_id)
    assert len(hashed) == 12
    assert hashed != user_id
    # Deterministic
    assert hash_user_id(user_id) == hashed


def test_scrub_event_nested_structures() -> None:
    event_dict = {
        "event": "test_event",
        "user_email": "test@domain.com",
        "payload": {
            "contact": "0987654321",
            "nested_list": ["Card: 4111 2222 3333 4444", "normal text"],
            "metadata": ("CCCD 012345678901", 123),
        },
    }
    cleaned = scrub_event(None, "info", event_dict)
    assert cleaned["user_email"] == "[REDACTED_EMAIL]"
    assert cleaned["payload"]["contact"] == "[REDACTED_PHONE_VN]"
    assert "4111 2222 3333 4444" not in cleaned["payload"]["nested_list"][0]
    assert "012345678901" not in cleaned["payload"]["metadata"][0]
