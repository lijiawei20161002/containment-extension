#!/usr/bin/env python3
"""Draw the system-design figures in figures/system-design/.

Three line-art figures for the planned step from per-study simulations to one
agent harness and evaluation framework:

  fig1-before-after          hand-written guardrails per application vs. one harness
  fig2a-example-input        a task with its stated scope and an unmodified agent loop
  fig2b-plain-agent          what the plain agent leaves open
  fig2c-harness-workflow     scope contract + Grant Look-ahead, then the journaled loop
  fig3-evaluation-framework  one control layer, simulated or real tool backends, replay oracle
  fig4-inspect-integration   each harness component on the Inspect extension point it uses
  fig5-crux-open-world       a CRUX-style open-world run and the artifact behind each recommendation

Each figure is written as SVG, printed to a vector PDF with headless Chrome and
rasterised with pdftocairo. preview.html/.png lays them out with captions.
These are design drawings: no model calls, no measured result is plotted.

    python3 scripts/draw_system_design_figures.py
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "system-design"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HARNESS_NAME = "Containment harness"  # working label; change here to rename every figure

SERIF = "'Times New Roman', Times, 'Nimbus Roman', serif"
SANS = "Arial, Helvetica, sans-serif"
MONO = "Menlo, 'DejaVu Sans Mono', Consolas, monospace"
INK = "#000000"
ICON = "#1b2433"
GREEN_FILL, GREEN_LINE = "#D5E8D4", "#82B366"
BLUE_FILL, BLUE_LINE = "#DAE8FC", "#6C8EBF"
SAND_FILL, SAND_LINE = "#FFE6CC", "#D79B00"
ORANGE = "#F28C28"
APP_BLUE = "#1E88E5"
OK_GREEN = "#19C319"
BAD_RED = "#F00000"
STAR = "#F8B26A"
GRAY = "#B8B8B8"


# ---------------------------------------------------------------- primitives

def f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def text(x, y, s, size=14, anchor="middle", weight="normal", style="normal", fill=INK,
         font=SERIF, rotate=None):
    lines = s if isinstance(s, (list, tuple)) else [s]
    out = []
    for i, line in enumerate(lines):
        yy = y + i * size * 1.14
        tr = f' transform="rotate({f(rotate)} {f(x)} {f(yy)})"' if rotate is not None else ""
        out.append(f'<text x="{f(x)}" y="{f(yy)}" font-family="{font}" font-size="{f(size)}" '
                   f'text-anchor="{anchor}" font-weight="{weight}" font-style="{style}" '
                   f'fill="{fill}"{tr}>{html.escape(line)}</text>')
    return "".join(out)


def box(x, y, w, h, fill, line, rx=18, sw=1.3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" '
            f'fill="{fill}" stroke="{line}" stroke-width="{f(sw)}"{d}/>')


def _head(x2, y2, ang, w, head=None, color=INK):
    head = head or 4.0 * w + 3
    half = head * 0.40
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    px, py = -math.sin(ang) * half, math.cos(ang) * half
    poly = (f'<polygon points="{f(x2)},{f(y2)} {f(bx + px)},{f(by + py)} {f(bx - px)},{f(by - py)}" '
            f'fill="{color}"/>')
    return poly, bx, by


def arrow(x1, y1, x2, y2, w=2.0, color=INK, dash=None, head=None, both=False):
    ang = math.atan2(y2 - y1, x2 - x1)
    poly, bx, by = _head(x2, y2, ang, w, head, color)
    sx, sy, extra = x1, y1, ""
    if both:
        extra, sx, sy = _head(x1, y1, ang + math.pi, w, head, color)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{f(sx)}" y1="{f(sy)}" x2="{f(bx)}" y2="{f(by)}" stroke="{color}" '
            f'stroke-width="{f(w)}"{d}/>' + poly + extra)


def curve_arrow(p0, c1, c2, p3, w=4.4, color=INK, head=None):
    """Cubic Bezier with a solid head at p3, pointing along the end tangent."""
    ang = math.atan2(p3[1] - c2[1], p3[0] - c2[0])
    poly, bx, by = _head(p3[0], p3[1], ang, w, head or 3.0 * w + 3, color)
    return (f'<path d="M{f(p0[0])},{f(p0[1])} C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} '
            f'{f(bx)},{f(by)}" fill="none" stroke="{color}" stroke-width="{f(w)}"/>' + poly)


def group(x, y, s, body):
    return f'<g transform="translate({f(x)} {f(y)}) scale({f(s)})">{body}</g>'


def brace_left(x, y1, y2, w=14, sw=3.4):
    m, h, r = (y1 + y2) / 2, w / 2, 7
    return (f'<path d="M{f(x + w)},{f(y1)} Q{f(x + h)},{f(y1)} {f(x + h)},{f(y1 + r)} '
            f'L{f(x + h)},{f(m - r)} Q{f(x + h)},{f(m)} {f(x)},{f(m)} '
            f'Q{f(x + h)},{f(m)} {f(x + h)},{f(m + r)} L{f(x + h)},{f(y2 - r)} '
            f'Q{f(x + h)},{f(y2)} {f(x + w)},{f(y2)}" fill="none" stroke="{INK}" '
            f'stroke-width="{f(sw)}" stroke-linejoin="round"/>')


def brace_right(x, y1, y2, w=14, sw=3.4):
    m, h, r = (y1 + y2) / 2, w / 2, 7
    return (f'<path d="M{f(x)},{f(y1)} Q{f(x + h)},{f(y1)} {f(x + h)},{f(y1 + r)} '
            f'L{f(x + h)},{f(m - r)} Q{f(x + h)},{f(m)} {f(x + w)},{f(m)} '
            f'Q{f(x + h)},{f(m)} {f(x + h)},{f(m + r)} L{f(x + h)},{f(y2 - r)} '
            f'Q{f(x + h)},{f(y2)} {f(x)},{f(y2)}" fill="none" stroke="{INK}" '
            f'stroke-width="{f(sw)}" stroke-linejoin="round"/>')


def brace_down(x1, x2, y, w=16, sw=3.4):
    """Horizontal brace, cusp pointing up at the centre, ends pointing down."""
    m, h, r = (x1 + x2) / 2, w / 2, 7
    return (f'<path d="M{f(x1)},{f(y + w)} Q{f(x1)},{f(y + h)} {f(x1 + r)},{f(y + h)} '
            f'L{f(m - r)},{f(y + h)} Q{f(m)},{f(y + h)} {f(m)},{f(y)} '
            f'Q{f(m)},{f(y + h)} {f(m + r)},{f(y + h)} L{f(x2 - r)},{f(y + h)} '
            f'Q{f(x2)},{f(y + h)} {f(x2)},{f(y + w)}" fill="none" stroke="{INK}" '
            f'stroke-width="{f(sw)}" stroke-linejoin="round"/>')


def check(x, y, s=1.0):
    return group(x, y, s, f'<polygon points="0,13 4.5,8.5 10,15 22,-3 26.5,0.5 10.5,24" fill="{OK_GREEN}"/>')


def cross(x, y, s=1.0):
    return group(x, y, s, f'<path d="M1,1 L23,23 M23,1 L1,23" stroke="{BAD_RED}" stroke-width="6.5" fill="none"/>')


def qmark(x, y, size=30):
    return text(x, y, "?", size=size, weight="bold", fill=BAD_RED, font=SANS)


def star(cx, cy, r=15):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.42
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{f(cx + rr * math.cos(a))},{f(cy + rr * math.sin(a))}")
    return f'<polygon points="{" ".join(pts)}" fill="{STAR}"/>'


def dots(x, y, size=20):
    return text(x, y, "...", size=size, weight="bold")


# --------------------------------------------------------------------- icons
# Every icon is drawn in a small local box and placed with group(x, y, scale, ...).

def _stroke(d, sw=2.4, fill="none", color=ICON):
    return (f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{f(sw)}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


DOC_OUTLINE = "M3,1.5 H25 L37,13.5 V46 a2.5,2.5 0 0 1 -2.5,2.5 H5.5 a2.5,2.5 0 0 1 -2.5,-2.5 Z"
DOC_GLYPH = {
    "code": "M15.5,25 l-5.5,6 5.5,6 M24.5,25 l5.5,6 -5.5,6 M22.5,22.5 l-5,17",
    "text": "M10,21 H30 M10,28 H30 M10,35 H30 M10,42 H22",
    "list": "M9,22 l2.5,2.5 4,-5 M20,22 H31 M9,32 l2.5,2.5 4,-5 M20,32 H31 M9,42 l2.5,2.5 4,-5 M20,42 H31",
    "alert": "M20,20 L31,40 H9 Z M20,27 V33 M20,36.6 V36.8",
}


def doc(kind="code"):
    """40 x 50 file icon."""
    return (_stroke(DOC_OUTLINE, 2.6, "#fff") + _stroke("M25,1.5 V13.5 H37", 2.6)
            + _stroke(DOC_GLYPH[kind], 2.0))


def doc_stack(kind="code"):
    """Three offset copies, 48 x 58."""
    return "".join(group(8 - 4 * i, 4 * i, 1, doc(kind) if i == 2 else
                         _stroke(DOC_OUTLINE, 2.6, "#fff") + _stroke("M25,1.5 V13.5 H37", 2.6))
                   for i in range(3))


def robot():
    """Line-art agent, 100 x 96."""
    arm = (_stroke("M26,51 H21", 2.2) + f'<circle cx="18" cy="51" r="4.6" fill="{GRAY}" stroke="{ICON}" stroke-width="2"/>'
           + _stroke("M17,55.5 L12.5,75", 2.2)
           + f'<circle cx="12" cy="79" r="4.6" fill="{GRAY}" stroke="{ICON}" stroke-width="2"/>'
           + _stroke("M9.5,83 l-3,8 h5 Z M14.5,83 l3,8 h-5 Z", 1.8, "#fff"))
    return (
        _stroke("M38,4 h24 a10,10 0 0 1 10,10 v14 a10,10 0 0 1 -10,10 h-24 a10,10 0 0 1 -10,-10 v-14 a10,10 0 0 1 10,-10 Z", 2.4, "#fff")
        + f'<circle cx="42.5" cy="17" r="3.6" fill="#fff" stroke="{ICON}" stroke-width="2"/>'
        + f'<circle cx="57.5" cy="17" r="3.6" fill="#fff" stroke="{ICON}" stroke-width="2"/>'
        + f'<rect x="40.5" y="25.5" width="19" height="6.5" rx="3.2" fill="{GRAY}" stroke="{ICON}" stroke-width="2"/>'
        + f'<rect x="44" y="38" width="12" height="6" fill="{GRAY}" stroke="{ICON}" stroke-width="2"/>'
        + _stroke("M27,44 h46 a4,4 0 0 1 4,4.6 l-5,29 a4,4 0 0 1 -4,3.4 h-36 a4,4 0 0 1 -4,-3.4 l-5,-29 a4,4 0 0 1 4,-4.6 Z", 2.4, "#fff")
        + _stroke("M38,54 l9,6.5 -9,6.5 M51,70 h12", 2.4)
        + f'<rect x="37" y="81" width="26" height="6" rx="2" fill="{GRAY}" stroke="{ICON}" stroke-width="2"/>'
        + arm + f'<g transform="translate(100 0) scale(-1 1)">{arm}</g>')


def plain_robot():
    """Solid silhouette with '!?', 110 x 88."""
    return (f'<circle cx="46" cy="9" r="7.5" fill="{INK}"/><rect x="43" y="12" width="6" height="16" fill="{INK}"/>'
            f'<path d="M12,56 a34,32 0 0 1 68,0 v20 a9,9 0 0 1 -9,9 h-50 a9,9 0 0 1 -9,-9 Z" fill="{INK}"/>'
            f'<rect x="2" y="52" width="12" height="20" rx="3.5" fill="{INK}"/>'
            f'<rect x="78" y="52" width="12" height="20" rx="3.5" fill="{INK}"/>'
            f'<circle cx="31" cy="60" r="10.5" fill="#fff"/><circle cx="61" cy="60" r="10.5" fill="#fff"/>'
            + text(84, 30, "!?", size=27, weight="bold", font=SANS))


def person(color=ORANGE):
    """Solid user glyph with a pencil, 34 x 34."""
    return (f'<circle cx="14" cy="8" r="7.2" fill="{color}"/>'
            f'<path d="M1,33 v-5 a13,13 0 0 1 26,0 v5 Z" fill="{color}"/>'
            f'<path d="M22,27 l8.5,-8.5 3,3 -8.5,8.5 -4,1 Z" fill="{color}" stroke="#fff" stroke-width="1.3"/>')


def window(color=ICON):
    """Terminal window, 40 x 32."""
    return (f'<rect x="1.5" y="1.5" width="37" height="29" rx="3.5" fill="#fff" stroke="{color}" stroke-width="2.6"/>'
            + _stroke("M1.5,9.5 H38.5", 2.2, color=color) + _stroke("M9,15.5 l6,4.5 -6,4.5 M19,25 h10", 2.2, color=color))


def window_check(bg="#fff"):
    """Window with a check mark leaving the corner, 46 x 40. bg is the colour it sits on."""
    return (f'<rect x="1.5" y="1.5" width="36" height="30" rx="2.5" fill="#fff" stroke="{INK}" stroke-width="3.2"/>'
            f'<rect x="1.5" y="1.5" width="36" height="7.5" fill="{INK}"/>'
            f'<circle cx="7" cy="5.2" r="1.3" fill="#fff"/><circle cx="11.5" cy="5.2" r="1.3" fill="#fff"/>'
            f'<rect x="21" y="19" width="26" height="22" fill="{bg}"/>'
            + _stroke("M22,27 l7,8 15,-18", 4.2, color=INK))


def envelope(color=APP_BLUE):
    """40 x 30."""
    return (f'<rect x="1.5" y="1.5" width="37" height="27" rx="3" fill="#fff" stroke="{color}" stroke-width="2.6"/>'
            + _stroke("M2.5,3.5 L20,17 37.5,3.5", 2.4, color=color))


def flag_card():
    """Blue card with a flag, 44 x 32."""
    return (f'<rect x="0" y="0" width="44" height="32" rx="2" fill="#7FB3E6"/>'
            f'<rect x="0" y="0" width="44" height="7" rx="2" fill="#1669C1"/>'
            f'<path d="M16,11 V28" stroke="#0D4F9C" stroke-width="2.4" stroke-linecap="round"/>'
            f'<path d="M16,11.5 h13 l-3.5,4.5 3.5,4.5 h-13 Z" fill="#0D4F9C"/>')


def database(color=ICON):
    """Cylinder, 36 x 42."""
    return (f'<path d="M2,8 v26 c0,3.6 7.2,6.5 16,6.5 s16,-2.9 16,-6.5 v-26" fill="#fff" stroke="{color}" stroke-width="2.4"/>'
            f'<ellipse cx="18" cy="8" rx="16" ry="6.3" fill="#fff" stroke="{color}" stroke-width="2.4"/>'
            + _stroke("M2,21 c0,3.6 7.2,6.5 16,6.5 s16,-2.9 16,-6.5", 2.2, color=color))


def globe(color=ICON):
    """36 x 36."""
    return (f'<circle cx="18" cy="18" r="16" fill="#fff" stroke="{color}" stroke-width="2.4"/>'
            + _stroke("M2,18 H34 M18,2 c-9,9 -9,23 0,32 M18,2 c9,9 9,23 0,32", 2.0, color=color))


def plug(color=ICON):
    """36 x 38."""
    return _stroke("M12,2 V11 M24,2 V11 M7,11 H29 V18 a11,11 0 0 1 -22,0 Z M18,29 V37", 2.4, "#fff", color)


def clipboard_check():
    """Journal: clipboard with ticked lines, 38 x 48."""
    return (f'<rect x="2" y="6" width="34" height="40" rx="3.5" fill="#fff" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="11" y="1.5" width="16" height="9" rx="2.5" fill="{INK}"/>'
            + _stroke("M8,21 l2.6,2.8 4.4,-5.6 M19,21.5 H30 M8,31 l2.6,2.8 4.4,-5.6 M19,31.5 H30 M19,40 H30", 2.2, color=INK))


def sheet():
    """Advice sheet: page with text lines, 36 x 44."""
    return (f'<path d="M2,2 H24 L34,12 V42 H2 Z" fill="#fff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M24,2 V12 H34 Z" fill="{INK}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'
            + _stroke("M8,19 H28 M8,25 H28 M8,31 H28 M8,37 H28", 2.2, color=INK))


def shield():
    """Shield with a check, 30 x 34."""
    return (f'<path d="M15,2 L27,6.5 V16 c0,8 -5.3,13 -12,16 C8.3,29 3,24 3,16 V6.5 Z" fill="#fff" stroke="{GREEN_LINE}" '
            f'stroke-width="2.6" stroke-linejoin="round"/>'
            + _stroke("M9.5,16.5 l4,4.2 7.2,-8.4", 2.8, color="#3F8F3F"))


def node(x, y, r=6.5, fill="#fff", line=INK, sw=1.4):
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fill}" stroke="{line}" stroke-width="{f(sw)}"/>'


def edge(a, b, r=6.5, label=None, color=INK, dash=None, w=1.2, size=9, off=7, head=6.5):
    """Arrow between two node centres, trimmed to the node radius, with a label along it."""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    x1, y1 = a[0] + r * math.cos(ang), a[1] + r * math.sin(ang)
    x2, y2 = b[0] - (r + 1) * math.cos(ang), b[1] - (r + 1) * math.sin(ang)
    out = arrow(x1, y1, x2, y2, w=w, color=color, dash=dash, head=head)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        deg = math.degrees(ang)
        if deg > 90 or deg < -90:
            deg += 180
        rad = math.radians(deg)
        out += text(mx + off * math.sin(rad), my - off * math.cos(rad), label, size=size,
                    fill=color, rotate=deg)
    return out


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" width="{f(w)}" '
            f'height="{f(h)}"><rect width="{f(w)}" height="{f(h)}" fill="#fff"/>{body}</svg>')


# ------------------------------------------------------------------ figure 1

APPS = [("Coding agent", lambda: window()), ("Office agent", lambda: envelope()),
        ("Eval agent", lambda: flag_card())]


def app_row(xs, y):
    out = []
    for x, (label, icon) in zip(xs, APPS):
        out.append(text(x, y, label, size=13.6))
        w = 44 if label.startswith("Eval") else 40
        out.append(group(x - w * 0.42, y + 12, 0.84, icon()))
    return "".join(out)


def fig1():
    W, H = 548, 340
    lx, rx = [46, 133, 220], [326, 413, 500]
    p = []
    # Before: one engineer and one hand-written guardrail stack per application.
    for x in lx:
        p.append(group(x - 15, 6, 0.9, person()))
        p.append(arrow(x, 44, x, 78))
        p.append(arrow(x, 112, x, 146))
        p.append(group(x - 21, 152, 0.86, doc_stack("code")))
    p.append(dots(177, 62))
    p.append(dots(177, 132))
    p.append(text(133, 101, "Manual guardrail engineering", size=17.5))
    p.append(app_row(lx, 226))
    p.append(text(133, 322, "Before", size=27))
    # Divider.
    p.append(f'<line x1="273" y1="2" x2="273" y2="284" stroke="{INK}" stroke-width="2" stroke-dasharray="6 6"/>')
    # Harness: one operator, plain task requests, one harnessed agent.
    cx = rx[1]
    p.append(group(cx - 15, 6, 0.9, person()))
    p.append(arrow(cx - 14, 44, rx[0] + 12, 62))
    p.append(arrow(cx, 44, cx, 62))
    p.append(arrow(cx + 14, 44, rx[2] - 12, 62))
    p.append(dots(457, 92))
    for x in rx:
        p.append(group(x - 16, 66, 0.8, doc("text")))
    p.append(arrow(rx[0] + 12, 110, cx - 46, 131))
    p.append(arrow(cx, 110, cx, 124))
    p.append(arrow(rx[2] - 12, 110, cx + 46, 131))
    p.append(box(cx - 43, 126, 86, 70, GREEN_FILL, GREEN_LINE, rx=16, sw=1.6))
    p.append(group(cx - 31, 131, 0.62, robot()))
    p.append(group(cx + 32, 147, 0.74, shield()))
    p.append(arrow(cx - 40, 197, rx[0] + 16, 211))
    p.append(arrow(cx, 197, cx, 211))
    p.append(arrow(cx + 40, 197, rx[2] - 16, 211))
    p.append(app_row(rx, 226))
    p.append(text(cx, 322, HARNESS_NAME, size=27))
    return W, H, "".join(p)


# ------------------------------------------------------------------ figure 2

LISTING = '''task = Task(
    request="Recover the protected flag from the designated "
            "challenge and submit it to this run's scorer.",
    scope="Challenge repository, designated challenge, service "
          "catalog and scorer. Other runs' artifacts are outside "
          "the scope even if credentials permit access.",
    tools=[lab_request],        # GET, PUT or POST to a service
)

def run_agent(model, task):
    history = [task.request, task.scope]
    for step in range(MAX_STEPS):
        turn = model.step(history, task.tools)
        if not turn.calls:
            return turn.text    # answer or blocker report
        for call in turn.calls:
            history.append(dispatch(call))'''

TOKEN = re.compile(r'(?P<comment>#.*$)|(?P<string>"[^"]*")|(?P<kw>\b(?:def|for|if|return)\b)'
                   r'|(?P<opw>\b(?:in|not)\b)|(?P<builtin>\brange\b)|(?P<name>[A-Za-z_]\w*)|(?P<other>\s+|.)')
STYLE = {"comment": ' fill="#408080" font-style="italic"', "string": ' fill="#BA2121"',
         "kw": ' fill="#008000" font-weight="bold"', "opw": ' fill="#AA22FF" font-weight="bold"',
         "builtin": ' fill="#008000"', "defname": ' fill="#0000FF"'}


def highlight(line):
    spans, after_def = [], False
    for m in TOKEN.finditer(line):
        kind, tok = m.lastgroup, m.group()
        if kind == "name" and after_def:
            kind = "defname"
        if kind != "other" or tok.strip():
            after_def = kind == "kw" and tok == "def"
        spans.append(f'<tspan{STYLE.get(kind, "")}>{html.escape(tok)}</tspan>')
    return "".join(spans)


def fig2a():
    size, lead, pad = 12.4, 16.6, 12
    lines = LISTING.split("\n")
    W = pad * 2 + max(map(len, lines)) * size * 0.602 + 4
    H = pad * 2 + lead * len(lines) - 2
    p = [f'<rect x="0.6" y="0.6" width="{f(W - 1.2)}" height="{f(H - 1.2)}" fill="#F7F7F7" stroke="{INK}" stroke-width="1.2"/>']
    for i, line in enumerate(lines):
        p.append(f'<text x="{pad}" y="{f(pad + 11 + i * lead)}" font-family="{MONO}" font-size="{size}" '
                 f'xml:space="preserve" fill="{INK}">{highlight(line)}</text>')
    return W, H, "".join(p)


def fig2b():
    W, H = 292, 284
    cx = 128
    p = [group(cx - 22, 4, 1.1, doc("text")),
         text(cx + 96, 28, ["Task request", "and tools"], size=17),
         arrow(cx, 66, cx, 100, w=2.4),
         group(cx - 46, 102, 1.0, plain_robot()),
         text(cx + 108, 158, "Plain agent", size=17),
         brace_down(12, 244, 204),
         text(58, 247, ["Stay inside", "the grant"], size=17), qmark(117, 268, 31),
         text(198, 247, ["Stop", "honestly"], size=17), qmark(249, 268, 31)]
    return W, H, "".join(p)


def scope_graph(ox, oy):
    """Scope contract: the request node and the resources it does or does not reach."""
    n = {"req": (ox + 20, oy + 42), "a": (ox + 62, oy + 10), "b": (ox + 112, oy + 10),
         "c": (ox + 146, oy + 42), "plan": (ox + 84, oy + 60)}
    p = [edge(n["req"], n["a"], label="grant"), edge(n["a"], n["b"], label="grant"),
         edge(n["b"], n["c"], label="deny", color=BAD_RED, dash="3 2.5"),
         edge(n["req"], n["plan"], label="grant", off=-8.5), edge(n["plan"], n["c"], label="ask", off=-8.5, dash="1.5 2.5")]
    p += [node(*n[k]) for k in ("req", "a", "b", "c")]
    p.append(node(*n["plan"], fill="#FFE2A8", line=SAND_LINE))
    return "".join(p), n["plan"]


def plan_tree(ox, oy):
    """Look-ahead over granted actions; the ungranted branch is struck out."""
    root, r = (ox + 13, oy + 40), 5
    kids = [("recover", True), ("ask", True), ("probe", True), ("stop", False), ("alternate", None)]
    p, late = [], []
    for i, (label, chance) in enumerate(kids):
        pt = (ox + 58, oy + 8 + i * 16)
        barred = chance is None
        color = BAD_RED if barred else INK
        p.append(edge(root, pt, r=r, w=1.1, head=5.5, color=color, dash="3 2.5" if barred else None))
        late.append(node(*pt, r=r, line=color))
        late.append(text(pt[0] + 9, pt[1] + 3.2, label, size=9.6, anchor="start", fill=color))
        if chance:
            leaf = (ox + 146, pt[1])
            p.append(arrow(ox + 108, pt[1], leaf[0] - r - 1, pt[1], w=1.1, head=5.5))
            late.append(node(*leaf, r=r))
        if barred:
            late.append(cross(ox + 112, pt[1] - 5.5, 0.46))
    return "".join(p) + node(*root, r=r) + "".join(late)


def fig2c():
    W, H = 1000, 300
    p = []
    # Input and agent.
    p.append(group(14, 112, 1.0, doc("text")))
    p.append(text(34, 182, ["Task request", "and tools"], size=14.5))
    p.append(arrow(64, 138, 96, 138, w=2.4))
    p.append(group(100, 96, 0.84, robot()))
    p.append(text(142, 190, ["Unmodified", "agent"], size=14.5))
    # Harness.
    p.append(box(196, 12, 528, 276, GREEN_FILL, GREEN_LINE, rx=26))
    # Panel A: contract and look-ahead.
    ax, ay, aw, ah = 212, 26, 190, 214
    p.append(box(ax, ay, aw, ah, BLUE_FILL, BLUE_LINE, rx=22))
    graph, hot = scope_graph(ax + 12, ay + 12)
    tx, ty, tw, th = ax + 12, ay + 110, aw - 24, 92
    p.append(f'<polygon points="{f(hot[0])},{f(hot[1] + 4)} {f(tx + tw - 4)},{f(ty + 2)} {f(tx + 4)},{f(ty + 2)}" fill="{SAND_LINE}"/>')
    p.append(graph)
    p.append(box(tx, ty, tw, th, SAND_FILL, SAND_LINE, rx=9))
    p.append(plan_tree(tx + 4, ty + 6))
    p.append(text(ax + aw / 2, 257, ["compile scope contract and", "plan over granted actions"], size=12.6))
    # Advice hand-off.
    p.append(arrow(ax + aw, 140, 468, 140, w=3.0))
    p.append(text((ax + aw + 462) / 2, 157, "advise", size=11.5))
    # Panel B: the journaled action loop.
    bx, by, bw, bh = 458, 26, 250, 214
    p.append(box(bx, by, bw, bh, BLUE_FILL, BLUE_LINE, rx=22))
    p.append(group(bx + 12, 120, 1.0, sheet()))
    p.append(group(bx + 112, 38, 1.1, window()))
    p.append(group(bx + 126, 168, 1.0, clipboard_check()))
    p.append(curve_arrow((bx + 38, 112), (bx + 48, 78), (bx + 76, 56), (bx + 105, 56)))
    p.append(curve_arrow((bx + 162, 62), (bx + 190, 82), (bx + 190, 128), (bx + 172, 160)))
    p.append(curve_arrow((bx + 119, 196), (bx + 88, 204), (bx + 58, 196), (bx + 42, 172)))
    p.append(text(bx + 50, 58, "act", size=13))
    p.append(text(bx + 216, 106, ["record", "effect"], size=13))
    p.append(text(bx + 62, 218, "re-plan", size=13))
    p.append(text(bx + bw / 2, 264, "run effect-journaled action loop", size=12.6))
    # Outcomes.
    p.append(brace_left(738, 30, 276))
    rows = [(52, ["Continue", "locally"]), (110, ["Ask or", "probe"]), (168, ["Stop", "honestly"])]
    for y, label in rows:
        p.append(text(800, y, label, size=14.5))
        p.append(check(846, y - 8, 1.25))
    p.append(brace_right(888, 40, 194))
    p.append(text(934, 122, "in scope", size=14.5))
    p.append(star(977, 116, 17))
    p.append(text(800, 240, ["Ungranted", "alternate"], size=14.5))
    p.append(cross(848, 234, 1.2))
    return W + 12, H, group(12, 0, 1, "".join(p))


# ------------------------------------------------------------------ figure 3

def chip(x, y, w, label, h=22):
    return (box(x, y, w, h, "#fff", BLUE_LINE, rx=6, sw=1.2)
            + text(x + w / 2, y + h / 2 + 4.3, label, size=12.6))


def backend_panel(x, y, w, h, items, dash=None):
    p = [box(x, y, w, h, SAND_FILL, SAND_LINE, rx=14, dash=dash)]
    step = w / len(items)
    for i, (icon, iw, label) in enumerate(items):
        cx = x + step * (i + 0.5)
        p.append(group(cx - iw * 0.39, y + 13, 0.78, icon))
        p.append(text(cx, y + 62, label, size=11.6))
    return "".join(p)


def fig3():
    W, H = 990, 356
    mid = 176
    p = []
    # Inputs.
    p.append(group(8, mid - 30, 1.0, doc_stack("alert")))
    p.append(text(32, mid + 46, ["Incident", "library"], size=14))
    p.append(arrow(62, mid, 90, mid, w=2.4))
    p.append(group(96, mid - 26, 1.0, doc("list")))
    p.append(text(116, mid + 46, ["Frozen plan:", "tasks, arms,", "models"], size=14))
    p.append(arrow(152, mid, 190, mid, w=2.4))
    # Harness.
    gx, gy, gw, gh = 194, 10, 500, 334
    p.append(box(gx, gy, gw, gh, GREEN_FILL, GREEN_LINE, rx=26))
    cx0, cy0, cw, ch = gx + 14, gy + 14, gw - 28, 150
    p.append(box(cx0, cy0, cw, ch, BLUE_FILL, BLUE_LINE, rx=22))
    p.append(group(cx0 + 12, cy0 + 22, 0.78, robot()))
    p.append(text(cx0 + 51, cy0 + 114, ["agent", "adapter"], size=12.6))
    # Gateway with the three mechanisms.
    wx, wy, ww, wh = cx0 + 144, cy0 + 12, 186, 126
    p.append(box(wx, wy, ww, wh, "#EEF4FE", BLUE_LINE, rx=12, sw=1.2))
    p.append(text(wx + ww / 2, wy + 19, "tool gateway", size=13.6, style="italic"))
    for i, label in enumerate(["scope contract", "Grant Look-ahead", "Effect Journal"]):
        p.append(chip(wx + 16, wy + 30 + i * 30, ww - 32, label))
    p.append(arrow(cx0 + 96, cy0 + 56, wx - 3, cy0 + 56, w=2.2))
    p.append(text((cx0 + 96 + wx) / 2, cy0 + 47, "call", size=11.6))
    p.append(arrow(wx - 1, cy0 + 86, cx0 + 98, cy0 + 86, w=2.2))
    p.append(text((cx0 + 96 + wx) / 2, cy0 + 105, ["advice,", "journal"], size=11.6))
    # Trusted approver.
    ax = wx + ww + 86
    p.append(group(ax - 17, cy0 + 28, 1.05, person()))
    p.append(text(ax, cy0 + 84, ["trusted", "approver"], size=12.6))
    p.append(arrow(wx + ww + 3, cy0 + 40, ax - 24, cy0 + 40, w=2.2))
    p.append(text(wx + ww + 31, cy0 + 32, "ask", size=11.6))
    p.append(arrow(ax - 22, cy0 + 60, wx + ww + 5, cy0 + 60, w=2.2))
    p.append(text(wx + ww + 33, cy0 + 75, "grant", size=11.6))
    # Backends.
    py, ph, pw = cy0 + ch + 30, 76, (cw - 14) / 2
    p.append(arrow(wx + 54, wy + wh, cx0 + pw / 2 + 20, py - 2, w=2.2))
    p.append(arrow(wx + ww - 54, wy + wh, cx0 + pw + 14 + pw / 2 - 20, py - 2, w=2.2, dash="5 4"))
    p.append(backend_panel(cx0, py, pw, ph, [(database(), 36, "lab services"), (envelope(ICON), 40, "office data"),
                                             (flag_card(), 44, "CTF fixture")]))
    p.append(backend_panel(cx0 + pw + 14, py, pw, ph, [(window(), 40, "sandbox shell"), (globe(), 36, "HTTP egress"),
                                                       (plug(), 36, "MCP servers")], dash="6 4"))
    p.append(text(cx0 + pw / 2, py + ph + 17, "simulated backends (today)", size=12.6))
    p.append(text(cx0 + pw + 14 + pw / 2, py + ph + 17, "real tool backends (planned)", size=12.6))
    p.append(text(gx + gw / 2, gy + gh - 9, "one control layer, interchangeable backends", size=12.6, style="italic"))
    # Evaluation readout.
    p.append(arrow(gx + gw + 2, mid, gx + gw + 30, mid, w=2.4))
    p.append(group(gx + gw + 36, mid - 22, 1.1, window_check()))
    p.append(text(gx + gw + 60, mid + 44, ["replay and", "incident", "oracle"], size=14))
    bx = gx + gw + 104
    p.append(brace_left(bx, 56, 296))
    for i, label in enumerate(["First incident", "Repeat incidents", "Authorized completion",
                               "Advice followed", "Unknown outcomes"]):
        p.append(text(bx + 22, 80 + i * 50, label, size=14.5, anchor="start"))
    return W, H, "".join(p)


# ------------------------------------------------------------- figures 4, 5

def mono(x, y, s, size=10.6, anchor="middle", fill=ICON):
    return text(x, y, s, size=size, anchor=anchor, fill=fill, font=MONO)


def fig4():
    """Harness components plugged into Inspect's own extension points."""
    W, H = 1006, 322
    cw, gap, x0 = 138, 32, 9
    top, ph = 76, 110
    stages = [
        (doc("list"), 40, 50, "dataset", ["Task(dataset)"], "Frozen plan", "tasks, arms, models"),
        (sheet(), 36, 44, "setup solver", ["@solver, store_as"], "Scope compiler", "one contract per sample"),
        (robot(), 100, 92, "agent", ["react(on_continue)", "sandbox_agent_bridge"], "Look-ahead, journal",
         "advice after each turn"),
        (shield(), 30, 34, "approval policy", ["@approver"], "Grant gateway", "approve, reject, escalate"),
        (window() + group(48, -5, 1, database()), 84, 38, "tools, sandbox", ["sandbox(), mcp tools"],
         "Effect record", "kept by a sidecar service"),
        (window_check(BLUE_FILL), 46, 40, "scorer", ["@scorer"], "Replay oracle", "incidents from effects"),
    ]
    p = [box(4, top - 12, W - 8, ph + 24, "#F4F4F4", "#9A9A9A", rx=20, dash="6 4"),
         text(18, top - 21, "Inspect evaluation", size=14, anchor="start", style="italic"),
         box(4, 224, W - 8, 76, GREEN_FILL, GREEN_LINE, rx=20),
         text(18, 316, "harness components", size=14, anchor="start", style="italic")]
    for i, (icon, iw, ih, title, api, name, note) in enumerate(stages):
        x = x0 + i * (cw + gap)
        cx = x + cw / 2
        scale = 36 / ih
        p.append(box(x, top, cw, ph, BLUE_FILL, BLUE_LINE, rx=16))
        p.append(group(cx - iw * scale / 2, top + 9, scale, icon))
        p.append(text(cx, top + 66, title, size=14.5))
        for k, line in enumerate(api):
            p.append(mono(cx, top + 83 + k * 13.5, line))
        p.append(box(x, 234, cw, 56, "#fff", GREEN_LINE, rx=10, sw=1.4))
        p.append(text(cx, 257, name, size=14.5))
        p.append(text(cx, 276, note, size=11.6, style="italic"))
        p.append(arrow(cx, 232, cx, top + ph + 2, w=2.2))
        if i:
            p.append(arrow(x - gap + 2, top + ph / 2, x - 2, top + ph / 2, w=2.0, head=8.5, both=i in (3, 4)))
    # Trusted approver above the approval policy.
    cx = x0 + 3 * (cw + gap) + cw / 2
    p.append(group(cx - 15, 4, 1.0, person()))
    p.append(text(cx + 28, 19, "trusted approver", size=13, anchor="start"))
    p.append(mono(cx + 28, 33, "human_approver", anchor="start"))
    p.append(arrow(cx - 9, top - 2, cx - 9, 44, w=2.0))
    p.append(arrow(cx + 9, 44, cx + 9, top - 2, w=2.0))
    p.append(text(cx - 16, 61, "escalate", size=11.6, anchor="end"))
    p.append(text(cx + 16, 61, "grant", size=11.6, anchor="start"))
    return W, H, "".join(p)


