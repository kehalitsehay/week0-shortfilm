"""Stage: assemble. Concatenate shot clips + end card, burn English subtitles, place the
narration, duck the score under the voice, normalise loudness, export 9:16 and 16:9.
Also builds the narration-only 'radio cut' used for the first user test."""
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
from ..core import config, timing
from ..core.stage import Job
from ..clients import ffmpeg
from ..clients.offline import _font
from . import music, narration, shots

ENC = shots.ENC


def _ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def timeline(sb, durs: dict[str, float]) -> list[tuple[str, float, float]]:
    """[(shot_id, start, end)] in seconds."""
    t, out = 0.0, []
    for s in sb.shots:
        out.append((s["id"], t, t + durs[s["id"]]))
        t += durs[s["id"]]
    return out


def write_srt(sb, durs, narr: dict[str, Path], path: Path) -> None:
    lines = []
    for i, (sid, start, _) in enumerate(timeline(sb, durs), 1):
        a = start + timing.NARRATION_LEAD
        b = a + timing.wav_seconds(narr[sid])
        lines.append(f"{i}\n{_ts(a)} --> {_ts(b)}\n{sb.shot(sid)['narration']['text']}\n")
    path.write_text("\n".join(lines))


def audio_graph(sb, durs, first_narr_idx: int, music_idx: int, total: float) -> str:
    tl = timeline(sb, durs)
    parts, labels = [], []
    for i, (_, start, _) in enumerate(tl):
        ms = int((start + timing.NARRATION_LEAD) * 1000)
        parts.append(f"[{first_narr_idx + i}:a]aresample=44100,aformat=channel_layouts=stereo,"
                     f"afade=t=in:d=0.04,areverse,afade=t=in:d=0.12,areverse,adelay={ms}|{ms}[n{i}]")
        labels.append(f"[n{i}]")
    parts.append("".join(labels) + f"amix=inputs={len(tl)}:normalize=0:duration=longest[narr]")
    parts.append(f"[narr]apad=whole_dur={total},asplit=2[nsc][nmix]")
    parts.append(f"[{music_idx}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.6,atrim=duration={total}[mus]")
    parts.append("[mus][nsc]sidechaincompress=threshold=0.02:ratio=10:attack=40:release=600[duck]")
    parts.append(f"[duck][nmix]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=-16:TP=-1.5:LRA=11,"
                 f"apad,atrim=duration={total}[aout]")
    return ";".join(parts)


def end_card_png(sb, w: int, h: int, out: Path) -> None:
    img = Image.new("RGB", (w, h), (14, 20, 30))
    d = ImageDraw.Draw(img)
    d.text((w // 2, int(h * 0.42)), sb["title"], fill=(240, 170, 70), font=_font(int(w * 0.11)), anchor="mm")
    d.text((w // 2, int(h * 0.54)), sb["end_card"]["text"], fill=(235, 235, 235), font=_font(int(w * 0.05)), anchor="mm")
    d.text((w // 2, int(h * 0.62)), "Story, images, voices and music generated with AI models",
           fill=(160, 170, 185), font=_font(int(w * 0.022)), anchor="mm")
    img.save(out)


def _inputs_for_audio(narr_paths: list[Path], score: Path) -> list[str]:
    args = []
    for p in narr_paths:
        args += ["-i", str(p)]
    args += ["-stream_loop", "-1", "-i", str(score)]
    return args


def plan(sb) -> list[Job]:
    narr = narration.playable(sb)
    durs = timing.shot_durations(sb, narr)
    clips = shots.paths(sb)
    score = music.path(sb)
    jobs = []
    for aspect, (w, h) in config.ASPECTS.items():
        # libass sizes are relative to a 288px-tall canvas, so values are small on purpose
        fs, mv = (9, 40) if aspect == "9x16" else (12, 14)
        inputs = {"stage": "assemble", "aspect": aspect, "sub_style": {"size": fs, "margin": mv},
                  "render_version": 2, "clips": [clips[f"{s['id']}_{aspect}"].name for s in sb.shots],
                  "narration": [narr[s["id"]].name for s in sb.shots], "score": score.name, "durations": durs,
                  "end_card": sb["end_card"], "title": sb["title"],
                  "subs": [s["narration"]["text"] for s in sb.shots]}

        def produce(out: Path, aspect=aspect, w=w, h=h, fs=fs, mv=mv):
            work = out.parent / f"_work_{aspect}"
            work.mkdir(parents=True, exist_ok=True)
            end_png, end_mp4 = work / "end.png", work / "end.mp4"
            end_card_png(sb, w, h, end_png)
            ffmpeg.run(["-loop", "1", "-i", str(end_png), "-t", str(sb["end_card"]["duration"]), *ENC, str(end_mp4)])
            lst = work / "list.txt"
            lst.write_text("".join(f"file '{clips[f'{s['id']}_{aspect}'].resolve().as_posix()}'\n" for s in sb.shots)
                           + f"file '{end_mp4.resolve().as_posix()}'\n")
            write_srt(sb, durs, narr, work / "film.srt")
            total = round(sum(durs.values()) + sb["end_card"]["duration"], 2)
            sub = (f"subtitles=film.srt:force_style="
                   f"'FontSize={fs},Outline=1,Shadow=0,MarginV={mv},Alignment=2'")
            n = len(sb.shots)
            graph = f"[0:v]{sub}[vout];" + audio_graph(sb, durs, 1, n + 1, total)
            ffmpeg.run(["-f", "concat", "-safe", "0", "-i", str(lst.resolve()),
                        *_inputs_for_audio([narr[s["id"]] for s in sb.shots], score),
                        "-filter_complex", graph, "-map", "[vout]", "-map", "[aout]",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", str(total), str(out)],
                       cwd=work)
            return {"model": "ffmpeg-assemble", "params": {"aspect": aspect, "total_seconds": total}}

        jobs.append(Job("final", f"film_{aspect}", inputs, "mp4", produce, global_job=True))
    return jobs


def publish(sb) -> list[Path]:
    """Copy the cache-keyed finals to stable names: outputs/film_9x16.mp4 etc."""
    made = []
    for j in plan(sb):
        if j.path.exists():
            dest = config.out() / f"{j.shot}.mp4"
            shutil.copyfile(j.path, dest)
            made.append(dest)
    return made


def radio_job(sb) -> Job:
    narr = narration.playable(sb)
    durs = timing.shot_durations(sb, narr)
    score = music.path(sb)
    inputs = {"stage": "radio", "narration": [narr[s["id"]].name for s in sb.shots], "score": score.name, "durations": durs}

    def produce(out: Path):
        total = round(sum(durs.values()), 2)
        n = len(sb.shots)
        ffmpeg.run(["-f", "lavfi", "-i", f"color=c=black:s=640x360:r=25:d={total}",
                    *_inputs_for_audio([narr[s["id"]] for s in sb.shots], score),
                    "-filter_complex", audio_graph(sb, durs, 1, n + 1, total), "-map", "0:v", "-map", "[aout]",
                    "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-t", str(total), str(out)])
        return {"model": "ffmpeg-radio-cut", "params": {"total_seconds": total}}

    return Job("radio", "radio_cut", inputs, "mp4", produce, global_job=True)
