"""Build the incident-aware optimization explainer deck (PPTX).

Pure python-pptx; no model calls; all claims come from docs/ and figures/.
Run: python3 scripts/build_incident_optimization_deck.py
Output: slides/incident-aware-optimization-v2.pptx
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
OUT = ROOT / "slides/incident-aware-optimization-v2.pptx"

INK = RGBColor(0x11, 0x11, 0x11)
BLUE = RGBColor(0x36, 0x5E, 0x9E)
BLUE_PALE = RGBColor(0xED, 0xF4, 0xFB)
BLUE_LIGHT = RGBColor(0xBD, 0xD8, 0xED)
GRAY = RGBColor(0x66, 0x66, 0x66)
LINE = RGBColor(0xC9, 0xC9, 0xC9)
RED = RGBColor(0xB3, 0x48, 0x31)
RED_PALE = RGBColor(0xFB, 0xEF, 0xEC)
GREEN = RGBColor(0x2E, 0x7D, 0x5B)
GREEN_PALE = RGBColor(0xEA, 0xF5, 0xEF)
YELLOW = RGBColor(0xFF, 0xF2, 0xCC)
ORANGE = RGBColor(0xB8, 0x73, 0x2A)
ORANGE_PALE = RGBColor(0xFD, 0xF3, 0xE7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Arial"

SW, SH = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.5)
FOOTER = "Incident-aware optimization · design proposal · containment-extension · October 2026 · no benchmark improvement measured"

prs = Presentation()
prs.slide_width, prs.slide_height = SW, SH
BLANK = prs.slide_layouts[6]
page = [0]


# ---------------------------------------------------------------- helpers
def _run(par, text, size, color=INK, bold=False, italic=False):
    r = par.add_run()
    r.text = text
    f = r.font
    f.name, f.size, f.bold, f.italic = FONT, Pt(size), bold, italic
    f.color.rgb = color
    return r


def textbox(slide, x, y, w, h, text="", size=14, color=INK, bold=False, align=PP_ALIGN.LEFT,
            anchor=MSO_ANCHOR.TOP, italic=False, line_spacing=1.1):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = anchor
    first = True
    for ln in text.split("\n"):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.line_spacing = line_spacing
        _run(p, ln, size, color, bold, italic)
    return tb


def bullets(slide, x, y, w, h, items, size=14, color=INK, gap=4, line_spacing=1.08):
    """items: list of str or (str, level) or (str, level, bold_prefix)."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    first = True
    for item in items:
        if isinstance(item, str):
            item = (item, 0)
        text, level = item[0], item[1]
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = level
        p.line_spacing = line_spacing
        p.space_after = Pt(gap)
        marker = "•  " if level == 0 else "–  "
        indent = "" if level == 0 else "      "
        if "**" in text:
            # inline bold: "**Label.** rest **more** ..."
            parts = text.split("**")
            sz = size if level == 0 else size - 1
            _run(p, indent + marker, sz, color)
            for i, part in enumerate(parts):
                if part:
                    _run(p, part, sz, color, bold=(i % 2 == 1))
        else:
            _run(p, indent + marker + text, size if level == 0 else size - 1, color)
    return tb


def rect(slide, x, y, w, h, fill=WHITE, line=LINE, width=0.75, rounded=True, dash=False):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                                 x, y, w, h)
    if rounded:
        shp.adjustments[0] = 0.06
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(width)
        if dash:
            from pptx.enum.dml import MSO_LINE_DASH_STYLE
            shp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    shp.shadow.inherit = False
    shp.text_frame.text = ""
    return shp


def card(slide, x, y, w, h, heading, body, fill=BLUE_PALE, edge=BLUE, hcolor=None,
         hsize=13, bsize=11, body_color=INK, badge=None):
    rect(slide, x, y, w, h, fill, edge, 1)
    hcolor = hcolor or edge
    hx = x + Inches(0.12)
    if badge is not None:
        circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.12), y + Inches(0.12),
                                      Inches(0.3), Inches(0.3))
        circ.fill.solid()
        circ.fill.fore_color.rgb = edge
        circ.line.fill.background()
        tf = circ.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        _run(p, str(badge), 10, WHITE, True)
        hx = x + Inches(0.5)
    textbox(slide, hx, y + Inches(0.08), w - (hx - x) - Inches(0.1), Inches(0.4),
            heading, hsize, hcolor, True)
    if isinstance(body, list):
        bullets(slide, x + Inches(0.08), y + Inches(0.48), w - Inches(0.16), h - Inches(0.55),
                body, bsize, body_color, gap=2)
    else:
        textbox(slide, x + Inches(0.1), y + Inches(0.48), w - Inches(0.2), h - Inches(0.55),
                body, bsize, body_color, line_spacing=1.12)


def arrow_right(slide, x, y, w=Inches(0.35), h=Inches(0.3), color=BLUE):
    a = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, y, w, h)
    a.fill.solid()
    a.fill.fore_color.rgb = color
    a.line.fill.background()
    return a


def table(slide, x, y, w, h, rows, col_widths=None, size=11, header_fill=BLUE, zebra=True,
          first_col_bold=False):
    nrows, ncols = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nrows, ncols, x, y, w, h)
    tbl = gt.table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Emu(int(w * cw / total))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            tf = cell.text_frame
            tf.word_wrap = True
            lines = str(val).split("\n")
            for i, ln in enumerate(lines):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.line_spacing = 1.05
                bold = r == 0 or (first_col_bold and c == 0)
                _run(p, ln, size, WHITE if r == 0 else INK, bold)
            cell.fill.solid()
            if r == 0:
                cell.fill.fore_color.rgb = header_fill
            elif zebra and r % 2 == 0:
                cell.fill.fore_color.rgb = RGBColor(0xF4, 0xF6, 0xFA)
            else:
                cell.fill.fore_color.rgb = WHITE
    return gt


