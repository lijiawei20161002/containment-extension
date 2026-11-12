"""Audit the paired raw/compiled-contract diagnostic without new inference."""
import argparse,csv,hashlib,json,sqlite3,sys
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('study',type=Path); p.add_argument('--output',type=Path,required=True)
a=p.parse_args(); study=a.study.resolve(); sys.path.insert(0,str(study/'source'))
from containment_extension.sabench_study import verify,report,tasks,partial_calls,score,runtime,digest
from containment_extension.verified_planner import compile_office_contract
plan=verify(study); summary=report(study)
assert summary['execution']['status']=='finished'
bank={t.task_id:t for t in tasks()}; rows=[]; hashes={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for r in summary['records']:
    folder=study/'episodes'/r['run']; task=bank[r['task_id']]
    calls=partial_calls(folder)
    audited=score(task,calls,r['final_response'],r['stop'])
    for k,v in audited.items(): assert r[k]==v,(r['run'],k)
    state=task.s0
    events=[json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines()] if (folder/'events.jsonl').exists() else []
    for event in events:
        call=event['call']
        actual,response,state=runtime.execute_tool_call(call['tool']+'_'+call['action'],call['args'],state,call['step'])
        assert response==event['response'] and digest(state)==event['state_sha256']
    if r['scope_compiler']:
        raw=json.loads((study/'contracts'/r['task_id']/'result.json').read_text())['contract']
        assert json.loads((folder/'scope-compiler.json').read_text())==compile_office_contract(raw,task.s0)
    messages=[json.loads(x) for x in (folder/'transcript.jsonl').read_text().splitlines()]
    for m in messages:
        payload=m.get('provider_request',m.get('provider_response'))
        if payload: assert payload['model']=='gpt-6-astra'
    budget=json.loads((folder/'budget.json').read_text())
    rows.append({**{k:r[k] for k in ['run','task_id','template_id','model_key','condition','stop','incident','authorized_completion','calls']},
                 'estimated_usd':budget['estimated_usd']+budget['reserved_usd'],'requests':budget['requests']})
    for path in folder.iterdir():
        if path.is_file(): hashes[str(path.relative_to(study))]=sha(path)
groups=[]
for condition in ['raw','compiled']:
    selected=[r for r in rows if r['condition']==condition]
    groups.append({'condition':condition,'assigned':len(selected),'incidents':sum(r['incident'] is True for r in selected),
                   'authorized_completion':sum(r['authorized_completion'] is True for r in selected),
                   'unknown_incident_outcomes':sum(r['incident'] is None for r in selected),
                   'safe_unfinished':sum(r['incident'] is False and r['authorized_completion'] is False for r in selected)})
a.output.mkdir(parents=True,exist_ok=True)
with (a.output/'episodes.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
    writer.writerows({k:'' if v is None else str(v).lower() if type(v) is bool else v for k,v in r.items()} for r in rows)
result={'groups':groups,'estimated_usd':summary['actor_estimated_usd'],'requests':summary['requests'],
        'limitations':plan['limitations'],'interpretation':'Retrospective implementation diagnostic; does not establish representative incident reduction or superiority over permissions-only guidance.'}
(a.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
(a.output/'provenance.json').write_text(json.dumps({'plan_sha256':sha(study/'plan.json'),
    'source_hashes':plan['frozen_hashes'],'episodes_sha256':sha(a.output/'episodes.csv'),'evidence_hashes':hashes,
    'analysis_sha256':sha(Path(__file__)),'original_contract_hashes':plan['original_contract_hashes']},indent=2)+'\n')
(a.output/'REPORT.md').write_text('# Calendar compiler diagnostic\n\n'+result['interpretation']+'\n\n'+
    '| Condition | Incidents | Authorized completion | Safe but unfinished | Unknown incident outcomes |\n| --- | ---: | ---: | ---: | ---: |\n'+
    '\n'.join(f"| {g['condition']} | {g['incidents']}/{g['assigned']} | {g['authorized_completion']}/{g['assigned']} | {g['safe_unfinished']} | {g['unknown_incident_outcomes']} |" for g in groups)+
    '\n\nAll four contracts whose structural operation changes under compilation are included. They were already inspected. The raw and compiled conditions use the same Astra actor and planner. The remaining compiled non-completion asks for year and time-zone clarification; it makes no write.\n')
print(json.dumps(result,indent=2))
