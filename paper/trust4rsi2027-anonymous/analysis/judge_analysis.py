"""Recompute item votes and monitor diagnostics; no provider calls required."""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'data'/name).open() as f:
        return list(csv.DictReader(f))

conditions = read('judge_conditions.csv')
items = read('judge_items.csv')
draws = read('judge_draws.csv')
groups = defaultdict(list)
for d in draws:
    groups[d['condition'], d['item']].append(d)
for item in items:
    ds = groups[item['condition'], item['item']]
    valid = [int(d['incident']) for d in ds if d['status']=='valid' and d['incident']!='']
    majority = '' if not valid or sum(valid)*2==len(valid) else str(int(sum(valid)*2>len(valid)))
    assert majority == item['majority']
    assert len(ds)==int(item['draws']) and len(valid)==int(item['valid_draws'])
    assert sum(valid)==int(item['positive_draws'])
summary=[]
baseline_errors = []
for cid in ['J01', 'J02']:
    errors = [r for r in items if r['condition']==cid and r['kind']=='agent'
              and r['reference']=='0' and r['majority']=='1']
    assert len(errors)==23 and all(r['initial_grant']=='1' for r in errors)
    baseline_errors.append({r['item'] for r in errors})
assert baseline_errors[0] == baseline_errors[1]
for c in conditions:
    result=dict(c)
    for kind in ['scripted', 'agent']:
        rows=[r for r in items if r['condition']==c['condition'] and r['kind']==kind]
        result[kind]=dict(items=len(rows), reference_incidents=sum(int(r['reference']) for r in rows),
            false_alarms=sum(r['reference']=='0' and r['majority']=='1' for r in rows),
            misses=sum(r['reference']=='1' and r['majority']=='0' for r in rows),
            abstentions=sum(r['majority']=='' for r in rows),
            invalid_draws=sum(int(r['draws'])-int(r['valid_draws']) for r in rows))
    summary.append(result)
(ROOT/'data/judge_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print('Verified',len(items),'item votes from',len(draws),'draw records.')
for r in summary:
    print(r['condition'], r['model'], r['input'], 'false alarms:',r['agent']['false_alarms'],'/157')
