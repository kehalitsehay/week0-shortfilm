"""Placeholder generators so the whole pipeline runs with no keys, no network, no GPU.
Used for development, tests, the radio-cut dry run, and as a last-resort fallback."""
import hashlib
import math
import wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .gemini import write_wav


def _font(size: int):
    for p in ("C:/Windows/Fonts/arialbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def image(prompt: str, label: str, seed: int, out: Path, size: int = 1024) -> dict:
    h = int(hashlib.sha256(f"{prompt}{seed}".encode()).hexdigest()[:6], 16)
    top = (20 + h % 40, 30 + (h >> 3) % 50, 60 + (h >> 6) % 80)
    bot = (200 - h % 60, 120 - (h >> 4) % 50, 40 + (h >> 8) % 40)
    y = np.linspace(0, 1, size)[:, None, None]
    arr = (np.array(top) * (1 - y) + np.array(bot) * y) * np.ones((size, size, 3))
    img = Image.fromarray(arr.astype("uint8"))
    d = ImageDraw.Draw(img)
    d.text((size // 2, size // 2 - 30), label, fill="white", font=_font(110), anchor="mm")
    words = prompt.split()
    for i in range(0, min(len(words), 24), 6):
        d.text((size // 2, size // 2 + 50 + 34 * (i // 6)), " ".join(words[i:i + 6]),
               fill=(255, 255, 255), font=_font(26), anchor="mm")
    img.save(out, format="PNG")
    return {"model": "offline-placeholder-image", "params": {}, "seed": seed}


def tts(text: str, voice: str, out: Path) -> dict:
    """A soft 'speech-like' hum: syllable-rate amplitude modulation, ~0.4s per word."""
    rate = 24000
    n = max(1, len(text.split()))
    dur = n * 0.4
    t = np.arange(int(rate * dur)) / rate
    f0 = 110 + (sum(map(ord, voice)) % 80)
    env = 0.5 * (1 + np.sin(2 * math.pi * 2.5 * t)) ** 1.5 / 2.8
    sig = 0.25 * env * (np.sin(2 * math.pi * f0 * t) + 0.4 * np.sin(2 * math.pi * 2 * f0 * t))
    write_wav(out, (sig * 32767).astype("<i2").tobytes(), rate)
    return {"model": "offline-placeholder-tts", "params": {"voice": voice}}


def score(seconds: float, out: Path, rate: int = 44100) -> dict:
    """Original procedural pad over Am-F-C-G, so the film never ships without music."""
    chords = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (261.6, 329.6, 392.0), (196.0, 246.9, 293.7)]
    t = np.arange(int(rate * seconds)) / rate
    seg = 8.0
    sig = np.zeros_like(t)
    for i, chord in enumerate(chords * int(seconds // (seg * 4) + 1)):
        a, b = i * seg, (i + 1) * seg
        if a >= seconds:
            break
        m = (t >= a) & (t < b)
        local = t[m] - a
        env = np.minimum(1, local / 2.0) * np.minimum(1, (seg - local) / 2.0)
        for f in chord:
            sig[m] += env * np.sin(2 * math.pi * f * t[m]) / 3
    sig *= 0.3 * (0.8 + 0.2 * np.sin(2 * math.pi * 0.1 * t))
    pcm = (np.stack([sig, sig], 1) * 32767).astype("<i2")
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return {"model": "offline-procedural-score", "params": {"seconds": seconds}}
