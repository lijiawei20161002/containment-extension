"""Execute offline stages and preserve source-bound evidence for both designs."""

from __future__ import annotations

from pathlib import Path

from . import archive, artifact, workflow
from .common import export_manifest

REPOSITORY = Path(__file__).resolve().parents[3]
DESIGNS = {
    "counterfactual": "counterfactual-evaluation-v1.design.json",
    "researcharena": "researcharena-monitoring-v1.design.json",
}


def run_offline(root, design, *, repository=REPOSITORY):
    if design not in DESIGNS:
        raise ValueError("Unknown evaluation design")
    root, repository = Path(root), Path(repository)
    root.mkdir(parents=True, exist_ok=False)
    if design == "counterfactual":
        summary = workflow.build(root / "workflow")
    else:
        summary = artifact.build(root / "artifacts")
        archived = archive.build(root / "archive", repository / "results/incident-monitor-inputs-v1",
                                 repository / "results")
        summary["archive"] = archived
        summary["passed"] = summary["passed"] and archived["baseline_label_gate_passed"]
        summary["completed_stages"] = (["RA0"] if archived["baseline_label_gate_passed"] else []) + ["RA2"]
    return export_manifest(root, repository / "experiments" / DESIGNS[design], summary)
