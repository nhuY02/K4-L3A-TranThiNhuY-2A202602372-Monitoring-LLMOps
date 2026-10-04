from __future__ import annotations

import hashlib
import re

# REQ-FR-03: Định nghĩa các mẫu Regex nhận diện dữ liệu nhạy cảm (PII)
# Bao gồm: Email, Số điện thoại Việt Nam, CCCD (12 chữ số) và Thẻ tín dụng/ghi nợ
PII_PATTERNS: dict[str, str] = {
    # Nhận diện email hợp lệ (hỗ trợ cả subdomain và các ký tự đặc biệt hợp lệ)
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    # Nhận diện số điện thoại Việt Nam (đầu 0 hoặc +84, theo sau bởi 9 chữ số với phân cách khoảng trắng, dấu chấm hoặc gạch nối)
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    # Nhận diện số Căn cước công dân (12 chữ số liền nhau hoặc chia nhóm 3-3-3-3)
    "cccd": r"(?<!\d)\d{3}[- ]?\d{3}[- ]?\d{3}[- ]?\d{3}(?!\d)|\b\d{12}\b",
    # Nhận diện thẻ thanh toán (chuẩn 16 số chia nhóm 4-4-4-4 hoặc 15 số 4-6-5 của Amex)
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b|\b\d{4}[- ]?\d{6}[- ]?\d{5}\b",
}

# Pre-compile regex để tối ưu hóa hiệu năng xử lý trong môi trường tải cao
COMPILED_PATTERNS: dict[str, re.Pattern] = {
    name: re.compile(pattern, re.IGNORECASE)
    for name, pattern in PII_PATTERNS.items()
}


def scrub_text(text: str) -> str:
    """Loại bỏ và thay thế các thông tin nhạy cảm (PII) trong chuỗi văn bản bằng nhãn REDACTED."""
    if not text:
        return text
    safe = text
    for name, compiled in COMPILED_PATTERNS.items():
        safe = compiled.sub(f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    """Tạo bản tóm tắt an toàn cho văn bản: đã được scrub PII và cắt ngắn theo max_len."""
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    """Mã hóa một chiều User ID bằng SHA-256 lấy 12 ký tự hex đầu tiên để bảo vệ danh tính người dùng."""
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
