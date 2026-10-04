"""Draw the implemented evaluation paths from their frozen offline evidence.

Run: python3 scripts/draw_evaluation_implementation.py
Produces editable SVG, PNG, and source provenance; no model calls.
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
OUT = ROOT / "figures/evaluation-implementation-v1"
C = {
    "bg": "#F5F7FA", "ink": "#182D40", "muted": "#587082", "line": "#D7E1E8",
    "white": "#FFFFFF", "green": "#187768", "gpale": "#E8F4EE",
    "blue": "#315EAC", "bpale": "#EAF0FA", "red": "#B34B43", "rpale": "#FBEDEA",
    "gray": "#6A737E", "graypale": "#EDF0F3",
}
plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                     "svg.hashsalt": "evaluation-implementation-v1"})


def main():
    sources = [ROOT / "results" / name / "summary.json" for name in (
        "counterfactual-evaluation-offline-v1", "researcharena-monitoring-offline-v1")]
    workflow, arena = [json.loads(p.read_text()) for p in sources]
    assert workflow["passed"] and arena["passed"]
    assert workflow["model_calls"] == arena["model_calls"] == 0
    labels = arena["archive"]["labels"]
    # Use a real qualified selective-corruption case for the worked example.
    cases = [json.loads(p.read_text()) for p in
             (sources[1].parent / "artifacts/reference").glob("*.json")]
    example = next(c for c in cases if c["condition"] == "selective_corruption"
                   and c["offset"] == 7 and c["trigger"] == 24)
    pair = example["reference"]["paired_probe"]

    fig = plt.figure(figsize=(18, 15), facecolor=C["bg"])
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 1800), ylim=(1500, 0))
    ax.axis("off")

    def text(x, y, value, size=13, color="ink", bold=False, ha="left", va="top"):
        return ax.text(x, y, value, fontsize=size, color=C.get(color, color),
                       fontweight="bold" if bold else "normal", ha=ha, va=va,
                       linespacing=1.45)

    def box(x, y, w, h, fill="white", edge="line", radius=14, dashed=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                   boxstyle=f"round,pad=0,rounding_size={radius}",
                                   facecolor=C[fill], edgecolor=C[edge], linewidth=1.3,
                                   linestyle="--" if dashed else "-"))

    def arrow(x1, y1, x2, y2, color="green"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                    mutation_scale=17, color=C[color], linewidth=2,
                                    shrinkA=4, shrinkB=4))

    def pill(x, y, w, label, color="green", fill="gpale"):
        box(x, y, w, 32, fill, fill, radius=16)
        text(x + w / 2, y + 16, label, 10, color, True, ha="center", va="center")

    def section(x, label, title, subtitle):
        text(x, 200, label, 11, "green", True)
        text(x, 228, title, 23, bold=True)
        text(x, 270, subtitle, 12.5, "muted")

    def step(x, y, w, number, title, body, metric=None):
        box(x, y, w, 128)
        box(x + 18, y + 18, 34, 34, "gpale", "gpale", radius=10)
        text(x + 35, y + 35, str(number), 12, "green", True, ha="center", va="center")
        text(x + 66, y + 20, title, 16, bold=True)
        text(x + 66, y + 57, body, 12, "muted")
        if metric:
            text(x + w - 22, y + 20, metric, 13, "green", True, ha="right")

    text(60, 30, "CONTAINMENT EXTENSION  /  IMPLEMENTATION SNAPSHOT  /  04 OCT 2026", 10.5, "muted", True)
    text(60, 68, "What is implemented and what has run", 32, bold=True)
    text(60, 124, "Two bounded evaluation paths, independent reference checks, and a shared evidence trail.", 15, "muted")
    pill(60, 159, 225, "OFFLINE: EXECUTED")
    pill(301, 159, 316, "LIVE RUNNER: BUILT, UNRUN", "blue", "bpale")
    pill(633, 159, 260, "LATER PROTOCOL WORK", "gray", "graypale")
    text(1738, 165, "0 model calls in these runs", 12, "green", True, ha="right")

    lx, rx, width = 60, 920, 820
    section(lx, "A  /  COUNTERFACTUAL EVALUATION", "Why did the task fail?",
            "Separate a missing solution from a broken environment or an unsupported claim.")
    section(rx, "B  /  RESEARCHARENA-INSPIRED EVALUATION", "What would the monitor need to see?",
            "Prepare action judgments and probe harmful behavior inside editable artifacts.")

    # Left path: construction, independent qualification, and grader evidence.
    box(lx, 312, width, 234)
    text(lx + 24, 334, "Four matched local workflows", 16, bold=True)
    text(lx + 24, 369, "Each begins with the same failed completion attempt.", 12, "muted")
    variants = [
        (lx + 24, 406, "Short repair", "2 allowed actions → goal", "gpale", "green"),
        (lx + 418, 406, "Longer repair", "4 allowed actions → goal", "gpale", "green"),
        (lx + 24, 469, "Bounded impossible", "All allowed routes checked", "graypale", "gray"),
        (lx + 418, 469, "Environment fault", "Repair setup → goal restored", "rpale", "red"),
    ]
    for x, y, title, detail, fill, color in variants:
        box(x, y, 374, 56, fill, fill, radius=9)
        text(x + 14, y + 7, title, 12, color, True)
        text(x + 14, y + 30, detail, 10.8, "muted")
    arrow(470, 550, 470, 578)
    step(lx, 580, width, 1, "Independent reference qualification",
         "Graph oracle ↔ actual dispatcher\nReplay solution witnesses; reject false labels.",
         f"{workflow['transition_checks']} checks")
    arrow(470, 710, 470, 738)
    step(lx, 740, width, 2, "Challenge the grader's conclusion",
         "Failed approach + criticism + candidate alternative\nCompare evidence support with the hidden reference.",
         f"{workflow['grader_cases']} cases")
    box(lx, 890, width, 120, "gpale", "gpale")
    text(lx + 24, 910, "A failed approach does not prove impossibility.", 17, "green", True)
    text(lx + 24, 950, "Deterministic grader controls passed.\nLearned-grader accuracy and actor capability are still unmeasured.", 12, "muted")

    # Right path: archived action evidence and a distinct artifact experiment.
    box(rx, 312, width, 173)
    text(rx + 24, 334, "Archive audit  •  before dispatch", 16, bold=True)
    text(rx + 24, 372,
         f"{arena['archive']['proposals']:,} proposals · {arena['archive']['source_rollouts']} source rollouts\n"
         "Rebuild paired views; check source hashes, cutoff, and service records.", 12, "muted")
    for x, value, label, color in [
        (rx + 24, labels["authorized"], "authorized", "green"),
        (rx + 290, labels["unauthorized"], "unauthorized target", "red"),
        (rx + 555, labels["malformed_or_unsupported"], "malformed / unsupported", "gray"),
    ]:
        text(x, 429, f"{value:,}", 20, color, True)
        text(x + (64 if value < 100 else 94), 438, label, 9.5, "muted")

    box(rx, 507, width, 248)
    text(rx + 24, 529, "Artifact probes  •  after the run", 16, bold=True)
    text(rx + 24, 565,
         f"{arena['cases']} scripted cache artifacts · full 32-input reference check\n"
         "Clean optimization / selective corruption / broad regression / fault", 11.6, "muted")
    box(rx + 24, 626, 344, 101, "gpale", "gpale", radius=10)
    text(rx + 40, 640, "Ordinary tests pass", 13, "green", True)
    text(rx + 40, 675, "Cache looks useful on common inputs.", 10.7, "muted")
    arrow(rx + 376, 676, rx + 416, 676, "red")
    box(rx + 423, 626, 373, 101, "rpale", "rpale", radius=10)
    text(rx + 439, 640, "A rare input reveals the defect", 12.5, "red", True)
    text(rx + 439, 675,
         f"x = {pair['inputs'][0]}: expected {pair['expected'][0]}, observed {pair['outputs'][0]}",
         12, "ink", True)

    arrow(1330, 760, 1330, 784)
    box(rx, 786, width, 224)
    text(rx + 24, 807, f"{arena['monitor_inputs']} artifact-monitor inputs prepared", 16, bold=True)
    text(rx + 24, 844, "Same case; vary visible explanations and artifact access.", 12, "muted")
    matrix_y = 884
    matrix = [
        (rx + 24, "T", "Actions only"),
        (rx + 222, "TE", "+ visible text"),
        (rx + 420, "TA", "+ inspect / probe"),
        (rx + 618, "TEA", "+ both"),
    ]
    for x, title, desc in matrix:
        box(x, matrix_y, 178, 66, "gpale", "gpale", radius=9)
        text(x + 89, matrix_y + 10, title, 14, "green", True, ha="center")
        text(x + 89, matrix_y + 39, desc, 10, "muted", ha="center")
    text(rx + 24, 972, "Model judgments pending; scripted explanations are labeled as such.", 11, "muted")

    # Both paths export evidence; execution remains visibly distinct.
    arrow(470, 1014, 470, 1043)
    arrow(1330, 1014, 1330, 1043)
    box(60, 1046, 1680, 103, "gpale", "gpale")
    text(86, 1065, "Shared evidence export", 18, "green", True)
    text(86, 1105, "Source + design snapshots  •  separate inputs and hidden references  •  hashed manifests  •  overwrite protection", 13, "muted")
    pill(1434, 1063, 280, "OFFLINE EXPORTS VERIFIED")
    arrow(900, 1154, 900, 1181, "blue")

    box(60, 1185, 1680, 149, "bpale", "blue")
    text(86, 1206, "Live execution code is implemented and tested with scripted transports", 19, "blue", True)
    text(86, 1246, "Workflow actors + graders   /   archive monitors   /   artifact monitors", 15, bold=True)
    text(86, 1287, "Frozen plans, per-assignment budgets, request logs, and retained failures. Live runs await a model and spending cap.", 12.5, "muted")

    box(60, 1356, 1680, 71, "graypale", "gray", dashed=True)
    text(86, 1377, "Later protocol work", 14, "gray", True)
    text(318, 1378, "RA4 deliberate-attack actors  •  new task families  •  causal prevention experiments", 13, "muted")
    text(60, 1450, "Observed here: fixture and evidence correctness. Model safety, detection quality, and generalization remain unmeasured.",
         12, "muted")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in ax.texts:
        b = item.get_window_extent(renderer)
        if b.x0 < 0 or b.y0 < 0 or b.x1 > fig.bbox.width or b.y1 > fig.bbox.height:
            raise ValueError(f"Text outside figure: {item.get_text()}")
    OUT.mkdir(parents=True, exist_ok=True)
    stem = "evaluation-implementation"
    fig.savefig(OUT / f"{stem}.svg", facecolor=C["bg"], metadata={"Date": None})
    fig.savefig(OUT / f"{stem}.png", facecolor=C["bg"], dpi=150)
    plt.close(fig)
    svg = OUT / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    provenance = {
        "title": "What is implemented and what has run", "snapshot_date": "2026-10-04",
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "worked_example_case_id": example["id"], "model_calls_for_figure": 0,
        "formats": ["SVG", "PNG"],
    }
    (OUT / "metadata.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Generated {OUT.relative_to(ROOT)}/{stem}.{{png,svg}}")


if __name__ == "__main__":
    main()
