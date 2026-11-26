"""Call each provider once and log latency. Run this first: it tells you what works."""
import tempfile
import time
from pathlib import Path
from .core import config, runlog
from .clients import cloudflare, ffmpeg, gemini


def run() -> int:
    ok = True
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        checks = [("gemini-tts", lambda: gemini.tts("Hello from the pipeline.", "Charon", None, d / "a.wav")),
                  ("cloudflare-flux", lambda: cloudflare.image("a lit window at night, illustration", 4, 7, d / "i.png"))]
        for name, fn in checks:
            t0 = time.time()
            try:
                meta = fn()
                runlog.log_call("smoke", name, latency_ms=(time.time() - t0) * 1000, **meta)
                print(f"[ok]   {name}: {time.time() - t0:.1f}s")
            except Exception as e:  # noqa: BLE001
                ok = False
                runlog.log_call("smoke", name, model=name, error=str(e), latency_ms=(time.time() - t0) * 1000)
                print(f"[FAIL] {name}: {e}")
    try:
        ffmpeg.run(["-version"])
    except Exception:
        pass
    print("Kaggle (Wan / ACE-Step) cannot be smoke-tested from here: run the notebooks and log with `log-manual`.")
    return 0 if ok else 1
