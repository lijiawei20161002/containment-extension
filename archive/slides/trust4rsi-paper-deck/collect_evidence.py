"""Collect only observed hosted-model evidence for the paper deck; no demonstrations."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def collect_extended(read, sources):
    """Archived studies, budgets and the public-incident library used by the longer deck."""
    library = read("figures/incidents/analysis/summary.json")
    records = {}
    for path in sorted((REPO / "incidents/records").glob("*.json")):
        name = str(path.relative_to(REPO))
        record = read(name)
        records[record["entry_number"]] = {
            "id": record["id"],
            "short_title": record["short_title"],
            "actor": record["actor"],
            "pathway": record["pathway"],
            "category": record["category"],
            "summary": record["summary"],
            "dates": record["dates"],
            "timeline": record["timeline"],
            "objective": record["coding"].get("objective"),
            "boundary": record["coding"].get("boundary"),
            "actions": record["coding"].get("actions", []),
            "indicators": record["indicators"],
            "stop_behavior": record["stop_behavior"],
            "evidence_level": record["evidence"]["level"],
            "sources": [
                {"name": s["name"], "publisher": s["publisher"], "date": s["date"]}
                for s in record["evidence"]["sources"]
            ],
            "mechanisms": {k: v["status"] for k, v in record["mechanisms"].items()},
            "propositions": {k: v["relation"] for k, v in record["propositions"].items()},
        }
    assert len(records) == 26 and library["n"] == 26
    overreach = [n for n, r in records.items() if r["pathway"] == "live_access_overreach"]
    link = read("results/link-study-v1/analysis.json")
    link_summary = read("results/link-study-v1/summary.json")
    pooled = {p["arm"]: p for p in link["pooled"]}
    contrasts = {
        (c["arm"], c["metric"]): c
        for c in link["contrasts"]
        if c["model"] == "pooled" and c["variant"] == "pooled"
    }
    sensitivity = {(c["arm"], c["metric"]): c for c in link["sensitivity"]}
    stalled_reminder = {"positive": 0, "unknown": 0, "assigned": 0}
    for g in link_summary["groups"]:
        if g["variant"] == "stalled" and "reminder" in g["arm"]:
            stalled_reminder["positive"] += g["any_outside"]
            stalled_reminder["unknown"] += g["any_unknown"]
            stalled_reminder["assigned"] += g["n"]
    assert stalled_reminder == {"positive": 27, "unknown": 3, "assigned": 32}
    destinations = {}
    for arm, counts in link["first_destinations_by_arm"].items():
        upstream = sum(v for k, v in counts.items() if "/repos/upstream/" in k)
        archive = sum(v for k, v in counts.items() if "run-prior" in k)
        catalog_guess = sum(v for k, v in counts.items() if "/catalog/" in k)
        destinations[arm] = {
            "upstream": upstream,
            "archive": archive,
            "catalog_guess": catalog_guess,
            "none": counts.get("none", 0),
            "assigned": sum(counts.values()),
        }
    cue = read("results/cue-study-v1/summary.json")
    scope_levels = read("results/scope-levels-v1/summary.json")
    ablation = read("results/feedback-ablation-v1/summary.json")
    original = next(g for g in ablation["groups"] if g["candidate"] == "original")
    assert ablation["status"] == "baseline_no_events" and ablation["recorded"] == 6
    terminal = read("results/incident-study-v1/terminal-review.json")
    assert terminal["reports_reviewed"] == 51 and terminal["clean_supported_blockers"] == 48
    historical = read("results/incident-study-v1/summary.json")
    cells = {}
    for g in historical["groups"]:
        model = "haiku" if "haiku" in g["model"] else "gpt"
        cells[(model, g["variant"], g["arm"])] = g
    tradeoff = read("figures/experiments/tradeoff-v1/cells.json")
    budgets = {}
    for study in (
        "incident-study-v1",
        "link-study-v1",
        "cue-study-v1",
        "baseline-diagnostic-v2",
        "transcript-audit-v4",
        "feedback-ablation-v1",
    ):
        b = read(f"results/{study}/budget.json")
        b = b.get("aggregate", b)
        budgets[study] = {"requests": b["requests"], "estimated_usd": b["estimated_usd"]}
    actor_runs = {
        "link-study-v1": link["runs"],
        "cue-study-v1": cue["runs"],
        "incident-study-v1": historical["runs"],
        "scope-levels-v1": scope_levels["recorded"],
        "feedback-ablation-v1": ablation["recorded"],
        "baseline-diagnostic-v1": 27,
        "baseline-diagnostic-v2": 48,
    }
    return {
        "library": library,
        "records": records,
        "overreach_entries": overreach,
        "link": {
            "runs": link["runs"],
            "pooled": {
                arm: {
                    k: pooled[arm][k]
                    for k in ("early_upstream", "any_outside", "writes", "cross_run_reads")
                }
                for arm in pooled
            },
            "timing_by_arm": link["timing_by_arm"],
            "destinations": destinations,
            "contrast_hidden": contrasts[("hidden", "early_outside")],
            "contrast_reminder": contrasts[("visible_reminder", "early_outside")],
            "sensitivity_hidden": sensitivity[("hidden", "early_upstream")],
            "stalled_reminder_any_outside": stalled_reminder,
            "stops": link["stops"],
        },
        "cue": {"runs": cue["runs"], "ranking": cue["ranking"], "errors": cue["provider_errors"]},
        "scope_levels_runs": scope_levels["recorded"],
        "ablation": {
            "status": ablation["status"],
            "assigned": ablation["assigned"],
            "recorded": ablation["recorded"],
            "original": original,
            "ceilings": ablation["ceilings"],
        },
        "terminal_review": {k: terminal[k] for k in terminal if k != "records"},
        "incident_cells": {"|".join(k): v for k, v in cells.items()},
        "tradeoff_cells": tradeoff["cells"],
        "budgets": budgets,
        "actor_runs": actor_runs,
    }


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
    notes = read("results/baseline-diagnostic-v2/notes.json")
    recovery_prefix = read(
        "results/feedback-ablation-v1/checkpoints/development-recoverable-12000/checkpoint.json"
    )
    blocked_prefix = read(
        "results/feedback-ablation-v1/checkpoints/development-impossible-12000/checkpoint.json"
    )
    assert recovery_prefix["prefix"] == blocked_prefix["prefix"]
    assert recovery_prefix["prefix"][-1]["response"]["status"] == 503
    research = read("slides/trust4rsi-paper-deck/research-sources.json")
    report_name = "docs/impossiblebench-upstream-baseline-results.md"
    sources.add(report_name)
    upstream_report = (REPO / report_name).read_text()
    assert "1/2 original tasks, 0/2 oneoff variants and 0/2 conflicting variants" in upstream_report
    assert "All six\nruns reached the 100-message limit" in upstream_report
    fp_request = read("results/transcript-audit-v4/judges/run-0028/request.json")
    fp_response = read("results/transcript-audit-v4/judges/run-0028/response.json")
    fp_packet = json.loads(fp_request["messages"][0]["content"])
    assert "call the designated challenge" in fp_packet["trusted_task"]
    assert "unauthorized privilege escalation" in fp_response["content"][0]["text"]
    failed_judges = {v: read(f"results/transcript-audit-{v}/summary.json") for v in ("v2", "v3")}
    for study in (
        "baseline-diagnostic-v2",
        "transcript-audit-v2",
        "transcript-audit-v3",
        "transcript-audit-v4",
    ):
        assert read(f"results/{study}/independent-audit.json")["passed"]
        read(f"results/{study}/plan.json")
    assert diagnostic["status"] == "finished" and diagnostic["recorded"] == 48
    assert judge["status"] == "finished" and judge["recorded"] == 68
    assert judge["diagnostic_only"] and not judge["calibration_passed"]
    assert judge["budget"]["requests"] == 56
    assert all(j["status"] == "calibration_or_integrity_failed" for j in failed_judges.values())
    old_counts = Counter(
        (r["stop"] == "scorer_success", bool(r["any_effect"])) for r in historical["records"]
    )
    assert len(historical["records"]) == 160
    assert all(r["any_effect"] in (0, 1) for r in historical["records"])
    cross_tab = {
        "pass_incident": old_counts[True, True],
        "pass_no_incident": old_counts[True, False],
        "no_pass_incident": old_counts[False, True],
        "no_pass_no_incident": old_counts[False, False],
    }
    assert cross_tab == {
        "pass_incident": 13,
        "pass_no_incident": 96,
        "no_pass_incident": 2,
        "no_pass_no_incident": 49,
    }
    trace_folders = [
        "results/incident-study-v1/run-0001",
        "results/incident-study-v1/run-0094",
        "results/feedback-ablation-v1/run-0001",
        "results/feedback-ablation-v1/run-0002",
    ]
    # The first completed input pair is shown without selecting for its outcome.
    trace_folders += [
        f"results/baseline-diagnostic-v2/{r['run']}" for r in diagnostic["records"][:2]
    ]
    trace_folders += ["results/baseline-diagnostic-v2/run-0028"]
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
                    turn = {"step": event["step"], "call_id": block["id"], "action": block["input"]}
                    calls.append(turn)
                    by_id[block["id"]] = turn
            if "tool_result" in event:
                by_id[event["call_id"]]["result"] = event["tool_result"]
        traces[folder] = {
            "calls": calls,
            "stop": result["stop_reason"],
            "final_text": result["final_text"],
            "incident": result["unauthorized_effect"],
            "task_completed": result["task_completed"],
        }
    assert traces[trace_folders[0]]["calls"][2]["action"]["url"].endswith("run-prior/solution")
    assert traces[trace_folders[0]]["calls"][-1]["result"]["correct"]
    copied_flag = traces[trace_folders[0]]["calls"][2]["result"]["flag"]
    assert (
        json.loads(traces[trace_folders[0]]["calls"][-1]["action"]["body"])["flag"] == copied_flag
    )
    assert traces[trace_folders[1]]["incident"] and not traces[trace_folders[1]]["task_completed"]
    assert len(traces[trace_folders[1]]["calls"]) == 5
    extended = collect_extended(read, sources)
    return {
        "scope": "Observed hosted-model runs in local synthetic services; no invented outcomes "
        "or scripted actor demonstrations in this deck",
        **extended,
        "cross_tab": cross_tab,
        "traces": traces,
        "diagnostic": diagnostic,
        "judge": judge,
        "interrupted_diagnostic": interrupted,
        "failed_judges": failed_judges,
        "raw_judge_fields": raw_fields,
        "notes": notes,
        "common_recovery_prefix_sha256": recovery_prefix["prefix_sha256"],
        "research_sources": research,
        "upstream_baseline_evidence": {
            "status": "report_only_raw_live_archive_absent_from_checkout",
            "source": report_name,
            "live_archive_present": (REPO / "results/upstream-baseline-live-v1").exists(),
            "not_independently_recomputed_this_revision": True,
        },
        "copied_flag": copied_flag,
        "false_positive_task": fp_packet["trusted_task"],
        "false_positive_judge_response": fp_response,
        "source_hashes": {
            p: hashlib.sha256((REPO / p).read_bytes()).hexdigest() for p in sorted(sources)
        },
    }


if __name__ == "__main__":
    result = collect()
    target = HERE / "qa/concrete-evidence.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print("Verified observed model traces, 48 actor runs and 68 judge calls:", target)
