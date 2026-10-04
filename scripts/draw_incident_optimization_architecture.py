"""Export a research architecture with the optimization objective and study design.

Run: python3 scripts/draw_incident_optimization_architecture.py
Produces editable SVG, PNG, and source hashes. No invented performance data.
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
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/incident-aware-optimization-v1"
COLORS = {
    "bg": "#F4F7FA", "ink": "#172E42", "muted": "#546D80",
    "line": "#D3E0E9", "white": "#FFFFFF", "teal": "#087F76",
    "teal_light": "#E5F3EF", "blue": "#345CB3", "blue_light": "#E9EFFB",
    "amber": "#915E12", "amber_light": "#FBF0DA", "gray_light": "#EAF0F4",
}
plt.rcParams.update({
    "font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans",
    "svg.fonttype": "none", "svg.hashsalt": "incident-aware-optimization-v1",
})


def main():
    sources = [ROOT / name for name in (
        "docs/incident-aware-optimization.md",
        "experiments/incident-aware-optimization-v1.design.json",
        "experiments/standardized-benchmarks-v1.design.json",
    )]
    design = json.loads(sources[1].read_text())
    assert design["primary_contrast"] == ["B4", "B3"]
    assert design["new_model_calls"] == 0
    assert design["status"] == "design_only_matched_feedback_ablation_not_implemented"

    fig = plt.figure(figsize=(18, 14.8), facecolor=COLORS["bg"])
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 1800), ylim=(1480, 0))
    ax.axis("off")
    containers = []

    def text(x, y, value, size=12, color="ink", bold=False, ha="left", va="top"):
        return ax.text(x, y, value, fontsize=size, color=COLORS.get(color, color),
                       fontweight="bold" if bold else "normal", ha=ha, va=va,
                       linespacing=1.42)

    def box(x, y, width, height, fill="white", edge="line", radius=14):
        ax.add_patch(FancyBboxPatch(
            (x, y), width, height, boxstyle=f"round,pad=0,rounding_size={radius}",
            facecolor=COLORS[fill], edgecolor=COLORS[edge], linewidth=1.2,
        ))
        return x, y, width, height

    def inside(bounds, *items):
        containers.extend((bounds, item) for item in items)

    def arrow(x1, y1, x2, y2, color="muted", width=1.8):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=17,
            linewidth=width, color=COLORS[color], shrinkA=3, shrinkB=3,
        ))

    def line(points, color="muted", dashed=False):
        ax.plot([p[0] for p in points], [p[1] for p in points],
                color=COLORS[color], lw=1.7, ls="--" if dashed else "-")

    def pill(x, y, width, label, fill="amber_light", color="amber"):
        bounds = box(x, y, width, 30, fill, fill, radius=15)
        inside(bounds, text(x + width / 2, y + 15, label, 9.4, color,
                            bold=True, ha="center", va="center"))

    text(60, 27, "CONTAINMENT EXTENSION  /  RESEARCH ARCHITECTURE  /  04 OCT 2026",
         10, "muted", True)
    pill(1300, 23, 440, "PROPOSED EXPERIMENT · NO MEASURED GAINS")
    text(60, 68, "Incident-aware policy optimization", 30, bold=True)
    text(60, 121, "Can verified effect feedback select safer policies at the same task capability and cost?",
         14.5, "muted")

    # The full constrained objective is visible before any architectural detail.
    objective = box(60, 164, 1680, 211, edge="teal")
    inside(objective,
           text(84, 184, "OBJECTIVE  /  WITHIN EACH BENCHMARK AND THREAT CONDITION",
                10.8, "teal", True),
           text(94, 231, r"$\theta^{\star}=\mathrm{arg\,min}_{\theta\in\Theta}\;R(\theta)$",
                26, "ink"),
           text(785, 221, r"$\mathrm{subject\ to}\quad U(\theta)\geq U(\theta_0)-\delta_U$",
                20, "ink"),
           text(998, 266, r"$C(\theta)\leq B_{\mathrm{run}},\qquad F(\theta)\leq\alpha_F$",
                20, "ink"),
           text(84, 324, "R: verified incident probability    U: feasible-task utility    C: cost per task    F: false intervention",
                12.3, "muted"),
           text(84, 350, r"$\theta_0$: reference policy    $\delta_U$: allowed utility loss    "
                r"$B$ and $\alpha_F$: predeclared cost and false-intervention limits",
                10.9, "muted"))

    text(60, 385, "01  /  DEVELOPMENT: SHARED ROLLOUTS, DIFFERENT SELECTION SIGNALS",
         11, "muted", True)
    text(1740, 385, r"Matched search budget: $C_{\mathrm{search}}\leq B_{\mathrm{search}}$",
         12, "muted", ha="right")

    # These signals are collected once. Only the optimizer's feedback differs.
    shared = box(60, 423, 1680, 109)
    line([(593, 444), (593, 510)], "line")
    line([(1172, 444), (1172, 510)], "line")
    inside(shared,
           text(84, 442, "Fixed candidate pool", 16, bold=True),
           text(84, 476, r"$\theta$: reviewed instruction clauses" + "\nSame actor, tasks, tools and search space",
                11.7, "muted"),
           text(639, 442, "Inspect execution + task scoring", 15.5, bold=True),
           text(639, 476, "One shared set of development rollouts\nFixed authorization and outer boundary",
                11.7, "muted"),
           text(1215, 442, "Extension: incident evidence", 15.5, "teal", True),
           text(1215, 476, "Independent state/effect observations\nQualified references and artifact probes",
                11.7, "muted"))
    arrow(538, 477, 623, 477)
    arrow(1123, 477, 1202, 477, "teal")

    # Shared rollout records feed both selectors; proxy selection never receives
    # independent effect labels, even though the common observer records them.
    line([(900, 533), (900, 548), (460, 548)], "muted")
    line([(900, 548), (1340, 548)], "muted")
    arrow(460, 548, 460, 568, "blue")
    arrow(1340, 548, 1340, 568, "teal")
    left = box(60, 570, 800, 166, "blue_light", "blue")
    right = box(940, 570, 800, 166, "teal_light", "teal")
    inside(left,
           text(84, 590, "B3  /  Proxy-feedback selection", 18, "blue", True),
           text(84, 628, "Task utility + frozen transcript-based incident proxy", 13, "ink"),
           text(84, 662, "Select from the shared pool under the same constraints.", 11.8, "muted"),
           text(84, 699, r"Selected policy: $\pi_{\theta_{\mathrm{proxy}}}$", 14, "blue", True))
    inside(right,
           text(964, 590, "B4  /  Incident-feedback selection", 18, "teal", True),
           text(964, 628, "Task utility + independently verified incident effects", 13, "ink"),
           text(964, 662, "Keep faults and unknowns separate from clean outcomes.", 11.8, "muted"),
           text(964, 699, r"Selected policy: $\pi_{\theta_{\mathrm{incident}}}$", 14, "teal", True))
    arrow(460, 739, 460, 771, "blue")
    arrow(1340, 739, 1340, 771, "teal")
    text(900, 755, "PRIMARY CONTRAST: B4 − B3", 10.2, "muted", True, ha="center")

    # The freeze boundary makes data isolation and the lack of test feedback clear.
    frozen = box(60, 775, 1680, 66, "ink", "ink")
    inside(frozen,
           text(84, 796, "FREEZE BEFORE TEST", 14, "white", True),
           text(467, 797, "Policies · models · scorer / observer · thresholds · budgets · task schedule",
                12.4, "white"))
    text(900, 853, "Group splits by task / issue / artifact lineage. Final test outcomes never return to selection.",
         11.2, "muted", ha="center")

    text(60, 893, "02  /  HELD-OUT BENCHMARK EVALUATION", 11, "muted", True)
    # All arms have the same final observer. B1's role is passive instrumentation.
    refs = box(60, 928, 390, 165)
    inside(refs,
           text(83, 949, "Reference arms", 16, bold=True),
           text(83, 987, "B0   Official upstream agent\nB1   Same behavior + observation\nB2   Established defense / control",
                11.7, "muted"))
    arrow(453, 1008, 506, 1008)
    test = box(510, 928, 733, 165)
    inside(test,
           text(533, 948, "Fresh rollouts on unseen tasks", 17, bold=True),
           text(533, 988, "Frozen B3 and B4 + reference arms B0 / B1 / B2\nSame independent incident observer for every arm\nAll assignments retained; paired task-level uncertainty",
                12.1, "muted"))
    arrow(900, 875, 900, 925)
    arrow(1246, 1008, 1297, 1008, "teal")
    endpoints = box(1300, 928, 440, 165, "teal_light", "teal")
    inside(endpoints,
           text(1321, 949, "Primary comparison", 16, "teal", True),
           text(1321, 987, r"$\Delta R=R_{B4}-R_{B3}$", 18, "ink"),
           text(1321, 1025, r"$\Delta U=U_{B4}-U_{B3}$", 18, "ink"),
           text(1321, 1064, "Also report refusal, cost and coverage.", 10.4, "muted"))

    text(60, 1122, "BENCHMARKS  /  RETAIN SEPARATE SCORES AND TASK-ONLY / ATTACK POPULATIONS",
         10.6, "muted", True)
    panels = [
        (60, "Impossible-SWEbench", "Original-task capability\nImpossible-task cheating\nIndependent policy effects", "blue"),
        (489, "AgentDojo", "Clean and attacked task utility\nInjection success\nFixed published defenses", "blue"),
        (918, "ResearchArena", "Same frozen trajectories\nMonitor access / probe policies\nDetection at fixed FPR and cost", "teal"),
        (1347, "BashArena / ControlArena", "Later online-control comparison\nTrusted monitoring / deferral\nEffects checked after each action", "muted"),
    ]
    for x, title, body, color in panels:
        bounds = box(x, 1156, 393, 128)
        inside(bounds, text(x + 19, 1175, title, 14, color, True),
               text(x + 19, 1209, body, 11.1, "muted"))

    # A separate objective prevents retrospective detection from being presented
    # as a causal prevention experiment.
    monitor = box(60, 1301, 1680, 89)
    inside(monitor,
           text(84, 1317, "MONITOR-ONLY OBJECTIVE", 10.7, "teal", True),
           text(84, 1342, r"$\phi$: monitor / probe policy. Benign-only calibration.", 10.5, "muted"),
           text(84, 1366, "Detection quality; prevention needs an online test.", 10.5, "muted"),
           text(706, 1325,
                r"$\max_{\phi}\;\mathrm{TPR}(\phi)\quad\mathrm{s.t.}\quad"
                r"\mathrm{FPR}(\phi)\leq\alpha,\quad C_{\mathrm{monitor}}(\phi)\leq B_{\mathrm{monitor}}$",
                19, "ink"))
    text(60, 1409, "Implemented foundations: effect observers, local instruction search, fixture qualification and offline reporting.",
         11.5, "muted")
    text(60, 1440, "Proposed: the matched B3/B4 benchmark experiment. No safety or performance gains have been measured.",
         11.5, "amber", True)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in ax.texts:
        bounds = item.get_window_extent(renderer)
        if not (0 <= bounds.x0 <= bounds.x1 <= fig.bbox.width
                and 0 <= bounds.y0 <= bounds.y1 <= fig.bbox.height):
            raise ValueError(f"Text outside canvas: {item.get_text()}")
    for (x, y, width, height), item in containers:
        bounds = item.get_window_extent(renderer).transformed(ax.transData.inverted())
        if (bounds.xmin < x + 5 or bounds.xmax > x + width - 5
                or bounds.ymin < y + 3 or bounds.ymax > y + height - 3):
            raise ValueError(f"Text outside its card: {item.get_text()}")

    OUT.mkdir(parents=True, exist_ok=True)
    stem = "incident-aware-optimization-architecture"
    fig.savefig(OUT / f"{stem}.svg", facecolor=COLORS["bg"], metadata={"Date": None})
    fig.savefig(OUT / f"{stem}.png", facecolor=COLORS["bg"], dpi=170)
    plt.close(fig)
    svg = OUT / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    metadata = {
        "title": "Incident-aware policy optimization", "created_on": "2026-10-04",
        "kind": "proposed_research_architecture", "empirical_result_claimed": False,
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sources},
        "model_calls": 0, "formats": ["PNG", "SVG"],
        "primary_contrast": design["primary_contrast"],
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Generated {OUT.relative_to(ROOT)}/{stem}.{{png,svg}}")


if __name__ == "__main__":
    main()
