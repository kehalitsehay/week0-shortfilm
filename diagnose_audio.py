"""One-shot health check for the audio fix:  python diagnose_audio.py"""
from pathlib import Path
from pipeline import clean
from pipeline.core import config, storyboard
from pipeline.stages import narration

config.load_env()
sb = storyboard.load()

print("== 1. CURRENT narration files (the ones the film actually uses) ==")
for sid, raw in narration.paths(sb).items():
    if not raw.exists():
        print(f"{sid}: MISSING {raw.name}  (run: python -m pipeline run --stage narration)")
        continue
    x, rate = clean.read(raw)
    cut = clean.cut_end_burst(x, rate)
    dur = len(x) / rate
    print(f"{sid}: {raw.name} {dur:.2f}s  " + ("no end burst detected" if cut is None else
          f"END BURST, {dur - cut / rate:.2f}s will be removed"))

print("\n== 2. is the fix wired into your code? ==")
st = config.ROOT / "pipeline" / "stages"
def has(path, text): return text in path.read_text(encoding="utf-8")
def count(path, text): return path.read_text(encoding="utf-8").count(text)
checks = [
    ("clean.py is the new version (c2)", has(config.ROOT / "pipeline" / "clean.py", 'CLEAN_VERSION = "c2"')),
    ("narration.py has playable()", has(st / "narration.py", "def playable")),
    ("shots.py uses narration.playable", has(st / "shots.py", "narration.playable(sb)") and not has(st / "shots.py", "narration.paths(sb)")),
    ("assemble.py uses narration.playable (twice)", count(st / "assemble.py", "narration.playable(sb)") == 2 and not has(st / "assemble.py", "narration.paths(sb)")),
    ("assemble.py has the music end-of-film fix (apad)", has(st / "assemble.py", "apad=whole_dur")),
]
for name, ok in checks:
    print(("[ok]      " if ok else "[MISSING] ") + name)

print("\n== 3. cleaned files on disk ==")
d = config.out() / "narration_clean"
n = len(list(d.glob("*_c2.wav"))) if d.exists() else 0
print(f"{n} cleaned file(s) in {d}  (expected 8 after a run)")
