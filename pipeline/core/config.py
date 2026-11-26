"""Paths, environment and model names. Everything configurable lives here."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORYBOARD = ROOT / "storyboard.json"
SCHEMA = ROOT / "schema" / "storyboard.schema.json"

ASPECTS = {"9x16": (720, 1280), "16x9": (1280, 720)}
FPS = 25

# ASSUMED list prices in USD per call, used only to report "what this would cost
# on a paid plan" in COSTS.md. Verify against the providers' price pages and
# update here; the numbers are placeholders, not quotes.
LIST_PRICE_USD = {"tts": 0, "image": 0, "music": 0, "video_clip": 0}


def load_env() -> None:
    """Tiny .env loader (no dependency). Existing environment variables win."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def out() -> Path:
    return Path(os.environ.get("HS_OUT", ROOT / "outputs"))


def runs_path() -> Path:
    return Path(os.environ.get("HS_RUNS", ROOT / "runs.jsonl"))


def offline() -> bool:
    return os.environ.get("OFFLINE") == "1"


def mode() -> str:
    return "offline" if offline() else "online"


def tts_model() -> str:
    return os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")


def image_model() -> str:
    return os.environ.get("CF_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell")


def require(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing {name}. Copy .env.example to .env and fill it in "
                           f"(or run with --offline for placeholder assets).")
    return v
