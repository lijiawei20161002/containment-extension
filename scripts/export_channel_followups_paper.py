"""Export the three 17 November channel follow-up allocations without new inference.

Copies audited results into the paper's data folder under followup_* names,
strips local paths, and records hashes of every exported file and of the
paper-side analysis script. Account-linked identifiers (OpenRouter generation
ids) are not exported; only the provider-audit summary is.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COHORTS = [("followup_mechanism", "channel-mechanism-v1", "channel-mechanism-20261117-v1", 288),
           ("followup_mechanism_claude", "channel-mechanism-anthropic-openrouter-v1",
            "channel-mechanism-anthropic-openrouter-20261117-v1", 288),
           ("followup_haiku", "channel-older-model-openrouter-v1", "channel-older-model-openrouter-20261117-v1", 480)]
DRAFT_SOURCES = ["channel-mechanism-20261117-v1", "channel-terra-opus-20261112-v1",
                 "ambiguity-planner-comparison-20261111-v1"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def portable(value):
    if isinstance(value, dict):
        return {k: portable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [portable(v) for v in value]
    return value.replace(str(ROOT) + "/", "") if isinstance(value, str) else value


def write(path, value):
    path.write_text(json.dumps(portable(value), indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path, required=True)
    paper = parser.parse_args().paper_dir
    data = paper / "data"
    blocks, filenames = [], []
    for prefix, result_name, run_name, expected in COHORTS:
        folder, run = ROOT / "results" / result_name, ROOT / "runs" / run_name
        provenance, plan = read(folder / "provenance.json"), read(run / "plan.json")
        assert sha(run / "plan.json") == provenance["plan_sha256"] and sha(run / "tasks.json") == provenance["tasks_sha256"]
        assert sha(run / "summary.json") == provenance["run_summary_sha256"]
        assert sha(folder / "clarification-review.json") == provenance["review_sha256"]
        assert read(run / "execution.json")["status"] == "finished"
        episodes = read(folder / "episodes.json")
        assert len(episodes) == expected == len(plan["schedule"])
        for source, target in [("episodes.json", "episodes"), ("contracts.json", "contracts"),
                               ("summary.json", "summary"), ("clarification-review.json", "review")]:
            write(data / f"{prefix}_{target}.json", read(folder / source))
            filenames.append(f"{prefix}_{target}.json")
        (data / f"{prefix}_protocol.txt").write_text(portable((run / "protocol.md").read_text()))
        filenames.append(f"{prefix}_protocol.txt")
        audit = read(run / "provider-audit.json")["summary"] if (run / "provider-audit.json").exists() else None
        blocks.append({"prefix": prefix, "source": result_name, "version": plan["version"], "assigned": expected,
                       "config": plan["config"], "report_conditions": plan["report_conditions"],
                       "delivery_text": plan.get("delivery_text"), "limitations": plan["limitations"],
                       "inherited_contracts": len(plan["inherited_contracts"]), "fresh_scope_tasks": plan["fresh_scope_tasks"],
                       "source_provenance": provenance, "protocol_sha256": sha(run / "protocol.md"),
                       "provider_audit": audit})
    mechanism, claude, haiku = (ROOT / "runs" / c[2] for c in COHORTS)
    assert (mechanism / "tasks.json").read_bytes() == (claude / "tasks.json").read_bytes()
    assert (haiku / "tasks.json").read_bytes() == (data / "channel_tasks.json").read_bytes()
    write(data / "followup_tasks.json", read(mechanism / "tasks.json"))
    filenames += ["followup_tasks.json", "channel_tasks.json"]
    # First-draft scope decisions, before the review pass, in every allocation that saved drafts.
    drafts, inherited = [], read(mechanism / "plan.json")["inherited_contracts"]
    for run_name in DRAFT_SOURCES:
        run = ROOT / "runs" / run_name
        tasks = {t["task_id"]: t for t in read(run / "tasks.json")}
        for path in sorted(run.glob("contracts/*/result.json")):
            saved = read(path)
            task = tasks[saved["task_id"]]
            if not task["is_ambiguous"] or saved.get("draft_contract") is None:
                continue
            draft = saved["draft_contract"]
            origin = "channel-algorithms-20261112-v1" if run_name == DRAFT_SOURCES[0] and saved["task_id"] in inherited else run_name
            drafts.append({"allocation": origin, "task_id": saved["task_id"],
                           "wording": "chase" if task["x"].startswith("Please chase") else "followup",
                           "draft_asks": draft["needs_clarification"],
                           "draft_write_tools": sorted({w["tool_name"] for w in draft["writes"]}),
                           "reviewed_asks": saved["contract"]["needs_clarification"]})
    write(data / "followup_scope_drafts.json", drafts)
    filenames.append("followup_scope_drafts.json")
    write(data / "followup_provenance.json", {
        "date": "2026-11-17", "assigned": sum(c[3] for c in COHORTS), "allocations": len(COHORTS), "cohorts": blocks,
        "data_sha256": {name: sha(data / name) for name in filenames},
        "analysis_sha256": sha(paper / "analysis/channel_followup_summary.py"),
        "notes": ["Exploratory allocations on known development topics; earlier outcomes are unchanged and rates are not pooled.",
                  "Claude models were called through OpenRouter's Responses-format endpoint, pinned to Anthropic's endpoint with fallbacks disabled; generation records confirm the serving provider for every response.",
                  "Clarification annotations are direct readings by an AI assistant running Fable 5.2, one of the studied models; not independent human ratings.",
                  "Reasoning summaries are model-written text returned by the provider, not the models' reasoning.",
                  "A direct-API Haiku 4.5 allocation was prepared and made no inference calls; it is not exported.",
                  "Costs use uncached list prices; neutral probes are excluded."]})
    for name in filenames + ["followup_provenance.json"]:
        contents = (data / name).read_text()
        assert "/Users/" not in contents and "/home/" not in contents and not re.search(r"gen-\d{8,}-", contents), name
    print(json.dumps({"actor_records": sum(c[3] for c in COHORTS), "allocations": len(COHORTS), "data_files": len(filenames) + 1}))


if __name__ == "__main__":
    main()