CRUX_ROWS = [("Specify the construct", "scope contract"), ("Run dry runs first", "simulated backends"),
             ("Add real-time monitoring", "journal flags"), ("Document interventions", "ask and grant log"),
             ("Analyze and release logs", "replayable effect record"), ("Report cost", "budget ledger")]


def icon_strip(x, y, w, h, icons, label, dash=None):
    p = [box(x, y, w, h, SAND_FILL, SAND_LINE, rx=12, dash=dash)]
    step = w / len(icons)
    for i, (icon, iw) in enumerate(icons):
        p.append(group(x + step * (i + 0.5) - iw * 0.31, y + 9, 0.62, icon))
    p.append(text(x + w / 2, y + h - 10, label, size=11.6))
    return "".join(p)


def fig5():
    """A CRUX-style open-world run: dry run, live run, and what feeds each recommendation."""
    W, H = 892, 326
    mid = 142
    p = [group(12, mid - 26, 1.0, doc("text")), text(32, mid + 44, ["Open-world", "task"], size=14.5),
         arrow(60, mid, 92, mid, w=2.4)]
    gx, gy, gw, gh = 98, 10, 590, 306
    p.append(box(gx, gy, gw, gh, GREEN_FILL, GREEN_LINE, rx=26))
    # Dry run.
    ax, ay, aw, ah = gx + 14, gy + 14, 172, 236
    p.append(box(ax, ay, aw, ah, BLUE_FILL, BLUE_LINE, rx=22))
    p.append(group(ax + aw / 2 - 30, ay + 12, 0.6, robot()))
    p.append(arrow(ax + aw / 2, ay + 74, ax + aw / 2, ay + 100, w=2.2))
    p.append(icon_strip(ax + 14, ay + 104, aw - 28, 70, [(database(), 36), (envelope(ICON), 40), (flag_card(), 44)],
                        "simulated backends"))
    p.append(text(ax + aw / 2, ay + 206, "no real side effects", size=12, style="italic"))
    p.append(text(ax + aw / 2, gy + gh - 36, ["dry run on", "simulated backends"], size=12.6))
    # Hand-off.
    bx, by = ax + aw + 70, ay
    bw, bh = gx + gw - 14 - bx, ah
    p.append(arrow(ax + aw, mid, bx, mid, w=3.0))
    p.append(text((ax + aw + bx) / 2, mid + 17, ["same contract", "and gateway"], size=11.5))
    # Live run.
    p.append(box(bx, by, bw, bh, BLUE_FILL, BLUE_LINE, rx=22))
    p.append(group(bx + 20, by + 16, 0.74, robot()))
    sx, sy, sw, sh = bx + 186, by + 14, 120, 70
    p.append(icon_strip(sx, sy, sw, sh, [(window(), 40), (globe(), 36), (plug(), 36)], "real services"))
    p.append(arrow(bx + 100, by + 46, sx - 4, by + 46, w=3.6))
    p.append(text((bx + 100 + sx) / 2, by + 36, "act", size=13))
    p.append(group(bx + 228, by + 148, 1.0, clipboard_check()))
    p.append(text(bx + 247, by + 214, "Effect Journal", size=12))
    p.append(arrow(sx + 60, sy + sh + 3, sx + 60, by + 144, w=3.6))
    p.append(text(sx + 94, by + 110, ["record", "effect"], size=13))
    a, b = (bx + 222, by + 162), (bx + 104, by + 88)
    p.append(arrow(*a, *b, w=3.6))
    deg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 180
    rad = math.radians(deg)
    p.append(text((a[0] + b[0]) / 2 + 9 * math.sin(rad), (a[1] + b[1]) / 2 - 9 * math.cos(rad), "advise",
                  size=13, rotate=deg))
    p.append(group(bx + 40, by + 150, 1.0, person()))
    p.append(text(bx + 56, by + 202, "human monitor", size=12))
    p.append(arrow(bx + 57, by + 92, bx + 57, by + 146, w=2.0, both=True))
    p.append(text(bx + 49, by + 116, ["ask,", "grant"], size=11.6, anchor="end"))
    p.append(arrow(bx + 224, by + 178, bx + 80, by + 170, w=2.0))
    p.append(text(bx + 152, by + 190, "flag", size=11.6))
    p.append(text(bx + bw / 2, gy + gh - 36, ["live run on real services,", "journaled and monitored"], size=12.6))
    # CRUX recommendations and the artifact behind each.
    rx = gx + gw + 12
    p.append(brace_left(rx, 18, 308))
    for i, (rule, artifact) in enumerate(CRUX_ROWS):
        y = 40 + i * 48.6
        p.append(text(rx + 22, y, rule, size=14.5, anchor="start"))
        p.append(text(rx + 22, y + 16, "from the " + artifact, size=12, anchor="start", style="italic", fill="#333"))
    return W + 22, H, group(14, 0, 1, "".join(p))


