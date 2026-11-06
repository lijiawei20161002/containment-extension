"""Prepare or run the bounded first E1 stage from containment-decision-story."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.config import load_env
from containment_extension.decision_story import prepare, run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "run"))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--config", type=Path, default=ROOT / "experiments/decision-story-e1-v1.json")
    p.add_argument("--env-file", type=Path)
    p.add_argument("--ca-file", type=Path)
    args = p.parse_args()
    if args.command == "prepare":
        result = prepare(args.output, args.config)
    else:
        load_env(args.env_file)
        if args.ca_file:
            if not args.ca_file.is_file():
                p.error("CA bundle does not exist")
            os.environ["SSL_CERT_FILE"] = str(args.ca_file.resolve())
        result = run(args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
