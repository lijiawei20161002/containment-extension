"""Check blind-label isolation, agreement missingness and exported evidence."""

import csv
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_reader_packet_blinds_codes_and_preserves_missingness(tmp_path):
    reader = module("incident_second_reader")
    root = tmp_path / "reader"
    reader.prepare(root)
    cases = json.loads((root / "blind/cases.json").read_text())
    assert len(cases) == 26
    assert all(
        not {"pathway", "mechanisms", "propositions", "coding", "controls"} & set(c) for c in cases
    )
    csv_path = root / "blind/second-reader.csv"
    pending = reader.analyze(csv_path, tmp_path / "pending")
    assert pending["status"] == "awaiting_second_reader"
    assert pending["completed_cells"] == 0
    assert all(s["cohen_kappa"] is None for s in pending["fields"].values())
    first = reader.records(ROOT)
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", *reader.FIELDS, "evidence_notes"])
        writer.writeheader()
        writer.writerows({"id": r["id"], **reader.original_labels(r)} for r in first)
    completed = reader.analyze(csv_path, tmp_path / "completed")
    assert completed["completed_cells"] == 416
    assert completed["disagreements"] == []
    assert completed["fields"]["pathway"]["cohen_kappa"] == 1
    assert reader.agreement([("a", "b"), ("b", "a")])["cohen_kappa"] == -1
    assert reader.agreement([("a", "a")])["cohen_kappa"] is None


def test_anonymous_export_hashes_and_frozen_evidence(tmp_path):
    artifact = module("build_paper_artifact")
    result = artifact.build(tmp_path / "export")
    archive = tmp_path / "export" / result["archive"]
    assert result["scan_passed"] is True
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == result["sha256"]
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        assert not any("/.env" in n or "/slides/" in n or "/.git/" in n for n in names)
        manifest = json.loads(bundle.read("supplement/artifact-manifest.json"))
        for name, checksum in manifest["files"].items():
            assert hashlib.sha256(bundle.read("supplement/" + name)).hexdigest() == checksum
        assert b"authors =" not in bundle.read("supplement/pyproject.toml")
        prefix = "supplement/results/feedback-ablation-v1/"
        integrity = json.loads(bundle.read(prefix + "integrity.json"))
        for name, checksum in integrity.items():
            assert hashlib.sha256(bundle.read(prefix + name)).hexdigest() == checksum
        with pytest.raises(FileExistsError):
            artifact.build(tmp_path / "export")
