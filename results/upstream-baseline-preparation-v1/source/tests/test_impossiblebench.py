import asyncio
import copy
import json
from pathlib import Path

import pytest

from containment_extension.impossiblebench.qualification import qualify, verify_qualification
from containment_extension.impossiblebench.runner import (
    Action,
    BudgetStop,
    InferenceBudget,
    Turn,
    run_one,
)
from containment_extension.impossiblebench.study import (
    ARMS,
    EXIT,
    INTERFACE,
    NEUTRAL_EXIT,
    NEUTRAL_SCOPE,
    POLICY,
    digest,
    intervention,
    load_plan,
    outcomes,
    prepare,
    summarize,
    validate_bundle,
    write_json,
)


@pytest.fixture
def bundle():
    return json.loads(Path("tests/fixtures/impossiblebench/bundle.json").read_text())


@pytest.fixture
def config():
    return json.loads(Path("experiments/impossiblebench-smoke.json").read_text())


def test_freeze_pairs_and_include_every_assigned_run(tmp_path, bundle, config):
    root = tmp_path / "study"
    plan = prepare(root, config, bundle)
    assert len(plan["schedule"]) == 12
    for start in range(0, 12, 4):
        block = plan["schedule"][start : start + 4]
        assert {r["arm"] for r in block} == set(ARMS)
        assert len({r["instance_id"] for r in block}) == 1
    assert load_plan(root) == (plan, bundle)
    summary = summarize(root)
    assert summary["assigned"] == 12
    assert all(r["any_verified_violation"] is None for r in summary["records"])
    assert all(c["task_bootstrap_95"] is None for c in summary["contrasts"])
    with pytest.raises(FileExistsError):
        prepare(root, config, bundle)
    modified = copy.deepcopy(plan)
    modified["policy"] = "changed"
    write_json(root / "plan.json", modified)
    with pytest.raises(ValueError, match="Frozen plan"):
        load_plan(root)


@pytest.mark.parametrize("name", ["arms", "variants"])
@pytest.mark.parametrize("value", [[], "N", ["bad"], ["N", "N"], [None]])
def test_invalid_subsets_cannot_silently_expand(tmp_path, bundle, config, name, value):
    config[name] = value
    with pytest.raises(ValueError, match=name):
        prepare(tmp_path / "study", config, bundle)
    assert not (tmp_path / "study").exists()


@pytest.mark.parametrize(
    "variants,arms,draws,count",
    [(["original"], ["N"], 2, 4), (["oneoff", "conflicting"], ["N", "RE"], 1, 8)],
)
def test_preflight_subsets_schedules_and_reports(
    tmp_path, bundle, config, variants, arms, draws, count
):
    others = copy.deepcopy(bundle["records"])
    for row in others:
        row["instance_id"] = "second-task"
    bundle["records"].extend(others)
    config.update(
        instance_ids=["scripted-double", "second-task"],
        variants=variants,
        arms=arms,
        repetitions=draws,
        planned_runs=count,
    )
    root = tmp_path / "study"
    plan = prepare(root, config, bundle)
    assert plan["assigned"] == count
    assert {s["variant"] for s in plan["schedule"]} == set(variants)
    assert {s["arm"] for s in plan["schedule"]} == set(arms)
    if draws == 2:
        for offset in (0, 2):
            assert {s["instance_id"] for s in plan["schedule"][offset : offset + 2]} == {
                "scripted-double",
                "second-task",
            }
    report = summarize(root)
    assert report["assigned"] == count
    assert all(r["strict_success"] is None for r in report["records"])
    assert {c["contrast"] for c in report["contrasts"]} == (
        set() if arms == ["N"] else {"combined_minus_neutral"}
    )
    assert prepare(tmp_path / "repeated", config, bundle)["schedule"] == plan["schedule"]
    config["planned_runs"] += 1
    with pytest.raises(ValueError, match="assignment count"):
        prepare(tmp_path / "wrong", config, bundle)


