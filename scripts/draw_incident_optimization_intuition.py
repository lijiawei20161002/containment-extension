"""Draw the intuition behind incident-aware policy selection as editable vectors.

This is a stylized example, not an empirical comparison of two agent policies.
Run: python3 scripts/draw_incident_optimization_intuition.py
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/containment-evaluation-mpl")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/incident-optimization-intuition-v1"
TITLE = "Why incident feedback can help"
C = {
    "bg": "#FFFFFF", "ink": "#20374C", "muted": "#697E8D",
    "line": "#D4DFE7", "blue": "#4373A5", "blue_light": "#EDF3FA",
    "teal": "#168571", "teal_light": "#E9F5F0", "teal_mid": "#BBE1D4",
    "orange": "#BF6434", "orange_light": "#FFF3E9", "orange_mid": "#F1CEB7",
    "white": "#FFFFFF", "shadow": "#E9EEF2", "gray_light": "#F5F8FA",
}
plt.rcParams.update({
    "font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans",
    "svg.fonttype": "none", "svg.hashsalt": "incident-optimization-intuition-v1",
})


def main():
    sources = [ROOT / path for path in (
        "docs/incident-aware-optimization.md",
        "experiments/incident-aware-optimization-v1.design.json",
        "src/containment_extension/instruction_optimization/catalog.py",
        "src/containment_extension/instruction_optimization/study.py",
    )]
    design = json.loads(sources[1].read_text())
    assert design["primary_contrast"] == ["B4", "B3"]
    fig = plt.figure(figsize=(17.6, 10.2), facecolor=C["bg"])
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 1760), ylim=(1020, 0))
    ax.axis("off")

    def text(x, y, value, size=14, color="ink", bold=False, ha="left", va="top"):
        return ax.text(x, y, value, fontsize=size, color=C.get(color, color),
                       fontweight="bold" if bold else "normal", ha=ha, va=va,
                       linespacing=1.35, zorder=10)

    def box(x, y, w, h, fill="white", edge="line", radius=12, lw=1.5, z=3):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
            fc=C[fill], ec=C[edge], lw=lw, zorder=z))

    def line(points, color="line", lw=2, z=5):
        ax.plot([p[0] for p in points], [p[1] for p in points],
                color=C[color], lw=lw, solid_capstyle="round", zorder=z)

    def poly(points, fill, edge, z=5):
        ax.add_patch(Polygon(points, closed=True, fc=C[fill], ec=C[edge], lw=1.6, zorder=z))

    def dot(x, y, r, fill, edge=None, z=6):
        ax.add_patch(Circle((x, y), r, fc=C[fill], ec=C[edge or fill], lw=1.5, zorder=z))

    def arrow(start, end, color="blue", lw=2.3):
        ax.add_patch(FancyArrowPatch(
            start, end, arrowstyle="-|>", mutation_scale=19,
            shrinkA=0, shrinkB=0, lw=lw, color=C[color], zorder=4))

    def shadow(cx, y, w):
        ax.add_patch(Ellipse((cx, y), w, 15, fc=C["shadow"], ec="none", zorder=2))

    def check(x, y, color="teal", scale=1):
        line([(x - 8 * scale, y), (x - 2 * scale, y + 6 * scale),
              (x + 10 * scale, y - 8 * scale)], color, 2.5, z=8)

    def badge(x, y, value, color):
        dot(x, y, 19, color)
        text(x, y, value, 14, "white", True, "center", "center")

    def robot(cx, cy, policy, color):
        shadow(cx, cy + 66, 116)
        # The same blue agent appears twice; only its instruction badge changes.
        box(cx - 61, cy - 82, 57, 71, "white", "line", 5)
        for dy, length in ((-65, 30), (-53, 23), (-41, 30)):
            line([(cx - 49, cy + dy), (cx - 49 + length, cy + dy)], "line", 1.5)
        line([(cx, cy - 63), (cx, cy - 48)], "blue", 2)
        dot(cx, cy - 66, 5, "blue_light", "blue")
        box(cx - 47, cy - 47, 94, 63, "blue_light", "blue", 17, 2)
        box(cx - 33, cy - 31, 66, 28, "ink", "ink", 9)
        dot(cx - 15, cy - 17, 4, "white")
        dot(cx + 15, cy - 17, 4, "white")
        box(cx - 31, cy + 23, 62, 33, "blue_light", "blue", 10, 2)
        line([(cx - 42, cy + 26), (cx - 48, cy + 47)], "blue", 3)
        line([(cx + 42, cy + 26), (cx + 48, cy + 47)], "blue", 3)
        line([(cx - 16, cy + 57), (cx - 16, cy + 64)], "blue", 3)
        line([(cx + 16, cy + 57), (cx + 16, cy + 64)], "blue", 3)
        badge(cx + 48, cy - 44, policy, color)
        text(cx, cy + 81, f"Policy {policy}", 14, "ink", True, "center")

    def document(x, y, w=83, h=106, color="teal", answer=False):
        fold = 20
        shadow(x + w / 2, y + h + 8, w + 12)
        poly([(x, y), (x + w - fold, y), (x + w, y + fold),
              (x + w, y + h), (x, y + h)], "white", color)
        poly([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)],
             f"{color}_light", color, 6)
        for dy, length in ((36, 43), (49, 34), (62, 43)):
            line([(x + 14, y + dy), (x + 14 + length, y + dy)], "line", 2)
        if answer:
            dot(x + w - 5, y + h - 4, 19, "teal")
            check(x + w - 5, y + h - 4, "white")

    def folder(cx, cy):
        x, y = cx - 67, cy - 35
        shadow(cx, y + 93, 153)
        poly([(x, y + 5), (x, y - 6), (x + 48, y - 6), (x + 62, y + 7),
              (x + 132, y + 7), (x + 132, y + 83), (x, y + 83)], "teal_mid", "teal")
        box(x + 17, y - 16, 87, 72, "white", "teal", 4, 1.5, 6)
        text(cx - 7, y + 4, "</>", 23, "teal", True, "center")
        poly([(x - 6, y + 32), (x + 139, y + 32), (x + 130, y + 83),
              (x + 3, y + 83)], "teal_light", "teal", 7)
        text(cx, cy - 89, "IN SCOPE", 10, "teal", True, "center")

    def archive(cx, cy):
        x, y = cx - 58, cy - 67
        shadow(cx, cy + 64, 144)
        poly([(x, y), (x + 17, y - 12), (x + 134, y - 12), (x + 117, y)],
             "orange_mid", "orange")
        poly([(x + 117, y), (x + 134, y - 12), (x + 134, y + 109),
              (x + 117, y + 121)], "orange_mid", "orange")
        box(x, y, 117, 121, "orange_light", "orange", 4, 1.7, 6)
        for dy in (12, 49, 86):
            box(x + 10, y + dy, 96, 27, "white", "orange_mid", 4, 1.2, 7)
            line([(cx - 11, y + dy + 10), (cx + 11, y + dy + 10)], "orange", 2, z=8)
        dot(cx + 69, cy + 46, 18, "orange")
        text(cx + 69, cy + 46, "!", 17, "white", True, "center", "center")
        text(cx + 6, cy - 100, "OUT OF SCOPE", 10, "orange", True, "center")

    def lock(x, y):
        ax.add_patch(Arc((x + 8, y + 4), 13, 17, theta1=180, theta2=360,
                         color=C["muted"], lw=1.8, zorder=6))
        box(x, y + 4, 16, 15, "gray_light", "muted", 3, 1.5, 7)

    text(65, 50, TITLE, 31, bold=True)
    text(67, 112, "Both policies pass. Only one stays within scope.", 18, "muted")
    box(1468, 60, 224, 34, "gray_light", "gray_light", 17, 0)
    text(1580, 77, "ILLUSTRATIVE EXAMPLE", 10, "muted", True, "center", "center")

    for x, number, title, subtitle in (
        (72, "1", "Run", "Same model, task, and budget"),
        (917, "2", "Observe", "Inspect + containment extension"),
        (1422, "3", "Optimize", "Select instructions, then retest"),
    ):
        badge(x + 17, 221, number, "ink")
        text(x + 51, 220, title, 21, bold=True, va="center")
        text(x, 259, subtitle, 12.5, "muted")

    # Two illustrative development rollouts. These are not measured policy scores.
    for cy, policy, color in ((445, "A", "teal"), (655, "B", "orange")):
        box(67, cy - 106, 737, 207, f"{color}_light", f"{color}_light", 20, 0, 1)
        robot(152, cy - 4, policy, color)
        arrow((237, cy), (337, cy), color)
        text(283, cy - 33, "solve" if policy == "A" else "copy", 12, color, ha="center")
        if policy == "A":
            folder(424, cy)
            resource_label = "Current workspace"
        else:
            archive(424, cy)
            resource_label = "Prior-run archive"
        text(429, cy + 77, resource_label, 13, "ink", ha="center")
        arrow((517, cy), (655, cy), color)
        document(677, cy - 61, answer=True)
        text(721, cy + 77, "Correct answer", 13, "ink", ha="center")
        arrow((807, cy), (897, cy), "blue")

    # A physical display combines the original scorer and independent effect log.
    shadow(1114, 785, 330)
    box(1084, 715, 57, 60, "line", "line", 0)
    box(1015, 769, 196, 13, "gray_light", "line", 6)
    box(910, 345, 421, 385, "ink", "ink", 18, 2)
    box(925, 360, 391, 350, "white", "white", 9, 0, 6)
    text(1057, 378, "Task", 14, "blue", True, "center")
    text(1220, 378, "Incident", 14, "orange", True, "center")
    line([(948, 411), (1292, 411)], "line", 1)
    for cy, policy, incident, color in ((445, "A", "NO", "teal"), (655, "B", "YES", "orange")):
        badge(956, cy, policy, color)
        box(1005, cy - 23, 107, 46, "blue_light", "blue_light", 9, 0, 7)
        text(1058, cy, "PASS", 17, "blue", True, "center", "center")
        box(1166, cy - 23, 108, 46, f"{color}_light", f"{color}_light", 9, 0, 7)
        text(1220, cy, incident, 17, color, True, "center", "center")
    text(1058, 550, "=", 36, "blue", ha="center", va="center")
    text(1220, 550, "≠", 36, "orange", ha="center", va="center")
    text(1118, 800, "Same score. Different risk.", 15, "ink", True, "center")

    # Select a candidate, freeze it, then evaluate unseen tasks without test feedback.
    text(1539, 383, "Prefer fewer incidents", 13, "teal", True, "center")
    arrow((1345, 536), (1400, 536), "teal", 2.8)
    for pin in (0, 1, 2, 3, 4):
        offset = pin * 41
        line([(1445 + offset, 437), (1445 + offset, 450)], "teal", 3)
        line([(1445 + offset, 603), (1445 + offset, 616)], "teal", 3)
    for yy in (473, 508, 544, 579):
        line([(1408, yy), (1421, yy)], "teal", 3)
        line([(1657, yy), (1670, yy)], "teal", 3)
    box(1421, 450, 236, 153, "teal_light", "teal", 13, 2)
    text(1539, 478, "OPTIMIZER", 12, "teal", True, "center")
    box(1443, 521, 192, 54, "teal", "teal", 9, 0, 7)
    text(1539, 548, "Select A", 19, "white", True, "center", "center")
    arrow((1539, 622), (1539, 681), "teal")
    lock(1489, 640)
    text(1560, 640, "Freeze", 12, "muted")
    for x, y in ((1474, 701), (1517, 690), (1560, 701)):
        box(x, y, 63, 74, "blue_light", "blue", 5, 1.5, 7)
        text(x + 31, y + 36, "?", 25, "blue", True, "center", "center")
    text(1539, 800, "Test on unseen tasks", 15, "ink", True, "center")

    # A compact, readable objective; the full protocol also constrains false refusals.
    box(65, 862, 1627, 104, "gray_light", "gray_light", 16, 0, 1)
    text(89, 878, "Goal: fewer incidents, with comparable success and cost.", 17, bold=True)
    text(89, 921,
         r"$\min_{\theta}\;\mathrm{IncidentRate}(\theta)"
         r"\quad\mathrm{s.t.}\quad\mathrm{Success}(\theta)\geq\mathrm{Success}_0-\delta,"
         r"\quad\mathrm{Cost}(\theta)\leq B$", 17)
    text(67, 985, "Illustrative mechanism, not a measured improvement. Simplified objective; full study uses matched baselines.",
         10.5, "muted")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in ax.texts:
        extent = item.get_window_extent(renderer)
        if not (0 <= extent.x0 <= extent.x1 <= fig.bbox.width
                and 0 <= extent.y0 <= extent.y1 <= fig.bbox.height):
            raise ValueError(f"Text outside canvas: {item.get_text()}")

    OUT.mkdir(parents=True, exist_ok=True)
    stem = "incident-optimization-intuition"
    fig.savefig(OUT / f"{stem}.png", dpi=180, facecolor=C["bg"])
    fig.savefig(OUT / f"{stem}.svg", facecolor=C["bg"], metadata={"Date": None})
    plt.close(fig)
    svg = OUT / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    metadata = {
        "title": TITLE, "kind": "illustrative_policy_selection_mechanism",
        "created_on": "2026-10-04",
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sources},
        "formats": ["PNG", "SVG"], "model_calls": 0, "empirical_result_claimed": False,
        "note": "Stylized feasible-task illustration based on the verified cached-answer "
                "shortcut mechanism. A/B are illustrative policies, not study arm IDs or "
                "measured model outcomes. Effects are independently observed; observation "
                "does not itself prevent incidents. The full study compares verified-effect "
                "feedback with a transcript-proxy baseline, at matched budgets, and constrains "
                "false refusals as well as utility and cost.",
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Generated {OUT.relative_to(ROOT)}/{stem}.{{png,svg}}")


if __name__ == "__main__":
    main()
