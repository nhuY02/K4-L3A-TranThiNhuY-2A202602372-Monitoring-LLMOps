# 10 — Prompt promote / rollback

> **Nguồn:** Langfuse Public API (`GET /api/public/v2/observations` cho trace, `PATCH /api/public/v2/prompts/day13-chat/versions/{v}` để đổi label), project `day13-k4-l3a-2A202602372`.
> **Loại evidence:** export text. Theo `docs/SUBMISSION.md`, mục này vẫn cần ảnh chụp Langfuse UI.
> **Cùng một input cho mọi request:** `feature=qa`, message `"Explain why metrics traces and logs work together"`.

## Trạng thái label

| Bước | v1 | v2 |
|---|---|---|
| Trước | `baseline`, `production` | `candidate`, `latest` |
| Promote v2 → `production` | `baseline` | `candidate`, `production`, `latest` |
| Rollback `production` → v1 | `baseline`, `production` | `candidate`, `latest` |

## Trace của từng bước

| start (UTC) | Bước | Label app dùng | trace_id | correlation_id | promptVersion |
|---|---|---|---|---|---:|
| 2026-09-29T09:05:57.705Z | Candidate | `candidate` | `97ec27143efb9cb792fe2826e555be87` | `req-cad10002` | 2 |
| 2026-09-29T09:08:39.669Z | Baseline (v1 = baseline + production) | `baseline` | `2c423dcf781b71e37c369d31cb56f59c` | `req-ba5e0011` | 1 |
| 2026-09-29T09:09:01.308Z | Sau promote v2 → production | `production` | `5f1f9a56f748c303b971340b1a684a9f` | `req-0f0d0013` | 2 |
| 2026-09-29T09:09:27.516Z | Sau rollback production → v1 | `production` | `78f725bba5d5c77b003926aa2c333e6e` | `req-0b1c0014` | 1 |

Cùng label `production`, version phục vụ đổi từ 2 về 1 sau rollback mà không cần deploy lại code.

**Label cuối cùng:** v1 = `baseline, production`; v2 = `candidate, latest`.
