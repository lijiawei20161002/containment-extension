"""Prepare, run once, or report the local information-flow harness."""

import argparse
import json
from pathlib import Path

from containment_extension.config import load_env
from containment_extension.coordination.study import prepare, report, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "report"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=Path("experiments/coordination-harness-v1.json"))
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--approved-cap", type=float, help="New user-authorized total API allocation, set only at preparation")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.output, json.loads(args.config.read_text()), approved_cap=args.approved_cap)
    elif args.command == "run":
        load_env(args.env_file)
        result = run(args.output)
    else:
        result = report(args.output)
    print(json.dumps({k: v for k, v in result.items() if k not in {"actor_records", "monitor_records"}}, indent=2))


if __name__ == "__main__":
    main()