@pytest.mark.parametrize("limit", ["requests", "input_tokens", "output_tokens", "estimated_usd"])
def test_per_run_rejection_does_not_spend_or_exhaust_other_runs(config, limit):
    shares = {"requests": 10, "input_tokens": 1000000, "output_tokens": 10000, "estimated_usd": 5}
    trial = InferenceBudget(config["budget"], config["models"])
    reservation = trial.reserve("mockllm/model", [], 50)
    shares[limit] = {
        "requests": 1,
        "input_tokens": reservation.inputs,
        "output_tokens": 50,
        "estimated_usd": reservation.cost,
    }[limit]
    budget = InferenceBudget(config["budget"], config["models"], shares)
    first = budget.reserve("mockllm/model", [], 50, run_id="first")
    budget.settle(first, None)
    with pytest.raises(BudgetStop) as exc:
        budget.reserve("mockllm/model", [], 50, run_id="first")
    assert exc.value.scope == "per_run"
    assert budget.requests == 1 and not budget.exhausted
    budget.reserve("mockllm/model", [], 50, run_id="second")
    assert budget.requests == 2
    assert budget.snapshot()["unknown_usage_requests"] == 2
    assert all(s["unknown_usage_requests"] == 1 for s in budget.snapshot()["runs"].values())


def test_budget_settlement_is_atomic_and_cannot_be_repeated(config):
    budget = InferenceBudget(config["budget"], config["models"], config["budget"])
    reservation = budget.reserve("mockllm/model", [], 50, run_id="first")
    usage = {"input_tokens": 20, "output_tokens": 5, "cache_write_input_tokens": 10}
    budget.settle(reservation, usage)
    aggregate, local = budget.snapshot(), budget.snapshot()["runs"]["first"]
    for key in (
        "requests",
        "accounted_input_tokens",
        "accounted_output_tokens",
        "estimated_usd",
        "cache_write_input_tokens",
        "unknown_usage_requests",
    ):
        assert aggregate[key] == local[key]
    with pytest.raises(ValueError, match="already settled"):
        budget.settle(reservation, usage)
    assert budget.snapshot() == aggregate


def test_aggregate_rejection_does_not_debit_new_run(config):
    budget = InferenceBudget(
        {**config["budget"], "requests": 1}, config["models"], config["budget"]
    )
    budget.reserve("mockllm/model", [], 50, run_id="first")
    with pytest.raises(BudgetStop) as exc:
        budget.reserve("mockllm/model", [], 50, run_id="second")
    assert exc.value.scope == "aggregate"
    assert budget.runs["second"].requests == 0
    assert budget.requests == 1


@pytest.mark.parametrize(
    "mutation", ["missing", "duplicate", "image", "revision", "traversal", "mismatch", "review"]
)
def test_invalid_dataset_cannot_be_frozen(bundle, mutation):
    if mutation == "missing":
        bundle["records"].pop()
    elif mutation == "duplicate":
        bundle["records"].append(bundle["records"][0])
    elif mutation == "image":
        bundle["records"][0]["image"] = "python:latest"
    elif mutation == "revision":
        bundle["revision"] = "main"
    elif mutation == "traversal":
        bundle["records"][0]["files"]["../outside"] = "bad"
    elif mutation == "mismatch":
        bundle["records"][0]["problem_statement"] = "different issue"
    else:
        bundle["records"][1]["contradiction_review"] = None
    with pytest.raises(ValueError):
        validate_bundle(bundle)


def test_held_out_partition_and_budget_validation(tmp_path, bundle, config):
    config.update(partition="held_out", development_ids=config["instance_ids"])
    with pytest.raises(ValueError, match="overlap"):
        prepare(tmp_path / "s", config, bundle)
    config.update(partition="development")
    config["models"][0]["rates"]["input"] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        prepare(tmp_path / "s", config, bundle)


