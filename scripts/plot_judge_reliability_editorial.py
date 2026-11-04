"""Create an editorial-style companion to the judge calibration figure.

Run from the repository root after plot_judge_reliability.py:
    python scripts/plot_judge_reliability_editorial.py
The source summary and the study plans remain the source of the plotted data.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from plot_judge_reliability import granted_calibration_cases

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/experiments/judge-reliability"


def main():
    conditions = json.loads((OUT / "judge-reliability.json").read_text())
    cases = sorted({case for c in conditions for case in c["calibration"]})
    granted = granted_calibration_cases(conditions)
    if not granted:
        raise SystemExit("No pre-granted calibration cases found in the study plans")

    ink = "#17242a"
    muted = "#647477"
    rule = "#dce5e3"
    blue = "#487c83"
    blue_light = "#e5f0ee"
    red = "#ae5145"
    red_light = "#f8e9e4"
    background = "#ffffff"

    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "figure.facecolor": background, "savefig.facecolor": background})
    fig, ax = plt.subplots(figsize=(14.4, 8.15))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_xlim(0, 28)
    ax.set_ylim(0, 15.1)
    ax.axis("off")

    ax.text(0.9, 14.35, "JUDGE RELIABILITY  /  CALIBRATION", color=blue,
            fontsize=9.5, weight="bold", va="center")
    ax.text(0.9, 13.43, "How consistently do judges match the journal?",
            fontsize=23, weight="medium", color=ink, va="center")
    ax.text(0.9, 12.72, "Majority label on 16 scripted cases, by model and evaluation setup",
            fontsize=11.2, color=muted, va="center")
    ax.plot([0.9, 27.1], [12.18, 12.18], color=rule, lw=1)

    case_x0, step = 12.12, 0.78
    xs = [case_x0 + i * step for i in range(len(cases))]
    row_top, row_step = 10.45, 0.84
    ax.text(0.9, 11.51, "MODEL", fontsize=8.3, color=muted, weight="bold")
    ax.text(3.55, 11.51, "EVALUATION SETUP", fontsize=8.3, color=muted, weight="bold")
    ax.text(case_x0, 11.93, "CALIBRATION CASE", fontsize=8.3, color=muted, weight="bold")
    ax.text(26.1, 11.51, "MATCHES", fontsize=8.3, color=muted, weight="bold", ha="right")
    for x, case in zip(xs, cases):
        is_granted = case in granted
        if is_granted:
            ax.add_patch(Rectangle((x - .36, 2.76), .72, 8.47,
                                   facecolor="#f5f8f7", edgecolor="none", zorder=0))
        ax.text(x, 11.49, case.replace("calibration-", "") + ("*" if is_granted else ""),
                ha="center", va="center", fontsize=9, color=ink if is_granted else muted,
                weight="bold" if is_granted else "normal")

    last_group = None
    for i, condition in enumerate(conditions):
        y = row_top - i * row_step
        group = condition["group"]
        if last_group is not None and group != last_group:
            ax.plot([0.9, 26.25], [y + row_step / 2, y + row_step / 2], color=rule, lw=1)
        last_group = group
        model, setup = condition["label"].split("\n", 1)
        setup = setup.replace("transcript + grant note", "Transcript + grant note")
        setup = setup.replace("grant note (instruction), reason-first schema",
                              "Grant note (instruction) · reason-first")
        setup = setup.replace("transcript + journal", "Transcript + journal")
        if setup == "transcript":
            setup = "Transcript"
        ax.text(0.9, y, model, fontsize=10.4, color=ink, weight="medium", va="center")
        ax.text(3.55, y, setup, fontsize=9.8, color=ink, va="center")
        matches = 0
        known = 0
        for x, case in zip(xs, cases):
            result = condition["calibration"].get(case)
            if result is None or result[0] is None:
                ax.text(x, y, "–", ha="center", va="center", color=muted, fontsize=11)
                continue
            label, truth = result
            match = label == truth
            known += 1
            matches += int(match)
            ax.add_patch(FancyBboxPatch((x - .26, y - .26), .52, .52,
                boxstyle="round,pad=0,rounding_size=0.09",
                facecolor=blue_light if match else red_light, edgecolor="none"))
            if match:
                ax.add_patch(Circle((x, y), .057, facecolor=blue, edgecolor="none"))
            else:
                ax.text(x, y, "×", color=red, fontsize=14, ha="center", va="center")
        ax.text(26.1, y, f"{matches}/{known}", ha="right", va="center", fontsize=10.4,
                weight="medium", color=ink)

    ax.plot([0.9, 27.1], [2.55, 2.55], color=rule, lw=1)
    ax.add_patch(FancyBboxPatch((.9, 1.75), .45, .45,
        boxstyle="round,pad=0,rounding_size=0.07", facecolor=blue_light, edgecolor="none"))
    ax.add_patch(Circle((1.125, 1.975), .05, facecolor=blue, edgecolor="none"))
    ax.text(1.53, 1.975, "Label matches journal", color=ink, fontsize=10, va="center")
    ax.add_patch(FancyBboxPatch((6.4, 1.75), .45, .45,
        boxstyle="round,pad=0,rounding_size=0.07", facecolor=red_light, edgecolor="none"))
    ax.text(6.625, 1.975, "×", color=red, fontsize=13, ha="center", va="center")
    ax.text(7.03, 1.975, "Label contradicts journal", color=ink, fontsize=10, va="center")
    ax.text(.9, 1.05, "* Alternate was pre-granted in the task text.  —  indicates a missing label.",
            fontsize=9.5, color=muted, va="center")
    for suffix in ("png", "svg"):
        fig.savefig(OUT / f"judge-reliability-editorial.{suffix}", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
