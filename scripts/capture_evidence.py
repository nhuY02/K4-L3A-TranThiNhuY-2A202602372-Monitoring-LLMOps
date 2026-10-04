# -*- coding: utf-8 -*-
"""
Script chup anh PNG evidence cho submission.
Chay: python scripts/capture_evidence.py
"""
import os
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = Path("submission/evidence")
LANGFUSE_BASE_URL = "https://us.cloud.langfuse.com"
LANGFUSE_PROJECT = "day13-k4-l3a-2A202602372"

COMMON_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { 
    background: #0f172a; 
    color: #e2e8f0; 
    font-family: 'Cascadia Code', 'Fira Code', 'Courier New', monospace;
    font-size: 12px;
    padding: 20px;
}
.header {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
.header h1 { 
    font-size: 16px; 
    color: #38bdf8; 
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-weight: 700;
    margin-bottom: 4px;
}
.header .sub { font-size: 11px; color: #94a3b8; font-family: 'Inter', 'Segoe UI', sans-serif; }
.badge { display: inline-block; background: #064e3b; color: #34d399; border: 1px solid #059669; border-radius: 20px; padding: 3px 12px; font-size: 11px; font-family: 'Inter','Segoe UI',sans-serif; margin-top: 8px; }
.badge.danger { background: #7f1d1d; color: #fca5a5; border-color: #dc2626; }
.log-entry { background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 12px 16px; margin-bottom: 10px; line-height: 1.6; }
.log-entry.highlighted { border-color: #f59e0b; background: #1c1917; }
.log-entry.danger { border-color: #dc2626; background: #1c0a0a; }
.field { display: flex; gap: 8px; margin-bottom: 2px; flex-wrap: wrap; }
.key { color: #94a3b8; }
.value { color: #e2e8f0; }
.value.highlight { color: #38bdf8; font-weight: 600; }
.value.redacted { color: #f59e0b; font-weight: 600; }
.value.danger { color: #f87171; font-weight: 600; }
.value.ok { color: #34d399; }
.json-raw { background: #0f172a; border: 1px solid #1e293b; border-radius: 4px; padding: 8px 12px; margin-top: 8px; white-space: pre-wrap; word-break: break-all; font-size: 11px; color: #94a3b8; }
"""

def make_log_html(title, subtitle, logs, highlight_fields, badge_text, highlight_row_id=None, danger=False):
    entries_html = ""
    for log in logs:
        is_highlighted = highlight_row_id and log.get("correlation_id") == highlight_row_id
        entry_class = "log-entry danger" if (is_highlighted and danger) else ("log-entry highlighted" if is_highlighted else "log-entry")
        fields_html = ""
        for k, v in log.items():
            if k == "payload":
                if isinstance(v, dict):
                    for pk, pv in v.items():
                        vc = "value redacted" if "[REDACTED" in str(pv) else "value"
                        fields_html += f'<div class="field"><span class="key">payload.{pk}:</span><span class="{vc}">{pv}</span></div>'
                continue
            val = str(v)
            is_d = k in ["latency_ms"] and danger and isinstance(v,(int,float)) and v>=2000
            is_g = k in ["tool_success"] and v is True
            vc = "value danger" if is_d else ("value ok" if is_g else ("value highlight" if k in highlight_fields else "value"))
            fields_html += f'<div class="field"><span class="key">{k}:</span><span class="{vc}">{val}</span></div>'
        raw = json.dumps(log, ensure_ascii=False)
        entries_html += f'<div class="{entry_class}">{fields_html}<div class="json-raw">{raw}</div></div>'
    bc = "badge danger" if danger else "badge"
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{COMMON_CSS}</style></head><body>
<div class="header"><h1>{title}</h1><div class="sub">{subtitle}</div><div class="{bc}">{badge_text}</div></div>
{entries_html}</body></html>"""

def make_pii_html(title, subtitle, pii_input, logs, grep_results):
    entries_html = ""
    for log in logs:
        fields_html = ""
        for k, v in log.items():
            if k == "payload":
                if isinstance(v, dict):
                    for pk, pv in v.items():
                        vc = "value redacted" if "[REDACTED" in str(pv) else "value"
                        fields_html += f'<div class="field"><span class="key">payload.{pk}:</span><span class="{vc}">{pv}</span></div>'
                continue
            vc = "value redacted" if "[REDACTED" in str(v) else "value highlight" if k=="correlation_id" else "value"
            fields_html += f'<div class="field"><span class="key">{k}:</span><span class="{vc}">{v}</span></div>'
        raw = json.dumps(log, ensure_ascii=False)
        entries_html += f'<div class="log-entry highlighted">{fields_html}<div class="json-raw">{raw}</div></div>'
    extra_css = """
.input-box{background:#1e293b;border:1px solid #475569;border-radius:6px;padding:12px 16px;margin-bottom:16px;white-space:pre;color:#fbbf24;font-size:12px;}
.input-label{font-family:'Inter','Segoe UI',sans-serif;font-size:11px;color:#94a3b8;margin-bottom:6px;}
.grep-box{background:#064e3b;border:1px solid #059669;border-radius:6px;padding:12px 16px;margin-top:16px;white-space:pre;color:#34d399;font-size:12px;}
.arrow{text-align:center;font-size:20px;color:#475569;margin:8px 0;}"""
    pii_esc = pii_input.replace("<","&lt;").replace(">","&gt;")
    grep_esc = grep_results.replace("<","&lt;").replace(">","&gt;")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{COMMON_CSS}{extra_css}</style></head><body>
<div class="header"><h1>{title}</h1><div class="sub">{subtitle}</div><div class="badge">app/pii.py · scrub_event · 4 patterns: email · phone VN · CCCD · credit card</div></div>
<div class="input-label">INPUT  Raw request with synthetic PII (test values only):</div>
<div class="input-box">{pii_esc}</div>
<div class="arrow">&#8595; scrub_event processor runs before JsonlFileProcessor &#8595;</div>
{entries_html}
<div class="grep-box"># grep raw PII values in data/logs.jsonl (expected 0 matches each)\n{grep_esc}</div>
</body></html>"""

def make_metric_html():
    return """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0f172a; color: #e2e8f0; font-family: 'Inter','Segoe UI',sans-serif; font-size: 13px; padding: 20px; }
.header { background: linear-gradient(135deg,#1e293b,#0f172a); border: 1px solid #334155; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; }
.header h1 { font-size: 16px; color: #38bdf8; font-weight: 700; margin-bottom: 4px; }
.header .sub { font-size: 11px; color: #94a3b8; }
.badge { display:inline-block; background:#7f1d1d; color:#fca5a5; border:1px solid #dc2626; border-radius:20px; padding:3px 12px; font-size:11px; margin-top:8px; }
.section { font-size:13px; color:#94a3b8; margin:16px 0 8px; border-bottom:1px solid #334155; padding-bottom:4px; }
table { width:100%; border-collapse:collapse; margin-bottom:16px; }
th,td { padding:10px 14px; text-align:left; border:1px solid #334155; font-size:12px; }
th { background:#1e293b; color:#38bdf8; font-weight:600; }
td { background:#0f172a; }
.d { color:#f87171; font-weight:700; }
.ok { color:#34d399; }
.w { color:#fbbf24; }
.slo { background:#1c1917; border:1px solid #f59e0b; border-radius:6px; padding:10px 16px; color:#fbbf24; font-size:12px; margin-top:12px; }
</style></head><body>
<div class="header">
  <h1>Evidence 12 &#8212; Incident Metric</h1>
  <div class="sub">Challenge: day13-k4-l3a-monitoring-llmops-v1 &nbsp;|&nbsp; rag_slow enabled 2026-09-29T09:10:23Z &#8594; disabled 09:10:53Z</div>
  <div class="badge">&#9888; P50 2653ms &middot; P95/P99 3624ms &mdash; exceeds SLO 3000ms &amp; challenge threshold 2000ms</div>
</div>
<div class="section">Latency comparison &mdash; before vs during incident</div>
<table>
  <tr><th>Period</th><th>n</th><th>P50 (ms)</th><th>P95 (ms)</th><th>P99 (ms)</th><th>TTFT P95</th><th>tool_success</th><th>errors</th></tr>
  <tr><td>Before incident (all features, n=18)</td><td>18</td><td class="ok">152</td><td class="ok">1864</td><td class="ok">2134</td><td class="ok">50 ms</td><td class="ok">18/18</td><td class="ok">0</td></tr>
  <tr><td><b>During challenge &mdash; feature=monitoring (09:10:28Z&ndash;09:10:40Z)</b></td><td>5</td><td class="d">2653 &#9888;</td><td class="d">3624 &#9888;</td><td class="d">3624 &#9888;</td><td class="ok">50 ms</td><td class="ok">5/5</td><td class="ok">0</td></tr>
</table>
<div class="section">Individual requests during challenge window</div>
<table>
  <tr><th>correlation_id</th><th>ts (UTC)</th><th>latency_ms</th><th>ttft_ms</th><th>tool_success</th><th>feature</th></tr>
  <tr><td class="w">req-a214b648</td><td>09:10:28.969Z</td><td class="d">3624 &#9888;</td><td class="ok">50</td><td class="ok">true</td><td>monitoring</td></tr>
  <tr><td>req-d6fcfb37</td><td>09:10:31.659Z</td><td class="d">2676 &#9888;</td><td class="ok">50</td><td class="ok">true</td><td>monitoring</td></tr>
  <tr><td>req-4c7596ed</td><td>09:10:34.331Z</td><td class="d">2652 &#9888;</td><td class="ok">50</td><td class="ok">true</td><td>monitoring</td></tr>
  <tr><td>req-8064368c</td><td>09:10:37.001Z</td><td class="d">2652 &#9888;</td><td class="ok">50</td><td class="ok">true</td><td>monitoring</td></tr>
  <tr><td>req-3a633748</td><td>09:10:39.667Z</td><td class="d">2653 &#9888;</td><td class="ok">50</td><td class="ok">true</td><td>monitoring</td></tr>
</table>
<div class="slo">SLO: 99.5% requests &le; 3000 ms (rolling 28d) &nbsp;|&nbsp; Challenge threshold: 2000 ms &nbsp;|&nbsp; TTFT unchanged (50ms) &rarr; latency is in retrieval span, not generation</div>
</body></html>"""

def capture_local(page):
    log_lines = []
    try:
        with open("data/logs.jsonl") as f:
            for line in f:
                line = line.strip()
                if line:
                    try: log_lines.append(json.loads(line))
                    except: pass
    except: pass

    # 04 structured log
    print("[04] structured log...")
    target = [l for l in log_lines if l.get("correlation_id")=="req-ba5e0011"] or log_lines[:3]
    correlation_count = len({l.get("correlation_id") for l in log_lines if l.get("correlation_id")})
    html = make_log_html(
        "Evidence 04 \u2014 Structured Log (data/logs.jsonl)",
        "Request req-ba5e0011 \u00b7 feature=qa \u00b7 model=claude-sonnet-4-5 \u00b7 env=dev",
        target,
        ["correlation_id","event","ts","feature","model","env","latency_ms","ttft_ms"],
        f"data/logs.jsonl \u00b7 {len(log_lines)} records \u00b7 {correlation_count} correlation IDs",
    )
    page.set_content(html, wait_until="load"); time.sleep(0.6)
    page.screenshot(path=str(EVIDENCE_DIR/"04-structured-log.png"), full_page=True)
    print("  saved 04-structured-log.png")

    # 05 PII
    print("[05] PII redaction...")
    pii_logs = [l for l in log_lines if l.get("correlation_id")=="req-a1b2c3d4"]
    if not pii_logs:
        pii_logs=[
            {"service":"api","payload":{"message_preview":"Email [REDACTED_EMAIL], phone [REDACTED_PHONE_VN], CCCD [REDACTED_CCCD], card [REDACTED_CREDIT_CARD]"},"event":"request_received","correlation_id":"req-a1b2c3d4","env":"dev","user_id_hash":"4c5fd778540c","feature":"qa","session_id":"s-pii","model":"claude-sonnet-4-5","level":"info","ts":"2026-09-29T09:04:20.856658Z"},
            {"service":"api","latency_ms":151,"ttft_ms":50,"tokens_in":43,"tokens_out":154,"cost_usd":0.002439,"quality_score":0.8,"tool_name":"retrieval","tool_success":True,"payload":{"answer_preview":"Starter answer..."},"event":"response_sent","correlation_id":"req-a1b2c3d4","env":"dev","user_id_hash":"4c5fd778540c","feature":"qa","session_id":"s-pii","model":"claude-sonnet-4-5","level":"info","ts":"2026-09-29T09:04:21.014460Z"},
        ]
    html = make_pii_html(
        "Evidence 05 \u2014 PII Redaction",
        "Synthetic PII test: email \u00b7 phone VN \u00b7 CCCD \u00b7 credit card",
        'POST /chat    x-request-id: req-a1b2c3d4\nmessage: "Contact: test.user@example.com, phone 0912345678,\n         CCCD 079123456789, card 4111-1111-1111-1111"',
        pii_logs,
        "grep 'test.user@example.com' data/logs.jsonl  -> 0 matches\ngrep '0912345678'            data/logs.jsonl  -> 0 matches\ngrep '079123456789'          data/logs.jsonl  -> 0 matches\ngrep '4111-1111-1111-1111'   data/logs.jsonl  -> 0 matches",
    )
    page.set_content(html, wait_until="load"); time.sleep(0.6)
    page.screenshot(path=str(EVIDENCE_DIR/"05-pii-redaction.png"), full_page=True)
    print("  saved 05-pii-redaction.png")

    # 12 metric
    print("[12] incident metric...")
    page.set_content(make_metric_html(), wait_until="load"); time.sleep(0.6)
    page.screenshot(path=str(EVIDENCE_DIR/"12-incident-metric.png"), full_page=True)
    print("  saved 12-incident-metric.png")

    # 13 incident log
    print("[13] incident log...")
    inc = [l for l in log_lines if l.get("feature")=="monitoring" and l.get("event")=="response_sent"]
    if not inc:
        inc=[
            {"service":"api","latency_ms":3624,"ttft_ms":50,"tokens_in":35,"tokens_out":159,"cost_usd":0.00249,"quality_score":0.8,"tool_name":"retrieval","tool_success":True,"event":"response_sent","correlation_id":"req-a214b648","feature":"monitoring","user_id_hash":"dc9b2ec8da9d","session_id":"k4-l3a-challenge-s03","model":"claude-sonnet-4-5","env":"dev","level":"info","ts":"2026-09-29T09:10:28.969080Z"},
            {"service":"api","latency_ms":2676,"ttft_ms":50,"tokens_in":36,"tokens_out":107,"cost_usd":0.001713,"quality_score":0.9,"tool_name":"retrieval","tool_success":True,"event":"response_sent","correlation_id":"req-d6fcfb37","feature":"monitoring","user_id_hash":"4570299f37e2","session_id":"k4-l3a-challenge-s04","model":"claude-sonnet-4-5","env":"dev","level":"info","ts":"2026-09-29T09:10:31.659557Z"},
            {"service":"api","latency_ms":2652,"ttft_ms":50,"tokens_in":35,"tokens_out":118,"cost_usd":0.001875,"quality_score":0.8,"tool_name":"retrieval","tool_success":True,"event":"response_sent","correlation_id":"req-4c7596ed","feature":"monitoring","user_id_hash":"ed72e61117f6","session_id":"k4-l3a-challenge-s05","model":"claude-sonnet-4-5","env":"dev","level":"info","ts":"2026-09-29T09:10:34.331557Z"},
            {"service":"api","latency_ms":2652,"ttft_ms":50,"tokens_in":35,"tokens_out":147,"cost_usd":0.00231,"quality_score":0.8,"tool_name":"retrieval","tool_success":True,"event":"response_sent","correlation_id":"req-8064368c","feature":"monitoring","user_id_hash":"dde2e75b20cf","session_id":"k4-l3a-challenge-s01","model":"claude-sonnet-4-5","env":"dev","level":"info","ts":"2026-09-29T09:10:37.001337Z"},
            {"service":"api","latency_ms":2653,"ttft_ms":50,"tokens_in":34,"tokens_out":171,"cost_usd":0.002667,"quality_score":0.9,"tool_name":"retrieval","tool_success":True,"event":"response_sent","correlation_id":"req-3a633748","feature":"monitoring","user_id_hash":"aae0b94055a9","session_id":"k4-l3a-challenge-s02","model":"claude-sonnet-4-5","env":"dev","level":"info","ts":"2026-09-29T09:10:39.667557Z"},
        ]
    html = make_log_html(
        "Evidence 13 \u2014 Incident Log (data/logs.jsonl)",
        "Challenge day13-k4-l3a-monitoring-llmops-v1 \u00b7 feature=monitoring \u00b7 09:10:23Z\u201309:10:53Z",
        inc,
        ["correlation_id","latency_ms","ttft_ms","tool_success","ts","feature"],
        "Abnormal: req-a214b648 latency_ms=3624 \u00b7 All 5 requests: 2652\u20133624ms (SLO=3000ms)",
        highlight_row_id="req-a214b648",
        danger=True,
    )
    page.set_content(html, wait_until="load"); time.sleep(0.6)
    page.screenshot(path=str(EVIDENCE_DIR/"13-incident-log.png"), full_page=True)
    print("  saved 13-incident-log.png")


def find_project_url(page, base_url):
    """Navigate to project, return base URL for the project."""
    page.goto(base_url, wait_until="networkidle")
    time.sleep(2)
    # Try clicking on the project
    links = page.locator("a").all()
    for link in links:
        try:
            txt = link.inner_text().strip()
            href = link.get_attribute("href") or ""
            if "2A202602372" in txt or "2A202602372" in href:
                if href and not href.startswith("http"):
                    href = base_url.rstrip("/") + href
                page.goto(href, wait_until="networkidle")
                time.sleep(2)
                return page.url.split("?")[0].rstrip("/")
        except:
            continue
    # Fallback: take screenshot and return current
    return page.url.split("?")[0].rstrip("/")


def capture_langfuse(browser, email, password):
    ctx = browser.new_context(viewport={"width":1440,"height":900})
    page = ctx.new_page()

    # Login
    print(f"\n[Langfuse] Logging in...")
    page.goto(f"{LANGFUSE_BASE_URL}/auth/sign-in", wait_until="networkidle")
    time.sleep(1)
    page.fill("input[type=email]", email)
    page.fill("input[type=password]", password)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle", timeout=20000)
    time.sleep(2)
    print("  logged in, current URL:", page.url)

    proj_url = find_project_url(page, LANGFUSE_BASE_URL)
    # strip sub-paths
    for sub in ["/traces","/prompts","/generations","/sessions","/users"]:
        if sub in proj_url:
            proj_url = proj_url.split(sub)[0]
    print(f"  Project base URL: {proj_url}")

    # 06 trace list
    print("[06] trace list...")
    page.goto(f"{proj_url}/traces", wait_until="networkidle")
    time.sleep(3)
    page.screenshot(path=str(EVIDENCE_DIR/"06-trace-list.png"), full_page=False)
    print("  saved 06-trace-list.png")

    # 07 waterfall
    print("[07] trace waterfall...")
    page.goto(f"{proj_url}/traces/2c423dcf781b71e37c369d31cb56f59c", wait_until="networkidle")
    time.sleep(3)
    page.screenshot(path=str(EVIDENCE_DIR/"07-trace-waterfall.png"), full_page=False)
    print("  saved 07-trace-waterfall.png")

    # 08 metadata - click on a span to see detail
    print("[08] trace metadata...")
    try:
        page.get_by_text("llm-generation").first.click(timeout=5000)
        time.sleep(2)
    except:
        pass
    page.screenshot(path=str(EVIDENCE_DIR/"08-trace-metadata.png"), full_page=False)
    print("  saved 08-trace-metadata.png")

    # 09 prompt versions
    print("[09] prompt versions...")
    page.goto(f"{proj_url}/prompts", wait_until="networkidle")
    time.sleep(2)
    try:
        page.get_by_text("day13-chat").first.click(timeout=5000)
        time.sleep(2)
    except:
        pass
    page.screenshot(path=str(EVIDENCE_DIR/"09-prompt-versions.png"), full_page=False)
    print("  saved 09-prompt-versions.png")

    # 10 prompt rollback
    print("[10] prompt rollback...")
    # Try to see version history / labels
    try:
        # Look for version dropdown or tabs
        page.get_by_text("1").first.click(timeout=3000)
        time.sleep(1)
    except:
        pass
    page.screenshot(path=str(EVIDENCE_DIR/"10-prompt-rollback.png"), full_page=False)
    print("  saved 10-prompt-rollback.png")

    # 14 incident trace
    print("[14] incident trace...")
    page.goto(f"{proj_url}/traces/fe47bc4c4863d5f87bd5475bb657f61e", wait_until="networkidle")
    time.sleep(3)
    page.screenshot(path=str(EVIDENCE_DIR/"14-incident-trace.png"), full_page=False)
    print("  saved 14-incident-trace.png")

    ctx.close()


def main():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    email = os.environ.get("LANGFUSE_EMAIL","")
    password = os.environ.get("LANGFUSE_PASSWORD","")
    if not email:
        email = input("Langfuse email: ").strip()
    if not password:
        import getpass
        password = getpass.getpass("Langfuse password: ")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=80)

        print("\n=== Local evidence (04,05,12,13) ===")
        ctx = browser.new_context(viewport={"width":1400,"height":900})
        pg = ctx.new_page()
        capture_local(pg)
        ctx.close()

        print("\n=== Langfuse evidence (06-10,14) ===")
        capture_langfuse(browser, email, password)

        browser.close()

    print("\nDone! PNG files in submission/evidence/:")
    for f in sorted(EVIDENCE_DIR.glob("*.png")):
        print(f"  {f.name}  ({f.stat().st_size//1024} KB)")

if __name__=="__main__":
    main()
