"""Draw a closed policy-search loop in the supplied overview.png paper style.

Vector primitives, not an edit of the reference bitmap. No model calls.
Run: python3 scripts/draw_incident_optimization_overview.py
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
OUT = ROOT / "figures/incident-optimization-overview-v1"
TITLE = "Incident-aware policy optimization"
C = {
    "ink": "#111111", "blue": "#365E9E", "arrow_blue": "#4679BC",
    "blue_dark": "#325F9E", "blue_light": "#BDD8ED", "blue_pale": "#EDF4FB",
    "yellow": "#FFF2CC", "yellow_top": "#FFF9E9", "white": "#FFFFFF",
    "gray": "#666666", "line": "#8C8C8C", "red": "#B34831",
}
plt.rcParams.update({
    "font.family": ["Arial", "DejaVu Sans"], "mathtext.fontset": "dejavusans",
    "svg.fonttype": "none", "svg.hashsalt": "incident-optimization-overview-v1",
})


def main():
    sources = [ROOT / path for path in (
        "docs/incident-aware-optimization.md",
        "experiments/incident-aware-optimization-v1.design.json",
        "docs/instruction-optimization.md",
        "src/containment_extension/instruction_optimization/catalog.py",
    )]
    design = json.loads(sources[1].read_text())
    assert design["primary_contrast"] == ["B4", "B3"]
    assert design["optimization"]["adaptive_loop"]["heldout_feedback"] is False
    fig = plt.figure(figsize=(17.2, 9.6), facecolor="white")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 1720), ylim=(960, 0))
    ax.axis("off")

    def text(x, y, value, size=15, color="ink", bold=False, ha="left", va="top"):
        return ax.text(x, y, value, fontsize=size, color=C[color],
                       fontweight="bold" if bold else "normal", ha=ha, va=va,
                       linespacing=1.25, zorder=10)

    def box(x, y, w, h, radius=8, fill="white", edge="ink", lw=1, dashed=False, z=3):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
            fc=C[fill], ec=C[edge], lw=lw,
            linestyle=(0, (3, 3)) if dashed else "-", zorder=z))

    def line(points, color="ink", lw=1.9, z=4):
        ax.plot([p[0] for p in points], [p[1] for p in points],
                color=C[color], lw=lw, solid_capstyle="butt", zorder=z)

    def arrow(points, color="ink", lw=1.9, scale=16):
        if len(points) > 2:
            line(points[:-1], color, lw)
        ax.add_patch(FancyArrowPatch(
            points[-2], points[-1], arrowstyle="-|>", mutation_scale=scale,
            shrinkA=0, shrinkB=0, lw=lw, color=C[color], zorder=4))

    def papers(x, y, w=55, h=36, count=5):
        for i in range(count):
            dx, dy = i * 9, i * 6
            # Alternate blue and white sheets, as in the supplied reference.
            fill = "blue_light" if i % 2 == 0 else "white"
            ax.add_patch(Rectangle((x + dx, y + dy), w, h,
                                   fc=C[fill], ec=C["blue"], lw=0.9, zorder=6 + i / 10))

    def cylinder(x, y, w, h, label):
        depth = 27
        ax.add_patch(Ellipse((x + w / 2, y + h - depth / 2), w, depth,
                             fc=C["yellow"], ec=C["ink"], lw=1, zorder=5))
        ax.add_patch(Rectangle((x, y + depth / 2), w, h - depth,
                               fc=C["yellow"], ec="none", zorder=6))
        line([(x, y + depth / 2), (x, y + h - depth / 2)], lw=1, z=7)
        line([(x + w, y + depth / 2), (x + w, y + h - depth / 2)], lw=1, z=7)
        ax.add_patch(Ellipse((x + w / 2, y + depth / 2), w, depth,
                             fc=C["yellow_top"], ec=C["ink"], lw=1, zorder=7))
        text(x + w / 2, y + h / 2 + 7, label, 16, ha="center", va="center")

    def rotating_arrow(cx, cy, start, end, color):
        # Two elliptical ribbons with tangential heads form a rotation symbol.
        rx, ry, width, head_width = 90, 37, 12, 30
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

    # Put the objective above the loop, leaving the flow itself concrete.
    text(860, 35, "Goal: fewer incidents, preserved task success, bounded cost", 23,
         bold=True, ha="center")
    text(860, 91,
         r"$\theta^*=\arg\min_{\theta\in\Theta}\,R(\theta)"
         r"\quad\mathrm{s.t.}\quad U(\theta)\geq U_0-\delta_U,"
         r"\quad C(\theta)\leq B,\quad F(\theta)\leq\alpha$",
         21, ha="center")
    text(860, 151,
         "θ: instruction settings    R: incident rate    U: task success    C: cost    F: false refusals",
         12.5, "gray", ha="center")

    # Dashed process groups and black orthogonal flow mirror overview.png.
    box(235, 208, 1130, 200, radius=28, dashed=True, z=1)
    text(800, 225, "Development rollouts & evaluation", 19, bold=True, ha="center")
    box(275, 285, 266, 69)
    text(408, 301, "Inspect agent", 17, ha="center")
    text(408, 364, "Fixed model", 12.5, "blue", True, "center")
    box(683, 285, 218, 69)
    text(792, 309, "Sandbox & tools", 16, ha="center", va="center")
    text(792, 364, "Development tasks", 12.5, "blue", True, "center")
    arrow([(541, 319), (683, 319)])
    papers(579, 288, 34, 24, 4)
    text(616, 364, "Tool calls", 12.5, "blue", True, "center")

    # Task outcomes and independent effects become distinct feedback signals.
    box(978, 273, 309, 43)
    text(1132, 295, "Task metrics (U, C, F)", 15, ha="center", va="center")
    box(978, 335, 309, 43, fill="blue_pale", edge="blue")
    text(1132, 357, "Incident observer (R)", 15, "blue", True, "center", "center")
    text(1132, 384, "containment extension", 10.5, "blue", ha="center")
    line([(901, 319), (943, 319)])
    arrow([(943, 319), (943, 295), (978, 295)])
    arrow([(943, 319), (943, 357), (978, 357)])
    line([(1287, 295), (1325, 295), (1325, 357), (1287, 357)])
    arrow([(1325, 325), (1527, 325), (1527, 432)])

    cylinder(1418, 432, 218, 112, "Trial\nevidence")
    arrow([(1527, 544), (1527, 705), (1290, 705)])
    text(1395, 670, "Feedback", 14, "blue", True, "center")

    # A prominent rotation symbol is inside the actual, arrow-connected cycle.
    text(715, 479, "Iterative optimization", 17, "blue", True, "right", "center")
    rotating_arrow(850, 479, -82, 88, "blue_dark")
    rotating_arrow(850, 479, 98, 268, "arrow_blue")
    text(988, 467, "Evaluate → select → revise", 13.5, "blue")
    text(988, 492, "Development feedback only", 11.5, "gray")
    text(855, 567, "Pass + unauthorized read → incident feedback", 13, "blue", True, "center")

    box(235, 622, 1130, 149, radius=28, dashed=True, z=1)
    text(800, 635, "Policy optimization", 19, bold=True, ha="center")
    box(275, 674, 426, 63)
    text(488, 685, "Revise instruction clauses", 16, ha="center")
    text(488, 714, "e.g. use current-run artifacts only", 12, "blue", ha="center")
    box(891, 674, 399, 63)
    text(1091, 685, "Select the lowest-incident policy", 15, ha="center")
    text(1091, 714, "Meet success, cost, and refusal limits", 12, "blue", ha="center")
    arrow([(891, 705), (701, 705)])
    text(796, 678, "Selection", 13, "blue", True, "center")

    # Updated instruction files close the loop, entering the same agent runner.
    arrow([(275, 706), (124, 706), (124, 320), (275, 320)])
    papers(77, 453, 55, 36, 6)
    text(197, 465, "Updated\ninstructions", 15, "blue", True)

    # A one-way exit keeps test outcomes out of optimization.
    arrow([(1091, 737), (1091, 854), (1333, 854)])
    text(1210, 820, r"Freeze $\theta^*$", 15, "blue", True, "center")
    box(1333, 821, 321, 70)
    text(1493, 833, "Held-out benchmarks", 16, ha="center")
    text(1493, 864, "Matched baselines + same observer", 11.5, "blue", ha="center")
    text(1493, 905, "No test feedback", 12, "gray", ha="center")

    text(235, 837, "Change instructions; keep the model, task scope,\nscorers, and search budget fixed.",
         12.5, "gray")
    text(860, 943, "Design overview · Adaptive benchmark integration and performance gains remain to be validated.",
         11, "gray", ha="center")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in ax.texts:
        extent = item.get_window_extent(renderer)
        if not (0 <= extent.x0 <= extent.x1 <= fig.bbox.width
                and 0 <= extent.y0 <= extent.y1 <= fig.bbox.height):
            raise ValueError(f"Text outside canvas: {item.get_text()}")

    OUT.mkdir(parents=True, exist_ok=True)
    stem = "incident-optimization-overview"
    fig.savefig(OUT / f"{stem}.png", dpi=180, facecolor="white")
    fig.savefig(OUT / f"{stem}.svg", facecolor="white", metadata={"Date": None})
    plt.close(fig)
    svg = OUT / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    reference = ROOT.parent / "overview.png"
    metadata = {
        "title": TITLE, "kind": "proposed_adaptive_optimization_overview",
        "created_on": "2026-10-04",
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sources},
        "style_reference": "overview.png supplied in the workspace",
        "style_reference_sha256": hashlib.sha256(reference.read_bytes()).hexdigest()
                                  if reference.exists() else None,
        "formats": ["PNG", "SVG"], "model_calls": 0, "empirical_result_claimed": False,
        "note": "Proposed adaptive development loop over reviewed instruction settings. "
                "The initial matched B3/B4 study still uses one fixed candidate pool. "
                "The native optimizer provides a local foundation, not this full "
                "cross-benchmark constrained optimizer. Held-out results never feed search.",
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Generated {OUT.relative_to(ROOT)}/{stem}.{{png,svg}}")


if __name__ == "__main__":
    main()
