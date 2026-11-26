"""Stage: narration. One WAV per shot from Gemini TTS (or an offline placeholder)."""
import os
from pathlib import Path
from ..core import config
from ..core.stage import Job
from ..clients import gemini, offline


def plan(sb) -> list[Job]:
    jobs = []
    for s in sb.shots:
        n = s["narration"]
        voice = sb.voice_for(n["speaker"])
        delivery = n.get("delivery")
        style = os.environ.get("GEMINI_TTS_STYLE", "off")
        inputs = {"stage": "narration", "mode": config.mode(), "text": n["text"], "voice": voice,
                  "delivery": delivery if style == "prefix" else None, "style": style,
                  "model": config.tts_model() if not config.offline() else "offline"} 
        def produce(out: Path, n=n, voice=voice, delivery=delivery):
            if config.offline():
                return offline.tts(n["text"], voice, out)
            return gemini.tts(n["text"], voice, delivery, out)

        # No silent fallback here: a placeholder voice in a real film is worse than a loud failure.
        jobs.append(Job("narration", s["id"], inputs, "wav", produce))
    return jobs


def paths(sb) -> dict[str, Path]:
    return {j.shot: j.path for j in plan(sb)}


def playable(sb) -> dict[str, Path]:
    """Cleaned copies of the raw narration (edge bursts/clicks removed). Local, no API."""
    from .. import clean
    from ..core import runlog
    out = {}
    for sid, raw in paths(sb).items():
        if not raw.exists():
            out[sid] = raw
            continue
        dst = config.out() / "narration_clean" / f"{raw.stem}_{clean.CLEAN_VERSION}.wav"
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            info = clean.clean(raw, dst)
            runlog.log_call("narration_clean", sid, model="numpy-trim-" + clean.CLEAN_VERSION,
                            params=info, output=str(dst))
        out[sid] = dst
    return out
