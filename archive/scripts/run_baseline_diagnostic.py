"""Prepare, execute once, report or audit the fixed 48-run paired-note diagnostic."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from containment_extension.baseline_diagnostic import (  # noqa: E402
    execute,
    independent_audit,
    prepare,
    report,
)
from containment_extension.config import load_env  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "execute", "report", "audit"])
    parser.add_argument("output", type=Path)
    parser.add_argument("--config", type=Path,
                        default=ROOT / "experiments/baseline-diagnostic-v1.json")
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        result = prepare(args.output, json.loads(args.config.read_text()), ROOT)
    elif args.action == "execute":
        load_env(args.env_file)
        result = execute(args.output)
    elif args.action == "audit":
        result = independent_audit(args.output)
    else:
        result = report(args.output)
    print(json.dumps({k: result[k] for k in ("status", "assigned", "recorded", "budget", "passed")
                      if k in result}, indent=2))
