"""Editable visual primitives shared by the decision-theory results deck.

Everything is a native PowerPoint shape (rectangles, ovals, triangles, text boxes) so the
deck stays editable and renders through render_deck_pdf.py without rasterisation.
Inline markup in text: ``_{...}`` is a subscript and ``^{...}`` a superscript.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
SHARED = HERE.parent / "trust4rsi-paper-deck"
sys.path.insert(0, str(SHARED))
from diagram_lib import arrow as shared_arrow  # noqa: E402

QA = HERE / "qa"
QA.mkdir(parents=True, exist_ok=True)
PRS = Presentation()
PRS.slide_width, PRS.slide_height = Inches(13.333), Inches(7.5)
PRS.core_properties.title = "Decision theory for delegated agents: six usable results"
PRS.core_properties.subject = "Theorems, assumptions, calculations and applications to containment-extension"
PRS.core_properties.author = "Jiawei Li"


def rgb(s):
    return RGBColor.from_string(s.lstrip("#"))


# Palette: one deep ink, one dark surface, five saturated accents, and their tints.
DEEP = rgb("0F1F33")
NAVY = rgb("172D46")
DARKBOX = rgb("22395A")
INK = rgb("22313F")
MUTED = rgb("5F6E80")
BLUE = rgb("3A6391")
TEAL = rgb("1E7A72")
ORANGE = rgb("B4602E")
RED = rgb("B04E45")
PLUM = rgb("6A4C93")
GOLD = rgb("A4761A")
BG = rgb("F6F8FA")
WHITE = rgb("FFFFFF")
PALE = rgb("E8EFF6")
MINT = rgb("E1F0ED")
SAND = rgb("F8ECE1")
ROSE = rgb("F7E6E4")
LILAC = rgb("EEE8F6")
CREAM = rgb("F7EFD9")
LINE = rgb("D3DCE5")
LIGHT = rgb("B9C8D8")
TINT = {BLUE: PALE, TEAL: MINT, ORANGE: SAND, RED: ROSE, PLUM: LILAC, GOLD: CREAM, NAVY: PALE}
PAGES = []
SW, SH = 13.333, 7.5
ML, MR = .62, 12.71           # content margins
CW = MR - ML                  # content width
TOTAL = 10

SOURCES = {
    "fixture": (
        "containment-extension: From reported incidents to testable questions",
        "../../docs/trust4rsi-incident-to-experiment.md",
    ),
    "x1b": (
        "containment-extension: Next experiments, X1 / X1b",
        "../../docs/trust4rsi-next-experiments.md",
    ),
    "pilot": (
        "containment-extension: 160-run incident study (September 17, 2026)",
        "../../docs/incident-study-results.md",
    ),
    "meta": (
        "Hay et al. (2012), Selecting Computations: Theory and Applications",
        "https://arxiv.org/abs/1207.5879",
    ),
    "cirl": (
        "Hadfield-Menell et al. (2016), Cooperative Inverse Reinforcement Learning",
        "https://arxiv.org/abs/1606.03137",
    ),
    "switch": (
        "Hadfield-Menell et al. (2017), The Off-Switch Game",
        "https://arxiv.org/abs/1611.08219",
    ),
}

_MARK = re.compile(r"(\^\{[^}]*\}|_\{[^}]*\})")
_ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}


def text(s, x, y, w, h, value, size=20, color=INK, bold=False, center=False,
         role="body", valign=MSO_ANCHOR.MIDDLE, ls=1.08, align=None):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = f"{role}:{len(s.shapes)}"
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(.025)
    tf.margin_top = tf.margin_bottom = Inches(.025)
    tf.vertical_anchor = valign
    alignment = _ALIGN[align] if align else (PP_ALIGN.CENTER if center else PP_ALIGN.LEFT)
    for i, line_ in enumerate(value.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alignment
        p.line_spacing = ls
        for part in _MARK.split(line_):
            if not part:
                continue
            script = None
            if part.startswith("_{"):
                script, part = "-25000", part[2:-1]
            elif part.startswith("^{"):
                script, part = "30000", part[2:-1]
            run = p.add_run()
            run.text = part
            run.font.name = "Arial"
            run.font.size = Pt(size)
            run.font.color.rgb = color
            run.font.bold = bold
            if script:
                run.font._element.set("baseline", script)
    return tb


def box(s, x, y, w, h, fill=PALE, line=None, rounded=True, width=1.0):
    shape = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    if rounded:
        shape.adjustments[0] = .05
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    if line is not None:
        shape.line.color.rgb = line
        shape.line.width = Pt(width)
    return shape


def line(s, x1, y1, x2, y2, color=LINE, width=.018):
    if y1 == y2:
        box(s, min(x1, x2), y1-width/2, max(abs(x2-x1), width), width, color, rounded=False)
    elif x1 == x2:
        box(s, x1-width/2, min(y1, y2), width, max(abs(y2-y1), width), color, rounded=False)
    else:
        raise ValueError("Only orthogonal lines are used.")


def dashed(s, x1, y1, x2, y2, color=LINE, width=.018, dash=.08, gap=.06):
    """A dashed orthogonal line made of short native segments."""
    if y1 == y2:
        x, end = min(x1, x2), max(x1, x2)
        while x < end:
            line(s, x, y1, min(x+dash, end), y1, color, width)
            x += dash+gap
    else:
        y, end = min(y1, y2), max(y1, y2)
        while y < end:
            line(s, x1, y, x1, min(y+dash, end), color, width)
            y += dash+gap


def arrow(s, points, color=BLUE):
    shared_arrow(s, [(Inches(x), Inches(y)) for x, y in points], color)


def circle(s, x, y, d, fill, line_=None):
    shape = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line_ is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line_
        shape.line.width = Pt(1.25)
    return shape


def dot(s, x, y, d=.07, fill=BLUE):
    return circle(s, x-d/2, y-d/2, d, fill)


def dotline(s, p1, p2, color, n=18, d=.065):
    """A straight line between two points drawn as evenly spaced dots (any angle)."""
    (x1, y1), (x2, y2) = p1, p2
    for i in range(n+1):
        t = i/n
        dot(s, x1+(x2-x1)*t, y1+(y2-y1)*t, d, color)


def badge(s, x, y, label, color, d=.44, size=13):
    circle(s, x, y, d, color)
    text(s, x, y, d, d, label, size, WHITE, True, True, role="label")


def square_badge(s, x, y, label, color, d=.46, size=13):
    box(s, x, y, d, d, color, rounded=True)
    text(s, x, y, d, d, label, size, WHITE, True, True, role="label")


def label(s, x, y, w, value, color=BLUE, size=11, align="l"):
    return text(s, x, y, w, .28, value.upper(), size, color, True, role="label", align=align)


def chip(s, x, y, w, value, color=BLUE, fill=None, size=11, h=.34):
    box(s, x, y, w, h, fill or TINT.get(color, PALE))
    text(s, x+.06, y, w-.12, h, value, size, color, True, True, role="label")


def card(s, x, y, w, h, accent=None, fill=WHITE, edge=LINE, bar=.07):
    """A crisp white card with a 1 pt edge and an optional solid accent bar on the left."""
    box(s, x, y, w, h, fill, edge, rounded=False)
    if accent is not None:
        box(s, x, y, bar, h, accent, rounded=False)


def panel(s, x, y, w, h, color):
    """A tinted panel with a matching solid top bar."""
    box(s, x, y, w, h, TINT.get(color, PALE), rounded=False)
    box(s, x, y, w, .06, color, rounded=False)


def theorem(s, x, y, w, h, formula, caption="", size=28, tag="RESULT", accent=TEAL, ls=1.08):
    """The statement band: dark surface, accent bar, white formula."""
    box(s, x, y, w, h, NAVY, rounded=False)
    box(s, x, y, .09, h, accent, rounded=False)
    label(s, x+.26, y+.12, w-.4, tag, accent)
    cap_h = .34 if caption else 0
    text(s, x+.26, y+.40, w-.42, h-.46-cap_h, formula, size, WHITE, True, role="formula",
         valign=MSO_ANCHOR.MIDDLE, ls=ls)
    if caption:
        text(s, x+.26, y+h-cap_h-.10, w-.42, cap_h, caption, 12.5, LIGHT, role="caption",
             valign=MSO_ANCHOR.TOP)


def bar(s, x, y, w, h, frac, color, track=PALE, rounded=False):
    box(s, x, y, w, h, track, rounded=rounded)
    if frac > 0:
        box(s, x, y, max(w*frac, .02), h, color, rounded=rounded)


def docicon(s, x, y, color, w=.50, h=.62, fill=WHITE):
    """A small document glyph: page with three text lines."""
    box(s, x, y, w, h, fill, color, rounded=False, width=1.5)
    for i, frac in enumerate((.62, .62, .40)):
        box(s, x+w*.17, y+h*(.27+i*.19), w*frac, h*.07, color, rounded=False)


def assumes(s, value):
    y, h = 5.70, .40
    box(s, ML, y, CW, h, SAND, rounded=False)
    box(s, ML, y, .07, h, ORANGE, rounded=False)
    label(s, ML+.22, y+.06, 1.0, "Assumes", ORANGE)
    text(s, ML+1.22, y, CW-1.4, h, value, 13, INK, role="assumption")


def use(s, value, color=TEAL):
    y, h = 6.22, .66
    box(s, ML, y, CW, h, color)
    box(s, ML+.16, y+.16, .62, .34, WHITE)
    text(s, ML+.16, y+.16, .62, .34, "USE", 12, color, True, True, role="label")
    text(s, ML+.96, y, CW-1.1, h, value, 18, WHITE, True, role="application")


def footer(s, n, source="", dark=False):
    color = LIGHT if dark else MUTED
    text(s, ML, 7.00, 11.3, .23, source or "containment-extension  /  Decision rules with stated assumptions",
         9, color, role="source")
    text(s, 11.95, 6.96, .76, .29, f"{n:02d} / {TOTAL}", 10, color, True, True, role="source")
    gap, seg = .06, (CW-9*.06)/TOTAL
    for i in range(TOTAL):
        done = i < n
        box(s, ML+i*(seg+gap), 7.34, seg, .055,
            (TEAL if done else DARKBOX) if dark else (TEAL if done else LINE), rounded=False)


def page(title, kicker, subtitle="", source="", dark=False, tag="", accent=BLUE):
    s = PRS.slides.add_slide(PRS.slide_layouts[6])
    box(s, 0, 0, SW, SH, DEEP if dark else BG, rounded=False)
    n = len(PRS.slides)
    kx = ML
    if tag:
        square_badge(s, ML, .40, tag, accent)
        kx = ML+.60
    text(s, kx, .40, 11.0, .46, kicker.upper(), 11, LIGHT if dark else accent, True, role="label")
    if title:
        text(s, ML, .92, CW, .70, title, 30, WHITE if dark else NAVY, True, role="title")
        box(s, ML, 1.68, .95, .05, accent, rounded=False)
    if subtitle:
        text(s, ML+.02, 1.80, CW, .44, subtitle, 15.5, LIGHT if dark else MUTED, role="subtitle")
    footer(s, n, source, dark)
    PAGES.append({"slide": n, "title": title, "kicker": kicker, "source": source})
    return s


def notes(s, body, keys=()):
    refs = "\n".join(f"{SOURCES[k][0]}\n{SOURCES[k][1]}" for k in keys)
    s.notes_slide.notes_text_frame.text = body + ("\n\nSources / 来源\n" + refs if refs else "")


def link(s, x, y, w, label_, url, color=BLUE, size=11, h=.32):
    shape = text(s, x, y, w, h, label_, size, color, role="source")
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            r.hyperlink.address = url
    return shape


def write_structure(extra):
    (QA/"structure-validation.json").write_text(json.dumps(
        {"pages": PAGES, "sources": SOURCES, **extra}, indent=2, ensure_ascii=False)+"\n")
