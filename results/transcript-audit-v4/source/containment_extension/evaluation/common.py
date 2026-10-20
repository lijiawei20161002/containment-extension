"""Immutable evidence export shared by the two evaluation designs."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def export_manifest(root, design, summary):
    """Freeze source and design, then hash every exported evidence file."""
    root = Path(root)
    package = Path(__file__).resolve().parents[1]
    source_files = sorted((package / "evaluation").glob("*.py"))
    source_files += [package / "cli.py", package / "__init__.py"]
    for path in source_files:
        target = root / "source" / path.relative_to(package)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(path.read_bytes())
    write_json(root / "design.json", json.loads(Path(design).read_text()))
    write_json(root / "summary.json", summary)
    files = {p.relative_to(root).as_posix(): file_hash(p)
             for p in sorted(root.rglob("*")) if p.is_file()}
    manifest = {"schema": "evaluation-evidence-v1", "created_at":
                datetime.now(timezone.utc).isoformat(), "files": files,
                "design_sha256": file_hash(design), "kind": "offline_qualification",
                "model_calls": 0}
    write_json(root / "manifest.json", manifest)
    write_json(root / "manifest.sha256.json", {"sha256": digest(manifest)})
    return summary


def verify_export(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    expected = json.loads((root / "manifest.sha256.json").read_text())["sha256"]
    if digest(manifest) != expected:
        raise ValueError("Evidence manifest hash mismatch")
    for relative, checksum in manifest["files"].items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file() or file_hash(path) != checksum:
            raise ValueError(f"Evidence missing or changed: {relative}")
    return manifest
