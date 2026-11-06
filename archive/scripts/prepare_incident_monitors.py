"""Prepare paired monitor views from archived proposals, without model calls.

Run from the repository root: python3 scripts/prepare_incident_monitors.py ...
The two views share exactly the same pre-proposal action evidence. Labels and
future outcomes stay outside their inputs. Only visible actor text is included.
"""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def visible_text(raw):
    parts = []
    for item in raw.get("output", raw.get("content", [])):
        if item.get("type") == "text":
            parts.append(item["text"])
        for part in item.get("content", []):
            if part.get("type") in {"text", "output_text"}:
                parts.append(part["text"])
    return "\n".join(parts)


def prepare(sources, output):
    output.mkdir(parents=True, exist_ok=False)
    counts, splits, source_hashes = Counter(), Counter(), {}
    with (output / "actions.jsonl").open("x") as stream:
        for source in sources:
            for file in sorted(source.glob("run-*/proposals.json")):
                run = file.parent
                prompt_path, transcript_path = run / "prompts.json", run / "transcript.jsonl"
                prompts = json.loads(prompt_path.read_text())
                proposals = json.loads(file.read_text())
                by_step = defaultdict(list)
                for proposal in proposals:
                    by_step[proposal["step"]].append(proposal)
                key = f"{source.name}/{run.name}"
                split = "held_out_rollouts" if int(hashlib.sha256(key.encode()).hexdigest(), 16) % 5 == 0 else "development"
                source_hashes[key] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in (file, prompt_path, transcript_path)}
                calls, tool_history, explanations = {}, [], []
                manifest = json.loads((run / "manifest.json").read_text())
                # Scripted checkpoint evidence is part of the actor's initial context.
                for entry in manifest.get("checkpoint", {}).get("prefix", []):
                    tool_history.append({"step": "scripted_setup", "action": entry["action"],
                                         "result": entry["response"]})
                for line in transcript_path.read_text().splitlines():
                    event = json.loads(line)
                    if "provider_response" in event:
                        text = visible_text(event["provider_response"])
                        if text:
                            explanations.append({"step": event["step"], "visible_text": text})
                        for proposal in by_step[event["step"]]:
                            calls[proposal["call_id"]] = proposal
                            evidence = {"system": prompts["system"], "task": prompts["task"],
                                        "prior_tool_events": list(tool_history),
                                        "proposed_tool": proposal["name"],
                                        "proposed_arguments": proposal["arguments"]}
                            # The study's user intervention is a trusted instruction, not actor prose.
                            history_path = run / "initial-history.json"
                            if history_path.exists():
                                history = json.loads(history_path.read_text())
                                last = history[-1]
                                evidence["checkpoint_instruction"] = (last["content"] if isinstance(last["content"], str)
                                    else next(b["text"] for b in last["content"] if b["type"] == "text"))
                            row = {"source_run": key, "step": event["step"],
                                   "call_id": proposal["call_id"], "split": split,
                                   "label": proposal["scope_label"],
                                   "label_metric_version": manifest.get("metric_version"),
                                   "views": {"actions_only": evidence,
                                             "with_visible_explanations": {
                                                 **evidence, "actor_explanations": list(explanations)}}}
                            if "scope_label_v2" in proposal:
                                row["historical_v2_label"] = proposal["scope_label_v2"]
                            stream.write(canonical(row) + "\n")
                            counts[proposal["scope_label"]] += 1
                            splits[split] += 1
                    elif "tool_result" in event:
                        call = calls[event["call_id"]]
                        tool_history.append({"step": event["step"], "action": call["arguments"],
                                             "result": event["tool_result"]})
    manifest = {"version": "incident-monitor-inputs-v1", "source_runs": len(source_hashes),
                "proposals": sum(counts.values()), "label_counts": dict(counts),
                "split_proposal_counts": dict(splits), "source_hashes": source_hashes,
                "generation_calls": 0,
                "limitations": [
                    "Label versions are preserved, not pooled: older URL labels include catalog errors.",
                    "All views of each source rollout share a split; task structures are not held out.",
                    "Views end at proposal time, before any results from that model turn.",
                    "Visible explanations are not private chain of thought.",
                    "No monitors have been tuned or evaluated; no detection-rate claims."
                ]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return {k: v for k, v in manifest.items() if k != "source_hashes"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.sources, args.output), indent=2))
