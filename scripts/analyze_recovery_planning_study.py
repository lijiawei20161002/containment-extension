"""Offline audit and fixed analysis of prospective recovery-planning episodes."""
from collections import Counter, defaultdict
import argparse
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

from analyze_sabench_study import binary, paired, holm


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); study=args.study.resolve()
    sys.path.insert(0,str(study/'source'))
    from containment_extension.recovery_planning_study import verify,report,Service,public_task,prompt,ARMS,MODELS
    from containment_extension.verified_planner import guidance
    plan=verify(study); base=report(study)
    arms=plan['config']['arms']
    exploratory=plan.get('mode')=='allocation'
    assert base['execution']['status']=='finished','Analyze the complete fixed allocation only'
    tasks={t['task_id']:t for t in json.loads((study/'tasks.json').read_text())}
    rows=[]; evidence={}; requests=Counter(); adherence=defaultdict(Counter)
    for record in base['records']:
        directory=study/'episodes'/record['run']; task=tasks[record['task_id']]
        service=Service(task)
        events=json.loads('[]')
        if (directory/'events.jsonl').exists():
            events=[json.loads(x) for x in (directory/'events.jsonl').read_text().splitlines()]
        logged=[]
        for event in events:
            batch=event.get('batch',[event['response']])
            logged.extend((response,event['guidance'] if j==len(batch)-1 else None)
                          for j,response in enumerate(batch))
        delivered=guidance(service.actions,service.facts,service.budget,frozenset(task['goals']),task['horizon'],record['arm'])
        assert delivered==json.loads((directory/'initial_advice.json').read_text())
        with sqlite3.connect(f"file:{directory/'effects.sqlite3'}?mode=ro",uri=True) as con:
            saved=con.execute('SELECT seq,operation,response,guidance FROM events ORDER BY seq').fetchall()
        for i,(seq,operation,response,feedback) in enumerate(saved):
            recommendation=delivered.get('recommendation',delivered.get('myopic_recommendation')) if delivered else None
            if recommendation:
                adherence[record['model_key'],record['arm']]['eligible']+=1
                adherence[record['model_key'],record['arm']]['followed']+=int(operation==recommendation)
            replayed=service.execute(operation)
            assert seq==service.steps and replayed==json.loads(response)
            delivered=(guidance(service.actions,service.facts,service.budget,frozenset(task['goals']),
                                task['horizon']-service.steps,record['arm']) if feedback is not None else None)
            if feedback is not None: assert delivered==json.loads(feedback)
            if i<len(logged): assert logged[i]==(replayed,delivered)
        normal=record['stop'] in {'model_finished','explicit_stop','action_limit'}
        rescored=service.result(normal)
        for key,value in rescored.items(): assert record[key]==value,(record['run'],key)
        messages=[json.loads(x) for x in (directory/'transcript.jsonl').read_text().splitlines()]
        budget=json.loads((directory/'budget.json').read_text())
        reqs=[x['provider_request'] for x in messages if 'provider_request' in x]
        responses=[x['provider_response'] for x in messages if 'provider_response' in x]
        assert len(reqs)==budget['requests']
        assert all(x['model']==MODELS[record['model_key']]['model'] for x in reqs+responses)
        # Reference and failure target are never in the common task serialization.
        visible=public_task(task)
        assert 'reference' not in visible and 'fault_action' not in visible
        requests[record['model_key']]+=len(reqs)
        elapsed=[]; last_request=None
        for message in messages:
            if 'provider_request' in message:
                last_request=datetime.fromisoformat(message['at'])
            elif 'provider_response' in message and last_request is not None:
                elapsed.append((datetime.fromisoformat(message['at'])-last_request).total_seconds())
                last_request=None
        row={k:record[k] for k in ['run','task_id','template_id','model_key','arm','feasible',
             'stop','incident','authorized_completion','task_completion','incident_count',
             'goals_satisfied','goals_total','steps','resources_used','fault_observed','advice_cpu_seconds']}
        row['ambiguous']=not row['feasible'] # Only for reuse of feasible-endpoint analysis.
        row['reference_cost']=task['reference']['cost']
        row['reference_steps']=len(task['reference']['plan'])
        row['excess_resource_cost']=(row['resources_used']-row['reference_cost']
            if row['authorized_completion'] is True and row['feasible'] else None)
        row['estimated_usd']=budget['estimated_usd']+budget['reserved_usd']
        row['requests']=budget['requests']
        row['input_tokens']=budget['input_tokens']
        row['output_tokens']=budget['output_tokens']
        row['observed_api_seconds']=sum(elapsed)
        # The frozen runner's field name says CPU, but perf_counter measures
        # elapsed wall time. Preserve its source value and label exports correctly.
        row['advice_elapsed_seconds']=row.pop('advice_cpu_seconds')
        rows.append(row)
        for path in directory.iterdir():
            if path.is_file(): evidence[str(path.relative_to(study))]=sha(path)
    contrasts=[paired(rows,m,a,endpoint,left='permissions') for m in MODELS for a in arms if a!='permissions'
               for endpoint in ['incident','authorized_completion']]
    if 'greedy' in arms:
        contrasts += [paired(rows,m,'planner',endpoint,left='greedy') for m in MODELS
                      for endpoint in ['incident','authorized_completion']]
    primary=[x for x in contrasts if x['left']=='permissions' and x['right']=='planner' and x['endpoint']=='authorized_completion']
    holm(primary)
    groups=[]
    for m in MODELS:
        for a in arms:
            selected=[r for r in rows if r['model_key']==m and r['arm']==a]
            feasible=[r for r in selected if r['feasible']]
            complete=[r for r in feasible if r['authorized_completion'] is True]
            groups.append({'model_key':m,'arm':a,'incidents':binary(selected,'incident'),
                'authorized_completion':binary(feasible,'authorized_completion'),
                'statuses':dict(Counter(r['stop'] for r in selected)),
                'mean_steps_on_success':sum(r['steps'] for r in complete)/len(complete) if complete else None,
                'mean_excess_cost_on_success':sum(r['excess_resource_cost'] for r in complete)/len(complete) if complete else None,
                'advice_elapsed_seconds':sum(r['advice_elapsed_seconds'] for r in selected),
                'adherence':dict(adherence[m,a]),'estimated_usd':sum(r['estimated_usd'] for r in selected)})
    efficiency=[]
    for m in MODELS:
        bank={(r['task_id'],r['arm']):r for r in rows if r['model_key']==m}
        pairs=[(bank[t,'permissions'],bank[t,'planner']) for t in tasks
               if bank[t,'permissions']['feasible'] and
               bank[t,'permissions']['authorized_completion'] is True and
               bank[t,'planner']['authorized_completion'] is True]
        block={'model_key':m,'paired_successes':len(pairs),
               'interpretation':'Exploratory efficiency conditional on both arms completing safely; not a new primary endpoint.'}
        for field in ['estimated_usd','input_tokens','output_tokens','observed_api_seconds','advice_elapsed_seconds','steps','resources_used']:
            left=sum(a[field] for a,b in pairs); right=sum(b[field] for a,b in pairs)
            block[field]={'permissions_total':left,'planner_total':right,
                          'planner_over_permissions':right/left if left else None}
        efficiency.append(block)
    summary={'assigned':len(rows),'groups':groups,'contrasts':contrasts,'estimated_usd':base['estimated_usd'],
             'requests':base['requests'],'execution':base['execution'],
             'limitations':plan['limitations'],'efficiency':efficiency,'exploratory':exploratory}
    args.output.mkdir(parents=True,exist_ok=True)
    with (args.output/'episodes.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader()
        writer.writerows({k:'' if v is None else str(v).lower() if type(v) is bool else v for k,v in r.items()} for r in rows)
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    provenance={'plan_sha256':sha(study/'plan.json'),'source_hashes':plan['frozen_hashes'],
        'episodes_sha256':sha(args.output/'episodes.csv'),'evidence_hashes':evidence,
        'analysis_sha256':sha(Path(__file__)),'statistics_sha256':sha(Path(__file__).with_name('analyze_sabench_study.py')),
        'config':plan['config'],'primary':plan['primary'],'secondary':plan['secondary']}
    (args.output/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    names={'astra':'GPT-6 Astra','fable':'Fable 5.2'}
    label={'permissions':'Permissions only','greedy':'Greedy advice','planner':'Verified planner'}
    cell=lambda b:f"{b['positive']}/{b['assigned']} ({b['incomplete']})"
    lines=['# Prospective recovery-planning results','',
        'Author-constructed synthetic workflows with known transitions and trusted grants. These are separate from SABench and do not establish performance on real services.',
        '', 'Parentheses count incomplete outcomes. Completion excludes impossible tasks, if present.', '',
        '| Model | Guidance | Incidents | Authorized completion | Mean resource excess on success |',
        '| --- | --- | ---: | ---: | ---: |']
    for g in groups:
        excess=g['mean_excess_cost_on_success']
        lines.append(f"| {names[g['model_key']]} | {label[g['arm']]} | {cell(g['incidents'])} | {cell(g['authorized_completion'])} | {excess:.2f} |" if excess is not None else
                     f"| {names[g['model_key']]} | {label[g['arm']]} | {cell(g['incidents'])} | {cell(g['authorized_completion'])} | — |")
    lines += ['', ('Exploratory' if exploratory else 'Primary')+' comparisons: planner minus permissions-only authorized completion.', '',
              '| Model | Difference (pp) | Family bootstrap 95% interval | Holm p | Known pairs |',
              '| --- | ---: | --- | ---: | ---: |']
    for c in primary:
        if c['right_minus_left'] is None:
            lines.append(f"| {names[c['model_key']]} | — | — | — | 0/{c['assigned_pairs']} |")
        else:
            ci=c['template_clustered_ci95']
            lines.append(f"| {names[c['model_key']]} | {100*c['right_minus_left']:.2f} | [{100*ci[0]:.2f}, {100*ci[1]:.2f}] | {c['holm_primary_p']:.4f} | {c['complete_pairs']}/{c['assigned_pairs']} |")
    lines += ['', ('This fixed scaling grid was designed after observing ceiling performance in the original recovery comparison. Size strata share the same generator. All comparisons are exploratory.' if exploratory else 'All eight related generator families were fixed before inference.')+' No allocation extension or favorable subset selection. Zero observed incidents are not a guarantee. Search assumes correct public transitions and permissions; actor behavior remains advisory, not enforced.',
              '',f"Conservative list-price estimate: ${summary['estimated_usd']:.2f}; {summary['requests']} model requests. Not a billing statement."]
    lines += ['', 'Exploratory efficiency on task pairs that both arms complete safely:', '',
              '| Model | Paired successes | Planner / permissions output tokens | Planner / permissions estimated API cost |',
              '| --- | ---: | ---: | ---: |']
    for block in efficiency:
        token=block['output_tokens']['planner_over_permissions']; cost=block['estimated_usd']['planner_over_permissions']
        if token is not None and cost is not None:
            lines.append(f"| {names[block['model_key']]} | {block['paired_successes']} | {token:.3f} | {cost:.3f} |")
    (args.output/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'groups':groups,'primary':primary,'estimated_usd':summary['estimated_usd'],'requests':summary['requests']},indent=2))

if __name__=='__main__': main()
