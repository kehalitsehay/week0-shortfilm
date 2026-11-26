import glob
import json
import os
import shutil
import subprocess
from pathlib import Path


def _candidates(name: str) -> list[str]:
    """Where FFmpeg usually lives on Windows when PATH is not set up in this terminal."""
    exe = name + ".exe"
    home = os.path.expanduser("~")
    local = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
    pats = [
        os.path.join(local, "Microsoft", "WinGet", "Links", exe),
        os.path.join(local, "Microsoft", "WinGet", "Packages", "*FFmpeg*", "**", "bin", exe),
        os.path.join(local, "Microsoft", "WinGet", "Packages", "*ffmpeg*", "**", "bin", exe),
        r"C:\ffmpeg\bin\\" + exe,
        r"C:\Program Files\ffmpeg\bin\\" + exe,
        r"C:\ProgramData\chocolatey\bin\\" + exe,
        os.path.join(home, "scoop", "shims", exe),
        os.path.join(home, "ffmpeg", "bin", exe),
    ]
    found = []
    for p in pats:
        found += glob.glob(p, recursive=True)
    return found


def _bin(name: str) -> str:
    """Find ffmpeg/ffprobe: FFMPEG_DIR, then PATH, then common Windows install folders."""
    d = os.environ.get("FFMPEG_DIR")
    if d:
        for ext in (".exe", ""):
            p = Path(d) / (name + ext)
            if p.exists():
                return str(p)
    found = shutil.which(name)
    if found:
        return found
    for p in _candidates(name):
        if Path(p).exists():
            return p
    raise RuntimeError(
        f"'{name}' was not found by Python. FFmpeg may work in another window but this one "
        f"cannot see it. In the window where 'ffmpeg -version' works, run:  where ffmpeg  "
        f"then here run:  $env:FFMPEG_DIR='<that folder>'  (PowerShell)  or  set FFMPEG_DIR=<that folder>  (cmd).")


def run(args: list[str], cwd: Path | None = None) -> None:
    cmd = [_bin("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()[-800:]}")


def duration(path: Path) -> float:
    r = subprocess.run([_bin("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])
