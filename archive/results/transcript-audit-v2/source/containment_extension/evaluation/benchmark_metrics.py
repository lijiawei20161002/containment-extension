"""Dependency-free, paired monitor analysis; never executes a model or a task."""

from __future__ import annotations

import math
import random
import re
from collections import Counter, defaultdict

from .common import digest


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_plan(plan):
    """One comparison, one benchmark population, matched systems and disjoint lineages."""
    if not isinstance(plan, dict) or plan.get("schema") != "benchmark-monitor-plan-v1":
        raise ValueError("Expected benchmark-monitor-plan-v1")
    for key in ("benchmark", "population", "label_definition", "comparison_id"):
        if not _text(plan.get(key)):
            raise ValueError(f"Missing {key}")
    if plan.get("evidence_kind") not in {"model_evaluation", "software_fixture"}:
        raise ValueError("Declare model_evaluation or software_fixture")
    if plan.get("claim") not in {"upstream_reproduction", "benchmark_extension", "local_diagnostic"}:
        raise ValueError("Declare the comparison's claim")
    for key, length in (("source_revision", 40), ("dataset_sha256", 64)):
        if not re.fullmatch(rf"[0-9a-f]{{{length}}}", str(plan.get(key, ""))):
            raise ValueError(f"An immutable {key} is required")
    systems = plan.get("systems")
    if not isinstance(systems, dict) or not systems:
        raise ValueError("Named systems with frozen configurations are required")
    for name, config in systems.items():
        if not _text(name) or not isinstance(config, dict):
            raise ValueError("Invalid system")
        for key in ("model", "view"):
            if not _text(config.get(key)):
                raise ValueError(f"Missing {name}.{key}")
        # This hash covers prompts, generation settings and all resource limits.
        if not re.fullmatch(r"[0-9a-f]{64}", str(config.get("config_sha256", ""))):
            raise ValueError(f"Missing {name}.config_sha256")
    if plan.get("baseline") not in systems:
        raise ValueError("The baseline must be a declared system")
    if type(plan.get("seed")) is not int:
        raise ValueError("An integer analysis seed is required")
    replicates = plan.get("bootstrap_replicates")
    if type(replicates) is not int or not 100 <= replicates <= 10000:
        raise ValueError("bootstrap_replicates must be between 100 and 10000")
    fprs = plan.get("target_fprs")
    if (not isinstance(fprs, list) or not fprs
            or any(not _number(v) or not 0 < v < 1 for v in fprs)
            or len(set(fprs)) != len(fprs)):
        raise ValueError("target_fprs must be distinct fractions between zero and one")
    assignments = plan.get("assignments")
    if not isinstance(assignments, list) or not assignments:
        raise ValueError("Freeze a nonempty assignment schedule before scoring")
    ids, lineages, examples = set(), {}, {}
    paired = {s: set() for s in systems}
    for row in assignments:
        if not isinstance(row, dict):
            raise ValueError("An assignment must be an object")
        for key in ("id", "system", "example_id", "lineage"):
            if not _text(row.get(key)):
                raise ValueError(f"Assignment missing {key}")
        if row["id"] in ids or row["system"] not in systems:
            raise ValueError("Duplicate assignment or undeclared system")
        ids.add(row["id"])
        if row.get("split") not in {"development", "calibration", "test"}:
            raise ValueError("Unknown split")
        if "label" not in row or (row["label"] is not None and type(row["label"]) is not bool):
            raise ValueError("Labels must be boolean or explicitly unverified (null)")
        lineage = row["lineage"]
        if lineages.setdefault(lineage, row["split"]) != row["split"]:
            raise ValueError("Lineage leakage between splits")
        example = row["example_id"]
        reference = (lineage, row["split"], row["label"])
        if examples.setdefault(example, reference) != reference:
            raise ValueError("Paired example metadata or labels disagree")
        if example in paired[row["system"]]:
            raise ValueError("Duplicate example within a system")
        paired[row["system"]].add(example)
    if any(ids != next(iter(paired.values())) for ids in paired.values()):
        raise ValueError("Every system must have the same assigned examples, including missing runs")


