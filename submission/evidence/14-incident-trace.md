# 14 — Incident trace

> **Nguồn:** Langfuse Public API `GET /api/public/v2/observations`, project `day13-k4-l3a-2A202602372`.
> **Challenge:** `day13-k4-l3a-monitoring-llmops-v1` (`rag_slow` bật 09:10:23Z, tắt 09:10:53Z ngày 2026-09-29).
> **Loại evidence:** export text. Theo `docs/SUBMISSION.md`, mục này vẫn cần ảnh chụp Langfuse UI.

## Trace của request bất thường

**`fe47bc4c4863d5f87bd5475bb657f61e`** · `correlation_id = req-a214b648` (cùng request với log ở [13-incident-log.md](13-incident-log.md))

```text
AGENT       lab-agent-run    3.625 s
├── RETRIEVER   retrieval        2.502 s   ← span gây chậm (~69% thời gian request)
└── GENERATION  llm-generation   0.154 s
```

## Năm trace trong cửa sổ challenge

| trace_id | correlation_id | `lab-agent-run` (s) | `retrieval` (s) | `llm-generation` (s) | Tỷ lệ retrieval / tổng |
|---|---|---:|---:|---:|---:|
| `fe47bc4c4863d5f87bd5475bb657f61e` | **`req-a214b648`** | **3.625** | **2.502** | 0.154 | 69% |
| `79c6cd4c01057f828cbdacf8bb137043` | `req-d6fcfb37` | 2.677 | 2.501 | 0.176 | 93% |
| `de9cc0bba73b29ffa1616e735093ee5c` | `req-4c7596ed` | 2.653 | 2.501 | 0.152 | 94% |
| `11afa744533f7867d6bdb2e8e335c97a` | `req-8064368c` | 2.658 | 2.506 | 0.151 | 94% |
| `6aea9a79639df4f7a7297dcd27aa4887` | `req-3a633748` | 2.653 | 2.501 | 0.151 | 94% |

## Kết luận

`retrieval` mất khoảng 2.50 s ở cả 5 trace, trong khi `llm-generation` vẫn khoảng 0.15 s như lúc bình thường. Điều này khớp với incident `rag_slow`, vốn thêm 2.5 s vào `app/mock_rag.py::retrieve`.
