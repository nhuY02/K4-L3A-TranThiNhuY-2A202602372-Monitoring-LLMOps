from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = Path(os.getenv("LOG_PATH", str(ROOT / "data" / "logs.jsonl")))
CONFIG_PATH = ROOT / "config" / "dashboard.yaml"


def _percentile(values: list[float], percentile: int) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((percentile / 100) * len(ordered) + 0.999) - 1))
    return round(ordered[index], 2)


def _read_records() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            stamp = record.get("ts")
            if isinstance(stamp, str):
                record["_timestamp"] = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                if record["_timestamp"].tzinfo is None:
                    record["_timestamp"] = record["_timestamp"].replace(tzinfo=timezone.utc)
                records.append(record)
        except (json.JSONDecodeError, ValueError):
            continue
    return records


def dashboard_snapshot(now: datetime | None = None) -> dict[str, Any]:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["dashboard"]
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    start = now - timedelta(minutes=config["time_range_minutes"])
    records = [
        record for record in _read_records()
        if start <= record["_timestamp"] <= now
    ]
    responses = [r for r in records if r.get("event") == "response_sent"]
    received = [r for r in records if r.get("event") == "request_received"]
    failures = [r for r in records if r.get("event") == "request_failed"]
    retrieval_checks = [r for r in records if isinstance(r.get("tool_success"), bool)]
    latencies = [float(r["latency_ms"]) for r in responses if isinstance(r.get("latency_ms"), (int, float))]
    ttfts = [float(r["ttft_ms"]) for r in responses if isinstance(r.get("ttft_ms"), (int, float))]

    minute_starts = [
        (start.replace(second=0, microsecond=0) + timedelta(minutes=i))
        for i in range(config["time_range_minutes"] + 1)
    ]
    buckets: dict[str, dict[str, float]] = {
        minute.isoformat(): {"requests": 0, "cost_usd": 0, "tokens_in": 0, "tokens_out": 0}
        for minute in minute_starts
    }
    latency_buckets: dict[str, list[float]] = {key: [] for key in buckets}
    for record in records:
        minute_key = record["_timestamp"].replace(second=0, microsecond=0).isoformat()
        bucket = buckets.get(minute_key)
        if bucket is None:
            continue
        if record.get("event") == "request_received":
            bucket["requests"] += 1
        if record.get("event") == "response_sent":
            latency = record.get("latency_ms")
            if isinstance(latency, (int, float)):
                latency_buckets[minute_key].append(float(latency))
            for field in ("cost_usd", "tokens_in", "tokens_out"):
                value = record.get(field)
                if isinstance(value, (int, float)):
                    bucket[field] += value

    def total(field: str) -> float:
        return round(sum(float(r.get(field, 0) or 0) for r in responses), 6)

    quality_values = [float(r["quality_score"]) for r in responses if isinstance(r.get("quality_score"), (int, float))]
    error_pct = round(100 * len(failures) / len(received), 2) if received else 0
    retrieval_pct = (
        round(100 * sum(r["tool_success"] is True for r in retrieval_checks) / len(retrieval_checks), 2)
        if retrieval_checks else 0
    )
    return {
        "title": config["title"],
        "time_range_minutes": config["time_range_minutes"],
        "refresh_seconds": config["refresh_seconds"],
        "updated_at": now.isoformat(),
        "thresholds": {panel["id"]: panel["threshold"] for panel in config["panels"]},
        "panels": {
            "latency": {
                "p50_ms": _percentile(latencies, 50),
                "p95_ms": _percentile(latencies, 95),
                "p99_ms": _percentile(latencies, 99),
                "ttft_p95_ms": _percentile(ttfts, 95),
                "series": [_percentile(latency_buckets[key], 95) or 0 for key in buckets],
            },
            "traffic": {
                "requests": len(received),
                "requests_per_minute": round(len(received) / max(config["time_range_minutes"], 1), 2),
                "series": [b["requests"] for b in buckets.values()],
            },
            "errors": {
                "error_rate_pct": error_pct,
                "error_count": len(failures),
                "retrieval_success_rate_pct": retrieval_pct,
            },
            "cost": {"total_usd": total("cost_usd"), "series": [b["cost_usd"] for b in buckets.values()]},
            "tokens": {
                "input": int(total("tokens_in")),
                "output": int(total("tokens_out")),
                "series": [b["tokens_in"] + b["tokens_out"] for b in buckets.values()],
            },
            "quality": {
                "mean": round(sum(quality_values) / len(quality_values), 3) if quality_values else None,
                "samples": len(quality_values),
            },
        },
    }


