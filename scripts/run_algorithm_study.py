"""Prepare, run, resume, or inspect the local two-algorithm pilot."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.algorithm_study import execute, prepare
from containment_extension.config import load_env


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "run", "status"))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--config", type=Path, default=ROOT / "experiments/decision-algorithms-v1.json")
    p.add_argument("--env-file", type=Path)
    p.add_argument("--ca-file", type=Path)
    args = p.parse_args()
    if args.command == "prepare":
        result = prepare(args.output, args.config)
    elif args.command == "status":
        result = {name: json.loads((args.output / name).read_text())
                  for name in ("worker.json", "progress.json", "budget.json") if (args.output / name).exists()}
    else:
        load_env(args.env_file)
        if args.ca_file:
            os.environ["SSL_CERT_FILE"] = str(args.ca_file.resolve())
        result = execute(args.output)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
