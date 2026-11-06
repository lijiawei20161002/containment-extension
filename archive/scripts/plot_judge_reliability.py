"""Result figure for the judge reliability studies (v1 baseline and v2 grant-note runs).

Reads the frozen plan.json and judgments/ of each study, rebuilds per-item rows with the
study's own `item_rows`, and draws one figure:

  the 16 scripted calibration cases, correct / wrong per judge condition (panels A-C of the
  earlier four-panel version were dropped on request; the summary JSON still carries their numbers)

Writes judge-reliability.{png,svg,json}.\nUsage: python3 scripts/plot_judge_reliability.py [--out figures/experiments/judge-reliability]
Only finished or partially finished studies that exist on disk are drawn.
"""
import argparse
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.judge_reliability import collect, item_rows  # noqa: E402
from containment_extension.evaluation.benchmark_metrics import bootstrap_interval  # noqa: E402

# Reference palette (dataviz skill, light mode).
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"          # categorical slots 1 and 2
SEQ = ["#f0efec", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
GOOD, CRITICAL = "#0ca30c", "#d03b3b"       # status palette, always paired with a glyph

CONDITIONS = [
    # label, run directory, view, group
    ("Haiku 4.5\ntranscript", "runs/judge-reliability-v1-haiku-4-5-20261102", "transcript", "v1"),
    ("Sonnet 4.6\ntranscript", "runs/judge-reliability-v1-sonnet-4-6-20261102", "transcript", "v1"),
    ("Haiku 4.5\ntranscript + journal", "runs/judge-reliability-v1-haiku-4-5-20261102", "transcript_journal", "v1"),
    ("Sonnet 4.6\ntranscript + journal", "runs/judge-reliability-v1-sonnet-4-6-20261102", "transcript_journal", "v1"),
    ("Haiku 4.5\ntranscript + grant note (instruction)", "runs/judge-reliability-v2-note-haiku-4-5-20261104", "transcript", "v2"),
    ("Haiku 4.5\ntranscript + grant note (packet)", "runs/judge-reliability-v2-packet-haiku-4-5-20261104", "transcript", "v2"),
    ("Sonnet 4.6\ntranscript + grant note (instruction)", "runs/judge-reliability-v2-note-sonnet-4-6-20261104", "transcript", "v2"),
    ("Haiku 4.5\ngrant note (instruction), reason-first schema", "runs/judge-reliability-v3-reasonfirst-haiku-4-5-20261104", "transcript", "v3"),
    ("Sonnet 4.6\ngrant note (instruction), reason-first schema", "runs/judge-reliability-v3-reasonfirst-sonnet-4-6-20261104", "transcript", "v3"),
]


def used_alternate(row):
    item_path = Path(row["_path"])
    transcript = json.loads((item_path.parent / "transcript.json").read_text())
    return any(e.get("operation") == "ALTERNATE" for e in transcript if isinstance(e, dict))


def benign_cell(row):
    if row["truth"]:
        return "incident"
    if row["environment"] and row["environment"].get("granted"):
        return "granted_alt" if used_alternate(row) else "granted_other"
    return "ungranted"


def load_condition(label, run, view, group):
    output = ROOT / run
    if not (output / "plan.json").exists():
        return None
    plan = json.loads((output / "plan.json").read_text())
    if view not in plan["config"]["views"]:
        return None
    table = collect(output, plan)
    rows = item_rows(plan, table, view)
    paths = {i["id"]: i["path"] for i in plan["items"]}
    for r in rows:
        r["_path"] = paths[r["id"]]
    dev = [r for r in rows if r["kind"] == "development"]
    cal = [r for r in rows if r["kind"] == "calibration"]
    if not dev:
        return None
    boot = plan["config"].get("bootstrap", {"seed": 0, "replicates": 1000})

    def fa(sub):
        benign = [r for r in sub if not r["truth"] and r["labels"]["majority"] is not None]
        return sum(r["labels"]["majority"] for r in benign) / len(benign) if benign else None

    def miss(sub):
        inc = [r for r in sub if r["truth"] and r["labels"]["majority"] is not None]
        return sum(not r["labels"]["majority"] for r in inc) / len(inc) if inc else None

    for r in dev:
        r["cell"] = benign_cell(r)
    cells = {}
    for name in ("granted_alt", "granted_other", "ungranted"):
        members = [r for r in dev if r["cell"] == name]
        cells[name] = (sum(bool(r["labels"]["majority"]) for r in members), len(members))
    finished = (output / "completed.json").exists()
    budget = json.loads((output / "budget.json").read_text()) if (output / "budget.json").exists() else {}
    return {"label": label, "group": group, "model": plan["config"]["model"], "view": view,
            "draws": plan["config"]["draws"], "finished": finished,
            "judged_dev": len(dev), "judged_cal": len(cal),
            "fa": fa(dev), "fa_ci": bootstrap_interval(dev, fa, seed=boot["seed"], replicates=boot["replicates"]),
            "miss": miss(dev), "miss_ci": bootstrap_interval(dev, miss, seed=boot["seed"], replicates=boot["replicates"]),
            "cells": cells,
            "scores_benign": [r["score"] for r in dev if not r["truth"] and r["score"] is not None],
            "scores_incident": [r["score"] for r in dev if r["truth"] and r["score"] is not None],
            "split": sum(r["split"] for r in dev),
            "calibration": {r["id"].split("/")[-1]: (r["labels"]["majority"], r["truth"]) for r in cal},
            "usd": budget.get("estimated_usd")}


def style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
        ax.spines[side].set_linewidth(1)
    ax.tick_params(colors=INK2, labelsize=8.5, length=0)
    ax.grid(False)


def panel_rates(ax, conds):
    style(ax)
    n = len(conds)
    ys = list(range(n))[::-1]
    for y, c in zip(ys, conds):
        for metric, color, dy in (("fa", BLUE, 0.16), ("miss", ORANGE, -0.16)):
            v = c[metric]
            if v is None:
                continue
            lo, hi = c[metric + "_ci"]["low"], c[metric + "_ci"]["high"]
            ax.plot([lo, hi], [y + dy, y + dy], color=color, lw=2, solid_capstyle="round", zorder=2)
            ax.plot([v], [y + dy], "o", ms=8, color=color, mec=SURFACE, mew=2, zorder=3)
        label = f"{c['fa'] * 100:.0f}%" if c["fa"] is not None else ""
        x_label = min(max(c["fa_ci"]["high"], c["fa"] or 0) + 0.015, 0.40)
        ax.text(x_label, y + 0.16, label, va="center", fontsize=8, color=INK2,
                ha="left" if x_label < 0.40 else "right",
                bbox={"facecolor": SURFACE, "edgecolor": "none", "pad": 1} if x_label >= 0.40 else None)
    ax.set_yticks(ys)
    ax.set_yticklabels([c["label"] for c in conds], fontsize=8.5, color=INK)
    ax.set_xlim(-0.01, 0.45)
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4])
    ax.set_xticklabels(["0", "10%", "20%", "30%", "40%"])
    ax.xaxis.grid(True, color=GRID, lw=1)
    ax.set_axisbelow(True)
    ax.set_xlabel("rate on the 160 development episodes (majority of draws)", fontsize=8.5, color=INK2)
    # group separator between v1 and v2
    for group, text in (("v2", "grant-semantics sentence added"), ("v3", "+ reason written before the label")):
        first = next((i for i, c in enumerate(conds) if c["group"] == group), None)
        if first is not None:
            ax.axhline(ys[first] + 0.5, color=AXIS, lw=1)
            ax.text(0.44, ys[first] + 0.62, text, ha="right", fontsize=7.5, color=MUTED)
    ax.legend(handles=[Line2D([], [], marker="o", color=BLUE, lw=2, ms=7, label="false-alarm rate"),
                       Line2D([], [], marker="o", color=ORANGE, lw=2, ms=7, label="miss rate")],
              loc="lower right", frameon=False, fontsize=8)
    ax.set_title("A  Error rates with 95% cluster-bootstrap intervals", loc="left", fontsize=10, color=INK, weight="bold")


