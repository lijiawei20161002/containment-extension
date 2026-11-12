"""Freeze all cached calendar-create/email-send tasks for the common interface fix."""
import argparse
import json
from pathlib import Path
import random
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from containment_extension.sabench_study import atomic, now, sha, digest, MODELS, RATES, tasks, verify
from containment_extension.verified_planner import compile_office_contract


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--models', nargs='+', choices=list(MODELS), default=['astra'])
    a = p.parse_args()
    original_plan = verify(a.source)
    bank = {t.task_id: t for t in tasks()}
    selected = []
    for task_id in original_plan['task_ids']:
        path = a.source / 'contracts' / task_id / 'result.json'
        record = json.loads(path.read_text())
        contract = record.get('contract')
        if contract and any(w['tool_name'] in {'calendar_create','email_send'} for w in contract['writes']):
            selected.append((bank[task_id], path, contract))
    assert len(selected) == 26, 'Inspect changed allocation before inference'
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    schedule, lineage = [], {}
    arms = ['plain', 'grant_only', 'planner']
    for task, path, raw in sorted(selected, key=lambda item: item[0].task_id):
        validation = compile_office_contract(raw, task.s0)
        assert validation['valid'], (task.task_id, validation['errors'])
        lineage[task.task_id] = sha(path)
        atomic(out / 'contracts' / task.task_id / 'result.json', {
            'task_id': task.task_id, 'status': 'complete', 'contract': validation['contract'],
            'uncompiled_contract': raw, 'validation': validation,
            'source': 'Original visible-input estimate compiled without scoring labels; no new inference',
            'original_result_sha256': sha(path)})
        for model in a.models:
            for arm in arms:
                schedule.append({'task_id': task.task_id, 'template_id': task.template_id,
                    'state_type': task.state_type, 'trap_type': task.trap_type, 'ambiguous': task.is_ambiguous,
                    'model_key': model, 'arm': arm})
    random.Random(20261115).shuffle(schedule)
    for i, spec in enumerate(schedule):
        spec['run'] = f'run-{i+1:05d}'
    shutil.copytree(ROOT / 'src/containment_extension', out / 'source/containment_extension',
                    ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(ROOT / 'third_party/sabench', out / 'third_party/sabench',
                    ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copy2(ROOT / 'docs/office-interface-regression-protocol.md', out / 'protocol.md')
    frozen = {str(path.relative_to(out)): sha(path)
              for folder in [out / 'source', out / 'third_party', out / 'contracts']
              for path in folder.rglob('*') if path.is_file()}
    frozen['protocol.md'] = sha(out / 'protocol.md')
    plan = {'version': 'office-interface-regression-v1', 'created_at': now(), 'split': 'interface_regression',
        'config': {'max_steps': 16, 'max_output_tokens': 16384, 'workers': 6, 'max_estimated_usd': None,
                   'arms': arms, 'models': {m: MODELS[m] for m in a.models}, 'rates': RATES,
                   'validate_scope': True, 'validate_arguments': True},
        'schedule': schedule, 'task_ids': sorted(lineage), 'frozen_hashes': frozen,
        'request_ceiling': 16 * len(schedule), 'original_contract_hashes': lineage,
        'source_plan_sha256': sha(a.source / 'plan.json'),
        'primary': 'None: retrospective interface regression on all contracts using the affected APIs.',
        'limitations': ['Known public tasks, selected by proposed API rather than actor success.',
            'Common syntax validation changes the environment for every arm; not planner safety improvement.',
            'All original outcomes remain unchanged; no new scope inference or model fallback.',
            'Fable corrected behavior remains pending while its workspace quota is exhausted.']}
    atomic(out / 'plan.json', plan)
    atomic(out / 'plan.sha256.json', {'sha256': digest(plan)})
    atomic(out / 'execution.json', {'status': 'prepared_without_inference'})
    print(json.dumps({'tasks': len(selected), 'models': a.models, 'episodes': len(schedule)}))


if __name__ == '__main__':
    main()
