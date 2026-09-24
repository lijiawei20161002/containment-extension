"""Inventory matched dataset triples before acquiring task images or making API calls."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .study import VARIANTS, digest, relative_path, write_json

DATASET = "fjzzq2002/impossible_swebench"
SHARED = ("repo", "version", "base_commit", "problem_statement", "patch", "original_test_patch")


def patch_paths(patch: str) -> list[str]:
    paths = sorted(set(re.findall(r"^(?:---|\+\+\+) [ab]/([^\n]+)$", patch, re.M)))
    for path in paths:
        relative_path(path)
    return paths


def build_catalog(splits: dict[str, list[dict]], revision: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Use an immutable Hugging Face dataset commit")
    if set(splits) != set(VARIANTS):
        raise ValueError("All three dataset splits are required")
    indexed = {}
    for variant, rows in splits.items():
        indexed[variant] = {}
        for row in rows:
            task_id = row["instance_id"]
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", task_id):
                raise ValueError("Invalid dataset task ID")
            if task_id in indexed[variant]:
                raise ValueError(f"Duplicate {variant} row: {task_id}")
            indexed[variant][task_id] = row
    tasks, exclusions = [], []
    for task_id in sorted(set().union(*(set(v) for v in indexed.values()))):
        rows = {v: indexed[v].get(task_id) for v in VARIANTS}
        reasons = ["missing:" + v for v, row in rows.items() if row is None]
        if not reasons:
            reasons.extend(
                "mismatched:" + field
                for field in SHARED
                if len({digest(r.get(field)) for r in rows.values()}) != 1
            )
            for variant, row in rows.items():
                for field in (*SHARED, "test_patch"):
                    if not isinstance(row.get(field), str) or not row[field]:
                        reasons.append("missing_field:" + variant + ":" + field)
                if not re.fullmatch(r"[0-9a-f]{40}", row.get("base_commit", "")):
                    reasons.append("invalid_base_commit:" + variant)
            if not reasons:
                try:
                    tests = {v: patch_paths(r["test_patch"]) for v, r in rows.items()}
                    changed = patch_paths(rows["original"]["patch"])
                    if not all(tests.values()) or not changed:
                        reasons.append("empty_patch_paths")
                    protected = set().union(*(set(paths) for paths in tests.values()))
                    if any(
                        p in protected
                        or p.startswith(".git/")
                        or p == ".git"
                        or (Path(p).name.startswith("test_") and p.endswith(".py"))
                        or Path(p).name
                        in {"conftest.py", "pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml"}
                        for p in changed
                    ):
                        reasons.append("reference_modifies_protected_files")
                except ValueError:
                    reasons.append("unsafe_patch_path")
        if reasons:
            exclusions.append({"instance_id": task_id, "reasons": sorted(set(reasons))})
            continue
        original = rows["original"]
        tasks.append(
            {
                "instance_id": task_id,
                "repo": original["repo"],
                "base_commit": original["base_commit"],
                "version": original["version"],
                "row_sha256": {v: digest(r) for v, r in rows.items()},
                "test_paths": tests,
                "reference_paths": changed,
                "status": "requires_mutation_review_and_image_qualification",
            }
        )
    return {
        "dataset": DATASET,
        "revision": revision,
        "split_counts": {v: len(splits[v]) for v in VARIANTS},
        "eligible_count": len(tasks),
        "repositories": dict(sorted(Counter(t["repo"] for t in tasks).items())),
        "tasks": tasks,
        "exclusions": exclusions,
        "notes": [
            "Structural eligibility is not proof of impossibility or runtime readiness.",
            "No issue has been assigned to development or held-out evaluation yet.",
        ],
    }


def catalog(revision: str, output: Path, *, cache_dir: Path | None = None) -> dict:
    if output.exists():
        raise FileExistsError(output)
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Use an immutable Hugging Face dataset commit")
    from datasets import load_dataset

    splits = {
        v: list(
            load_dataset(
                DATASET,
                split=v,
                revision=revision,
                cache_dir=str(cache_dir) if cache_dir else None,
                token=False,
            )
        )
        for v in VARIANTS
    }
    report = build_catalog(splits, revision)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, report)
    return report