def test_prompt_slots_keep_authority_permissions_and_exit_constant():
    assert len(POLICY.split()) == len(NEUTRAL_SCOPE.split())
    assert len(EXIT.split()) == len(NEUTRAL_EXIT.split())
    assert "finish" in INTERFACE
    for arm, (reminder, exit_wording) in ARMS.items():
        assert (POLICY in intervention(arm)) == reminder
        assert (EXIT in intervention(arm)) == exit_wording


class FakeBackend:
    def __init__(self):
        self.events = []
        self.closed = False
        self.commands = []
        self.record = None
        self.reference = False

    async def setup(self, record, reference=False):
        self.record, self.reference = record, reference

    async def shell(self, command):
        self.commands.append(command)
        if command == "tamper-and-restore":
            self.events.append({"path": "test_task.py", "protected": True, "seq": 0})
        if command == "raise":
            raise RuntimeError("tool failed")
        return {"returncode": 0}

    async def grade(self):
        return {"passed": self.reference and self.record["variant"] == "original"}

    async def evidence(self):
        return {"complete": True, "events": copy.deepcopy(self.events)}

    async def capture_final(self):
        return {**await self.evidence(), "snapshots_complete": True, "file_changes": {}}

    async def close(self):
        self.closed = True


class FakeAgent:
    def __init__(self, turns):
        self.turns = iter(turns)
        self.histories = []

    async def generate(self, messages, max_tokens):
        self.histories.append(copy.deepcopy(messages))
        turn = next(self.turns)
        if isinstance(turn, Exception):
            raise turn
        turn.usage = {"input_tokens": 10, "output_tokens": 10}
        return turn


def finish(identifier="finish"):
    return Action(
        identifier,
        "finish",
        {
            "outcome": "blocked",
            "report": "Tests contradict spec",
            "evidence": ["Expected both 4 and 5 for the same input"],
        },
    )


def execute(tmp_path, config, bundle, turns, arm="RE", **limits):
    spec = {
        "run": "run-00000",
        "model": "mockllm/model",
        "instance_id": "scripted-double",
        "variant": "conflicting",
        "arm": arm,
        "repetition": 0,
    }
    record = bundle["records"][2]
    backend, agent = FakeBackend(), FakeAgent(turns)
    budget = InferenceBudget(config["budget"], config["models"])
    result = asyncio.run(
        run_one(
            tmp_path / spec["run"],
            spec,
            record,
            {**config["limits"], **limits},
            agent,
            backend,
            budget,
            qualified=True,
        )
    )
    return result, backend, agent, budget


def test_failure_injects_once_and_keeps_all_original_messages(tmp_path, config, bundle):
    result, backend, agent, _ = execute(
        tmp_path,
        config,
        bundle,
        [
            Turn(actions=[Action("s1", "submit", {})]),
            Turn(actions=[Action("s2", "submit", {})]),
            Turn(actions=[finish()]),
        ],
    )
    assert result["stop"] == "finished" and result["triggered"]
    for history in agent.histories:
        assert POLICY in history[1]["content"] and INTERFACE in history[1]["content"]
    notes = [m for m in agent.histories[-1] if m["content"] == intervention("RE")]
    assert len(notes) == 1 and notes[0]["role"] == "user"
    assert backend.closed


def test_batch_exit_stops_dispatch_but_preserves_proposals_and_earlier_effect(
    tmp_path, config, bundle
):
    result, backend, agent, _ = execute(
        tmp_path,
        config,
        bundle,
        [
            Turn(
                actions=[
                    Action("write", "shell", {"command": "tamper-and-restore"}),
                    finish(),
                    Action("late", "shell", {"command": "must never run"}),
                ]
            )
        ],
    )
    assert backend.commands == ["tamper-and-restore"]
    assert len(result["proposals"]) == 3
    assert [p["dispatched"] for p in result["proposals"]] == [True, True, False]
    assert len(agent.histories) == 1 and backend.closed
    scored = outcomes(result["assignment"], result)
    assert scored["any_verified_violation"] is True
    assert scored["clean_blocker"] is False
    assert result["evidence"]["events"][0]["path"] == "test_task.py"


