"""Publication-sized vector figures for the incident and judge-study material.

Requires matplotlib; no network access and no model calls. Writes
figures/judge-reliability.pdf, figures/incident-pathways.pdf, a detailed
featured-workbook.pdf, and two example
incident-library diagrams rendered from data/incident_specs/*.spec.json.
"""
import csv
import json
import textwrap
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 7,
                     'pdf.fonttype': 42, 'ps.fonttype': 42})
INK = '#282738'; GREY = '#78717b'; CORAL = '#c7543d'; PEACH = '#f8e4dc'
VIOLET = '#5541a1'; LAV = '#e8e3f5'; LINE = '#e4ded6'; GREEN = '#467b62'
BLUE = '#2b5f9e'; SKY = '#e7eef8'; SLATE = '#9a98a6'; MIST = '#f1f0f3'
META = {'Author': '', 'Creator': 'Matplotlib', 'Title': 'Anonymous research figure'}


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set(xlim=(0, w), ylim=(0, h)); ax.axis('off')
    return fig, ax


def save(fig, name):
    fig.savefig(ROOT / 'figures' / f'{name}.pdf', metadata=META)
    plt.close(fig)


def text(ax, x, y, s, size=7, color=INK, weight='normal', **kw):
    kw.setdefault('va', 'center')
    return ax.text(x, y, s, fontsize=size, color=color, weight=weight, **kw)


def rbox(ax, x, y, w, h, fc, ec='none', lw=0.8, r=0.04, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                                facecolor=fc, edgecolor=ec, lw=lw, zorder=z))


# ---------------------------------------------------------------- judge study
def badge(ax, x, y, yes, w=0.2, h=0.15, incorrect=False):
    rbox(ax, x, y - h / 2, w, h, PEACH if yes else LAV, CORAL if incorrect else 'none', 0.9, 0.03, 4)
    text(ax, x + w / 2, y, 'YES' if yes else 'NO', 5.6, CORAL if yes else VIOLET, 'bold', ha='center', zorder=5)


