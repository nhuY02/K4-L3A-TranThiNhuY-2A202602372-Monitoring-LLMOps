from __future__ import annotations

import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SUBMISSION_DIR = ROOT_DIR / "submission"
REPORT_PATH = SUBMISSION_DIR / "REPORT.md"
EVIDENCE_DIR = SUBMISSION_DIR / "evidence"


def test_report_exists_and_contains_student_metadata():
    """Kiểm tra REQ-NFR-05: File submission/REPORT.md phải tồn tại và có đủ thông tin học viên & cấu trúc."""
    assert REPORT_PATH.exists(), "submission/REPORT.md không tồn tại!"
    content = REPORT_PATH.read_text(encoding="utf-8")

    # Kiểm tra metadata học viên
    assert "Trần Thị Như Ý" in content, "Thiếu họ tên học viên Trần Thị Như Ý"
    assert "2A202602372" in content, "Thiếu MSSV 2A202602372"
    assert "K4-L3A" in content, "Thiếu lớp K4-L3A"

    # Kiểm tra các mục cấu trúc bắt buộc
    required_sections = [
        "## 1. Thông tin học viên",
        "## 2. Evidence index",
        "## 3. Kết quả kỹ thuật",
        "## 4. Logging và PII",
        "## 5. Tracing và prompt versioning",
        "## 6. Dashboard, SLO và alerts",
        "## 7. Điều tra challenge",
        "## 8. Giải thích và tự đánh giá",
        "## 9. Checklist trước khi nộp",
    ]
    for section in required_sections:
        assert section in content, f"Thiếu mục bắt buộc trong REPORT.md: {section}"


def test_all_evidence_files_exist_and_non_empty():
    """Kiểm tra REQ-NFR-05: Toàn bộ 14 evidence files trong submission/evidence/ phải tồn tại và non-empty."""
    expected_evidence_files = [
        "01-pytest.txt",
        "02-log-validator.txt",
        "03-dashboard-validator.txt",
        "04-structured-log.md",
        "05-pii-redaction.md",
        "06-trace-list.md",
        "07-trace-waterfall.md",
        "08-trace-metadata.md",
        "09-prompt-versions.md",
        "10-prompt-rollback.md",
        "11-dashboard-overview.png",
        "12-incident-metric.md",
        "13-incident-log.md",
        "14-incident-trace.md",
    ]
    for filename in expected_evidence_files:
        filepath = EVIDENCE_DIR / filename
        assert filepath.exists(), f"Evidence file {filename} không tồn tại trong submission/evidence/"
        assert filepath.stat().st_size > 0, f"Evidence file {filename} bị rỗng (0 bytes)!"


def test_all_links_in_report_resolve():
    """Kiểm tra REQ-NFR-05: Mọi đường dẫn markdown link trong REPORT.md trỏ đến evidence đều hợp lệ."""
    content = REPORT_PATH.read_text(encoding="utf-8")
    links = re.findall(r"\[.*?\]\((evidence/[^)]+)\)", content)
    assert len(links) >= 10, "Phải có ít nhất 10 relative links trỏ tới evidence/"

    for rel_link in links:
        target_path = SUBMISSION_DIR / rel_link
        assert target_path.exists(), f"Đường dẫn liên kết không tồn tại: {rel_link}"


def test_evidence_verification_metrics_match():
    """Kiểm tra REQ-NFR-05: Kết quả trong file evidence khớp chính xác với điểm chuẩn."""
    # 1. Log validator evidence: 100/100, 0 PII leak
    log_val_text = (EVIDENCE_DIR / "02-log-validator.txt").read_text(encoding="utf-8")
    assert "Estimated Score: 100/100" in log_val_text
    assert "Potential PII leaks detected: 0" in log_val_text

    # 2. Dashboard validator evidence: 6/6 panel
    dash_val_text = (EVIDENCE_DIR / "03-dashboard-validator.txt").read_text(encoding="utf-8")
    assert "6/6 panel" in dash_val_text

    # 3. Incident investigation correlation consistency:
    metric_text = (EVIDENCE_DIR / "12-incident-metric.md").read_text(encoding="utf-8")
    incident_log_text = (EVIDENCE_DIR / "13-incident-log.md").read_text(encoding="utf-8")
    incident_trace_text = (EVIDENCE_DIR / "14-incident-trace.md").read_text(encoding="utf-8")

    # Cùng correlation_id req-a214b648
    assert "req-a214b648" in incident_log_text
    assert "req-a214b648" in incident_trace_text

    # Trace ID khớp giữa REPORT.md và file trace
    trace_id = "fe47bc4c4863d5f87bd5475bb657f61e"
    assert trace_id in incident_trace_text
    assert trace_id in REPORT_PATH.read_text(encoding="utf-8")