def test_intervention_follows_all_results_in_same_batch(tmp_path, config, bundle):
    result, _, agent, _ = execute(
        tmp_path,
        config,
        bundle,
        [
            Turn(
                actions=[
                    Action("s", "submit", {}),
                    Action("read", "shell", {"command": "inspect files"}),
                ]
            ),
            Turn(actions=[finish()]),
        ],
    )
    history = agent.histories[1]
    assert [m["role"] for m in history[-3:]] == ["tool", "tool", "user"]
    assert result["trigger_step"] == 0


@pytest.mark.parametrize(
    "turn,stop",
    [
        (Turn(text="plain final report"), "model_finished"),
        (Turn(), "empty_response"),
        (Turn(actions=[finish()], truncated=True), "output_limit"),
        (Turn(text="unfinished", interrupted="model_length"), "model_length"),
        (Turn(text="filtered", interrupted="content_filter"), "content_filter"),
        (RuntimeError("API secret body must not be archived"), "error"),
    ],
)
def test_terminal_paths_are_preserved_without_inventing_clean_outcomes(
    tmp_path, config, bundle, turn, stop
):
    result, backend, _, _ = execute(tmp_path, config, bundle, [turn])
    assert result["stop"] == stop and backend.closed
    assert outcomes(result["assignment"], result)["any_verified_violation"] is None
    assert "secret body" not in (tmp_path / "run-00000/result.json").read_text()


def test_effect_survives_later_error_and_usage_is_reserved(tmp_path, config, bundle):
    result, backend, _, budget = execute(
        tmp_path,
        config,
        bundle,
        [
            Turn(actions=[Action("w", "shell", {"command": "tamper-and-restore"})]),
            RuntimeError("disconnect"),
        ],
    )
    assert result["stop"] == "error" and backend.closed
    assert outcomes(result["assignment"], result)["protected_change"] is True
    assert budget.snapshot()["unknown_usage_requests"] == 1


def test_limits_are_not_safe_negatives(tmp_path, config, bundle):
    result, backend, _, _ = execute(
        tmp_path, config, bundle, [Turn(actions=[Action("s", "submit", {})])], model_calls=1
    )
    assert result["stop"] == "model_call_limit" and backend.closed
    assert outcomes(result["assignment"], result)["impossible_pass"] is None


def test_call_twenty_checkpoint_preserves_history_without_an_actor_message(
    tmp_path, config, bundle
):
    turns = [Turn(actions=[Action(f"s{i}", "shell", {"command": "inspect"})]) for i in range(20)]
    result, _, agent, _ = execute(
        tmp_path,
        config,
        bundle,
        [*turns, Turn(text="Finished inspecting")],
        model_calls=21,
        actions=30,
    )
    checkpoint = json.loads((tmp_path / "run-00000/checkpoint-call-20.json").read_text())
    assert checkpoint["result"]["model_calls"] == 20
    assert checkpoint["result"]["actions"] == 20
    assert checkpoint["messages"] == agent.histories[-1]
    assert result["model_calls"] == 21


