"""Continue only unstarted assignments under the remaining approved allocation.

The original interrupted execution and every started rollout remain immutable.
This uses the same InspectAgent and run_one loop, without Inspect's eval scheduler.
"""

import asyncio
import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

from containment_extension.config import load_env
from containment_extension.impossiblebench.docker import DockerBackend
from containment_extension.impossiblebench.qualification import verify_qualification
from containment_extension.impossiblebench.runner import InferenceBudget, run_one
from containment_extension.impossiblebench.study import (
    digest, load_plan, prepare, summarize, validate_bundle, write_json,
)

PARENT = Path("runs/impossible-live-preflight-proposed-01")
ROOT = Path("runs/impossible-live-preflight-continuation-01")
QUALIFICATION = Path("runs/impossible-controls-dev-02/qualification.json")


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_continuation():
    old = json.loads((PARENT / "plan.json").read_text())
    assert digest(old) == json.loads((PARENT / "plan.sha256.json").read_text())["sha256"]
    assert digest(json.loads((PARENT / "source.json").read_text())) == old["source_sha256"]
    assert json.loads((PARENT / "execution.json").read_text())["status"] == "ended"
    bundle = json.loads((PARENT / "bundle.json").read_text())
    assert digest(bundle) == old["bundle_sha256"]
    ledger = json.loads((PARENT / "reconciled-budget.json").read_text())
    assert ledger["parent_plan_sha256"] == digest(old)
    for key, ceiling in old["config"]["budget"].items():
        assert abs(ledger["usage"][key] + ledger["remaining_budget"][key] - ceiling) < 1e-8
    carried = {}
    for spec in old["schedule"]:
        directory = PARENT / spec["run"]
        if directory.exists():
            result = json.loads((directory / "result.json").read_text())
            assert result["assignment"] == spec
            carried[spec["run"]] = {
                "result_sha256": digest(result),
                "files": {p.relative_to(directory).as_posix(): file_hash(p)
                          for p in sorted(directory.rglob("*")) if p.is_file()},
            }
    assert set(carried) == {"run-00000", "run-00001", "run-00002"}
    config = copy.deepcopy(old["config"])
    config["status"] = "approved_continuation"
    config["budget"] = ledger["remaining_budget"]
    config["continuation"] = {
        "parent_plan_sha256": digest(old),
        "parent_source_sha256": old["source_sha256"],
        "reconciled_budget_sha256": digest(ledger),
        "authorized_total_budget": old["config"]["budget"],
        "prior_accounted_usage": ledger["usage"],
        "carried_forward": carried,
        "execution_script_sha256": file_hash(Path(__file__)),
        "reason": "Cached-input accounting repaired; only unstarted assignments execute. "
        "All started results are retained, including the interrupted third rollout.",
    }
    plan = prepare(ROOT, config, bundle)
    for key in ("schedule", "policy", "interface", "prompt_bank", "bundle_sha256"):
        assert plan[key] == old[key]
    for name in carried:
        shutil.copytree(PARENT / name, ROOT / name)
    shutil.copyfile(PARENT / "plan.json", ROOT / "parent-plan.json")
    shutil.copyfile(PARENT / "reconciled-budget.json", ROOT / "prior-budget.json")
    shutil.copyfile(PARENT / "authorization.json", ROOT / "authorization.json")
    summarize(ROOT)
    print(json.dumps({"assigned": len(plan["schedule"]), "carried_forward": len(carried),
                      "unstarted": len(plan["schedule"]) - len(carried),
                      "remaining_budget": config["budget"]}), flush=True)


async def execute():
    from inspect_ai.model import GenerateConfig, get_model
    from containment_extension.impossiblebench.inspect_adapter import InspectAgent

    plan, bundle = load_plan(ROOT)
    provenance = plan["config"]["continuation"]
    assert provenance["execution_script_sha256"] == file_hash(Path(__file__))
    for name, carried in provenance["carried_forward"].items():
        for file, expected in carried["files"].items():
            assert file_hash(ROOT / name / file) == expected
        assert digest(json.loads((ROOT / name / "result.json").read_text())) == carried["result_sha256"]
    qualification = verify_qualification(QUALIFICATION, bundle)
    write_json(ROOT / "qualification.json", qualification)
    load_env(Path("/home/ubuntu/.env"))
    budget = InferenceBudget(plan["config"]["budget"], plan["config"]["models"])
    model_name = plan["config"]["models"][0]["name"]
    assert len(plan["config"]["models"]) == 1
    model = get_model(model_name, config=GenerateConfig(max_retries=0),
                      max_retries=0, memoize=False)
    agent = InspectAgent(model)
    records = validate_bundle(bundle)
    with (ROOT / "execution.json").open("x") as stream:
        json.dump({"plan_sha256": digest(plan), "status": "started", "mode": "continuation"}, stream)
    try:
        for spec in plan["schedule"]:
            if spec["run"] in provenance["carried_forward"]:
                continue
            result = await run_one(ROOT / spec["run"], spec,
                                   records[(spec["instance_id"], spec["variant"])],
                                   plan["config"]["limits"], agent, DockerBackend(), budget,
                                   qualified=True)
            print(json.dumps({"run": spec["run"], "stop": result["stop"],
                              "calls": result["model_calls"], "budget": budget.snapshot()}), flush=True)
    finally:
        write_json(ROOT / "budget.json", budget.snapshot())
        summarize(ROOT)
        write_json(ROOT / "execution.json", {"plan_sha256": digest(plan), "status": "ended",
                                              "mode": "continuation", "assigned": 24})


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare_continuation()
    elif sys.argv[1:] == ["run"]:
        asyncio.run(execute())
    else:
        raise SystemExit("Expected prepare or run")
