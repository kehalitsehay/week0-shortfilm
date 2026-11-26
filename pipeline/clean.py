"""Non-destructive clean-up of narration WAVs (runs on the raw files, costs no API quota).
Removes the things TTS models tend to leave at clip edges: a short blip or breath after a
gap, a long noisy tail, and hard clicks from abrupt starts/ends."""
import wave
from pathlib import Path
import numpy as np

CLEAN_VERSION = "c2"
FRAME_MS = 20


def read(path: Path):
    with wave.open(str(path), "rb") as w:
        rate, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, rate


def write(path: Path, x: np.ndarray, rate: int) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def segments(x, rate, rel_thresh=0.08, merge_gap_ms=250):
    """Return (list of (start_s, end_s), rms-per-frame, threshold). Speech = frames above
    a threshold relative to the loud part; gaps shorter than merge_gap_ms are bridged."""
    hop = int(rate * FRAME_MS / 1000)
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1)) if n else np.zeros(0)
    if n == 0:
        return [], rms, 0.0
    thr = max(np.percentile(rms, 95) * rel_thresh, 1e-4)
    active = rms > thr
    segs, i = [], 0
    gap = int(merge_gap_ms / FRAME_MS)
    while i < n:
        if active[i]:
            j, last = i, i
            while j < n and (active[j] or j - last <= gap):
                if active[j]:
                    last = j
                j += 1
            segs.append((i * FRAME_MS / 1000, (last + 1) * FRAME_MS / 1000))
            i = last + 1
        else:
            i += 1
    return segs, rms, thr


def cut_end_burst(x, rate, ratio=None, window_s=0.35):
    """TTS ends each line with a short, much LOUDER pop (about 0.16 s, ~3-4x the speech level)
    in the last fraction of a second of the file. Find the first frame in the last `window_s`
    seconds that is `ratio` x louder than the median speech and return where to cut (30 ms
    before it), or None. A real raw clip ends after the speech, so nothing loud should be
    there. Override: CLEAN_FORCE_TRIM_MS=180 always trims a fixed tail; CLEAN_BURST_RATIO tunes."""
    import os
    force = int(os.environ.get("CLEAN_FORCE_TRIM_MS", "0"))
    if force:
        return max(0, len(x) - int(rate * force / 1000))
    ratio = ratio or float(os.environ.get("CLEAN_BURST_RATIO", "2.5"))
    hop = int(rate * 0.01)
    n = len(x) // hop
    if n < 60:
        return None
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1)) + 1e-9
    start = max(10, n - int(window_s * 100))
    body = rms[:start]
    loud = body[body > 0.1 * np.percentile(body, 90)]
    if len(loud) < 5:
        return None
    ref = np.median(loud)
    hits = np.where(rms[start:] > ratio * ref)[0]
    if len(hits) == 0:
        return None
    return max(0, (start + hits[0]) * hop - int(0.03 * rate))


def clean(src: Path, dst: Path, drop_tail_under_s=0.35) -> dict:
    x, rate = read(src)
    info = {"raw_s": round(len(x) / rate, 2), "end_burst_cut": False, "dropped_tail_blips": 0}
    cut = cut_end_burst(x, rate)
    if cut is not None:
        x = x[:cut]
        info["end_burst_cut"] = True
    segs, _, _ = segments(x, rate)
    if not segs:
        write(dst, x, rate)
        return info
    while len(segs) > 1 and (segs[-1][1] - segs[-1][0]) < drop_tail_under_s:
        segs.pop()                       # short blip after a pause = TTS artifact
        info["dropped_tail_blips"] += 1
    a = max(0.0, segs[0][0] - 0.08)
    b = min(len(x) / rate, segs[-1][1] + 0.20)
    y = x[int(a * rate):int(b * rate)].copy()
    fi, fo = int(0.015 * rate), int(0.15 * rate)
    y[:fi] *= np.linspace(0, 1, fi)
    y[-fo:] *= np.linspace(1, 0, min(fo, len(y)))
    write(dst, y, rate)
    info.update(clean_s=round(len(y) / rate, 2), trimmed_start_s=round(a, 2),
                trimmed_end_s=round(len(x) / rate - b, 2))
    return info
