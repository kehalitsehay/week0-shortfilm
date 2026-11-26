"""Cloudflare Workers AI image generation (FLUX) over REST."""
import base64
import io
from pathlib import Path
import requests
from PIL import Image
from ..core import config


def image(prompt: str, steps: int, seed: int, out: Path) -> dict:
    model = config.image_model()
    acct = config.require("CF_ACCOUNT_ID")
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"
    r = requests.post(url, json={"prompt": prompt, "steps": steps}, timeout=120,
                      headers={"Authorization": f"Bearer {config.require('CF_API_TOKEN')}"})
    r.raise_for_status()
    raw = base64.b64decode(r.json()["result"]["image"])
    Image.open(io.BytesIO(raw)).convert("RGB").save(out, format="PNG")
    # Seed is recorded for our own reproducibility notes; FLUX schnell on Workers AI
    # may ignore it, which EXPERIMENTS.md should test rather than assume.
    return {"model": model, "params": {"steps": steps}, "seed": seed,
            "list_price_usd": config.LIST_PRICE_USD["image"]}
