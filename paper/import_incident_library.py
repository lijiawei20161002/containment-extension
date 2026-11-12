"""Export the frozen incident library as anonymous derived records for the paper.

Reads incidents/records/*.json and two figure specs; writes
data/incident_library.csv and data/incident_specs/*.json inside the anonymous
package. No model calls; repository paths and figure links are not exported.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / 'paper/trust4rsi2027-anonymous'
OUT = PKG / 'data'
EXAMPLES = [
    'figures/incidents/artifactory-unauthorized-communication/incident-14-artifactory-unauthorized-communication.spec.json',
    'figures/incidents/public-hosting-local-workbook/incident-15-public-hosting-local-workbook.spec.json',
]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def status(v):
    return v['status'] if isinstance(v, dict) else v


def first_source(ev):
    s = ev['sources'][0]
    date = s.get('date') or ''
    return s['publisher'], date


rows = []
for path in sorted((ROOT / 'incidents/records').glob('*.json')):
    r = json.loads(path.read_text())
    ev, d = r['evidence'], r['dates']
    publisher, date = first_source(ev)
    rows.append({
        'entry': r['entry_number'],
        'id': r['id'],
        'short_title': r['short_title'],
        'title': r['title'],
        'actor': r['actor'],
        'models': '; '.join(r['models']),
        'category': r['category'],
        'pathway': r['pathway'],
        'occurred_start': d.get('occurred_start') or '',
        'occurred_end': d.get('occurred_end') or '',
        'detected': d.get('detected') or '',
        'disclosed': d.get('disclosed') or '',
        'detail_report': d.get('detail_report') or '',
        'evidence_level': ev['level'],
        'disputed': str(bool(ev.get('disputed'))).lower(),
        'counting_unit': ev['counting_unit'],
        'primary_source_publisher': publisher,
        'primary_source_date': date,
        'confirmed_by': '; '.join(ev.get('confirmed_by', [])),
        'stop_behavior': r['stop_behavior'],
        'lineage_group': r['lineage']['group'],
        **{f'ind_{k}': status(r['indicators'][k]) for k in 'fpxcvo'},
        **{f'mech_{k}': status(r['mechanisms'][k]) for k in ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']},
        'bas_layers': ' '.join(r['controls']['bas_layers_implicated']),
        'review_status': r['provenance']['review_status'],
        'compiled_from': r['provenance']['compiled_from'],
    })
assert len(rows) == 26 and [x['entry'] for x in rows] == list(range(1, 27))
with (OUT / 'incident_library.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

spec_dir = OUT / 'incident_specs'
spec_dir.mkdir(exist_ok=True)
prov = json.loads((OUT / 'figure_provenance.json').read_text())
known = {s['asset'] for s in prov['sources']}
for rel in EXAMPLES:
    src = ROOT / rel
    spec = json.loads(src.read_text())
    (spec_dir / f"incident-{spec['n']:02d}.spec.json").write_text(json.dumps(spec, indent=1) + '\n')
    if rel not in known:
        prov['sources'].append({'asset': rel, 'sha256': digest(src)})
prov['incident_examples'] = ('Entries 14 and 15 redrawn as vector diagrams from the library figure specs; '
                             'text content unchanged except wrapping. Icons omitted.')
prov['incident_library'] = {
    'records': 26,
    'sha256': digest(OUT / 'incident_library.csv'),
    'note': 'Derived from the 27 September 2026 public-source briefing records; codings are analyst drafts.',
}
(OUT / 'figure_provenance.json').write_text(json.dumps(prov, indent=1) + '\n')
print('wrote', len(rows), 'records and', len(EXAMPLES), 'specs')
