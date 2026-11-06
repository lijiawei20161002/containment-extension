"""Small-sample summaries with explicit missing-outcome bounds."""

import math
import random


def binary(values):
    observed = [bool(v) for v in values if v is not None]
    n, k, assigned = len(observed), sum(observed), len(values)
    interval = None
    if n:
        z = 1.959963984540054
        center = (k / n + z * z / (2 * n)) / (1 + z * z / n)
        radius = z * math.sqrt(k / n * (1 - k / n) / n + z * z / (4 * n * n))
        radius /= 1 + z * z / n
        interval = [max(0, center - radius), min(1, center + radius)]
    return {
        "positive": k,
        "observed": n,
        "assigned": assigned,
        "unknown": assigned - n,
        "rate": k / n if n else None,
        "wilson95": interval,
        "assigned_bounds": [k / assigned, (k + assigned - n) / assigned] if assigned else None,
    }


def paired(rows, endpoint, *, variants):
    """B4 minus B3, paired by fixture seed; bootstrap whole seeds, not cells."""
    bank = {(r["candidate"], r["variant"], r["seed"]): r[endpoint] for r in rows}
    seeds = sorted({r["seed"] for r in rows})
    pairs, clusters, lows, highs = [], [], [], []
    for seed in seeds:
        cluster = []
        for variant in variants:
            a = bank.get(("B3", variant, seed))
            b = bank.get(("B4", variant, seed))
            delta = int(b) - int(a) if a is not None and b is not None else None
            pairs.append({"seed": seed, "variant": variant, "B3": a, "B4": b, "difference": delta})
            lows.append((int(b) if b is not None else 0) - (int(a) if a is not None else 1))
            highs.append((int(b) if b is not None else 1) - (int(a) if a is not None else 0))
            cluster.append(delta)
        if all(v is not None for v in cluster):
            clusters.append(sum(cluster) / len(cluster))
    deltas = [p["difference"] for p in pairs if p["difference"] is not None]
    ci = None
    if len(clusters) >= 2:
        rng = random.Random(20261020)
        samples = sorted(
            sum(rng.choices(clusters, k=len(clusters))) / len(clusters) for _ in range(10000)
        )
        ci = [samples[249], samples[9749]]
    return {
        "pairs": pairs,
        "complete_pairs": len(deltas),
        "difference": sum(deltas) / len(deltas) if deltas else None,
        "assigned_bounds": [sum(lows) / len(lows), sum(highs) / len(highs)] if lows else None,
        "seed_bootstrap95": ci,
        "complete_seeds": len(clusters),
        "interpretation": "Exploratory seed-cluster percentile interval; one task structure, "
        "very few seeds. A degenerate interval is not proof of equivalence.",
    }
