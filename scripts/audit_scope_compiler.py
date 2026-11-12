"""Retrospective compiler regression audit; never a new actor experiment."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from containment_extension.sabench_study import tasks,contract_ops,APICall,Trace,oracle_verify
from containment_extension.verified_planner import compile_office_contract

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('study',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    bank={t.task_id:t for t in tasks()}
    rows=[]; hashes={}
    for path in sorted((args.study/'contracts').glob('*/result.json')):
        raw=json.loads(path.read_text())
        if raw.get('status')!='complete' or not raw.get('contract'): continue
        task=bank[path.parent.name]
        # Compiler is called before the audit accesses any gold authorization.
        result=compile_office_contract(raw['contract'],task.s0)
        before=set(contract_ops(raw['contract']))
        after=set(contract_ops(result['contract'])) if result['valid'] else None
        rows.append({'task_id':task.task_id,'valid':result['valid'],'changes':result['changes'],
                     'errors':result['errors'],'before_exact':before==task.A_explicit,
                     'after_exact':after==task.A_explicit if after is not None else None,
                     'before_extra':len(before-task.A_explicit),
                     'after_extra':len(after-task.A_explicit) if after is not None else None,
                     'original_contract':raw['contract'],'compiled_contract':result['contract']})
        hashes[str(path.relative_to(args.study))]=sha(path)
    summary={'contracts':len(rows),'changed':sum(bool(r['changes']) for r in rows),
             'invalid':sum(not r['valid'] for r in rows),
             'exact_before':sum(r['before_exact'] for r in rows),
             'exact_after':sum(r['after_exact'] is True for r in rows),
             'extra_write_contracts_before':sum(r['before_extra']>0 for r in rows),
             'extra_write_contracts_after':sum((r['after_extra'] or 0)>0 for r in rows),
             'compiler_sha256':sha(ROOT/'src/containment_extension/verified_planner.py'),
             'source_plan_sha256':sha(args.study/'plan.json'),'contract_hashes':hashes,
             'interpretation':'Retrospective deterministic regression on previously inspected tasks; does not change recorded model outcomes or establish an actor/planner advantage.'}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.output/'contracts.json').write_text(json.dumps(rows,indent=2)+'\n')
    lines=['# Scope compiler regression audit','',summary['interpretation'],'',
           f"The compiler changes {summary['changed']}/{len(rows)} contracts. Exact reference agreement changes from {summary['exact_before']}/{len(rows)} to {summary['exact_after']}/{len(rows)}. It rejects {summary['invalid']} unrepresentable contracts.",
           '',f"Contracts proposing an unauthorized write: {summary['extra_write_contracts_before']} before, {summary['extra_write_contracts_after']} after compilation.",
           '', 'This repairs date/time representation using public API semantics. It does not resolve semantic permission ambiguity or claim that the original model incidents disappeared.']
    (args.output/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='contract_hashes'},indent=2))

if __name__=='__main__': main()
