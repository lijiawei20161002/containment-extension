"""Draw the v2 incident-aware optimization overview: history -> replay -> policy.

Extends figures/incident-optimization-overview-v1 with the incident intake,
history library, case synthesis, counterfactual replay, action monitor, and
versioned release stages. Vector primitives in the same overview.png style.
No model calls. Run: python3 scripts/draw_incident_optimization_overview_v2.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/containment-evaluation-mpl")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/incident-optimization-overview-v2"
TITLE = "Incident-aware policy optimization v2: from incident history to safer agent policies"
C = {
    "ink": "#111111", "blue": "#365E9E", "arrow_blue": "#4679BC",
    "blue_dark": "#325F9E", "blue_light": "#BDD8ED", "blue_pale": "#EDF4FB",
    "yellow": "#FFF2CC", "yellow_top": "#FFF9E9", "white": "#FFFFFF",
    "gray": "#666666", "line": "#8C8C8C", "red": "#B34831", "red_pale": "#FBEFEC",
    "green": "#2E7D5B", "green_pale": "#EAF5EF", "orange": "#B8732A",
    "orange_pale": "#FDF3E7",
}
plt.rcParams.update({
    "font.family": ["Arial", "DejaVu Sans"], "mathtext.fontset": "dejavusans",
    "svg.fonttype": "none", "svg.hashsalt": "incident-optimization-overview-v2",
})


def main():
    sources = [ROOT / path for path in (
        "docs/incident-aware-optimization.md",
        "docs/counterfactual-replay.md",
        "docs/counterfactual-evaluation-infrastructure.md",
        "experiments/incident-aware-optimization-v1.design.json",
        "figures/incident-optimization-overview-v1/metadata.json",
    )]
    design = json.loads(sources[3].read_text())
    assert design["primary_contrast"] == ["B4", "B3"]
    assert design["optimization"]["adaptive_loop"]["heldout_feedback"] is False

    W, H = 1920, 1230
    fig = plt.figure(figsize=(W / 100, H / 100), facecolor="white")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, W), ylim=(H, 0))
    ax.axis("off")

    def text(x, y, value, size=15, color="ink", bold=False, ha="left", va="top", z=10):
        return ax.text(x, y, value, fontsize=size, color=C[color],
                       fontweight="bold" if bold else "normal", ha=ha, va=va,
                       linespacing=1.25, zorder=z)

    def box(x, y, w, h, radius=8, fill="white", edge="ink", lw=1, dashed=False, z=3):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
            fc=C[fill], ec=C[edge], lw=lw,
            linestyle=(0, (3, 3)) if dashed else "-", zorder=z))

    def line(points, color="ink", lw=1.9, z=4, dashed=False):
        ax.plot([p[0] for p in points], [p[1] for p in points],
                color=C[color], lw=lw, solid_capstyle="butt", zorder=z,
                linestyle=(0, (5, 4)) if dashed else "-")

    def arrow(points, color="ink", lw=1.9, scale=16, dashed=False):
        if len(points) > 2:
            line(points[:-1], color, lw, dashed=dashed)
        ax.add_patch(FancyArrowPatch(
            points[-2], points[-1], arrowstyle="-|>", mutation_scale=scale,
            shrinkA=0, shrinkB=0, lw=lw, color=C[color], zorder=4,
            linestyle=(0, (5, 4)) if dashed else "-"))

    def papers(x, y, w=55, h=36, count=5):
        for i in range(count):
            dx, dy = i * 9, i * 6
            fill = "blue_light" if i % 2 == 0 else "white"
            ax.add_patch(Rectangle((x + dx, y + dy), w, h,
                                   fc=C[fill], ec=C["blue"], lw=0.9, zorder=6 + i / 10))

    def cylinder(x, y, w, h, label, size=16, sub=None):
        depth = 27
        ax.add_patch(Ellipse((x + w / 2, y + h - depth / 2), w, depth,
                             fc=C["yellow"], ec=C["ink"], lw=1, zorder=5))
        ax.add_patch(Rectangle((x, y + depth / 2), w, h - depth,
                               fc=C["yellow"], ec="none", zorder=6))
        line([(x, y + depth / 2), (x, y + h - depth / 2)], lw=1, z=7)
        line([(x + w, y + depth / 2), (x + w, y + h - depth / 2)], lw=1, z=7)
        ax.add_patch(Ellipse((x + w / 2, y + depth / 2), w, depth,
                             fc=C["yellow_top"], ec=C["ink"], lw=1, zorder=7))
        if sub is None:
            text(x + w / 2, y + h / 2 + 7, label, size, ha="center", va="center")
        else:
            text(x + w / 2, y + depth + 10, label, size, ha="center", va="top")
            text(x + w / 2, y + depth + 40, sub, 10, "blue", ha="center", va="top")

    def badge(x, y, number, color="blue"):
        ax.add_patch(Ellipse((x, y), 26, 26, fc=C[color], ec="none", zorder=9))
        text(x, y + 1, str(number), 13, "white", True, "center", "center", z=11)

    def rotating_arrow(cx, cy, start, end, color):
        rx, ry, width, head_width = 70, 30, 10, 26
        head_base = end - 22

        def point(degrees, offset=0):
            angle = math.radians(degrees)
            cosine, sine = math.cos(angle), math.sin(angle)
            nx, ny = ry * cosine, rx * sine
            length = math.hypot(nx, ny)
            return (cx + rx * cosine + offset * nx / length,
                    cy + ry * sine + offset * ny / length)

        angles = [start + (head_base - start) * i / 60 for i in range(61)]
        points = [point(a, width / 2) for a in angles]
        points += [point(head_base, head_width / 2), point(end),
                   point(head_base, -head_width / 2)]
        points += [point(a, -width / 2) for a in reversed(angles)]
        ax.add_patch(Polygon(points, closed=True, fc=C[color], ec="#849DC0", lw=0.65, zorder=6))

    # ---- objective ---------------------------------------------------------
    text(W / 2, 26, "Goal: every past incident becomes a permanent improvement to tasks, monitors and instructions",
         21, bold=True, ha="center")
    text(W / 2, 70,
         r"$\theta^*=\arg\min_{\theta\in\Theta}\,R(\theta)"
         r"\quad\mathrm{s.t.}\quad U(\theta)\geq U_0-\delta_U,"
         r"\quad C(\theta)\leq B,\quad F(\theta)\leq\alpha,"
         r"\quad \mathrm{Reg}(\theta)=0$",
         19, ha="center")
    text(W / 2, 120,
         "θ: instructions + monitor rules    R: verified incident rate    U: task success    "
         "C: cost    F: false refusals    Reg: regressions on library cases",
         12, "gray", ha="center")

    # ---- group 1: intake and history --------------------------------------
    g1y, g1h = 165, 230
    box(50, g1y, 1800, g1h, radius=26, dashed=True, z=1)
    badge(78, g1y + 20, 1)
    text(98, g1y + 9, "Incident intake & history library", 18, bold=True)
    text(1830, g1y + 12, "researcher tooling · never visible to the evaluated agent", 11, "gray", ha="right")

    box(80, 225, 300, 120)
    text(230, 236, "Incident sources", 15, bold=True, ha="center")
    text(230, 264, "own Inspect logs via Scout scanners\n"
                   "public: AIID · OECD AIM · MIT AI Risk\n"
                   "Repository · postmortems · advisories",
         10, "blue", ha="center")
    arrow([(380, 285), (430, 285)])

    box(430, 225, 310, 120)
    text(585, 236, "Intake agent", 15, bold=True, ha="center")
    text(585, 264, "normalize to incident schema · taxonomy\n"
                   "(MITRE ATLAS, OWASP agentic) · fingerprint\n"
                   "evidence grade A / B / C · dedupe\n"
                   "provenance kept · unverified → quarantine",
         10, "blue", ha="center")
    arrow([(740, 285), (790, 285)])

    box(790, 240, 180, 90, fill="red_pale", edge="red")
    text(880, 250, "Human review gate", 13.5, "red", True, "center")
    text(880, 274, "accept / reject / defer\nblocks poisoned or\nfabricated reports", 10, "red", ha="center")
    arrow([(970, 285), (1020, 285)])

    cylinder(1020, 213, 250, 142, "Incident library (history)", 14,
             sub="versioned executable cases\nbenign twins · dev / held-out\nsplit by lineage and by date")
    arrow([(1270, 285), (1320, 285)])

    box(1320, 225, 500, 120)
    text(1570, 236, "Case synthesis & qualification", 15, bold=True, ha="center")
    text(1570, 264, "narrative → sandboxed reproduction → matched family\n"
                    "(feasible / impossible / broken env) + legitimate twin\n"
                    "reference replay · negative-label evidence · env check",
         10, "blue", ha="center")

    # ---- group 2: development rollouts ------------------------------------
    g2y, g2h = 490, 230
    box(50, g2y, 1800, g2h, radius=26, dashed=True, z=1)
    badge(78, g2y + 20, 2)
    text(98, g2y + 9, "Development rollouts & evaluation", 18, bold=True)
    text(1830, g2y + 12, "Inspect runs the agent; the extension observes", 11, "gray", ha="right")

    box(120, 560, 240, 70)
    text(240, 572, "Inspect agent", 17, ha="center")
    text(240, 602, "fixed model · candidate θ", 11.5, "blue", ha="center")
    arrow([(360, 595), (425, 595)])
    papers(372, 570, 28, 20, 3)
    text(392, 636, "tool calls", 11.5, "blue", True, "center")

    box(425, 545, 290, 98, fill="green_pale", edge="green")
    text(570, 553, "Action monitor", 15, "green", True, "center")
    text(570, 578, "Inspect approver · ControlArena monitors\nscope contract + incident signatures +\ncalibrated monitor · shadow/flag/defer/block",
         9.8, "green", ha="center")
    arrow([(715, 595), (765, 595)])

    box(765, 556, 290, 78)
    text(910, 564, "Sandbox & tools", 16, ha="center")
    text(910, 594, "ImpossibleBench · AgentDojo · ControlArena\nqualified development cases from the library", 9.8, "blue", ha="center")

    box(1110, 546, 310, 42)
    text(1265, 567, "Task metrics (U, C, F)", 14.5, ha="center", va="center")
    box(1110, 604, 310, 42, fill="blue_pale", edge="blue")
    text(1265, 625, "Incident observer (R)", 14.5, "blue", True, "center", "center")
    text(1265, 654, "independent effect witnesses · outside agent authority", 10, "blue", ha="center")
    line([(1055, 595), (1070, 595)])
    arrow([(1070, 595), (1070, 567), (1110, 567)])
    arrow([(1070, 595), (1070, 625), (1110, 625)])
    line([(1420, 567), (1458, 567), (1458, 625), (1420, 625)])
    arrow([(1458, 596), (1540, 596)])

    cylinder(1540, 540, 210, 112, "Trial\nevidence", 15)
    text(1645, 662, "transcripts · effects · costs · monitor verdicts", 10, "blue", ha="center")

    # library -> monitor signatures; synthesis -> development tasks
    arrow([(1060, 355), (1060, 425), (570, 425), (570, 545)], "blue", 1.6, dashed=True)
    text(815, 406, "incident signatures with provenance", 11, "blue", True, "center")
    arrow([(1570, 345), (1570, 462), (910, 462), (910, 556)], "blue", 1.6)
    text(1235, 441, "qualified development cases (held-out families locked)", 11, "blue", True, "center")

    # ---- group 3: diagnosis, optimization, release ------------------------
    g3y, g3h = 820, 230
    box(50, g3y, 1800, g3h, radius=26, dashed=True, z=1)
    badge(78, g3y + 20, 3)
    text(98, g3y + 9, "Diagnosis, policy optimization & versioned release", 18, bold=True)
    text(1830, g3y + 12, "development feedback only", 11, "gray", ha="right")

    arrow([(1645, 652), (1645, 880)])
    text(1660, 790, "feedback", 12, "blue", True)

    box(1475, 880, 345, 105)
    text(1647, 890, "Counterfactual replay", 15, bold=True, ha="center")
    text(1647, 916, "same checkpoint, one change →\nfirst differing observation → minimal\ntrigger → blame a clause, cue or tool",
         10, "blue", ha="center")
    arrow([(1475, 932), (1420, 932)])

    box(1040, 880, 380, 105)
    text(1230, 890, "Select eligible lowest-incident θ", 15, bold=True, ha="center")
    text(1230, 916, "U ≥ U₀ − δ,   C ≤ B,   F ≤ α\nincident feedback (B4) vs proxy feedback (B3)\nmissing outcomes stay unknown",
         10, "blue", ha="center")
    arrow([(1040, 932), (985, 932)])

    box(635, 880, 350, 105)
    text(810, 890, "Revise clauses & monitor rules", 15, bold=True, ha="center")
    text(810, 916, "grounded clause catalog, no free text\nthresholds from benign calibration only\nproposer sees aggregates, never test data",
         10, "blue", ha="center")
    arrow([(635, 932), (580, 932)])

    box(230, 880, 350, 105, fill="red_pale", edge="red")
    text(405, 890, "Regression gate + human approval", 15, "red", True, "center")
    text(405, 916, "replay every library case: Reg(θ) = 0\nsigned release vN: instructions + rules +\neval pack · changelog · rollback",
         10, "red", ha="center")

    # release returns to the agent and the monitor
    arrow([(230, 932), (100, 932), (100, 595), (120, 595)])
    papers(118, 738, 40, 26, 4)
    text(205, 742, "Release vN\ninstructions + monitor rules", 12, "blue", True)

    # replay results return to the library through qualification
    arrow([(1820, 932), (1880, 932), (1880, 285), (1820, 285)], "blue", 1.6, dashed=True)
    text(1897, 610, "new executable cases + blame records", 10.5, "blue", True, "center", "center",
         ).set_rotation(90)

    # rotation symbol in the gap between rollouts and optimization
    text(880, 770, "Automatic update loop", 14, "blue", True, "right", "center")
    rotating_arrow(960, 770, -82, 88, "blue_dark")
    rotating_arrow(960, 770, 98, 268, "arrow_blue")
    text(1050, 756, "ingest → synthesize → run → diagnose → revise → gate → release", 11.5, "blue")
    text(1050, 778, "scheduled; each release carries evidence per changed clause", 10.5, "gray")

    # ---- exit: frozen policy to held-out ----------------------------------
    arrow([(1230, 985), (1230, 1112), (1330, 1112)])
    text(1245, 1000, r"Freeze $\theta^*$", 14, "blue", True)
    box(1330, 1070, 490, 84)
    text(1575, 1078, "Held-out evaluation", 15, ha="center")
    text(1575, 1102, "ImpossibleBench · AgentDojo · ResearchArena · BashArena · SHADE-Arena\n"
                     "+ incident families reported after date T · same observer\n"
                     "baselines: AI Control protocols, AgentDojo defences · no test feedback",
         9.5, "blue", ha="center")
    text(1575, 1162, "time-split: tune on history before T, test on what came after", 11, "gray", ha="center")

    text(230, 1075, "Change instructions and monitor rules; keep the model, task\n"
                    "authorization, incident definition, observer, scorers and\n"
                    "search budget fixed. The library never reaches the agent.",
         12, "gray")
    text(W / 2, 1200,
         "Design overview v2 · Intake, synthesis, replay, monitor and release stages are proposed; "
         "native observer, clause search and offline qualification exist. No benchmark improvement is measured.",
         11, "gray", ha="center")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in ax.texts:
        extent = item.get_window_extent(renderer)
        if not (0 <= extent.x0 <= extent.x1 <= fig.bbox.width
                and 0 <= extent.y0 <= extent.y1 <= fig.bbox.height):
            raise ValueError(f"Text outside canvas: {item.get_text()}")

    OUT.mkdir(parents=True, exist_ok=True)
    stem = "incident-optimization-overview-v2"
    fig.savefig(OUT / f"{stem}.png", dpi=180, facecolor="white")
    fig.savefig(OUT / f"{stem}.svg", facecolor="white", metadata={"Date": None})
    plt.close(fig)
    svg = OUT / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    metadata = {
        "title": TITLE, "kind": "proposed_incident_history_optimization_overview",
        "created_on": "2026-10-05",
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sources},
        "extends": "figures/incident-optimization-overview-v1",
        "formats": ["PNG", "SVG"], "model_calls": 0, "empirical_result_claimed": False,
        "note": "Adds incident intake, history library, case synthesis, counterfactual "
                "replay, action monitor, regression gate and versioned release to the "
                "v1 development loop. All added stages are proposals. Held-out results "
                "and post-date-T incidents never feed search.",
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Generated {OUT.relative_to(ROOT)}/{stem}.{{png,svg}}")


if __name__ == "__main__":
    main()
