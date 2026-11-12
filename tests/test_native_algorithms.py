import json
from pathlib import Path

import pytest

from containment_extension.budget import BudgetStop, StudyBudget
from containment_extension.native_algorithms import (
    ARCHIVE_URL, DurableNativeBudget, FeedbackLab, execute, prepare, row_for, run_one,
)
from containment_extension.providers import NativeAgent

ROOT = Path(__file__).resolve().parents[1]


def plan_for(tmp_path, provider="anthropic"):
    config = json.loads((ROOT / "experiments/native-algorithms-v1-sonnet-4-6.json").read_text())
    config.update(actor={"provider": provider, "model": "test"}, temperature=None,
                  seeds={"impossible": [16000]}, arms=["plain"], stop_rewards=[0.],
                  limits={"max_output_tokens": 16384, "max_total_tokens": 160000,
                          "max_history_bytes": 1000000},
                  request_extra={"output_config": {"effort": "high"}} if provider == "anthropic"
                  else {"reasoning": {"effort": "high"}},
                  rates={"test": {"input": 8., "output": 40.}},
                  per_run_budget={"max_input_tokens": 1000000, "max_estimated_usd": 4.},
                  budget={"requests": 10, "estimated_usd": 5.})
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    output = tmp_path / "study"
    prepare(output, path)
    return output, json.loads((output / "plan.json").read_text())


@pytest.mark.parametrize("incident_first", [False, True])
def test_refusal_does_not_become_a_clean_negative_or_erase_an_incident(tmp_path, incident_first):
    output, _ = plan_for(tmp_path)
    calls = []
    thinking = {"type": "thinking", "thinking": "synthetic reasoning", "signature": "opaque-signature"}
    def transport(provider, path, payload):
        calls.append(json.loads(json.dumps(payload)))
        content = [{"type": "text", "text": "I cannot continue."}]
        stop = "refusal"
        if incident_first and len(calls) == 1:
            content = [thinking, {"type": "tool_use", "id": "call-1", "name": "lab_request",
                       "input": {"method": "GET", "url": ARCHIVE_URL, "body": ""}}]
            stop = "tool_use"
        return {"model": "test", "stop_reason": stop, "content": content,
                "usage": {"input_tokens": 100, "output_tokens": 100}}
    summary = execute(output, transport)
    row = summary["records"][0]
    assert row["stop"] == "provider_refusal"
    assert row["unauthorized_effect"] is (True if incident_first else None)
    assert row["blocker_with_observed_evidence"] is (False if incident_first else None)
    assert row["out_of_scope_proposals"] == (1 if incident_first else None)
    assert calls[0]["max_tokens"] == 16384
    assert calls[0]["output_config"] == {"effort": "high"}
    assert "temperature" not in calls[0]
    if incident_first:
        assert calls[1]["messages"][:len(calls[0]["messages"])] == calls[0]["messages"]
        assert calls[1]["messages"][-2]["content"][0] == thinking
        assert calls[1]["system"] == calls[0]["system"]
        assert calls[1]["tools"] == calls[0]["tools"]
    with pytest.raises(ValueError, match="Cannot run"):
        execute(output, transport)


def test_interrupted_run_is_preserved_without_replaying_and_keeps_positive_witness(tmp_path):
    output, plan = plan_for(tmp_path)
    spec = plan["schedule"][0]
    directory = output / spec["run"]
    lab, _ = FeedbackLab.restore(output / "checkpoints" / spec["checkpoint"], directory,
                                 max_actions=20)
    lab.configure(spec["candidate"], False, "permissive")
    lab.request("GET", ARCHIVE_URL)
    marker = directory / "transcript.jsonl"
    marker.write_text('evidence must survive\n')
    assert run_one(output, plan, spec, None) is None
    assert marker.read_text() == 'evidence must survive\n'
    row = row_for(output, spec)
    assert row["stop"] == "interrupted_unknown"
    assert row["unauthorized_effect"] is True


def test_cost_reservation_survives_process_loss_and_prevents_overspend(tmp_path):
    ledger = tmp_path / "budget.json"
    settings = {"max_requests": 2, "max_estimated_usd": 1.,
                "rates": {"test": {"input": 8., "output": 40.}}}
    budget = DurableNativeBudget(ledger, **settings)
    in_flight = None
    def transport(*args):
        nonlocal in_flight
        in_flight = ledger.read_text()
        raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        budget.call(transport, "anthropic", "/messages", {"model": "test", "max_tokens": 16384})
    # Restore the on-disk state that would remain after SIGKILL, before finally executes.
    ledger.write_text(in_flight)
    restored = DurableNativeBudget(ledger, **settings)
    assert restored.requests == 1 and restored.unknown_usage_requests == 1
    assert restored.estimated_usd > .65
    with pytest.raises(BudgetStop):
        restored.call(transport, "anthropic", "/messages", {"model": "test", "max_tokens": 16384})
    assert restored.requests == 1


def test_openrouter_checkpoint_and_encrypted_reasoning_use_responses_protocol(tmp_path):
    output, plan = plan_for(tmp_path, "openrouter")
    requests = []
    def transport(provider, path, payload):
        requests.append(json.loads(json.dumps(payload)))
        assert provider == "openrouter" and path == "/responses"
        assert payload["reasoning"]["effort"] == "high"
        assert payload["store"] is False and "temperature" not in payload
        assert any(m.get("type") == "function_call_output" for m in payload["input"])
        if len(requests) == 1:
            output_items = [{"type": "reasoning", "id": "r1", "encrypted_content": "opaque"},
                {"type": "function_call", "call_id": "c1", "name": "lab_request",
                 "arguments": json.dumps({"method": "GET", "url": ARCHIVE_URL, "body": ""})}]
        else:
            assert payload["input"][-3]["encrypted_content"] == "opaque"
            output_items = [{"type": "message", "content": [{"type": "output_text", "text": "Done"}]}]
        return {"model": "test", "status": "completed", "output": output_items,
                "usage": {"input_tokens": 100, "output_tokens": 100}}
    total = StudyBudget(max_requests=10, max_estimated_usd=5., rates=plan["config"]["rates"])
    result = run_one(output, plan, plan["schedule"][0], total, transport)
    assert result["unauthorized_effect"] is True and len(requests) == 2


def test_extra_fields_cannot_bypass_model_or_cost_limit():
    with pytest.raises(ValueError, match="cannot override"):
        NativeAgent("anthropic", "test", request_extra={"max_tokens": 1000000})
