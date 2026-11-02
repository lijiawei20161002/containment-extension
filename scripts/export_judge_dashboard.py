"""Export judge-reliability studies into dashboard/judge-data.json; no inference.

Works on partial studies: items with no saved draws are skipped, and metrics are recomputed
from saved draws so a running worker's progress is visible after a refresh.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.judge_reliability import analyze, collect, incident_turn, item_rows  # noqa: E402

DEFAULT_STUDIES = {
    "haiku-4-5": "runs/judge-reliability-v1-haiku-4-5-20261102",
    "sonnet-4-6": "runs/judge-reliability-v1-sonnet-4-6-20261102",
}


def operations(item):
    path = Path(item["path"])
    if item["kind"] == "calibration":
        transcript = json.loads(path.read_text())["transcript"]
    else:
        transcript = json.loads((path.parent / "transcript.json").read_text())
    ops = []
    for event in transcript:
        if "operation" in event:
            result = event["tool_result"]
            ops.append({"op": event["operation"], "status": result.get("status"),
                        "grant": result.get("trusted_grant_for_alternate")})
    return ops


def export_study(name, directory):
    directory = ROOT / directory
    if not (directory / "plan.json").exists():
        return None
    plan = json.loads((directory / "plan.json").read_text())
    config = plan["config"]
    report = analyze(directory, plan)
    for extra in ("worker.json", "budget.json"):
        path = directory / extra
        report[extra.split(".")[0]] = json.loads(path.read_text()) if path.exists() else None
    table = collect(directory, plan)
    per_view = {view: {r["id"]: r for r in item_rows(plan, table, view)} for view in config["views"]}
    items = []
    for item in plan["items"]:
        views = {}
        for view in config["views"]:
            row = per_view[view].get(item["id"])
            if row:
                views[view] = {"draws": row["draws"], "valid": row["valid"], "positives": row["positives"],
                               "score": row["score"], "majority": row["labels"]["majority"],
                               "split": row["split"], "reasons": row["reasons"], "cited": row["cited"]}
        if not views:
            continue
        env = item["environment"] or {}
        items.append({"id": item["id"], "short": item["id"].split("/")[-1], "kind": item["kind"],
                      "cell": {k: env.get(k) for k in ("family", "available", "granted", "seed")},
                      "arm": item["arm"], "truth": item["truth"], "severity": item["severity"],
                      "first_incident_turn": incident_turn(item), "ops": operations(item), "views": views})
    return {"id": name, "dir": str(directory.relative_to(ROOT)), "model": config["model"],
            "draws": config["draws"], "views": config["views"], "status": (report["worker"] or {}).get("status"),
            "judged_items": report["judged_items"], "planned_items": report["planned_items"],
            "budget": report["budget"], "metrics": {v: report["views"][v]["metrics"] for v in config["views"]},
            "failure_cells": {v: report["views"][v]["failure_cells"] for v in config["views"]},
            "cross_view_disagreements": report["cross_view_disagreements"],
            "limitations": report["limitations"], "items": items}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=ROOT / "dashboard/judge-data.json")
    p.add_argument("--study", action="append", metavar="NAME=DIR")
    args = p.parse_args()
    studies = dict(s.split("=", 1) for s in args.study) if args.study else DEFAULT_STUDIES
    archived_path = ROOT / "results/judge-reliability-v1/archived-labels.json"
    data = {"generated_at": datetime.now(timezone.utc).isoformat(),
            "studies": [s for s in (export_study(n, d) for n, d in studies.items()) if s],
            "archived": json.loads(archived_path.read_text()) if archived_path.exists() else {}}
    args.output.write_text(json.dumps(data, indent=1, allow_nan=False) + "\n")
    print(json.dumps({"written": str(args.output), "studies": [(s["id"], s["status"], s["judged_items"])
                                                                for s in data["studies"]],
                      "bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
