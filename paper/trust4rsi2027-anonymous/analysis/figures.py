"""Render the paper's vector figures. Requires matplotlib; no network access."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from summarize import select, counts, LABELS

ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,
                     'axes.spines.top':False,'axes.spines.right':False})
META={'Author':'','Creator':'','Title':'Anonymous research figure','CreationDate':None,'ModDate':None}

fig,axes=plt.subplots(1,2,figsize=(6.9,2.65),sharey=True)
arms=['plain','journal','planner','planner_journal','broker']
for ax,c,name in zip(axes,['C09','C10'],['Haiku 4.5','Sonnet 4.6']):
    for b,color,shift,marker in [(0,'#256582',.14,'o'),(8,'#b75a30',-.14,'s')]:
        for y,a in enumerate(arms):
            if b==8 and a=='broker':continue
            i,u,n=counts(select(c,f'b{b}-{a}','impossible'))
            ax.plot([100*i/n,100*(i+u)/n],[y+shift]*2,color=color,lw=3)
            ax.scatter([100*i/n],[y+shift],marker=marker,s=24,color=color,zorder=3,
                       label=f'Stop reward {b}' if y==0 else None)
            ax.scatter([100*(i+u)/n],[y+shift],marker='|',s=55,color=color,zorder=3)
    ax.set_title(name,fontsize=10)
    ax.set_xticks([0,25,50,75,100]);ax.set_xlim(-3,103)
    ax.set_xlabel('Incident fraction bounds (%)')
    ax.grid(axis='x',color='#dddddd',lw=.5)
    ax.set_axisbelow(True)
axes[0].set_yticks(range(5),[LABELS[a] for a in arms]);axes[0].invert_yaxis()
axes[1].legend(loc='lower right',fontsize=9,frameon=False)
fig.tight_layout(pad=.6,w_pad=1.3)
fig.savefig(ROOT/'figures/native-bounds.pdf',metadata=META)
plt.close(fig)

fig,ax=plt.subplots(figsize=(6.9,2.0))
ax.set_xlim(0,10);ax.set_ylim(0,3.1);ax.axis('off')
def box(x,y,w,h,text,color):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04,rounding_size=0.08',
                               facecolor=color,edgecolor='#354556',lw=.8))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9)
def arrow(a,b):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,lw=.9,color='#354556'))
box(.1,1.05,1.75,.86,'Trusted grant\nand service state','#e8edf3')
box(2.35,1.9,2.15,.93,'Grant Look-ahead\nPermitted values\nand recommendation','#e2eff4')
box(4.9,1.05,1.45,.86,'LLM actor\nChooses action','#f7f5ef')
box(7.0,1.05,2.8,.86,'Service dispatcher\nOptional scope broker','#e8edf3')
box(2.35,.15,2.15,.78,'Effect Journal\nCommitted outcomes','#f5e6dd')
arrow((1.85,1.7),(2.35,2.15));arrow((4.5,2.3),(5.4,1.91))
arrow((6.35,1.48),(7.0,1.48));arrow((4.5,.55),(5.4,1.05))
ax.plot([8.4,8.4,4.65],[1.05,.48,.48],color='#354556',lw=.9)
arrow((4.65,.48),(4.5,.48))
ax.text(8.35,2.35,'Plain / feedback arms: dispatch\nBroker arm: reject excluded calls',ha='center',va='center',fontsize=9)
ax.text(1.05,.28,'Only trusted replies\nchange permission',ha='center',fontsize=9)
fig.subplots_adjust(left=.005,right=.995,top=.99,bottom=.01)
fig.savefig(ROOT/'figures/architecture.pdf',metadata=META)
plt.close(fig)
print('Wrote two vector PDF figures.')
