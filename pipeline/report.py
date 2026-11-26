"""Measurement: summarise runs.jsonl per stage (latency, GPU minutes, list-price equivalent)."""
from collections import defaultdict
from .core import runlog


def summarise() -> str:
    rows = defaultdict(lambda: {"calls": 0, "hits": 0, "ms": 0, "gpu_min": 0.0, "list": 0.0, "errors": 0, "fallbacks": 0})
    for r in runlog.read_all():
        a = rows[r["stage"]]
        if r.get("cache_hit"):
            a["hits"] += 1
            continue
        a["calls"] += 1
        a["ms"] += r.get("latency_ms", 0)
        a["gpu_min"] += r.get("gpu_minutes", 0) or 0
        a["list"] += r.get("list_price_usd", 0) or 0
        a["errors"] += 1 if r.get("error") else 0
        a["fallbacks"] += 1 if r.get("fallback_used") else 0
    lines = ["| stage | model calls | cache hits | total s | avg s/call | GPU min | list-price USD | errors | fallbacks |",
             "|---|---|---|---|---|---|---|---|---|"]
    for st, a in rows.items():
        avg = a["ms"] / a["calls"] / 1000 if a["calls"] else 0
        lines.append(f"| {st} | {a['calls']} | {a['hits']} | {a['ms'] / 1000:.1f} | {avg:.1f} | "
                     f"{a['gpu_min']:.1f} | {a['list']:.3f} | {a['errors']} | {a['fallbacks']} |")
    return "\n".join(lines)
