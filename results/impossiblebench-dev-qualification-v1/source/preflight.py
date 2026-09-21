"""Read-only host and cached-image checks; never pull images or invoke models."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .study import validate_bundle, write_json

GIB = 1024**3
# Conservative planning thresholds, not necessary minima for every individual issue.
PROFILES = {
    "fixture": {"cpus": 2, "memory_bytes": 2 * GIB, "free_disk_bytes": GIB},
    "swebench": {"cpus": 8, "memory_bytes": 16 * GIB, "free_disk_bytes": 120 * 10**9},
}


def architecture(value: str) -> str:
    return {"x86_64": "amd64", "aarch64": "arm64"}.get(value, value)


def assess(profile: str, host: dict, images: list[dict]) -> dict:
    requirements = PROFILES[profile]
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("docker_available", host.get("docker_available"), host.get("docker_error"))
    check("linux_containers", host.get("os") == "linux", host.get("os"))
    for field, threshold in requirements.items():
        measured = host.get(field)
        check(
            field,
            measured is not None and measured >= threshold,
            {"observed": measured, "planning_threshold": threshold},
        )
    check(
        "storage_on_execution_host",
        host.get("local_docker"),
        "Run this command on the Docker host; client disk space cannot qualify a remote daemon.",
    )
    if profile == "swebench":
        check(
            "recommended_architecture",
            architecture(host.get("architecture", "")) == "amd64",
            "SWE-bench recommends x86-64; ARM requires separate image qualification.",
        )
    for item in images:
        check("cached_image:" + item["image"], item.get("available"), item.get("error"))
        if item.get("available"):
            check(
                "image_architecture:" + item["image"],
                architecture(item["architecture"]) == architecture(host.get("architecture", "")),
                {"image": item["architecture"], "docker": host.get("architecture")},
            )
            check(
                "image_without_volumes:" + item["image"],
                not item.get("volumes"),
                "Image-declared volumes would create mounts prohibited by the backend.",
            )
    return {
        "profile": profile,
        "resource_checks_passed": all(c["passed"] for c in checks),
        "host": host,
        "images": images,
        "checks": checks,
        "notes": [
            "Read-only check: no image pulls, containers, model calls, or credential values.",
            "Planning thresholds are conservative; a pass does not qualify task behavior.",
            "Network access is needed for image acquisition and API inference on the host; "
            "actor containers remain offline.",
        ],
    }


def inspect_resources(
    output: Path, bundle: dict | None = None, *, profile: str | None = None
) -> dict:
    if output.exists():
        raise FileExistsError(output)
    if bundle is not None:
        validate_bundle(bundle)
    profile = profile or (bundle["kind"] if bundle else "swebench")
    if profile not in PROFILES:
        raise ValueError("Unknown resource profile")
    if bundle and bundle["kind"] == "swebench" and profile != "swebench":
        raise ValueError("SWE-bench bundles require the SWE-bench resource profile")
    output.parent.mkdir(parents=True, exist_ok=True)

    def docker(*args):
        response = subprocess.run(
            ["docker", *args], capture_output=True, text=True, timeout=30, check=True
        )
        return json.loads(response.stdout)

    host = {"docker_available": False, "free_disk_bytes": shutil.disk_usage(output.parent).free}
    try:
        info = docker("info", "--format", "{{json .}}")
        context = docker("context", "inspect")[0]
        # DOCKER_HOST can override the selected context; do not assume it is local.
        import os

        endpoint = context["Endpoints"]["docker"]["Host"]
        if not os.environ.get("DOCKER_CONTEXT"):
            endpoint = os.environ.get("DOCKER_HOST") or endpoint
        host.update(
            docker_available=True,
            os=info["OSType"],
            cpus=info["NCPU"],
            memory_bytes=info["MemTotal"],
            architecture=info["Architecture"],
            docker_version=info["ServerVersion"],
            local_docker=endpoint.startswith("unix://"),
        )
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, IndexError) as exc:
        host["docker_error"] = type(exc).__name__
    images = []
    for name in sorted({r["image"] for r in bundle["records"]} if bundle else set()):
        item = {"image": name, "available": False}
        try:
            image = docker("image", "inspect", name)[0]
            item.update(
                available=True,
                architecture=image["Architecture"],
                size_bytes=image["Size"],
                image_id=image["Id"],
                volumes=image.get("Config", {}).get("Volumes"),
            )
        except (OSError, subprocess.SubprocessError, ValueError, KeyError, IndexError) as exc:
            item["error"] = type(exc).__name__
        images.append(item)
    report = assess(profile, host, images)
    write_json(output, report)
    return report
