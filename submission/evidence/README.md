# Evidence files

| File | Nguồn | Dạng |
|---|---|---|
| `01-pytest.txt`, `02-log-validator.txt`, `03-dashboard-validator.txt` | Output của pytest và hai validator, chạy lại trên source cuối ngày 2026-10-04 | output lệnh |
| `04-structured-log.md`, `05-pii-redaction.md`, `13-incident-log.md` | Structured log trong `data/logs.jsonl` (file log không commit) | trích xuất log |
| `06`–`10`, `14` (`.md`) | Export từ Langfuse Public API v2, project cá nhân `day13-k4-l3a-2A202602372` | export API |
| `11-dashboard-overview.png` | Ảnh `/dashboard` chụp bằng headless Chrome | ảnh runtime |
| `12-incident-metric.md` | Percentile tính từ event `response_sent` trong cửa sổ challenge | tính từ log |
| `baseline-log-validator.txt` | Validator chạy trên log starter, trước CP1 | output lệnh |

Có đủ 14 evidence đánh số `01`–`14`. Các file `.md` chỉ trình bày lại dữ liệu đã trích xuất; số liệu được giữ nguyên.

**Còn thiếu:** theo `docs/SUBMISSION.md`, các mục `04`–`10` và `12`–`14` cần ảnh chụp màn hình runtime/UI. Khi có ảnh, lưu cùng số thứ tự với đuôi `.png` (ví dụ `06-trace-list.png`).

Không chứa API key hoặc PII thật; PII trong `05` là giá trị test giả. `config/challenge.json` được giữ ngoài Git theo `.gitignore`.