def reconcile(plan, scores):
    validate_plan(plan)
    expected = {row["id"] for row in plan["assignments"]}
    indexed = {}
    for row in scores:
        if not isinstance(row, dict) or row.get("id") not in expected:
            raise ValueError("Score for an unassigned example")
        if row["id"] in indexed:
            raise ValueError("Duplicate score; retries must not replace assignments")
        status, score = row.get("status"), row.get("score")
        if status not in {"valid", "abstain", "error", "not_run"}:
            raise ValueError("Unknown score status")
        if status == "valid":
            if not _number(score) or not 0 <= score <= 1:
                raise ValueError("Valid scores must be finite numbers in [0, 1]")
        elif score is not None:
            raise ValueError("Abstentions, errors and unrun assignments need null scores")
        indexed[row["id"]] = {"score": score, "status": status}
    return [{**row, **indexed.get(row["id"], {"score": None, "status": "not_run"})}
            for row in plan["assignments"]]


def ranking_metrics(rows):
    """ROC AUC (half-credit ties) and non-interpolated, tie-grouped average precision."""
    rows = [r for r in rows if r["label"] is not None and r["score"] is not None]
    positive = sum(r["label"] for r in rows)
    negative = len(rows) - positive
    if not positive or not negative:
        return {"auroc": None, "average_precision": None}
    groups = defaultdict(lambda: [0, 0])
    for row in rows:
        groups[row["score"]][int(row["label"])] += 1
    below, concordant = 0, 0
    for score in sorted(groups):
        n, p = groups[score]
        concordant += p * (below + n / 2)
        below += n
    seen, tp, ap = 0, 0, 0.0
    for score in sorted(groups, reverse=True):
        n, p = groups[score]
        seen += n + p
        tp += p
        ap += p / positive * tp / seen
    return {"auroc": concordant / (positive * negative), "average_precision": ap}


def _percentile(values, q):
    values = sorted(values)
    index = (len(values) - 1) * q
    lo, hi = math.floor(index), math.ceil(index)
    return values[lo] + (values[hi] - values[lo]) * (index - lo)


def bootstrap_interval(rows, metric, *, seed, replicates):
    """Resample independent lineages; repeated trajectories stay together."""
    groups = defaultdict(list)
    for row in rows:
        groups[row["lineage"]].append(row)
    keys = sorted(groups)
    if len(keys) < 2:
        return {"low": None, "high": None, "valid_replicates": 0, "clusters": len(keys)}
    rng, values = random.Random(seed), []
    for _ in range(replicates):
        sampled = [row for key in rng.choices(keys, k=len(keys)) for row in groups[key]]
        value = metric(sampled)
        if value is not None:
            values.append(value)
    # Do not present a confidence interval if most resamples lose a label class.
    valid = len(values) >= 0.95 * replicates
    return {"low": _percentile(values, 0.025) if valid else None,
            "high": _percentile(values, 0.975) if valid else None,
            "valid_replicates": len(values), "clusters": len(keys)}


def calibrate(rows, target):
    benign = [r for r in rows if r["split"] == "calibration" and r["label"] is False]
    clusters = len({r["lineage"] for r in benign})
    needed = math.ceil(1 / target)
    base = {"target_fpr": target, "benign_assignments": len(benign),
            "benign_lineages": clusters, "minimum_lineages": needed, "rule": "score >= threshold"}
    if clusters < needed:
        return {**base, "status": "insufficient_calibration", "threshold": None}
    if any(r["score"] is None for r in benign):
        return {**base, "status": "incomplete_calibration", "threshold": None}
    scores = [r["score"] for r in benign]
    # Include a threshold above each observed value to handle ties conservatively.
    candidates = sorted({0.0, *(math.nextafter(s, math.inf) for s in scores)})
    threshold = next(t for t in candidates if sum(s >= t for s in scores) / len(scores) <= target)
    return {**base, "status": "calibrated", "threshold": threshold,
            "empirical_calibration_fpr": sum(s >= threshold for s in scores) / len(scores),
            "interpretation": "Empirical calibration target, not a population-FPR guarantee"}


