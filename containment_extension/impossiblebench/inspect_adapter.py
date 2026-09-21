"""Inspect integration. Import only when the optional evaluation extra is installed."""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai import Task, eval
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessage, GenerateConfig, Model, get_model
from inspect_ai.scorer import Score, scorer
from inspect_ai.solver import solver
from inspect_ai.tool import ToolInfo
from pydantic import TypeAdapter

from .docker import DockerBackend
from .qualification import verify_qualification
from .runner import TOOLS, Action, InferenceBudget, Turn, run_one
from .study import digest, load_plan, outcomes, summarize, validate_bundle, write_json

CHAT = TypeAdapter(ChatMessage)


class InspectAgent:
    def __init__(self, model: Model):
        client = getattr(model.api, "client", None)
        if getattr(client, "max_retries", 0) != 0:
            raise ValueError("Configure provider SDK max_retries=0 before starting the study")
        self.model = model
        self.last_output = None

    async def generate(self, messages: list[dict], max_tokens: int) -> Turn:
        output = await self.model.generate(
            input=[CHAT.validate_python(m) for m in messages],
            tools=[ToolInfo.model_validate(t) for t in TOOLS],
            config=GenerateConfig(
                max_tokens=max_tokens,
                max_retries=0,
                parallel_tool_calls=False,
                cache=False,
                cache_prompt=False,
            ),
        )
        self.last_output = output
        usage = (
            {
                # Inspect excludes cache reads/writes from input_tokens.
                "input_tokens": output.usage.input_tokens
                + (output.usage.input_tokens_cache_read or 0)
                + (output.usage.input_tokens_cache_write or 0),
                "output_tokens": output.usage.output_tokens,
                "cache_read_input_tokens": output.usage.input_tokens_cache_read or 0,
                "cache_write_input_tokens": output.usage.input_tokens_cache_write or 0,
            }
            if output.usage
            else None
        )
        return Turn(
            text=output.completion,
            actions=[
                Action(c.id, c.function, c.arguments) for c in output.message.tool_calls or []
            ],
            usage=usage,
            truncated=any(c.stop_reason == "max_tokens" for c in output.choices),
            interrupted=next(
                (
                    c.stop_reason
                    for c in output.choices
                    if c.stop_reason in {"model_length", "content_filter"}
                ),
                None,
            ),
            raw=output.model_dump(mode="json", exclude_none=True),
            message=output.message.model_dump(mode="json", exclude_none=True),
        )


def build_task(
    root: Path,
    model_name: str,
    budget: InferenceBudget,
    *,
    backend_factory=DockerBackend,
    agent_factory=None,
) -> Task:
    plan, bundle = load_plan(root)
    records = validate_bundle(bundle)
    assignments = [s for s in plan["schedule"] if s["model"] == model_name]
    if not assignments:
        raise ValueError("Model is absent from the frozen assignment schedule")
    qualification = verify_qualification(root / "qualification.json", bundle)

    @solver
    def transfer_solver():
        async def solve(state, generate):
            spec = state.metadata["assignment"]
            record = records[(spec["instance_id"], spec["variant"])]
            agent = agent_factory() if agent_factory else InspectAgent(get_model())
            result = await run_one(
                root / spec["run"],
                spec,
                record,
                plan["config"]["limits"],
                agent,
                backend_factory(),
                budget,
                qualified=qualification["passed"],
            )
            saved = json.loads((root / spec["run"] / "messages.json").read_text())
            state.messages = [CHAT.validate_python(m) for m in saved]
            if getattr(agent, "last_output", None) is not None:
                state.output = agent.last_output
            state.metadata["transfer_outcomes"] = outcomes(spec, result)
            state.completed = True
            return state

        return solve

    @scorer(metrics=[])
    def transfer_scorer():
        async def score(state, target):
            row = state.metadata["transfer_outcomes"]
            # No aggregate Inspect accuracy: U is unknown and must not become a zero.
            values = {
                key: "U" if row[key] is None else "C" if row[key] else "I"
                for key in (
                    "raw_pass",
                    "impossible_pass",
                    "protected_change",
                    "any_verified_violation",
                    "strict_success",
                    "clean_blocker",
                )
            }
            return Score(
                value=values,
                metadata=row,
                explanation="Use summary.json for assigned-denominator estimates; U=unknown.",
            )

        return score

    return Task(
        name="impossiblebench_transfer",
        dataset=[
            Sample(
                id=s["run"],
                input=records[(s["instance_id"], s["variant"])]["problem_statement"],
                metadata={"assignment": s},
            )
            for s in assignments
        ],
        solver=transfer_solver(),
        scorer=transfer_scorer(),
        fail_on_error=False,
        metadata={
            "plan_sha256": digest(plan),
            "dataset_kind": bundle["kind"],
            "upstream_revision": plan["upstream_revision"],
        },
    )


def run_study(root: Path, qualification_path: Path) -> dict:
    plan, bundle = load_plan(root)
    qualification = verify_qualification(qualification_path, bundle)
    # One execution per plan. Interrupted runs stay assigned and cannot be silently replaced.
    with (root / "execution.json").open("x") as stream:
        json.dump({"plan_sha256": digest(plan), "status": "started"}, stream)
    write_json(root / "qualification.json", qualification)
    budget = InferenceBudget(plan["config"]["budget"], plan["config"]["models"])
    try:
        for model in plan["config"]["models"]:
            task = build_task(root, model["name"], budget)
            runtime_model = get_model(
                model["name"], config=GenerateConfig(max_retries=0), max_retries=0, memoize=False
            )
            eval(
                task,
                model=runtime_model,
                log_dir=str(root / "inspect-logs"),
                max_samples=1,
                max_tasks=1,
                max_retries=0,
                retry_on_error=0,
                log_model_api=True,
                fail_on_error=False,
            )
    finally:
        write_json(root / "budget.json", budget.snapshot())
        report = summarize(root)
        write_json(
            root / "execution.json",
            {"plan_sha256": digest(plan), "status": "ended", "assigned": report["assigned"]},
        )
    return report
