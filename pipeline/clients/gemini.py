"""Gemini text-to-speech over plain REST, with rate-limit handling for the free tier."""
import base64
import os
import time
import wave
from pathlib import Path
import requests
from ..core import config

URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_last_call = 0.0


def write_wav(path: Path, pcm: bytes, rate: int = 24000) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)


def _pace() -> None:
    """Keep a minimum gap between calls so the free tier's per-minute limit is not hit."""
    global _last_call
    gap = float(os.environ.get("GEMINI_MIN_INTERVAL", "8"))
    wait = gap - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


def tts(text: str, voice: str, delivery: str | None, out: Path) -> dict:
    model = config.tts_model()
    style = os.environ.get("GEMINI_TTS_STYLE", "off")
    prompt = f"Say {delivery}: {text}" if (delivery and style == "prefix") else text
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    headers = {"x-goog-api-key": config.require("GEMINI_API_KEY")}
    r = None
    for attempt in range(6):
        _pace()
        r = requests.post(URL.format(model=model), json=body, headers=headers, timeout=120)
        if r.status_code != 429:
            break
        wait = 30 * (attempt + 1)
        print(f"[narration] rate limited (429), waiting {wait}s then retrying ({attempt + 1}/6)...")
        time.sleep(wait)
    if r.status_code == 429:
        raise RuntimeError("Gemini keeps returning 429. You may have used up today's free quota. "
                           "Check usage in Google AI Studio, wait, and run the same command again: "
                           "finished lines are cached. Server said: " + r.text[:300])
    if not r.ok:
        raise RuntimeError(f"Gemini TTS error {r.status_code}: {r.text[:300]}")
    part = r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]
    write_wav(out, base64.b64decode(part["data"]))
    return {"model": model, "params": {"voice": voice, "delivery": delivery, "style": style},
            "list_price_usd": config.LIST_PRICE_USD["tts"]}