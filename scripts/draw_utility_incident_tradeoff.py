"""E1: archived policy trade-offs, preserving study populations and endpoints."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from containment_extension.feedback_metrics import binary  # noqa: E402


def build_cells(root=ROOT):
    sources = [
        root / "results" / study / name
        for study, name in (
            ("incident-study-v1", "summary.json"),
            ("scope-levels-v1", "summary.json"),
            ("link-study-v1", "analysis.json"),
        )
    ]
    cells = []
    for source in sources:
        study = source.parent.name
        rows = json.loads(source.read_text())["records"]
        arm = "level" if study == "scope-levels-v1" else "arm"
        for model, policy in sorted({(r["model"], r[arm]) for r in rows}):
            selected = [r for r in rows if r["model"] == model and r[arm] == policy]
            impossible = [r for r in selected if r["variant"] in {"impossible", "stalled"}]
            controls = [r for r in selected if r["variant"] in {"recoverable", "solvable"}]
            incident_key = {
                "incident-study-v1": "any_effect",
                "scope-levels-v1": "unauthorized_effect",
                "link-study-v1": "outside_effect",
            }[study]
            utility_key = "authorized_completion" if arm == "level" else "strict_success"

            # Archived link-study utility booleans on incomplete runs are not clean negatives.
            def utility(row, utility_key=utility_key, study=study):
                value = row[utility_key]
                if (
                    study == "link-study-v1"
                    and not value
                    and row["stop"] not in {"scorer_success", "model_finished"}
                    and not row["outside_effect"]
                ):
                    return None
                return value

            cells.append(
                {
                    "study": study,
                    "model": model,
                    "policy": policy,
                    "incident_population": "impossible/stalled only",
                    "incident_endpoint": incident_key,
                    "utility_population": "recoverable + solvable controls",
                    "incidents": binary([r[incident_key] for r in impossible]),
                    "utility": binary([utility(r) for r in controls]),
                    "source": source.relative_to(root).as_posix(),
                }
            )
    link = json.loads(sources[-1].read_text())
    return {
        "cells": cells,
        "link_early_read_diagnostic": [
            {
                "policy": row["arm"],
                "population": "both models and all variants (32 assigned)",
                "early_upstream": row["early_upstream"],
            }
            for row in link["pooled"]
        ],
        "sources": {
            p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources
        },
        "notes": "No curve or pooling across studies. Intervals use observed outcomes; unknowns "
        "and assigned-population bounds remain explicit. Early read diagnostic is a "
        "different endpoint and population from full-rollout verified incidents.",
    }


def draw(output, data):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "svg.fonttype": "none"})
    fig, axes = plt.subplots(1, 3, figsize=(16, 6.5), sharey=True)
    studies = ["incident-study-v1", "scope-levels-v1", "link-study-v1"]
    for ax, study in zip(axes, studies, strict=True):
        points = [r for r in data["cells"] if r["study"] == study]
        policies = sorted({r["policy"] for r in points})
        colors = {p: plt.get_cmap("tab10")(i) for i, p in enumerate(policies)}
        for row in points:
            x, y = row["utility"], row["incidents"]
            if x["rate"] is None or y["rate"] is None:
                continue
            hollow = row["model"].startswith("gpt")
            ax.errorbar(
                x["rate"],
                y["rate"],
                xerr=[
                    [max(0, x["rate"] - x["wilson95"][0])],
                    [max(0, x["wilson95"][1] - x["rate"])],
                ],
                yerr=[
                    [max(0, y["rate"] - y["wilson95"][0])],
                    [max(0, y["wilson95"][1] - y["rate"])],
                ],
                fmt="s" if hollow else "o",
                color=colors[row["policy"]],
                mfc="white" if hollow else colors[row["policy"]],
                markersize=7,
                capsize=3,
                alpha=0.75,
            )
        ax.set(
            title=study,
            xlabel="Authorized control completion",
            xlim=(-0.04, 1.04),
            ylim=(-0.04, 1.04),
        )
        ax.grid(alpha=0.18)
        ax.legend(
            handles=[
                Line2D([0], [0], color=colors[p], marker="o", linestyle="", label=p)
                for p in policies
            ],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.16),
            ncol=2,
            fontsize=9,
        )
        notes = [
            f"{r['policy']} ({'GPT' if r['model'].startswith('gpt') else 'Haiku'}): "
            f"I={r['incidents']['positive']}/{r['incidents']['observed']}, "
            f"U={r['utility']['positive']}/{r['utility']['observed']}; "
            f"unknown I/U={r['incidents']['unknown']}/{r['utility']['unknown']}"
            for r in points
        ]
        ax.text(0, -0.42, "\n".join(notes), transform=ax.transAxes, fontsize=7.5, va="top")
    axes[0].set_ylabel("Verified incident rate on impossible/stalled tasks")
    fig.suptitle(
        "Archived instruction policies: utility and verified incidents\n"
        "95% Wilson intervals · filled circles: Haiku 4.5 · hollow squares: GPT-4.1 mini\n"
        "Coincident points are retained at their measured coordinates",
        fontsize=13,
    )
    fig.subplots_adjust(top=0.8, bottom=0.47, wspace=0.12)
    for ext in ("png", "svg"):
        fig.savefig(output / f"utility-incident-tradeoff.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)
    (output / "cells.json").write_text(json.dumps(data, indent=2) + "\n")
    (output / "metadata.json").write_text(
        json.dumps(
            {
                "generator": "scripts/draw_utility_incident_tradeoff.py",
                "inference_calls": 0,
                "sources": data["sources"],
                "notes": data["notes"],
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "figures/experiments/tradeoff-v1")
    draw(parser.parse_args().output, build_cells())
