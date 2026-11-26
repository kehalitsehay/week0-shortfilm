"""Stage: moving shots. Default is a Ken Burns pan/zoom rendered by FFmpeg (free, instant,
deterministic). If motion is "wan" and a clip from the Kaggle notebook exists at
outputs/wan/<shot>.mp4, that clip is conformed instead. Both aspect ratios are rendered."""
from pathlib import Path
from ..core import cache, config, timing
from ..core.stage import Job
from ..clients import ffmpeg
from . import keyframes, narration

ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(config.FPS)]


def _zoompan(motion: str, n: int) -> tuple[str, str, str]:
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    return {
        "zoom_in": (f"1+0.15*on/{n}", cx, cy),
        "zoom_out": (f"1.15-0.15*on/{n}", cx, cy),
        "pan_left": ("1.15", f"(iw-iw/zoom)*(1-on/{n})", cy),
        "pan_right": ("1.15", f"(iw-iw/zoom)*on/{n}", cy),
    }[motion]


def kenburns(img: Path, out: Path, w: int, h: int, dur: float, motion: str) -> None:
    n = int(round(dur * config.FPS))
    a = round(w / h, 5)
    z, x, y = _zoompan(motion, n)
    vf = (f"crop=w='if(gt(iw/ih,{a}),ih*{a},iw)':h='if(gt(iw/ih,{a}),ih,iw/{a})',"
          f"scale={2 * w}:{2 * h},zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={w}x{h}:fps={config.FPS},format=yuv420p")
    ffmpeg.run(["-i", str(img), "-vf", vf, "-t", f"{dur}", *ENC, str(out)])


def conform(clip: Path, out: Path, w: int, h: int, dur: float) -> None:
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={config.FPS},"
          f"tpad=stop_mode=clone:stop_duration={dur},format=yuv420p")
    ffmpeg.run(["-i", str(clip), "-vf", vf, "-t", f"{dur}", *ENC, str(out)])


def wan_path(shot_id: str) -> Path:
    return config.out() / "wan" / f"{shot_id}.mp4"


def plan(sb) -> list[Job]:
    kf = keyframes.paths(sb)
    durs = timing.shot_durations(sb, narration.playable(sb))
    jobs = []
    for s in sb.shots:
        sid, motion = s["id"], s["motion"]
        wan = wan_path(sid) if motion == "wan" and wan_path(sid).exists() else None
        eff = motion if (motion != "wan" or wan) else "zoom_in"   # missing Wan clip -> Ken Burns
        for aspect, (w, h) in config.ASPECTS.items():
            inputs = {"stage": "shots", "keyframe": kf[sid].name, "motion": eff, "duration": durs[sid],
                      "aspect": aspect, "wan": cache.file_hash(wan) if wan else None}

            def produce(out: Path, sid=sid, w=w, h=h, eff=eff, wan=wan, d=durs[sid]):
                if wan:
                    conform(wan, out, w, h, d)
                    return {"model": "wan2.2-ti2v-5b (imported)", "params": {"conform": f"{w}x{h}"},
                            "list_price_usd": config.LIST_PRICE_USD["video_clip"]}
                kenburns(kf[sid], out, w, h, d, eff)
                return {"model": "ffmpeg-kenburns", "params": {"motion": eff, "size": f"{w}x{h}", "seconds": d}}

            jobs.append(Job("shots", f"{sid}_{aspect}", inputs, "mp4", produce, group=sid))
    return jobs


def paths(sb) -> dict[str, Path]:
    return {j.shot: j.path for j in plan(sb)}
