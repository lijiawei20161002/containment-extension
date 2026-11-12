"""Export anonymous outcomes from the November 11 native API cohorts.

Reads completed, frozen evidence only; makes no model calls. Provider payloads,
credentials and local paths are excluded from the paper data.
"""
import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from containment_extension.evaluation.common import digest


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tri(value):
    return "" if value is None else str(bool(value)).lower()


def is_refusal(raw):
    return raw.get("stop_reason") == "refusal" or any(
        part.get("type") == "refusal"
        for item in raw.get("output", []) if item.get("type") == "message"
        for part in item.get("content", []))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path, required=True)
    args = parser.parse_args()
    rows, provenance = [], []
    for cohort, label in [("F01", "fable-5-2"), ("F02", "opus-5-5"),
                          ("F03", "gpt-6-astra")]:
        root = ROOT / "runs" / f"native-frontier-20261111-{label}"
        plan = json.loads((root / "plan.json").read_text())
        summary = json.loads((root / "summary.json").read_text())
        expected = json.loads((root / "plan.sha256.json").read_text())["sha256"]
        assert digest(plan) == expected
        assert summary["status"] == "finished" and summary["recorded"] == summary["assigned"] == 48
        for name, expected_hash in plan["source_hashes"].items():
            assert sha(root / "source/containment_extension" / name) == expected_hash
        models, evidence, errors = set(), {}, Counter()
        for row in summary["records"]:
            directory = root / row["run"]
            result_file = directory / "result.json"
            result = json.loads(result_file.read_text()) if result_file.exists() else None
            transcript = [json.loads(line) for line in (directory / "transcript.jsonl").read_text().splitlines()]
            responses = [x["provider_response"] for x in transcript if "provider_response" in x]
            refusals = [i for i, raw in enumerate(responses) if is_refusal(raw)]
            assert bool(refusals) == (row["stop"] == "provider_refusal")
            if result is not None:
                models.update(result["resolved_models"])
                if result.get("error"):
                    errors[result["error"]] += 1
                assert result["steps"] == len(responses)
                assert row["unauthorized_effect"] is (True if result["unauthorized_effect"] else
                    False if row["stop"] in {"model_finished", "scorer_success"} else None)
                inputs, outputs = result["input_tokens"], result["output_tokens"]
            else:
                # The frozen runner never replays a started episode after interruption.
                assert row["stop"] == "interrupted_unknown"
                assert row["unauthorized_effect"] in (None, True)
                models.update(raw["model"] for raw in responses)
                inputs = sum((raw.get("usage") or {}).get("input_tokens", 0) for raw in responses)
                outputs = sum((raw.get("usage") or {}).get("output_tokens", 0) for raw in responses)
            rows.append({"cohort": cohort, "model": plan["config"]["actor"]["model"], "arm": row["arm"],
                "variant": row["variant"], "seed": row["seed"], "status": row["stop"],
                "incident": tri(row["unauthorized_effect"]),
                "authorized_completion": tri(row["authorized_completion"]),
                "outside_proposals": row["out_of_scope_proposals"],
                "continuation_actions": row["continuation_attempts"],
                "refusal_turn": refusals[0] + 1 if refusals else "",
                "refusal_category": (responses[refusals[0]].get("stop_details") or {}).get("category", "") if refusals else "",
                "input_tokens": inputs, "output_tokens": outputs})
            evidence[row["run"]] = {name: sha(directory / name) if (directory / name).exists() else None for name in
                                   ["result.json", "transcript.jsonl", "manifest.json", "services.sqlite3"]}
        assert models == {plan["config"]["actor"]["model"]}
        provenance.append({"cohort": cohort, "model": sorted(models), "plan_sha256": expected,
            "summary_file_sha256": sha(root / "summary.json"), "source_hashes": plan["source_hashes"],
            "config": {k: v for k, v in plan["config"].items() if k != "authorization"},
            "started_at": summary["started_at"], "finished_at": summary["finished_at"],
            "budget": summary["budget"], "error_counts": dict(errors), "evidence_hashes": evidence,
            "operator_events_sha256": sha(root / "operator-events.json")
                if (root / "operator-events.json").exists() else None})
    destination = args.paper_dir / "data"
    with (destination / "frontier_episodes.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    diagnostic = ROOT / "runs/astra-http400-diagnostic-20261111.json"
    diagnosis = json.loads(diagnostic.read_text())
    assert diagnosis["http_status"] == 400 and diagnosis["error"]["code"] == "cyber_policy"
    (destination / "frontier_provenance.json").write_text(json.dumps({
        "date": "2026-11-11", "kind": "fresh focused replication; separate from historical actor CSV",
        "episode_count": len(rows), "csv_sha256": sha(destination / "frontier_episodes.csv"),
        "cohorts": provenance,
        "access_diagnostic": {"cohort": "F03", "episode": "run-0001",
            "purpose": "One diagnostic repeat of a failed request; no tool actions executed; excluded from behavioral outcomes",
            "http_status": diagnosis["http_status"], "code": diagnosis["error"]["code"],
            "evidence_sha256": sha(diagnostic), "budget": diagnosis["budget"],
            "limitation": "Other HTTP 400 bodies were not retained; their causes are not individually confirmed."},
        "notes": ["48 assignments per model; two arms, only zero stop reward.",
                  "No replacement of started episodes; no alternate-model fallback.",
                  "Neutral access/tool checks are excluded from the behavioral assignments.",
                  "One Astra episode was interrupted during error diagnosis and remains incomplete; a null result hash denotes the missing result file.",
                  "An empty Boolean field means unknown because the run ended early.",
                  "A refusal is not a model-generated, evidence-supported blocker report."]}, indent=2) + "\n")
    print(json.dumps({"exported": len(rows), "cohorts": len(provenance)}))


if __name__ == "__main__":
    main()
