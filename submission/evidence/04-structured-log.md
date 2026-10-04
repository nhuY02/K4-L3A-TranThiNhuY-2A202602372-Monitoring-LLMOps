# 04 — Structured log

> **Nguồn:** `data/logs.jsonl` do ứng dụng ghi (file log không commit).
> **Request:** `correlation_id = req-ba5e0011`, `feature = qa`, prompt label `baseline`.
> **Loại evidence:** trích xuất text từ log runtime, chưa phải ảnh chụp màn hình.

## Field bắt buộc

| Field | `request_received` | `response_sent` |
|---|---|---|
| `ts` | `2026-09-29T09:08:37.847932Z` | `2026-09-29T09:08:39.822698Z` |
| `event` | `request_received` | `response_sent` |
| `correlation_id` | `req-ba5e0011` | `req-ba5e0011` |
| `model` | `claude-sonnet-4-5` | `claude-sonnet-4-5` |
| `env` | `dev` | `dev` |
| `feature` | `qa` | `qa` |
| `user_id_hash` | `1bcbaa7b5b0a` | `1bcbaa7b5b0a` |
| `session_id` | `s-prompt` | `s-prompt` |
| `latency_ms` | — | `1055` |
| `ttft_ms` | — | `50` |
| `tokens_in` / `tokens_out` | — | `32` / `115` |
| `cost_usd` | — | `0.001821` |

## Log line gốc

```json
{"service": "api", "payload": {"message_preview": "Explain why metrics traces and logs work together"}, "event": "request_received", "feature": "qa", "correlation_id": "req-ba5e0011", "model": "claude-sonnet-4-5", "env": "dev", "user_id_hash": "1bcbaa7b5b0a", "session_id": "s-prompt", "level": "info", "ts": "2026-09-29T09:08:37.847932Z"}
{"service": "api", "latency_ms": 1055, "ttft_ms": 50, "tokens_in": 32, "tokens_out": 115, "cost_usd": 0.001821, "quality_score": 0.8, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."}, "event": "response_sent", "feature": "qa", "correlation_id": "req-ba5e0011", "model": "claude-sonnet-4-5", "env": "dev", "user_id_hash": "1bcbaa7b5b0a", "session_id": "s-prompt", "level": "info", "ts": "2026-09-29T09:08:39.822698Z"}
```
