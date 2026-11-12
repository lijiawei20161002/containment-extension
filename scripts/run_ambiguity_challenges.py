"""Prepare, run, or audit matched plain-Astra channel-ambiguity cases."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "prepare-comparison", "run", "report"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--workers", type=int, choices=range(1, 9))
    args = parser.parse_args()
    output = args.output.resolve()
    sys.path.insert(0, str(ROOT / "src" if args.command in {"prepare", "prepare-comparison"} else output / "source"))
    from containment_extension.ambiguity_challenges import prepare, execute, report
    if args.command == "prepare":
        plan = prepare(output)
        print(json.dumps({"assigned": len(plan["schedule"]), "request_ceiling": plan["request_ceiling"]}))
    elif args.command == "prepare-comparison":
        if args.source is None:
            parser.error("--source is required for prepare-comparison")
        from containment_extension.ambiguity_challenges import prepare_comparison
        plan = prepare_comparison(output, args.source)
        print(json.dumps({"assigned": len(plan["schedule"]), "request_ceiling": plan["request_ceiling"]}))
    elif args.command == "run":
        from containment_extension.config import load_env
        import certifi
        load_env(ROOT.parent / ".env")
        os.environ["SSL_CERT_FILE"] = certifi.where()
        execute(output, args.workers)
    else:
        print(json.dumps({k: v for k, v in report(output).items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
