"""Prepare, run or replay the channel follow-up allocations.

prepare-mechanism     wording-by-topic and advice delivery, Astra and Terra
prepare-mechanism-anthropic  the mechanism allocation on Fable and Opus through OpenRouter
prepare-older-model   Haiku 4.5 on the unchanged tasks and arms
run / report          execute or replay a prepared allocation from its frozen source
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["prepare-mechanism", "prepare-mechanism-anthropic", "prepare-older-model", "run", "report"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path, help="finished channel-algorithms allocation (prepare only)")
    parser.add_argument("--workers", type=int, choices=range(1, 9))
    parser.add_argument("--route", choices=["anthropic", "openrouter"], default="anthropic",
                        help="provider path for prepare-older-model")
    args = parser.parse_args()
    output = args.output.resolve()
    preparing = args.command.startswith("prepare")
    sys.path.insert(0, str(ROOT / "src" if preparing else output / "source"))
    from containment_extension import channel_followups as study
    if preparing:
        if args.source is None:
            parser.error("prepare requires --source")
        if args.command == "prepare-mechanism":
            plan = study.prepare_mechanism(output, args.source)
        elif args.command == "prepare-mechanism-anthropic":
            plan = study.prepare_mechanism_anthropic(output, args.source)
        else:
            plan = study.prepare_older_model(output, args.source, route=args.route)
        print(json.dumps({"version": plan["version"], "assigned": len(plan["schedule"]),
                          "request_ceiling": plan["request_ceiling"], "fresh_scope_tasks": len(plan["fresh_scope_tasks"])}))
    elif args.command == "run":
        from containment_extension.config import load_env
        import certifi
        load_env(ROOT.parent / ".env")
        os.environ["SSL_CERT_FILE"] = certifi.where()
        study.execute(output, args.workers)
    else:
        summary = study.report(output)
        print(json.dumps({k: v for k, v in summary.items() if k not in {"records", "groups"}}, indent=2))


if __name__ == "__main__":
    main()
