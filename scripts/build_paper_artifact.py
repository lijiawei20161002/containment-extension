"""E6: create a local, deterministic, identity-scanned supplementary ZIP."""

import argparse
import hashlib
import json
import re
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIES = (
    "incident-study-v1",
    "scope-levels-v1",
    "link-study-v1",
    "feedback-ablation-v1",
    "incident-second-reader-v1",
)
SCRIPTS = (
    "draw_utility_incident_tradeoff.py",
    "run_feedback_ablation.py",
    "incident_second_reader.py",
    "build_paper_artifact.py",
)
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt", ".toml", ".csv", ".svg"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded_json(data):
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode()


def candidates(repo):
    paths = list((repo / "src").rglob("*.py"))
    paths += [repo / "scripts" / name for name in SCRIPTS]
    paths += [
        repo / "tests" / name for name in ("test_feedback_ablation.py", "test_paper_artifacts.py")
    ]
    paths += [
        repo / "pyproject.toml",
        repo / "experiments/feedback-ablation-v1.json",
        repo / "docs/trust4rsi-experiments.md",
    ]
    paths += list((repo / "figures/experiments/tradeoff-v1").rglob("*"))
    paths += list((repo / "incidents/records").glob("*.json"))
    paths += [repo / "incidents/taxonomy.json"]
    for study in STUDIES:
        paths += list((repo / "results" / study).rglob("*"))
    # The package includes only experiment code/evidence, never the repository workspace.
    return sorted(
        {
            p
            for p in paths
            if p.is_file()
            and not p.is_symlink()
            and not any(
                part in {"__pycache__", ".git", ".venv", "slides"} or part.startswith(".env")
                for part in p.relative_to(repo).parts
            )
            and p.suffix not in {".pyc", ".pptx", ".pdf"}
        }
    )


def secrets_for_scan(env_path):
    values = []
    if env_path and env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            value = value.strip().strip("\"'")
            if any(word in key for word in ("KEY", "TOKEN", "SECRET")) and len(value) >= 12:
                values.append(value.encode())
    return values


def build(output, repo=ROOT, env_path=None):
    output.mkdir(parents=True, exist_ok=False)
    metadata = tomllib.loads((repo / "pyproject.toml").read_text())
    identities = [a["name"] for a in metadata["project"].get("authors", []) if a.get("name")]
    identities += [Path.home().name]
    secret_values = secrets_for_scan(env_path)
    files, transformations = {}, []
    for path in candidates(repo):
        name = path.relative_to(repo).as_posix()
        original = path.read_bytes()
        data = original
        if path.suffix in TEXT_SUFFIXES:
            text = original.decode("utf-8")
            if path.name == "pyproject.toml":
                text = re.sub(r"^authors\s*=.*\n", "", text, flags=re.MULTILINE)
            for identity in identities:
                if len(identity) >= 4:
                    text = re.sub(re.escape(identity), "anonymous", text, flags=re.IGNORECASE)
            text = re.sub(r"/(?:Users|home)/[A-Za-z0-9_.-]+", "/anonymous", text)
            data = text.encode()
        if data != original:
            transformations.append(
                {
                    "file": name,
                    "original_sha256": sha(original),
                    "export_sha256": sha(data),
                    "reason": "author identity removal",
                }
            )
        files[name] = data
    # The historical incident archive includes its old packaging author line. Rebind
    # that archive's file index to the anonymized copy; never modify original evidence.
    index_path = "results/incident-study-v1/artifact-hashes.json"
    index = json.loads(files[index_path])
    updates = []
    for relative in index:
        target = "results/incident-study-v1/" + relative
        if target in files and index[relative] != sha(files[target]):
            updates.append(relative)
            index[relative] = sha(files[target])
    if updates:
        original = files[index_path]
        files[index_path] = encoded_json(index)
        transformations.append(
            {
                "file": index_path,
                "original_sha256": sha(original),
                "export_sha256": sha(files[index_path]),
                "reason": "rebind exported checksum index",
                "updated_entries": updates,
            }
        )
    # No server account identity or environment values belong in supplementary data.
    findings = []
    patterns = [
        rb"sk-ant-[A-Za-z0-9_-]{20,}",
        rb"sk-[A-Za-z0-9_-]{30,}",
        rb"hf_[A-Za-z0-9]{25,}",
        rb"/(?:Users|home)/[A-Za-z0-9_.-]+",
    ]
    for name, data in files.items():
        if (
            any(value in data for value in secret_values)
            or any(re.search(pattern, data) for pattern in patterns)
            or any(
                identity.lower().encode() in data.lower()
                for identity in identities
                if len(identity) >= 4
            )
        ):
            findings.append(name)
    if findings:
        raise ValueError("Identity/secret scan failed for files: " + ", ".join(findings))
    summary = json.loads(files["results/feedback-ablation-v1/summary.json"])
    files["README.md"] = (
        "# Anonymous experiment supplement\n\n"
        "Python 3.11+. Offline checks need pytest; E1 rendering also needs matplotlib. "
        "The native runner uses the standard library and hosted inference; no GPU is needed.\n\n"
        "```sh\npython3 -m pip install -e '.[dev]' matplotlib\n"
        "python3 -m pytest -q\n"
        "python3 scripts/draw_utility_incident_tradeoff.py\n"
        "python3 scripts/run_feedback_ablation.py report results/feedback-ablation-v1\n```\n\n"
        f"Archived E2 status: {summary['status']}. Do not mistake the scripted tests for model "
        "performance. The live run stopped at its predeclared baseline gate; selection, judge "
        "calibration and held-out stages were not reached. See the experiment report and frozen "
        "plan for exact budgets and schedules.\n\n"
        "A fresh live replication requires an API key outside this archive, a new output "
        "directory, and a new authorization statement in a copied configuration. "
        "Never overwrite this evidence.\n\n"
        "E5 contains blank independent-reader worksheets; no human agreement result is claimed. "
        "Send only results/incident-second-reader-v1/blind to the reader.\n\n"
        "Public incident sources and synthetic .lab.test addresses are retained. Author identity "
        "metadata is removed only in exported copies. The transformation log and exported file "
        "hashes are in artifact-manifest.json. This is a local supplement; nothing was uploaded.\n"
    ).encode()
    manifest = {
        "version": "paper-artifact-v1",
        "files": {k: sha(v) for k, v in sorted(files.items())},
        "transformations": transformations,
        "scan": {
            "passed": True,
            "files_scanned": len(files) - 1,
            "checks": [
                "author identity",
                "local home paths",
                "API key patterns",
                "exact local credentials (values never exported)",
            ],
        },
        "excluded": [
            "dotenv files",
            "Git metadata",
            "slide decks",
            "HANDOFF",
            "repository README",
            "unrelated studies",
            "compiled caches",
        ],
        "publication": "local_only_not_uploaded",
    }
    files["artifact-manifest.json"] = encoded_json(manifest)
    archive = output / "anonymous-experiments.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo("supplement/" + name, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, data)
    digest = sha(archive.read_bytes())
    (output / "anonymous-experiments.zip.sha256").write_text(f"{digest}  {archive.name}\n")
    (output / "manifest.json").write_bytes(encoded_json(manifest))
    return {
        "archive": archive.name,
        "sha256": digest,
        "files": len(files),
        "bytes": archive.stat().st_size,
        "scan_passed": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output, env_path=args.env_file), indent=2))
