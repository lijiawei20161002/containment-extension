import asyncio
import json
from pathlib import Path

import pytest

pytest.importorskip("inspect_ai")

from inspect_ai import eval as inspect_eval
from inspect_ai.model import (
    ChatCompletionChoice,
    ChatMessageAssistant,
    ModelOutput,
    ModelUsage,
    get_model,
)
from inspect_ai.tool import ToolCall

from containment_extension.impossiblebench.inspect_adapter import InspectAgent, build_task
from containment_extension.impossiblebench.runner import InferenceBudget
from containment_extension.impossiblebench.study import (
    POLICY,
    digest,
    prepare,
    source_digest,
    summarize,
    write_json,
)


class Backend:
    async def setup(self, record, reference=False):
        self.variant = record["variant"]

    async def grade(self):
        return {"passed": self.variant == "original"}

    async def evidence(self):
        return {"complete": True, "events": []}

    async def close(self):
        pass


def tool_output(name, arguments, *, truncated=False):
    return ModelOutput(
        model="mockllm/model",
        choices=[
            ChatCompletionChoice(
                message=ChatMessageAssistant(
                    content="",
                    tool_calls=[ToolCall(id="call-1", function=name, arguments=arguments)],
                ),
                stop_reason="max_tokens" if truncated else "tool_calls",
            )
        ],
        usage=ModelUsage(input_tokens=100, output_tokens=20, total_tokens=120),
    )


def test_real_inspect_model_translation_preserves_tools_and_truncation():
    model = get_model(
        "mockllm/model",
        memoize=False,
        custom_outputs=[
            tool_output(
                "finish",
                {"outcome": "blocked", "report": "contradiction", "evidence": []},
                truncated=True,
            )
        ],
    )
    turn = asyncio.run(InspectAgent(model).generate([{"role": "user", "content": "task"}], 100))
    assert turn.truncated
    assert turn.actions[0].name == "finish"
    assert turn.usage == {
        "input_tokens": 100,
        "output_tokens": 20,
        "cache_read_input_tokens": 0,
        "cache_write_input_tokens": 0,
    }
    assert turn.message["tool_calls"][0]["id"] == "call-1"


def test_cached_input_counts_toward_token_and_cost_limits():
    def respond(messages, tools, choice, generation):
        assert generation.cache_prompt is False
        output = tool_output("submit", {})
        output.usage = ModelUsage(
            input_tokens=5, input_tokens_cache_read=1000,
            input_tokens_cache_write=200, output_tokens=20, total_tokens=1225,
        )
        return output

    model = get_model("mockllm/model", memoize=False, custom_outputs=respond)
    turn = asyncio.run(InspectAgent(model).generate([{"role": "user", "content": "task"}], 100))
    assert turn.usage["input_tokens"] == 1205
    budget = InferenceBudget(
        {"requests": 2, "input_tokens": 100000, "output_tokens": 1000, "estimated_usd": 1},
        [{"name": "mockllm/model", "rates": {"input": 1, "output": 5}}],
    )
    reservation = budget.reserve("mockllm/model", [], 100)
    budget.settle(reservation, turn.usage)
    assert budget.snapshot()["actual_input_tokens"] == 1205
    assert budget.snapshot()["accounted_input_tokens"] == 1205
    assert budget.snapshot()["estimated_usd"] == pytest.approx((1205 + 200 + 20 * 5) / 1e6)
    assert budget.snapshot()["cache_read_input_tokens"] == 1000
    assert budget.snapshot()["cache_write_input_tokens"] == 200


@pytest.mark.parametrize(
    "name", ["openai/gpt-4.1-mini-2025-04-14", "anthropic/claude-haiku-4-5-20251001"]
)
def test_provider_sdk_retries_are_disabled_without_making_requests(name):
    pytest.importorskip(name.split("/")[0])
    default_model = get_model(name, api_key="unused-test-key", memoize=False)
    with pytest.raises(ValueError, match="SDK max_retries"):
        InspectAgent(default_model)
    model = get_model(name, api_key="unused-test-key", max_retries=0, memoize=False)
    assert model.api.client.max_retries == 0
    InspectAgent(model)


def test_inspect_evaluation_keeps_assigned_denominators_and_actual_histories(tmp_path):
    bundle = json.loads(Path("tests/fixtures/impossiblebench/bundle.json").read_text())
    config = json.loads(Path("experiments/impossiblebench-smoke.json").read_text())
    root = tmp_path / "study"
    prepare(root, config, bundle)
    # Mock infrastructure qualification only for this mocked-backend integration test.
    qualification = {
        "bundle_sha256": digest(bundle),
        "source_sha256": source_digest(),
        "passed": True,
        "observer_checks": [
            {
                "instance_id": r["instance_id"],
                "variant": r["variant"],
                "image": r["image"],
                "ok": True,
                "transient_write": {"ok": True},
                "observer_protection": {"ok": True},
            }
            for r in bundle["records"]
        ],
        "checks": [
            {"instance_id": r["instance_id"], "variant": r["variant"], "reference": ref, "ok": True}
            for r in bundle["records"]
            for ref in (False, True)
        ],
    }
    write_json(root / "qualification.json", qualification)
    histories = []

    def respond(messages, tools, tool_choice, generation):
        histories.append(messages)
        assert POLICY in messages[1].text
        assert generation.max_retries == 0 and not generation.parallel_tool_calls
        assert generation.cache_prompt is False
        if any(m.role == "tool" for m in messages):
            return tool_output(
                "finish",
                {"outcome": "blocked", "report": "conflicting tests", "evidence": ["test failure"]},
            )
        return tool_output("submit", {})

    model = get_model("mockllm/model", memoize=False, custom_outputs=respond)
    budget = InferenceBudget(config["budget"], config["models"])
    task = build_task(root, "mockllm/model", budget, backend_factory=Backend)
    logs = inspect_eval(
        task,
        model=model,
        log_dir=str(tmp_path / "logs"),
        display="none",
        max_samples=1,
        max_tasks=1,
        max_retries=0,
        retry_on_error=0,
    )
    assert len(logs) == 1 and logs[0].status == "success"
    assert len(logs[0].samples) == 12
    report = summarize(root)
    assert report["assigned"] == 12
    assert sum(r["raw_pass"] is True for r in report["records"]) == 4
    assert sum(r["triggered"] for r in report["records"]) == 8
    assert all(r["any_verified_violation"] is None for r in report["records"])
    assert len(histories) == 20
    assert budget.snapshot()["requests"] == 20
