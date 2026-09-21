"""Reconcile a completed upstream baseline and extract evidence for semantic review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from inspect_ai.log import read_eval_log

from containment_extension.impossiblebench.study import digest, write_json


def patch_sections(patch: str) -> dict[str, str]:
    sections = re.split(r"(?=^diff --git )", patch, flags=re.M)
    result = {}
    for section in sections:
        match = re.match(r"diff --git a/(.+) b/(.+)\n", section)
        if match:
            result[match[2]] = section
    return result


def analyze(root: Path) -> dict:
    plan = json.loads((root / "plan.json").read_text())
    execution = json.loads((root / "execution.json").read_text())
    if execution["status"] != "ended":
        raise ValueError("Wait for execution to end before final reconciliation")
    budget = json.loads((root / "budget.json").read_text())
    results = json.loads((root / "results.json").read_text())
    by_run = {r["assignment"]["run"]: r for r in results}
    usage = [json.loads(line) for line in (root / "usage.jsonl").read_text().splitlines()]
    qualification = json.loads((root / "qualification/report.json").read_text())
    baseline_patches = {
        c["assignment"]["run"]: c["score"].get("metadata", {}).get("model_patch", "")
        for c in qualification["checks"]
        if c["dummy"] == "nochange"
    }
    output = root / "analysis"
    output.mkdir(exist_ok=False)
    records = []
    sums = Counter()
    for spec in plan["schedule"]:
        run_id = spec["run"]
        saved = by_run.get(run_id, {})
        record = {
            **spec,
            "raw_score": saved.get("raw_score"),
            "log_status": saved.get("log_status"),
            "limit": saved.get("sample_limit"),
            "error": saved.get("sample_error"),
            "budget": budget.get("runs", {}).get(run_id),
            "semantic_review": None,
        }
        known_usage = [u["usage"] for u in usage if u["run"] == run_id and u["usage"] is not None]
        ins = sum(
            u["input_tokens"]
            + (u.get("input_tokens_cache_read") or 0)
            + (u.get("input_tokens_cache_write") or 0)
            for u in known_usage
        )
        outs = sum(u["output_tokens"] for u in known_usage)
        reads = sum(u.get("input_tokens_cache_read") or 0 for u in known_usage)
        writes = sum(u.get("input_tokens_cache_write") or 0 for u in known_usage)
        record["usage"] = {
            "known_responses": len(known_usage),
            "input_tokens": ins,
            "output_tokens": outs,
            "cache_reads": reads,
            "cache_writes": writes,
        }
        sums.update(record["usage"])
        logs = list((root / run_id).glob("*.eval"))
        if len(logs) > 1:
            raise ValueError(f"Unexpected multiple logs for {run_id}")
        if logs:
            log = read_eval_log(str(logs[0]), resolve_attachments=True)
            record["log_sha256"] = hashlib.sha256(logs[0].read_bytes()).hexdigest()
            sample = log.samples[0] if log.samples else None
            if sample:
                models = [e for e in sample.events if e.event == "model"]
                tools = [e for e in sample.events if e.event == "tool"]
                scores = [e for e in sample.events if e.event == "score"]
                submissions = [e for e in tools if e.function == "submit"]
                record.update(
                    model_events=len(models),
                    tool_counts=dict(Counter(e.function for e in tools)),
                    elapsed_seconds=sample.total_time,
                    submissions=[
                        {
                            "id": e.id,
                            "timestamp": e.timestamp.isoformat(),
                            "arguments": e.arguments,
                            "error": e.model_dump(mode="json")["error"],
                        }
                        for e in submissions
                    ],
                    score_events=[
                        {
                            "timestamp": e.timestamp.isoformat(),
                            "value": e.score.value,
                            "intermediate": e.intermediate,
                        }
                        for e in scores
                    ],
                    human_intervention=sample.metadata.get("flag_for_human_intervention", False),
                    output_stop_reason=sample.output.stop_reason if sample.output.choices else None,
                )
                trace = [
                    {
                        "id": e.id,
                        "function": e.function,
                        "arguments": e.arguments,
                        "result": e.model_dump(mode="json")["result"],
                        "error": e.model_dump(mode="json")["error"],
                    }
                    for e in tools
                    if e.function != "think"
                ]
                write_json(output / (run_id + "-actions.json"), trace)
                patches = [
                    e.score.metadata.get("model_patch")
                    for e in scores
                    if e.score.metadata and e.score.metadata.get("model_patch")
                ]
                latest = (saved.get("score") or {}).get("metadata", {}) or {}
                if latest.get("model_patch"):
                    patches.append(latest["model_patch"])
                if patches:
                    final = patches[-1]
                    (output / (run_id + ".patch")).write_text(final)
                    base = patch_sections(baseline_patches[run_id])
                    changed = patch_sections(final)
                    paths = sorted(
                        p for p in set(base) | set(changed) if base.get(p) != changed.get(p)
                    )
                    record["paths_differing_from_initialized_task"] = paths
                    record["patch_sha256"] = digest(final)
        records.append(record)
    checks = {
        "all_assignments_recorded": len(results) == plan["assigned"],
        "known_input_matches_ledger": sums["input_tokens"] == budget["actual_input_tokens"],
        "known_output_matches_ledger": sums["output_tokens"] == budget["actual_output_tokens"],
        "responses_and_reservations_match": sums["known_responses"]
        + budget["unknown_usage_requests"]
        == budget["requests"],
        "no_reservation_overrun": not budget["reservation_overrun"],
        "aggregate_within_limits": budget["requests"] <= budget["limits"]["requests"]
        and budget["accounted_input_tokens"] <= budget["limits"]["input_tokens"]
        and budget["accounted_output_tokens"] <= budget["limits"]["output_tokens"]
        and budget["estimated_usd"] <= budget["limits"]["estimated_usd"],
        "per_run_within_limits": all(
            b["requests"] <= b["limits"]["requests"]
            and b["accounted_input_tokens"] <= b["limits"]["input_tokens"]
            and b["accounted_output_tokens"] <= b["limits"]["output_tokens"]
            and b["estimated_usd"] <= b["limits"]["estimated_usd"]
            for b in budget.get("runs", {}).values()
        ),
    }
    report = {
        "plan_sha256": digest(plan),
        "assigned": plan["assigned"],
        "accounting_checks": checks,
        "usage": dict(sums),
        "budget": budget,
        "records": records,
        "notes": [
            "Raw upstream scores; semantic reviews are separate evidence-bound labels.",
            "Patch differences subtract trusted task initialization; "
            "final diffs do not detect all transient changes.",
        ],
    }
    write_json(output / "execution-analysis.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = analyze(args.directory)
    print(json.dumps({k: v for k, v in result.items() if k not in {"records", "budget"}}, indent=2))
