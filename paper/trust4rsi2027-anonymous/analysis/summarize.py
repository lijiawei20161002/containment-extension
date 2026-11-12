"""Rebuild paper tables and descriptive statistics from the anonymous CSVs.

Python 3 standard library only. Run from any directory; no network or API calls.
"""
import csv
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = list(csv.DictReader((ROOT/'data/episodes.csv').open()))
COHORTS = list(csv.DictReader((ROOT/'data/cohorts.csv').open()))
ADVICE = list(csv.DictReader((ROOT/'data/advice_transitions.csv').open()))
ARMS = ['plain','journal','planner','planner_journal','broker']
LABELS = {'plain':'Plain','journal':'Journal','planner':'Planner','planner_journal':'Planner + journal','broker':'Broker',
          'journal_audited':'Journal + audited','journal_unaudited':'Journal + unaudited'}
MODELS = {'C01':'Haiku 4.5','C02':'Haiku 5.5','C03':'Sonnet 4.6','C04':'Sonnet 5',
          'C05':'Sonnet 5.5','C06':'Haiku 4.5','C07':'Sonnet 5','C08':'Sonnet 5.5',
          'C09':'Haiku 4.5','C10':'Sonnet 4.6'}

def select(cohort, candidate=None, family=None):
    return [r for r in ROWS if r['cohort']==cohort and (candidate is None or r['candidate']==candidate)
            and (family is None or r['family']==family)]

def counts(rows,field='incident'):
    return sum(r[field]=='true' for r in rows),sum(r[field]=='' for r in rows),len(rows)

def cell(rows,field='incident'):
    i,u,n=counts(rows,field)
    return f'{i}/{n} ({u})'

def matched(cohort,candidate):
    b={r['seed']:r for r in select(cohort,candidate.split('-')[0]+'-plain','impossible')}
    a={r['seed']:r for r in select(cohort,candidate,'impossible')}
    ds=[int(a[k]['incident']=='true')-int(b[k]['incident']=='true') for k in b if a[k]['incident'] and b[k]['incident']]
    worse,better=ds.count(1),ds.count(-1)
    d=worse+better
    p=min(1.,2*sum(math.comb(d,k) for k in range(min(worse,better)+1))/2**d) if d else 1.
    ia,ua,n=counts(list(a.values()));ib,ub,_=counts(list(b.values()))
    return dict(cohort=cohort,candidate=candidate,complete_pairs=len(ds),better=better,worse=worse,
                difference=sum(ds)/len(ds),p=p,lower=(ia-ib-ub)/n,upper=(ia+ua-ib)/n)

def table(name,lines):
    (ROOT/'tables'/name).write_text('\n'.join(lines)+'\n')

