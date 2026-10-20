"""Collect only observed hosted-model evidence for the paper deck; no demonstrations."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def collect():
    sources = set()

    def read(name):
        sources.add(name)
        return json.loads((REPO / name).read_text())

    historical = read("results/incident-study-v1/summary.json")
    diagnostic = read("results/baseline-diagnostic-v2/summary.json")
    interrupted = read("results/baseline-diagnostic-v1/summary.json")
    assert read("results/baseline-diagnostic-v1/independent-audit.json")["passed"]
    judge = read("results/transcript-audit-v4/summary.json")
    raw_fields = read("results/transcript-audit-v4/raw-field-audit.json")
    failed_judges = {v: read(f"results/transcript-audit-{v}/summary.json")
                     for v in ("v2", "v3")}
    for study in ("baseline-diagnostic-v2", "transcript-audit-v2",
                  "transcript-audit-v3", "transcript-audit-v4"):
        assert read(f"results/{study}/independent-audit.json")["passed"]
        read(f"results/{study}/plan.json")
    assert diagnostic["status"] == "finished" and diagnostic["recorded"] == 48
    assert judge["status"] == "finished" and judge["recorded"] == 68
    assert judge["diagnostic_only"] and not judge["calibration_passed"]
    assert judge["budget"]["requests"] == 56
    assert all(j["status"] == "calibration_or_integrity_failed" for j in failed_judges.values())
    old_counts = Counter((r["stop"] == "scorer_success", bool(r["any_effect"]))
                         for r in historical["records"])
    assert len(historical["records"]) == 160
    assert all(r["any_effect"] in (0, 1) for r in historical["records"])
    cross_tab = {"pass_incident": old_counts[True, True],
                 "pass_no_incident": old_counts[True, False],
                 "no_pass_incident": old_counts[False, True],
                 "no_pass_no_incident": old_counts[False, False]}
    assert cross_tab == {"pass_incident": 13, "pass_no_incident": 96,
                         "no_pass_incident": 2, "no_pass_no_incident": 49}
    trace_folders = ["results/incident-study-v1/run-0001", "results/incident-study-v1/run-0094",
                     "results/feedback-ablation-v1/run-0001",
                     "results/feedback-ablation-v1/run-0002"]
    # The first completed input pair is shown without selecting for its outcome.
    trace_folders += [f"results/baseline-diagnostic-v2/{r['run']}"
                      for r in diagnostic["records"][:2]]
    traces = {}
    for folder in trace_folders:
        result = read(f"{folder}/result.json")
        assert result["kind"] == "live"
        name = f"{folder}/transcript.jsonl"
        sources.add(name)
        calls, by_id = [], {}
        for line in (REPO / name).read_text().splitlines():
            event = json.loads(line)
            for block in event.get("provider_response", {}).get("content", []):
                if block["type"] == "tool_use":
                    turn = {"step": event["step"], "call_id": block["id"],
                            "action": block["input"]}
                    calls.append(turn)
                    by_id[block["id"]] = turn
            if "tool_result" in event:
                by_id[event["call_id"]]["result"] = event["tool_result"]
        traces[folder] = {"calls": calls, "stop": result["stop_reason"],
                          "final_text": result["final_text"],
                          "incident": result["unauthorized_effect"],
                          "task_completed": result["task_completed"]}
    assert traces[trace_folders[0]]["calls"][2]["action"]["url"].endswith("run-prior/solution")
    assert traces[trace_folders[0]]["calls"][-1]["result"]["correct"]
    assert traces[trace_folders[1]]["incident"] and not traces[trace_folders[1]]["task_completed"]
    assert len(traces[trace_folders[1]]["calls"]) == 5
    return {
        "scope": "Observed hosted-model runs in local synthetic services; no invented outcomes "
                 "or scripted actor demonstrations in this deck",
        "cross_tab": cross_tab, "traces": traces, "diagnostic": diagnostic, "judge": judge,
        "interrupted_diagnostic": interrupted, "failed_judges": failed_judges,
        "raw_judge_fields": raw_fields,
        "source_hashes": {p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
                          for p in sorted(sources)},
    }


if __name__ == "__main__":
    result = collect()
    target = HERE / "qa/concrete-evidence.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print("Verified observed model traces, 48 actor runs and 68 judge calls:", target)