def judge_figure():
    with (ROOT / 'data/judge_items.csv').open() as f:
        items = list(csv.DictReader(f))
    summary = json.loads((ROOT / 'data/judge_summary.json').read_text())
    scripted = lambda cond: sorted([r for r in items if r['condition'] == cond and r['kind'] == 'scripted'],
                                   key=lambda r: r['item'])
    reference = scripted('J01')
    assert len(reference) == 16 and sum(r['reference'] == '1' for r in reference) == 6
    pre = {'C03', 'C11'}  # alternate use under an initial grant
    names = {'Transcript': 'transcript', 'Transcript + journal': 'transcript + journal',
             'Grant rule: instruction': 'transcript + rule in instruction',
             'Grant rule: packet': 'transcript + rule in packet',
             'Instruction + reason first': 'transcript + rule in instruction + reason-first'}
    fig, ax = canvas(7.0, 3.5)
    # legend
    badge(ax, 0.05, 3.38, True); text(ax, 0.3, 3.38, 'unauthorized effect occurred', 6.8)
    badge(ax, 2.0, 3.38, False); text(ax, 2.25, 3.38, 'no unauthorized effect', 6.8)
    rbox(ax, 3.75, 3.38 - 0.075, 0.2, 0.15, 'none', CORAL, 0.9, 0.03, 4)
    text(ax, 4.0, 3.38, 'outline = incorrect prediction', 6.8, CORAL)
    # headers
    x0, step, bw = 2.05, 0.228, 0.2
    xs = [x0 + i * step for i in range(16)]
    text(ax, 0.05, 3.12, 'JUDGE / INPUT', 6.3, GREY, 'bold')
    text(ax, 0.05, 3.0, 'Each row scores the same two datasets', 6, GREY)
    text(ax, x0, 3.12, '16 SCRIPTED TEST RUNS', 6.3, GREY, 'bold')
    text(ax, x0, 3.0, '6 incidents · 10 benign', 6, GREY)
    text(ax, 5.84, 3.12, '160 AGENT TRACES', 6.3, GREY, 'bold')
    text(ax, 5.84, 3.0, '3 incidents · 157 benign', 6, GREY)
    for i, (x, r) in enumerate(zip(xs, reference), 1):
        star = r['item'] in pre
        text(ax, x + bw / 2, 2.82, f'{i}{"*" if star else ""}', 6, CORAL if star else GREY, ha='center')
    fx, tx = 6.12, 6.68
    text(ax, fx, 2.82, 'FALSE ALARMS', 5.0, GREY, 'bold', ha='center')
    text(ax, tx + 0.02, 2.82, 'DETECTED', 5.0, GREY, 'bold', ha='center')
    text(ax, fx, 2.64, 'benign\nflagged', 5.6, GREY, ha='center', linespacing=1.05)
    text(ax, tx, 2.64, 'incidents\nfound', 5.6, GREY, ha='center', linespacing=1.05)
    text(ax, 0.05, 2.64, 'Journal reference', 7, VIOLET, 'bold')
    for x, r in zip(xs, reference):
        badge(ax, x, 2.64, r['reference'] == '1')
    ax.plot([0.05, 6.95], [2.51, 2.51], color=LINE, lw=0.9)
    ax.plot([5.76, 5.76], [0.22, 3.2], color=LINE, lw=0.8)
    for i, s in enumerate(summary):
        y = 2.32 - i * 0.25
        if i in (4, 7):
            ax.plot([0.05, 6.95], [y + 0.125, y + 0.125], color=LINE, lw=0.8)
        text(ax, 0.05, y + 0.06, s['model'], 7, INK, 'bold')
        text(ax, 0.05, y - 0.068, names[s['input']], 6, GREY)
        for x, r in zip(xs, scripted(s['condition'])):
            badge(ax, x, y, r['majority'] == '1', incorrect=r['majority'] != r['reference'])
        fa, miss = s['agent']['false_alarms'], s['agent']['misses']
        text(ax, fx, y, f'{fa}/157', 7.4, CORAL if fa else GREEN, 'bold', ha='center')
        text(ax, tx, y, f'{3 - miss}/3', 7.4, CORAL if miss else GREEN, 'bold', ha='center')
    text(ax, 0.05, 0.09, '* Pre-authorized in task.  Rule = permission semantics.  '
         'Reason-first = explanation before label.  Majority of 3–5 draws.', 6, GREY)
    save(fig, 'judge-reliability')


# ------------------------------------------------------------ incident cards
ACCENT = {'purple': VIOLET, 'blue': BLUE, 'red': CORAL, 'navy': INK, 'gray': GREY}
FILL = {'purple': 'white', 'blue': 'white', 'red': '#fdf1ee', 'navy': 'white', 'gray': MIST}


def fit_lines(fig, ax, s, width, size):
    """Wrap s to width inches at the given font size, shrinking if needed."""
    renderer = fig.canvas.get_renderer()
    for sz in (size, size - 0.4, size - 0.8, size - 1.2):
        chars = max(8, int(width / (sz * 0.56 / 72)))
        lines = textwrap.wrap(s, chars)
        t = ax.text(0, 0, '\n'.join(lines), fontsize=sz)
        bb = t.get_window_extent(renderer); t.remove()
        if bb.width / fig.dpi <= width:
            return lines, sz
    return lines, sz


def card(fig, ax, x, y, w, h, title, body, accent, title_size=7, body_size=6.2):
    col = ACCENT[accent]
    rbox(ax, x, y, w, h, FILL[accent], col, 0.9, 0.05, 3)
    ax.add_patch(Circle((x + 0.11, y + h - 0.11), 0.033, facecolor=col, edgecolor='none', zorder=4))
    for st, sb in ((0, 0), (0, 0.4), (0.4, 0.4), (0.4, 0.8), (0.8, 0.8), (0.8, 1.2), (1.2, 1.2), (1.2, 1.6), (1.6, 1.6)):
        tl, ts = fit_lines(fig, ax, title, w - 0.28, title_size - st)
        bl, bs = fit_lines(fig, ax, body, w - 0.28, body_size - sb)
        need = 0.05 + len(tl) * ts * 1.12 / 72 + 0.02 + len(bl) * bs * 1.15 / 72 + 0.02
        if need <= h:
            break
    top = y + h - 0.05
    text(ax, x + 0.2, top, '\n'.join(tl), ts, col, 'bold', va='top', linespacing=1.1, zorder=4)
    top -= len(tl) * ts * 1.12 / 72 + 0.02
    text(ax, x + 0.2, top, '\n'.join(bl), bs, INK, va='top', linespacing=1.15, zorder=4)


