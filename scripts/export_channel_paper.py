"""Export the channel comparison and its complete exploratory selection history."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def portable(value):
    if isinstance(value, dict):
        return {k: portable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [portable(v) for v in value]
    return value.replace(str(ROOT) + "/", "") if isinstance(value, str) else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path, required=True)
    paper = parser.parse_args().paper_dir
    data = paper / "data"
    sources = [
        ("C01", "astra-challenges-v1", "cases.json", "authority", 32),
        ("C02", "astra-challenges-v1", "cases.json", "ambiguity", 16),
        ("C03", "ambiguity-planner-comparison-v1", "episodes.json", None, 48),
        ("C04", "followon-comparison-v1", "episodes.json", None, 24),
        ("C05", "frontier-incident-discovery-v1", "episodes.json", None, 96),
        ("C06", "channel-algorithms-v1", "episodes.json", None, 160),
    ]
    development, blocks = [], []
    for code, name, filename, subset, expected in sources:
        folder = ROOT / "results" / name
        provenance = read(folder / "provenance.json")
        for file, expected_hash in provenance["export_hashes"].items():
            assert sha(folder / file) == expected_hash, (name, file)
        rows = read(folder / filename)
        if subset:
            rows = [r for r in rows if r["cohort"] == subset]
        assert len(rows) == expected
        if code != "C06":
            development.append({"cohort": code, "source": name, "records": rows})
        blocks.append({"cohort": code, "source": name, "assigned": expected,
                       "source_data_sha256": sha(folder / filename), "provenance": portable(provenance)})
    folder = ROOT / "results/channel-algorithms-v1"
    rows = read(folder / "episodes.json")
    columns = ["cohort", "run", "task_id", "template_id", "model_key", "arm", "ambiguous",
               "incident", "authorized_completion", "reviewed_safe_clarification", "stop",
               "unauthorized_write_count", "repeat_write_count", "initial_ask_user",
               "correct_journal_warning", "unauthorized_writes_after_warning",
               "argument_rejections", "requests", "input_tokens", "output_tokens", "estimated_usd"]
    with (data / "channel_episodes.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            record = {k: row.get(k) for k in columns}
            record.update(cohort="C06", initial_ask_user=(row["initial_recommendation"] or {}).get("action") == "ASK_USER",
                          correct_journal_warning=row["first_correct_journal_warning_step"] is not None)
            for key in ["requests", "input_tokens", "output_tokens", "estimated_usd"]:
                record[key] = row["budget"][key]
            writer.writerow({k: "" if v is None else str(v).lower() if isinstance(v, bool) else v
                             for k, v in record.items()})
    for target, source in {
        "channel_traces.json": "episodes.json", "channel_contracts.json": "contracts.json",
        "channel_reported_summary.json": "summary.json", "channel_review.json": "clarification-review.json",
    }.items():
        (data / target).write_bytes((folder / source).read_bytes())
    run = ROOT / "runs/channel-algorithms-20261112-v1"
    (data / "channel_tasks.json").write_bytes((run / "tasks.json").read_bytes())
    (data / "channel_protocol.txt").write_bytes((run / "protocol.md").read_bytes())
    write(data / "channel_development.json", development)
    filenames = ["channel_episodes.csv", "channel_traces.json", "channel_contracts.json",
                 "channel_reported_summary.json", "channel_review.json", "channel_tasks.json",
                 "channel_protocol.txt", "channel_development.json"]
    plan = read(run / "plan.json")
    write(data / "channel_provenance.json", {
        "date": "2026-11-12", "assigned": 376, "allocations": 6,
        "comparison_assigned": 160, "preceding_development_assigned": 216,
        "cohorts": blocks, "config": plan["config"], "frozen_hashes": plan["frozen_hashes"],
        "data_sha256": {name: sha(data / name) for name in filenames},
        "analysis_sha256": sha(paper / "analysis/channel_summary.py"),
        "notes": ["Six separate exploratory allocations; never pool their incident rates.",
                  "C06 uses all eight previously inspected unspecified-channel cases and all eight matched explicit-email controls.",
                  "C01-C05 preserve selection history, negative cases and the prior Astra algorithm comparison.",
                  "Shared scope-estimation cost is counted once. No new inference is performed by this export.",
                  "Clarification annotations are Codex direct readings, not independent human ratings."]})
    for filename in filenames + ["channel_provenance.json"]:
        text = (data / filename).read_text()
        assert "/Users/" not in text and "/home/" not in text, filename
    print(json.dumps({"actor_records": 376, "comparison": 160, "selection_history": 216, "allocations": 6}))


if __name__ == "__main__":
    main()
