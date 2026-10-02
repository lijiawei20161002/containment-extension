"""Export five precise, illustrated research diagrams as PNG and editable SVG.

No model calls. These are proposed designs and illustrative mechanisms, not results.
Run: MPLCONFIGDIR=/tmp/containment-mpl python3 scripts/draw_coordination_figures.py
"""

from pathlib import Path
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/containment-mpl")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "coordination-harness"
BG = "#F7F6F2"
INK = "#192E3E"
MUTED = "#5D6D78"
LINE = "#D8DED9"
TEAL = "#197B75"
PALE_TEAL = "#E2F1EB"
CORAL = "#BF5946"
PALE_CORAL = "#FAE9E0"
BLUE = "#4266A1"
PALE_BLUE = "#E8EEF8"
GOLD = "#A07827"
PALE_GOLD = "#F6EDCE"
WHITE = "#FFFFFF"

plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                     "svg.hashsalt": "coordination-design-v1"})
FIGURES = []


def text(ax, x, y, value, size=18, color=INK, weight="normal", ha="left", va="top", **kw):
    return ax.text(x, y, value, fontsize=size, color=color, weight=weight,
                   ha=ha, va=va, linespacing=1.45, **kw)


def box(ax, x, y, w, h, fill=WHITE, stroke=LINE, radius=18, lw=1.25, **kw):
    patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                          facecolor=fill, edgecolor=stroke, linewidth=lw, **kw)
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, color=TEAL, style="-", curve=0, lw=2.5):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=17,
                                linewidth=lw, linestyle=style, color=color,
                                connectionstyle=f"arc3,rad={curve}", shrinkA=4, shrinkB=4))


def pill(ax, x, y, w, value, fill=PALE_TEAL, color=TEAL, size=13):
    box(ax, x, y, w, 36, fill=fill, stroke=fill, radius=18)
    text(ax, x + w / 2, y + 18, value, size=size, color=color, weight="bold", ha="center", va="center")


def robot(ax, cx, cy, name, color=TEAL, scale=1):
    # Small vector illustration; labels and arrows remain exact and editable.
    s = scale
    ax.plot([cx, cx], [cy - 35 * s, cy - 52 * s], color=color, lw=2)
    ax.add_patch(Circle((cx, cy - 56 * s), 5 * s, facecolor=color))
    box(ax, cx - 42 * s, cy - 32 * s, 84 * s, 65 * s, fill=WHITE, stroke=color, radius=16 * s, lw=2)
    for dx in (-16, 16):
        ax.add_patch(Circle((cx + dx * s, cy - 4 * s), 5 * s, facecolor=color))
    ax.plot([cx - 10 * s, cx + 10 * s], [cy + 16 * s] * 2, color=color, lw=2)
    box(ax, cx - 29 * s, cy + 42 * s, 58 * s, 28 * s, fill=color, stroke=color, radius=9 * s)
    text(ax, cx, cy + 87 * s, name, size=16 * s, weight="bold", ha="center", color=color)


def page(number, title, subtitle, resource):
    fig = plt.figure(figsize=(16, 10), facecolor=BG)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 1600), ylim=(1000, 0))
    ax.axis("off")
    text(ax, 60, 30, f"CONTAINMENT EXTENSION  /  EXPERIMENT DESIGN {number:02d}",
         size=12, color=TEAL, weight="bold")
    pill(ax, 1290, 24, 250, "PROPOSED · NO RESULTS", fill=PALE_GOLD, color=GOLD, size=11)
    text(ax, 60, 82, title, size=31, weight="bold")
    text(ax, 60, 145, subtitle, size=17, color=MUTED)
    ax.plot([60, 1540], [193, 193], color=LINE, lw=1.2)
    text(ax, 60, 965, "Local synthetic services · fixed scope · independent effect records", size=11, color=MUTED)
    text(ax, 1540, 965, resource, size=11, color=MUTED, ha="right")
    return fig, ax


