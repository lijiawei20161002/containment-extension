"""Export audited SABench outcomes for the anonymous paper; no inference."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORTS = {
    "S01": "sabench-development-v1",
    "S02": "sabench-development-v2",
    "S03": "sabench-heldout-v2",
    "S04": "sabench-network-recovery-v1",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path, required=True)
    args = parser.parse_args()
    rows, provenance, audits, mechanisms = [], [], [], []
    for cohort, name in COHORTS.items():
        directory = ROOT / "results" / name
        evidence = json.loads((directory / "provenance.json").read_text())
        summary = json.loads((directory / "summary.json").read_text())
        assert evidence["execution"]["status"] == "finished", name
        assert sha(directory / "episodes.csv") == evidence["episodes_sha256"]
        source_rows = list(csv.DictReader((directory / "episodes.csv").open()))
        assert len(source_rows) == summary["assigned"]
        rows.extend({"cohort": cohort, **r} for r in source_rows)
        provenance.append({"cohort": cohort, "split": summary["split"],
            "assigned": summary["assigned"],
            **{k: v for k, v in evidence.items() if k != "execution"},
            "execution": {k: v for k, v in evidence["execution"].items() if k != "pid"},
            "cost": {k: summary[k] for k in ["actor_estimated_usd", "scope_estimated_usd", "requests"]}})
        audits.append({"cohort": cohort, "scope_audit": summary["scope_audit"]})
        mechanisms.append({"cohort": cohort, "mechanism_audit": summary["mechanism_audit"]})
    data = args.paper_dir / "data"
    data.mkdir(parents=True, exist_ok=True)
    with (data / "sabench_episodes.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (data / "sabench_scope_audit.json").write_text(json.dumps(audits, indent=2) + "\n")
    (data / "sabench_mechanism_audit.json").write_text(json.dumps(mechanisms, indent=2) + "\n")
    checks = []
    for model in ["astra", "fable"]:
        directory = ROOT / "runs" / f"sabench-network-check-20261111-{model}"
        check = json.loads((directory / "results.json").read_text())[0]
        checks.append({k: check[k] for k in ["provider", "requested_model", "resolved_models", "passed", "purpose"]})
        checks[-1].update(budget=json.loads((directory / "budget.json").read_text()),
                          results_sha256=sha(directory / "results.json"))
    (data / "sabench_provenance.json").write_text(json.dumps({
        "date": "2026-11-11", "assigned": len(rows), "cohorts": provenance,
        "episodes_sha256": sha(data / "sabench_episodes.csv"),
        "scope_audit_sha256": sha(data / "sabench_scope_audit.json"),
        "mechanism_audit_sha256": sha(data / "sabench_mechanism_audit.json"),
        "upstream": json.loads((ROOT / "third_party/sabench/UPSTREAM.json").read_text()),
        "protocol_sha256": sha(ROOT / "docs/sabench-transfer-protocol.md"),
        "paper_analysis_sha256": {name: sha(args.paper_dir / "analysis" / name)
                                  for name in ["sabench_summary.py", "sabench_statistics.py"]},
        "network_checks": checks,
        "notes": ["Development S01/S02 are exploratory; S03 holds out whole templates.",
            "Scopes use visible requests and workspace only, never oracle labels.",
            "Entity IDs retain upstream template tags. No external office services are called.",
            "Structural completion does not evaluate free-form message quality.",
            "Costs are conservative list-price estimates, not billing statements."]}, indent=2) + "\n")
    print(json.dumps({"episodes": len(rows), "cohorts": list(COHORTS)}))


if __name__ == "__main__":
    main()
