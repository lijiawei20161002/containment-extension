"""Export audited argument failures and new interface-regression outcomes."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from containment_extension.sabench_study import atomic, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--paper-dir', type=Path, required=True)
    paper = p.parse_args().paper_dir
    data = paper / 'data'
    mappings = {
        'office_interface_episodes.csv': 'office-interface-regression-v1/episodes.csv',
        'office_interface_summary.json': 'office-interface-regression-v1/summary.json',
        'office_argument_episodes.json': 'office-argument-audit/episodes.json',
        'office_argument_summary.json': 'office-argument-audit/summary.json',
    }
    for target, source in mappings.items():
        (data / target).write_bytes((ROOT / 'results' / source).read_bytes())
    reports = {}
    for name in ['office-interface-regression-v1', 'office-argument-audit']:
        reports[name] = json.loads((ROOT / 'results' / name / 'provenance.json').read_text())
        reports[name].pop('execution', None)
    quota = ROOT / 'runs/fable-interface-check-20261111-network.json'
    atomic(data / 'office_interface_provenance.json', {
        'date': '2026-11-11', 'assigned': 78, 'reports': reports,
        'data_sha256': {name: sha(data / name) for name in mappings},
        'analysis_sha256': sha(paper / 'analysis/office_interface_summary.py'),
        'quota_diagnostic': {'sha256': sha(quota), **json.loads(quota.read_text())},
        'notes': ['An additional 78 Astra records; historical audit rows repeat earlier records and add no actor episodes.',
                  'All 26 cached calendar-create/email-send tasks are included in three conditions.',
                  'Shared syntax validation is an environment amendment, not planner-specific safety improvement.',
                  'No Fable behavioral requests were launched after the benign check confirmed an exhausted workspace quota.']})
    print(json.dumps({'new_actor_records': 78, 'historical_audited_records': 1320}))


if __name__ == '__main__':
    main()