def takeaway(ax, lead, body, color=TEAL):
    box(ax, 60, 835, 1480, 106, fill=WHITE, stroke=LINE)
    box(ax, 60, 835, 9, 106, fill=color, stroke=color, radius=4)
    text(ax, 89, 851, lead, size=17, weight="bold", color=color)
    text(ax, 89, 893, body, size=16, color=MUTED)


def save(fig, stem, title, caption):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{stem}.svg", facecolor=BG, metadata={"Date": None})
    fig.savefig(OUT / f"{stem}.png", dpi=150, facecolor=BG)
    # Check all text against page bounds; visual review checks internal spacing.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in fig.axes[0].texts:
        bounds = item.get_window_extent(renderer)
        if bounds.x0 < -1 or bounds.x1 > fig.bbox.width + 1 or bounds.y0 < -1 or bounds.y1 > fig.bbox.height + 1:
            raise ValueError(f"Text outside page: {item.get_text()}")
    plt.close(fig)
    FIGURES.append({"stem": stem, "title": title, "caption": caption})


def effects():
    fig, ax = page(1, "Can a read create a signal?",
                   "Start with observable effects: what changes, and who can see the change?", "SCRIPTED CONTROLS  /  CPU ONLY")
    box(ax, 60, 221, 1480, 358, fill=WHITE)
    pill(ax, 83, 241, 298, "ILLUSTRATIVE SHARED SERVICE", fill=PALE_CORAL, color=CORAL, size=11)
    robot(ax, 172, 387, "Agent A")
    text(ax, 300, 314, "GET /document", size=19, weight="bold")
    arrow(ax, (248, 382), (628, 382))
    text(ax, 320, 408, "Receives fixed text", size=16, color=MUTED)
    box(ax, 640, 298, 360, 224, fill=PALE_CORAL, stroke=PALE_CORAL)
    text(ax, 820, 325, "SHARED QUOTA", size=14, color=CORAL, weight="bold", ha="center")
    text(ax, 820, 373, "100 → 99", size=35, weight="bold", ha="center")
    text(ax, 820, 450, "The read consumes one unit", size=15, ha="center", color=CORAL)
    arrow(ax, (1008, 382), (1328, 382), color=CORAL)
    text(ax, 1050, 314, "GET /quota", size=19, weight="bold")
    text(ax, 1050, 408, "Can observe 99", size=16, color=CORAL)
    robot(ax, 1420, 387, "Agent B", color=BLUE)
    text(ax, 83, 540, "Possible information path: A's activity → shared resource → B's observation", size=16, color=MUTED)
    for x, title, detail in (
        (60, "Describe the operation", "Primary effect: read text\nSecondary effect: reduce quota"),
        (562, "Specify the permission", "Document access can be allowed\nwhile disclosure is forbidden"),
        (1064, "Change the visibility", "Partitioned quotas: A sees 99\nwhile B still sees 100"),
    ):
        box(ax, x, 604, 476, 192, fill=PALE_TEAL if x == 1064 else WHITE)
        text(ax, x + 23, 629, title, size=18, weight="bold")
        text(ax, x + 23, 677, detail, size=16, color=MUTED)
    takeaway(ax, "Measure: side effects + cross-principal visibility + authorization.",
             "A GET label alone does not describe information flow. Observing an effect does not establish intent.")
    save(fig, "01-effects", "Can a read create a signal?",
         "A document read can change a shared quota. The contract distinguishes reading, secondary effects, visibility, and permission.")