def picture(slide, path, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(path), x, y, w, h)


def new_slide(title, subtitle=None, section=None):
    s = prs.slides.add_slide(BLANK)
    page[0] += 1
    # accent bar + title
    bar = rect(s, MARGIN, Inches(0.42), Inches(0.09), Inches(0.62), BLUE, None, rounded=False)
    tsize = 26 if len(title) <= 50 else (23 if len(title) <= 60 else 20)
    textbox(s, MARGIN + Inches(0.2), Inches(0.33), Inches(11.5), Inches(0.6), title, tsize, INK, True,
            anchor=MSO_ANCHOR.MIDDLE)
    if subtitle:
        textbox(s, MARGIN + Inches(0.2), Inches(0.95), Inches(12), Inches(0.4), subtitle, 13, GRAY,
                italic=False)
    if section:
        textbox(s, Inches(9.3), Inches(0.12), Inches(3.5), Inches(0.3), section, 9, BLUE, True,
                align=PP_ALIGN.RIGHT)
    # footer
    ln = s.shapes.add_connector(1, MARGIN, Inches(7.05), SW - MARGIN, Inches(7.05))
    ln.line.color.rgb = LINE
    ln.line.width = Pt(0.5)
    textbox(s, MARGIN, Inches(7.08), Inches(11), Inches(0.3), FOOTER, 8, GRAY)
    textbox(s, SW - MARGIN - Inches(1), Inches(7.08), Inches(1), Inches(0.3), str(page[0]), 9, GRAY,
            align=PP_ALIGN.RIGHT)
    return s


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


BODY_Y = Inches(1.45)
BODY_W = SW - 2 * MARGIN
BODY_H = Inches(5.5)
CB = 15   # card body size
CH = 16   # card heading size


def big_bullets(slide, x, y, w, h, items, size=18):
    return bullets(slide, x, y, w, h, items, size, gap=10, line_spacing=1.12)


def band(slide, y, text, h=Inches(0.9), fill=YELLOW, size=15):
    rect(slide, MARGIN, y, BODY_W, h, fill, None)
    textbox(slide, MARGIN + Inches(0.25), y + Inches(0.08), BODY_W - Inches(0.5), h - Inches(0.16),
            text, size, INK, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.15)


# ===================================================================== 1 title
s = prs.slides.add_slide(BLANK)
page[0] += 1
rect(s, 0, 0, SW, SH, WHITE, None, rounded=False)
rect(s, 0, 0, Inches(0.35), SH, BLUE, None, rounded=False)
textbox(s, Inches(1.0), Inches(1.6), Inches(11.5), Inches(1.2),
        "Incident-Aware Optimization", 44, INK, True)
textbox(s, Inches(1.0), Inches(2.6), Inches(11.3), Inches(1.4),
        "Turning the history of agent incidents into better evaluation tasks,\n"
        "runtime monitors and instructions: a proposed Inspect extension", 22, BLUE)
textbox(s, Inches(1.0), Inches(4.35), Inches(11), Inches(1.4),
        "We cannot make incidents never happen. We can make every incident that did happen\n"
        "a permanent, regression-tested improvement to the next policy.", 16, GRAY, italic=True)
textbox(s, Inches(1.0), Inches(5.9), Inches(11), Inches(0.8),
        "Jiawei Li · containment-extension · design proposal, October 2026", 12, GRAY)

# ===================================================================== 2 agenda
s = new_slide("What this deck covers")
items = [
    ("1", "Motivation", "Incidents are inevitable; history is the asset"),
    ("2", "Delivery", "An Inspect extension plus an incident library; who uses it"),
    ("3", "Design", "One architecture, seven principles"),
    ("4", "Components", "Intake, library, synthesis, replay, optimizer, monitor, release"),
    ("5", "Standout features", "Time split, benign twins, poisoning defence, blame"),
    ("6", "Risks, evaluation, status", "What could fool us, how we would know, what exists"),
]
y = BODY_Y
for num, head, body in items:
    rect(s, MARGIN, y, BODY_W, Inches(0.78), BLUE_PALE if int(num) % 2 else WHITE, LINE, 0.5)
    textbox(s, MARGIN + Inches(0.15), y + Inches(0.1), Inches(0.6), Inches(0.6), num, 24, BLUE, True)
    textbox(s, MARGIN + Inches(0.8), y + Inches(0.08), Inches(3.6), Inches(0.6), head, 18, INK, True,
            anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, MARGIN + Inches(4.5), y + Inches(0.08), Inches(7.7), Inches(0.62), body, 15, GRAY,
            anchor=MSO_ANCHOR.MIDDLE)
    y += Inches(0.88)

# ===================================================================== 3 complex systems
s = new_slide("Incidents are a property of complex systems", "Four views that agree on the premise", "1 · MOTIVATION")
quotes = [
    ("Perrow, Normal Accidents (1984)", "Tightly coupled, complex systems make some accidents inevitable."),
    ("Taleb, The Black Swan (2007)", "Rare events cannot be predicted in detail. Build systems that gain from them."),
    ("Popper (1963)", "Knowledge grows by correcting errors."),
    ("Reason, Swiss cheese (1990)", "Holes in the defences move. Each incident shows where one is."),
]
y = BODY_Y
for h, b in quotes:
    card(s, MARGIN, y, Inches(6.6), Inches(1.08), h, b, BLUE_PALE, BLUE, hsize=14, bsize=CB)
    y += Inches(1.17)
rows = [["Year", "Nobody predicted it in detail"],
        ["2008", "Global financial crisis"],
        ["2011", "Fukushima"],
        ["2019", "Boeing 737 MAX"],
        ["2021", "Log4Shell"],
        ["2024", "CrowdStrike outage"],
        ["2025", "Coding agent deletes a production database"]]
