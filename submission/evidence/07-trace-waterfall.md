# 07 — Trace waterfall

> **Nguồn:** Langfuse Public API `GET /api/public/v2/observations`, project `day13-k4-l3a-2A202602372`.
> **Trace:** `2c423dcf781b71e37c369d31cb56f59c` · `correlation_id = req-ba5e0011`.
> **Loại evidence:** export text. Theo `docs/SUBMISSION.md`, mục này vẫn cần ảnh chụp Langfuse UI.

```text
AGENT       lab-agent-run    id=aea81c49c420d75d  parent=None              start=09:08:38.766Z  latency=1.056s
├── RETRIEVER   retrieval       id=e809c4e05cf443e6  parent=aea81c49c420d75d  start=09:08:38.768Z  latency=0s
└── GENERATION  llm-generation  id=12d358cb644ec351  parent=aea81c49c420d75d  start=09:08:39.669Z  latency=0.153s
```

| Observation | Type | id | parent | start (UTC) | latency |
|---|---|---|---|---|---:|
| `lab-agent-run` | AGENT (root) | `aea81c49c420d75d` | — | 2026-09-29T09:08:38.766Z | 1.056 s |
| `retrieval` | RETRIEVER | `e809c4e05cf443e6` | `aea81c49c420d75d` | 2026-09-29T09:08:38.768Z | 0 s |
| `llm-generation` | GENERATION | `12d358cb644ec351` | `aea81c49c420d75d` | 2026-09-29T09:08:39.669Z | 0.153 s |

Cả `retrieval` và `llm-generation` đều có `parent` là root `lab-agent-run`, đúng quan hệ cha–con.