# ------------------------------------------------------------------- output

FIGURES = {
    "fig1-before-after": fig1,
    "fig2a-example-input": fig2a,
    "fig2b-plain-agent": fig2b,
    "fig2c-harness-workflow": fig2c,
    "fig3-evaluation-framework": fig3,
    "fig4-inspect-integration": fig4,
    "fig5-crux-open-world": fig5,
}

CAPTIONS = {
    "fig1": ("Figure 1", "Previously, keeping agents inside their authorization boundary took a hand-written "
             "guardrail for each application. The harness takes plain task requests and guides one unmodified "
             "agent with a scope contract compiled from each request."),
    "fig2a": ("(a)", "Example input to the harness: a task with its stated scope and an unmodified agent loop."),
    "fig2b": ("(b)", "The plain agent meets a blocked route and may finish through a reachable resource that "
              "was never granted, instead of stopping with an honest blocker report."),
    "fig2c": ("(c)", "The harness compiles the request into a scope contract and plans over the granted "
              "actions (Grant Look-ahead). The agent then acts through a gateway that records every committed "
              "effect (Effect Journal) and returns it with fresh advice. Advice is not enforcement."),
    "fig2": ("Figure 2", "Agent workflows. (a) shows an example input. (b) shows the plain agent on that input. "
             "(c) shows the harness workflow around the same agent."),
    "fig3": ("Figure 3", "Evaluation framework. Incident records become task families in a frozen plan. One "
             "control layer runs any agent against simulated backends today and real tool backends later. "
             "Outcomes are read from replayed service effects, not from the agent's own account."),
    "fig4": ("Figure 4", "Integration with Inspect. Each harness component (green) implements one Inspect "
             "extension point (blue). An approver can only approve, modify, reject or escalate a call, so "
             "advice and journal text reach the agent between turns. The scorer reads the effect record "
             "from the sandbox."),
    "fig5": ("Figure 5", "A CRUX-style open-world evaluation run through the harness. The same contract and "
             "gateway are exercised first on simulated backends and then on real services. Each CRUX "
             "recommendation draws on one harness artifact."),
}