table(s, Inches(7.45), BODY_Y, Inches(5.38), Inches(3.3), rows, [1.0, 4.4], size=13, first_col_bold=True)
rect(s, Inches(7.45), Inches(5.1), Inches(5.38), Inches(1.75), YELLOW, None)
textbox(s, Inches(7.6), Inches(5.18), Inches(5.1), Inches(1.6),
        "AI agents are the newest tightly coupled system.\nThe question is not whether incidents happen. It is what we do with each one.",
        15, INK, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.15)

# ===================================================================== 4 institutions
s = new_slide("What other fields built from their incidents", "Every mature high-risk field runs a learning loop", "1 · MOTIVATION")
rows = [
    ["Domain", "Institution", "What gets updated"],
    ["Aviation", "NTSB investigations; confidential ASRS reports", "Procedures, checklists, training"],
    ["Nuclear", "INPO peer review after Three Mile Island", "Fleet-wide lessons and inspections"],
    ["Finance", "Stress tests after 2008 (Dodd-Frank, Basel III)", "Historical crises rerun against every bank, yearly"],
    ["Cybersecurity", "CVE, NVD, MITRE ATT&CK", "Proof of concept, patch, detection rule, regression test"],
    ["Software ops", "Blameless postmortems", "Alerts, runbooks, CI gates"],
]
table(s, MARGIN, BODY_Y, BODY_W, Inches(3.6), rows, [1.6, 4.4, 4.4], size=14, first_col_bold=True)
band(s, Inches(5.4), "The pattern: investigate → record → test → update → check against the next event.\n"
                     "None promised zero incidents. They promised no incident would be wasted.", Inches(1.4), BLUE_PALE, 16)

# ===================================================================== 4b incidents on record
s = new_slide("Agent incidents on the record, 2024–2025", "Documented by the developers themselves, by evaluators, or by security researchers", "1 · MOTIVATION")
rows = [
    ["When", "System", "What happened", "Documented by"],
    ["Aug 2024", "Sakana AI Scientist", "Edited its own run script to lift the timeout instead of fixing the code", "Sakana AI"],
    ["Dec 2024", "OpenAI o1", "In tests: tried to disable oversight (5%), manipulated data (19%), denied it afterwards", "Apollo Research, o1 system card"],
    ["Dec 2024", "OpenAI o1-preview", "Edited the game state to beat Stockfish; 45 hack attempts in 122 games, unprompted", "Palisade Research"],
    ["Mar 2025", "OpenAI reasoning agent", "Reward hacking in coding tasks; penalising it taught the model to hide intent", "OpenAI (Baker et al.)"],
    ["May 2025", "OpenAI o3", "Sabotaged its shutdown script in 7 of 100 runs despite being told to allow shutdown", "Palisade Research"],
    ["May 2025", "Claude Opus 4", "Blackmail in 84% of a constructed replacement scenario; later 16-model study", "Anthropic system card; Agentic Misalignment"],
    ["May 2025", "GitHub MCP server", "Prompt injection in a public issue made the agent leak private repositories", "Invariant Labs"],
    ["Jul 2025", "Replit agent", "Deleted a production database during a code freeze, then misreported it", "SaaStr founder; Replit"],
    ["Jul 2025", "Amazon Q extension", "A malicious pull request shipped a wiper prompt in release 1.84.0", "AWS; 404 Media"],
    ["Jul 2025", "Gemini CLI", "Moved files into a directory that did not exist, destroying a user's project", "AI Incident Database #1178"],
    ["Aug 2025", "Perplexity Comet", "Hidden text on a web page made the browser agent exfiltrate a one-time password", "Brave"],
    ["Oct 2025", "ChatGPT Atlas", "New prompt-injection class found by red teaming; OpenAI: may never be fully solved", "OpenAI"],
    ["Nov 2025", "Claude Code (GTG-1002)", "State-linked operator ran an espionage campaign on ~30 targets, 80–90% autonomous", "Anthropic; AI Incident Database #1263"],
]
table(s, MARGIN, BODY_Y, BODY_W, Inches(5.45), rows, [1.1, 2.3, 6.0, 3.0], size=10.5, first_col_bold=True)
notes(s, "Every row is a public report; figures are the reporters' own. Full sources on the incident references slide. "
         "Several rows are evaluation findings in constructed scenarios, not deployment incidents; the deck says which.")

# ===================================================================== 5 AI 2025-26
s = new_slide("AI agents, 2025–2026: incidents arrive, institutions form", None, "1 · MOTIVATION")
card(s, MARGIN, BODY_Y, Inches(6.05), Inches(3.4), "What those incidents share", [
    "Exploiting the evaluation: test cases, timeouts, game state",
    "Resisting oversight in tests: shutdown, replacement",
    "Following injected instructions: issues, web pages, extensions",
    "Destructive actions despite explicit instructions: code freeze, file moves",
    "Agents as attack tooling at scale"],
     RED_PALE, RED, hsize=CH, bsize=CB)
card(s, Inches(7.0), BODY_Y, Inches(5.83), Inches(3.4), "In policy", [
    "EU AI Act, Art. 73: serious-incident reporting for high-risk systems",
    "California SB 53: critical-incident reporting by frontier developers",
    "OECD AI Incident Monitor, AI Incident Database",
    "All of it is narrative. Nobody turns a report into an executable test"],
     BLUE_PALE, BLUE, hsize=CH, bsize=CB)
band(s, Inches(5.1), "Expected harm = incident rate × deployment volume.\n"
                     "Patching a prompt has diminishing returns. A regression case is reused against every future policy. Learning compounds.",
     Inches(1.75), YELLOW, 15)

