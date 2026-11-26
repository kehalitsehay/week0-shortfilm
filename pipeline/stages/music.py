"""Stage: music. Imports the ACE-Step track you chose on Kaggle (assets/music/score.*),
normalised to 44.1 kHz stereo WAV. If none exists, falls back to an original procedural pad
and records that in runs.jsonl so the fallback is never silent."""
from pathlib import Path
from ..core import cache, config
from ..core.stage import Job
from ..clients import ffmpeg, offline

SCORE_SECONDS = 95


def source() -> Path | None:
    for ext in ("wav", "mp3", "flac", "ogg"):
        p = config.ROOT / "assets" / "music" / f"score.{ext}"
        if p.exists():
            return p
    return None


def plan(sb) -> list[Job]:
    src = None if config.offline() else source()
    inputs = {"stage": "music", "mode": config.mode(), "prompt": sb["music"]["prompt"],
              "source": cache.file_hash(src) if src else None}

    def produce(out: Path):
        if src:
            ffmpeg.run(["-i", str(src), "-ar", "44100", "-ac", "2", str(out)])
            return {"model": "ace-step-1.5 (imported from Kaggle)", "params": {"prompt": sb["music"]["prompt"]},
                    "list_price_usd": config.LIST_PRICE_USD["music"]}
        meta = offline.score(SCORE_SECONDS, out)
        if not config.offline():
            meta["params"]["note"] = "no assets/music/score.* found, used procedural fallback"
        return meta

    return [Job("music", "score", inputs, "wav", produce, global_job=True)]


def path(sb) -> Path:
    return plan(sb)[0].path
