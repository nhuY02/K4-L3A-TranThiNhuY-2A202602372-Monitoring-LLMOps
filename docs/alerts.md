# Alert runbooks

All alerts notify the Slack channel `#llmops-alerts`. First confirm the alert's
time window in `/dashboard`, then follow Metrics → Logs → Traces using the
request `correlation_id`. Do not include raw user prompts in incident messages.

## Alert 1 — Elevated user-facing latency

- **Severity / owner:** warning / LLM Platform On-call
- **Condition:** response latency P95 exceeds 3,000 ms continuously for 5 minutes.
- **SLO:** `fast_successful_requests` (99.5% within 3,000 ms over 28 days).
- **User impact:** chat responses are slower; the SLO error budget is consumed.
- **First checks:**
  1. Check the latency and traffic panels at `http://127.0.0.1:8000/dashboard` and note the affected time range.
  2. Filter `data/logs.jsonl` for slow `response_sent` events in that range and record a `correlation_id`.
  3. Open the Langfuse trace with that ID and compare retrieval and generation durations.
- **Mitigation:** if retrieval dominates, disable the affected retrieval path or restore the last known-good retrieval configuration; if generation dominates, roll back the recently promoted production prompt or route to the last known-good model configuration. Verify P95 recovers before resolving.

## Alert 2 — Elevated request error rate

- **Severity / owner:** critical / API On-call
- **Condition:** `request_failed / request_received` exceeds 2% continuously for 5 minutes.
- **SLI:** successful responses divided by all received requests; failures consume the SLO budget.
- **User impact:** some chat requests fail instead of returning an answer.
- **First checks:**
  1. Check the errors panel and group `request_failed` logs by `error_type`.
  2. Compare affected `correlation_id` values with Langfuse traces to identify the failing observation.
  3. Check whether the error began after a deployment, prompt promotion, or incident injection.
- **Mitigation:** roll back the last change associated with the failing step. If the dependency remains unavailable, return a safe service error rather than claiming a successful answer. Confirm the error rate falls below 2% for at least 5 minutes.

## Alert 3 — Low retrieval success rate

- **Severity / owner:** warning / Retrieval On-call
- **Condition:** successful retrievals divided by non-null retrieval results falls below 90% continuously for 10 minutes.
- **SLI:** retrieval success rate; low retrieval quality or availability can make answers incomplete.
- **User impact:** answers may lack the expected supporting context.
- **First checks:**
  1. Check retrieval success and request error panels for the same 10-minute window.
  2. Inspect `tool_success`, `tool_name`, and `error_type` in affected logs.
  3. Open matching traces and inspect the retrieval observation's duration and status.
- **Mitigation:** restore the last known-good retrieval/index configuration. If retrieval cannot be restored promptly, disable unsupported retrieval-dependent answers or show a clear fallback response. Confirm retrieval success exceeds 90% for 10 minutes before resolving.