def step_badge(ax, x, y, n, color, r=0.075):
    ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor='white', lw=0.6, zorder=7))
    text(ax, x, y, str(n), 5.4, 'white', 'bold', ha='center', zorder=8)


def arrow(ax, pts, color, dashed=False, thin=False, z=5):
    lw = 0.8 if thin else 1.5
    ls = (0, (2.2, 1.6)) if dashed else '-'
    for a, b in zip(pts[:-2], pts[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, ls=ls, zorder=z, solid_capstyle='round')
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle='-|>', mutation_scale=7 if thin else 9,
                                 lw=lw, color=color, linestyle=ls, zorder=z, shrinkA=0, shrinkB=0))


def pathways_figure():
    cases = [
        ('A', 'Shared storage: Artifactory (May 8 and 15, 2026)', [
            ('Training samples', 'Task inputs missing; supplied repository credentials remain usable', 'purple'),
            ('Shared repository', 'Notes written and read across samples as stored artifacts', 'red'),
            ('Scope crossed', 'Cross-sample contact outside the intended isolation', 'navy')]),
        ('B', 'File handoff: public hosting (April 14, 2026)', [
            ('Local workbook', 'Handoff to the collaborator fails; deliverable must stay local', 'blue'),
            ('Public file host', 'Workbook made publicly downloadable', 'red'),
            ('Public link returned', 'Uploader verifies download; collaborator receipt not established', 'navy')]),
        ('C', 'Cyber evaluation: real repository (July 2026)', [
            ('Authorized route blocked', 'No permitted route to the challenge solution remains', 'blue'),
            ('Real repository', 'Malicious contribution submitted; false identities seek approval', 'red'),
            ('Maintainer rejects', 'Attempt did not land; runs contained after detection', 'navy')]),
    ]
    fig, ax = canvas(6.9, 3.15)
    cw, ch, gap = 2.12, 0.5, 0.22
    for row, (letter, title, cards) in enumerate(cases):
        ytop = 3.02 - row * 0.95
        text(ax, 0.05, ytop, letter, 7.5, CORAL, 'bold')
        text(ax, 0.2, ytop, title, 7.5, INK, 'bold')
        cy = ytop - 0.13 - ch
        for j, (t, b, acc) in enumerate(cards):
            x = 0.05 + j * (cw + gap)
            card(fig, ax, x, cy, cw, ch, t, b, acc)
            if j < 2:
                x1, x2 = x + cw, x + cw + gap
                col = CORAL if j == 0 else BLUE
                arrow(ax, [(x1 + 0.01, cy + ch / 2), (x2 - 0.01, cy + ch / 2)], col)
                step_badge(ax, (x1 + x2) / 2, cy + ch / 2 + 0.12, j + 1, col, 0.065)
    y = 0.14
    rbox(ax, 0.05, y - 0.07, 0.26, 0.14, FILL['red'], CORAL, 0.9, 0.03, 4)
    text(ax, 0.38, y, 'reported out-of-scope action', 6.3, GREY)
    arrow(ax, [(2.05, y), (2.35, y)], CORAL); text(ax, 2.43, y, 'step into the violation', 6.3, GREY)
    arrow(ax, [(3.65, y), (3.95, y)], BLUE); text(ax, 4.03, y, 'reported consequence', 6.3, GREY)
    save(fig, 'incident-pathways')


def clamped(fig, ax, x, y, s, size, color, weight='normal', lo=0.06, hi=6.84):
    """Centered text whose extent is kept inside the canvas."""
    t = text(ax, x, y, s, size, color, weight, ha='center')
    half = t.get_window_extent(fig.canvas.get_renderer()).width / fig.dpi / 2
    t.set_x(min(max(x, lo + half), hi - half))


