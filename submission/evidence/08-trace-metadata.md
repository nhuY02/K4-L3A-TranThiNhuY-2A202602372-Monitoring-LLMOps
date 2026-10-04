# 08 — Trace metadata

> **Nguồn:** Langfuse Public API `GET /api/public/v2/observations`, project `day13-k4-l3a-2A202602372`.
> **Trace:** `2c423dcf781b71e37c369d31cb56f59c` · `correlation_id = req-ba5e0011` (đã bỏ các attribute scope/resource của SDK).
> **Loại evidence:** export text. Theo `docs/SUBMISSION.md`, mục này vẫn cần ảnh chụp Langfuse UI.

## Tóm tắt các field cần chấm

| Field | Giá trị |
|---|---|
| `correlation_id` | `req-ba5e0011` (có trên cả 3 observation) |
| `model` | `claude-sonnet-4-5` |
| Prompt name / version / label | `day13-chat` / `1` / `baseline` |
| Tokens (in / out / total) | 32 / 115 / 147 |
| Cost USD (in / out / total) | 0.000096 / 0.001725 / 0.001821 |
| TTFT | 50 ms |
| PII thô | Không có. Retrieval chỉ ghi `document_count`; root chỉ ghi `query_preview` đã scrub |

## Metadata gốc

```json
{
 "type": "AGENT",
 "name": "lab-agent-run",
 "metadata": {
  "correlation_id": "req-ba5e0011",
  "model": "claude-sonnet-4-5",
  "feature": "qa",
  "prompt_fetch_error": "",
  "prompt_source": "langfuse",
  "prompt_version": 1,
  "prompt_label": "baseline",
  "prompt_name": "day13-chat",
  "query_preview": "Explain why metrics traces and logs work together",
  "doc_count": 1
 }
}
{
 "type": "RETRIEVER",
 "name": "retrieval",
 "metadata": {
  "correlation_id": "req-ba5e0011",
  "model": "claude-sonnet-4-5",
  "feature": "qa",
  "document_count": 1
 }
}
{
 "type": "GENERATION",
 "name": "llm-generation",
 "metadata": {
  "correlation_id": "req-ba5e0011",
  "model": "claude-sonnet-4-5",
  "feature": "qa",
  "ttft_ms": 50,
  "cost_usd": 0.001821,
  "output_tokens": 115,
  "input_tokens": 32,
  "prompt_version": 1,
  "prompt_label": "baseline",
  "prompt_name": "day13-chat"
 },
 "model": "claude-sonnet-4-5",
 "usageDetails": {
  "input": 32,
  "output": 115,
  "total": 147
 },
 "costDetails": {
  "input": 9.6e-05,
  "output": 0.001725,
  "total": 0.001821
 },
 "promptName": "day13-chat",
 "promptVersion": 1
}
```
