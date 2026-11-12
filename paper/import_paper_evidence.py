"""Read frozen evidence and export anonymous, minimal paper data. No model calls."""
import csv
import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).parent / 'trust4rsi2027-anonymous'

def read(p):
    return json.loads(p.read_text())

def write_csv(name, rows):
    with (OUT / 'data' / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v) if isinstance(v, bool) else v for k,v in row.items()})

data = read(ROOT / 'dashboard/data.json')
rows, cohorts, transitions, traces = [], [], [], []
audited = 0
for index,c in enumerate(data['cohorts'],1):
    cid = f'C{index:02d}'
    d = ROOT / 'runs' / c['name']
    plan = read(d / 'plan.json')
    native = c['study']=='native-algorithms'
    cohorts.append(dict(cohort=cid,study=c['study'],model=c['model'],
        status=c['worker']['status'],assigned=c['development_assigned'],
        recorded=sum(e['phase']=='dev' for e in c['episodes']),
        historical_test=sum(e['phase']=='test' for e in c['episodes']),
        plan_sha256=hashlib.sha256((d/'plan.json').read_bytes()).hexdigest()))
    if native:
        native_rows = {x['run']:x for x in read(d/'summary.json')['records']}
    for e in c['episodes']:
        if e['phase']!='dev':
            continue
        steps=[]
        if native:
            r=native_rows[e['run']]
            assert e['incident']==r['unauthorized_effect']
            assert e['authorized_completion']==r['authorized_completion']
            result=read(d/e['run']/'result.json')
            expected=True if result['unauthorized_effect'] else False if result['stop_reason'] in ('scorer_success','model_finished') and not result['error'] else None
            assert expected==e['incident']
            prefix=read(d/e['run']/'manifest.json')['checkpoint']['prefix_actions']
            attempts=[a for a in read(d/e['run']/'attempts.json') if a['seq']>prefix]
            for a in attempts:
                steps.append(dict(step=a['seq']-prefix,operation=a['action'].get('method','?')+' '+a['action'].get('url','?'),scope=a['scope_label']))
            complete_unknown = e['authorized_completion'] is None
        else:
            ep=d/'episodes'/e['id']
            result=read(ep/'result.json')
            o=result['outcome']
            assert e['incident']==o['incident'] and e['authorized_completion']==o['authorized_completion']
            with sqlite3.connect(f'file:{ep / "effects.sqlite3"}?mode=ro',uri=True) as con:
                effects=con.execute('SELECT seq, authorized FROM effects ORDER BY seq').fetchall()
            inc=sum(not x[1] for x in effects)
            assert inc==e['incident_count']
            assert e['repeat_incidents']==max(0,inc-1)
            assert e['incident']==(True if inc else False if o['terminated_normally'] else None)
            transcript=read(ep/'transcript.json') if (ep/'transcript.json').exists() else []
            acts=[x for x in transcript if 'operation' in x]
            for a,b in zip(acts,acts[1:]):
                advice=a['tool_result'].get('planning_advice')
                if advice:
                    transitions.append(dict(cohort=cid,episode=e['id'],model=c['model'],study=c['study'],candidate=e['candidate'],
                        recommendation=advice['recommended_action'],next_operation=b['operation'],agrees=advice['recommended_action']==b['operation']))
            for i,a in enumerate(acts,1):
                j=a['tool_result'].get('verified_effect_journal')
                steps.append(dict(step=i,operation=a['operation'],response=a['tool_result'].get('status'),
                    advice=(a['tool_result'].get('planning_advice') or {}).get('recommended_action'),
                    journal_incidents=None if j is None else sum(not x['authorized'] for x in j)))
            complete_unknown=not o['terminated_normally'] and not o['authorized_completion'] and not inc
        rows.append(dict(cohort=cid,study=c['study'],model=c['model'],cohort_status=c['worker']['status'],
            episode=e['id'],family=e['family'],seed=e['seed'],candidate=e['candidate'],arm=e['arm'],
            stop_reward=e['stop_reward'],alternate_cost='' if native else e['alternate_cost'],
            available=e['available'],initial_grant=e['granted'],grant_reply=e['grant_reply'],
            incident=e['incident'],repeat_effects=e['repeat_incidents'],authorized_completion=e['authorized_completion'],
            completion_unknown=complete_unknown,attempted_outside=e.get('attempted_outside'),
            status=e['status'],steps=e['steps']))
        traces.append(dict(cohort=cid,episode=e['id'],steps=steps))
        audited+=1
write_csv('episodes.csv',rows)
write_csv('cohorts.csv',cohorts)
write_csv('advice_transitions.csv',transitions)
(OUT/'data/action_traces.json').write_text(json.dumps(traces,indent=2)+'\n')
z=zipfile.ZipFile('/private/tmp/AuthorKit27.zip')
for filename in ['aaai2027.sty','aaai2027.bst']:
    (OUT/filename).write_bytes(z.read('AuthorKit27/'+filename))
(OUT/'data/provenance.json').write_text(json.dumps(dict(
    description='Anonymous derived records. Raw evidence was read without modification; no inference was run.',
    extraction_date='2026-11-09',audited_episodes=audited,
    dashboard_sha256=hashlib.sha256((ROOT/'dashboard/data.json').read_bytes()).hexdigest(),
    author_kit_url='https://aaai.org/wp-content/uploads/2026/05/AuthorKit27.zip',
    author_kit_sha256=hashlib.sha256(Path('/private/tmp/AuthorKit27.zip').read_bytes()).hexdigest(),
    checks=['Native labels cross-checked against final summary and per-run result.',
        'Workflow labels and repeat-effect counts cross-checked against per-episode result and read-only SQLite effects.',
        'Advice agreement uses only a recorded recommendation followed by a recorded tool operation; initial advice and text-only exits excluded.'],
    excluded='Historical selectively assigned test episodes are inventoried but not pooled with the balanced development comparisons.'
),indent=2)+'\n')
print(json.dumps(dict(audited=audited,cohorts=len(cohorts),advice_transitions=len(transitions))))
