"""Export selected matched SWE-bench triples at a pinned Hugging Face revision."""

from __future__ import annotations

import re
from pathlib import Path

from .docker import test_command
from .study import VARIANTS, VERSION, validate_bundle, write_json


def export(selection: dict, output: Path) -> dict:
    if output.exists():
        raise FileExistsError(output)
    revision = selection["revision"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Use an immutable Hugging Face dataset commit")
    # Optional imports keep the native service runner dependency-free.
    from datasets import load_dataset
    from swebench.harness.constants import MAP_REPO_VERSION_TO_SPECS
    from swebench.harness.test_spec.python import get_test_directives

    selected = selection["tasks"]
    records = []
    for variant in VARIANTS:
        dataset = load_dataset("fjzzq2002/impossible_swebench", split=variant, revision=revision)
        for row in dataset:
            if row["instance_id"] not in selected:
                continue
            settings = selected[row["instance_id"]]
            spec = MAP_REPO_VERSION_TO_SPECS[row["repo"]][row["version"]]
            paths = re.findall(r"^(?:---|\+\+\+) [ab]/([^\n]+)$", row["test_patch"], re.M)
            records.append(
                {
                    "instance_id": row["instance_id"],
                    "variant": variant,
                    "repo": row["repo"],
                    "base_commit": row["base_commit"],
                    "problem_statement": row["problem_statement"],
                    "test_patch": row["test_patch"],
                    "reference_patch": row["patch"],
                    "original_test_patch": row["original_test_patch"],
                    "test_targets": {
                        key: row.get(key, []) for key in ("FAIL_TO_PASS", "PASS_TO_PASS")
                    },
                    "image": settings["image"],
                    "python": settings.get("python", "/opt/miniconda3/bin/python"),
                    "test_command": settings.get("test_command")
                    or test_command(
                        spec["test_cmd"], get_test_directives(row), spec.get("eval_commands", [])
                    ),
                    "protected_paths": sorted(set(paths)),
                    "contradiction_review": settings.get("reviews", {}).get(variant),
                }
            )
    bundle = {
        "schema": VERSION,
        "kind": "swebench",
        "dataset": "fjzzq2002/impossible_swebench",
        "revision": revision,
        "records": records,
    }
    validate_bundle(bundle)
    if {r["instance_id"] for r in records} != set(selected):
        raise ValueError("Not every selected issue has a matched triple at this revision")
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, bundle)
    return bundle
