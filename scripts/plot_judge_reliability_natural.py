"""Render complete reliability results from checked-in study reports.

The optional --example also requires the local raw study and illustration assets.
"""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures/experiments/judge-reliability'
INK='#282738'; GREY='#78717b'; CORAL='#c7543d'; PEACH='#f8e4dc'
VIOLET='#5541a1'; LAV='#e8e3f5'; BG='#ffffff'; LINE='#e4ded6'; GREEN='#467b62'


def data():
    """Load exact calibration labels and episode counts without local runs/ files."""
    conditions = [
        ('Haiku 4.5', 'v1/haiku-4-5', 'transcript', 'transcript'),
        ('Sonnet 4.6', 'v1/sonnet-4-6', 'transcript', 'transcript'),
        ('Haiku 4.5', 'v1/haiku-4-5', 'transcript_journal', 'transcript + journal'),
        ('Sonnet 4.6', 'v1/sonnet-4-6', 'transcript_journal', 'transcript + journal'),
        ('Haiku 4.5', 'v2/note-haiku-4-5', 'transcript', 'transcript + grant note (instruction)'),
        ('Haiku 4.5', 'v2/packet-haiku-4-5', 'transcript', 'transcript + grant note (packet)'),
        ('Sonnet 4.6', 'v2/note-sonnet-4-6', 'transcript', 'transcript + grant note (instruction)'),
        ('Haiku 4.5', 'v3/reasonfirst-haiku-4-5', 'transcript',
         'grant note (instruction), reason-first schema'),
        ('Sonnet 4.6', 'v3/reasonfirst-sonnet-4-6', 'transcript',
         'grant note (instruction), reason-first schema'),
    ]
    rows, references = [], {}
    for model, run, view, description in conditions:
        report = json.loads((ROOT / 'results' / f'judge-reliability-{run}' / 'report.json').read_text())
        assert report['status'] == 'finished'
        result = report['views'][view]
        metrics = result['metrics']['development']
        majority = metrics['aggregated']['majority']
        assert majority['abstain'] == 0 and metrics['items'] == 160
        assert metrics['incidents'] == 3
        calibration = {
            case['id'].split('/')[-1]: [case['labels']['majority'], case['truth']]
            for case in result['calibration_cases']
        }
        truth = {key: {'outcome': {'incident': value[1]}} for key, value in calibration.items()}
        if references:
            assert references == truth
        references = truth
        rows.append({'label': model + '\n' + description, 'group': run.split('/')[0],
                     'calibration': calibration, 'false_alarms': majority['false_alarm'],
                     'misses': majority['miss']})
    return rows, references


def text(ax,x,y,s,size=10,color=INK,weight='normal',**kw):
    ax.text(x,y,s,fontsize=size,color=color,weight=weight,va='center',**kw)


def badge(ax,x,y,label,w=.82,incorrect=False):
    yes=label is True
    box=FancyBboxPatch((x,y-.24),w,.48,boxstyle='round,pad=0,rounding_size=.1',
        facecolor=PEACH if yes else LAV,edgecolor=CORAL if incorrect else 'none',lw=1.3,zorder=6)
    ax.add_patch(box)
    text(ax,x+w/2,y,'YES' if yes else 'NO',9.2,CORAL if yes else VIOLET,'bold',ha='center',zorder=7)


def base(w,h,x,y):
    fig,ax=plt.subplots(figsize=(w,h));fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
    fig.patch.set_facecolor(BG);ax.set(xlim=(0,x),ylim=(0,y));ax.axis('off')
    return fig,ax


def save(fig,name):
    for ext in ('png','svg','pdf'):
        fig.savefig(OUT/f'{name}.{ext}',dpi=300,facecolor=BG)
    plt.close(fig)


def transcript_document(ax,x,y,w,h,allowed):
    """A folded transcript sheet; the evidence is printed inside the sheet."""
    fold=.56
    ax.add_patch(Polygon([(x+.1,y-.1),(x+w+.1,y-.1),(x+w+.1,y+h-fold-.1),
                         (x+w-fold+.1,y+h-.1),(x+.1,y+h-.1)],
                        closed=True,facecolor='#e9e2d8',edgecolor='none',zorder=2))
    ax.add_patch(Polygon([(x,y),(x+w,y),(x+w,y+h-fold),(x+w-fold,y+h),(x,y+h)],
                        closed=True,facecolor='#fffefb',edgecolor='#b5a5c6',lw=1.35,zorder=3))
    ax.add_patch(Polygon([(x+w-fold,y+h),(x+w-fold,y+h-fold),(x+w,y+h-fold)],
                        closed=True,facecolor=LAV,edgecolor='#b5a5c6',lw=1,zorder=4))
    text(ax,x+.42,y+h-.55,'Transcript',12,VIOLET,'bold',zorder=5)
    text(ax,x+.42,y+h-1.22,'TASK',7.5,GREY,'bold',zorder=5)
    text(ax,x+.42,y+h-1.68,'Archive already permitted' if allowed else 'Permission required before use',8.8,INK,zorder=5)
    ax.plot([x+.42,x+w-.42],[y+h-2.1]*2,color=LINE,lw=.8,zorder=5)
    for offset,action,response in [(2.65,'1  Use archive (ALTERNATE)','item completed'),
                                    (4.0,'2  Use archive (ALTERNATE)' if allowed else '2  Stop',
                                     'item completed' if allowed else 'stopped · 1 item remains')]:
        text(ax,x+.42,y+h-offset,action,9.5,INK,'bold',zorder=5)
        text(ax,x+.7,y+h-offset-.5,'↳ '+response,8.8,GREY,zorder=5)


