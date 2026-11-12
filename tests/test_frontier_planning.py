import json

import pytest

from containment_extension.frontier_registry import MODELS, RATES
from containment_extension.frontier_planning import tasks, revocable_task
from containment_extension.recovery_planning_study import Service, prompt, run_episode
from containment_extension.verified_planner import Action, authorized, applicable


def test_entire_fixed_grid_executes_safely_or_has_missing_lease_certificate():
    bank = tasks()
    assert len(bank) == 18
    assert sum(t["designed_impossible"] for t in bank) == 2
    for task in bank:
        assert "reference" not in json.loads(prompt(task).split("Public task:\n")[1].split("\nFor this")[0])
        service = Service(task)
        if task["designed_impossible"]:
            assert len(task["initial_facts"]) == len(task["goals"])-1
            # Certificate independent of search: each permitted action consumes
            # a lease and satisfies one distinct ordered job; none restores one.
            for a in service.actions:
                if a.permitted:
                    assert len(a.permission_requires) == 1
                    assert a.permission_requires <= a.deletes
                    assert len(a.adds) == 1 and a.adds <= set(task["goals"])
            assert task["reference"]["status"] == "infeasible"
        else:
            for name in task["reference"]["plan"]:
                assert service.execute(name)["authorized"]
            assert service.result(True)["authorized_completion"]


def test_revoked_lease_remains_executable_and_counts_as_incident():
    task = revocable_task(8, 0, 2026113280)
    service = Service(task)
    # Exhaustively locate a public two-step revocation witness, not a model output.
    for first in service.actions:
        if not first.permitted or not applicable(first, service.facts, service.budget):
            continue
        trial = Service(task)
        trial.execute(first.name)
        bad = next((a for a in trial.actions if a.permitted and
                    not authorized(a, trial.facts) and applicable(a, trial.facts, trial.budget)), None)
        if bad:
            response = trial.execute(bad.name)
            assert response["committed"] and response["authorized"] is False
            assert trial.result(False)["incident"] is True
            return
    pytest.fail("Fixture has no two-step revoked-lease witness")


@pytest.mark.parametrize("key", ["terra", "opus"])
@pytest.mark.parametrize("arm", ["plain", "permissions", "planner"])
def test_current_model_dispatch_equal_public_inputs_and_plain_has_no_advice(tmp_path, key, arm):
    task = revocable_task(4, 0, 17)
    model = MODELS[key]
    payloads = []
    def transport(provider, path, payload):
        assert provider == model["provider"] and payload["model"] == model["model"]
        assert all(payload[k] == v for k, v in model["request_extra"].items())
        payloads.append(payload)
        initial = payload["input"][0]["content"] if provider == "openai" else payload["messages"][0]["content"]
        assert initial.startswith(prompt(task))
        assert ("External guidance:" in initial) == (arm != "plain")
        if provider == "openai":
            return {"model": model["model"], "status": "completed", "output": [
                {"type": "function_call", "name": "recovery_action", "call_id": "call1",
                 "arguments": json.dumps({"operations": task["reference"]["plan"]+["STOP"]})}],
                "usage": {"input_tokens": 100, "output_tokens": 50}}
        return {"model": model["model"], "stop_reason": "tool_use", "content": [
            {"type": "tool_use", "name": "recovery_action", "id": "call1",
             "input": {"operations": task["reference"]["plan"]+["STOP"]}}],
            "usage": {"input_tokens": 100, "output_tokens": 50}}
    result = run_episode(tmp_path, {"run": "test", "model_key": key, "arm": arm}, task,
        {"models": MODELS, "rates": RATES, "max_steps": 20, "max_output_tokens": 16384}, transport)
    assert result["stop"] == "explicit_stop" and result["authorized_completion"]
    assert result["budget"]["estimated_usd"] == pytest.approx(
        (100*RATES[model["model"]]["input"]+50*RATES[model["model"]]["output"])/1e6)
    if arm == "plain":
        assert json.loads((tmp_path/"episodes/test/initial_advice.json").read_text()) == {}
