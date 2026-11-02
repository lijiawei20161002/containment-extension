"""Run one AgentDojo suite for one model and one arm, with a spending ceiling.

Writes AgentDojo's own per-task traces under --logdir plus a summary JSON with utility,
security, effect-journal counts and metered usage. Grants are cached under
<logdir>/grants/<model>/ so every arm sees the same grant for a user task.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.config import load_env  # noqa: E402

RATES = {"claude-haiku-4-5-20251001": {"input": 1.0, "output": 5.0},
         "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
         "claude-haiku-5-5": {"input": 0.1, "output": 0.5},
         "claude-sonnet-5": {"input": 2.0, "output": 10.0}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--suite", required=True)
    p.add_argument("--model", required=True, choices=sorted(RATES))
    p.add_argument("--arm", required=True)
    p.add_argument("--attack", default="important_instructions", help="AgentDojo attack name, or 'none' for benign only")
    p.add_argument("--benchmark-version", default="v1.2.2")
    p.add_argument("--user-tasks", default=None, help="comma-separated user task IDs")
    p.add_argument("--injection-tasks", default=None, help="comma-separated injection task IDs")
    p.add_argument("--approver", default="deny", choices=("deny", "approve"))
    p.add_argument("--update", default="none", choices=("none", "narrow"), help="grant_broker only: Progent-style narrowing updates")
    p.add_argument("--generate-grants", action="store_true", help="only generate and cache grants for the suite's user and injection tasks")
    p.add_argument("--grant-version", default="v1", choices=("v1", "v2"), help="v2: read-only tools always allowed")
    p.add_argument("--budget-usd", type=float, required=True)
    p.add_argument("--logdir", type=Path, required=True)
    p.add_argument("--env-file", type=Path, default=Path.home() / "Desktop/.env")
    p.add_argument("--ca-file", type=Path, default=ROOT / ".venv/lib/python3.13/site-packages/certifi/cacert.pem")
    p.add_argument("--benign", action="store_true", help="also run the suite without injections")
    args = p.parse_args()
    load_env(args.env_file)
    if args.ca_file:
        os.environ["SSL_CERT_FILE"] = str(args.ca_file)

    import anthropic
    from agentdojo.attacks.attack_registry import load_attack
    from agentdojo.benchmark import benchmark_suite_with_injections, benchmark_suite_without_injections
    from agentdojo.logging import OutputLogger
    from agentdojo.task_suite.load_suites import get_suite
    from containment_extension.agentdojo_grant import (
        ARMS, BudgetExceeded, GrantStore, JournalCollector, UsageMeter, build_pipeline,
    )
    assert args.arm in ARMS, args.arm

    suite = get_suite(args.benchmark_version, args.suite)
    meter = UsageMeter(RATES[args.model], args.budget_usd)
    collector = JournalCollector()
    store = GrantStore(args.logdir / "grants" / args.model, anthropic.Anthropic(), args.model, meter, version=args.grant_version)
    pipeline = build_pipeline(args.arm, args.model, store, collector, meter, approver=args.approver, update=args.update)
    if args.generate_grants:
        runtime = __import__("agentdojo.functions_runtime", fromlist=["FunctionsRuntime"]).FunctionsRuntime(suite.tools)
        functions = list(runtime.functions.values())
        made = {}
        for task in list(suite.user_tasks.values()) + list(suite.injection_tasks.values()):
            prompt = task.PROMPT if hasattr(task, "PROMPT") else task.GOAL
            grant = store.get(prompt, functions)
            made[task.ID] = grant.describe()
        print(json.dumps({"grants": made, "usage": meter.snapshot()}, indent=1))
        return

    # Tag every run so the executor's journal entries land in the right bucket.
    original = suite.run_task_with_pipeline
    def tagged(agent_pipeline, user_task, injection_task, injections, **kw):
        collector.context = (user_task.ID, injection_task.ID if injection_task else "")
        return original(agent_pipeline, user_task, injection_task, injections, **kw)
    suite.run_task_with_pipeline = tagged

    user_tasks = args.user_tasks.split(",") if args.user_tasks else None
    injection_tasks = args.injection_tasks.split(",") if args.injection_tasks else None
    summary = {"suite": args.suite, "model": args.model, "arm": args.arm, "attack": args.attack,
               "benchmark_version": args.benchmark_version, "pipeline": pipeline.name,
               "approver": args.approver, "started_at": datetime.now(timezone.utc).isoformat(),
               "status": "running", "error": None, "benign": None, "attacked": None}
    out = args.logdir / "summaries" / f"{args.suite}-{pipeline.name}-{args.attack}.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    def journal_stats(keys):
        rows = {}
        for key in keys:
            entries = collector.runs.get(key, [])
            rows["|".join(key)] = {
                "calls": len(entries),
                "blocked": sum(e["decision"] == "blocked" for e in entries),
                "unauthorized_executed": sum(e["decision"] == "executed" and not e["authorized"] for e in entries),
                "requests": sum(e["tool"] == "request_authorization" for e in entries),
                "entries": entries}
        return rows

    try:
        with OutputLogger(str(args.logdir), live=None):
            if args.benign or args.attack == "none":
                results = benchmark_suite_without_injections(pipeline, suite, logdir=args.logdir, force_rerun=False,
                                                             user_tasks=user_tasks, benchmark_version=args.benchmark_version)
                utility = {"|".join(k): v for k, v in results["utility_results"].items()}
                summary["benign"] = {"n": len(utility), "utility": sum(utility.values()),
                                     "per_task": utility, "journal": journal_stats(results["utility_results"])}
                atomic(out, {**summary, "usage": meter.snapshot()})
            if args.attack != "none":
                attack = load_attack(args.attack, suite, pipeline)
                results = benchmark_suite_with_injections(pipeline, suite, attack, logdir=args.logdir, force_rerun=False,
                                                          user_tasks=user_tasks, injection_tasks=injection_tasks,
                                                          benchmark_version=args.benchmark_version)
                utility = {"|".join(k): v for k, v in results["utility_results"].items()}
                security = {"|".join(k): v for k, v in results["security_results"].items()}
                summary["attacked"] = {"n": len(utility), "utility": sum(utility.values()),
                                       "attack_success": sum(security.values()),
                                       "injection_tasks_as_user_tasks": results["injection_tasks_utility_results"],
                                       "per_task_utility": utility, "per_task_security": security,
                                       "journal": journal_stats(results["security_results"])}
        summary["status"] = "finished"
    except BudgetExceeded as exc:
        summary["status"], summary["error"] = "budget_stop", str(exc)
    except Exception as exc:  # noqa: BLE001 - record and re-raise so the caller sees it
        summary["status"], summary["error"] = "error", f"{type(exc).__name__}: {exc}"
        atomic(out, {**summary, "usage": meter.snapshot(), "finished_at": datetime.now(timezone.utc).isoformat()})
        raise
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    atomic(out, {**summary, "usage": meter.snapshot()})
    print(json.dumps({k: summary[k] for k in ("suite", "model", "arm", "attack", "status", "error")}
                     | {"benign": summary["benign"] and {k: summary["benign"][k] for k in ("n", "utility")},
                        "attacked": summary["attacked"] and {k: summary["attacked"][k] for k in ("n", "utility", "attack_success")},
                        "usage": meter.snapshot()}, indent=2))


def atomic(path, value):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, indent=2, default=str))
    os.replace(tmp, path)


if __name__ == "__main__":
    main()
