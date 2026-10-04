# 13 — Incident log

> **Challenge:** `day13-k4-l3a-monitoring-llmops-v1` · `feature=monitoring`.
> **Nguồn:** event `response_sent` / `request_received` trong `data/logs.jsonl`.
> **Loại evidence:** trích xuất text từ log runtime, chưa phải ảnh chụp màn hình.

## Response trong cửa sổ sự cố

| ts (UTC) | correlation_id | latency_ms | ttft_ms | tool_success | session_id |
|---|---|---:|---:|---|---|
| 2026-09-29T09:10:28.969080Z | **`req-a214b648`** | **3624** | 50 | true | `k4-l3a-challenge-s03` |
| 2026-09-29T09:10:31.659557Z | `req-d6fcfb37` | 2676 | 50 | true | `k4-l3a-challenge-s04` |
| 2026-09-29T09:10:34.331157Z | `req-4c7596ed` | 2652 | 50 | true | `k4-l3a-challenge-s05` |
| 2026-09-29T09:10:37.001322Z | `req-8064368c` | 2652 | 50 | true | `k4-l3a-challenge-s01` |
| 2026-09-29T09:10:39.667668Z | `req-3a633748` | 2653 | 50 | true | `k4-l3a-challenge-s02` |

## Request bất thường được chọn: `req-a214b648`

Request này có latency cao nhất trong cửa sổ (3624 ms). Trace tương ứng xem ở [14-incident-trace.md](14-incident-trace.md).

```json
{"service": "api", "payload": {"message_preview": "Summarize the observability workflow for an AI API."}, "event": "request_received", "correlation_id": "req-a214b648", "feature": "monitoring", "user_id_hash": "dc9b2ec8da9d", "session_id": "k4-l3a-challenge-s03", "model": "claude-sonnet-4-5", "env": "dev", "level": "info", "ts": "2026-09-29T09:10:24.425876Z"}
{"service": "api", "latency_ms": 3624, "ttft_ms": 50, "tokens_in": 35, "tokens_out": 159, "cost_usd": 0.00249, "quality_score": 0.8, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."}, "event": "response_sent", "correlation_id": "req-a214b648", "feature": "monitoring", "user_id_hash": "dc9b2ec8da9d", "session_id": "k4-l3a-challenge-s03", "model": "claude-sonnet-4-5", "env": "dev", "level": "info", "ts": "2026-09-29T09:10:28.969080Z"}
```

## Toàn bộ log line `response_sent` trong challenge

```json
{"service": "api", "latency_ms": 3624, "ttft_ms": 50, "tokens_in": 35, "tokens_out": 159, "cost_usd": 0.00249, "quality_score": 0.8, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."}, "event": "response_sent", "correlation_id": "req-a214b648", "feature": "monitoring", "user_id_hash": "dc9b2ec8da9d", "session_id": "k4-l3a-challenge-s03", "model": "claude-sonnet-4-5", "env": "dev", "level": "info", "ts": "2026-09-29T09:10:28.969080Z"}
{"service": "api", "latency_ms": 2676, "ttft_ms": 50, "tokens_in": 36, "tokens_out": 107, "cost_usd": 0.001713, "quality_score": 0.9, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."}, "event": "response_sent", "correlation_id": "req-d6fcfb37", "feature": "monitoring", "user_id_hash": "4570299f37e2", "session_id": "k4-l3a-challenge-s04", "model": "claude-sonnet-4-5", "env": "dev", "level": "info", "ts": "2026-09-29T09:10:31.659557Z"}
{"service": "api", "latency_ms": 2652, "ttft_ms": 50, "tokens_in": 35, "tokens_out": 118, "cost_usd": 0.001875, "quality_score": 0.8, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."}, "event": "response_sent", "correlation_id": "req-4c7596ed", "feature": "monitoring", "user_id_hash": "ed72e61117f6", "session_id": "k4-l3a-challenge-s05", "model": "claude-sonnet-4-5", "env": "dev", "level": "info", "ts": "2026-09-29T09:10:34.331157Z"}
{"service": "api", "latency_ms": 2652, "ttft_ms": 50, "tokens_in": 35, "tokens_out": 147, "cost_usd": 0.00231, "quality_score": 0.8, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."}, "event": "response_sent", "correlation_id": "req-8064368c", "feature": "monitoring", "user_id_hash": "dde2e75b20cf", "session_id": "k4-l3a-challenge-s01", "model": "claude-sonnet-4-5", "env": "dev", "level": "info", "ts": "2026-09-29T09:10:37.001322Z"}
{"service": "api", "latency_ms": 2653, "ttft_ms": 50, "tokens_in": 34, "tokens_out": 171, "cost_usd": 0.002667, "quality_score": 0.9, "tool_name": "retrieval", "tool_success": true, "payload": {"answer_preview": "Starter answer. You should improve this output logic and add better quality chec..."}, "event": "response_sent", "correlation_id": "req-3a633748", "feature": "monitoring", "user_id_hash": "aae0b94055a9", "session_id": "k4-l3a-challenge-s02", "model": "claude-sonnet-4-5", "env": "dev", "level": "info", "ts": "2026-09-29T09:10:39.667668Z"}
```