def panel_cells(ax, conds):
    style(ax)
    cols = [("granted_alt", "pre-granted,\nused ALTERNATE"), ("granted_other", "pre-granted,\nno ALTERNATE"),
            ("ungranted", "ungranted\nbenign")]
    n = len(conds)
    for i, c in enumerate(conds):
        y = n - 1 - i
        for j, (key, _) in enumerate(cols):
            k, m = c["cells"][key]
            rate = k / m if m else 0
            color = SEQ[min(7, int(round(rate * 7)))]
            ax.add_patch(plt.Rectangle((j + 0.04, y + 0.04), 0.92, 0.92, color=color, lw=0))
            ax.text(j + 0.5, y + 0.5, f"{k}/{m}", ha="center", va="center", fontsize=8.5,
                    color=("#ffffff" if rate > 0.45 else INK))
    ax.set_xlim(0, len(cols))
    ax.set_ylim(0, n)
    ax.set_xticks([j + 0.5 for j in range(len(cols))])
    ax.set_xticklabels([t for _, t in cols], fontsize=8, color=INK)
    ax.set_yticks([n - 1 - i + 0.5 for i in range(n)])
    ax.set_yticklabels([c["label"].replace("\n", " · ") for c in conds], fontsize=7.5, color=INK)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_title("B  False alarms by benign cell (flagged/items)", loc="left", fontsize=10, color=INK, weight="bold")


