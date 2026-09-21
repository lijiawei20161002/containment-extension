"""Summarize the two execution phases without rewriting their raw results."""

import json
from collections import Counter
from pathlib import Path

from containment_extension.impossiblebench.study import digest, summarize, write_json

root = Path("runs/impossible-live-preflight-continuation-01")
plan = json.loads((root / "plan.json").read_text())
assert json.loads((root / "execution.json").read_text())["status"] == "ended"
prior = json.loads((root / "prior-budget.json").read_text())
budget = json.loads((root / "budget.json").read_text())
raw = summarize(root)
rows = []
for spec in plan["schedule"]:
    directory = root / spec["run"]
    path = directory / "result.json"
    result = json.loads(path.read_text()) if path.exists() else None
    row = {**spec, "stop": "missing", "calls": 0, "actions": 0,
           "submissions": [], "triggered": False, "observed_protected_paths": [],
           "changed_paths": [], "observed": False, "shell_tests": 0}
    if result is not None:
        assert result["assignment"] == spec
        evidence = result["evidence"]
        row.update(stop=result["stop"], calls=result["model_calls"], actions=result["actions"],
                   submissions=[s["passed"] for s in result["submissions"]],
                   triggered=result["triggered"], observed=evidence.get("complete", False),
                   changed_paths=sorted(evidence.get("file_changes", {})),
                   observed_protected_paths=sorted({e["path"] for e in evidence.get("events", [])
                                                   if e.get("protected")}),
                   result_sha256=digest(result))
        if (directory / "interruption-evidence.json").exists():
            row["stop"] = "interrupted"
        transcript = directory / "transcript.jsonl"
        if transcript.exists():
            # The interrupted result may lag its durable request journal.
            row["calls"] = sum("request" in json.loads(line)
                               for line in transcript.read_text().splitlines())
        for p in result["proposals"]:
            if p["dispatched"] and p["name"] == "shell":
                command = p["arguments"].get("command", "")
                # Descriptive count only, never a substitute for the trusted scorer.
                if "pytest " in command or "bin/test " in command:
                    row["shell_tests"] += 1
    rows.append(row)

rates = plan["config"]["models"][0]["rates"]
new_known_estimate = (
    (budget["actual_input_tokens"] - .9 * budget["cache_read_input_tokens"]
     + .25 * budget["cache_write_input_tokens"]) * rates["input"]
    + budget["actual_output_tokens"] * rates["output"]
) / 1e6
new_known_conservative = (
    (budget["actual_input_tokens"] + budget["cache_write_input_tokens"]) * rates["input"]
    + budget["actual_output_tokens"] * rates["output"]
) / 1e6
usage = {
    "requests": prior["usage"]["requests"] + budget["requests"],
    "accounted_input_tokens": prior["usage"]["input_tokens"] + budget["accounted_input_tokens"],
    "accounted_output_tokens": prior["usage"]["output_tokens"] + budget["accounted_output_tokens"],
    "conservative_estimated_usd": prior["usage"]["estimated_usd"] + budget["estimated_usd"],
    "unknown_requests": prior["unknown_requests"] + budget["unknown_usage_requests"],
    "known_response_estimate_usd": prior["known_response_estimate_5m_cache_usd"]
    + new_known_estimate,
    "unresolved_request_reservation_usd": sum(e["conservative_usd"] for e in prior["entries"]
                                            if e["unknown"])
    + max(0, budget["estimated_usd"] - new_known_conservative),
}
limits = plan["config"]["continuation"]["authorized_total_budget"]
assert usage["requests"] <= limits["requests"]
assert usage["accounted_input_tokens"] <= limits["input_tokens"]
assert usage["accounted_output_tokens"] <= limits["output_tokens"]
assert usage["conservative_estimated_usd"] <= limits["estimated_usd"]
report = {
    "assigned": len(rows), "started": sum(r["calls"] > 0 for r in rows),
    "stops": dict(Counter(r["stop"] for r in rows)),
    "scored_submissions": sum(len(r["submissions"]) for r in rows),
    "interventions_delivered": sum(r["triggered"] for r in rows),
    "runs_with_observed_protected_changes": sum(bool(r["observed_protected_paths"]) for r in rows),
    "usage": usage, "authorized_limits": limits, "records": rows,
    "notes": [
        "Original evidence is immutable; interrupted raw stop='running' is labeled interrupted here.",
        "The 3 carried results used the prior source; only unstarted assignments used the corrected source.",
        "Known response estimate uses 5-minute cache rates for the first phase; not a provider bill.",
        "Shell-test count is descriptive and does not imply a scored submission or intervention trigger.",
        "Limits, missing execution, and interruption remain unknown outcomes, never clean negatives.",
    ],
}
write_json(root / "execution-analysis.json", report)
print(json.dumps({k: v for k, v in report.items() if k != "records"}, indent=2))
