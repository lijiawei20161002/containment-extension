import asyncio
import json
from types import SimpleNamespace

import pytest

pytest.importorskip("inspect_ai")

from inspect_ai.model import ChatMessageUser, GenerateConfig, ModelOutput, ModelUsage

from containment_extension.impossiblebench.runner import BudgetStop, InferenceBudget
from containment_extension.impossiblebench.study import write_json
from scripts.upstream_baseline import compose, guarded_model, summarize


def test_upstream_budget_guards_real_tool_schema_and_preserves_unknown_usage(tmp_path):
    calls = []

    async def generate(*args):
        calls.append(args)
        if len(calls) == 1:
            return ModelOutput(
                model="mockllm/model",
                usage=ModelUsage(
                    input_tokens=10,
                    output_tokens=3,
                    input_tokens_cache_read=100,
                    input_tokens_cache_write=20,
                    total_tokens=133,
                ),
            )
        raise RuntimeError("provider disconnect")

    config = {"requests": 2, "input_tokens": 100000, "output_tokens": 1000, "estimated_usd": 1}
    budget = InferenceBudget(
        config, [{"name": "mockllm/model", "rates": {"input": 1, "output": 5}}], config
    )
    model = SimpleNamespace(api=SimpleNamespace(generate=generate))
    guarded_model(model, budget, {"run": "one", "model": "mockllm/model"}, tmp_path)
    args = (
        [ChatMessageUser(content="task")],
        [],
        "auto",
        GenerateConfig(max_tokens=100, max_retries=0, cache_prompt=False),
    )
    asyncio.run(model.api.generate(*args))
    assert budget.inputs == 130
    assert budget.cache_reads == 100 and budget.cache_writes == 20
    with pytest.raises(RuntimeError, match="disconnect"):
        asyncio.run(model.api.generate(*args))
    saved = json.loads((tmp_path / "budget.json").read_text())
    assert saved["unknown_usage_requests"] == 1
    assert saved["runs"]["one"]["unknown_usage_requests"] == 1
    with pytest.raises(BudgetStop):
        asyncio.run(model.api.generate(*args))
    assert len(calls) == 2


def test_upstream_summary_keeps_missing_runs_and_original_controls_separate(tmp_path):
    schedule = [
        {"run": f"r{i}", "variant": variant}
        for i, variant in enumerate(["original", "oneoff", "conflicting"])
    ]
    write_json(
        tmp_path / "plan.json",
        {
            "assigned": 3,
            "schedule": schedule,
            "config": {"variants": [s["variant"] for s in schedule]},
        },
    )
    write_json(tmp_path / "results.json", [{"assignment": schedule[1], "raw_score": 1}])
    report = summarize(tmp_path)
    assert report["assigned"] == 3
    assert [c["unknown_scores"] for c in report["cells"]] == [1, 0, 1]
    assert [c["raw_passes"] for c in report["cells"]] == [0, 1, 0]
    assert report["cells"][0]["assigned_pass_rate_bounds"] == [0, 1]


def test_baseline_compose_disables_network_mounts_privileges_and_image_pulls():
    import yaml

    service = yaml.safe_load(compose("sha256:" + "a" * 64))["services"]["default"]
    assert service["network_mode"] == "none"
    assert service["user"] == "1000:1000"
    assert service["cap_drop"] == ["ALL"]
    assert service["pull_policy"] == "never" and service["x-local"]
    assert not service.get("volumes") and not service.get("ports")
    with pytest.raises(ValueError):
        compose("python:latest")
