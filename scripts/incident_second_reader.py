"""E5: blind coding packet and per-field agreement, without invented human labels."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["pathway"] + [f"M{i}" for i in range(1, 7)] + [f"P{i}" for i in range(1, 10)]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def records(repo):
    return sorted(
        [json.loads(p.read_text()) for p in (repo / "incidents/records").glob("*.json")],
        key=lambda r: r["id"],
    )


def original_labels(record):
    return {
        "pathway": record["pathway"],
        **{k: v["status"] for k, v in record["mechanisms"].items()},
        **{k: v["relation"] for k, v in record["propositions"].items()},
    }


def prepare(output, repo=ROOT):
    output.mkdir(parents=True, exist_ok=False)
    blind = output / "blind"
    blind.mkdir()
    rows = records(repo)
    fields = ("id", "title", "summary", "dates", "timeline", "evidence", "impact")
    write_json(blind / "cases.json", [{k: r[k] for k in fields if k in r} for r in rows])
    taxonomy = json.loads((repo / "incidents/taxonomy.json").read_text())
    codebook = {k: taxonomy[k] for k in ("pathways", "mechanisms", "propositions")}
    codebook["allowed_labels"] = {
        "pathway": list(taxonomy["pathways"]),
        "mechanisms": ["present", "partial", "absent", "unknown"],
        "propositions": ["violated", "demonstrated", "mixed", "not_applicable"],
    }
    write_json(blind / "codebook.json", codebook)
    with (blind / "second-reader.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", *FIELDS, "evidence_notes"])
        writer.writeheader()
        writer.writerows({"id": r["id"]} for r in rows)
    missing = [
        {"id": r["id"], "source": s["name"]}
        for r in rows
        for s in r["evidence"]["sources"]
        if not s.get("url")
    ]
    write_json(blind / "sources-needing-resolution.json", missing)
    (blind / "INSTRUCTIONS.txt").write_text(
        "Independent second-reader coding\n\n"
        "Use only this blind directory and the public source reports. Do not open the repository's "
        "incident records, first-reader codings, figures or aggregate analysis before submitting.\n"
        "Code pathway, M1-M6 and P1-P9 using codebook.json; cite evidence in evidence_notes. "
        "Leave unassessed fields blank; 'unknown' is an explicit mechanism judgment, "
        "not missing data. "
        "No default or AI-generated second-reader answers are supplied.\n"
        "The supplied summaries may retain the first analyst's framing. "
        "Read the original sources independently. Missing source URLs are listed separately; "
        "obtain the reports before coding those cases.\n"
        "Return the completed CSV. Preserve independent labels before any adjudication; resolve "
        "disagreements or mark them disputed. Do not overwrite the original records.\n"
    )
    write_json(
        output / "manifest.json",
        {
            "status": "awaiting_independent_human_reader",
            "records": len(rows),
            "fields_per_record": len(FIELDS),
            "source_links_needing_resolution": len(missing),
            "record_hashes": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted((repo / "incidents/records").glob("*.json"))
            },
        },
    )
    return {"records": len(rows), "fields": len(FIELDS), "source_links_missing": len(missing)}


def agreement(pairs):
    n = len(pairs)
    if not n:
        return {"paired": 0, "agreements": 0, "agreement": None, "cohen_kappa": None}
    a, b = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    same = sum(x == y for x, y in pairs)
    expected = sum(a[k] * b[k] for k in set(a) | set(b)) / n**2
    return {
        "paired": n,
        "agreements": same,
        "agreement": same / n,
        "cohen_kappa": (same / n - expected) / (1 - expected) if expected < 1 else None,
        "first_marginals": dict(a),
        "second_marginals": dict(b),
        "kappa_note": "Undefined when chance agreement is 1; nominal unweighted categories.",
    }


def analyze(csv_path, output, repo=ROOT):
    source = {r["id"]: original_labels(r) for r in records(repo)}
    with csv_path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["id", *FIELDS, "evidence_notes"]:
            raise ValueError("CSV headers do not match the blind template")
        submitted = list(reader)
    if len({r["id"] for r in submitted}) != len(submitted):
        raise ValueError("Duplicate incident IDs")
    if {r["id"] for r in submitted} != set(source):
        raise ValueError("The CSV must retain all 26 incident rows")
    taxonomy = json.loads((repo / "incidents/taxonomy.json").read_text())
    stats, disputed = {}, []
    for field in FIELDS:
        allowed = (
            set(taxonomy["pathways"])
            if field == "pathway"
            else {"present", "partial", "absent", "unknown"}
            if field.startswith("M")
            else {"violated", "demonstrated", "mixed", "not_applicable"}
        )
        pairs = []
        for row in submitted:
            value = row[field].strip()
            if not value:
                continue
            if value not in allowed:
                raise ValueError(f"Invalid label for {row['id']} / {field}")
            original = source[row["id"]][field]
            pairs.append((original, value))
            if original != value:
                disputed.append(
                    {
                        "id": row["id"],
                        "field": field,
                        "first_reader": original,
                        "second_reader": value,
                        "status": "disputed",
                        "resolution": "",
                        "evidence_notes": row["evidence_notes"],
                    }
                )
        stats[field] = {**agreement(pairs), "missing": len(source) - len(pairs)}
    completed = sum(s["paired"] for s in stats.values())
    result = {
        "status": "awaiting_second_reader"
        if not completed
        else "complete_independent_coding"
        if completed == len(source) * len(FIELDS)
        else "partial_second_reader",
        "fields": stats,
        "disagreements": disputed,
        "completed_cells": completed,
        "expected_cells": len(source) * len(FIELDS),
        "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "notes": "Agreement precedes adjudication. Disputed labels remain unresolved and "
        "must be excluded or separately reported; no original labels were changed.",
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "agreement.json", result)
    with (output / "adjudication.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "id",
                "field",
                "first_reader",
                "second_reader",
                "status",
                "resolution",
                "evidence_notes",
            ],
        )
        writer.writeheader()
        writer.writerows(disputed)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "analyze"])
    parser.add_argument("output", type=Path)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    if args.action == "analyze" and args.csv is None:
        parser.error("analyze requires --csv")
    result = prepare(args.output) if args.action == "prepare" else analyze(args.csv, args.output)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in {"fields", "disagreements"}}, indent=2
        )
    )
