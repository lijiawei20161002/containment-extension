"""Freeze a separate retry cohort selected only by original transport failures.

The original cohort remains immutable and primary. This user-requested recovery
batch starts fresh episodes with identical frozen code, settings and contracts.
It does not replace originals or select episodes by behavioral outcomes.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import json
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    sys.path.insert(0, str(source / "source"))
    from containment_extension.sabench_study import verify, sha, now, atomic, digest
    parent = verify(source)
    assert json.loads((source / "execution.json").read_text())["status"] == "finished"
    schedule, mapping = [], []
    for spec in parent["schedule"]:
        path = source / "episodes" / spec["run"] / "result.json"
        result = json.loads(path.read_text())
        if result["stop"] != "provider_error":
            continue
        run = f"retry-{len(schedule)+1:05d}"
        schedule.append({**spec, "run": run, "retry_of": spec["run"]})
        mapping.append({"run": run, "source_run": spec["run"], "task_id": spec["task_id"],
                        "model_key": spec["model_key"], "arm": spec["arm"],
                        "source_error": result["error"], "source_result_sha256": sha(path)})
    assert schedule, "No transport failures to retry"
    output.mkdir(parents=True, exist_ok=False)
    for folder in ["source", "third_party"]:
        shutil.copytree(source / folder, output / folder, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    task_ids = sorted({r["task_id"] for r in schedule})
    for task_id in task_ids:
        destination = output / "contracts" / task_id / "result.json"
        destination.parent.mkdir(parents=True)
        original = source / "contracts" / task_id / "result.json"
        assert json.loads(original.read_text())["status"] == "complete"
        shutil.copy2(original, destination)
    frozen = {str(p.relative_to(output)): sha(p) for folder in ["source", "third_party", "contracts"]
              for p in (output / folder).rglob("*") if p.is_file()}
    plan = {**deepcopy(parent), "version": "sabench-network-recovery-v1", "created_at": now(),
        "split": "network_recovery", "task_ids": task_ids, "schedule": schedule, "frozen_hashes": frozen,
        "request_ceiling": len(schedule) * parent["config"]["max_steps"],
        "authorization": "User explicitly requested trying again after the network issue. Original results are preserved; retries are separately labeled.",
        "primary": "None: selected infrastructure-recovery cohort, not a new confirmatory comparison.",
        "secondary": "Descriptive recovery outcomes; original held-out analysis remains primary.",
        "network_recovery": {"source_plan_sha256": digest(parent), "assignment_map": mapping,
            "selection": "Every original provider_error, independent of incident or completion outcomes.",
            "scope_reuse": "Original reviewed contracts reused without additional inference or duplicate cost accounting.",
            "interpretation": "Fresh starts, not continuation of original trajectories. Never overwrite or silently substitute outcomes."}}
    plan["limitations"] = [*parent["limitations"], "Original no-replay policy applies to the primary cohort; this separately authorized replay batch is exploratory."]
    atomic(output / "plan.json", plan)
    atomic(output / "plan.sha256.json", {"sha256": digest(plan)})
    atomic(output / "execution.json", {"status": "prepared_without_inference"})
    print(json.dumps({"assignments": len(schedule), "reused_contracts": len(task_ids), "max_estimated_usd": None}))


if __name__ == "__main__":
    main()