DASHBOARD_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Day 13 LLMOps dashboard</title><style>
:root{color-scheme:dark;font:15px system-ui;background:#101820;color:#e8f0f6}body{margin:0;padding:24px;max-width:1440px;margin:auto}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}.muted{color:#9db0bf}.grid{display:grid;grid-template-columns:repeat(3,minmax(240px,1fr));gap:16px}
article{background:#182632;border:1px solid #2a4050;border-radius:12px;padding:18px;min-height:170px}h1{font-size:22px;margin:0}h2{font-size:16px;margin:0 0 14px}.big{font-size:28px;font-weight:650;margin:6px 0}.stats{display:flex;gap:14px;flex-wrap:wrap}.stats span{display:block}.spark{height:48px;width:100%;margin-top:10px}.badge{color:#b9f3cf}.bad{color:#ff9a9a}
@media(max-width:850px){.grid{grid-template-columns:repeat(2,minmax(220px,1fr))}}@media(max-width:560px){.grid{grid-template-columns:1fr}body{padding:14px}}
</style></head><body><header><div><h1 id="title">Day 13 Monitoring &amp; LLMOps</h1><div class="muted" id="range">Loading dashboard…</div></div><div class="muted" id="updated"></div></header>
<main class="grid">
<article><h2>Latency percentiles and TTFT</h2><div class="stats" id="latency"></div><svg class="spark" id="latency-chart"></svg><div class="muted">Unit: ms · threshold: P95 ≤ 3000 ms</div></article>
<article><h2>Request traffic</h2><div id="traffic"></div><svg class="spark" id="traffic-chart"></svg><div class="muted">Unit: requests/min · 60 minute window</div></article>
<article><h2>Error rate and retrieval success</h2><div id="errors"></div><div class="muted">Error threshold ≤ 2% · retrieval success ≥ 90%</div></article>
<article><h2>Cost over time</h2><div id="cost"></div><svg class="spark" id="cost-chart"></svg><div class="muted">Unit: USD · window total threshold ≤ $2.50</div></article>
<article><h2>Input and output tokens</h2><div id="tokens"></div><svg class="spark" id="tokens-chart"></svg><div class="muted">Unit: tokens · window threshold ≤ 50,000</div></article>
<article><h2>Quality proxy</h2><div id="quality"></div><div class="muted">Unit: score 0–1 · target ≥ 0.75</div></article>
</main><script>
const fmt=(x,d=2)=>x===null||x===undefined?'—':Number(x).toFixed(d);
function bars(id,values){const svg=document.getElementById(id),w=600,h=48,max=Math.max(1,...values);svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.innerHTML=values.map((v,i)=>{let bw=w/values.length-1, bh=Math.max(1,(v/max)*(h-3));return `<rect x="${i*w/values.length}" y="${h-bh}" width="${bw}" height="${bh}" fill="#43c6ac"/>`}).join('')}
function render(d){const p=d.panels;document.getElementById('title').textContent=d.title;document.getElementById('range').textContent=`Last ${d.time_range_minutes} minutes · refresh every ${d.refresh_seconds}s`;
document.getElementById('updated').textContent=`Updated ${new Date(d.updated_at).toLocaleTimeString()}`;
document.getElementById('latency').innerHTML=`<span>P50 <b>${fmt(p.latency.p50_ms)} ms</b></span><span>P95 <b>${fmt(p.latency.p95_ms)} ms</b></span><span>P99 <b>${fmt(p.latency.p99_ms)} ms</b></span><span>TTFT P95 <b>${fmt(p.latency.ttft_p95_ms)} ms</b></span>`;
document.getElementById('traffic').innerHTML=`<div class="big">${p.traffic.requests}</div><div>${fmt(p.traffic.requests_per_minute)} requests/min average</div>`;
document.getElementById('errors').innerHTML=`<div class="stats"><span>Error rate <b class="${p.errors.error_rate_pct>2?'bad':'badge'}">${fmt(p.errors.error_rate_pct)}%</b></span><span>Failed <b>${p.errors.error_count}</b></span><span>Retrieval success <b class="${p.errors.retrieval_success_rate_pct<90?'bad':'badge'}">${fmt(p.errors.retrieval_success_rate_pct)}%</b></span></div>`;
document.getElementById('cost').innerHTML=`<div class="big">$${fmt(p.cost.total_usd,6)}</div><div>sum over window</div>`;
document.getElementById('tokens').innerHTML=`<div class="stats"><span>Input <b>${p.tokens.input.toLocaleString()}</b></span><span>Output <b>${p.tokens.output.toLocaleString()}</b></span></div>`;
document.getElementById('quality').innerHTML=`<div class="big">${fmt(p.quality.mean,3)}</div><div>${p.quality.samples} response samples</div>`;
bars('latency-chart',p.latency.series);bars('traffic-chart',p.traffic.series);bars('cost-chart',p.cost.series);bars('tokens-chart',p.tokens.series)}
async function refresh(){try{const response=await fetch('/dashboard/data',{cache:'no-store'});if(!response.ok)throw new Error(response.status);render(await response.json())}catch(e){document.getElementById('range').textContent='Dashboard data unavailable. Check data/logs.jsonl.'}}
refresh();setInterval(refresh,30000);
</script></body></html>"""