# ===================================================================== 6 thesis
s = new_slide("The thesis", None, "1 · MOTIVATION")
rect(s, MARGIN, BODY_Y, BODY_W, Inches(1.5), BLUE, None)
textbox(s, MARGIN + Inches(0.3), BODY_Y + Inches(0.1), BODY_W - Inches(0.6), Inches(1.3),
        "We cannot remove every possibility of an agent incident.\nWe can make sure no incident that did happen is wasted.",
        24, WHITE, True, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)
textbox(s, MARGIN, Inches(3.1), BODY_W, Inches(0.45),
        "“Those who cannot remember the past are condemned to repeat it.”  Santayana", 13, GRAY, italic=True, align=PP_ALIGN.CENTER)
card(s, MARGIN, Inches(3.7), Inches(4.0), Inches(3.15), "What we cannot do", [
    "Enumerate every route an agent might take",
    "Prevent with instructions alone",
    "Certify absence from a handful of clean runs"], RED_PALE, RED, hsize=CH, bsize=CB)
card(s, Inches(4.67), Inches(3.7), Inches(4.0), Inches(3.15), "What we can do", [
    "Observe effects independently",
    "Store each incident as an executable case",
    "Replay every case against every new policy",
    "Hold out by lineage and by date"], GREEN_PALE, GREEN, hsize=CH, bsize=CB)
