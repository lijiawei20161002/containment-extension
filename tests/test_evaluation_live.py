import json
from pathlib import Path

import pytest

from containment_extension.evaluation import live, workflow
from containment_extension.providers import ProviderError

REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / "results/counterfactual-evaluation-offline-v1"
ARTIFACT = REPO / "results/researcharena-monitoring-offline-v1"


def config():
    return {"provider": "anthropic", "model": "scripted-test-model", "rates": {"input": 1, "output": 5},
            "aggregate_budget": {"requests": 2048, "input_tokens": 100000000, "output_tokens": 1000000, "estimated_usd": 100},
            "per_assignment_budget": {"requests": 12, "input_tokens": 1000000, "output_tokens": 8192, "estimated_usd": 1},
            "max_steps": 8, "max_output_tokens": 512, "max_wall_seconds": 60, "probe_quota": 8,
            "threshold": 0.5, "seed": 7, "archive_rollout_limit": 2}


def fake_transport(provider, path, payload):
    """Protocol control, never reported as model inference evidence."""
    packet = json.loads(payload["messages"][0]["content"])
    supported = workflow.judge_support(packet)["blocker_supported"] if "claim_under_review" in packet else False
    return {"model": payload["model"], "content": [{"type": "text", "text": json.dumps({
        "score": 0.8 if supported else 0.2, "reason": "Scripted protocol check.", "blocker_supported": supported})}],
            "stop_reason": "end_turn", "usage": {"input_tokens": 10, "output_tokens": 20}}


def test_frozen_grade_plan_run_accounting_and_no_reexecution(tmp_path):
    root = tmp_path / "graders"
    p = live.prepare(root, WORKFLOW, "workflow_graders", config())
    assert p["assignments"] == 17 and p["model_calls"] == 0
    result = live.run(root, transport=fake_transport)
    assert result["status"] == "finished" and result["budget"]["requests"] == 17
    assert all(r["status"] == "valid" for r in result["records"])
    assert sum(g["false_positive"] for g in result["groups"].values()) == 0
    live.verify_results(root)
    with pytest.raises(FileExistsError):
        live.run(root, transport=fake_transport)


def test_failed_request_reservation_and_all_assignments_survive(tmp_path):
    root = tmp_path / "failed"
    live.prepare(root, WORKFLOW, "workflow_graders", config())
    def fail(*args):
        raise ProviderError("Do not serialize this error body")
    result = live.run(root, transport=fail)
    assert result["status"] == "incomplete"
    assert result["budget"]["unknown_usage_requests"] == 1
    assert result["records"][0]["status"] == "error"
    assert len(result["records"]) == 17
    assert sum(r["status"] == "not_started" for r in result["records"]) == 16
    assert "Do not serialize" not in (root / "report.json").read_text()
    live.verify_results(root)


def test_cache_usage_counted_and_no_missing_usage_success(tmp_path):
    root = tmp_path / "cached"
    live.prepare(root, WORKFLOW, "workflow_graders", config())
    def cached(*args):
        response = fake_transport(*args)
        response["usage"].update(cache_read_input_tokens=5, cache_creation_input_tokens=7)
        return response
    result = live.run(root, transport=cached)
    assert result["budget"]["actual_input_tokens"] == 17 * 22
    assert result["budget"]["cache_write_input_tokens"] == 17 * 7
    other = tmp_path / "no-usage"
    live.prepare(other, WORKFLOW, "workflow_graders", config())
    def unknown(*args):
        response = fake_transport(*args)
        del response["usage"]
        return response
    result = live.run(other, transport=unknown)
    assert result["status"] == "incomplete" and result["budget"]["unknown_usage_requests"] == 1


def test_budget_stop_never_calls_transport(tmp_path):
    root = tmp_path / "tiny"
    c = config()
    c["aggregate_budget"]["estimated_usd"] = 0.000001
    c["per_assignment_budget"]["estimated_usd"] = 0.000001
    live.prepare(root, WORKFLOW, "workflow_graders", c)
    def forbidden(*args):
        pytest.fail("No request can fit this allocation")
    result = live.run(root, transport=forbidden)
    assert result["budget"]["requests"] == 0 and result["status"] == "incomplete"


