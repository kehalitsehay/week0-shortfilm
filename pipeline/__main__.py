"""CLI: python -m pipeline <command>.  See README.md."""
import argparse
import os
import sys
from pathlib import Path
from .core import config, runlog, storyboard


def main(argv=None) -> int:
    config.load_env()
    p = argparse.ArgumentParser(prog="pipeline", description="Heritage Short pipeline")
    p.add_argument("--storyboard", default=str(config.STORYBOARD))
    p.add_argument("--offline", action="store_true", help="placeholder assets, no keys/network/GPU")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate", help="check storyboard.json against the schema")
    r = sub.add_parser("run", help="run the whole pipeline (cached)")
    r.add_argument("--stage", action="append", help="limit to a stage (repeatable)")
    r.add_argument("--only", action="append", help="limit to a shot id, e.g. s03 (repeatable)")
    r.add_argument("--force", action="store_true", help="ignore the cache")
    sub.add_parser("radio", help="build the narration-only radio cut for user test 1")
    sub.add_parser("smoke", help="call each provider once and log latency")
    sub.add_parser("costs", help="print per-stage latency / GPU / list-price table")
    sub.add_parser("showcase", help="build showcase/index.html")
    m = sub.add_parser("log-manual", help="log work done outside the repo (Kaggle GPU runs)")
    m.add_argument("--stage", required=True)
    m.add_argument("--model", required=True)
    m.add_argument("--minutes", type=float, required=True, help="GPU minutes used")
    m.add_argument("--shot", default="-")
    m.add_argument("--note", default="")
    a = p.parse_args(argv)

    if a.offline:
        os.environ["OFFLINE"] = "1"
    try:
        if a.cmd == "log-manual":
            runlog.log_call(a.stage, a.shot, a.model, latency_ms=a.minutes * 60000, gpu_minutes=a.minutes,
                            params={"note": a.note, "manual": True}, list_price_usd=config.LIST_PRICE_USD["video_clip"])
            print("logged")
            return 0
        if a.cmd == "costs":
            from . import report
            print(report.summarise())
            return 0
        if a.cmd == "smoke":
            from . import smoke
            return smoke.run()
        sb = storyboard.load(Path(a.storyboard))
        if a.cmd == "validate":
            print(f"OK: {len(sb.shots)} shots, planned runtime {sb.runtime_estimate():.0f}s")
        elif a.cmd == "run":
            from . import run_all
            run_all.run(sb, stages=a.stage, only=a.only, force=a.force)
        elif a.cmd == "radio":
            from . import run_all
            run_all.radio(sb)
        elif a.cmd == "showcase":
            from . import showcase
            print(showcase.build(sb))
    except storyboard.StoryboardError as e:
        print(e, file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
