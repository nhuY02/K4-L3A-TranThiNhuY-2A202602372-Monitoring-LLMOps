# 09 — Prompt versions

> **Nguồn:** Langfuse Public API `GET /api/public/v2/prompts/day13-chat?version=N`, project `day13-k4-l3a-2A202602372`.
> **Loại evidence:** export text. Theo `docs/SUBMISSION.md`, mục này vẫn cần ảnh chụp Langfuse UI.

| Version | Labels (hiện tại) | Commit message | Created (UTC) | Khác biệt |
|---:|---|---|---|---|
| 1 | `baseline`, `production` | `v1 baseline` | 2026-09-29T09:02:59.306Z | Template gốc |
| 2 | `candidate`, `latest` | `v2 candidate: concise bullet format` | 2026-09-29T09:02:59.550Z | Thêm dòng `Answer in at most 3 concise bullet points.` |

## Nội dung prompt

**v1**

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

**v2**

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
Answer in at most 3 concise bullet points.
```

## Export gốc

```json
{"name": "day13-chat", "version": 1, "type": "text", "labels": ["baseline", "production"], "commitMessage": "v1 baseline", "createdAt": "2026-09-29T09:02:59.306Z", "prompt": "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}"}
{"name": "day13-chat", "version": 2, "type": "text", "labels": ["candidate", "latest"], "commitMessage": "v2 candidate: concise bullet format", "createdAt": "2026-09-29T09:02:59.550Z", "prompt": "Feature={{feature}}\nDocs={{docs}}\nQuestion={{message}}\nAnswer in at most 3 concise bullet points."}
```
