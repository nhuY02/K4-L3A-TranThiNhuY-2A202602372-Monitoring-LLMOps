# Evidence files

| File | Nguồn | Dạng |
|---|---|---|
| `01-pytest.txt`, `02-log-validator.txt`, `03-dashboard-validator.txt` | Output của pytest và hai validator, chạy lại trên source cuối ngày 2026-10-04 | output lệnh |
| `04-structured-log.png`, `05-pii-redaction.png`, `13-incident-log.png` | Ảnh hiển thị log thực đọc từ `data/logs.jsonl`; nội dung chi tiết đối chiếu trong các file `.md` cùng số | PNG |
| `04-structured-log.md`, `05-pii-redaction.md`, `13-incident-log.md` | Structured log trong `data/logs.jsonl` (file log không commit) | trích xuất log |
| `06-trace-list.png`, `07-trace-waterfall.png`, `08-trace-metadata.png`, `09-prompt-versions.png`, `10-prompt-rollback.png`, `14-incident-trace.png` | Ảnh chụp trực tiếp UI project Langfuse cá nhân `day13-k4-l3a-2A202602372` | PNG từ UI Langfuse |
| `06`–`10`, `14` (`.md`) | Export từ Langfuse Public API v2 của cùng project, dùng đối chiếu trace ID, metadata và prompt version | export API |
| `11-dashboard-overview.png` | Ảnh `/dashboard` chụp bằng headless Chrome | ảnh runtime |
| `12-incident-metric.png` | Bảng metric kết xuất từ các event `response_sent` trong cửa sổ challenge | PNG từ log runtime |
| `12-incident-metric.md` | Percentile tính từ event `response_sent` trong cửa sổ challenge | tính từ log |
| `baseline-log-validator.txt` | Validator chạy trên log starter, trước CP1 | output lệnh |

Có đủ 14 evidence đánh số `01`–`14`. Ảnh `04`, `05`, `12`, `13` được dựng từ dữ liệu runtime gốc và không tự thêm log/metric; các file `.md` giữ chi tiết để kiểm tra. Ảnh `06`–`10` và `14` được chụp trực tiếp từ UI Langfuse; các export text cùng số dùng để đối chiếu.

Không chứa API key hoặc PII thật; PII trong `05` là giá trị test giả. `config/challenge.json` được giữ ngoài Git theo `.gitignore`.