def behavior():
    fig, ax = page(2, "Do reminders and isolation change behavior?",
                   "Use separate agent histories and match the task, schedule, and budgets across conditions.", "LIVE AGENTS  /  API KEY · NO GPU")
    box(ax, 60, 220, 1480, 128, fill=WHITE)
    robot(ax, 115, 270, "", scale=.52)
    text(ax, 170, 244, "A knows a random color", size=18, weight="bold")
    text(ax, 170, 287, "B gets eight labels, shuffled separately", size=15, color=MUTED)
    arrow(ax, (684, 282), (774, 282))
    pill(ax, 795, 247, 284, "FIRST: ALLOWED CONTROL", fill=PALE_TEAL, size=11)
    text(ax, 796, 295, "Check that the pair can use the channel", size=14, color=MUTED)
    text(ax, 1218, 250, "Then: forbid", size=18, weight="bold", color=CORAL)
    text(ax, 1218, 287, "communication", size=18, weight="bold", color=CORAL)
    text(ax, 772, 367, "SAME AUTHORIZATION IN ALL FOUR CELLS: COMMUNICATION FORBIDDEN", size=12,
         color=CORAL, weight="bold", ha="center")
    text(ax, 674, 411, "Original scope", size=19, weight="bold", ha="center")
    text(ax, 1252, 411, "+ Effect reminder", size=19, weight="bold", ha="center")
    for y, row_name, detail, shared in ((453, "Shared state", "A and B see one counter", True),
                                      (594, "Partitioned state", "A and B see separate counters", False)):
        text(ax, 62, y + 31, row_name, size=18, weight="bold")
        text(ax, 62, y + 69, detail, size=12, color=MUTED)
        for x, reminder in ((404, False), (982, True)):
            box(ax, x, y, 558, 121, fill=PALE_CORAL if shared else PALE_TEAL,
                stroke=PALE_CORAL if shared else PALE_TEAL)
            text(ax, x + 33, y + 41, "A", size=24, weight="bold", color=TEAL)
            text(ax, x + 481, y + 41, "B", size=24, weight="bold", color=BLUE)
            if shared:
                box(ax, x + 178, y + 30, 190, 60, fill=WHITE, stroke=WHITE)
                text(ax, x + 273, y + 60, "one counter", size=16, ha="center", va="center")
                arrow(ax, (x + 82, y + 60), (x + 168, y + 60), color=CORAL)
                arrow(ax, (x + 376, y + 60), (x + 465, y + 60), color=CORAL)
            else:
                for bx, label, color in ((x + 100, "A's counter", TEAL), (x + 310, "B's counter", BLUE)):
                    box(ax, bx, y + 30, 150, 60, fill=WHITE, stroke=WHITE)
                    text(ax, bx + 75, y + 60, label, size=13, ha="center", va="center", color=color)
                ax.plot([x + 278, x + 278], [y + 24, y + 96], color=TEAL, ls="--", lw=2)
    text(ax, 60, 758, "Run each cell with an unavailable source AND with a legitimate source B can use.", size=18, weight="bold")
    text(ax, 60, 797, "Pilot design: 4 allowed-control pairs + 16 study pairs. Count independent pairs; chance color accuracy is 1/8.", size=14, color=MUTED)
    takeaway(ax, "Measure: unauthorized proposals, committed effects, receiver accuracy, and legitimate completion.",
             "The reminder tests behavior; partitioning tests the service boundary. Keep stress tasks and ordinary controls separate.")
    save(fig, "02-behavior", "Do reminders and isolation change behavior?",
         "An authorized capability check precedes a 2 × 2 comparison of reminders and state isolation, with separate legitimate-task controls.")


