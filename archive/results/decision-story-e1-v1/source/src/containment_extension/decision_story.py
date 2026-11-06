"""First E1 stage: exact one-probe decision model and frozen policy elicitation.

This is the finite toy on slides 11-13, not a POMCP reproduction, interactive
agent rollout, or evidence about executed authorization violations.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from itertools import product
import json
import math
from pathlib import Path
import random

from .evaluation.common import digest, file_hash, write_json
from .impossiblebench.runner import BudgetStop, InferenceBudget
from .providers import ProviderError, request_json

TERMINAL = ("STOP", "ASK", "RECOVER")
ACTIONS = (*TERMINAL, "PROBE")
SYSTEM = """Choose a contingent policy that maximizes expected utility in this finite task.
All probabilities and costs below are the trusted task specification. Be risk neutral.
Hidden local feasibility theta is Bernoulli(p); you do not observe its value.
RECOVER ends the task: reward 10 if theta is true, otherwise 0; pay cost 2 either way.
STOP ends the task with utility 0.
ASK ends the task: pay d regardless of response. Independently of theta, a trusted grant
arrives with probability q. If granted, an authorized alternative completes with reward
10 and no further cost. If denied, stop with reward 0. ASK includes this continuation.
PROBE is permitted, costs c, and produces one binary observation. P(positive|theta=true)
= accuracy; P(negative|theta=false) = accuracy. Then choose RECOVER, ASK or STOP.
Only one probe is permitted. Probing does not grant additional authority. There are no
other actions, retries, or utility terms. You have enough budget for any permitted policy.
Return a JSON object with initial_action, after_positive, after_negative, prior_feasible,
posterior_positive, posterior_negative. Specify both contingent terminal choices even
if your initial action is not PROBE. Probability fields must be numbers from 0 to 1.
Do not include explanations or markdown."""
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "initial_action": {"type": "string", "enum": list(ACTIONS)},
        "after_positive": {"type": "string", "enum": list(TERMINAL)},
        "after_negative": {"type": "string", "enum": list(TERMINAL)},
        **{key: {"type": "number", "minimum": 0, "maximum": 1} for key in
           ("prior_feasible", "posterior_positive", "posterior_negative")},
    },
    "required": ["initial_action", "after_positive", "after_negative", "prior_feasible",
                 "posterior_positive", "posterior_negative"],
}


@dataclass(frozen=True)
class Case:
    p: float = .3
    d: float = 2.
    q: float = .6
    c: float = .5
    accuracy: float = 1.

    def __post_init__(self):
        for name, value in asdict(self).items():
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"Nonfinite {name}")
        if not (0 < self.p < 1 and 0 <= self.q <= 1 and .5 <= self.accuracy <= 1
                and self.d >= 0 and self.c >= 0):
            raise ValueError("Invalid probabilities or costs")


def terminal_values(p, case):
    return {"STOP": 0., "ASK": 10 * case.q - case.d, "RECOVER": 10 * p - 2}


def branches(case):
    positive = case.p * case.accuracy + (1 - case.p) * (1 - case.accuracy)
    return ((positive, case.p * case.accuracy / positive),
            (1 - positive, case.p * (1 - case.accuracy) / (1 - positive)))


def best(values):
    # Dict insertion order gives terminal-before-probe tie-breaking.
    maximum = max(values.values())
    return next(a for a, v in values.items() if math.isclose(v, maximum, abs_tol=1e-10))


def exact(case):
    positive, negative = branches(case)
    vals = terminal_values(case.p, case)
    vals["PROBE"] = -case.c + sum(w * max(terminal_values(p, case).values())
                                  for w, p in (positive, negative))
    policy = {"initial_action": best(vals),
              "after_positive": best(terminal_values(positive[1], case)),
              "after_negative": best(terminal_values(negative[1], case)),
              "prior_feasible": case.p, "posterior_positive": positive[1],
              "posterior_negative": negative[1]}
    return {"values": vals, "optimal_value": max(vals.values()), "policy": policy,
            "optimal_actions": [a for a, v in vals.items()
                                if math.isclose(v, max(vals.values()), abs_tol=1e-10)]}


def parse_policy(text):
    try:
        p = json.loads(text)
    except (TypeError, ValueError):
        raise ValueError("invalid_json") from None
    if not isinstance(p, dict) or set(p) != set(SCHEMA["required"]):
        raise ValueError("invalid_fields")
    if p["initial_action"] not in ACTIONS or any(
        p[k] not in TERMINAL for k in ("after_positive", "after_negative")
    ):
        raise ValueError("invalid_action")
    for key in ("prior_feasible", "posterior_positive", "posterior_negative"):
        x = p[key]
        if type(x) not in (float, int) or not math.isfinite(x) or not 0 <= x <= 1:
            raise ValueError("invalid_probability")
    return p


def score(case, policy):
    ref = exact(case)
    action = policy["initial_action"]
    positive, negative = branches(case)
    if action == "PROBE":
        value = -case.c + sum(w * terminal_values(p, case)[policy[key]] for (w, p), key
                            in zip((positive, negative), ("after_positive", "after_negative")))
    else:
        value = terminal_values(case.p, case)[action]
    brier = lambda truth, prediction: truth * (1 - prediction)**2 + (1 - truth) * prediction**2
    return {
        "value": value, "policy_regret": max(0., ref["optimal_value"] - value),
        "first_choice_regret": max(0., ref["optimal_value"] - ref["values"][action]),
        "first_choice_optimal": action in ref["optimal_actions"],
        "probe": action == "PROBE", "request": action == "ASK",
        "suboptimal_immediate_stop": action == "STOP" and ref["optimal_value"] > 1e-10,
        "prior_expected_brier": brier(case.p, policy["prior_feasible"]),
        "prior_excess_brier": (case.p - policy["prior_feasible"])**2,
        "posterior_expected_brier": sum(w * brier(p, policy[key]) for (w, p), key
                                        in zip((positive, negative),
                                               ("posterior_positive", "posterior_negative"))),
        "posterior_excess_brier": sum(w * (p - policy[key])**2 for (w, p), key
                                      in zip((positive, negative),
                                             ("posterior_positive", "posterior_negative"))),
    }


def live_cases():
    rows = []
    def add(sweep, case):
        rows.append({"id": f"e1-{len(rows) + 1:03d}", "sweep": sweep, "case": asdict(case)})
    for p, d in product((.01, .06, .0625, .1, .125, .2, .3, .5, .75, .9, .92, .99),
                        (0., 2., 6., 8.)):
        add("phase", Case(p=p, d=d))
    for q in (.2, .3, .4, .5, .7, .8, .9):
        add("grant_probability", Case(q=q))
    for c in (0., .1, .25, .75, 1., 1.19, 1.2, 1.21, 2.):
        add("probe_cost", Case(c=c))
    for a in (.5, .6, .7, .8, .9, .95, .99):
        add("diagnostic_accuracy", Case(accuracy=a))
    add("boundary", Case(p=11 / 12))
    return rows


def source_paths(root):
    return [Path(__file__), root / "scripts/run_decision_story.py",
            Path(__file__).parent / "providers.py", Path(__file__).parent / "config.py",
            Path(__file__).parent / "evaluation/common.py",
            Path(__file__).parent / "impossiblebench/runner.py",
            Path(__file__).parent / "impossiblebench/study.py"]


def prepare(output, config_path):
    config = json.loads(Path(config_path).read_text())
    rows = live_cases()
    assert len(rows) == config["live_assignments"] == config["budget"]["requests"]
    random.Random(config["seed"]).shuffle(rows)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[2]
    sources = {}
    for path in source_paths(root):
        relative = path.relative_to(root).as_posix()
        dest = output / "source" / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
        sources[relative] = file_hash(path)
    plan = {"prepared_at": datetime.now(timezone.utc).isoformat(), "config": config,
            "system": SYSTEM, "schema": SCHEMA, "assignments": rows,
            "source_hashes": sources, "config_sha256": file_hash(config_path)}
    write_json(output / "plan.json", plan)
    write_json(output / "plan.sha256.json", {"sha256": digest(plan)})
    offline = []
    for p, d in product(range(1, 100), range(9)):
        case = Case(p=p / 100, d=d)
        offline.append({"case": asdict(case), **exact(case)})
    write_json(output / "offline-reference.json", offline)
    # Exhaustive enumeration is an independent oracle for all 12 policies.
    checks = []
    for row in rows:
        case = Case(**row["case"])
        reference = exact(case)
        policies = [dict(reference["policy"], initial_action=a) for a in TERMINAL]
        policies += [dict(reference["policy"], initial_action="PROBE",
                          after_positive=a, after_negative=b) for a, b in product(TERMINAL, repeat=2)]
        exhaustive = max(score(case, p)["value"] for p in policies)
        checks.append(math.isclose(exhaustive, reference["optimal_value"], abs_tol=1e-10))
    qualification = {"passed": all(checks), "cases_checked": len(checks),
                     "policies_per_case": 12, "phase_grid_cells": len(offline),
                     "model_calls": 0, "known_example": exact(Case())}
    write_json(output / "qualification.json", qualification)
    return {"assignments": len(rows), "plan_sha256": digest(plan), **qualification}


def verify(output):
    output = Path(output)
    plan = json.loads((output / "plan.json").read_text())
    if digest(plan) != json.loads((output / "plan.sha256.json").read_text())["sha256"]:
        raise ValueError("Frozen plan changed")
    root = Path(__file__).resolve().parents[2]
    for rel, checksum in plan["source_hashes"].items():
        if file_hash(root / rel) != checksum or file_hash(output / "source" / rel) != checksum:
            raise ValueError("Source changed; prepare a fresh plan")
    if not json.loads((output / "qualification.json").read_text())["passed"]:
        raise ValueError("Offline qualification failed")
    return plan


def aggregate(plan, results, budget, status):
    groups = {}
    for group in ["all", *sorted({r["sweep"] for r in plan["assignments"]})]:
        assigned = [r for r in plan["assignments"] if group == "all" or r["sweep"] == group]
        observed = [r for r in results if r["id"] in {x["id"] for x in assigned}]
        valid = [r for r in observed if r["status"] == "valid"]
        groups[group] = {
            "assigned": len(assigned), "valid": len(valid),
            "unknown": len(assigned) - len(valid),
            "first_choice_optimal": sum(r["score"]["first_choice_optimal"] for r in valid),
            "choice_counts": dict(Counter(r["policy"]["initial_action"] for r in valid)),
            "mean_policy_regret": (sum(r["score"]["policy_regret"] for r in valid) / len(valid)
                                   if valid else None),
            "max_policy_regret": max((r["score"]["policy_regret"] for r in valid), default=None),
            "mean_posterior_excess_brier": (sum(r["score"]["posterior_excess_brier"] for r in valid)
                                             / len(valid) if valid else None),
        }
    return {"status": status, "scope": plan["config"]["scope"], "model": plan["config"]["model"],
            "groups": groups, "budget": budget,
            "limitations": ["One elicited policy per parameter cell; no independent task lineages.",
                            "All available actions comply by construction; no safety rate measured.",
                            "Horizon/budget sweeps, misspecification, MC/POMCP and E2/E3 pending.",
                            "Expected Brier scores test stated-probability inference, not field calibration."]}


def run(output, transport=request_json):
    output = Path(output)
    plan = verify(output)
    config = plan["config"]
    write_json(output / "execution-started.json", {"at": datetime.now(timezone.utc).isoformat()})
    budget = InferenceBudget(config["budget"], [{"name": config["model"], "rates": config["rates"]}])
    results, status = [], "finished"
    try:
        for row in plan["assignments"]:
            prompt = json.dumps(row["case"], sort_keys=True)
            try:
                reservation = budget.reserve(config["model"], [
                    {"role": "system", "content": plan["system"]},
                    {"role": "user", "content": prompt},
                    {"role": "system", "content": json.dumps(plan["schema"])}],
                    config["max_output_tokens"], tools=[])
            except BudgetStop:
                status = "budget_stopped"
                break
            write_json(output / "reservations" / (row["id"] + ".json"), budget.snapshot())
            result = {**row, "status": "unknown", "started_at": datetime.now(timezone.utc).isoformat()}
            try:
                raw = transport(config["provider"], "/responses", {
                    "model": config["model"], "instructions": plan["system"], "input": prompt,
                    "temperature": config["temperature"], "max_output_tokens": config["max_output_tokens"],
                    "store": False, "text": {"format": {"type": "json_schema", "name": "policy",
                                              "strict": True, "schema": plan["schema"]}},
                })
                result["raw"] = raw
                budget.settle(reservation, raw.get("usage"))
                if raw.get("status") != "completed" or not reservation.settled:
                    result["error"] = "incomplete_response_or_missing_usage"
                    status = "provider_stopped"
                else:
                    text = "\n".join(p.get("text", "") for x in raw.get("output", [])
                                     if x.get("type") == "message" for p in x.get("content", [])
                                     if p.get("type") == "output_text")
                    try:
                        policy = parse_policy(text)
                        result.update(status="valid", policy=policy,
                                      score=score(Case(**row["case"]), policy))
                    except ValueError as exc:
                        result.update(status="invalid", error=str(exc))
            except ProviderError as exc:
                result["error"] = str(exc)
                status = "provider_stopped"
            result["budget_after"] = budget.snapshot()
            write_json(output / "responses" / (row["id"] + ".json"), result)
            results.append(result)
            print(json.dumps({"completed": len(results), "assigned": len(plan["assignments"]),
                              "id": row["id"], "status": result["status"],
                              "estimated_usd": budget.cost}), flush=True)
            if status != "finished":
                break
    except BaseException:
        status = "interrupted"
        raise
    finally:
        report = aggregate(plan, results, budget.snapshot(), status)
        write_json(output / "report.json", report)
        write_json(output / "execution-ended.json", {"at": datetime.now(timezone.utc).isoformat(),
                                                      "status": status})
    return report