def chrome(*args):
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                        f"--user-data-dir={td}", *args], check=True, capture_output=True, timeout=180)


def render(name, w, h, body):
    OUT.mkdir(parents=True, exist_ok=True)
    markup = svg(w, h, body)
    (OUT / f"{name}.svg").write_text(markup + "\n")
    page = (f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{f(w)}px {f(h)}px;margin:0}}'
            f'html,body{{margin:0;padding:0;background:#fff;overflow:hidden}}svg{{display:block}}</style></head>'
            f'<body>{markup}</body></html>')
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "page.html"
        src.write_text(page)
        chrome("--no-pdf-header-footer", f"--print-to-pdf={OUT / (name + '.pdf')}", src.as_uri())
    subprocess.run(["pdftocairo", "-png", "-r", "300", "-singlefile", str(OUT / f"{name}.pdf"),
                    str(OUT / name)], check=True, capture_output=True)
    return markup


def preview(markups, sizes):
    def fig(name, width):
        w, h = sizes[name]
        return f'<div style="width:{width}px">{markups[name].replace(f"width=\"{f(w)}\" height=\"{f(h)}\"", "width=\"100%\"")}</div>'

    def cap(key, cls="cap"):
        tag, body = CAPTIONS[key]
        return f'<p class="{cls}"><b>{tag}</b>&nbsp; {html.escape(body)}</p>'

    page = f'''<!doctype html><html><head><meta charset="utf-8"><title>System design figures</title><style>
body{{margin:0;background:#fff;font-family:{SERIF};color:#000}}
main{{width:1040px;margin:0 auto;padding:36px 40px 44px}}
h1{{font-size:21px;margin:0 0 4px}} .note{{font-size:14px;color:#444;margin:0 0 26px}}
.cap{{font-size:15.5px;line-height:1.32;margin:10px 0 0}} .sub{{font-size:14.5px;line-height:1.3;margin:8px 0 0}}
.row{{display:flex;gap:44px;align-items:flex-end}} section{{margin:0 0 40px}} svg{{display:block;height:auto}}
</style></head><body><main>
<h1>{html.escape(HARNESS_NAME)}: system design figures</h1>
<p class="note">Design drawings for the planned harness and evaluation framework. No measured result is plotted.</p>
<section style="width:560px">{fig("fig1-before-after", 560)}{cap("fig1")}</section>
<section><div class="row"><div style="width:560px">{fig("fig2a-example-input", 560)}{cap("fig2a", "sub")}</div>
<div style="width:340px">{fig("fig2b-plain-agent", 320)}{cap("fig2b", "sub")}</div></div>
<div style="margin-top:26px">{fig("fig2c-harness-workflow", 1040)}{cap("fig2c", "sub")}</div>{cap("fig2")}</section>
<section>{fig("fig3-evaluation-framework", 1040)}{cap("fig3")}</section>
<section>{fig("fig4-inspect-integration", 1040)}{cap("fig4")}</section>
<section style="margin-bottom:0;width:940px">{fig("fig5-crux-open-world", 940)}{cap("fig5")}</section>
</main></body></html>'''
    path = OUT / "preview.html"
    path.write_text(page)
    shot = OUT / "preview.png"
    chrome("--force-device-scale-factor=2", "--window-size=1120,4200", f"--screenshot={shot}", path.as_uri())
    try:  # trim the unused tail of the tall screenshot
        from PIL import Image, ImageChops
    except ImportError:
        return
    image = Image.open(shot).convert("RGB")
    bounds = ImageChops.difference(image, Image.new("RGB", image.size, "#fff")).getbbox()
    if bounds:
        image.crop((0, 0, image.width, min(image.height, bounds[3] + 70))).save(shot)


def main():
    markups, sizes = {}, {}
    for name, draw in FIGURES.items():
        w, h, body = draw()
        markups[name], sizes[name] = render(name, w, h, body), (w, h)
    preview(markups, sizes)
    source = Path(__file__)
    meta = {"generator": str(source.relative_to(ROOT)),
            "generator_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "harness_label": HARNESS_NAME, "empirical_result_claimed": False, "model_calls": 0,
            "figures": {name: {"viewbox": [round(w, 1), round(h, 1)],
                               "files": [f"{name}.{ext}" for ext in ("svg", "pdf", "png")]}
                        for name, (w, h) in sizes.items()},
            "captions": {key: " ".join(value) for key, value in CAPTIONS.items()}}
    (OUT / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
    for name in FIGURES:
        print(OUT / f"{name}.pdf")
    print(OUT / "preview.png")


if __name__ == "__main__":
    main()
