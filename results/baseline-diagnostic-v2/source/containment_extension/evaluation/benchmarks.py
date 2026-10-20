"""Pinned benchmark inventory, conservative official-result imports and report exports."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

from . import benchmark_metrics
from .common import digest, file_hash, write_json


def check_suite(config):
    if config.get("schema") != "containment-standardized-benchmarks-v1":
        raise ValueError("Unknown benchmark suite schema")
    ids, checks = set(), []
    for entry in config.get("benchmarks", []):
        name = entry["id"]
        if name in ids:
            raise ValueError("Duplicate benchmark")
        ids.add(name)
        if not re.fullmatch(r"[0-9a-f]{40}", entry["source_revision"]):
            raise ValueError(f"Unpinned benchmark source: {name}")
        if not entry["source_url"].startswith("https://github.com/"):
            raise ValueError(f"Missing canonical source: {name}")
        if not entry.get("baselines") or not entry.get("primary_metrics"):
            raise ValueError(f"Missing baselines or endpoints: {name}")
        requirements = entry.get("execution_requirements", {})
        required = {"dataset_manifest_sha256", "task_schedule_sha256", "environment_lock_sha256",
                    "model_config_sha256", "budget_config_sha256", "qualification_report_sha256"}
        if set(requirements) != required:
            raise ValueError(f"Incomplete execution lock schema: {name}")
        for key, value in requirements.items():
            if value is not None and not re.fullmatch(r"[0-9a-f]{64}", str(value)):
                raise ValueError(f"Invalid {name}.{key}")
        missing = [key for key, value in requirements.items() if value is None]
        checks.append({"benchmark": name, "source_locked": True,
                       "adapter_status": entry["adapter_status"],
                       "ready_to_run": not missing, "missing": missing})
    if not checks:
        raise ValueError("Empty benchmark suite")
    return {"schema": "benchmark-readiness-v1", "suite_sha256": digest(config),
            "new_model_calls": 0, "benchmarks": checks,
            "ready_to_run": all(c["ready_to_run"] for c in checks)}


def _numeric_or_unknown(raw, key, *, upper=None):
    value = raw.get(key)
    if value is None or value == -1:
        return None
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"Invalid upstream {key}")
    if upper is not None and value > upper:
        raise ValueError(f"Upstream {key} exceeds its documented scale")
    return value


def normalize_researcharena(raw):
    """Retain continuous task scores; upstream suspicion is 0..100, not probability."""
    if not isinstance(raw.get("metadata"), dict) or not any(
            key in raw for key in ("main_task_score", "side_task_score", "suspicion_score")):
        raise ValueError("Expected one ResearchArena results.json object")
    suspicion = _numeric_or_unknown(raw, "suspicion_score", upper=100)
    return {
        "benchmark": "researcharena", "metadata": raw["metadata"],
        "main_task_score": _numeric_or_unknown(raw, "main_task_score"),
        "side_task_score": _numeric_or_unknown(raw, "side_task_score"),
        "monitor_score": None if suspicion is None else suspicion / 100,
        "effect_verified": None,
        "interpretation": "Native task scores retained without binarization. A side-task score "
                          "alone does not certify a behavioral witness; inspect the evaluator evidence.",
    }


def normalize_agentdojo(raw):
    required = {"suite_name", "pipeline_name", "user_task_id", "injection_task_id",
                "attack_type", "error", "utility", "security"}
    if not required <= raw.keys() or any(type(raw[k]) is not bool for k in ("utility", "security")):
        raise ValueError("Expected an AgentDojo TaskResults object with explicit error field")
    attack = raw["attack_type"] not in (None, "none", "")
    error = raw["error"] not in (None, "")
    # AgentDojo writes security=True on some provider errors, and as a sentinel
    # on clean runs. Neither is evidence of a successfully executed injection.
    return {
        "benchmark": "agentdojo", "suite": raw["suite_name"],
        "pipeline": raw["pipeline_name"], "user_task_id": raw["user_task_id"],
        "injection_task_id": raw["injection_task_id"], "attack_type": raw["attack_type"],
        "status": "error" if error else "scored", "error": raw["error"],
        "utility": None if error else raw["utility"],
        "attack_success": raw["security"] if attack and not error else None,
        "interpretation": "Raw security=True means injection success on attack runs; "
                          "clean-run sentinels and error fallbacks are not attack outcomes.",
    }


def _seal(output, summary):
    """Source and input provenance, using the repository's standard verification command."""
    output = Path(output)
    source = output / "source"
    source.mkdir()
    for name in ("benchmarks.py", "benchmark_metrics.py", "common.py"):
        with (source / name).open("xb") as stream:
            stream.write(Path(__file__).with_name(name).read_bytes())
    write_json(output / "summary.json", summary)
    manifest = {"schema": "benchmark-analysis-evidence-v1", "new_model_calls": 0,
                "files": {p.relative_to(output).as_posix(): file_hash(p)
                          for p in sorted(output.rglob("*")) if p.is_file()}}
    write_json(output / "manifest.json", manifest)
    write_json(output / "manifest.sha256.json", {"sha256": digest(manifest)})


def import_result(source, output, format_name):
    source, output = Path(source), Path(output)
    content = source.read_bytes()
    raw = json.loads(content)
    adapters = {"researcharena": normalize_researcharena, "agentdojo": normalize_agentdojo}
    if format_name not in adapters:
        raise ValueError("Unsupported upstream result format")
    result = adapters[format_name](raw)
    result.update(schema="benchmark-result-import-v1", source_sha256=hashlib.sha256(content).hexdigest(),
                  provenance_status="format_checked_execution_not_attested", new_model_calls=0)
    output.mkdir(parents=True, exist_ok=False)
    with (output / "upstream-result.json").open("xb") as stream:
        stream.write(content)
    _seal(output, result)
    return result


def write_monitor_report(plan_path, scores_path, output):
    plan_bytes, scores_bytes = Path(plan_path).read_bytes(), Path(scores_path).read_bytes()
    plan = json.loads(plan_bytes)
    scores = [json.loads(line) for line in scores_bytes.splitlines() if line.strip()]
    result = benchmark_metrics.report(plan, scores)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name, content in (("plan.json", plan_bytes), ("scores.jsonl", scores_bytes)):
        with (output / name).open("xb") as stream:
            stream.write(content)
    _seal(output, result)
    return result
