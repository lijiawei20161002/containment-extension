"""Export the three audited planner follow-ups without additional inference."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORTS = {"R01": ("recovery-planning-v2", 192),
           "R02": ("allocation-planning-v1", 96),
           "D01": ("scope-compiler-diagnostic", 8)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path, required=True)
    paper = parser.parse_args().paper_dir
    data = paper / "data"
    data.mkdir(exist_ok=True)
    rows, cohorts = [], []
    for code, (name, count) in COHORTS.items():
        folder = ROOT / "results" / name
        evidence = json.loads((folder / "provenance.json").read_text())
        assert sha(folder / "episodes.csv") == evidence["episodes_sha256"]
        records = list(csv.DictReader((folder / "episodes.csv").open()))
        assert len(records) == count
        for record in records:
            if code == "D01":
                record["arm"] = record.pop("condition")
                record.update(feasible="true", ambiguous="false")
            rows.append({"cohort": code, **record})
        summary = json.loads((folder / "summary.json").read_text())
        # Provenance carries hashes, not identifying raw transcripts.
        evidence.pop("execution", None)
        cohorts.append({"cohort": code, "assigned": count, "evidence": evidence,
                        "reported_summary": {k: v for k, v in summary.items() if k != "execution"}})
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (data / "planner_revision_episodes.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    audit = ROOT / "results/scope-compiler-regression"
    for name in ["summary", "contracts"]:
        (data / f"scope_compiler_{name}.json").write_bytes((audit / f"{name}.json").read_bytes())
    quota_path = ROOT / "runs/recovery-fable-diagnostic-20261111.json"
    checks = []
    for model in ["astra", "fable"]:
        folder = ROOT / "runs" / f"recovery-planning-check-20261111-{model}"
        result = json.loads((folder / "results.json").read_text())[0]
        checks.append({k: result[k] for k in ["provider", "requested_model", "resolved_models", "passed", "purpose"]})
        checks[-1].update(budget=json.loads((folder / "budget.json").read_text()),
                          results_sha256=sha(folder / "results.json"))
    files = ["planner_revision_episodes.csv", "scope_compiler_summary.json", "scope_compiler_contracts.json"]
    provenance = {"date": "2026-11-11", "assigned": len(rows), "cohorts": cohorts,
        "data_sha256": {name: sha(data / name) for name in files},
        "scope_regression_provenance": json.loads((audit / "provenance.json").read_text()) if (audit / "provenance.json").exists() else {},
        "paper_analysis_sha256": {name: sha(paper / "analysis" / name) for name in
                                  ["planner_revision_summary.py", "sabench_statistics.py"]},
        "network_checks": checks,
        "quota_diagnostic": {"sha256": sha(quota_path), **json.loads(quota_path.read_text())},
        "notes": ["R01 was fixed before inference; its eight generators are related.",
                  "R02 was designed after observing R01's ceiling and is exploratory.",
                  "D01 is a retrospective regression on four already inspected contracts, selected by structural compiler changes.",
                  "No original outcome is replaced. The superseded recovery v1 plan made no model calls.",
                  "API errors leave negative endpoints unknown; estimated costs include failed-call reservations."]}
    (data / "planner_revision_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({"episodes": len(rows), "cohorts": list(COHORTS)}))


if __name__ == "__main__":
    main()
