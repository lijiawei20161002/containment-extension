"""Prepare/run/report frozen latest-model SABench transfer cohorts."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run", "report"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split", choices=["development", "heldout"], default="development")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--arms", nargs="+", choices=["plain", "reminder", "journal", "grant_only", "planner"])
    args = parser.parse_args()
    sys.path.insert(0, str(args.output.resolve() / "source" if args.command != "prepare" else ROOT / "src"))
    from containment_extension.sabench_study import prepare, execute, report
    if args.command == "prepare":
        p = prepare(args.output, args.split, args.arms)
        print(json.dumps({"split": p["split"], "tasks": len(p["task_ids"]), "episodes": len(p["schedule"]),
                          "max_estimated_usd": p["config"]["max_estimated_usd"]}))
    elif args.command == "run":
        from containment_extension.config import load_env
        load_env(ROOT.parent / ".env")
        os.environ["SSL_CERT_FILE"] = str(ROOT / ".venv/lib/python3.13/site-packages/certifi/cacert.pem")
        execute(args.output.resolve(), args.workers)
    else:
        s = report(args.output.resolve())
        print(json.dumps({k: v for k, v in s.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