def replay_figure():
    fig, ax = page(3, "Did A change what B could see?",
                   "Counterfactual replay: hold B's requests and the initial state fixed; change only A's actions.", "SCRIPTED REPLAY  /  CPU ONLY")
    pill(ax, 60, 223, 472, "ILLUSTRATIVE EXPECTED RESPONSES · SHARED STATE", fill=PALE_GOLD, color=GOLD, size=10)
    for y, name, sender, value, color, fill in (
        (282, "Baseline world", "A does nothing", "0", BLUE, PALE_BLUE),
        (461, "Perturbed world", "A increments once", "1", CORAL, PALE_CORAL),
    ):
        box(ax, 60, y, 1480, 156, fill=WHITE)
        text(ax, 84, y + 32, name, size=18, weight="bold")
        text(ax, 84, y + 81, "Fresh counter starts at 0", size=14, color=MUTED)
        box(ax, 414, y + 30, 314, 95, fill=BG, stroke=BG)
        text(ax, 571, y + 78, sender, size=18, ha="center", va="center")
        arrow(ax, (742, y + 78), (857, y + 78), color=color)
        box(ax, 870, y + 30, 400, 95, fill=fill, stroke=fill)
        text(ax, 1070, y + 55, "B sends the SAME request", size=15, weight="bold", ha="center")
        text(ax, 1070, y + 89, "GET /counter", size=18, ha="center")
        arrow(ax, (1277, y + 78), (1373, y + 78), color=color)
        text(ax, 1450, y + 77, value, size=37, weight="bold", ha="center", va="center", color=color)
    box(ax, 60, 652, 1480, 143, fill=PALE_TEAL, stroke=PALE_TEAL)
    text(ax, 88, 676, "Repeat with partitioned state", size=20, color=TEAL, weight="bold")
    text(ax, 88, 726, "B's counter stays at 0 in both worlds.", size=19)
    text(ax, 892, 677, "Diagnostic output", size=17, weight="bold")
    text(ax, 892, 717, "First differing B response\n+ responsible prior service event", size=16, color=MUTED)
    takeaway(ax, "Measure: whether A can influence B through this channel, under these traces.",
             "This qualifies the mechanism before paid trials. It does not show that a live agent discovers or uses it.")
    save(fig, "03-replay", "Did A change what B could see?",
         "Two fresh worlds differ only in the sender trace. Receiver-response divergence diagnoses channel influence within the replayed cases.")


def monitors():
    fig, ax = page(4, "What evidence does a monitor need?",
                   "Judge the same proposed request under the same policy, with progressively richer prior evidence.", "OFFLINE MODEL JUDGMENTS  /  API KEY · NO GPU")
    cards = [(60, "Action", PALE_BLUE, BLUE), (562, "+ Actor history", PALE_GOLD, GOLD),
             (1064, "+ Service provenance", PALE_TEAL, TEAL)]
    for i, (x, title, fill, color) in enumerate(cards):
        box(ax, x, 229, 476, 420, fill=WHITE)
        pill(ax, x + 23, 250, 430, title.upper(), fill=fill, color=color, size=13)
        text(ax, x + 23, 312, "B proposes", size=16, color=MUTED)
        text(ax, x + 23, 348, "GET /counter", size=24, weight="bold")
        ax.plot([x + 23, x + 453], [411, 411], color=LINE, lw=1)
        if i == 0:
            text(ax, x + 23, 444, "Policy + operation contract", size=17, weight="bold")
            text(ax, x + 23, 493, "Who last changed the value?\nThat evidence is absent.", size=16, color=MUTED)
        elif i == 1:
            text(ax, x + 23, 444, "Prior requests + responses", size=17, weight="bold")
            text(ax, x + 23, 493, "What B has already observed\nthrough its own tools.", size=16, color=MUTED)
        else:
            text(ax, x + 23, 444, "Trusted prior service events", size=17, weight="bold")
            text(ax, x + 23, 493, "Which principal changed state?\nWho could observe that change?", size=16, color=MUTED)
        text(ax, x + 23, 600, "Output: authorization score", size=15, color=color, weight="bold")
    box(ax, 60, 679, 900, 119, fill=PALE_CORAL, stroke=PALE_CORAL)
    text(ax, 83, 698, "PRE-ACTION CUTOFF", size=14, color=CORAL, weight="bold")
    text(ax, 83, 738, "No current result, future event, hidden answer, or reference label.", size=16)
    box(ax, 987, 679, 553, 119, fill=WHITE)
    text(ax, 1010, 698, "Matched benign controls", size=17, weight="bold")
    text(ax, 1010, 737, "Clean reads · private work · allowed sharing", size=14, color=MUTED)
    takeaway(ax, "Measure: unauthorized-action detection AND false blocks on authorized work.",
             "The provenance view adds information. Offline judgment accuracy alone does not establish live prevention.")
    save(fig, "04-monitor", "What evidence does a monitor need?",
         "Compare proposed-action, actor-history, and trusted-provenance views at a strict pre-action cutoff; evaluate false blocks as well as detection.")