def main():
    table('native.tex',[
        r'\begin{tabular}{llrrrrrr}',r'\toprule',
        r'& & \multicolumn{3}{c}{Haiku 4.5} & \multicolumn{3}{c}{Sonnet 4.6} \\',
        r'$b$ & Arm & Incidents ($U$) & Attempts & Completion ($U_C$) & Incidents ($U$) & Attempts & Completion ($U_C$) \\',r'\midrule',
        *[str(b)+' & '+LABELS[a]+' & '+' & '.join(
            ' & '.join([cell(select(c,f'b{b}-{a}','impossible')),
                        f"{sum(int(r['attempted_outside'] or 0)>0 for r in select(c,f'b{b}-{a}','impossible'))}/16",
                        cell([r for r in select(c,f'b{b}-{a}') if r['family']!='impossible'],'authorized_completion')])
            for c in ['C09','C10'])+r' \\' for b in [0,8] for a in ARMS if not (b==8 and a=='broker')],
        r'\bottomrule',r'\end{tabular}'])
    table('workflow.tex',[
        r'\begin{tabular}{llrrrr}',r'\toprule',r'Model & $b$ & Plain & Journal & Planner & Both \\',r'\midrule',
        *[MODELS[c]+f' & {b} & '+' & '.join(
            f"{counts(select(c,f'b{b}-{a}'))[0]} ({counts(select(c,f'b{b}-{a}'))[1]}); {sum(r['authorized_completion']=='true' for r in select(c,f'b{b}-{a}'))}"
            for a in ARMS[:4])+r' \\' for c in ['C01','C02','C03','C04'] for b in [0,8]],
        r'\bottomrule',r'\end{tabular}'])
    table('awareness.tex',[
        r'\begin{tabular}{llrr}',r'\toprule',r'Alternate & Arm & Haiku 4.5 & Sonnet 5 \\',r'\midrule',
        *[('Cost 3' if cost==3 else 'Bonus 4')+' & '+LABELS[a]+' & '+
          ' & '.join(cell(select(c,('b0-' if cost==3 else 'b0-am4-')+a)) for c in ['C06','C07'])+r' \\'
          for cost in [3,-4] for a in ['plain','planner','journal','journal_audited','journal_unaudited']],
        r'\bottomrule',r'\end{tabular}'])
    contrasts=[matched(c,f'b{b}-{a}') for c in ['C09','C10'] for b in [0,8] for a in ARMS[1:] if not (b==8 and a=='broker')]
    table('contrasts.tex',[
        r'\begin{tabular}{llrrrr}',r'\toprule',r'Model & Contrast vs. plain & Pairs & Better/worse & $\Delta$ & $p$ \\',r'\midrule',
        *[MODELS[x['cohort']]+' & '+x['candidate'].replace('_',r'\_')+f" & {x['complete_pairs']}/16 & {x['better']}/{x['worse']} & {x['difference']:+.3f} & {x['p']:.4f}"+r' \\' for x in contrasts],
        r'\bottomrule',r'\end{tabular}'])
    table('adherence.tex',[
        r'\begin{tabular}{llrrrr}',r'\toprule',r'& & \multicolumn{2}{c}{Planner} & \multicolumn{2}{c}{Planner + journal} \\',
        r'Model & $b$ & Agree/next & First STOP & Agree/next & First STOP \\',r'\midrule',
        *[MODELS[c]+f' & {b} & '+' & '.join(
            f"{sum(x['agrees']=='true' for x in ADVICE if x['cohort']==c and x['candidate']==f'b{b}-{a}')}/{sum(x['cohort']==c and x['candidate']==f'b{b}-{a}' for x in ADVICE)} & "+
            f"{sum(t['steps'][0]['operation']=='STOP' for t in json.loads((ROOT/'data/action_traces.json').read_text()) if t['cohort']==c and t['episode'].endswith(f'-b{b}-{a}') and t['steps'])}/16"
            for a in ['planner','planner_journal'])+r' \\' for c in ['C01','C02','C03','C04'] for b in [0,8]],
        r'\bottomrule',r'\end{tabular}'])
    inventory=[r'\begin{tabular}{llrr}',r'\toprule',r'ID & Model & Plan/recorded & Test \\',r'\midrule']
    for study,title in [('decision-algorithms','Workflow'),('eval-awareness','Audit cues'),('native-algorithms','Native')]:
        inventory.append(r'\multicolumn{4}{l}{'+title+r'} \\')
        for r in COHORTS:
            if r['study']!=study:continue
            inventory.append(r['cohort']+(r'$^{\dagger}$' if r['status']=='interrupted' else '')+' & '+MODELS[r['cohort']]+' & '+r['assigned']+'/'+r['recorded']+' & '+r['historical_test']+r' \\')
    table('cohorts.tex',inventory+[r'\bottomrule',r'\end{tabular}'])
    details={}
    for c in COHORTS:
        rs=select(c['cohort']);i,u,n=counts(rs)
        details[c['cohort']]=dict(incidents=i,unknown=u,recorded=n,not_recorded=int(c['assigned'])-n,
            repeat_effects=None if c['study']=='native-algorithms' else sum(int(r['repeat_effects'] or 0) for r in rs),
            statuses=dict(Counter(r['status'] for r in rs)))
    (ROOT/'data/summary.json').write_text(json.dumps(dict(cohorts=details,contrasts=contrasts),indent=2)+'\n')
    print(json.dumps(dict(episodes=len(ROWS),cohorts=details),indent=2))

if __name__=='__main__':
    main()
