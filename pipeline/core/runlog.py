"""Append-only log: one JSON line per model call (or cache hit)."""
import json
import time
from . import config


def log_call(stage, shot, model, latency_ms=0, params=None, seed=None, cost_usd=0.0,
             list_price_usd=0.0, cache_hit=False, error=None, fallback_used=None,
             key=None, output=None, **extra) -> dict:
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "stage": stage, "shot": shot,
           "model": model, "params": params or {}, "seed": seed, "latency_ms": int(latency_ms),
           "cost_usd": cost_usd, "list_price_usd": list_price_usd, "cache_hit": cache_hit,
           "error": error, "fallback_used": fallback_used, "key": key, "output": output, **extra}
    p = config.runs_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def read_all() -> list[dict]:
    p = config.runs_path()
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