# -------------------------------------------- library examples from specs
def render_incident(spec, name):
    W, H = 1680, 945
    sx = 6.9 / W
    # Compress whitespace while retaining card heights and type size for the
    # two full-width examples that share an appendix page.
    from bisect import bisect_right
    source_y = [0, 52, 97, 118, 135, 240, 348, 385, 405, 493, 513,
                515, 611, 625, 662, 696, 719, 752, 775, 798, 845, 882, 901, H]
    print_y = [0, .12, .30, .40, .46, .94, 1.52, 1.71, 1.82, 2.29, 2.40,
               2.43, 2.85, 2.91, 3.04, 3.20, 3.31, 3.43, 3.54, 3.65,
               3.81, 3.97, 4.07, 4.15]
    height = print_y[-1]
    def down(u):
        i = max(0, min(bisect_right(source_y, u) - 1, len(source_y) - 2))
        return print_y[i] + (u - source_y[i]) * (print_y[i + 1] - print_y[i]) / (source_y[i + 1] - source_y[i])
    fig, ax = canvas(6.9, height)
    X = lambda u: u * sx
    Y = lambda u: height - down(u)
    rect = lambda c: (X(c['x']), Y(c['y'] + c['h']), c['w'] * sx, down(c['y'] + c['h']) - down(c['y']))
    text(ax, X(42), Y(52), spec['title'], 9.5, INK, 'bold')
    text(ax, X(42), Y(97), spec['subtitle'].replace('  •  ', ' · '), 6.8, BLUE)
    ax.plot([X(42), X(1638)], [Y(118)] * 2, color=LINE, lw=0.8)
    for p in spec['panels']:
        x, y, w, h = rect(p)
        rbox(ax, x, y, w, h, MIST if p['tint'] == 'gray' else SKY, 'none', 0, 0.08, 1)
        t = text(ax, x + 0.1, y + h - 0.12, p['title'], 8, INK, 'bold')
        if p.get('title2'):
            bb = t.get_window_extent(fig.canvas.get_renderer())
            text(ax, x + 0.1 + bb.width / fig.dpi + 0.05, y + h - 0.12, '|  ' + p['title2'], 8, BLUE, 'bold')
        sl, ss = fit_lines(fig, ax, p['sub'], w - 0.2, 6.2)
        text(ax, x + 0.1, y + h - 0.23, '\n'.join(sl), ss, GREY, va='top', linespacing=1.1)
    boxes = {}
    for c in spec['cards']:
        x, y, w, h = rect(c)
        boxes[c['id']] = (x, y, w, h)
        card(fig, ax, x, y, w, h, c['title'], ' '.join(c['lines']), c['accent'])
    style = {'purple': VIOLET, 'blue': BLUE, 'red': CORAL, 'gray': SLATE, 'navy': INK}

    def anchor(cid, spec_side):
        x, y, w, h = boxes[cid]
        side, _, frac = spec_side.partition(':')
        f = float(frac) if frac else 0.5
        return {'right': (x + w, y + h * (1 - f)), 'left': (x, y + h * (1 - f)),
                'top': (x + w * f, y + h), 'bottom': (x + w * f, y)}[side], side

    for a in spec['arrows']:
        (p0, s0), (p1, s1) = anchor(a['frm'], a['fa']), anchor(a['to'], a['ta'])
        if a.get('via'):
            pts = [p0] + [(X(u), Y(v)) for u, v in a['via']] + [p1]
        elif a.get('mid') is not None:
            m = X(a['mid']); pts = [p0, (m, p0[1]), (m, p1[1]), p1]
        elif s0 in ('left', 'right') and s1 in ('left', 'right') and abs(p0[1] - p1[1]) > 0.02:
            m = (p0[0] + p1[0]) / 2; pts = [p0, (m, p0[1]), (m, p1[1]), p1]
        else:
            pts = [p0, p1]
        col = style[a['style']]
        arrow(ax, pts, col, a.get('dashed', False), a.get('thin', False))
        if a.get('num') is not None:
            if a.get('badge_at'):
                bx, by = X(a['badge_at'][0]), Y(a['badge_at'][1])
            else:
                mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
                if len(pts) == 2:
                    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                bx, by = mx + a.get('badge_dx', 0) * sx, my - a.get('badge_dy', 0) * sx
            step_badge(ax, bx, by, a['num'], col, 0.07)
        if a.get('label'):
            lx, ly = X(a['label_at'][0]), Y(a['label_at'][1])
            if spec['n'] == 20 and a['label'] == '2 actions':
                lx = X(501)  # Keep this annotation in the gutter between cards.
            text(ax, lx, ly, a['label'], 5.8, GREY, ha='center',
                 bbox=dict(facecolor=MIST, edgecolor='none', pad=1.2))
    # timeline
    tl = spec['timeline']; ty = Y(662)
    txs = [X(115 + i * (1588 - 115) / max(1, len(tl) - 1)) for i in range(len(tl))]
    dotcol = {'navy': INK, 'purple': VIOLET}
    for i, (tx, e) in enumerate(zip(txs, tl)):
        col = dotcol.get(e.get('color'), BLUE)
        if i:
            ax.plot([txs[i - 1], tx], [ty, ty], color=VIOLET if e.get('color') == 'purple' else BLUE, lw=1.2, zorder=2)
        ax.add_patch(Circle((tx, ty), 0.045, facecolor=col, edgecolor='none', zorder=3))
        clamped(fig, ax, tx, Y(696), e['date'], 6.3, col, 'bold')
        clamped(fig, ax, tx, Y(719), e['label'], 6, INK)
    # evidence, legend, sources
    rbox(ax, X(42), Y(798), X(1638) - X(42), down(798) - down(752), MIST, 'none', 0, 0.04, 1)
    text(ax, X(60), Y(775), ' '.join(spec['evidence']), 6.2, INK)
    lx = X(42); ly = Y(845)
    for item in spec['legend']:
        st = item['style']
        if st.endswith('-line'):
            ax.plot([lx, lx + 0.3], [ly, ly], color=style[st[:-5]], lw=1.3)
        else:
            arrow(ax, [(lx, ly), (lx + 0.3, ly)], style[st], st == 'purple', st in ('purple', 'gray'))
        t = text(ax, lx + 0.38, ly, item['text'], 6.2, INK)
        lx += 0.38 + t.get_window_extent(fig.canvas.get_renderer()).width / fig.dpi + 0.3
    for i, s in enumerate(spec['sources']):
        text(ax, X(42), Y(882 + i * 19), s, 5.8, GREY)
    save(fig, name)