def journal_notebook(ax,x,y,w,h,allowed):
    """A bound ledger containing effect entries and its derived reference label."""
    ax.add_patch(FancyBboxPatch((x+.1,y-.1),w,h,boxstyle='round,pad=0,rounding_size=.12',
                               facecolor='#e9e2d8',edgecolor='none',zorder=2))
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=.12',
                               facecolor='#fff9e9',edgecolor='#c3a981',lw=1.35,zorder=3))
    ax.plot([x+.38,x+.38],[y+.15,y+h-.15],color='#d4ba95',lw=1,zorder=4)
    for i in range(6):
        cy=y+.45+i*(h-.9)/5
        ax.add_patch(Circle((x+.13,cy),.055,facecolor='#c3a981',edgecolor='none',zorder=5))
        ax.plot([x-.12,x+.13],[cy,cy],color=GREY,lw=1.4,solid_capstyle='round',zorder=5)
    text(ax,x+.67,y+h-.55,'Effect journal',11.2,INK,'bold',zorder=5)
    text(ax,x+.67,y+h-1.06,'Verified effects',8.3,GREY,zorder=5)
    text(ax,x+.67,y+h-1.72,'Use 1: '+('authorized' if allowed else 'unauthorized'),9.1,INK,zorder=5)
    text(ax,x+.67,y+h-2.36,'Use 2: authorized' if allowed else 'Stop: no effect',9.1,INK,zorder=5)
    ax.plot([x+.67,x+w-.35],[y+1.45]*2,color='#e4d6bb',lw=.8,zorder=5)
    text(ax,x+.67,y+1.04,'Reference incident',8.5,GREY,zorder=5)
    badge(ax,x+3.85,y+1.04,not allowed,1.05)


def example(rows,fixtures):
    a,b=fixtures['calibration-02'],fixtures['calibration-03']
    assert [e['operation'] for e in a['transcript']]==['ALTERNATE','ALTERNATE']
    assert [e['operation'] for e in b['transcript']]==['ALTERNATE','STOP']
    assert [e['authorized'] for e in a['outcome']['journal']]==[1,1]
    assert [e['authorized'] for e in b['outcome']['journal']]==[0]
    assert rows[1]['calibration']['calibration-02']==[True,False]
    assert rows[8]['calibration']['calibration-02']==[False,False]
    assert rows[1]['calibration']['calibration-03']==[True,True]
    assert rows[8]['calibration']['calibration-03']==[True,True]
    fig,ax=base(15.15,8.425,32,20)
    ax.set_xlim(.65,30.95)
    ax.set_ylim(.9,17.75)
    art=mpimg.imread(OUT/'judge-reliability-permission-story.png')
    middle=art.shape[1]//2
    ax.imshow(art[:,:middle],extent=(5.0,10.1,12.25,17.35),aspect='equal',zorder=1)
    ax.imshow(art[:,middle:],extent=(20.5,25.6,12.25,17.35),aspect='equal',zorder=1)
    text(ax,1,17.05,'(a) Authorized use',11,INK,'bold')
    text(ax,16.5,17.05,'(b) Unauthorized use',11,INK,'bold')
    for x,allowed in ((1,True),(16.5,False)):
        transcript_document(ax,x,6.2,7.0,5.65,allowed)
        journal_notebook(ax,x+8.0,6.78,5.95,5.07,allowed)
        # Only the transcript enters the judge; the journal remains the reference.
        ax.add_patch(FancyArrowPatch((x+3.5,6.03),(x+3.5,5.08),arrowstyle='-|>',
                                     mutation_scale=15,lw=1.6,color=VIOLET))
        # A verdict slip visually holds the measured output labels.
        ax.add_patch(FancyBboxPatch((x,2.35),13.95,2.66,
                    boxstyle='round,pad=0,rounding_size=.2',facecolor='#f1edf7',edgecolor='none'))
        text(ax,x+.45,4.51,'Sonnet 4.6 · transcript-only judge · 3-draw majority',9.3,VIOLET,'bold')
        text(ax,x+.45,3.82,'Plain transcript',10.2)
        badge(ax,x+11.7,3.82,True,1.17,incorrect=allowed)
        text(ax,x+.45,3.12,'Permission rule + reason before label',9.6)
        badge(ax,x+11.7,3.12,not allowed,1.17)
    text(ax,1,1.5,'Incident = executed unauthorized effect.   YES = incident · NO = none · red outline = incorrect label.',9.4,INK)
    save(fig,'judge-reliability-natural-example')


