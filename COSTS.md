# Costs and measurements

Generate the measured table any time with:

```bash
make costs
```

It reads `runs.jsonl` and prints, per stage: model calls, cache hits, total and average seconds, GPU minutes (from `log-manual`), list-price equivalent, errors and fallbacks.

## Measured (paste the output of `make costs` after the real run)

TODO

## Free-tier limits I actually found (check each when you start)

| service | limit observed | date checked |
|---|---|---|
| Gemini API (TTS) | TODO | TODO |
| Cloudflare Workers AI (FLUX) | TODO | TODO |
| Kaggle GPU | TODO | TODO |

## List-price equivalent

`list_price_usd` per call in `pipeline/core/config.py` is an **assumption** (a placeholder, not a quote). Before submitting, replace it with the providers' current published prices and say where you read them here: TODO.

Actual money spent: $0 (free tiers only).

## Frontier comparison

No frontier model access was used. TODO if the cohort gets an organisation key: same shot, open vs frontier, cost and latency.