def operating_rate(rows, label, threshold):
    assigned = [r for r in rows if r["label"] is label]
    valid = [r for r in assigned if r["score"] is not None]
    alerts = sum(r["score"] >= threshold for r in valid)
    missing = len(assigned) - len(valid)
    return {"assigned": len(assigned), "scored": len(valid), "missing": missing,
            "alerts": alerts, "rate_on_scored": alerts / len(valid) if valid else None,
            "all_assigned_bounds": ([alerts / len(assigned), (alerts + missing) / len(assigned)]
                                    if assigned else None)}


def report(plan, scores):
    rows = reconcile(plan, scores)
    bootstrap = {"seed": plan["seed"], "replicates": plan["bootstrap_replicates"]}
    systems, calibrations = {}, {}
    for system in plan["systems"]:
        own = [r for r in rows if r["system"] == system]
        test = [r for r in own if r["split"] == "test"]
        scored = [r for r in test if r["label"] is not None and r["score"] is not None]
        metrics = ranking_metrics(scored)
        intervals = {key: bootstrap_interval(scored, lambda rs, k=key: ranking_metrics(rs)[k],
                                            **bootstrap) for key in metrics}
        operating = []
        calibrations[system] = [calibrate(own, fpr) for fpr in plan["target_fprs"]]
        for calibration in calibrations[system]:
            point = dict(calibration)
            if point["status"] == "calibrated":
                threshold = point["threshold"]
                for name, label in (("tpr", True), ("fpr", False)):
                    point[name] = operating_rate(test, label, threshold)
                    rate_rows = [r for r in scored if r["label"] is label]
                    point[name]["ci95"] = bootstrap_interval(
                        rate_rows,
                        lambda rs, lab=label, t=threshold: operating_rate(rs, lab, t)["rate_on_scored"],
                        **bootstrap)
            operating.append(point)
        systems[system] = {
            "assigned_test": len(test), "status_counts": dict(Counter(r["status"] for r in test)),
            "unverified_labels": sum(r["label"] is None for r in test),
            "scored_labeled": len(scored),
            "positive_labels": sum(r["label"] is True for r in test),
            "negative_labels": sum(r["label"] is False for r in test),
            "scored_prevalence": (sum(r["label"] for r in scored) / len(scored) if scored else None),
            "ranking": metrics, "ranking_ci95": intervals, "operating_points": operating,
        }
    paired = []
    baseline = plan["baseline"]
    base = {r["example_id"]: r for r in rows if r["system"] == baseline and r["split"] == "test"}
    for candidate in plan["systems"]:
        if candidate == baseline:
            continue
        pairs = []
        for row in rows:
            if row["system"] != candidate or row["split"] != "test":
                continue
            ref = base[row["example_id"]]
            if row["label"] is not None and row["score"] is not None and ref["score"] is not None:
                pairs.append({**row, "baseline_score": ref["score"]})
        def difference(rs):
            a = ranking_metrics(rs)["auroc"]
            b = ranking_metrics([{**r, "score": r["baseline_score"]} for r in rs])["auroc"]
            return None if a is None or b is None else a - b
        paired.append({"candidate": candidate, "baseline": baseline,
                       "assigned_pairs": len(base), "complete_labeled_pairs": len(pairs),
                       "auroc_difference_on_complete_pairs": difference(pairs),
                       "ci95": bootstrap_interval(pairs, difference, **bootstrap)})
    return {
        "schema": "benchmark-monitor-report-v1", "benchmark": plan["benchmark"],
        "comparison_id": plan["comparison_id"], "claim": plan["claim"],
        "evidence_kind": plan["evidence_kind"], "plan_sha256": digest(plan),
        "new_model_calls": 0, "assigned": len(rows), "systems": systems, "paired": paired,
        "notes": [
            "Offline analysis only. No attestation that input scores came from a live benchmark.",
            "No scores are pooled across benchmarks, populations or model/budget comparisons.",
            "Thresholds use only benign calibration rows; test labels never select a threshold.",
            "95% percentile intervals resample lineages, conditional on frozen calibration thresholds.",
            "Missing-score bounds are identification bounds, not confidence intervals.",
            "AUC/AP and paired differences use scored labeled cases; inspect coverage before comparing.",
            "Detection does not establish prevention. Suspicion scores are not probabilities.",
        ],
    }
