"""Plot a completed E1 first-stage run without additional model calls."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.decision_story import Case, branches, exact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    out = args.run / "figures"
    out.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/containment-e1-matplotlib")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.lines import Line2D
    import numpy as np

    report = json.loads((args.run / "report.json").read_text())
    rows = [json.loads(p.read_text()) for p in (args.run / "responses").glob("*.json")]
    rows = [r for r in rows if r["status"] == "valid"]
    colors = {"STOP": "#808b96", "ASK": "#2874a6", "PROBE": "#16a085", "RECOVER": "#d68910"}
    actions = list(colors)
    index = {a: i for i, a in enumerate(actions)}
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.3), layout="constrained")
    ax = axes[0, 0]
    ps, ds = np.linspace(.001, .999, 180), np.linspace(0, 8, 120)
    z = [[index[exact(Case(p=float(p), d=float(d)))["policy"]["initial_action"]]
          for p in ps] for d in ds]
    ax.pcolormesh(ps, ds, z, cmap=ListedColormap(list(colors.values())), vmin=-.5,
                  vmax=3.5, shading="nearest", alpha=.3, rasterized=True)
    for r in rows:
        if r["sweep"] != "phase":
            continue
        ax.scatter(r["case"]["p"], r["case"]["d"], s=45,
                   color=colors[r["policy"]["initial_action"]],
                   marker="o" if r["score"]["first_choice_optimal"] else "X",
                   edgecolor="white", linewidth=.5, zorder=3)
    ax.set(xlabel="Feasibility prior p", ylabel="Request cost d", ylim=(-.2, 8.2),
           title="Exact phase regions; dots = model choices\nX = strictly suboptimal first choice")
    ax.legend(handles=[Line2D([], [], marker="o", linestyle="", color=c, label=a)
                       for a, c in colors.items()], ncol=4, fontsize=8, loc="center right")

    ax = axes[0, 1]
    ordered = sorted((r for r in rows if r["sweep"] == "probe_cost"), key=lambda r: r["case"]["c"])
    for r in ordered:
        c = r["case"]["c"]
        ref = exact(Case(**r["case"]))
        for a in ref["optimal_actions"]:
            ax.scatter(c, index[a], s=140, facecolor="none", edgecolor="black", linewidth=1)
        a = r["policy"]["initial_action"]
        ax.scatter(c, index[a], s=35, color=colors[a], zorder=3)
    ax.axvline(1.2, color="#888888", linestyle="--", linewidth=1)
    ax.set(xlabel="Probe cost c (p = 0.3, d = 2, q = 0.6)", yticks=range(4), yticklabels=actions,
           ylim=(-.4, 3.4), title="Cost boundary at c = 1.2\nRings = all optimal ties; dots = model")

    ax = axes[1, 0]
    for r in rows:
        if r["sweep"] != "diagnostic_accuracy":
            continue
        for (weight, truth), key, marker in zip(branches(Case(**r["case"])),
                                                ("posterior_positive", "posterior_negative"),
                                                ("o", "s")):
            ax.scatter(truth, r["policy"][key], s=100 * weight + 15, marker=marker,
                       color="#2874a6" if marker == "o" else "#d68910", alpha=.8)
    ax.plot([0, 1], [0, 1], "--", color="#888888", linewidth=1)
    ax.set(xlabel="Exact Bayesian posterior", ylabel="Model-reported posterior",
           xlim=(-.03, 1.03), ylim=(-.03, 1.03),
           title="Noisy diagnostic probability elicitation\nCircles = positive; squares = negative")

    ax = axes[1, 1]
    groups = [g for g in report["groups"] if g != "all"]
    values = [report["groups"][g]["mean_policy_regret"] for g in groups]
    ax.barh(range(len(groups)), [v or 0 for v in values], color="#566573")
    ax.set(yticks=range(len(groups)), yticklabels=[g.replace("_", " ") for g in groups],
           xlabel="Mean exact policy-value regret (utility units)", title="Regret includes contingent branch choices")
    for i, g in enumerate(groups):
        n = report["groups"][g]["valid"]
        ax.text((values[i] or 0) + .01, i, f"n={n}", va="center", fontsize=9)
    ax.set_xlim(0, max(.1, max(v or 0 for v in values) * 1.3))
    total = report["groups"]["all"]
    fig.suptitle(f"E1 one-probe pilot | {report['model']}\n"
                 f"{total['valid']}/{total['assigned']} valid; {total['first_choice_optimal']} optimal first choices",
                 fontsize=14, fontweight="bold")
    fig.supxlabel("Synthetic policy elicitation; one response per cell. No executed containment effects or deployment safety measured.",
                  fontsize=9)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"e1-first-stage.{ext}", dpi=180)
    plt.close(fig)
    print(out / "e1-first-stage.png")


if __name__ == "__main__":
    main()
