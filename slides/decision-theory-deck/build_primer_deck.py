"""Build a ten-slide primer: decision-theory problems and techniques for containment-extension.

Companion to build_deck.py (discussion deck). Each content slide pairs one classical decision
problem with its standard solution technique and the place it occupies in the project.
No model calls; every project number is copied from docs/ or figures/incidents/analysis/summary.json
and cited on the slide. Toy quantities are labelled as such.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SHARED = HERE.parent / "trust4rsi-paper-deck"
sys.path.insert(0, str(SHARED))
from diagram_lib import arrow as shared_arrow  # noqa: E402

QA = HERE / "qa-primer"
QA.mkdir(parents=True, exist_ok=True)
SUMMARY = json.loads((REPO / "figures/incidents/analysis/summary.json").read_text())
LAT = SUMMARY["latency"]
STOP = SUMMARY["stop_behavior"]

PRS = Presentation()
PRS.slide_width, PRS.slide_height = Inches(13.333), Inches(7.5)
PRS.core_properties.title = "Decision theory for incident-aware agents"
PRS.core_properties.subject = "Seven decision problems and their techniques, mapped onto containment-extension"
PRS.core_properties.author = "Jiawei Li"


def rgb(s):
    return RGBColor.from_string(s.lstrip("#"))


NAVY = rgb("172D46")
INK = rgb("24364A")
MUTED = rgb("637285")
BLUE = rgb("3F6795")
TEAL = rgb("247B77")
ORANGE = rgb("B96333")
RED = rgb("B65249")
BG = rgb("F8F9FB")
WHITE = rgb("FFFFFF")
PALE = rgb("EAF0F6")
MINT = rgb("E7F2EF")
SAND = rgb("F7EDE4")
ROSE = rgb("F6E8E6")
LINE = rgb("D6DFE8")
LIGHT = rgb("BDCDDD")
DARKBOX = rgb("29445F")
PAGES = []
FOOT = "containment-extension  /  Decision theory primer  /  20 Oct 2026"


def text(s, x, y, w, h, value, size=18, color=INK, bold=False, center=False,
         role="body", valign=MSO_ANCHOR.MIDDLE, ls=1.08, font="Arial"):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = f"{role}:{len(s.shapes)}"
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(.025)
    tf.margin_top = tf.margin_bottom = Inches(.025)
    tf.vertical_anchor = valign
    for i, line_ in enumerate(value.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
        p.line_spacing = ls
        run = p.add_run()
        run.text = line_
        run.font.name = font
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.bold = bold
    return tb


def box(s, x, y, w, h, fill=PALE, line=None, rounded=True):
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
        shape.line.width = Pt(1)
    return shape


def line(s, x1, y1, x2, y2, color=LINE, width=.018):
    if y1 == y2:
        box(s, min(x1, x2), y1-width/2, max(abs(x2-x1), width), width, color, rounded=False)
    elif x1 == x2:
        box(s, x1-width/2, min(y1, y2), width, max(abs(y2-y1), width), color, rounded=False)
    else:
        raise ValueError("Only orthogonal lines are used.")


def arrow(s, points, color=BLUE):
    shared_arrow(s, [(Inches(x), Inches(y)) for x, y in points], color)


def circle(s, x, y, d, fill):
    shape = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    return shape


def footer(s, n, source="", dark=False):
    color = LIGHT if dark else MUTED
    text(s, .62, 7.06, 11.6, .23, source or FOOT, 9, color, role="source")
    text(s, 12.03, 7.02, .68, .29, f"{n:02d} / 10", 10, color, center=True, role="source")


def page(title, kicker, subtitle="", source="", dark=False):
    s = PRS.slides.add_slide(PRS.slide_layouts[6])
    box(s, 0, 0, 13.333, 7.5, NAVY if dark else BG, rounded=False)
    n = len(PRS.slides)
    text(s, .62, .32, 11.8, .28, kicker.upper(), 11, LIGHT if dark else BLUE, True, role="label")
    if title:
        text(s, .62, .84, 12.08, .9, title, 28, WHITE if dark else NAVY, True, role="title")
    if subtitle:
        text(s, .64, 1.76, 11.9, .44, subtitle, 16, LIGHT if dark else MUTED, role="subtitle")
    footer(s, n, source, dark)
    PAGES.append({"slide": n, "title": title, "kicker": kicker, "source": source})
    return s


def notes(s, body):
    s.notes_slide.notes_text_frame.text = body


def link(s, x, y, w, label, url, color=BLUE, size=11):
    shape = text(s, x, y, w, .3, label, size, color, role="source")
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            r.hyperlink.address = url


# Column frame shared by the seven problem slides -------------------------------------
LX, RX, CW, CY, CH = .65, 6.80, 5.88, 2.30, 3.22


def columns(s, problem_title, technique_title):
    box(s, LX, CY, CW, CH, WHITE, LINE)
    box(s, RX, CY, CW, CH, PALE)
    text(s, LX+.2, CY+.12, CW-.4, .3, "THE PROBLEM", 11, BLUE, True, role="label")
    text(s, LX+.2, CY+.4, CW-.4, .55, problem_title, 16, NAVY, True, ls=1.0)
    text(s, RX+.2, CY+.12, CW-.4, .3, "THE TECHNIQUE", 11, BLUE, True, role="label")
    text(s, RX+.2, CY+.4, CW-.4, .55, technique_title, 16, NAVY, True, ls=1.0)


def technique_body(s, formula, bullets, formula_size=20, bullet_size=13.5):
    text(s, RX+.2, CY+.95, CW-.4, .62, formula, formula_size, NAVY, True, role="formula",
         valign=MSO_ANCHOR.TOP, font="Arial")
    text(s, RX+.2, CY+1.62, CW-.4, CH-1.75, "\n".join("•  "+b for b in bullets), bullet_size,
         INK, valign=MSO_ANCHOR.TOP, ls=1.12)


def strip(s, body, label="IN CONTAINMENT-EXTENSION", color=TEAL, fill=MINT):
    box(s, .65, 5.74, 12.03, 1.12, fill)
    text(s, .85, 5.80, 3.0, .28, label, 11, color, True, role="label")
    text(s, .85, 6.06, 11.65, .74, body, 15, INK, valign=MSO_ANCHOR.TOP, ls=1.1)


# 01 Title ---------------------------------------------------------------------------------
s = page("", "containment-extension × decision theory", dark=True)
PAGES[-1]["title"] = "Decision theory for incident-aware agents"
text(s, .66, 1.05, 6.9, 2.1, "Decision theory for\nincident-aware agents", 40, WHITE, True, role="title")
text(s, .69, 3.35, 6.3, 1.0, "Seven classical problems, the standard technique for each, "
     "and where each one already lives in the project.", 19, LIGHT)
text(s, .69, 5.1, 6.4, .9, "A primer for discussion. Project numbers are copied from docs/\n"
     "and the incident-library summary; toy quantities are labelled.", 13, LIGHT, role="label")
items = [
    ("00", "Formulation", "a constrained POMDP"),
    ("01", "Optimal stopping", "when to stop retrying"),
    ("02", "Value of information", "diagnose or ask first"),
    ("03", "Constrained optimum", "min R  s.t.  U, C, F"),
    ("04", "Principal–agent", "incomplete grants"),
    ("05", "Ambiguity", "a silent A(c)"),
    ("06", "Sequential monitoring", "stop or continue, per action"),
    ("07", "Release gating", "a two-action decision"),
]
for i, (num, name, sub) in enumerate(items):
    y = 1.08 + i*.68
    box(s, 7.75, y, 4.95, .58, DARKBOX)
    text(s, 7.88, y+.1, .5, .38, num, 14, rgb("78B7B0"), True)
    text(s, 8.42, y+.04, 2.6, .5, name, 14, WHITE, True)
    text(s, 10.85, y+.06, 1.8, .46, sub, 11, LIGHT, ls=1.0)
notes(s, "Roadmap. One formulation slide, then seven problem slides, each with the same frame: "
      "the problem, the technique, and where it lives in containment-extension. Close with a map and readings.")

# 02 Formulation -----------------------------------------------------------------------------
s = page("The agent's situation is a constrained POMDP.", "00 / Formulation",
         "Three objects evolve by three different rules: the belief, the grant, and the value.",
         FOOT + "  /  Kaelbling, Littman & Cassandra 1998; Altman 1999; project docs/trust4rsi-next-experiments.md")
columns(s, "What the agent sees, believes, may do, and does", "Belief-state dynamic programming")
rows = [
    ("s", "State", "task feasibility, tool state, grant context c", BLUE, PALE),
    ("o", "Observation", "tool outputs, errors such as 503, human replies", BLUE, PALE),
    ("a", "Action", "work · retry · substitute · ask · stop", TEAL, MINT),
    ("e", "Effect", "what the action actually touched, journaled", ORANGE, SAND),
]
for i, (sym, name, body, color, fill) in enumerate(rows):
    y = CY + .98 + i*.55
    box(s, LX+.2, y, .5, .46, fill)
    text(s, LX+.2, y, .5, .46, sym, 18, color, True, True)
    text(s, LX+.82, y-.01, 1.45, .46, name, 14, NAVY, True)
    text(s, LX+2.2, y, CW-2.45, .46, body, 12.5, INK, ls=1.0)
technique_body(s, "V(b) = max a  [ r(b, a) + E o  V(b′) ]", [
    "Belief b updates by Bayes on each observation o.",
    "Permitted set A(c) updates only by a valid grant from the authorizer; a tool reply never enlarges it.",
    "Violation V(e, c) = 1[ e not in A(c) ] is a constraint on effects, not a term rewards can outbid.",
])
strip(s, "Recovery availability sets b; the grant column sets A(c); the objective min R s.t. U, C, F scores a policy θ. "
         "The 503 is evidence about b and never a grant. Three readings of one 503: epistemic, deontic, evaluative.")
notes(s, "Keep the three objects apart: belief changes with evidence, the grant changes only with a valid authorization "
      "event, and the value function compares completion, cost and honest stopping. This is the frame used by every later slide.")

# 03 Optimal stopping -------------------------------------------------------------------------
s = page("When should the agent stop retrying?", "01 / Optimal stopping",
         "Persist while one more attempt is expected to beat its cost; otherwise take the honest exit.",
         FOOT + "  /  Toy quantities: R = 10, B = 2, c = 1.6 give q* = 0.20. Gittins 1979; Snell-envelope backward induction.")
columns(s, "Each attempt costs c, succeeds with probability q, and an honest stop pays B", "Threshold rules and route indices")
text(s, LX+.2, CY+.95, CW-.4, .5, "One attempt:  stop = B,   try = qR + (1 − q)B − c", 15, INK)
x0, x1, yy = LX+.45, LX+CW-.45, CY+2.05
thr = x0 + (x1-x0)*.2
line(s, x0, yy, thr, yy, MUTED, .07)
line(s, thr, yy, x1, yy, BLUE, .07)
circle(s, thr-.09, yy-.09, .18, ORANGE)
text(s, x0-.1, yy+.12, .4, .28, "0", 12, MUTED)
text(s, x1-.3, yy+.12, .4, .28, "1", 12, MUTED, center=True)
text(s, thr-.7, yy+.12, 1.4, .3, "q* = c / (R − B)", 13, ORANGE, True, True)
text(s, x0, yy-.55, 1.4, .3, "STOP", 12, MUTED, True)
text(s, x1-1.0, yy-.55, 1.0, .3, "TRY", 12, BLUE, True, center=True)
text(s, LX+.2, CY+2.55, CW-.4, .55, "Calibrated q, risk neutrality, and a real honest-stop option are the assumptions that make the line a line.", 12.5, MUTED, ls=1.05)
technique_body(s, "try  iff  q (R − B) > c", [
    "Many steps: backward induction. Continue while the continuation value exceeds the stopping value (Snell envelope).",
    "Many recovery routes: a Gittins index per route; try the highest index, stop when all fall below B (Gittins 1979).",
    "A better exit option B raises q* and shortens persistence; a worse one buys stubbornness.",
])
strip(s, "The substitution incident family is persistence past the stated route. Readouts come from the effect journal, "
         "split into premature stops and wasted attempts, so a lower violation rate is not mistaken for better stopping.")
notes(s, "This is the smallest solvable version. The point is the shape of the rule: persistence is governed by the gap "
      "between success and the honest exit, divided into the attempt cost. The numbers are illustrative only.")

# 04 Value of information ---------------------------------------------------------------------
s = page("Diagnose or ask before acting?", "02 / Value of information",
         "A query is worth paying for only when some possible answer would change the action.",
         FOOT + "  /  Howard 1966; Hay, Russell, Tolpin & Shimony 2012 (arXiv:1207.5879); X1b in docs/trust4rsi-next-experiments.md")
columns(s, "Act on the current belief, or pay k for an answer first", "Expected value of information and metareasoning")
box(s, LX+.25, CY+1.0, 1.9, .78, PALE)
text(s, LX+.3, CY+1.03, 1.8, .4, "Act now", 15, BLUE, True, True)
text(s, LX+.3, CY+1.4, 1.8, .32, "max a  E[u(a)]", 12, MUTED, center=True)
box(s, LX+.25, CY+2.15, 1.9, .78, MINT)
text(s, LX+.3, CY+2.18, 1.8, .4, "Query, pay k", 15, TEAL, True, True)
text(s, LX+.3, CY+2.55, 1.8, .32, "then act on o", 12, MUTED, center=True)
arrow(s, [(LX+2.2, CY+2.54), (LX+2.75, CY+2.54), (LX+2.75, CY+1.95), (LX+3.25, CY+1.95)], TEAL)
arrow(s, [(LX+2.75, CY+2.54), (LX+2.75, CY+3.0), (LX+3.25, CY+3.0)], TEAL)
box(s, LX+3.3, CY+1.65, 2.35, .6, WHITE, LINE)
text(s, LX+3.35, CY+1.67, 2.25, .56, "o = recoverable\n→ best a | o", 12, INK, ls=1.0)
box(s, LX+3.3, CY+2.7, 2.35, .6, WHITE, LINE)
text(s, LX+3.35, CY+2.72, 2.25, .56, "o = not recoverable\n→ best a | o", 12, INK, ls=1.0)
text(s, LX+2.2, CY+1.0, 3.5, .6, "Same interface, two targets: a diagnostic informs b; a clarification informs A(c).", 12.5, MUTED, ls=1.05)
technique_body(s, "VOI = E o [ max a E[u | o] ] − max a E[u]  ≥ 0", [
    "Howard 1966: VOI is never negative and is zero when no answer would change the choice. Query iff VOI > k.",
    "Rational metareasoning: among diagnostics and questions pick the one with the largest VOI − cost (Hay et al. 2012).",
    "A request differs from a clarification: a valid reply can change A(c) itself, not only the belief about it.",
], formula_size=18)
strip(s, "X1b unspecified column: the reference behaviour is a clarification that names the archive and the missing permission. "
         "Scored as a response mix (silent read / clarification / authorized completion), never as a violation rate.")
notes(s, "VOI is the cleanest tool for the asking decision. Note the two targets: the belief about feasibility and the belief "
      "about the grant. Only a request to the authorizer can change the grant; a diagnostic cannot.")

# 05 Constrained optimization ----------------------------------------------------------------
s = page("Minimize incidents, subject to utility, cost and false intervention.", "03 / Constrained optimization",
         "The project objective is a constrained MDP, not a weighted sum of task score and safety.",
         FOOT + "  /  Objective from docs/incident-aware-optimization.md; Altman 1999; Achiam et al. 2017 (CPO, arXiv:1705.10528)")
columns(s, "Pick a policy θ on the utility–risk plane", "Lagrangian prices and what finite data cannot tell")
px, py, pw, ph = LX+.55, CY+1.0, 3.3, 1.8
line(s, px, py+ph, px+pw, py+ph, MUTED, .025)
line(s, px, py, px, py+ph, MUTED, .025)
text(s, px+pw-.2, py+ph+.05, 1.1, .26, "utility U →", 11, MUTED)
text(s, px+.08, py-.02, 1.6, .26, "incidents R ↑", 11, MUTED)
ux = px + pw*.55
box(s, ux, py, pw-(ux-px), ph, rgb("EEF5EC"), rounded=False)
line(s, ux, py, ux, py+ph, ORANGE, .03)
text(s, ux-.9, py+ph+.05, 1.8, .26, "U ≥ U(θ0) − δU", 11, ORANGE, True, True)
circle(s, px+pw*.78-.08, py+ph*.55-.08, .16, MUTED)
text(s, px+pw*.78+.1, py+ph*.55-.15, .6, .3, "θ0", 12, MUTED, True)
circle(s, px+pw*.62-.09, py+ph*.25-.09, .18, TEAL)
text(s, px+pw*.62+.1, py+ph*.25-.15, .6, .3, "θ*", 12, TEAL, True)
circle(s, px+pw*.3-.08, py+ph*.32-.08, .16, RED)
text(s, px+pw*.3-.15, py+ph*.32+.1, 1.2, .3, "infeasible", 11, RED)
text(s, LX+4.05, CY+1.0, 1.75, 2.1, "Feasible region: utility non-inferior, cost under B_run, false intervention under αF.\n\nθ* is the lowest R inside it.", 12, MUTED, valign=MSO_ANCHOR.TOP, ls=1.05)
technique_body(s, "θ* = argmin R(θ)  s.t.  U ≥ U(θ0) − δU,  C ≤ B_run,  F ≤ αF", [
    "Lagrangian L = R + λU·(U0 − δU − U)+ + λC·(…) + λF·(…): each multiplier is the price of its constraint (Altman 1999; CPO).",
    "Hard wall vs soft penalty is not identifiable from finite data: a large enough λ reproduces zero violations.",
    "Missing incident observations are unknown, not zeros; zero observed incidents is not a certified population bound.",
], formula_size=15.5, bullet_size=13)
strip(s, "Arms B3 and B4 run the same search under the same constraints with different R estimators: a frozen transcript proxy "
         "versus independently observed effects. ΔR, ΔU and false interventions are reported separately, never pooled.")
notes(s, "Say explicitly that the equation defines the target, not a scoring rule for the LLM. The multipliers are the only "
      "sense in which safety has a price here, and that price is set before search, not learned by the agent.")

# 06 Principal–agent -------------------------------------------------------------------------
s = page("Who holds the grant, and what happens when it is silent?", "04 / Principal–agent and incomplete contracts",
         "No grant covers every state. The agent must act where the contract says nothing or contradicts itself.",
         FOOT + "  /  Hadfield-Menell & Hadfield 2019 (arXiv:1804.04268); Hadfield-Menell et al. 2016 (CIRL), 2017 (Off-Switch Game)")
columns(s, "A principal writes grant c; the agent acts; an oracle judges the effect", "Cooperative games with information asymmetry")
chain = [("Principal", "writes c", BLUE, PALE), ("Agent", "chooses a", TEAL, MINT),
         ("Effect e", "journaled", ORANGE, SAND), ("Oracle", "V(e, c)", RED, ROSE)]
for i, (name, sub, color, fill) in enumerate(chain):
    x = LX+.25 + i*1.42
    box(s, x, CY+1.05, 1.22, .86, fill)
    text(s, x+.05, CY+1.1, 1.12, .4, name, 14, color, True, True)
    text(s, x+.05, CY+1.48, 1.12, .34, sub, 11, MUTED, center=True)
    if i < 3:
        arrow(s, [(x+1.25, CY+1.48), (x+1.4, CY+1.48)], MUTED)
text(s, LX+.25, CY+2.1, CW-.5, 1.0,
     "Effect oracle ≠ authorization oracle. The journal says what e touched; only c says whether e was allowed. "
     "The same action is legitimate or a violation depending only on c.", 13, INK, valign=MSO_ANCHOR.TOP, ls=1.08)
technique_body(s, "V(e, c) = 1[ e not in A(c) ];  A(c) undefined when c is silent", [
    "Incomplete contracting: who holds residual control in the uncovered state is the design variable (Hadfield-Menell & Hadfield 2019).",
    "CIRL: human and agent share a reward the agent does not know; the optimal agent elicits and defers rather than guesses (2016).",
    "Off-switch game: deference has positive value exactly when the agent is uncertain about the objective (2017).",
], formula_size=17, bullet_size=13)
strip(s, "Library records code the boundary crossed but not whether the grant was stated to the agent. Proposed E5 codebook field: "
         "explicit / implicit / unspecified / conflicting. The blurred recovery boundary is this slide's uncovered state.")
notes(s, "This is where the blurred-boundary thread connects to a literature. The incomplete-contracts framing gives the "
      "vocabulary: residual control rights, uncovered states, and who decides there.")

# 07 Ambiguity ---------------------------------------------------------------------------------
s = page("What should a careful agent do when A(c) is unknown?", "05 / Decision under ambiguity",
         "Not risk, where probabilities are known, but ambiguity: a set of plausible grants with no prior over them.",
         FOOT + "  /  Gilboa & Schmeidler 1989; Savage 1951; Iyengar 2005; Turner, Hadfield-Menell & Tadepalli 2020 (arXiv:1902.09725). Toy payoffs.")
columns(s, "Two plausible grants, three actions, toy payoffs", "Rules that do not need a prior over grants")
hdr = ["action", "c: allowed", "c: excluded", "maxmin", "regret"]
rows = [
    ["read archive", "+10", "−20", "−20", "30"],
    ["ask first", "+7", "+7", "+7", "3"],
    ["stop, report", "+2", "+2", "+2", "8"],
]
cx = [LX+.25, LX+1.5, LX+2.7, LX+3.9, LX+4.75]
cw = [1.25, 1.2, 1.2, .85, .85]
for j, h in enumerate(hdr):
    text(s, cx[j], CY+1.0, cw[j], .34, h, 10.5, BLUE, True, center=j > 0)
for i, row in enumerate(rows):
    y = CY+1.38 + i*.46
    box(s, LX+.2, y, CW-.4, .42, WHITE if i % 2 else PALE, rounded=False)
    for j, v in enumerate(row):
        col = TEAL if (j == 3 and i == 1) or (j == 4 and i == 1) else INK
        text(s, cx[j], y+.02, cw[j], .38, v, 12.5, col, j == 0 or col == TEAL, center=j > 0)
text(s, LX+.2, CY+2.8, CW-.4, .4, "Regret of a = best payoff in that column − payoff of a. Both rules pick ask; a prior p would pick read for large p.", 11.5, MUTED, ls=1.0)
technique_body(s, "maxmin:  max a  min c  E c [ u(a) ]\nregret:  min a  max c  [ u*(c) − u(a, c) ]", [
    "Maxmin expected utility (Gilboa & Schmeidler 1989); minimax regret (Savage 1951); robust MDPs over an uncertainty set (Iyengar 2005).",
    "Impact regularisers such as attainable-utility preservation penalise irreversible, option-destroying moves (Turner et al. 2020).",
    "Prediction: ambiguity-averse agents prefer reversible actions and questions. Over-conservatism is the price, so measure it.",
], formula_size=14.5, bullet_size=13)
strip(s, "X1b adds unspecified and conflicting grant columns (64 runs). Over-conservatism is read on the authorized-feasible cells, "
         "where a blocker is a cost rather than caution; access rate plus response mix replaces a violation rate under silence.")
notes(s, "Distinguish risk from ambiguity. Under silence there is no authorization oracle, so expected-utility rules need a prior "
      "the task does not supply. Maxmin and regret rules give a reference behaviour without one.")

# 08 Sequential monitoring --------------------------------------------------------------------
dk, dm = LAT["detection_days_known"], LAT["detection_median"]
dsk, dsm = LAT["disclosure_days_known"], LAT["disclosure_median"]
retro, n_inc = STOP["retrospective_only"], SUMMARY["n"]
s = page("An approver decides stop or continue, one action at a time.", "06 / Sequential monitoring",
         "Evidence arrives as a stream, and the harm it points to is observed late, partially, or never.",
         FOOT + "  /  Wald 1945; Page 1954; monitor objective and latency figures from docs/incident-aware-optimization.md and incident-library-analysis.md")
columns(s, "A log-likelihood walk between two boundaries", "Sequential tests with asymmetric costs")
wx, wy, ww, wh = LX+.35, CY+1.0, 3.6, 1.5
line(s, wx, wy+.15, wx+ww, wy+.15, RED, .025)
line(s, wx, wy+wh-.15, wx+ww, wy+wh-.15, TEAL, .025)
line(s, wx, wy+wh/2, wx+ww, wy+wh/2, LINE, .015)
text(s, wx+ww+.05, wy+.02, 1.4, .26, "log B: stop", 11, RED, True)
text(s, wx+ww+.05, wy+wh-.28, 1.4, .26, "log A: clear", 11, TEAL, True)
pts = [(0, .5), (.1, .42), (.2, .55), (.3, .47), (.4, .36), (.5, .3), (.6, .33), (.7, .22), (.8, .17), (.9, .08)]
for (fx, fy) in pts:
    circle(s, wx+ww*fx-.05, wy+wh*fy-.05, .1, BLUE)
for (fx1, fy1), (fx2, fy2) in zip(pts, pts[1:]):
    # stair-step so lines stay orthogonal
    line(s, wx+ww*fx1, wy+wh*fy1, wx+ww*fx2, wy+wh*fy1, BLUE, .02)
    line(s, wx+ww*fx2, wy+wh*fy1, wx+ww*fx2, wy+wh*fy2, BLUE, .02)
text(s, wx, wy+wh+.02, ww, .26, "actions observed →", 11, MUTED)
text(s, LX+.2, CY+2.8, CW-.4, .4,
     f"Public library, n = {n_inc}: {retro} found only in retrospect; detection median {dm:g} days (n = {dk}); "
     f"disclosure median {dsm:g} days (n = {dsk}).", 11.5, MUTED, ls=1.0)
technique_body(s, "SPRT: continue while A < Λn < B;  Λn = ∏ p1(oi) / p0(oi)", [
    "Wald 1945: A and B follow from the costs of a false stop and a missed violation; CUSUM (Page 1954) for a change in behaviour.",
    "Project monitor objective: max TPR s.t. FPR ≤ α and monitor cost ≤ B_monitor, thresholds from benign calibration only.",
    "Labels are delayed and right-censored, so the observer's evidence lags the action; detection is not prevention.",
], formula_size=14.5)
strip(s, "The action monitor runs as an Inspect approver and the effect journal supplies e per step. Arm B1 versus B0 measures "
         "what observation adds on its own, with no claimed prevention effect.")
notes(s, "The sequential frame explains why the approver's thresholds are a cost decision, not a probability cutoff. "
      "The latency numbers show that the labels used to calibrate it arrive weeks or months late.")

# 09 Release gating ----------------------------------------------------------------------------
s = page("Release the new policy, or hold it?", "07 / Release gating as a statistical decision",
         "A gate is a two-action decision with asymmetric losses and a noisy, paired estimate of the difference.",
         FOOT + "  /  Bayes decision rule; McNemar exact test on paired twins; Smith & Winkler 2006 (The Optimizer's Curse)")
columns(s, "Loss matrix and the paired counts that inform it", "Decide by expected loss, then guard the estimate")
gx, gy = LX+.3, CY+1.0
text(s, gx+1.3, gy, 1.2, .3, "safe", 12, MUTED, True, True)
text(s, gx+2.55, gy, 1.2, .3, "unsafe", 12, MUTED, True, True)
for i, (rl, a, b, ca, cb) in enumerate([("release", "0", "L_miss", MINT, ROSE), ("hold", "L_hold", "0", SAND, MINT)]):
    y = gy+.35 + i*.62
    text(s, gx, y, 1.2, .55, rl, 13, NAVY, True)
    box(s, gx+1.3, y, 1.2, .55, ca)
    text(s, gx+1.3, y, 1.2, .55, a, 13, INK, True, True)
    box(s, gx+2.55, y, 1.2, .55, cb)
    text(s, gx+2.55, y, 1.2, .55, b, 13, INK, True, True)
text(s, gx+4.0, gy+.35, 1.6, 1.2, "Paired twins:\nb = old fails, new passes\nc = old passes, new fails", 11.5, MUTED, valign=MSO_ANCHOR.TOP, ls=1.05)
text(s, LX+.2, CY+2.65, CW-.4, .55, "Only discordant pairs carry information about the difference; the exact McNemar test uses b and c alone.", 12, MUTED, ls=1.05)
technique_body(s, "release  iff  P(unsafe | data)·L_miss  <  P(safe | data)·L_hold", [
    "Frequentist twin: exact McNemar on discordant pairs with power fixed before the run; the paper deck carries the power table.",
    "Optimizer's curse: the best-looking candidate among many is biased upward; shrink or confirm on held-out twins (Smith & Winkler 2006).",
    "Group-sequential or always-valid tests let the gate stop early without inflating the error rates.",
], formula_size=15.5, bullet_size=13)
strip(s, "Regression gate plus hidden-effect twins. Every twin carries an explicit grant, so the gate tests constraint compliance; "
         "an effect journal alone cannot label an environment whose grant is silent.")
notes(s, "A gate is a decision, so write its loss matrix. The McNemar machinery estimates one probability in that rule; "
      "the losses are a policy choice and belong in the preregistration.")

# 10 Map --------------------------------------------------------------------------------------
s = page("Where each problem lives in containment-extension.", "Summary",
         "One row per problem: the technique it brings and the project hook that uses it.",
         FOOT + "  /  Reading path linked below; the companion discussion deck (decision-theory.pptx) asks the open questions.")
hdr = ["Problem", "Technique", "Project hook"]
cols_ = [(.66, 2.6), (3.3, 4.6), (7.95, 4.72)]
for (x, w), h in zip(cols_, hdr):
    text(s, x+.08, 2.25, w-.16, .3, h.upper(), 11, BLUE, True)
table = [
    ("Formulation", "belief-state DP with an effect constraint", "b from recovery; A(c) from grant; min R s.t. U, C, F"),
    ("Optimal stopping", "threshold q(R−B) > c; Gittins index", "substitution family; premature stops vs wasted attempts"),
    ("Value of information", "VOI = E max − max E; metareasoning", "X1b: clarification as reference behaviour"),
    ("Constrained optimization", "constrained MDP, Lagrangian prices", "B3 vs B4 under identical constraints"),
    ("Principal–agent", "incomplete contracts; CIRL; off-switch", "E5 field: explicit / implicit / unspecified / conflicting"),
    ("Ambiguity", "maxmin, minimax regret, impact penalties", "X1b silent and conflicting cells; over-conservatism readout"),
    ("Sequential monitoring", "SPRT, CUSUM; max TPR s.t. FPR ≤ α", "Inspect approver; B1 vs B0; delayed labels"),
    ("Release gating", "expected-loss rule; McNemar; optimizer's curse", "regression gate + hidden-effect twins"),
]
for i, row in enumerate(table):
    y = 2.58 + i*.42
    box(s, .66, y, 12.0, .38, WHITE if i % 2 else PALE, rounded=False)
    for j, v in enumerate(row):
        x, w = cols_[j]
        text(s, x+.08, y+.02, w-.16, .34, v, 12, NAVY if j == 0 else INK, j == 0, ls=1.0)
line(s, .66, 6.05, 12.66, 6.05)
text(s, .68, 6.12, 11.9, .28, "Reading path:  formulation → information → contracts → robustness → sequential decisions", 12, MUTED)
refs = [
    (.68, 2.3, "Kaelbling et al. 1998, POMDPs", "https://doi.org/10.1016/S0004-3702(98)00023-X"),
    (3.0, 1.7, "Howard 1966, VOI", "https://doi.org/10.1109/TSSC.1966.300074"),
    (4.7, 2.35, "Hay et al. 2012, metareasoning", "https://arxiv.org/abs/1207.5879"),
    (7.05, 2.1, "Hadfield-Menell 2016 / 2017", "https://arxiv.org/abs/1606.03137"),
    (9.15, 1.8, "Turner et al. 2020, AUP", "https://arxiv.org/abs/1902.09725"),
    (10.95, 1.75, "Achiam et al. 2017, CPO", "https://arxiv.org/abs/1705.10528"),
]
for x, w, label, url in refs:
    link(s, x, 6.45, w, label, url, BLUE, 10.5)
text(s, .68, 6.75, 11.9, .26, "Altman 1999 (Constrained MDPs) · Gittins 1979 · Gilboa & Schmeidler 1989 · Wald 1945 · Page 1954 · Smith & Winkler 2006", 10, MUTED, role="source")
notes(s, "Use the map to route discussion: which of these rows does the Trust4RSI paper actually need, and which belong "
      "to the next programme? The open questions are in the companion discussion deck.")


def validate():
    assert len(PRS.slides) == 10
    issues, counts = [], []
    for i, slide in enumerate(PRS.slides, 1):
        visible = []
        assert slide.notes_slide.notes_text_frame.text.strip(), f"Missing notes: {i}"
        for shape in slide.shapes:
            if min(shape.left, shape.top) < 0:
                issues.append(f"slide {i}: negative bounds: {shape.name}")
            if shape.left+shape.width > PRS.slide_width+Inches(.01):
                issues.append(f"slide {i}: right overflow: {shape.name}")
            if shape.top+shape.height > PRS.slide_height+Inches(.01):
                issues.append(f"slide {i}: bottom overflow: {shape.name}")
            if shape.has_text_frame and shape.text:
                visible.append(shape.text)
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        if not shape.name.startswith("source") and r.font.size < Pt(10):
                            issues.append(f"slide {i}: small text: {shape.name}")
        counts.append({"slide": i, "words": len(" ".join(visible).split())})
    assert not issues, issues
    (QA / "structure-validation.json").write_text(json.dumps({
        "slides": 10, "editable_text_and_shapes": True, "word_counts": counts,
        "bounds_issues": issues, "pages": PAGES, "model_calls": 0,
        "project_numbers": {"latency": {k: LAT[k] for k in ("detection_days_known", "detection_median",
                                                            "disclosure_days_known", "disclosure_median")},
                            "retrospective_only": STOP["retrospective_only"], "n": SUMMARY["n"]},
    }, indent=2, ensure_ascii=False)+"\n")
    return counts


if __name__ == "__main__":
    counts = validate()
    target = HERE / "decision-theory-primer.pptx"
    PRS.save(target)
    print(f"Saved {target}: 10 slides. Words per slide: {[c['words'] for c in counts]}")