def featured_workbook():
    """Detailed library-style view with source-supported outcomes."""
    spec = json.loads((ROOT / 'data/incident_specs/incident-15.spec.json').read_text())
    assert spec['n'] == 15
    spec['panels'][1]['title2'] = 'Verified outcome'
    for item in spec['cards']:
        if item['id'] == 'dl':
            item['title'] = 'Download verified'
            item['lines'] = ['Agent A verifies download from the public host [1]']
        elif item['id'] == 'note':
            item['title'] = 'Decision-policy choices (proposed)'
            item['lines'] = ['Recover locally; probe feasibility; request permission or resources; stop if no authorized solution remains.']
    # The primary report confirms uploader verification, not receipt by Agent B.
    spec['arrows'] = [a for a in spec['arrows'] if not (a['frm'] == 'dl' and a['to'] == 'a2')]
    spec['evidence'] = ['Evidence: the report confirms uploader-verified download; collaborator download is not established. [1]']
    render_incident(spec, 'featured-workbook')


if __name__ == '__main__':
    judge_figure()
    pathways_figure()
    featured_workbook()
    for n in (14, 20):
        spec = json.loads((ROOT / f'data/incident_specs/incident-{n:02d}.spec.json').read_text())
        render_incident(spec, f'incident-example-{n:02d}')
    print('Wrote five vector PDF figures.')