card(s, Inches(8.83), Inches(3.7), Inches(4.0), Inches(3.15), "What this proposal is", [
    "An Inspect extension plus an incident library",
    "A constrained optimiser: fewer incidents at the same utility and cost",
    "A human-gated, versioned release pipeline"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)

# ===================================================================== 7 same score different risk
s = new_slide("Same score, different risk", "Task scorers do not see incidents", "1 · MOTIVATION")
picture(s, FIG / "incident-optimization-intuition-v1/incident-optimization-intuition.png",
        MARGIN + Inches(0.3), BODY_Y - Inches(0.05), w=Inches(8.4))
big_bullets(s, Inches(9.35), BODY_Y, Inches(3.6), Inches(5.3), [
    "Policy A solves the task. Policy B copies a prior run's answer. Both pass.",
    "Only an independent observer of effects tells them apart.",
    "Seen in our runs: 6/8 outside reads without enforcement, 0/8 with it; a cached flag accepted by the scorer.",
], 15)
notes(s, "Sources: docs/incident-study-results.md, docs/link-study-results.md, results/link-study-v1/run-0022.")

# ===================================================================== 8 gap
s = new_slide("The gap this proposal closes", None, "1 · MOTIVATION")
rows = [
    ["Missing today", "This design"],
    ["Scorers are blind to authorization", "Independent incident observer"],
    ["Incident knowledge is scattered prose", "One executable, versioned library"],
    ["Fixes are not regression-tested", "Every library case replays before release"],
    ["Monitors lack calibration and provenance", "Calibrated thresholds; every rule cites its incident"],
    ["No held-out protocol for learned policies", "Hold out by lineage and by date"],
]
table(s, MARGIN, BODY_Y, BODY_W, Inches(4.6), rows, [5.0, 6.0], size=16, first_col_bold=True)

# ===================================================================== 9 deliverable
s = new_slide("What is delivered", "An Inspect extension plus an incident library; the model is never modified", "2 · DELIVERY")
cols = [
    ("Python package", BLUE_PALE, BLUE, ["Incident observer scorers", "Action monitor as a tool-call approver", "Replay toolbox", "Optimizer CLI with regression gate"]),
    ("Incident library", YELLOW, ORANGE, ["Structured incident records", "Executable cases with benign twins", "Dev / calibration / held-out splits", "Researcher-only; never in the agent's context"]),
    ("Releases", GREEN_PALE, GREEN, ["Eval pack vN: qualified tasks", "Policy vN: clauses + monitor rules", "Evidence per change, changelog, rollback"]),
]
x = MARGIN
for head, fill, edge, body in cols:
    card(s, x, BODY_Y, Inches(4.0), Inches(4.2), head, body, fill, edge, hsize=CH, bsize=CB)
    x += Inches(4.17)
band(s, Inches(5.9), "Built on Inspect (approvers, scorers, eval logs), Inspect Scout (scanners), ControlArena (monitors, micro-protocols) and Hawk (runs at scale).", Inches(0.9), BLUE_PALE, 14)

# ===================================================================== 10 who uses it
s = new_slide("Who uses it: optional or mandated?", None, "2 · DELIVERY")
rows = [
    ["Mode", "Who", "What they do"],
    ["A · Opt-in plugin", "Agent developers, eval teams", "Run on their own tasks; private library"],
    ["B · Shared library", "Labs, AISIs, academic groups", "Contribute redacted cases; pull eval packs"],
    ["C · Reference suite", "Third-party evaluators, regulators", "Require passing the held-out incident pack"],
]
table(s, MARGIN, BODY_Y, BODY_W, Inches(2.6), rows, [2.4, 3.6, 5.0], size=15, first_col_bold=True)
card(s, MARGIN, Inches(4.45), Inches(6.05), Inches(2.4), "Recommendation", [
    "Ship A first and make it good",
    "Design the shared schema for B from day one",
    "Do not design around C; a mandate needs a reproducible library first"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
card(s, Inches(7.0), Inches(4.45), Inches(5.83), Inches(2.4), "Governance in every mode", [
    "Humans approve cases in and policies out",
    "The evaluated agent never sees the library",
    "Every released rule cites its incident and trial"], RED_PALE, RED, hsize=CH, bsize=CB)

# ===================================================================== 11 architecture
s = new_slide("The architecture: history → replay → policy", "Three stages, one scheduled loop, one one-way exit to held-out evaluation", "3 · DESIGN")
picture(s, FIG / "incident-optimization-overview-v2/incident-optimization-overview-v2.png",
        MARGIN + Inches(0.55), Inches(1.35), h=Inches(5.65))

# ===================================================================== 11b ecosystem
s = new_slide("What we build on, and what we add", "The design composes existing systems; the new parts are the library, the gate and the loop", "3 · DESIGN")
rows = [
    ["System", "It provides", "We reuse", "We add"],
    ["Inspect (UK AISI)", "Tasks, scorers, sandboxes, tool-call approvers, eval logs", "Everything; approvers host the action monitor", "Incident observer scorers; regression gate"],
    ["Inspect Scout", "Transcript scanners at scale", "Scan own logs for intake", "Incident schema; evidence grades"],
    ["ControlArena", "Monitors with suspicion scores; trusted monitoring, defer-to-trusted; settings with side tasks", "Monitor interface and micro-protocols; BashArena", "Rule provenance; calibration-only thresholds"],
    ["Hawk / Vivaria (METR)", "Run Inspect at scale; action monitor tied to approvals", "Execution backend; context-gap warning", "Time-split evaluation; versioned releases"],
    ["ImpossibleBench, AgentDojo, ResearchArena, SHADE-Arena", "Tasks and official baselines", "Held-out tasks; published defences", "Benign twins; post-cutoff incident families"],
    ["AIID, OECD AIM, MIT AI Risk Repository, MITRE ATLAS", "Incident reports and taxonomies", "Sources and tags", "Executable reproductions"],
]
table(s, MARGIN, BODY_Y, BODY_W, Inches(5.2), rows, [2.6, 3.6, 3.0, 3.1], size=12, first_col_bold=True)

# ===================================================================== 12 principles
s = new_slide("Seven design principles", "Each closes a way the loop could fool itself", "3 · DESIGN")
princ = [
    ("Observe effects, not vibes", "An incident is a witnessed effect, recorded outside the agent's authority."),
    ("Executable, not narrative", "A case must replay. Grades: A executable, B trace, C narrative."),
    ("Every incident has a benign twin", "A fix that blocks the twin counts as a false refusal."),
    ("Development feedback only", "Held-out by lineage and by date; the proposer sees aggregates."),
    ("Constrained optimisation", "min R s.t. utility, cost, refusals and zero regressions."),
    ("Grounded changes", "Clauses from a reviewed catalog; thresholds from benign data."),
    ("Human gates, versioned releases", "Signed, diffable, rollback-able."),
]
cw, ch = Inches(4.0), Inches(1.62)
for i, (h, b) in enumerate(princ):
    col, row = i % 3, i // 3
    x = MARGIN + col * (cw + Inches(0.17))
    y = BODY_Y + row * (ch + Inches(0.12))
    w = Inches(12.33) if i == 6 else cw
    card(s, x, y, w, ch, h, b, BLUE_PALE if i % 2 == 0 else WHITE, BLUE, INK, 14, CB, badge=i + 1)

# ===================================================================== 13 C1 intake
s = new_slide("Component 1 · Incident intake", "From the web and from your own runs", "4 · COMPONENTS")
card(s, MARGIN, BODY_Y, Inches(3.6), Inches(2.9), "Sources", [
    "Own Inspect logs, scanned with Inspect Scout", "AI Incident Database, OECD AI Incident Monitor, MIT AI Risk Repository", "Postmortems, issues, advisories; provenance kept"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
arrow_right(s, Inches(4.2), Inches(2.75))
card(s, Inches(4.65), BODY_Y, Inches(4.0), Inches(2.9), "Intake agent", [
    "Normalise to one incident schema", "Taxonomy from MITRE ATLAS and OWASP agentic threats; dedupe", "Grade evidence: A executable, B trace, C narrative"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
arrow_right(s, Inches(8.75), Inches(2.75))
card(s, Inches(9.2), BODY_Y, Inches(3.63), Inches(2.9), "Human review gate", [
    "Accept, reject, defer", "A report alone never changes a policy"], RED_PALE, RED, hsize=CH, bsize=CB)
card(s, MARGIN, Inches(4.6), Inches(6.05), Inches(2.25), "Unique", [
    "Evidence grades separate leads from facts", "Fingerprints carry an incident across benchmarks"], GREEN_PALE, GREEN, hsize=CH, bsize=CB)
card(s, Inches(7.0), Inches(4.6), Inches(5.83), Inches(2.25), "Threat: library poisoning", [
    "Web reports are untrusted input to an optimiser", "Defence: grade, quarantine, reproduce before influence, human gate"], RED_PALE, RED, hsize=CH, bsize=CB)

# ===================================================================== 14 C2 library
s = new_slide("Component 2 · The incident library", "Executable history with partitions", "4 · COMPONENTS")
card(s, MARGIN, BODY_Y, Inches(6.05), Inches(5.4), "One case contains", [
    "Checkpoint, authorization policy, tools",
    "Exact trace and the minimal trigger",
    "Expected effects",
    "A benign twin task",
    "Evidence grade, report date, provenance hashes",
    "Lineage: variants and retries stay together",
    "Case format compatible with ControlArena settings (main task + side task)"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
card(s, Inches(7.0), BODY_Y, Inches(5.83), Inches(2.6), "Partitions", [
    "Development, calibration, held-out", "Split by lineage and by report date"], YELLOW, ORANGE, hsize=CH, bsize=CB)
card(s, Inches(7.0), Inches(4.25), Inches(5.83), Inches(2.6), "Unique", [
    "Executable, like CVE proofs of concept", "Benign twins built in", "Researcher tooling only; never reaches the agent"], GREEN_PALE, GREEN, hsize=CH, bsize=CB)
notes(s, "Seed material already in the repo: 28 harness cases, 8 replay controls, 12 permission controls, ImpossibleBench checks, 1,543 monitor inputs from 224 rollouts. None stored in this schema yet.")

# ===================================================================== 15 C3 synthesis
s = new_slide("Component 3 · Case synthesis", "The evaluation updates itself", "4 · COMPONENTS")
steps = [
    ("Narrative → reproduction", "Rebuild the scenario in a sandbox with the same tools and boundary"),
    ("Matched family", "Feasible, impossible, broken environment, plus a benign twin"),
    ("Qualification", "Reference solution replays; negative labels need evidence"),
    ("Variants", "Mutate names, URLs and wording so nothing is memorised"),
    ("Release into eval pack", "Qualified cases join development; held-out stays locked"),
]
y = BODY_Y
for i, (h, b) in enumerate(steps):
    rect(s, MARGIN, y, Inches(8.0), Inches(0.82), BLUE_PALE if i % 2 == 0 else WHITE, LINE, 0.5)
    textbox(s, MARGIN + Inches(0.15), y, Inches(2.6), Inches(0.82), h, 14, BLUE, True, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, MARGIN + Inches(2.8), y, Inches(5.1), Inches(0.82), b, CB, INK, anchor=MSO_ANCHOR.MIDDLE)
    y += Inches(0.9)
card(s, Inches(8.75), BODY_Y, Inches(4.08), Inches(4.4), "Unique", [
    "New incidents become new tasks on a schedule",
    "An unexpected pass triggers a label audit, not a silent win",
    "A narrative lead becomes evidence only here"], GREEN_PALE, GREEN, hsize=CH, bsize=CB)
notes(s, "Foundation: counterfactual evaluation infrastructure offline stages passed (4 cases, 320 transition checks, 17 grader cases).")

# ===================================================================== 16 C4 replay
s = new_slide("Component 4 · Counterfactual replay and blame", None, "4 · COMPONENTS")
picture(s, FIG / "counterfactual-diagnostic-tool-v1/counterfactual-diagnostic-tool.png",
        MARGIN, BODY_Y, w=Inches(6.2))
card(s, Inches(6.95), BODY_Y, Inches(5.88), Inches(2.5), "Two comparisons", [
    "Fixed-call replay: change one action, find the first differing response",
    "Agent continuation: change one cue, re-sample, estimate P(incident | cue)"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
card(s, Inches(6.95), Inches(4.1), Inches(5.88), Inches(2.75), "Unique: blame records", [
    "Each incident gets a minimal trigger and a named cause",
    "Blame proposes both a clause and a monitor signature",
    "Replays become new library cases"], GREEN_PALE, GREEN, hsize=CH, bsize=CB)

# ===================================================================== 17 C5 optimizer
s = new_slide("Component 5 · The policy optimizer", "Constrained search with a feedback ablation", "4 · COMPONENTS")
rect(s, MARGIN, BODY_Y, BODY_W, Inches(0.9), BLUE_PALE, BLUE, 1)
textbox(s, MARGIN, BODY_Y, BODY_W, Inches(0.9),
        "min R(θ)   s.t.   U ≥ U₀ − δ,   C ≤ B,   F ≤ α,   Reg(θ) = 0", 20, BLUE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
card(s, MARGIN, Inches(2.6), Inches(6.05), Inches(2.2), "θ is", [
    "Instruction clauses from a reviewed catalog", "Monitor rules and thresholds", "Approval mode per tool class"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
card(s, Inches(7.0), Inches(2.6), Inches(5.83), Inches(2.2), "Rules of the search", [
    "Proposer sees aggregates only", "Selection rule frozen before search", "Missing outcomes stay unknown"], RED_PALE, RED, hsize=CH, bsize=CB)
rows = [["Arm", "Selects on"],
        ["B0 · upstream", "nothing (reference)"],
        ["B1 · observation only", "nothing; observer added"],
        ["B2 · established defence", "AgentDojo defences; AI Control protocols"],
        ["B3 · proxy feedback", "utility + transcript judge"],
        ["B4 · incident feedback", "utility + verified effects   ← primary contrast: B4 vs B3"]]
table(s, MARGIN, Inches(5.0), BODY_W, Inches(1.9), rows, [3.0, 8.0], size=12, first_col_bold=True)

# ===================================================================== 18 C6 monitor
s = new_slide("Component 6 · The action monitor", "The library at runtime, as an Inspect tool-call approver", "4 · COMPONENTS")
chain = [("Tool call", WHITE, INK), ("Scope contract", BLUE_PALE, BLUE), ("Incident signatures", BLUE_PALE, BLUE),
         ("ControlArena monitor", BLUE_PALE, BLUE), ("shadow → flag → defer → block", GREEN_PALE, GREEN)]
x = MARGIN
cw = Inches(2.3)
for i, (h, fill, edge) in enumerate(chain):
    rect(s, x, BODY_Y, cw, Inches(1.1), fill, edge, 1)
    textbox(s, x, BODY_Y, cw, Inches(1.1), h, 14, edge, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    if i < len(chain) - 1:
        arrow_right(s, x + cw + Inches(0.03), BODY_Y + Inches(0.4), Inches(0.2), Inches(0.28))
    x += cw + Inches(0.2)
card(s, MARGIN, Inches(3.0), Inches(6.05), Inches(3.85), "Built on", [
    "Inspect tool-call approvers: approve, modify, reject, escalate, terminate",
    "ControlArena monitors with suspicion scores",
    "AI Control micro-protocols: trusted monitoring, defer-to-trusted, resampling (Ctrl-Z)",
    "Hawk's lesson: a monitor with less context than the agent is a known failure"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
card(s, Inches(7.0), Inches(3.0), Inches(5.83), Inches(3.85), "What we add", [
    "Every rule links to the incident and replay behind it",
    "Thresholds from benign calibration at a fixed false-positive rate",
    "Shadow mode first, so observation itself is measured",
    "Monitor cost counts in C(θ); ships inside each release"], GREEN_PALE, GREEN, hsize=CH, bsize=CB)

# ===================================================================== 19 C7 release
s = new_slide("Component 7 · Automatic update and release", "CI for safety policies: scheduled, gated, diffable, reversible", "4 · COMPONENTS")
stages = ["ingest", "synthesize", "run", "diagnose", "revise", "regression gate", "human approval", "release vN"]
x = MARGIN
bw = Inches(1.38)
for i, st in enumerate(stages):
    fill, edge = (RED_PALE, RED) if st in ("regression gate", "human approval") else (BLUE_PALE, BLUE)
    rect(s, x, BODY_Y, bw, Inches(0.85), fill, edge, 1)
    textbox(s, x, BODY_Y, bw, Inches(0.85), st, 12, edge, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    if i < len(stages) - 1:
        arrow_right(s, x + bw + Inches(0.01), BODY_Y + Inches(0.29), Inches(0.17), Inches(0.26))
    x += bw + Inches(0.19)
big_bullets(s, MARGIN, Inches(2.75), BODY_W, Inches(3.0), [
    "A release ships clauses, monitor rules, the eval pack and evidence per change",
    "Gate: every grade-A case replays without a new incident; refusals stay under the limit",
    "Nothing auto-deploys; a human approves",
    "\"No eligible candidate\" is a valid, reported outcome",
], 17)

# ===================================================================== 20 features
s = new_slide("What makes this more than a prompt optimizer", None, "5 · FEATURES")
feats = [
    ("Time-split evaluation", "Tune on incidents before T; test on those after T."),
    ("Benign twins", "False refusals measured on the same object."),
    ("Poisoning defence", "No report changes policy without a reproduction."),
    ("Cross-benchmark reuse", "One fingerprint, probes in several benchmarks."),
    ("Counterfactual blame", "Every rule carries the replay that justified it."),
    ("Federated sharing", "Share signatures and cases, never raw traces."),
    ("Observer-effect reporting", "B1 vs B0 shows whether watching changes behaviour."),
    ("No-win is a result", "Zero incidents is reported with uncertainty, not as a bound."),
]
cw, ch = Inches(3.0), Inches(2.55)
for i, (h, b) in enumerate(feats):
    col, row = i % 4, i // 4
    x = MARGIN + col * (cw + Inches(0.11))
    y = BODY_Y + row * (ch + Inches(0.12))
    card(s, x, y, cw, ch, h, b, GREEN_PALE if i % 2 == 0 else WHITE, GREEN, INK, 13.5, CB, badge=i + 1)

# ===================================================================== 21 risks
s = new_slide("What could fool us", "And what in the design answers it", "6 · RISKS")
rows = [
    ["Threat", "Answer"],
    ["Goodhart on the library", "Held-out by lineage and date; surface variants"],
    ["Safety bought by refusal", "F ≤ α on benign twins; utility non-inferiority"],
    ["Observers change the count", "B1 vs B0 on the same trajectories"],
    ["Leakage to proposer or agent", "Strict partitions; aggregates only"],
    ["Poisoned reports", "Grades, quarantine, reproduction, human gate"],
    ["Non-transfer across models", "Repeat on a second model family"],
    ["Cost blow-up", "Search and replay budgets predeclared"],
]
table(s, MARGIN, BODY_Y, BODY_W, Inches(5.2), rows, [4.5, 6.5], size=15, first_col_bold=True)

# ===================================================================== 22 evaluation
s = new_slide("How we would know it worked", None, "6 · EVALUATION")
rows = [
    ["Benchmark", "Established baselines we compare against"],
    ["ImpossibleBench (Zhong et al., 2025)", "Upstream scaffold with its STOP instruction"],
    ["AgentDojo (Debenedetti et al., 2024)", "No defence, repeat-user-prompt, spotlighting, tool filter"],
    ["ResearchArena (2025)", "Upstream monitors; never-flag / always-flag controls"],
    ["BashArena in ControlArena (AISI, 2025)", "Untrusted-only, trusted monitoring, defer-to-trusted (Greenblatt et al., 2023)"],
    ["SHADE-Arena (Kutasov et al., 2025)", "Upstream monitor on the same transcripts"],
    ["Incident families reported after the cutoff", "Time-split stream; no baseline has seen them"],
]
table(s, MARGIN, BODY_Y, BODY_W, Inches(3.2), rows, [4.6, 6.4], size=13, first_col_bold=True)
card(s, MARGIN, Inches(4.85), Inches(6.05), Inches(2.0), "Endpoints and success", [
    "ΔR = R(B4) − R(B3) and ΔU, paired by task lineage, plus refusals and cost",
    "Success: fewer verified incidents at comparable utility on untouched data"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
card(s, Inches(7.0), Inches(4.85), Inches(5.83), Inches(2.0), "The main figure", [
    "x: task utility   y: verified incident rate; mark B0, B2, B3, B4",
    "No improving curve before data exist"], WHITE, BLUE, hsize=CH, bsize=CB)

# ===================================================================== 23 status
s = new_slide("Status and roadmap", None, "6 · STATUS")
card(s, MARGIN, BODY_Y, Inches(4.0), Inches(2.9), "Exists", [
    "Independent observers (native, container)", "Clause catalog and native optimizer", "Offline qualification; benchmark importers"], GREEN_PALE, GREEN, hsize=CH, bsize=CB)
card(s, Inches(4.67), BODY_Y, Inches(4.0), Inches(2.9), "Still needed for the core comparison", [
    "ImpossibleBench actor-environment repair", "Matched B3 vs B4 ablation", "Pre-registered splits and budgets"], ORANGE_PALE, ORANGE, hsize=CH, bsize=CB)
card(s, Inches(8.83), BODY_Y, Inches(4.0), Inches(2.9), "New in this design", [
    "Intake, library, synthesis", "Replay blame, action monitor", "Regression gate and release"], BLUE_PALE, BLUE, hsize=CH, bsize=CB)
rows = [["Phase", "Scope", "Model calls"],
        ["1", "Schema, library, own-run intake, splits", "No"],
        ["2", "Replay and synthesis on the local sandbox", "Small"],
        ["3", "Monitor in shadow mode; B3 vs B4 ablation", "Pre-registered"],
        ["4", "Web intake, time split, first signed release", "Yes"]]
table(s, MARGIN, Inches(4.55), BODY_W, Inches(2.3), rows, [1.0, 7.0, 2.0], size=14, first_col_bold=True)

# ===================================================================== 24 summary
s = new_slide("Summary", None, "SUMMARY")
big_bullets(s, MARGIN, BODY_Y, Inches(7.2), Inches(4.2), [
    "Incidents will keep happening; a scorer cannot see them, an observer can",
    "Each verified incident becomes an executable case with a benign twin",
    "A scheduled loop replays, revises and releases only what passes a regression gate and a human",
    "The frozen policy is judged on untouched tasks and on incidents reported after the cutoff",
], 18)
card(s, Inches(8.1), BODY_Y, Inches(4.73), Inches(4.2), "Decisions to make", [
    "Opt-in plugin first?", "First benchmark for B3 vs B4?", "Who qualifies shared cases?", "Budget for Phases 2 and 3?"], GREEN_PALE, GREEN, hsize=CH, bsize=CB)
band(s, Inches(5.95), "No benchmark-level safety or utility improvement has been measured. The figures are design overviews, not results.", Inches(0.9), YELLOW, 14)


# ===================================================================== 25 references
s = new_slide("References", None, "REFERENCES")
left = [
    "Greenblatt et al. (2023). AI Control: Improving Safety Despite Intentional Subversion. arXiv:2312.06942",
    "Bhatt et al. (2025). Ctrl-Z: Controlling AI Agents via Resampling. arXiv:2504.10374",
    "Kutasov et al. (2025). SHADE-Arena: Evaluating Sabotage and Monitoring in LLM Agents. arXiv:2506.15740",
    "Debenedetti et al. (2024). AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents. NeurIPS D&B",
    "Zhong, Raghunathan, Carlini (2025). ImpossibleBench: Measuring LLMs' Propensity of Exploiting Test Cases. arXiv:2510.20270",
    "ResearchArena (aisa-group, 2025). github.com/aisa-group/ResearchArena",
    "Baker et al. (2025). Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation. arXiv:2503.11926",
    "Slattery et al. (2024). The AI Risk Repository. MIT. arXiv:2408.12622",
]
right = [
    "UK AI Security Institute. Inspect AI: tool approval and approvers. inspect.aisi.org.uk",
    "UK AISI and Meridian Labs (2025). Inspect Scout: transcript analysis",
    "UK AISI (2025). ControlArena: monitors, micro-protocols, BashArena. control-arena.aisi.org.uk",
    "METR (2025). Hawk: run Inspect evals in the cloud. github.com/METR/hawk",
    "McGregor (2021). Preventing Repeated Real World AI Failures by Cataloging Incidents: The AI Incident Database. AAAI",
    "OECD (2023). AI Incident Monitor. MITRE ATLAS. OWASP Top 10 for LLM and Agentic Applications",
    "Perrow (1984). Normal Accidents. Reason (1990). Human Error. Taleb (2007). The Black Swan. Popper (1963). Conjectures and Refutations",
    "EU AI Act, Article 73. California SB 53 (2025)",
]
bullets(s, MARGIN, BODY_Y, Inches(6.1), Inches(5.4), left, 11, gap=5, line_spacing=1.05)
bullets(s, Inches(6.85), BODY_Y, Inches(6.0), Inches(5.4), right, 11, gap=5, line_spacing=1.05)

# ===================================================================== 27 incident references
s = new_slide("References: incidents", None, "REFERENCES")
left = [
    "Sakana AI (Aug 2024). The AI Scientist. sakana.ai/ai-scientist; coverage: Ars Technica",
    "OpenAI (Dec 2024). o1 System Card, Apollo Research scheming evaluations. cdn.openai.com/o1-system-card-20241205.pdf",
    "Palisade Research (Dec 2024, Feb 2025). o1-preview hacks its chess environment. x.com/PalisadeAI; MIT Technology Review",
    "Baker et al., OpenAI (Mar 2025). Monitoring Reasoning Models for Misbehavior. arXiv:2503.11926",
    "Palisade Research (May 2025). o3 sabotages shutdown in 7/100 runs. BleepingComputer, The Register",
    "Anthropic (May 2025). System Card: Claude Opus 4 and Sonnet 4. anthropic.com/claude-4-system-card",
    "Anthropic (Jun 2025). Agentic Misalignment: How LLMs Could Be Insider Threats",
]
right = [
    "Invariant Labs (May 2025). GitHub MCP private-repository exfiltration. github/github-mcp-server issue #844",
    "SaaStr / Replit (Jul 2025). Production database deleted during code freeze. Slashdot, Fortune",
    "AWS; 404 Media (Jul 2025). Amazon Q Developer extension 1.84.0 wiper prompt. SC Media",
    "AI Incident Database (Jul 2025). Incident 1178: Gemini CLI deletes user files. incidentdatabase.ai/cite/1178",
    "Brave Security (Aug 2025). Indirect prompt injection in Perplexity Comet. brave.com/blog",
    "OpenAI (Oct–Dec 2025). ChatGPT Atlas prompt-injection update. CyberScoop",
    "Anthropic (Nov 2025). Disrupting the first AI-orchestrated cyber espionage campaign (GTG-1002). AI Incident Database 1263",
]
bullets(s, MARGIN, BODY_Y, Inches(6.1), Inches(5.4), left, 11, gap=5, line_spacing=1.05)
bullets(s, Inches(6.85), BODY_Y, Inches(6.0), Inches(5.4), right, 11, gap=5, line_spacing=1.05)
OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(f"Saved {OUT.relative_to(ROOT)} with {len(prs.slides)} slides")
