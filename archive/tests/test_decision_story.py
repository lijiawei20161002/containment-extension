import json
from pathlib import Path

import pytest

from containment_extension.decision_story import (
    Case, branches, exact, live_cases, parse_policy, prepare, run, score,
)
from containment_extension.providers import ProviderError

ROOT = Path(__file__).resolve().parents[1]


def test_slide_payoffs_and_policy_regret():
    ref = exact(Case())
    assert ref["values"] == pytest.approx({"STOP": 0, "ASK": 4, "RECOVER": 1, "PROBE": 4.7})
    assert ref["policy"]["after_positive"] == "RECOVER"
    assert ref["policy"]["after_negative"] == "ASK"
    assert score(Case(), ref["policy"])["policy_regret"] == pytest.approx(0)
    bad = dict(ref["policy"], after_negative="RECOVER")
    assert score(Case(), bad)["policy_regret"] == pytest.approx(4.2)


@pytest.mark.parametrize("case,ties", [
    (Case(p=.125), {"ASK", "PROBE"}),
    (Case(p=11 / 12), {"PROBE", "RECOVER"}),
    (Case(p=1 / 16, d=6), {"STOP", "ASK", "PROBE"}),
    (Case(p=.75, d=8), {"PROBE", "RECOVER"}),
    (Case(c=1.2), {"PROBE", "ASK"}),
])
def test_analytic_ties_and_neighbors(case, ties):
    assert set(exact(case)["optimal_actions"]) == ties


def test_noisy_bayes_and_uninformative_probe():
    b = branches(Case(p=.3, accuracy=.8))
    assert b[0] == pytest.approx((.38, .24 / .38))
    assert b[1] == pytest.approx((.62, .06 / .62))
    ref = exact(Case(accuracy=.5))
    assert ref["values"]["PROBE"] == pytest.approx(3.5)
    assert ref["policy"]["initial_action"] == "ASK"


def test_frozen_grid_contains_unique_72_cases():
    rows = live_cases()
    assert len(rows) == 72
    assert len({json.dumps(r["case"], sort_keys=True) for r in rows}) == 72


@pytest.mark.parametrize("replacement", [True, float("nan"), -1, 1.1, "0.3"])
def test_invalid_probabilities_rejected(replacement):
    p = exact(Case())["policy"]
    p["prior_feasible"] = replacement
    with pytest.raises(ValueError, match="invalid_probability"):
        parse_policy(json.dumps(p))


def test_provider_failure_retains_unknown_and_all_assignments(tmp_path):
    out = tmp_path / "run"
    prepare(out, ROOT / "experiments/decision-story-e1-v1.json")
    def fail(*args):
        raise ProviderError("openai: HTTP 429")
    report = run(out, transport=fail)
    assert report["status"] == "provider_stopped"
    assert report["groups"]["all"]["unknown"] == 72
    assert report["budget"]["unknown_usage_requests"] == 1
    assert len(list((out / "responses").glob("*.json"))) == 1
    with pytest.raises(FileExistsError):
        run(out, transport=fail)


def test_scripted_exact_policies_score_zero_without_network(tmp_path):
    out = tmp_path / "run"
    prepare(out, ROOT / "experiments/decision-story-e1-v1.json")
    def scripted(provider, path, payload):
        assert "theta" not in json.loads(payload["input"])
        policy = exact(Case(**json.loads(payload["input"])))["policy"]
        return {"status": "completed", "usage": {"input_tokens": 100, "output_tokens": 80},
                "output": [{"type": "message", "content": [
                    {"type": "output_text", "text": json.dumps(policy)}]}]}
    report = run(out, transport=scripted)
    assert report["groups"]["all"]["valid"] == 72
    assert report["groups"]["all"]["mean_policy_regret"] == pytest.approx(0)
    assert report["budget"]["unknown_usage_requests"] == 0
