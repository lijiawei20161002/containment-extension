"""Export standalone research figures from the completed live follow-up summaries."""
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/trust4rsi-followup-matplotlib")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/experiments/followup-v2"


def main():
    files = ["results/baseline-diagnostic-v2/summary.json",
             "results/transcript-audit-v4/summary.json"]
    actor, judge = [json.loads((ROOT / p).read_text()) for p in files]
    assert actor["status"] == judge["status"] == "finished"
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.fonttype": "none", "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.3), gridspec_kw={"width_ratios": [1, 1, .85]})
    bank = {(g["arm"], g["variant"]): g for g in actor["groups"]}
    arms = ["current_original", "archived_N"]
    colors = ["#365e9e", "#b34831"]
    for i, arm in enumerate(arms):
        stat = bank[arm, "impossible"]["incidents"]
        lo, hi = stat["wilson95"]
        axes[0].errorbar(stat["rate"], 1-i,
                         xerr=[[max(0, stat['rate']-lo)], [max(0, hi-stat['rate'])]],
                         fmt='o', color=colors[i], capsize=5, markersize=7)
        axes[0].text(.03, 1-i+.18,
                     f"{stat['positive']}/{stat['observed']}; unknown {stat['unknown']}",
                     color=colors[i])
        for offset, variant, marker in [(.12, "recoverable", 'o'), (-.12, "solvable", 's')]:
            utility = bank[arm, variant]["authorized_completion"]
            lo, hi = utility['wilson95']
            axes[1].errorbar(utility['rate'], 1-i+offset,
                             xerr=[[max(0, utility['rate']-lo)], [max(0, hi-utility['rate'])]],
                             fmt=marker, color=colors[i], capsize=4,
                             label=variant if i == 0 else None)
            axes[1].text(.03, 1-i+offset,
                         f"{variant}: {utility['positive']}/{utility['observed']}", fontsize=8)
    for ax in axes[:2]:
        ax.set_xlim(-.03, 1.04)
        ax.set_ylim(-.5, 1.5)
        ax.set_yticks([1, 0], ["Current note", "Archived N"])
        ax.set_xticks([0, .25, .5, .75, 1])
        ax.grid(axis='x', alpha=.2)
    axes[0].set_title("A  Impossible-task incidents", loc='left', fontweight='bold')
    axes[0].set_xlabel("Verified incident rate (95% Wilson)")
    axes[1].set_title("B  Authorized completion", loc='left', fontweight='bold')
    axes[1].set_xlabel("Control utility (95% Wilson)")
    axes[1].legend(loc='lower left', fontsize=8)
    m = judge['target_matrix']
    matrix = np.array([[m['TP'], m['FN']], [m['FP'], m['TN']]])
    axes[2].imshow(matrix, cmap='Blues', vmin=0)
    for row in range(2):
        for col in range(2):
            axes[2].text(col, row, str(matrix[row, col]), ha='center', va='center', fontsize=23,
                         color='white' if matrix[row, col] > matrix.max()/2 else '#111111')
    axes[2].set_xticks([0, 1], ['Incident', 'Clean'])
    axes[2].set_yticks([0, 1], ['Incident', 'Clean'])
    axes[2].set_xlabel('Transcript judge')
    axes[2].set_ylabel('Service observer')
    axes[2].set_title('C  New-target confusion', loc='left', fontweight='bold')
    fig.suptitle('Real hosted-model responses in a controlled local service fixture', fontsize=13)
    fig.text(.02, .02,
             f"48 actor assignments; 16 impossible + 4 recoverable + 4 easy inputs per note. "
             f"Judge matrix: 48 new targets, unknown {judge['target_unknown']}; "
             "fixed threshold 0.5, calibration failed.\n"
             "20 archive cases excluded from the matrix. Interrupted actor v1 reported separately.",
             fontsize=8)
    fig.tight_layout(rect=(0, .08, 1, .94))
    for ext in ('png', 'svg'):
        fig.savefig(OUT / f'live-followup-results.{ext}', dpi=200)
    plt.close(fig)
    (OUT/'source-data.json').write_text(json.dumps({
        'actor_groups': actor['groups'], 'paired': actor['paired'],
        'judge_matrix': judge['target_matrix'], 'judge_unknown': judge['target_unknown'],
        'judge_calibration_passed': judge['calibration_passed'],
        'judge_threshold': judge['threshold'],
        'source_hashes': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
    }, indent=2)+'\n')
    print(OUT)


if __name__ == '__main__':
    main()
