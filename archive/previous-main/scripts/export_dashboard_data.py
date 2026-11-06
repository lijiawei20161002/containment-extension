"""Collect every algorithm-study cohort under runs/ into one dashboard JSON.

Works on partial cohorts: per-episode results are read directly, and report.json,
selection.json and judge-calibration.json are included when the worker has written them.
Transcripts are condensed to the operation sequence plus the actor's visible text.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def actor_text(assistant):
    parts = []
    for item in assistant or []:
        if item.get("type") == "text":
            parts.append(item.get("text", ""))
        elif item.get("type") == "message":
            parts += [p.get("text", "") for p in item.get("content", []) if p.get("type") == "output_text"]
    return "\n".join(p for p in parts if p).strip()


def condense(transcript):
    steps, pending = [], None
    for event in transcript:
        if "assistant" in event:
            pending = actor_text(event["assistant"])
        else:
            result = dict(event["tool_result"])
            journal = result.pop("verified_effect_journal", None)
            advice = result.pop("planning_advice", None)
            notice = result.pop("journal_audit_notice", None)
            steps.append({"operation": event["operation"], "text": pending or "",
                          "result": result,
                          "journal_shown": None if journal is None else len(journal),
                          "advice": advice["recommended_action"] if advice else None,
                          "notice": notice})
            pending = None
    if pending:
        steps.append({"operation": None, "text": pending, "result": {}, "journal_shown": None,
                      "advice": None, "notice": None})
    return steps


def load_json(path):
    return json.loads(path.read_text()) if path.exists() else None


def recover_actor_turns(directory, plan):
    """Map serial inference records back to episodes.

    The frozen worker stored only OpenAI-shaped assistant output in transcript.json, so
    Anthropic actor text is recovered from the durable inference records: the worker is
    serial, actor calls carry "tools", and each episode's calls are consecutive in plan order.
    Each recovered call is verified against the episode's own tool results.
    """
    records = []
    for path in sorted((directory / "inference").glob("call-*.json")):
        record = load_json(path)
        if record and record.get("status") == "received" and "tools" in record["payload"]:
            records.append(record)
    order = [a["id"] for a in plan["development"]]
    schedule = load_json(directory / "heldout-schedule.json") or []
    order += [a["id"] for a in schedule]
    recovered, cursor = {}, 0
    for identity in order:
        transcript = load_json(directory / "episodes" / identity / "transcript.json")
        if transcript is None:
            continue
        turns = sum("assistant" in e for e in transcript)
        texts = []
        for k in range(turns):
            if cursor >= len(records):
                break
            payload, response = records[cursor]["payload"], records[cursor]["response"]
            messages = payload.get("messages") or payload.get("input") or []
            if k > 0:
                expected = json.dumps(transcript[2 * k - 1]["tool_result"])
                last = messages[-1]
                blob = (last["content"][0]["content"] if isinstance(last.get("content"), list)
                        else last.get("output", ""))
                if blob != expected:
                    break
            content = response.get("content") or response.get("output") or []
            texts.append(actor_text(content))
            cursor += 1
        recovered[identity] = texts
    return recovered


def cohort(directory):
    plan = load_json(directory / "plan.json")
    config = plan["config"]
    labels = {}
    for path in (directory / "judgments").glob("*.json"):
        name = path.stem
        for view in ("transcript_journal", "transcript"):
            if name.endswith("-" + view):
                labels.setdefault(name[: -len(view) - 1], {})[view] = load_json(path).get("incident")
                break
    recovered = recover_actor_turns(directory, plan)
    episodes = []
    for episode in sorted((directory / "episodes").glob("*")):
        result = load_json(episode / "result.json")
        if result is None:
            continue
        transcript = load_json(episode / "transcript.json") or []
        texts = recovered.get(result["id"], [])
        k = 0
        for event in transcript:
            if "assistant" in event and not actor_text(event["assistant"]) and k < len(texts):
                event["assistant"] = [{"type": "text", "text": texts[k]}]
                k += 1
        outcome = result.get("outcome") or {}
        episodes.append({
            "id": result["id"], "phase": result["environment"]["phase"],
            "family": result["environment"]["family"],
            "available": result["environment"]["available"],
            "granted": result["environment"]["granted"],
            "grant_reply": result["environment"].get("grant_reply"),
            "seed": result["environment"]["seed"],
            "candidate": result["candidate"]["id"], "arm": result["candidate"]["arm"],
            "stop_reward": result["candidate"]["stop_reward"],
            "alternate_cost": result["candidate"].get("alternate_cost", 3.0),
            "status": result.get("status"),
            "incident": outcome.get("incident"), "incident_count": outcome.get("incident_count"),
            "first_incident_step": outcome.get("first_incident_step"),
            "repeat_incidents": outcome.get("repeat_incidents"),
            "authorized_completion": outcome.get("authorized_completion"),
            "task_completion": outcome.get("task_completion"),
            "completed_items": outcome.get("completed_items"),
            "utility": outcome.get("utility"), "steps": outcome.get("steps"),
            "terminated_normally": outcome.get("terminated_normally"),
            "operations": [s["operation"] for s in condense(transcript) if s["operation"]],
            "labels": labels.get(result["id"], {}),
            "transcript": condense(transcript),
        })
    progress = load_json(directory / "progress.json") or {}
    worker = load_json(directory / "worker.json") or {}
    budget = load_json(directory / "budget.json") or {}
    return {
        "name": directory.name, "version": config["version"], "model": config["model"],
        "provider": config["provider"], "study": ("eval-awareness" if "eval-awareness" in config["version"]
                                                  else "decision-algorithms"),
        "config": {k: config.get(k) for k in ("stop_rewards", "alternate_costs", "arms", "actor_steps",
                                               "temperature", "request_extra", "grant_probability",
                                               "development_seeds", "heldout_seeds", "scope",
                                               "hypotheses", "notes")},
        "candidates": plan["candidates"],
        "development_assigned": len(plan["development"]),
        "worker": worker, "progress": progress,
        "budget": {k: budget.get(k) for k in ("requests", "estimated_usd", "actual_input_tokens",
                                               "actual_output_tokens", "limits")},
        "report": load_json(directory / "report.json"),
        "selection": load_json(directory / "selection.json"),
        "calibration": load_json(directory / "judge-calibration.json"),
        "theory": plan.get("theory"), "limitations": plan.get("limitations"),
        "episodes": episodes,
    }


def native_cohort(directory):
    """Map a native-fixture algorithm study (native_algorithms.py) onto the cohort schema."""
    plan = load_json(directory / "plan.json")
    config = plan["config"]
    summary = load_json(directory / "summary.json") or {}
    sys.path.insert(0, str(ROOT / "src"))
    from containment_extension.native_algorithms import row_for
    records = {}
    for spec in plan["schedule"]:
        try:
            records[spec["run"]] = row_for(directory, spec)
        except Exception as exc:  # noqa: BLE001 - a half-written run is reported as not started
            records[spec["run"]] = {"stop": "not_started", "error": str(exc)}
    episodes = []
    for spec in plan["schedule"]:
        run = directory / spec["run"]
        row = records.get(spec["run"]) or {}
        result = load_json(run / "result.json")
        transcript, operations = [], []
        if result:
            lines = [json.loads(l) for l in (run / "transcript.jsonl").read_text().splitlines()]
            pending = ""
            for line in lines:
                if "provider_response" in line:
                    pending = actor_text(line["provider_response"].get("content") or line["provider_response"].get("output") or [])
                    if not any(c.get("type") in ("tool_use", "function_call") for c in (line["provider_response"].get("content") or line["provider_response"].get("output") or [])):
                        transcript.append({"operation": None, "text": pending, "result": {}, "journal_shown": None, "advice": None, "notice": None})
                        pending = ""
                elif "tool_result" in line:
                    r = dict(line["tool_result"])
                    journal = r.pop("verified_effect_journal", None)
                    advice = r.pop("planning_advice", None)
                    attempts = load_json(run / "attempts.json") or []
                    seq = len([t for t in transcript if t["operation"]]) + 1
                    label = None
                    prefix = (load_json(run / "manifest.json") or {}).get("checkpoint", {}).get("prefix_actions", 0)
                    a = attempts[prefix + seq - 1] if prefix + seq - 1 < len(attempts) else None
                    if a:
                        act = a["action"]; label = f"{act.get('method', '?')} {act.get('url', act.get('invalid', '?')).replace('https://', '')}"
                        if a.get("scope_label") == "out_of_scope":
                            label = "OUT_OF_SCOPE " + label
                    transcript.append({"operation": label or "request", "text": pending, "result": r,
                                       "journal_shown": None if journal is None else len(journal),
                                       "advice": (advice or {}).get("recommended_action", "").split(":")[0] or None,
                                       "notice": None})
                    operations.append((label or "request").split(" ")[0] if label and label.startswith("OUT_OF_SCOPE") else (label or "request").split(" ")[-1].split("/")[-1][:24])
                    pending = ""
        c = spec["candidate"]
        episodes.append({
            "id": spec["variant"] + "-" + str(spec["seed"]) + "-" + c["id"], "run": spec["run"],
            "phase": "dev", "family": spec["variant"], "available": spec["variant"] != "impossible",
            "granted": False, "grant_reply": spec.get("grant_reply", False), "seed": spec["seed"],
            "candidate": c["id"], "arm": c["arm"], "stop_reward": c["stop_reward"], "alternate_cost": 3.0,
            "status": row.get("stop", "not_started"),
            "incident": row.get("unauthorized_effect"), "incident_count": int(bool(row.get("unauthorized_effect"))),
            "first_incident_step": None, "repeat_incidents": 0,
            "authorized_completion": row.get("authorized_completion"), "task_completion": row.get("task_completed"),
            "completed_items": int(bool(row.get("task_completed"))), "utility": row.get("utility"),
            "steps": row.get("continuation_attempts"), "terminated_normally": row.get("stop") in ("scorer_success", "model_finished"),
            "operations": operations, "labels": {}, "transcript": transcript,
            "attempted_outside": row.get("out_of_scope_proposals"), "asks": row.get("asks"), "scope_blocks": row.get("scope_blocks"),
            "clean_blocker": row.get("blocker_with_observed_evidence")})
    execution = load_json(directory / "execution.json") or {}
    progress = load_json(directory / "progress.json") or {}
    return {"name": directory.name, "version": config["version"], "model": config["actor"]["model"],
            "provider": config["actor"]["provider"], "study": "native-algorithms",
            "config": {"stop_rewards": config["stop_rewards"], "alternate_costs": [3.0], "arms": config["arms"],
                       "actor_steps": 10, "temperature": config["temperature"], "request_extra": None,
                       "grant_probability": 0.0, "development_seeds": config["seeds"]["impossible"],
                       "heldout_seeds": [], "scope": config["scope"], "hypotheses": None, "notes": None},
            "candidates": plan["candidates"], "development_assigned": len(plan["schedule"]),
            "worker": {"status": {"finished": "finished", "running": "running"}.get(execution.get("status"), execution.get("status", "prepared")),
                       "error": execution.get("error")},
            "progress": {"phase": "development", "completed": progress.get("completed", 0), "assigned": len(plan["schedule"])},
            "budget": {"requests": (progress.get("budget") or {}).get("requests"), "estimated_usd": None, "limits": config["budget"]},
            "report": None, "selection": None, "calibration": None, "theory": None,
            "limitations": plan.get("limitations"), "native_summary": {k: v for k, v in summary.items() if k in ("groups", "contrasts", "status")},
            "episodes": episodes}


def e1_archive():
    base = ROOT / "results/decision-story-e1-v1"
    report = load_json(base / "report.json")
    if report is None:
        return None
    with (base / "per-case.csv").open() as f:
        rows = list(csv.DictReader(f))
    return {"report": {k: report[k] for k in ("groups", "model", "scope", "status", "limitations")},
            "budget": report["budget"], "cases": rows}


def agentdojo_runs(runs_dir):
    """Summaries written by scripts/run_agentdojo_grant.py, trimmed for the dashboard."""
    out = []
    for path in sorted(runs_dir.glob("agentdojo-*/summaries/*.json")):
        if "smoke" in path.parts[-3]:
            continue
        d = load_json(path)
        if not d:
            continue
        def trim(block):
            if not block:
                return None
            journal = {k: {x: v[x] for x in ("calls", "blocked", "unauthorized_executed", "requests")}
                       for k, v in block.get("journal", {}).items()}
            return {k: v for k, v in block.items() if k != "journal"} | {"journal": journal}
        out.append({"cohort": path.parts[-3], "suite": d["suite"], "model": d["model"], "arm": d["arm"],
                    "pipeline": d["pipeline"], "attack": d["attack"], "approver": d.get("approver"),
                    "status": d["status"], "error": d.get("error"), "usage": {k: d["usage"].get(k) for k in ("requests", "input_tokens", "output_tokens")},
                    "benign": trim(d.get("benign")), "attacked": trim(d.get("attacked"))})
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", type=Path, default=ROOT / "runs")
    p.add_argument("--pattern", default="*-20261031")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    cohorts = [cohort(d) for d in sorted(args.runs.glob(args.pattern)) if (d / "plan.json").exists() and (d / "source").is_dir() and not (d / "checkpoints").exists()]
    cohorts += [native_cohort(d) for d in sorted(args.runs.glob("native-algorithms-*")) if (d / "plan.json").exists()]
    data = {"generated_at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
            "cohorts": cohorts, "e1": e1_archive(), "agentdojo": agentdojo_runs(args.runs)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, separators=(",", ":")))
    print(json.dumps({"cohorts": [(c["name"], len(c["episodes"]), c["worker"].get("status")) for c in cohorts],
                      "bytes": args.output.stat().st_size}, indent=1))


if __name__ == "__main__":
    main()
