"""Audit and summarize one frozen SABench cohort without model calls."""
from collections import Counter, defaultdict
from copy import deepcopy
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import sqlite3
import sys


def binary(rows, field):
    n = len(rows)
    positive = sum(r[field] is True for r in rows)
    missing = sum(r[field] is None for r in rows)
    return {"positive": positive, "incomplete": missing, "assigned": n,
            "bounds": [positive / n, (positive + missing) / n] if n else None}


def percentile(values, q):
    values = sorted(values)
    index = (len(values) - 1) * q
    low = math.floor(index)
    high = math.ceil(index)
    return values[low] * (high - index) + values[high] * (index - low) if high != low else values[low]


def cluster_signflip(sums):
    """Exact signed permutation distribution via integer convolution, not Monte Carlo."""
    sums = [x for x in sums if x]
    if not sums:
        return 1.
    distribution = Counter({0: 1})
    for value in sums:
        nxt = Counter()
        for total, count in distribution.items():
            nxt[total + value] += count
            nxt[total - value] += count
        distribution = nxt
    threshold = abs(sum(sums))
    return sum(n for value, n in distribution.items() if abs(value) >= threshold) / (2 ** len(sums))


def paired(rows, model, right, field, *, left="plain", draws=10000):
    chosen = [r for r in rows if r["model_key"] == model and
              (field != "authorized_completion" or not r["ambiguous"])]
    bank = {(r["task_id"], r["arm"]): r for r in chosen}
    ids = sorted({r["task_id"] for r in chosen})
    deltas, clusters = [], defaultdict(list)
    left_rows, right_rows = [], []
    for task_id in ids:
        a, b = bank.get((task_id, left)), bank.get((task_id, right))
        if not a or not b:
            continue
        left_rows.append(a)
        right_rows.append(b)
        if a[field] is None or b[field] is None:
            continue
        d = int(b[field]) - int(a[field])
        deltas.append(d)
        clusters[a["template_id"]].append(d)
    n = len(left_rows)
    l, r = binary(left_rows, field), binary(right_rows, field)
    bounds = [(r["positive"] - l["positive"] - l["incomplete"]) / n,
              (r["positive"] + r["incomplete"] - l["positive"]) / n] if n else None
    result = {"model_key": model, "left": left, "right": right, "endpoint": field,
        "assigned_pairs": n, "complete_pairs": len(deltas), "templates": len(clusters),
        "right_minus_left": sum(deltas) / len(deltas) if deltas else None,
        "missing_outcome_difference_bounds": bounds, "left_only": deltas.count(-1),
        "right_only": deltas.count(1), "template_clustered_ci95": None,
        "template_signflip_p": None, "mcnemar_descriptive_p": None}
    if not deltas:
        return result
    values = [(sum(ds), len(ds)) for ds in clusters.values()]
    rng = random.Random(20261111)
    bootstrap = []
    for _ in range(draws):
        sample = [rng.choice(values) for _ in values]
        bootstrap.append(sum(v for v, count in sample) / sum(count for v, count in sample))
    result["template_clustered_ci95"] = [percentile(bootstrap, .025), percentile(bootstrap, .975)]
    result["template_signflip_p"] = cluster_signflip([v for v, _ in values])
    discordant = sum(d != 0 for d in deltas)
    smaller = min(deltas.count(-1), deltas.count(1))
    result["mcnemar_descriptive_p"] = min(1., 2 * sum(math.comb(discordant, i) for i in range(smaller + 1)) / 2 ** discordant)
    return result


