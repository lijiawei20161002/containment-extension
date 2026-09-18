import copy
import json
import subprocess
from pathlib import Path

import pytest

from containment_extension.impossiblebench.catalog import build_catalog, catalog
from containment_extension.impossiblebench.preflight import GIB, assess, inspect_resources


def healthy_host():
    return {
        "docker_available": True,
        "os": "linux",
        "cpus": 8,
        "memory_bytes": 32 * GIB,
        "free_disk_bytes": 200 * GIB,
        "local_docker": True,
        "architecture": "x86_64",
    }


def test_preflight_distinguishes_fixture_resources_from_real_study():
    host = {
        **healthy_host(),
        "memory_bytes": 4 * GIB,
        "free_disk_bytes": 11 * GIB,
        "architecture": "aarch64",
    }
    assert assess("fixture", host, [])["resource_checks_passed"]
    real = assess("swebench", host, [])
    assert not real["resource_checks_passed"]
    assert {c["name"] for c in real["checks"] if not c["passed"]} == {
        "memory_bytes",
        "free_disk_bytes",
        "recommended_architecture",
    }


def test_remote_daemon_cannot_be_qualified_using_client_storage():
    assert not assess("swebench", {**healthy_host(), "local_docker": False}, [])[
        "resource_checks_passed"
    ]


@pytest.mark.parametrize(
    "image",
    [
        {"available": False},
        {"available": True, "architecture": "arm64"},
        {"available": True, "architecture": "amd64", "volumes": {"/testbed": {}}},
    ],
)
def test_missing_incompatible_or_mounted_images_fail_preflight(image):
    assert not assess("swebench", healthy_host(), [{"image": "pinned", **image}])[
        "resource_checks_passed"
    ]


def test_preflight_selects_safe_metadata_and_only_reads_docker(tmp_path, monkeypatch):
    calls = []
    bundle = json.loads(Path("tests/fixtures/impossiblebench/bundle.json").read_text())

    def run(args, **kwargs):
        calls.append(args)
        if args[1] == "info":
            data = {
                "OSType": "linux",
                "NCPU": 8,
                "MemTotal": 32 * GIB,
                "Architecture": "arm64",
                "ServerVersion": "test",
                "HttpProxy": "https://secret:password@proxy",
            }
        elif args[1] == "context":
            data = [{"Endpoints": {"docker": {"Host": "unix:///docker.sock"}}}]
        else:
            data = [
                {
                    "Architecture": "arm64",
                    "Size": 10,
                    "Id": "digest",
                    "Config": {"Env": ["SECRET=hidden"], "Volumes": {}},
                }
            ]
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(data))

    monkeypatch.delenv("DOCKER_HOST", raising=False)
    monkeypatch.setattr("subprocess.run", run)
    path = tmp_path / "preflight.json"
    result = inspect_resources(path, bundle)
    assert result["resource_checks_passed"]
    assert "secret" not in path.read_text().lower()
    assert [c[1] for c in calls] == ["info", "context", "image"]
    with pytest.raises(FileExistsError):
        inspect_resources(path, bundle)
    with pytest.raises(ValueError, match="SWE-bench bundles"):
        # Profile checks happen after bundle validation, which is independently tested.
        monkeypatch.setattr(
            "containment_extension.impossiblebench.preflight.validate_bundle", lambda _: {}
        )
        inspect_resources(tmp_path / "bad.json", {"kind": "swebench"}, profile="fixture")


def test_unavailable_docker_is_saved_as_failed_check(tmp_path, monkeypatch):
    def run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "docker", stderr="sensitive body")

    monkeypatch.setattr("subprocess.run", run)
    path = tmp_path / "preflight.json"
    assert not inspect_resources(path)["resource_checks_passed"]
    assert "sensitive" not in path.read_text()


def triples():
    row = {
        "instance_id": "example__repo-1",
        "repo": "example/repo",
        "version": "1.0",
        "base_commit": "a" * 40,
        "problem_statement": "Do the specified thing.",
        "patch": "--- a/example.py\n+++ b/example.py\n",
        "original_test_patch": "original",
        "test_patch": "--- a/test_x.py\n+++ b/test_x.py\n",
    }
    return {v: [copy.deepcopy(row)] for v in ("original", "oneoff", "conflicting")}


def test_catalog_retains_row_provenance_but_does_not_claim_qualification():
    splits = triples()
    report = build_catalog(splits, "b" * 40)
    assert report["eligible_count"] == 1
    assert report["exclusions"] == []
    task = report["tasks"][0]
    assert task["status"] == "requires_mutation_review_and_image_qualification"
    before = task["row_sha256"]["oneoff"]
    splits["oneoff"][0]["test_patch"] += "new assertion\n"
    assert build_catalog(splits, "b" * 40)["tasks"][0]["row_sha256"]["oneoff"] != before


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("missing", "missing:oneoff"),
        ("mismatch", "mismatched:problem_statement"),
        ("protected", "reference_modifies_protected_files"),
        ("traversal", "unsafe_patch_path"),
    ],
)
def test_catalog_records_exclusions_instead_of_silently_dropping_tasks(defect, reason):
    splits = triples()
    if defect == "missing":
        splits["oneoff"] = []
    elif defect == "mismatch":
        splits["oneoff"][0]["problem_statement"] = "Different issue"
    else:
        for rows in splits.values():
            rows[0]["patch"] = (
                "--- a/test_x.py\n+++ b/test_x.py\n"
                if defect == "protected"
                else "--- a/../../file\n+++ b/../../file\n"
            )
    report = build_catalog(splits, "b" * 40)
    assert report["eligible_count"] == 0
    assert reason in report["exclusions"][0]["reasons"]


def test_catalog_rejects_duplicates_and_unpinned_fetch_before_network(tmp_path):
    splits = triples()
    splits["original"].append(splits["original"][0])
    with pytest.raises(ValueError, match="Duplicate"):
        build_catalog(splits, "b" * 40)
    with pytest.raises(ValueError, match="immutable"):
        catalog("main", tmp_path / "catalog.json")
