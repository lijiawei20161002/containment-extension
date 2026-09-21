"""Scripted qualification, with no model inference and no automatic image downloads."""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path, PurePosixPath

from .docker import DockerBackend
from .study import digest, source_digest, validate_bundle, write_json


async def close_backend(backend, item: dict) -> None:
    try:
        await backend.close()
    except Exception as exc:
        item.update(ok=False, cleanup_error=type(exc).__name__, cleanup_detail=str(exc))


async def check_environment(backend, record: dict) -> dict:
    expected = (
        record["python"]
        if "files" in record
        else str(PurePosixPath(record["python"]).parent.parent / "envs/testbed/bin/python")
    )
    imports = {"pytest-dev/pytest": ["pytest", "_pytest"], "sympy/sympy": ["sympy"]}.get(
        record["repo"], []
    )
    code = (
        "import sys, json, importlib; from pathlib import Path; "
        f"assert Path(sys.executable).resolve() == Path({expected!r}).resolve(); "
        f"[importlib.import_module(m) for m in {imports!r}]; "
        "print(json.dumps({'ok': True, 'python': sys.executable, 'version': sys.version}))"
    )
    command = "python -c " + shlex.quote(code)
    responses = []
    for index in range(2):
        # Mutating this shell's PATH must not affect the next shell call.
        reply = await backend.shell(command + ("\nexport PATH=/nonexistent" if index == 0 else ""))
        responses.append(reply)
    try:
        ok = all(r["returncode"] == 0 and json.loads(r["stdout"])["ok"] is True for r in responses)
    except (KeyError, TypeError, ValueError):
        ok = False
    return {
        "ok": ok,
        "expected_python": expected,
        "required_imports": imports,
        "responses": responses,
    }


async def qualify(bundle: dict, output: Path, backend_factory=DockerBackend) -> dict:
    records = validate_bundle(bundle)
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "bundle_sha256": digest(bundle),
        "source_sha256": source_digest(),
        "kind": bundle["kind"],
        "scripted": True,
        "checks": [],
        "observer_checks": [],
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
                item["environment"] = await check_environment(backend, record)
                score = await backend.grade()
                evidence = await backend.capture_final()
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
                    and evidence.get("snapshots_complete") is True
                    and (not reference or compliant)
                    and item["environment"]["ok"]
                )
            except Exception as exc:
                item["error"] = type(exc).__name__
                item["detail"] = str(exc)
            finally:
                await close_backend(backend, item)
            report["checks"].append(item)
            write_json(output / "qualification.json", report)
    # Each variant has its own setup and protected paths, even when images are shared.
    for key, record in sorted(records.items()):
        backend = backend_factory()
        item = {
            "instance_id": key[0],
            "variant": key[1],
            "image": record["image"],
            "ok": False,
        }
        try:
            await backend.setup(record)
            protected = record["protected_paths"][0]
            code = (
                "from pathlib import Path; p=Path(" + repr(protected) + "); "
                "b=p.read_bytes(); p.write_bytes(b+b'\\n'); p.write_bytes(b)"
            )
            response = await backend.shell(
                shlex.quote(record["python"]) + " -I -c " + shlex.quote(code)
            )
            evidence = await backend.capture_final()
            item["transient_write"] = {
                "path": protected,
                "response": response,
                "evidence": evidence,
                "ok": response["returncode"] == 0
                and evidence.get("complete") is True
                and evidence.get("snapshots_complete") is True
                and evidence.get("file_changes") == {}
                and any(
                    e.get("protected") is True and e.get("path") == protected
                    for e in evidence.get("events", [])
                ),
            }
            denied = await backend.shell("printf tamper > /opt/containment-audit/record.json")
            after = await backend.capture_final()
            item["observer_protection"] = {
                "response": denied,
                "evidence": after,
                "ok": denied["returncode"] != 0
                and after.get("complete") is True
                and after.get("snapshots_complete") is True,
            }
            item["ok"] = item["transient_write"]["ok"] and item["observer_protection"]["ok"]
        except Exception as exc:
            item.update(error=type(exc).__name__, detail=str(exc))
        finally:
            await close_backend(backend, item)
        report["observer_checks"].append(item)
        write_json(output / "qualification.json", report)
    report["passed"] = all(c["ok"] for c in report["checks"]) and all(
        c["ok"] for c in report["observer_checks"]
    )
    write_json(output / "qualification.json", report)
    return report


def verify_qualification(path: Path, bundle: dict) -> dict:
    report = json.loads(path.read_text())
    records = validate_bundle(bundle)
    expected = {(task, variant, ref) for task, variant in records for ref in (False, True)}
    try:
        seen = {(c["instance_id"], c["variant"], c["reference"]) for c in report["checks"]}
        observers = report["observer_checks"]
        expected_observers = {
            (task, variant, row["image"]) for (task, variant), row in records.items()
        }
        seen_observers = {(c["instance_id"], c["variant"], c["image"]) for c in observers}
        valid = (
            report.get("bundle_sha256") == digest(bundle)
            and report.get("source_sha256") == source_digest()
            and report.get("passed") is True
            and seen == expected
            and len(report["checks"]) == len(expected)
            and all(c["ok"] is True for c in report["checks"])
            and all(c["environment"]["ok"] is True for c in report["checks"])
            and seen_observers == expected_observers
            and len(observers) == len(expected_observers)
            and all(
                c["ok"] is True
                and c["transient_write"]["ok"] is True
                and c["observer_protection"]["ok"] is True
                for c in observers
            )
        )
    except (KeyError, TypeError, AttributeError):
        valid = False
    if not valid:
        raise ValueError("Missing, incomplete, failed, or mismatched local qualification")
    return report
