"""The shared job runner. A stage only has to *plan* jobs; this runs them with
caching, retries, optional fallback and logging."""
import time
from dataclasses import dataclass, field
from typing import Callable, Optional
from pathlib import Path

from . import cache, config, runlog
from .retry import retry


@dataclass
class Job:
    stage: str                      # e.g. "keyframes"
    shot: str                       # shot id, or a global name like "score"
    inputs: dict                    # EVERYTHING that influences the output (hashed)
    ext: str                        # output file extension
    produce: Callable[[Path], dict]  # writes the file, returns {model, params, seed, ...}
    fallback: Optional[Callable[[Path], dict]] = None
    global_job: bool = False        # True: runs even when --only filters shots
    group: Optional[str] = None     # shot id this job belongs to (for --only), defaults to `shot`
    sleep: Callable = field(default=time.sleep, repr=False)

    @property
    def key(self) -> str:
        return cache.key(self.inputs)

    @property
    def path(self) -> Path:
        return config.out() / self.stage / f"{self.shot}_{self.key}.{self.ext}"


def execute(jobs: list[Job], only: Optional[list[str]] = None, force: bool = False) -> list[Path]:
    paths = []
    for job in jobs:
        if only and not job.global_job and (job.group or job.shot) not in only:
            paths.append(job.path)
            continue
        path = job.path
        paths.append(path)
        if path.exists() and not force:
            runlog.log_call(job.stage, job.shot, model="cache", cache_hit=True,
                            key=job.key, output=str(path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.stem + ".part." + job.ext)
        t0 = time.time()
        err, used_fallback, meta = None, None, {}
        try:
            meta = retry(lambda: job.produce(tmp), sleep=job.sleep)
        except Exception as e:  # noqa: BLE001 - we log and maybe fall back
            err = f"{type(e).__name__}: {e}"
            if job.fallback is None:
                runlog.log_call(job.stage, job.shot, model="failed", error=err,
                                latency_ms=(time.time() - t0) * 1000, key=job.key)
                raise
            meta = job.fallback(tmp)
            used_fallback = meta.get("model", "fallback")
        tmp.replace(path)
        runlog.log_call(job.stage, job.shot, latency_ms=(time.time() - t0) * 1000,
                        error=err, fallback_used=used_fallback, key=job.key,
                        output=str(path), **meta)
    return paths