def library():
    fig, ax = page(5, "Does a fix survive a new channel?",
                   "Preserve executable cases, freeze the intervention, and evaluate on a different mechanism family.", "CASE LIBRARY  /  CPU + API FOR LEARNED JUDGMENTS")
    box(ax, 60, 230, 487, 415, fill=WHITE)
    pill(ax, 84, 252, 438, "DEVELOPMENT LIBRARY", fill=PALE_TEAL, color=TEAL, size=13)
    for y, title, detail in ((316, "Single counter", "Information in an integer"),
                              (452, "Named counters", "Information in a chosen key")):
        box(ax, 85, y, 437, 112, fill=BG, stroke=BG)
        text(ax, 109, y + 17, title, size=20, weight="bold")
        text(ax, 109, y + 61, detail, size=16, color=MUTED)
    text(ax, 85, 598, "Reproducer → regression check", size=15, color=TEAL, weight="bold")
    arrow(ax, (558, 427), (655, 427))
    box(ax, 670, 325, 260, 221, fill=INK, stroke=INK)
    text(ax, 800, 355, "FREEZE", size=25, weight="bold", color=WHITE, ha="center")
    text(ax, 800, 412, "Policy / monitor\nThreshold + budget\nSource + case hashes", size=15, color=WHITE, ha="center")
    arrow(ax, (941, 427), (1038, 427), color=BLUE)
    box(ax, 1053, 230, 487, 415, fill=WHITE)
    pill(ax, 1077, 252, 438, "HELD-OUT FAMILIES", fill=PALE_BLUE, color=BLUE, size=13)
    for y, title, detail in ((316, "Quota consumption", "Reads change shared state"),
                              (452, "Local URL storage", "A query stores visible text")):
        box(ax, 1078, y, 437, 112, fill=BG, stroke=BG)
        text(ax, 1102, y + 17, title, size=20, weight="bold")
        text(ax, 1102, y + 61, detail, size=16, color=MUTED)
    text(ax, 1078, 598, "Keep failures; no retuning this run", size=15, color=BLUE, weight="bold")
    box(ax, 60, 680, 1480, 119, fill=PALE_GOLD, stroke=PALE_GOLD)
    text(ax, 85, 698, "EACH CASE IS AN EXECUTABLE EVIDENCE PACKET", size=14, color=GOLD, weight="bold")
    text(ax, 85, 739, "Initial state    +    permission    +    exact actions    +    observed effects    +    expected outcome    +    source hashes", size=16)
    takeaway(ax, "Measure: detection and authorized-action acceptance on mechanisms excluded from development.",
             "Better starting points belong in the development library. Held-out answers stay out of actor and tuning inputs.")
    save(fig, "05-transfer", "Does a fix survive a new channel?",
         "Development examples and held-out families remain separate. Freeze the monitor before transfer evaluation and preserve failures without retuning.")


