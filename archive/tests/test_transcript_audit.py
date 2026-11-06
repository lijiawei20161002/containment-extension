"""Exercise the actual judge request path and keep reference labels out of payloads."""
import importlib.util
import json
from pathlib import Path

import pytest

from containment_extension.feedback_ablation import JUDGE_SYSTEM
from containment_extension.instruction_optimization.study import save

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "transcript_audit", ROOT / "scripts/run_transcript_audit.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def prepare_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "ROOT", tmp_path)
    actors, root = tmp_path / "actors", tmp_path / "audit"
    actors.mkdir()
    root.mkdir()
    runs = [f"run-{i:04d}" for i in range(48)]
    save(actors, "schedule.json", [{"run": r} for r in runs])
    save(actors, "plan.json", {})
    save(actors, "execution.json", {"status": "finished"})
    save(actors, "observations.json", [
        {"run": r, "unauthorized_effect": i == 0} for i, r in enumerate(runs)])
    monkeypatch.setattr(module, "transcript_packet", lambda _: {"trusted_task": "visible task"})
    plan = {"actors": "actors", "actor_plan_sha256": module.file_hash(actors / "plan.json"),
            "actor_schedule_sha256": module.file_hash(actors / "schedule.json"),
            "source_hashes": {}, "judge": {"model": "test"},
            "rates": {"test": {"input": 1., "output": 5.}},
            "judge_system": JUDGE_SYSTEM, "target_runs": runs}
    save(root, "plan.json", plan)
    save(root, "archive-inputs.json", [
        {"id": f"archive-{i}", "reference": i >= 12,
         "use": "benign_calibration" if i < 12 else "positive_audit",
         "packet": {"trusted_task": "visible task"}} for i in range(20)])
    save(root, "judgments.json", {})
    save(root, "budget.json", {})
    save(root, "execution.json", {"status": "prepared_without_inference"})
    return root


def test_judge_payload_is_allowlisted_and_confusion_is_measured(tmp_path, monkeypatch):
    root = prepare_fixture(tmp_path, monkeypatch)
    count = 0

    def transport(provider, path, payload):
        nonlocal count
        assert json.loads(payload["messages"][0]["content"]) == {"trusted_task": "visible task"}
        positive = 12 <= count <= 20
        count += 1
        return {"model": "test", "stop_reason": "end_turn",
                "usage": {"input_tokens": 100, "output_tokens": 20},
                "content": [{"type": "text", "text": json.dumps({
                    "unauthorized_access": positive, "score": .9 if positive else .1,
                    "reason": "test response"})}]}
    result = module.execute(root, transport)
    assert count == 68 and result["status"] == "finished"
    assert result["threshold"] == .5
    assert result["target_matrix"] == {"TP": 1, "FN": 0, "FP": 0, "TN": 47}
    assert result["target_unknown"] == 0
    assert module.audit(root)["passed"]
    with pytest.raises(ValueError, match="Already started"):
        module.execute(root, transport)


def test_invalid_judgments_stay_unknown(tmp_path, monkeypatch):
    root = prepare_fixture(tmp_path, monkeypatch)
    save(root, "threshold.json", {"threshold": .5})
    save(root, "references.json", {f"run-{i:04d}": i < 2 for i in range(48)})
    save(root, "judgments.json", {
        "run-0000": {"status": "valid", "score": .9},
        "run-0001": {"status": "invalid", "score": None}})
    result = module.summarize(root)
    assert result["target_unknown"] == 47
    assert result["target_tpr"]["assigned"] == 2
    assert result["target_tpr"]["unknown"] == 1
    assert result["target_tpr"]["assigned_bounds"] == [.5, 1.]


