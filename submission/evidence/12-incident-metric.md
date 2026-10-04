# 12 — Incident metric

> **Challenge:** `day13-k4-l3a-monitoring-llmops-v1` (cohort K4, `feature=monitoring`, `latency_threshold_ms=2000`).
> **Cửa sổ sự cố:** `rag_slow` bật 2026-09-29T09:10:23Z → tắt 09:10:53Z; các response trong khoảng 09:10:28Z–09:10:40Z.
> **Nguồn:** các event `response_sent` trong `data/logs.jsonl`, cùng dữ liệu với panel latency của `/dashboard` (xem [11-dashboard-overview.png](11-dashboard-overview.png)).
> **Loại evidence:** số liệu tính từ log, chưa phải ảnh chụp màn hình.

| Giai đoạn | n | P50 (ms) | P95 (ms) | P99 (ms) | Max (ms) | TTFT P95 (ms) | Retrieval success | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Trước incident (mọi feature) | 18 | 152 | 1864 | 2134 | 2134 | 50 | 18/18 | 0 |
| **Trong challenge** | **5** | **2653** | **3624** | **3624** | **3624** | 50 | 5/5 | 0 |

## Triệu chứng

- P50 trong challenge là 2653 ms, đã vượt ngưỡng challenge 2000 ms.
- P95 là 3624 ms, vượt SLO line 3000 ms.
- TTFT (50 ms), retrieval success (100%) và error rate (0%) không đổi.
- Kết luận: đây là **sự cố latency**, không phải sự cố lỗi, và phần chậm nằm trước bước sinh token.
