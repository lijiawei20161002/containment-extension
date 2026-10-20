"""Prepare, execute once, or report the frozen E2 experiment."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from containment_extension.config import load_env  # noqa: E402
from containment_extension.feedback_ablation import execute, prepare, report  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "execute", "report"])
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--config", type=Path, default=ROOT / "experiments/feedback-ablation-v1.json"
    )
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        result = prepare(args.output, json.loads(args.config.read_text()), ROOT)
    elif args.action == "execute":
        load_env(args.env_file)
        result = execute(args.output)
    else:
        result = report(args.output)
    print(
        json.dumps({k: result[k] for k in ("status", "assigned", "recorded", "ceilings")}, indent=2)
    )
