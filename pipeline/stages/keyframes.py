"""Stage: keyframes. Character sheets first, then one still per shot.
Consistency comes from (a) one fixed description per character repeated verbatim in every
prompt, (b) one shared style string, (c) one fixed seed. FLUX schnell is text-only, so there
is no image conditioning; EXPERIMENTS.md should test how well this works."""
from pathlib import Path
from ..core import config
from ..core.stage import Job
from ..clients import cloudflare, offline

STEPS = 4


def shot_prompt(sb, shot: dict) -> str:
    chars = " ".join(sb["characters"][c] + "." for c in shot.get("characters", []))
    return f"{sb['style']}. {chars} {shot['image_prompt']}".strip()


def sheet_prompt(sb, name: str) -> str:
    return (f"{sb['style']}. Character reference sheet, same person shown front view, three-quarter "
            f"view and full body on a plain neutral background: {sb['characters'][name]}")


def _job(stage_id: str, prompt: str, seed: int, label: str, global_job=False) -> Job:
    inputs = {"stage": "keyframes", "mode": config.mode(), "prompt": prompt, "seed": seed, "steps": STEPS,
              "model": config.image_model() if not config.offline() else "offline"}

    def produce(out: Path):
        if config.offline():
            return offline.image(prompt, label, seed, out)
        return cloudflare.image(prompt, STEPS, seed, out)

    return Job("keyframes", stage_id, inputs, "png", produce, global_job=global_job)


def plan(sb) -> list[Job]:
    seed = sb["seed"]
    jobs = [_job(f"sheet_{n}", sheet_prompt(sb, n), seed, n, global_job=True) for n in sb["characters"]]
    jobs += [_job(s["id"], shot_prompt(sb, s), seed, s["id"]) for s in sb.shots]
    return jobs


def paths(sb) -> dict[str, Path]:
    return {j.shot: j.path for j in plan(sb)}