def panel_scores(ax, conds):
    style(ax)
    import random
    rng = random.Random(4)
    n = len(conds)
    for i, c in enumerate(conds):
        y = n - 1 - i
        for scores, color, dy in ((c["scores_benign"], BLUE, 0.14), (c["scores_incident"], ORANGE, -0.14)):
            xs = scores
            ys = [y + dy + rng.uniform(-0.09, 0.09) for _ in xs]
            ax.scatter(xs, ys, s=22, color=color, alpha=0.55, edgecolors=SURFACE, linewidths=1, zorder=3)
    ax.set_yticks([n - 1 - i for i in range(n)])
    ax.set_yticklabels([c["label"].replace("\n", " · ") for c in conds], fontsize=7.5, color=INK)
    ax.set_xlim(-0.03, 1.03)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.xaxis.grid(True, color=GRID, lw=1)
    ax.set_axisbelow(True)
    ax.set_xlabel("mean reported incident probability per episode", fontsize=8.5, color=INK2)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=BLUE, ms=6, label="benign (journal: no incident)"),
                       Line2D([], [], marker="o", ls="", color=ORANGE, ms=6, label="incident (journal: unauthorized effect)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=8)
    ax.set_title("C  Reported probability, benign vs incident episodes", loc="left", fontsize=10, color=INK, weight="bold")


def panel_calibration(ax, conds, granted_cases):
    style(ax)
    cases = sorted({k for c in conds for k in c["calibration"]})
    n = len(conds)
    for i, c in enumerate(conds):
        y = n - 1 - i
        for j, case in enumerate(cases):
            if case not in c["calibration"]:
                continue
            label, truth = c["calibration"][case]
            if label is None:
                ax.text(j + 0.5, y + 0.5, "?", ha="center", va="center", fontsize=9, color=MUTED)
            elif label is truth:
                ax.text(j + 0.5, y + 0.5, "✓", ha="center", va="center", fontsize=9, color=GOOD)
            else:
                ax.add_patch(plt.Rectangle((j + 0.08, y + 0.08), 0.84, 0.84, color="#fbe3e3", lw=0))
                ax.text(j + 0.5, y + 0.5, "✗", ha="center", va="center", fontsize=9, color=CRITICAL, weight="bold")
    ax.set_xlim(0, len(cases))
    ax.set_ylim(0, n)
    ax.set_xticks([j + 0.5 for j in range(len(cases))])
    ax.set_xticklabels([case.replace("calibration-", "") + ("*" if case in granted_cases else "")
                        for case in cases], fontsize=7.5, color=INK)
    ax.set_yticks([n - 1 - i + 0.5 for i in range(n)])
    ax.set_yticklabels([c["label"].replace("\n", " · ") for c in conds], fontsize=7.5, color=INK)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_xlabel("scripted calibration case (* = alternate pre-granted in the task text)", fontsize=8.5, color=INK2)
    ax.legend(handles=[Line2D([], [], marker="$✓$", ls="", color=GOOD, ms=8, label="label matches journal"),
                       Patch(facecolor="#fbe3e3", edgecolor=CRITICAL, label="✗ label contradicts journal")],
              loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False, fontsize=8)
    ax.set_title("D  The 16 scripted calibration fixtures", loc="left", fontsize=10, color=INK, weight="bold")


def granted_calibration_cases(conds):
    for _, run, _, _ in CONDITIONS:
        plan_path = ROOT / run / "plan.json"
        if plan_path.exists():
            plan = json.loads(plan_path.read_text())
            out = set()
            for item in plan["items"]:
                if item["kind"] == "calibration":
                    fixture = json.loads(Path(item["path"]).read_text())
                    if "explicitly permitted" in fixture["trusted_task"]:
                        out.add(item["id"].split("/")[-1])
            return out
    return set()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=ROOT / "figures/experiments/judge-reliability")
    args = p.parse_args()
    conds = [c for c in (load_condition(*spec) for spec in CONDITIONS) if c]
    if not conds:
        raise SystemExit("no judge studies found")
    granted = granted_calibration_cases(conds)

    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE})
    fig, ax = plt.subplots(figsize=(11, 5.4))
    panel_calibration(ax, conds, granted)
    ax.set_title("The 16 scripted calibration fixtures: judge label versus the effect journal",
                 loc="left", fontsize=11, color=INK, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 1))
    args.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out / "judge-reliability.png", dpi=180)
    fig.savefig(args.out / "judge-reliability.svg")
    summary = [{k: v for k, v in c.items() if k not in ("scores_benign", "scores_incident")} for c in conds]
    (args.out / "judge-reliability.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps([{"label": c["label"].replace("\n", " · "), "finished": c["finished"], "dev": c["judged_dev"],
                       "fa": c["fa"], "miss": c["miss"], "cells": c["cells"], "split": c["split"], "usd": c["usd"]}
                      for c in conds], indent=1))


if __name__ == "__main__":
    main()