def holm(contrasts):
    valid = sorted([c for c in contrasts if c["template_signflip_p"] is not None],
                   key=lambda c: c["template_signflip_p"])
    previous = 0.
    for i, c in enumerate(valid):
        adjusted = min(1., max(previous, (len(contrasts) - i) * c["template_signflip_p"]))
        c["holm_primary_p"] = adjusted
        previous = adjusted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    study = args.study.resolve()
    sys.path.insert(0, str(study / "source"))
    from containment_extension.sabench_study import (
        verify, tasks, report, score, APICall, contract_ops, sha, runtime, digest,
        write_operation_from_call,
    )
    from sabench_re.oracle import oracle_verify
    from sabench_re.models import Trace
    plan = verify(study)
    summary = report(study)
    bank = {t.task_id: t for t in tasks()}
    rows, hashes, scopes, mechanism_audit = [], {}, [], []
    api_counts, resolved_models = Counter(), defaultdict(set)
    for spec in plan["schedule"]:
        directory = study / "episodes" / spec["run"]
        result = next(r for r in summary["records"] if r["run"] == spec["run"])
        if (directory / "result.json").exists():
            transcript_path = directory / "transcript.jsonl"
            transcript = [json.loads(line) for line in transcript_path.read_text().splitlines()] if transcript_path.exists() else []
            requests = [e["provider_request"] for e in transcript if "provider_request" in e]
            responses = [e["provider_response"] for e in transcript if "provider_response" in e]
            expected_model = plan["config"]["models"][spec["model_key"]]["model"]
            assert len(requests) <= plan["config"]["max_steps"]
            assert len(responses) <= len(requests)
            assert all(q["model"] == expected_model for q in requests)
            if result["stop"] == "model_finished":
                assert requests and len(requests) == len(responses)
                assert all(r["model"] == expected_model for r in responses)
            if "budget" in result:
                assert result["budget"]["requests"] == len(requests)
                inputs = sum(r["usage"]["input_tokens"] + r["usage"].get("cache_read_input_tokens", 0) +
                             r["usage"].get("cache_creation_input_tokens", 0) for r in responses)
                outputs = sum(r["usage"]["output_tokens"] for r in responses)
                assert inputs == result["budget"]["input_tokens"]
                assert outputs == result["budget"]["output_tokens"]
            api_counts["actor_requests"] += len(requests)
            api_counts["actor_responses"] += len(responses)
            resolved_models[spec["model_key"]].update(r.get("model") for r in responses)
            events_path = directory / "events.jsonl"
            events = [json.loads(line) for line in events_path.read_text().splitlines()] if events_path.exists() else []
            calls = [APICall.from_dict(event["call"]) for event in events]
            database = directory / "effects.sqlite3"
            if database.exists():
                with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as con:
                    committed = con.execute("SELECT seq,api,args,response,state_sha256 FROM calls ORDER BY seq").fetchall()
                assert len(committed) == len(calls), spec["run"]
                state = deepcopy(bank[spec["task_id"]].s0)
                for event, call, (seq, api, encoded_args, response, state_hash) in zip(events, calls, committed):
                    assert seq == call.step + 1
                    assert api == f"{call.tool}_{call.action}" and json.loads(encoded_args) == call.args
                    assert json.loads(response) == event["response"]
                    if plan['config'].get('validate_arguments'):
                        from containment_extension.office_arguments import execute_office_tool
                        actual, replayed_response, state = execute_office_tool(api, call.args, state, seq - 1, validate=True)
                    else:
                        actual, replayed_response, state = runtime.execute_tool_call(api, call.args, state, seq - 1)
                    assert (actual.tool, actual.action, actual.args, actual.success) == (call.tool, call.action, call.args, call.success)
                    assert replayed_response == event["response"]
                    assert digest(state) == state_hash == event["state_sha256"], spec["run"]
                if calls:
                    assert json.loads((directory / "state.json").read_text()) == state
            check = score(bank[spec["task_id"]], calls, result.get("final_response", ""), result["stop"])
            for field in ["incident", "task_goal", "authorized_completion", "oracle"]:
                assert check[field] == result[field], (spec["run"], field)
            contract_path = study / "contracts" / spec["task_id"] / "result.json"
            contract = json.loads(contract_path.read_text()).get("contract") if contract_path.exists() else None
            if contract:
                reference = oracle_verify(bank[spec["task_id"]], Trace(calls=calls))
                inferred = set(contract_ops(contract))
                violations = [call for call in calls if write_operation_from_call(call) in reference.cd]
                correct_warning_delivered = False
                after_warning = 0
                for event, call in zip(events, calls):
                    op = write_operation_from_call(call)
                    if op in reference.cd and correct_warning_delivered:
                        after_warning += 1
                    entries = event["delivered"].get("effect_journal", {}).get("entries", [])
                    for entry in entries:
                        from sabench_re.models import WriteOperation
                        if not entry["within_inferred_scope"] and WriteOperation.from_dict(entry["committed_write"]) in reference.cd:
                            correct_warning_delivered = True
                mechanism_audit.append({"run": spec["run"], "task_id": spec["task_id"],
                    "model_key": spec["model_key"], "arm": spec["arm"],
                    "unauthorized_writes": len(violations),
                    "unauthorized_writes_permitted_by_estimate": sum(write_operation_from_call(c) in inferred for c in violations),
                    "unauthorized_writes_after_correct_journal_warning": after_warning})
        rows.append({key: result.get(key) for key in ["task_id", "template_id", "state_type", "trap_type",
            "ambiguous", "model_key", "arm", "stop", "incident", "task_goal", "authorized_completion",
            "valid_clarification", "unauthorized_write_count", "repeat_write_count", "calls"]})
        if plan['config'].get('validate_arguments'):
            rejected = sum(e['response'].get('error') == 'invalid_arguments' for e in events)
            assert rejected == result.get('argument_rejections', 0)
            rows[-1]['argument_rejections'] = rejected
        hashes[spec["run"]] = {name: sha(directory / name) if (directory / name).exists() else None
            for name in ["result.json", "events.jsonl", "effects.sqlite3", "transcript.jsonl"]}
    for task_id in plan["task_ids"]:
        path = study / "contracts" / task_id / "result.json"
        if not path.exists():
            scopes.append({"task_id": task_id, "status": "missing"})
            continue
        raw = json.loads(path.read_text())
        item = {"task_id": task_id, "status": raw["status"], "sha256": sha(path)}
        for label in ("draft_contract", "contract"):
            contract = raw.get(label)
            if contract is None:
                continue
            t = bank[task_id]
            ops = set(contract_ops(contract))
            calls = [APICall(*runtime.split_api_name(w["tool_name"]), w["arguments"], step=i)
                     for i, w in enumerate(contract["writes"])]
            audit = oracle_verify(t, Trace(calls=calls))
            item[label] = {"exact_explicit_scope": ops == t.A_explicit,
                "needs_clarification": contract["needs_clarification"], "reference_ambiguous": t.is_ambiguous,
                "proposed_unauthorized_writes": len(audit.cd), "omitted_explicit_writes": len(t.A_explicit - ops),
                "reference_goal_met_by_proposed_writes": None if t.is_ambiguous else audit.goal_satisfied}
        scopes.append(item)
    groups = []
    for model in plan["config"]["models"]:
        for arm in plan["config"]["arms"]:
            selected = [r for r in rows if r["model_key"] == model and r["arm"] == arm]
            groups.append({"model_key": model, "arm": arm, "incidents": binary(selected, "incident"),
                "authorized_completion": binary([r for r in selected if not r["ambiguous"]], "authorized_completion"),
                "valid_clarification": binary([r for r in selected if r["ambiguous"]], "valid_clarification"),
                "statuses": dict(Counter(r["stop"] for r in selected)),
                "repeat_effect_episodes": sum((r["repeat_write_count"] or 0) > 0 for r in selected)})
            if plan['config'].get('validate_arguments'):
                groups[-1]['argument_rejections'] = sum(r['argument_rejections'] for r in selected)
                groups[-1]['episodes_with_argument_rejections'] = sum(r['argument_rejections'] > 0 for r in selected)
    contrasts = [paired(rows, model, arm, field) for model in plan["config"]["models"]
        for arm in plan["config"]["arms"] if arm != "plain"
        for field in ["incident", "authorized_completion"]]
    if plan["split"] in {"network_recovery", "interface_regression"}:
        contrasts = []
    primary = [c for c in contrasts if c["right"] == "planner" and c["endpoint"] == "incident"]
    holm(primary)
    if "grant_only" in plan["config"]["arms"] and plan["split"] not in {"network_recovery", "interface_regression"}:
        contrasts += [paired(rows, model, "planner", field, left="grant_only")
            for model in plan["config"]["models"] for field in ["incident", "authorized_completion"]]
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "episodes.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: "" if v is None else str(v).lower() if isinstance(v, bool) else v for k, v in row.items()} for row in rows)
    analyses = {"split": plan["split"], "assigned": len(rows), "groups": groups,
        "contrasts": contrasts, "scope_audit": scopes, "mechanism_audit": mechanism_audit,
        "actor_estimated_usd": summary["actor_estimated_usd"], "scope_estimated_usd": summary["scope_estimated_usd"],
        "requests": summary["requests"], "inference": "Selected provider-error recovery cohort; descriptive outcomes only." if plan["split"] == "network_recovery" else
        "Exact paired template sign-flip; 10,000 paired template bootstrap draws. Primary p-values Holm-adjusted across models."}
    if plan['split'] == 'interface_regression':
        analyses['inference'] = 'Retrospective interface regression on all cached calendar-create/email-send contracts; descriptive outcomes only. Common syntax validation is an environment change, not planner safety benefit.'
    (args.output / "summary.json").write_text(json.dumps(analyses, indent=2) + "\n")
    (args.output / "provenance.json").write_text(json.dumps({"plan_sha256": json.loads((study / "plan.sha256.json").read_text())["sha256"],
        "analysis_code_sha256": sha(Path(__file__)),
        "source_hashes": plan["frozen_hashes"], "evidence_hashes": hashes,
        "episodes_sha256": sha(args.output / "episodes.csv"), "execution": summary["execution"],
        "api_audit": {**api_counts, "resolved_models": {k: sorted(v) for k, v in resolved_models.items()}},
        "network_recovery": plan.get("network_recovery"),
        "config": plan["config"], "limitations": plan["limitations"]}, indent=2) + "\n")
    cell = lambda b: f"{b['positive']}/{b['assigned']} ({b['incomplete']})"
    model_names = {"astra": "GPT-6 Astra", "fable": "Fable 5.2"}
    arm_names = {"plain": "Plain", "reminder": "Scope reminder", "journal": "Effect journal",
                 "grant_only": "Permissions only", "planner": "Planner"}
    lines = ["# SABench transfer results", "", f"Split: {plan['split']}; {len(rows)} assigned episodes.", "",
        "Fractions use all assignments; parentheses count incomplete outcomes. Completion excludes ambiguous tasks.", "",
        "| Model | Arm | Incidents | Authorized completion | Oracle-matched clarification |", "| --- | --- | ---: | ---: | ---: |"]
    for g in groups:
        lines.append(f"| {model_names[g['model_key']]} | {arm_names[g['arm']]} | {cell(g['incidents'])} | {cell(g['authorized_completion'])} | {cell(g['valid_clarification'])} |")
    if primary:
        lines += ["", "Primary comparisons are planner versus plain; development contrasts are exploratory.", "",
            "| Model | Planner − plain (percentage points) | Template-clustered 95% interval | Holm p | Complete pairs |", "| --- | ---: | --- | ---: | ---: |"]
    for c in primary:
        delta = f"{100*c['right_minus_left']:.2f}" if c["right_minus_left"] is not None else "—"
        ci = c["template_clustered_ci95"]
        interval = f"[{100*ci[0]:.2f}, {100*ci[1]:.2f}]" if ci else "—"
        p = c.get("holm_primary_p")
        ptext = f"{p:.4f}" if p is not None else "—"
        lines.append(f"| {model_names[c['model_key']]} | {delta} | {interval} | {ptext} | {c['complete_pairs']}/{c['assigned_pairs']} |")
    if primary:
        lines += ["", "These intervals resample whole templates. The p-values use exact paired template sign-flips; only the two primary comparisons receive Holm correction.", ""]
    for c in primary:
        bounds = c["missing_outcome_difference_bounds"]
        if bounds:
            lines.append(f"{model_names[c['model_key']]}: the all-assignment difference ranges from {100*bounds[0]:.2f} to {100*bounds[1]:.2f} percentage points under all possible missing outcomes. This is a missing-data bound, not a confidence interval.")
    lines += ["", "The permission estimator is fallible and adds inference beyond the actor. Most tasks require one write, so this study offers little evidence about planning depth. Completion checks structural actions, not message quality; clarification uses text matching. Benchmark-defined incidents can reflect annotation errors. Development and held-out outcomes must remain separate."]
    if plan["split"] == "network_recovery":
        lines += ["", "This cohort retries every original provider-error assignment after connectivity checks succeeded. These are separate fresh starts, selected only by failure status. They do not replace original outcomes and do not support a standalone treatment-effect comparison. Original reviewed contracts are reused; no estimator calls or costs are duplicated."]
    if plan['split'] == 'interface_regression':
        lines += ['', analyses['inference'], '', 'Rejected argument attempts (retained separately from committed effects):']
        lines += [f"- {model_names[g['model_key']]} / {arm_names[g['arm']]}: {g['argument_rejections']} rejected calls in {g['episodes_with_argument_rejections']} episodes." for g in groups]
    lines += ["", f"Conservative cost estimate: actors ${summary['actor_estimated_usd']:.2f}; scope inference ${summary['scope_estimated_usd']:.2f}. Not a billing statement.", ""]
    (args.output / "REPORT.md").write_text("\n".join(lines))
    print(json.dumps({k: v for k, v in analyses.items() if k not in {"scope_audit", "mechanism_audit", "contrasts"}}, indent=2))
    print(json.dumps({"primary": primary}, indent=2))


if __name__ == "__main__":
    main()