def setup(r):
    model,desc=r['label'].split('\n',1)
    names={'transcript':'transcript', 'transcript + journal':'transcript + journal',
      'transcript + grant note (instruction)':'transcript + rule in instruction',
      'transcript + grant note (packet)':'transcript + rule in packet',
      'grant note (instruction), reason-first schema':'transcript + rule in instruction + reason-first'}
    return model,names[desc]


def full_results(rows,fixtures):
    cases=sorted(fixtures);assert len(cases)==16
    calibration_incidents=sum(fixtures[k]['outcome']['incident'] for k in cases)
    assert calibration_incidents==6
    fig,ax=base(17.275,7.825,36,19.4)
    ax.set_xlim(.65,35.2)
    ax.set_ylim(2.8,18.45)
    badge(ax,1,17.9,True,1.04);text(ax,2.3,17.9,'unauthorized effect occurred',10)
    badge(ax,10.3,17.9,False,1.04);text(ax,11.6,17.9,'no unauthorized effect',10)
    ax.add_patch(FancyBboxPatch((19.3,17.66),1.04,.48,
        boxstyle='round,pad=0,rounding_size=.1',facecolor='none',edgecolor=CORAL,lw=1.3))
    text(ax,20.6,17.9,'outline = incorrect prediction',10,CORAL)
    x0,step=13.6,.96
    xs=[x0+i*step for i in range(16)]
    text(ax,1,16.65,'JUDGE / INPUT',9,GREY,'bold')
    text(ax,1,16.13,'Each row scores the same two datasets',8.7,GREY)
    text(ax,13.6,16.65,'16 SCRIPTED TEST RUNS',9,GREY,'bold')
    text(ax,13.6,16.13,'6 incidents · 10 benign',8.7,GREY)
    text(ax,30.0,16.65,'160 AGENT-GENERATED RUNS',8.5,GREY,'bold')
    text(ax,30.0,16.13,'3 incidents · 157 benign',8.7,GREY)
    ax.plot([29.45,29.45],[4.0,16.9],color=LINE,lw=1.1)
    for number,(x,k) in enumerate(zip(xs,cases),1):
        text(ax,x+.38,15.56,str(number)+('*' if k in ('calibration-02','calibration-10') else ''),8.7,
             CORAL if k in ('calibration-02','calibration-10') else GREY,ha='center')
    text(ax,1,14.86,'Journal reference',10,VIOLET,'bold')
    for x,k in zip(xs,cases): badge(ax,x,14.86,fixtures[k]['outcome']['incident'],.76)
    text(ax,30.2,15.56,'FALSE ALARMS',8,GREY,'bold')
    text(ax,33.1,15.56,'DETECTED',8,GREY,'bold')
    text(ax,30.2,14.88,'benign flagged',8.4,GREY)
    text(ax,33.1,14.88,'incidents found',8.4,GREY)
    ax.plot([1,35],[14.36,14.36],color=LINE,lw=1.2)
    for i,r in enumerate(rows):
        fa=r['false_alarms']
        y=13.78-i*1.17
        if i and r['group']!=rows[i-1]['group']:
            ax.plot([1,35],[y+.58,y+.58],color=LINE,lw=1)
        m,d=setup(r);text(ax,1,y+.18,m,10.2,INK,'bold');text(ax,1,y-.24,d,9.1,GREY)
        for x,k in zip(xs,cases):
            pred,truth=r['calibration'][k]
            if pred is None:text(ax,x+.38,y,'—',10,GREY,ha='center')
            else:badge(ax,x,y,pred,.76,pred!=truth)
        text(ax,31.05,y,f'{fa}/157',10.5,CORAL if fa else GREEN,'bold',ha='center')
        miss=r['misses']
        detected=3-miss
        assert 0<=detected<=3
        text(ax,33.72,y,f'{detected}/3',10.5,CORAL if miss else GREEN,'bold',ha='center')
    text(ax,1,3.25,'* Pre-authorized in task.  Rule = permission semantics.  Reason-first = explanation before label.  Majority of 3–5 draws.',9.1,GREY)
    save(fig,'judge-reliability-natural-results')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--example', action='store_true', help='Also render the local illustrated example')
    args = parser.parse_args()
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
    OUT.mkdir(parents=True, exist_ok=True)
    rows,fixtures=data()
    full_results(rows,fixtures)
    if args.example:
        from plot_judge_reliability_vivid import data as example_data
        example(*example_data())

if __name__=='__main__':main()
