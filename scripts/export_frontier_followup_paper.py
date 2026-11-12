"""Export the two completed frontier follow-ups without new inference."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def portable(value):
    if isinstance(value, dict):
        return {k: portable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [portable(v) for v in value]
    return value.replace(str(ROOT) + "/", "") if isinstance(value, str) else value


def write(path, value):
    path.write_text(json.dumps(portable(value), indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path, required=True)
    paper = parser.parse_args().paper_dir
    data = paper / "data"
    blocks, filenames = [], []
    for prefix, result_name, run_name, expected in [
        ("deep_planning", "frontier-deep-planning-v1", "frontier-deep-planning-20261112-v1", 216),
        ("channel_additional", "channel-terra-opus-v1", "channel-terra-opus-20261112-v1", 160),
    ]:
        folder, run = ROOT / "results" / result_name, ROOT / "runs" / run_name
        provenance = read(folder / "provenance.json")
        for name, expected_hash in provenance["export_hashes"].items():
            assert sha(folder / name) == expected_hash, (result_name, name)
            target = f"{prefix}_{name.replace('-', '_')}"
            write(data / target, read(folder / name))
            filenames.append(target)
        assert len(read(folder / "episodes.json")) == expected
        assert sha(run / "plan.json") == provenance["plan_sha256"]
        assert sha(run / "tasks.json") == provenance["tasks_sha256"]
        plan = read(run / "plan.json")
        target = f"{prefix}_protocol.txt"
        (data / target).write_text(portable((run / "protocol.md").read_text()))
        filenames.append(target)
        blocks.append({"source": result_name, "assigned": expected, "config": plan["config"],
                       "source_provenance": provenance, "protocol_sha256": sha(run / "protocol.md")})
    assert (ROOT / "runs/channel-terra-opus-20261112-v1/tasks.json").read_bytes() == (data / "channel_tasks.json").read_bytes()
    # The earlier comparison is an input to the combined presentation, not a new allocation.
    filenames += ["channel_tasks.json", "channel_traces.json", "channel_provenance.json"]
    write(data / "frontier_followup_provenance.json", {
        "date": "2026-11-12", "assigned": 376, "allocations": 2, "cohorts": blocks,
        "data_sha256": {name: sha(data / name) for name in filenames},
        "analysis_sha256": sha(paper / "analysis/frontier_followup_summary.py"),
        "notes": ["Exploratory allocations; earlier outcomes are unchanged and rates are not pooled.",
                  "Channel task bytes match the previous Astra/Fable allocation; scope estimates are fresh.",
                  "Efficiency ratios exclude impossible controls and compare matched safe completions.",
                  "Clarification and control annotations are Codex readings, not independent human ratings.",
                  "Costs use uncached list prices and count shared scope inference once; probes are excluded."]})
    for name in filenames + ["frontier_followup_provenance.json"]:
        contents = (data / name).read_text()
        assert "/Users/" not in contents and "/home/" not in contents, name
    print(json.dumps({"actor_records": 376, "allocations": 2, "data_files": len(filenames)}))


if __name__ == "__main__":
    main()