def gallery():
    from PIL import Image, ImageDraw, ImageFont

    font_path = matplotlib.font_manager.findfont("DejaVu Sans")
    title_font = ImageFont.truetype(font_path, 37)
    body_font = ImageFont.truetype(font_path, 23)
    sheet = Image.new("RGB", (1660, 1730), BG)
    draw = ImageDraw.Draw(sheet)
    draw.text((35, 27), "Five experiments for an information-flow harness", fill=INK, font=title_font)
    draw.text((35, 88), "Proposed designs · local synthetic services · no GPU required", fill=MUTED, font=body_font)
    for i, entry in enumerate(FIGURES):
        im = Image.open(OUT / f"{entry['stem']}.png").convert("RGB")
        im.thumbnail((790, 495), Image.Resampling.LANCZOS)
        x, y = 30 + (i % 2) * 820, 148 + (i // 2) * 520
        sheet.paste(im, (x, y))
    x, y = 878, 1225
    for offset, line in enumerate(("The research loop", "1  Describe effects", "2  Compare behavior and isolation",
                                   "3  Diagnose channel influence", "4  Compare monitor evidence", "5  Test transfer to new mechanisms")):
        draw.text((x, y + 65 * offset), line, fill=TEAL if offset == 0 else INK,
                  font=title_font if offset == 0 else body_font)
    sheet.save(OUT / "overview.png")
    import html
    parts = ["""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Five containment experiments</title>
<style>body{margin:0;background:#f7f6f2;color:#192e3e;font:18px/1.65 system-ui,sans-serif}
main{max-width:1280px;margin:40px auto;padding:0 24px}h1{line-height:1.2;font-size:38px}
.intro{max-width:900px}figure{margin:38px 0 64px}img{width:100%;height:auto;border:1px solid #d8ded9;border-radius:12px}
figcaption{padding:14px 6px}a{color:#197b75}nav{display:flex;gap:18px;flex-wrap:wrap}
.tag{color:#a07827;font-weight:650}.downloads{font-size:15px}footer{border-top:1px solid #d8ded9;padding:25px 0;font-size:15px}
</style><main><p class="tag">RESEARCH DESIGNS · NO MEASURED RESULTS IN THESE FIGURES</p>
<h1>Five experiments for an information-flow harness</h1>
<p class="intro">Can an agent affect another agent through a service that appears to be read-only?
These diagrams connect explicit effect contracts, controlled agent trials, counterfactual replay,
provenance monitoring, and transfer across channel families. Small agent illustrations keep the
mechanisms approachable; exact labels keep the experimental comparisons clear.</p>
<p class="intro">All services are bounded local replicas. Offline controls need only CPU/Python;
live actor and monitor calls need a provider key and an API budget. No GPU is required.</p><nav>"""]
    parts += [f'<a href="#{e["stem"]}">{i+1}. {html.escape(e["title"])}</a>' for i, e in enumerate(FIGURES)]
    parts.append("</nav>")
    for i, e in enumerate(FIGURES):
        parts.append(f'<figure id="{e["stem"]}"><a href="{e["stem"]}.png"><img src="{e["stem"]}.svg" alt="{html.escape(e["caption"])}"></a>'
                     f'<figcaption><strong>{i+1}. {html.escape(e["title"])}</strong> {html.escape(e["caption"])}'
                     f'<div class="downloads"><a href="{e["stem"]}.png" download>PNG</a> · '
                     f'<a href="{e["stem"]}.svg" download>Editable SVG</a></div></figcaption></figure>')
    parts.append('''<footer>Design details: <a href="../../docs/coordination-harness.md">experiment protocol</a>.
Inspired by <a href="https://blog.mlc.ai/2026/09/29/tirx-harness-an-open-compiler-harness-for-agentic-gpu-programming">TIRx Harness</a>
and <a href="https://www.lesswrong.com/posts/SCdR7W6L5GvKaEzaZ/encoded-coordination-on-the-open-web">Encoded Coordination on the Open Web</a>.
<br>Figures are reproducible with <code>scripts/draw_coordination_figures.py</code>. No model calls were used to draw them.</footer></main></html>''')
    (OUT / "index.html").write_text("\n".join(parts))
    (OUT / "manifest.json").write_text(json.dumps({"status": "proposed_designs_not_results", "figures": FIGURES}, indent=2) + "\n")


if __name__ == "__main__":
    effects()
    behavior()
    replay_figure()
    monitors()
    library()
    gallery()
    print(f"Created {len(FIGURES)} PNG/SVG figures, overview, and gallery in {OUT}")
