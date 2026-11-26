"""Load and validate storyboard.json (the contract between all stages)."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from . import config


class StoryboardError(Exception):
    pass


class Storyboard:
    def __init__(self, data: dict):
        self.data = data

    def __getitem__(self, k):
        return self.data[k]

    def get(self, k, default=None):
        return self.data.get(k, default)

    @property
    def shots(self) -> list[dict]:
        return self.data["shots"]

    def shot(self, sid: str) -> dict:
        return next(s for s in self.shots if s["id"] == sid)

    def voice_for(self, speaker: str) -> str:
        return self.data["voices"][speaker]

    def runtime_estimate(self) -> float:
        return sum(s["duration"] for s in self.shots) + self.data["end_card"]["duration"]


def load(path: Path | None = None, validate: bool = True) -> Storyboard:
    path = Path(path or config.STORYBOARD)
    data = json.loads(path.read_text())
    sb = Storyboard(data)
    if validate:
        warnings = check(sb)
        for w in warnings:
            print(f"[storyboard] warning: {w}")
    return sb


def check(sb: Storyboard) -> list[str]:
    """Raise StoryboardError on contract violations; return soft warnings."""
    schema = json.loads(config.SCHEMA.read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(sb.data), key=lambda e: list(e.path))
    if errors:
        msg = "\n".join(f"  - {'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in errors)
        raise StoryboardError("storyboard.json does not match schema:\n" + msg)
    ids = [s["id"] for s in sb.shots]
    if len(ids) != len(set(ids)):
        raise StoryboardError("duplicate shot ids")
    for s in sb.shots:
        for c in s.get("characters", []):
            if c not in sb["characters"]:
                raise StoryboardError(f"shot {s['id']}: unknown character '{c}'")
        if s["narration"]["speaker"] not in sb["voices"]:
            raise StoryboardError(f"shot {s['id']}: no voice for speaker '{s['narration']['speaker']}'")
    warnings = []
    rt = sb.runtime_estimate()
    if not 60 <= rt <= 90:
        warnings.append(f"planned runtime {rt:.0f}s is outside the required 60-90s")
    return warnings
