"""Prepare, run or replay the Astra/Fable channel algorithm comparison."""
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
    parser.add_argument("--source", type=Path)
    parser.add_argument("--original", type=Path)
    parser.add_argument("--models", nargs="+", choices=["astra", "fable", "terra", "opus"])
    parser.add_argument("--workers", type=int, choices=range(1, 9))
    args = parser.parse_args()
    output = args.output.resolve()
    sys.path.insert(0, str(ROOT / "src" if args.command == "prepare" else output / "source"))
    from containment_extension.channel_algorithms import prepare, execute, report
    if args.command == "prepare":
        if args.source is None or args.original is None:
            parser.error("prepare requires --source and --original")
        plan = prepare(output, args.source, args.original, args.models)
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