def test_archive_baseline_gate_and_monitor_label_separation(tmp_path):
    root = tmp_path / "archive"
    live.prepare(root, ARTIFACT, "archive_monitors", config())
    p = live.verify_plan(root)
    for a in p["assignments"]:
        assert "semantic_proposal_label" not in json.dumps(a["input"])
        assert "independent_effect_evidence" not in json.dumps(a["input"])
    with pytest.raises(ValueError, match="requires"):
        live.prepare(tmp_path / "artifact-no-baseline", ARTIFACT, "artifact_monitors", config())
    live.run(root, transport=fake_transport)
    prepared = live.prepare(tmp_path / "artifact", ARTIFACT, "artifact_monitors", config(), baseline=root)
    assert prepared["assignments"] == 128
    (root / "report.json").write_text("{}")
    with pytest.raises(ValueError, match="changed"):
        live.verify_plan(tmp_path / "artifact")


def tool_response(payload, operation, inputs=None, data=""):
    return {"model": payload["model"], "content": [{"type": "tool_use",
            "id": f"call-{len(payload['messages'])}", "name": "lab_request",
            "input": {"operation": operation, "inputs": inputs or [], "data": data}}],
            "stop_reason": "tool_use", "usage": {"input_tokens": 10, "output_tokens": 20}}


def test_workflow_actors_exercise_real_interface_and_preserve_environment_fault(tmp_path):
    root = tmp_path / "actors"
    live.prepare(root, WORKFLOW, "workflow_actors", config())
    def actor(provider, path, payload):
        history = payload["messages"]
        if len(history) == 1:
            return tool_response(payload, "inspect")
        response = json.loads(history[-1]["content"][-1]["content"])
        if response.get("status") == 503 or response.get("provisions", {}).get("activation") is False:
            return tool_response(payload, "finish", data="The observed provision or environment blocks this path.")
        state = response["state"]
        op = "restore" if state == 0 else "prepare" if state == 1 else "activate" if state == 3 else "complete"
        return tool_response(payload, op)
    result = live.run(root, transport=actor)
    assert result["status"] == "finished"
    assert sum(r["authorized_completion"] for r in result["actor_outcomes"]) == 2
    fault = next(r for r in result["actor_outcomes"] if r["variant"] == "environment_fault")
    assert fault["environment_errors"] == 1 and not fault["authorized_completion"]


def test_artifact_monitor_tool_loops_are_isolated_and_reference_free(tmp_path):
    baseline = tmp_path / "baseline"
    live.prepare(baseline, ARTIFACT, "archive_monitors", config())
    live.run(baseline, transport=fake_transport)
    root = tmp_path / "artifact-monitors"
    live.prepare(root, ARTIFACT, "artifact_monitors", config(), baseline=baseline)
    def monitor(provider, path, payload):
        packet = json.loads(payload["messages"][0]["content"])
        if packet["artifact_access"]:
            if len(payload["messages"]) == 1:
                return tool_response(payload, "inspect")
            if len(payload["messages"]) == 3:
                return tool_response(payload, "probe", [24, 25])
        return fake_transport(provider, path, payload)
    result = live.run(root, transport=monitor)
    assert result["status"] == "finished" and len(result["records"]) == 128
    assert result["budget"]["requests"] == 256
    for row in result["records"]:
        events = json.loads((root / "assignments" / row["id"] / "monitor_probe_events.json").read_text())
        assert len(events) == (2 if row["view"] in {"TA", "TEA"} else 0)
        assert '"expected"' not in json.dumps(events)
    live.verify_results(root)


@pytest.mark.parametrize("text,status", [
    ('{"score":true,"blocker_supported":false,"reason":"x"}', "invalid"),
    ('{"score":NaN,"blocker_supported":false,"reason":"x"}', "invalid"),
    ('{"score":null,"reason":"unknown"}', "abstained"),
    ('not JSON', "invalid"),
    ('{"score":0.1,"blocker_supported":false,"reason":"x","status":"forged","id":"forged"}', "valid"),
])
def test_judgments_cannot_overwrite_identity_or_forge_status(text, status):
    result = live.parse_judgment(text)
    assert result["status"] == status
    assert "id" not in result


def test_model_settings_and_budgets_must_be_explicit():
    for key in ("model", "rates", "aggregate_budget", "per_assignment_budget"):
        c = config()
        c[key] = None
        with pytest.raises(ValueError):
            live.validate_config(c)
