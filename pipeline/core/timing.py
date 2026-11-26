"""Effective shot durations: never shorter than the storyboard says, never shorter
than the narration plus a breathing pause."""
import wave
from pathlib import Path

NARRATION_LEAD = 0.5   # seconds of picture before the voice starts
NARRATION_TAIL = 0.8   # seconds of picture after the voice ends


def wav_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def shot_durations(sb, narration_paths: dict[str, Path]) -> dict[str, float]:
    out = {}
    for s in sb.shots:
        d = float(s["duration"])
        p = narration_paths.get(s["id"])
        if p and p.exists():
            d = max(d, wav_seconds(p) + NARRATION_LEAD + NARRATION_TAIL)
        out[s["id"]] = round(d, 2)
    return out
