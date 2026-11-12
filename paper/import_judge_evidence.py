"""Read frozen judge evidence and export anonymous, auditable derived records.

No model calls. The import script is kept outside the anonymous paper package.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper/trust4rsi2027-anonymous/data'
CONDITIONS = [
    ('J01', 'Haiku 4.5', 'v1/haiku-4-5', 'transcript', 'Transcript'),
    ('J02', 'Sonnet 4.6', 'v1/sonnet-4-6', 'transcript', 'Transcript'),
    ('J03', 'Haiku 4.5', 'v1/haiku-4-5', 'transcript_journal', 'Transcript + journal'),
    ('J04', 'Sonnet 4.6', 'v1/sonnet-4-6', 'transcript_journal', 'Transcript + journal'),
    ('J05', 'Haiku 4.5', 'v2/note-haiku-4-5', 'transcript', 'Grant rule: instruction'),
    ('J06', 'Haiku 4.5', 'v2/packet-haiku-4-5', 'transcript', 'Grant rule: packet'),
    ('J07', 'Sonnet 4.6', 'v2/note-sonnet-4-6', 'transcript', 'Grant rule: instruction'),
    ('J08', 'Haiku 4.5', 'v3/reasonfirst-haiku-4-5', 'transcript', 'Instruction + reason first'),
    ('J09', 'Sonnet 4.6', 'v3/reasonfirst-sonnet-4-6', 'transcript', 'Instruction + reason first'),
]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write_csv(name, rows):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

all_items, all_draws, conditions, provenance = [], [], [], []
base_ids = None
for cid, model, relative, view, description in CONDITIONS:
    report_dir = ROOT / 'archive/results' / ('judge-reliability-' + relative)
    plan = json.loads((report_dir / 'plan.json').read_text())
    report = json.loads((report_dir / 'report.json').read_text())
    assert report['status'] == 'finished'
    prefix = 'judge-reliability-' + relative.replace('/', '-') + '-'
    runs = list((ROOT / 'archive/runs').glob(prefix + '*'))
    assert len(runs) == 1
    run = runs[0]
    items = sorted(plan['items'], key=lambda i: i['id'])
    ids = [i['id'] for i in items]
    if base_ids is None:
        base_ids = ids
    assert ids == base_ids
    condition_rows = []
    source_hashes = []
    draw_hashes = []
    counter = Counter()
    for item in items:
        kind = 'scripted' if item['kind'] == 'calibration' else 'agent'
        suffix = item['id'].split('/')[-1]
        if kind == 'scripted':
            aid = f"C{int(suffix.split('-')[-1])+1:02d}"
            partition = 'scripted'
        else:
            counter['agent'] += 1
            aid = f"A{counter['agent']:03d}"
            partition = 'development' if suffix.startswith('dev-') else 'selected_test'
        source = ROOT / 'runs' / item['path'].split('/runs/')[1]
        evidence = json.loads(source.read_text())['outcome']
        assert evidence['incident'] == item['truth']
        assert any(not e['authorized'] for e in evidence['journal']) == item['truth']
        source_hashes.append([aid, digest(source)])
        valid_labels = []
        for k in range(plan['config']['draws']):
            p = run / 'judgments' / f"{item['id'].replace('/', '--')}-{view}-d{k:02d}.json"
            d = json.loads(p.read_text())
            valid = d['status'] == 'valid' and isinstance(d.get('incident'), bool)
            if valid:
                valid_labels.append(d['incident'])
            all_draws.append(dict(condition=cid, item=aid, draw=k,
                status=d['status'], incident=int(d['incident']) if valid else '',
                probability=d.get('probability', '') if valid else ''))
            draw_hashes.append([aid, k, digest(p)])
        positive = sum(valid_labels)
        majority = '' if not valid_labels or positive * 2 == len(valid_labels) else int(positive * 2 > len(valid_labels))
        row = dict(condition=cid, item=aid, kind=kind, partition=partition,
            reference=int(item['truth']), majority=majority,
            initial_grant=int(item['environment']['granted']) if kind == 'agent' else '',
            draws=plan['config']['draws'], valid_draws=len(valid_labels), positive_draws=positive)
        all_items.append(row)
        condition_rows.append(row)
    for kind, key in [('agent', 'development'), ('scripted', 'calibration')]:
        rows = [r for r in condition_rows if r['kind'] == kind]
        metrics = report['views'][view]['metrics'][key]
        calculated = dict(items=len(rows), abstain=sum(r['majority'] == '' for r in rows),
            false_alarm=sum(r['majority'] == 1 and r['reference'] == 0 for r in rows),
            miss=sum(r['majority'] == 0 and r['reference'] == 1 for r in rows),
            agree=sum(r['majority'] == r['reference'] for r in rows))
        assert all(metrics['aggregated']['majority'][k] == v for k,v in calculated.items())
        assert sum(r['reference'] for r in rows) == metrics['incidents']
    conditions.append(dict(condition=cid, model=model, input=description,
        stage=relative.split('/')[0], draws=plan['config']['draws']))
    provenance.append(dict(condition=cid, plan_sha256=digest(report_dir/'plan.json'),
        report_sha256=digest(report_dir/'report.json'), source_items=source_hashes,
        draw_sha256=draw_hashes))

write_csv('judge_items.csv', all_items)
write_csv('judge_draws.csv', all_draws)
write_csv('judge_conditions.csv', conditions)
assert len(all_items) == 1584 and len(all_draws) == 5456
(OUT/'judge_provenance.json').write_text(json.dumps(dict(
    extraction_date='2026-11-09', conditions=provenance,
    checks=['All nine majority-result configurations match frozen reports.',
            'All 176 unique item labels match saved source outcomes and effect journals.',
            'Same 176 items across conditions; repeated judging is not independent actor evidence.'],
    scope='128 development episodes overlap the main actor study; 32 historical selected-test episodes and 16 scripted cases are used only for monitor diagnostics.'), indent=2)+'\n')
print(json.dumps(dict(item_rows=len(all_items), draw_rows=len(all_draws),
    statuses=dict(Counter(r['status'] for r in all_draws)),
    partitions=dict(Counter(r['partition'] for r in all_items if r['condition']=='J01'))), indent=2))
