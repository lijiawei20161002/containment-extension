from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_env
from .cue_study import run_study, summarize
from .experiment import build_report, run_live, run_scripted, write_json
from .lab import MODES, VARIANTS
from .providers import ProviderError, request_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Contained local incident-analogue experiments")
    parser.add_argument("--env-file", type=Path, help="Explicit dotenv file; never logged or sourced")
    sub = parser.add_subparsers(dest="command", required=True)
    catalog = sub.add_parser("models", help="Query available model IDs (no generation)")
    catalog.add_argument("--provider", choices=("openai", "anthropic"), required=True)
    scripted = sub.add_parser("scripted", help="Positive controls; NOT model behavior")
    scripted.add_argument("--output", type=Path, required=True)
    live = sub.add_parser("run", help="One bounded live model rollout")
    live.add_argument("--provider", choices=("openai", "anthropic"), required=True)
    live.add_argument("--model", required=True)
    live.add_argument("--variant", choices=VARIANTS, default="solvable")
    live.add_argument("--mode", choices=MODES, default="permissive")
    live.add_argument("--seed", type=int, default=0)
    live.add_argument("--max-steps", type=int, default=12)
    live.add_argument("--max-actions", type=int, default=24)
    live.add_argument("--max-output-tokens", type=int, default=768)
    live.add_argument("--output", type=Path, required=True)
    suite = sub.add_parser("suite", help="Run an explicit, versioned pilot matrix")
    suite.add_argument("--config", type=Path, required=True)
    suite.add_argument("--output", type=Path, required=True)
    report = sub.add_parser("report", help="Regenerate a report without making model requests")
    report.add_argument("directory", type=Path)
    cue = sub.add_parser("cue-study", help="Bounded SURF-inspired attribute search and validation")
    cue.add_argument("--config", type=Path, required=True)
    cue.add_argument("--output", type=Path, required=True)
    cue.add_argument("--dry-run", action="store_true")
    cue_report = sub.add_parser("cue-report", help="Rebuild a cue study report without inference")
    cue_report.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        load_env(args.env_file)
        if args.command == "models":
            data = request_json(args.provider, "/models")
            print(json.dumps([m["id"] for m in data["data"]], indent=2))
        elif args.command == "scripted":
            args.output.mkdir(parents=True, exist_ok=False)
            for mode in MODES:
                result = run_scripted(args.output / mode, mode=mode)
                print(mode, json.dumps(result), flush=True)
            build_report(args.output)
        elif args.command == "run":
            result = run_live(args.output, provider=args.provider, model=args.model,
                              variant=args.variant, mode=args.mode, seed=args.seed,
                              max_steps=args.max_steps, max_actions=args.max_actions,
                              max_output_tokens=args.max_output_tokens)
            print(json.dumps(result, indent=2))
            if result["error"]:
                raise SystemExit(1)
        elif args.command == "suite":
            config = json.loads(args.config.read_text())
            args.output.mkdir(parents=True, exist_ok=False)
            write_json(args.output / "plan.json", config)
            failed = False
            for i, model in enumerate(config["models"]):
                for variant in config["variants"]:
                    for seed in config["seeds"]:
                        for mode in config["modes"]:
                            name = f"model-{i + 1}_{variant}_{mode}_seed-{seed}"
                            print(f"Starting {name}: {model['model']}", flush=True)
                            result = run_live(args.output / name, **model, variant=variant,
                                              mode=mode, seed=seed, **config["limits"])
                            failed |= result["error"] is not None
                            print(json.dumps({"run": name, **result}), flush=True)
                            build_report(args.output)
            if failed:
                raise SystemExit(1)
        elif args.command == "cue-study":
            result = run_study(args.output, json.loads(args.config.read_text()), dry_run=args.dry_run)
            print(json.dumps({k: v for k, v in result.items()
                              if k not in {"ranking", "groups", "validation_contrasts"}}, indent=2))
        elif args.command == "cue-report":
            print(json.dumps(summarize(args.directory), indent=2))
        else:
            print(build_report(args.directory))
    except (ValueError, OSError, ProviderError) as exc:
        # Paths may be useful; never print environment or raw HTTP bodies.
        parser.exit(2, f"{type(exc).__name__}: {exc}\n")
