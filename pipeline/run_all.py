"""Orchestrator: validate -> narration -> keyframes -> music -> shots -> assemble."""
import shutil
from .core import config
from .core.stage import execute
from .stages import assemble, keyframes, music, narration, shots


def run(sb, stages=None, only=None, force=False):
    order = ["narration", "keyframes", "music", "shots", "assemble"]
    want = stages or order
    mods = {"narration": narration, "keyframes": keyframes, "music": music, "shots": shots, "assemble": assemble}
    for name in order:
        if name not in want:
            continue
        print(f"[{name}] ...")
        execute(mods[name].plan(sb), only=only, force=force)   # plan() is called AFTER upstream stages ran
    if "assemble" in want:
        for p in assemble.publish(sb):
            print(f"[done] {p}")


def radio(sb, force=False):
    execute(narration.plan(sb))
    execute(music.plan(sb))
    job = assemble.radio_job(sb)
    execute([job], force=force)
    dest = config.out() / "radio_cut.mp4"
    shutil.copyfile(job.path, dest)
    print(f"[done] {dest}")
    return dest
