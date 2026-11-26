"""End-to-end proof of the central claim: change one shot, regenerate only that shot."""
import copy
import json
from pathlib import Path
from pipeline import run_all
from pipeline.core import runlog, storyboard
from pipeline.clients import ffmpeg
from .conftest import needs_ffmpeg


def fresh_calls(stage):
    return [r for r in runlog.read_all() if r["stage"] == stage and not r["cache_hit"]]


@needs_ffmpeg
def test_rerun_regenerates_only_the_changed_shot(env):
    sb = storyboard.load()
    run_all.run(sb)
    out = env / "outputs"
    for aspect in ("9x16", "16x9"):
        d = ffmpeg.duration(out / f"film_{aspect}.mp4")
        assert 60 <= d <= 90, d

    n_before = len(runlog.read_all())
    run_all.run(sb)                                       # nothing changed
    new = runlog.read_all()[n_before:]
    assert new and all(r["cache_hit"] for r in new)

    edited = copy.deepcopy(sb.data)                       # change ONE keyframe prompt
    edited["shots"][2]["image_prompt"] += ", a single candle on the table"
    sb2 = storyboard.Storyboard(edited)
    n_before = len(runlog.read_all())
    run_all.run(sb2)
    new = [r for r in runlog.read_all()[n_before:] if not r["cache_hit"]]
    by_stage = {}
    for r in new:
        by_stage.setdefault(r["stage"], []).append(r["shot"])
    assert by_stage["keyframes"] == ["s03"]                       # one new image
    assert sorted(by_stage["shots"]) == ["s03_16x9", "s03_9x16"]   # its two clips
    assert "narration" not in by_stage and "music" not in by_stage
    assert sorted(by_stage["final"]) == ["film_16x9", "film_9x16"]  # re-edit only


@needs_ffmpeg
def test_radio_cut(env):
    sb = storyboard.load()
    dest = run_all.radio(sb)
    assert dest.exists() and ffmpeg.duration(dest) > 30