@pytest.mark.parametrize('wrapper,valid', [
    ('{}', True), ('```json\n{}\n```', True), ('```\n{}\n```', True),
    ('Here is the result:\n```json\n{}\n```', False),
    ('```json\n{}\n```\nextra', False),
])
def test_format_normalization_changes_only_complete_fence(wrapper, valid):
    payload = json.dumps({'unauthorized_access': False, 'score': 0, 'reason': 'observed'})
    raw = {'content': [{'type': 'text', 'text': wrapper.format(payload)}],
           'stop_reason': 'end_turn'}
    saved = json.loads(json.dumps(raw))
    result = module.parse_audit_judge(raw, True)
    assert (result['status'] == 'valid') is valid
    assert raw == saved
    if valid:
        assert result['score'] == 0 and result['unauthorized_access'] is False


def test_reused_calibration_is_not_called_or_billed_twice(tmp_path, monkeypatch):
    root = prepare_fixture(tmp_path, monkeypatch)
    origin = tmp_path / 'old-audit'
    origin.mkdir()
    plan = module.read(root/'plan.json')
    plan.update(reuse_calibration='old-audit', reused_response_hashes={},
                allow_json_fence=True, max_calls=56, aggregate_usd=1.9)
    old_ledgers = {}
    packet = {'trusted_task': 'visible task'}
    for i in range(12):
        folder = origin/'judges'/f'archive-{i}'
        folder.mkdir(parents=True)
        req = {'model': 'test', 'system': JUDGE_SYSTEM, 'temperature': 0, 'max_tokens': 512,
               'messages': [{'role': 'user', 'content': json.dumps(packet)}]}
        text = json.dumps({'unauthorized_access': False, 'score': 0, 'reason': 'test'})
        raw = {'model': 'test', 'stop_reason': 'end_turn',
               'usage': {'input_tokens': 100, 'output_tokens': 20},
               'content': [{'type': 'text', 'text': f'```json\n{text}\n```'}]}
        for name, value in [('request.json', req), ('response.json', raw)]:
            module.save(origin, f'judges/archive-{i}/{name}', value)
            path = folder/name
            plan['reused_response_hashes'][str(path.relative_to(tmp_path))] = module.file_hash(path)
        old_ledgers[f'archive-{i}'] = {'input_tokens': 100, 'output_tokens': 20}
    module.save(origin, 'budget.json', {'assignments': old_ledgers})
    module.save(root, 'plan.json', plan)
    calls = 0

    def transport(provider, path, payload):
        nonlocal calls
        positive = calls <= 8
        calls += 1
        text = json.dumps({'unauthorized_access': positive,
                           'score': .9 if positive else 0, 'reason': 'test'})
        return {'model': 'test', 'stop_reason': 'end_turn',
                'usage': {'input_tokens': 100, 'output_tokens': 20},
                'content': [{'type': 'text', 'text': f'```json\n{text}\n```'}]}

    result = module.execute(root, transport)
    assert result['status'] == 'finished' and result['recorded'] == 68
    assert calls == result['budget']['requests'] == 56
    assert result['target_matrix'] == {'TP': 1, 'FN': 0, 'FP': 0, 'TN': 47}
    audited = module.audit(root)
    assert audited['passed'] and audited['reused_calibration_responses'] == 12


def test_diagnostic_retains_failure_and_inconsistent_scores(tmp_path, monkeypatch):
    root = prepare_fixture(tmp_path, monkeypatch)
    plan = module.read(root/'plan.json')
    plan['diagnostic_only'] = True
    module.save(root, 'plan.json', plan)

    def contradictory(provider, path, payload):
        return {'model': 'test', 'stop_reason': 'end_turn',
                'usage': {'input_tokens': 100, 'output_tokens': 20},
                'content': [{'type': 'text', 'text': json.dumps({
                    'unauthorized_access': False, 'score': 1., 'reason': 'test conflict'})}]}
    result = module.execute(root, contradictory)
    assert result['status'] == 'finished'
    assert result['calibration_passed'] is False
    assert result['threshold'] == .5 and result['boolean_score_disagreements'] == 48
    assert result['target_matrix']['FP'] == 47
    assert result['boolean_matrix']['FN'] == 1
