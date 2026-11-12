"""Generate the incident-library appendix tables from data/incident_library.csv.

Standard library only. The 26 records are the motivating public-report library
frozen on 27 September 2026; codings are analyst drafts.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = list(csv.DictReader((ROOT / 'data/incident_library.csv').open()))
assert len(ROWS) == 26

CATEGORY = {
    'agent_scope_violation': 'Scope violation', 'evaluation_exposure': 'Evaluation exposure',
    'training_time_behavior': 'Training-time behaviour', 'external_attack_on_ai_infra': 'External attack',
    'human_directed_misuse': 'Human-directed misuse', 'attribution_unresolved': 'Attribution unresolved'}
PATHWAY = {
    'adaptive_escape': 'adaptive escape', 'misconfiguration_exposure': 'misconfiguration exposure',
    'live_access_overreach': 'live-access overreach', 'training_sample_boundary': 'training-sample boundary',
    'external_adversary': 'external adversary', 'unresolved': 'unresolved'}
STOP = {
    'manual_stop': 'Manual stop', 'automatic_stop_failed_then_manual': 'Auto-stop failed; manual',
    'retrospective_only': 'Retrospective only', 'human_stop_ignored': 'Human stop ignored',
    'none_observed': 'None observed', 'contained_by_third_party': 'Third-party containment',
    'self_stop_after_access': 'Self-stop after access', 'not_applicable': 'Not applicable'}
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MARK = {'present': r'\CIRCLE', 'yes': r'\CIRCLE', 'partial': r'\LEFTcircle', 'absent': r'\Circle',
        'no': r'\Circle', 'unknown': r'$\cdot$'}


def tex(s):
    s = (s.replace('\\', r'\textbackslash{}').replace('&', r'\&').replace('%', r'\%')
         .replace('$', r'\$').replace('#', r'\#').replace('_', r'\_')
         .replace('’', "'").replace('‘', "'").replace('≈', r'$\approx$')
         .replace('≥', r'$\geq$').replace('>', r'$>$').replace('<', r'$<$'))
    return s


def date(s, year=True):
    if not s:
        return 'n.r.'
    parts = s.split('-')
    y, m = int(parts[0]), MONTHS[int(parts[1]) - 1]
    out = f'{int(parts[2])} {m}' if len(parts) == 3 else m
    return f'{out} {y}' if year and y != 2026 else out


def occurred(r):
    a, b = r['occurred_start'], r['occurred_end']
    if not a:
        return 'n.r.'
    if b and b != a:
        return f'{date(a)}--{date(b)}'
    return date(a)


lines = [r'\begin{tabular}{@{}r R{2.2in} R{1.3in} R{0.9in} c R{1.6in}@{}}', r'\toprule',
         r'\# & Incident; reporting party; model(s) & Category; pathway & Occurred $\to$ disclosed & Ev. '
         r'& Counting unit \\', r'\midrule']
for r in ROWS:
    models = r['models'] or 'not identified'
    who = f"{tex(r['actor'])}; {tex(models)}"
    lines.append(
        f"{r['entry']} & {tex(r['title'])}. \\textit{{{who}}} & {CATEGORY[r['category']]}; "
        f"{PATHWAY[r['pathway']]} & {occurred(r)} $\\to$ {date(r['disclosed'])} & {r['evidence_level']} & "
        f"{tex(r['counting_unit'])} \\\\")
lines += [r'\bottomrule', r'\end{tabular}']
(ROOT / 'tables/incident-library.tex').write_text('\n'.join(lines) + '\n')

lines = [r'\begin{tabular}{@{}r R{1.3in} cccccc cccccc l R{0.78in} l@{}}', r'\toprule',
         r' & & \multicolumn{6}{c}{Leading indicators} & \multicolumn{6}{c}{Mechanisms} & & & \\',
         r'\cmidrule(lr){3-8}\cmidrule(lr){9-14}',
         r'\# & Incident & f & p & x & c & v & o & M1 & M2 & M3 & M4 & M5 & M6 & Layers & Stop behaviour & Lineage group \\',
         r'\midrule']
for r in ROWS:
    ind = ' & '.join(MARK[r[f'ind_{k}']] for k in 'fpxcvo')
    mech = ' & '.join(MARK[r[f'mech_M{k}']] for k in range(1, 7))
    lines.append(f"{r['entry']} & {tex(r['short_title'])} & {ind} & {mech} & {r['bas_layers'].replace('L', '')} & "
                 f"{STOP[r['stop_behavior']]} & \\texttt{{{tex(r['lineage_group'].removesuffix('-2026'))}}} \\\\")
lines += [r'\bottomrule', r'\end{tabular}']
(ROOT / 'tables/incident-codings.tex').write_text('\n'.join(lines) + '\n')
print('wrote tables/incident-library.tex and tables/incident-codings.tex')
