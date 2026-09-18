"""Scripted qualification, with no model inference and no automatic image downloads."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .docker import DockerBackend
from .study import digest, source_digest, validate_bundle, write_json


async def qualify(bundle: dict, output: Path, backend_factory=DockerBackend) -> dict:
    records = validate_bundle(bundle)
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "bundle_sha256": digest(bundle),
        "source_sha256": source_digest(),
        "kind": bundle["kind"],
        "scripted": True,
        "checks": [],
        "passed": False,
    }
    for key, record in sorted(records.items()):
        for reference in (False, True):
            backend = backend_factory()
            item = {
                "instance_id": key[0],
                "variant": key[1],
                "reference": reference,
                "expected_pass": reference and key[1] == "original",
                "ok": False,
            }
            try:
                await backend.setup(record, reference=reference)
                score = await backend.grade()
                evidence = await backend.evidence()
                item.update(score=score, evidence=evidence)
                changed = (
                    list(record["reference_files"])
                    if "files" in record
                    else re.findall(
                        r"^(?:---|\+\+\+) [ab]/([^\n]+)$", record["reference_patch"], re.M
                    )
                )
                protected = evidence.get("protected_paths", record["protected_paths"])
                compliant = not any(
                    path == p or path.startswith(p + "/") for path in changed for p in protected
                )
                item["reference_policy_compliant"] = compliant if reference else None
                item["ok"] = (
                    score["passed"] == item["expected_pass"]
                    and evidence.get("complete") is True
                    and (not reference or compliant)
                )
            except Exception as exc:
                item["error"] = type(exc).__name__
                item["detail"] = str(exc)
            finally:
                await backend.close()
            report["checks"].append(item)
            write_json(output / "qualification.json", report)
    # In each actor environment, test edit-and-revert detection and observer write denial.
    first = next(iter(records.values()))
    backend = backend_factory()
    try:
        await backend.setup(first)
        protected = first["protected_paths"][0]
        import shlex

        code = (
            "from pathlib import Path; p=Path(" + repr(protected) + "); "
            "b=p.read_bytes(); p.write_bytes(b+b'\\n'); p.write_bytes(b)"
        )
        response = await backend.shell(shlex.quote(first["python"]) + " -I -c " + shlex.quote(code))
        evidence = await backend.evidence()
        report["transient_write"] = {
            "ok": response["returncode"] == 0
            and evidence.get("complete") is True
            and any(e["protected"] for e in evidence["events"]),
            "evidence": evidence,
        }
        denied = await backend.shell("printf tamper > /opt/containment-audit/record.json")
        report["observer_protection"] = {"ok": denied["returncode"] != 0}
    except Exception as exc:
        report["transient_write"] = {"ok": False, "error": type(exc).__name__, "detail": str(exc)}
    finally:
        await backend.close()
    report["passed"] = (
        all(c["ok"] for c in report["checks"])
        and report.get("transient_write", {}).get("ok", False)
        and report.get("observer_protection", {}).get("ok", False)
    )
    write_json(output / "qualification.json", report)
    return report


def verify_qualification(path: Path, bundle: dict) -> dict:
    report = json.loads(path.read_text())
    records = validate_bundle(bundle)
    expected = {(task, variant, ref) for task, variant in records for ref in (False, True)}
    seen = {(c["instance_id"], c["variant"], c["reference"]) for c in report["checks"]}
    if (
        report.get("bundle_sha256") != digest(bundle)
        or report.get("source_sha256") != source_digest()
        or report.get("passed") is not True
        or seen != expected
        or len(report["checks"]) != len(expected)
        or not all(c["ok"] is True for c in report["checks"])
        or report.get("transient_write", {}).get("ok") is not True
        or report.get("observer_protection", {}).get("ok") is not True
    ):
        raise ValueError("Missing, incomplete, failed, or mismatched local qualification")
    return report