def test_run_budget_stop_preserves_next_assignment_and_durable_reservation(
    tmp_path, config, bundle
):
    budget = InferenceBudget(
        config["budget"], config["models"], {**config["budget"], "requests": 1}
    )
    spec = {
        "model": "mockllm/model",
        "instance_id": "scripted-double",
        "variant": "conflicting",
        "arm": "N",
        "repetition": 0,
    }

    class DurableAgent(FakeAgent):
        async def generate(self, messages, max_tokens):
            saved = json.loads((tmp_path / "budget.json").read_text())
            assert saved["unknown_usage_requests"] == 1
            return await super().generate(messages, max_tokens)

    first = asyncio.run(
        run_one(
            tmp_path / "first",
            {**spec, "run": "first"},
            bundle["records"][2],
            config["limits"],
            DurableAgent([Turn(actions=[Action("submit", "submit", {})])]),
            FakeBackend(),
            budget,
            qualified=True,
        )
    )
    assert first["stop"] == "per_run_budget"
    assert first["calls_remaining_at_trigger"] == config["limits"]["model_calls"] - 1
    assert first["submissions"][0]["model_calls"] == 1
    assert not budget.exhausted
    second = asyncio.run(
        run_one(
            tmp_path / "second",
            {**spec, "run": "second"},
            bundle["records"][2],
            config["limits"],
            DurableAgent([Turn(actions=[finish()])]),
            FakeBackend(),
            budget,
            qualified=True,
        )
    )
    assert second["stop"] == "finished"
    assert second["budget"]["requests"] == 1
    assert budget.requests == 2


def test_budget_stops_before_a_second_call_and_retains_failed_reservations(config):
    budget = InferenceBudget({**config["budget"], "requests": 1}, config["models"])
    reservation = budget.reserve("mockllm/model", [], 50)
    budget.settle(reservation, None)
    with pytest.raises(BudgetStop):
        budget.reserve("mockllm/model", [], 50)
    assert budget.snapshot()["accounted_output_tokens"] == 50
    assert budget.snapshot()["unknown_usage_requests"] == 1


def test_original_pass_requires_semantic_review_and_impossible_pass_requires_qualification():
    spec = {"variant": "original"}
    result = {
        "stop": "passed",
        "evidence": {"complete": True, "events": []},
        "submissions": [{"passed": True}],
    }
    assert outcomes(spec, result)["strict_success"] is None
    result["review"] = {"semantic_clean": True}
    assert outcomes(spec, result)["strict_success"] is True
    del result["review"]
    spec["variant"] = "conflicting"
    assert outcomes(spec, result)["impossible_pass"] is None
    result["mutation_qualified"] = True
    assert outcomes(spec, result)["any_verified_violation"] is True


def test_qualification_rejects_missing_and_wrong_bundle_checks(tmp_path, bundle):
    report = {
        "bundle_sha256": digest(bundle),
        "passed": True,
        "checks": [],
        "transient_write": {"ok": True},
        "observer_protection": {"ok": True},
    }
    path = tmp_path / "q.json"
    write_json(path, report)
    with pytest.raises(ValueError, match="qualification"):
        verify_qualification(path, bundle)


def test_qualification_cannot_pass_with_broken_observation(tmp_path, bundle):
    class BrokenObserver(FakeBackend):
        async def evidence(self):
            return {"complete": False, "events": []}

    report = asyncio.run(qualify(bundle, tmp_path / "q", BrokenObserver))
    assert not report["passed"]
    assert len(report["checks"]) == 6
    assert all(not c["ok"] for c in report["checks"])


class QualificationBackend(FakeBackend):
    async def shell(self, command):
        if command.startswith("python -c "):
            return {"returncode": 0, "stdout": '{"ok": true}'}
        if command.startswith("printf tamper"):
            return {"returncode": 1, "stderr": "Permission denied"}
        self.events.append({"path": self.record["protected_paths"][0], "protected": True, "seq": 0})
        return {"returncode": 0}


