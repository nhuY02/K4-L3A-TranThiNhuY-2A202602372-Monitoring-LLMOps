# 05 — PII redaction

> **Nguồn:** `data/logs.jsonl`. Request gửi với header `x-request-id: req-a1b2c3d4`.
> **Dữ liệu đầu vào là PII giả** dùng cho test, không phải dữ liệu người dùng thật.
> **Loại evidence:** trích xuất text từ log runtime, chưa phải ảnh chụp màn hình.

## Input → log đầu ra

| Loại PII | Giá trị test (giả) | Trong log |
|---|---|---|
| Email | `test.user@example.com` | `[REDACTED_EMAIL]` |
| Điện thoại VN | `0912345678` | `[REDACTED_PHONE_VN]` |
| CCCD | `079123456789` | `[REDACTED_CCCD]` |
| Thẻ tín dụng | `4111-1111-1111-1111` | `[REDACTED_CREDIT_CARD]`* |

\* `message_preview` bị cắt ở 80 ký tự nên log line chỉ hiện `[R...`; giá trị gốc của thẻ cho 0 kết quả khi tìm (bảng dưới).

## Log line cùng `correlation_id`

```json
{"service": "api", "payload": {"message_preview": "Email [REDACTED_EMAIL], phone [REDACTED_PHONE_VN], CCCD [REDACTED_CCCD], card [R..."}, "event": "request_received", "correlation_id": "req-a1b2c3d4", "env": "dev", "user_id_hash": "4c5fd778540c", "feature": "qa", "session_id": "s-pii", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-09-29T09:04:20.856658Z"}
{"service": "api", "latency_ms": 151, "ttft_ms": 50, "tokens_in": 43, "tokens_out": 154, "cost_usd": 0.002439, "quality_score": 0.8, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."}, "event": "response_sent", "correlation_id": "req-a1b2c3d4", "env": "dev", "user_id_hash": "4c5fd778540c", "feature": "qa", "session_id": "s-pii", "model": "claude-sonnet-4-5", "level": "info", "ts": "2026-09-29T09:04:21.014460Z"}
```

## Tìm giá trị gốc trong `data/logs.jsonl` (kỳ vọng 0)

| Chuỗi tìm | Số kết quả |
|---|---:|
| `test.user@example.com` | 0 |
| `0912345678` | 0 |
| `079123456789` | 0 |
| `4111-1111-1111-1111` | 0 |
| `student@vinuni.edu.vn` | 0 |
