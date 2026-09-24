from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_env
from .cue_study import run_study, summarize
from .experiment import build_report, run_live, run_scripted, write_json
from .lab import MODES, VARIANTS
from .link_study import run_study as run_link_study, summarize as summarize_link_study
from .incident_study import run_study as run_incident_study, summarize as summarize_incident_study
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
    link = sub.add_parser("link-study", help="Matched README visibility and scope-reminder study")
    link.add_argument("--config", type=Path, required=True)
    link.add_argument("--output", type=Path, required=True)
    link.add_argument("--dry-run", action="store_true")
    link_report = sub.add_parser("link-report", help="Audit link study without inference")
    link_report.add_argument("directory", type=Path)
    incident = sub.add_parser("incident-study", help="Checkpointed scope and accepted-blocker pilot")
    incident.add_argument("--config", type=Path, required=True)
    incident.add_argument("--output", type=Path, required=True)
    incident.add_argument("--dry-run", action="store_true")
    incident_report = sub.add_parser("incident-report", help="Audit incident pilot without inference")
    incident_report.add_argument("directory", type=Path)
    scope = sub.add_parser("scope-study", help="Matched levels of scope instruction specificity")
    scope.add_argument("--config", type=Path, required=True)
    scope.add_argument("--output", type=Path, required=True)
    scope.add_argument("--dry-run", action="store_true")
    scope_report = sub.add_parser("scope-report", help="Audit instruction-level outcomes")
    scope_report.add_argument("directory", type=Path)
    optimize = sub.add_parser("instruction-optimize", help="Bounded grounded instruction search")
    optimize.add_argument("--config", type=Path, required=True)
    optimize.add_argument("--output", type=Path, required=True)
    optimize.add_argument("--dry-run", action="store_true", help="Qualify and preview without inference")
    optimize_report = sub.add_parser("instruction-report", help="Audit an instruction search offline")
    optimize_report.add_argument("directory", type=Path)
    ib_export = sub.add_parser("impossible-export", help="Export pinned Impossible-SWEbench triples")
    ib_export.add_argument("--selection", type=Path, required=True)
    ib_export.add_argument("--output", type=Path, required=True)
    ib_prepare = sub.add_parser("impossible-prepare", help="Freeze a study without inference")
    ib_prepare.add_argument("--bundle", type=Path, required=True)
    ib_prepare.add_argument("--config", type=Path, required=True)
    ib_prepare.add_argument("--output", type=Path, required=True)
    ib_qualify = sub.add_parser("impossible-qualify", help="Scripted Docker controls; no model calls")
    ib_qualify.add_argument("--bundle", type=Path, required=True)
    ib_qualify.add_argument("--output", type=Path, required=True)
    ib_run = sub.add_parser("impossible-run", help="Execute a frozen, qualified Inspect study")
    ib_run.add_argument("directory", type=Path)
    ib_run.add_argument("--qualification", type=Path, required=True)
    ib_report = sub.add_parser("impossible-report", help="Report every assigned ImpossibleBench run")
    ib_report.add_argument("directory", type=Path)
    ib_report.add_argument("--reviews", type=Path, help="Separate evidence-bound review labels")
    ib_preflight = sub.add_parser("impossible-preflight", help="Read-only resource and cached-image checks")
    ib_preflight.add_argument("--output", type=Path, required=True)
    ib_preflight.add_argument("--bundle", type=Path)
    ib_preflight.add_argument("--profile", choices=("fixture", "swebench"))
    ib_catalog = sub.add_parser("impossible-catalog", help="Inventory matched tasks at a pinned revision")
    ib_catalog.add_argument("--revision", required=True)
    ib_catalog.add_argument("--output", type=Path, required=True)
    ib_catalog.add_argument("--cache-dir", type=Path)
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
        elif args.command == "link-study":
            result = run_link_study(args.output, json.loads(args.config.read_text()), dry_run=args.dry_run)
            print(json.dumps({k: v for k, v in result.items() if k not in {"groups", "records"}}, indent=2))
        elif args.command == "link-report":
            print(json.dumps(summarize_link_study(args.directory), indent=2))
        elif args.command == "incident-study":
            result = run_incident_study(args.output, json.loads(args.config.read_text()),
                                        dry_run=args.dry_run)
            print(json.dumps({k: v for k, v in result.items()
                              if k not in {"groups", "records", "contrasts"}}, indent=2))
        elif args.command == "incident-report":
            result = summarize_incident_study(args.directory)
            print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))
        elif args.command in {"scope-study", "scope-report"}:
            from .scope_levels import run_study as run_scope, summarize as scope_summary

            result = (run_scope(args.output, json.loads(args.config.read_text()),
                                dry_run=args.dry_run) if args.command == "scope-study"
                      else scope_summary(args.directory))
            print(json.dumps({k: v for k, v in result.items()
                              if k not in {"records", "comparisons"}}, indent=2))
        elif args.command in {"instruction-optimize", "instruction-report"}:
            from .instruction_optimization.study import run_study as optimize_instructions
            from .instruction_optimization.study import summarize as instruction_summary

            result = (optimize_instructions(args.output, json.loads(args.config.read_text()),
                                            dry_run=args.dry_run)
                      if args.command == "instruction-optimize"
                      else instruction_summary(args.directory))
            print(json.dumps({k: v for k, v in result.items() if k not in {"records", "groups"}},
                             indent=2))
            if result["status"].startswith("stopped_") or result["status"] == "interrupted":
                raise SystemExit(1)
        elif args.command.startswith("impossible-"):
            import asyncio

            from .impossiblebench.study import prepare, summarize as impossible_summary

            if args.command == "impossible-preflight":
                from .impossiblebench.preflight import inspect_resources
                result = inspect_resources(args.output,
                    json.loads(args.bundle.read_text()) if args.bundle else None, profile=args.profile)
                print(json.dumps(result, indent=2))
                if not result["resource_checks_passed"]:
                    parser.exit(1, f"Resource checks failed; inspect {args.output}\n")
                return
            elif args.command == "impossible-catalog":
                from .impossiblebench.catalog import catalog
                result = catalog(args.revision, args.output, cache_dir=args.cache_dir)
                print(json.dumps({k: v for k, v in result.items() if k not in {"tasks", "exclusions"}}, indent=2))
                return
            elif args.command == "impossible-export":
                from .impossiblebench.dataset import export
                result = export(json.loads(args.selection.read_text()), args.output)
            elif args.command == "impossible-prepare":
                result = prepare(args.output, json.loads(args.config.read_text()),
                                 json.loads(args.bundle.read_text()))
            elif args.command == "impossible-qualify":
                from .impossiblebench.qualification import qualify
                result = asyncio.run(qualify(json.loads(args.bundle.read_text()), args.output))
                if not result["passed"]:
                    parser.exit(1, f"Qualification failed; inspect {args.output}/qualification.json\n")
            elif args.command == "impossible-run":
                from .impossiblebench.inspect_adapter import run_study as impossible_run
                result = impossible_run(args.directory, args.qualification)
            else:
                result = impossible_summary(args.directory, args.reviews)
            print(json.dumps({k: v for k, v in result.items()
                              if k not in {"records", "schedule", "checks", "contrasts"}}, indent=2))
        else:
            print(build_report(args.directory))
    except (ValueError, OSError, ProviderError) as exc:
        # Paths may be useful; never print environment or raw HTTP bodies.
        parser.exit(2, f"{type(exc).__name__}: {exc}\n")
