"""Applies the three missing edits for the audio fix. Safe to run more than once."""
from pathlib import Path

st = Path(__file__).parent / "pipeline" / "stages"

PLAYABLE = '''

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
'''

n = st / "narration.py"
s = n.read_text(encoding="utf-8")
if "def playable" not in s:
    n.write_text(s.rstrip() + "\n" + PLAYABLE, encoding="utf-8")
    print("narration.py: added playable()")
else:
    print("narration.py: already has playable()")

for name in ("shots.py", "assemble.py"):
    f = st / name
    s = f.read_text(encoding="utf-8")
    c = s.count("narration.paths(sb)")
    if c:
        f.write_text(s.replace("narration.paths(sb)", "narration.playable(sb)"), encoding="utf-8")
    print(f"{name}: replaced {c} use(s) of narration.paths(sb)")
print("Done. Now run: python diagnose_audio.py")
