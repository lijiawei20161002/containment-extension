"""Export boundary-games studies into dashboard/games-data.json; no inference.

Works on partial studies: every saved episode result is read directly, and the summary is
recomputed from them so a running worker's progress is visible after a refresh.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.boundary_games import summarize  # noqa: E402

DEFAULT_STUDIES = {"haiku-4-5": "runs/boundary-games-v1-haiku-4-5-20261102"}


def actor_text(assistant):
    parts = []
    for item in assistant or []:
        if item.get("type") == "text":
            parts.append(item.get("text", ""))
    return "\n".join(p for p in parts if p).strip()


def steps_of(transcript):
    steps, pending = [], ""
    for event in transcript:
        if "assistant" in event:
            pending = actor_text(event["assistant"])
        else:
            result = dict(event["tool_result"])
            journal = result.pop("verified_effect_journal", None)
            advice = result.pop("planning_advice", None)
            result.pop("journal_audit_notice", None)
            steps.append({"action": event.get("action"), "target": event.get("target"), "text": pending,
                          "status": result.get("status"), "result": result, "render": event.get("render"),
                          "advice": advice and advice.get("recommended_verb"), "journal_shown": None if journal is None else len(journal)})
            pending = ""
    return steps


def export_study(name, directory):
    directory = ROOT / directory
    if not (directory / "plan.json").exists():
        return None
    plan = json.loads((directory / "plan.json").read_text())
    config = plan["config"]
    rows, episodes = [], []
    for assignment in plan["assignments"]:
        folder = directory / "episodes" / assignment["id"]
        saved = folder / "result.json"
        if not saved.exists():
            continue
        result = json.loads(saved.read_text())
        rows.append(result)
        transcript = json.loads((folder / "transcript.json").read_text()) if (folder / "transcript.json").exists() else []
        o = result.get("outcome") or {}
        env = result["environment"]
        episodes.append({"id": result["id"], "game": env["game"], "arm": result["arm"], "available": env["available"],
                         "granted": all(env["grants"].values()), "decoy": env["decoy"], "seed": env["seed"],
                         "status": result["status"], "incident": o.get("incident"), "incident_count": o.get("incident_count"),
                         "first_incident_step": o.get("first_incident_step"), "completed_items": o.get("completed_items"),
                         "authorized_completion": o.get("authorized_completion"), "honest_reports": o.get("honest_reports"),
                         "utility": o.get("utility"), "steps": o.get("steps"), "extra": o.get("extra"),
                         "journal": o.get("journal") or [], "render": result.get("render"), "final_note": o.get("final_note"),
                         "steps_detail": steps_of(transcript)})
    worker = directory / "worker.json"
    budget = directory / "budget.json"
    return {"id": name, "dir": str(directory.relative_to(ROOT)), "model": config["model"], "games": config["games"],
            "arms": config["arms"], "status": json.loads(worker.read_text()).get("status") if worker.exists() else None,
            "completed": len(rows), "assigned": len(plan["assignments"]),
            "budget": json.loads(budget.read_text()) if budget.exists() else None,
            "summary": summarize(rows, config), "tasks": plan["tasks"], "limitations": plan["limitations"], "episodes": episodes}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=ROOT / "dashboard/games-data.json")
    p.add_argument("--study", action="append", metavar="NAME=DIR")
    args = p.parse_args()
    studies = dict(s.split("=", 1) for s in args.study) if args.study else DEFAULT_STUDIES
    data = {"generated_at": datetime.now(timezone.utc).isoformat(),
            "studies": [s for s in (export_study(n, d) for n, d in studies.items()) if s]}
    args.output.write_text(json.dumps(data, indent=1, allow_nan=False) + "\n")
    print(json.dumps({"written": str(args.output), "studies": [(s["id"], s["status"], s["completed"], s["assigned"]) for s in data["studies"]],
                      "bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