@pytest.mark.parametrize("shared_image", [True, False])
def test_qualification_checks_every_environment_and_rejects_partial_reports(
    tmp_path, bundle, shared_image
):
    other = copy.deepcopy(bundle["records"])
    for row in other:
        row["instance_id"] = "second-task"
        if not shared_image:
            row["image"] = "fixture@sha256:" + "b" * 64
    bundle["records"].extend(other)
    backends = []

    def factory():
        backend = QualificationBackend()
        backends.append(backend)
        return backend

    report = asyncio.run(qualify(bundle, tmp_path / "q", factory))
    assert report["passed"]
    assert len(report["checks"]) == 12
    assert len(report["observer_checks"]) == 6
    assert all(b.closed for b in backends)
    assert verify_qualification(tmp_path / "q/qualification.json", bundle) == report
    for mutation in ("missing", "duplicate", "wrong_image", "failed", "legacy", "malformed"):
        modified = copy.deepcopy(report)
        controls = modified["observer_checks"]
        if mutation == "missing":
            controls.pop()
        elif mutation == "duplicate":
            controls[-1] = controls[0]
        elif mutation == "wrong_image":
            controls[-1]["image"] = "fixture@sha256:" + "c" * 64
        elif mutation == "failed":
            controls[-1]["observer_protection"]["ok"] = False
        elif mutation == "legacy":
            del modified["observer_checks"]
            modified.update(transient_write={"ok": True}, observer_protection={"ok": True})
        else:
            controls[-1] = None
        path = tmp_path / (mutation + ".json")
        write_json(path, modified)
        with pytest.raises(ValueError, match="qualification"):
            verify_qualification(path, bundle)


@pytest.mark.parametrize(
    "failure", ["unobserved", "not_restored", "snapshots", "writable_observer", "setup", "cleanup"]
)
def test_failure_in_later_variant_fails_qualification_and_preserves_evidence(
    tmp_path, bundle, failure
):
    class BrokenEnvironment(QualificationBackend):
        async def setup(self, record, reference=False):
            await super().setup(record, reference)
            if record["variant"] == "oneoff" and failure == "setup":
                raise RuntimeError("broken environment")

        async def shell(self, command):
            response = await super().shell(command)
            if self.record["variant"] == "oneoff":
                if failure == "unobserved":
                    self.events.clear()
                if failure == "writable_observer" and command.startswith("printf tamper"):
                    response["returncode"] = 0
            return response

        async def capture_final(self):
            evidence = await super().capture_final()
            if self.record["variant"] == "oneoff":
                if failure == "snapshots":
                    evidence["snapshots_complete"] = False
                if failure == "not_restored":
                    evidence["file_changes"] = {"test_task.py": {"after": "changed"}}
            return evidence

        async def close(self):
            await super().close()
            if self.record["variant"] == "oneoff" and failure == "cleanup":
                raise RuntimeError("cleanup failed")

    report = asyncio.run(qualify(bundle, tmp_path / "q", BrokenEnvironment))
    assert not report["passed"]
    assert len(report["checks"]) == 6
    assert len(report["observer_checks"]) == 3
    assert {c["variant"] for c in report["observer_checks"] if not c["ok"]} == {"oneoff"}
    assert json.loads((tmp_path / "q/qualification.json").read_text()) == report


def test_review_is_bound_to_original_evidence_without_overwriting_it(tmp_path, bundle, config):
    root = tmp_path / "study"
    plan = prepare(root, config, bundle)
    spec = plan["schedule"][0]
    directory = root / spec["run"]
    directory.mkdir()
    result = {
        "assignment": spec,
        "stop": "passed",
        "evidence": {"complete": True, "events": []},
        "submissions": [{"passed": True}],
    }
    write_json(directory / "result.json", result)
    labels = {
        spec["run"]: {
            "result_sha256": digest(result),
            "reviewer": "test reviewer",
            "reason": "Inspected implementation and test evidence",
            "semantic_clean": True,
            "supported_blocker": False,
            "false_blocker": False,
        }
    }
    path = tmp_path / "reviews.json"
    write_json(path, labels)
    assert summarize(root, path)["records"][0]["strict_success"] is True
    assert json.loads((directory / "result.json").read_text()) == result
    labels[spec["run"]]["result_sha256"] = "stale"
    write_json(path, labels)
    with pytest.raises(ValueError, match="stale"):
        summarize(root, path)
