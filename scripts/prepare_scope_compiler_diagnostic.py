"""Freeze all contracts whose structural operation changes under compilation.

Selection is by representation change, not actor success, and this remains a
retrospective diagnostic on already inspected tasks. No hidden labels select it.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import random
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from containment_extension.sabench_study import atomic,now,sha,digest,MODELS,RATES,tasks,contract_ops
from containment_extension.verified_planner import compile_office_contract

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args(); out=a.output.resolve(); out.mkdir(parents=True,exist_ok=False)
bank={t.task_id:t for t in tasks()}; selected=[]; lineage={}
for path in sorted((a.source/'contracts').glob('*/result.json')):
    record=json.loads(path.read_text()); contract=record.get('contract')
    if not contract or record.get('status')!='complete': continue
    t=bank[path.parent.name]; compiled=compile_office_contract(contract,t.s0)
    if compiled['valid'] and set(contract_ops(contract))!=set(contract_ops(compiled['contract'])):
        selected.append(t)
        lineage[t.task_id]=sha(path)
        atomic(out/'contracts'/t.task_id/'result.json',{'task_id':t.task_id,'status':'complete',
            'contract':contract,'source':'Reused original reviewed contract; no new scope inference',
            'original_result_sha256':sha(path)})
assert len(selected)==4,'Inspect unexpected diagnostic selection before any inference'
schedule=[]
for t in selected:
    for compiled in [False,True]:
        schedule.append({'task_id':t.task_id,'template_id':t.template_id,'state_type':t.state_type,
            'trap_type':t.trap_type,'ambiguous':t.is_ambiguous,'model_key':'astra','arm':'planner',
            'scope_compiler':compiled,'condition':'compiled' if compiled else 'raw'})
random.Random(20261114).shuffle(schedule)
for i,s in enumerate(schedule): s['run']=f'run-{i+1:05d}'
shutil.copytree(ROOT/'src/containment_extension',out/'source/containment_extension',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(ROOT/'third_party/sabench',out/'third_party/sabench',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
frozen={str(p.relative_to(out)):sha(p) for folder in [out/'source',out/'third_party',out/'contracts'] for p in folder.rglob('*') if p.is_file()}
plan={'version':'scope-compiler-diagnostic-v1','created_at':now(),'split':'diagnostic',
      'task_ids':[t.task_id for t in selected],'schedule':schedule,'frozen_hashes':frozen,
      'config':{'max_steps':16,'max_output_tokens':16384,'workers':4,'max_estimated_usd':None,
                'models':{'astra':MODELS['astra']},'rates':RATES,'arms':['planner'],'validate_scope':False},
      'request_ceiling':128,'original_contract_hashes':lineage,
      'primary':'None. Retrospective bug diagnostic; all structurally changed contracts included.',
      'limitations':['Already inspected tasks, selected by compiler-induced structural change; not representative incidence estimates.',
          'No new scope inference. Same actor and planner in both conditions; only argument compilation differs.',
          'Does not test an advantage over permissions-only guidance and does not replace original outcomes.']}
atomic(out/'plan.json',plan); atomic(out/'plan.sha256.json',{'sha256':digest(plan)})
atomic(out/'execution.json',{'status':'prepared_without_inference'})
print(json.dumps({'tasks':plan['task_ids'],'episodes':len(schedule),'purpose':plan['primary']}))
