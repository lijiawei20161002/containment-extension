"""Prepare, execute or summarize the frozen prospective recovery planning study."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['prepare','run','report'])
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,choices=range(1,9))
    p.add_argument('--mode',choices=['recovery','allocation'],default='recovery')
    args=p.parse_args(); output=args.output.resolve()
    sys.path.insert(0,str(ROOT/'src' if args.command=='prepare' else output/'source'))
    from containment_extension.recovery_planning_study import prepare,execute,report
    if args.command=='prepare':
        plan=prepare(output,args.mode)
        print(json.dumps({'tasks':len(plan['task_ids']),'episodes':len(plan['schedule']),'request_ceiling':plan['request_ceiling']}))
    elif args.command=='run':
        from containment_extension.config import load_env
        load_env(ROOT.parent/'.env')
        os.environ['SSL_CERT_FILE']=str(ROOT/'.venv/lib/python3.13/site-packages/certifi/cacert.pem')
        execute(output,args.workers)
    else:
        result=report(output)
        print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))

if __name__=='__main__': main()
