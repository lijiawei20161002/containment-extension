"""Cross-case analysis of the incident library -> figures/incidents/analysis/ + docs/incident-library-analysis.md.

Charts follow the dataviz method: one hue for magnitude (blue ramp), a validated
blue/orange pair with a hatched neutral for polarity, shapes + legends so identity is
never color-alone, thin marks, recessive grid.
"""
from __future__ import annotations
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from containment_extension.incident_library import (  # noqa: E402
    INDICATOR_LABELS, MECHANISM_LABELS, PROPOSITION_LABELS, Pathway, load_records)

OUT = HERE.parent / "figures" / "incidents" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)
DOC = HERE.parent / "docs" / "incident-library-analysis.md"

plt.rcParams.update({"font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"], "font.size": 11,
                     "axes.edgecolor": "#d6dae0", "axes.linewidth": 0.8, "xtick.color": "#5b6068", "ytick.color": "#222733",
                     "axes.labelcolor": "#5b6068", "text.color": "#222733", "figure.facecolor": "#ffffff", "axes.facecolor": "#ffffff"})
NAVY, BLUE, ORANGE, INK, MUTED = "#1b2d55", "#1c5cab", "#eb6834", "#222733", "#5b6068"
SEQ = {"present": "#1c5cab", "partial": "#86b6ef", "absent": "#eceef1", "unknown": "#ffffff"}
POL = {"violated": "#1c5cab", "demonstrated": "#eb6834", "mixed": "#c9ced6", "not_applicable": "#ffffff"}
TRI = {"yes": "#1c5cab", "no": "#eceef1", "unknown": "#ffffff"}
PATHWAY_LABEL = {"adaptive_escape": "Adaptive escape", "misconfiguration_exposure": "Misconfiguration exposure", "live_access_overreach": "Live-access overreach",
                 "training_sample_boundary": "Training-sample boundary", "external_adversary": "External adversary", "unresolved": "Unresolved"}
PATHWAY_ORDER = ["adaptive_escape", "misconfiguration_exposure", "live_access_overreach", "training_sample_boundary", "external_adversary", "unresolved"]
CATEGORY_LABEL = {"agent_scope_violation": "Agent scope violation", "evaluation_exposure": "Evaluation exposure", "training_time_behavior": "Training-time behavior",
                  "external_attack_on_ai_infra": "External attack on AI infra", "human_directed_misuse": "Human-directed misuse", "attribution_unresolved": "Attribution unresolved"}
STOP_LABEL = {"none_observed": "No stop observed", "self_stop_after_access": "Self-stop after access", "automatic_stop": "Automatic stop",
              "automatic_stop_failed_then_manual": "Auto-stop failed → manual", "manual_stop": "Manual stop / revocation", "contained_by_third_party": "Contained by third party",
              "human_stop_ignored": "Human stop ignored", "retrospective_only": "Found only in retrospect", "not_applicable": "Not applicable"}


def head(ax, title, subtitle, t_off=48, s_off=32):
    ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(0, t_off), textcoords="offset points", fontsize=15, fontweight="bold", color=NAVY, va="bottom", ha="left")
    ax.annotate(subtitle, xy=(0, 1), xycoords="axes fraction", xytext=(0, s_off), textcoords="offset points", fontsize=10, color=MUTED, va="bottom", ha="left")


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def row_label(r):
    return f"{r.entry_number:>2}  {r.short_title}"


def matrix_chart(recs, cols, getter, palette, name, title, subtitle, legend_items, col_labels=None, total_key=None, hatch_key=None, width=10.5):
    ordered = [r for p in PATHWAY_ORDER for r in recs if r.pathway.value == p]
    n, m = len(ordered), len(cols)
    fig, ax = plt.subplots(figsize=(width, 0.34 * n + 2.2))
    for i, r in enumerate(ordered):
        for j, c in enumerate(cols):
            v = getter(r, c)
            face = palette[v]
            hatched = v == hatch_key
            ax.add_patch(Rectangle((j + 0.06, n - 1 - i + 0.06), 0.88, 0.88, facecolor=face,
                                   edgecolor="#9aa2ad" if hatched else ("#d6dae0" if face == "#ffffff" else "none"),
                                   linewidth=0.6, hatch="////" if hatched else None))
    # pathway group separators and labels
    y = n
    for p in PATHWAY_ORDER:
        k = sum(1 for r in ordered if r.pathway.value == p)
        if not k:
            continue
        y -= k
        ax.axhline(y, color="#9aa2ad", linewidth=0.8)
        ax.text(m + 0.25, y + k / 2, PATHWAY_LABEL[p], va="center", ha="left", fontsize=9.5, color=MUTED)
    ax.set_xlim(0, m + 3.4); ax.set_ylim(0, n)
    ax.set_yticks([n - 1 - i + 0.5 for i in range(n)]); ax.set_yticklabels([row_label(r) for r in ordered], fontsize=9.5)
    ax.set_xticks([j + 0.5 for j in range(m)]); ax.set_xticklabels(col_labels or cols, fontsize=9.5, color=INK)
    ax.xaxis.tick_top(); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    if total_key:
        for j, c in enumerate(cols):
            t = sum(1 for r in ordered if getter(r, c) == total_key)
            ax.text(j + 0.5, -0.35, str(t), ha="center", va="top", fontsize=10, color=INK, fontweight="bold")
        ax.text(-0.1, -0.35, f"count '{total_key}'", ha="right", va="top", fontsize=9, color=MUTED)
        ax.set_ylim(-0.9, n)
    head(ax, title, subtitle, 78, 62)
    ax.legend(handles=legend_items, loc="lower left", bbox_to_anchor=(0, -0.09 - 0.6 / n), ncol=len(legend_items), frameon=False, fontsize=9.5, handlelength=1.4)
    save(fig, name)
    return ordered


def main():
    recs = load_records()
    n = len(recs)
    stats = {"n": n}

    # ---------------------------------------------------------------- pathways bar
    pc = Counter(r.pathway.value for r in recs)
    stats["pathways"] = {p: pc.get(p, 0) for p in PATHWAY_ORDER}
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ys = list(range(len(PATHWAY_ORDER)))[::-1]
    vals = [pc.get(p, 0) for p in PATHWAY_ORDER]
    bars = ax.barh(ys, vals, height=0.52, color=[BLUE if p in ("adaptive_escape", "misconfiguration_exposure") else "#86b6ef" for p in PATHWAY_ORDER])
    for b, v in zip(bars, vals):
        ax.text(v + 0.15, b.get_y() + b.get_height() / 2, str(v), va="center", fontsize=11, color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([PATHWAY_LABEL[p] for p in PATHWAY_ORDER], fontsize=11)
    ax.set_xlim(0, max(vals) + 2); ax.set_xticks([]); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Incident pathways across the 26 cases", loc="left", fontsize=14, fontweight="bold", color=NAVY, pad=14)
    ax.legend(handles=[Patch(color=BLUE, label="Usual pathways in the literature"), Patch(color="#86b6ef", label="Added to cover the 2026 cases")], loc="lower right", frameon=False, fontsize=9.5)
    save(fig, "pathways-bar")

    # ---------------------------------------------------------------- mechanisms heatmap
    mech_cols = ["M1", "M2", "M3", "M4", "M5", "M6"]
    matrix_chart(recs, mech_cols, lambda r, c: r.mechanisms[c].status, SEQ, "mechanism-heatmap",
                 "Six cross-case failure mechanisms, coded per incident", "Rows grouped by pathway. Hatched = not determinable from the public record.",
                 [Patch(color=SEQ["present"], label="present"), Patch(color=SEQ["partial"], label="partial"), Patch(color=SEQ["absent"], label="absent"),
                  Patch(facecolor="#fff", edgecolor="#9aa2ad", hatch="////", label="unknown")],
                 col_labels=[f"{c}\n{l}" for c, l in zip(mech_cols, ["Objective\npressure", "Capability\ncomposition", "Shared\nstate", "Detection w/o\nescalation", "Env. grounding\n& audit gaps", "Fragmented\nownership"])], total_key="present", hatch_key="unknown")
    stats["mechanisms"] = {c: Counter(r.mechanisms[c].status for r in recs) for c in mech_cols}

    # ---------------------------------------------------------------- propositions heatmap
    prop_cols = [f"P{i}" for i in range(1, 10)]
    matrix_chart(recs, prop_cols, lambda r, c: r.propositions[c].relation, POL, "proposition-heatmap",
                 "Nine design propositions: which incidents violate or demonstrate them", "Blue = case shows what happens without the proposition; orange = case shows it working; hatched gray = mixed.",
                 [Patch(color=POL["violated"], label="violated"), Patch(color=POL["demonstrated"], label="demonstrated"), Patch(facecolor=POL["mixed"], hatch="////", edgecolor="#9aa2ad", label="mixed"),
                  Patch(facecolor="#fff", edgecolor="#d6dae0", label="not applicable")], total_key="violated", hatch_key="mixed", width=11.5)
    stats["propositions"] = {c: Counter(r.propositions[c].relation for r in recs) for c in prop_cols}

    # ---------------------------------------------------------------- indicators matrix
    ind_cols = ["f", "p", "x", "c", "v", "o"]
    matrix_chart(recs, ind_cols, lambda r, c: r.indicators[c], TRI, "indicator-matrix",
                 "Leading indicators observed per incident", "z_t = (f, p, x, c, v, o). Hatched = unknown from the public record.",
                 [Patch(color=TRI["yes"], label="observed"), Patch(color=TRI["no"], label="not observed"), Patch(facecolor="#fff", edgecolor="#9aa2ad", hatch="////", label="unknown")],
                 col_labels=[f"{c}\n{l}" for c, l in zip(ind_cols, ["repeated\nfailure", "boundary\nprobing", "external\ncontact", "cross-run\ncomms", "privilege\nchange", "observability\nloss"])], total_key="yes", hatch_key="unknown", width=9.5)
    stats["indicators"] = {c: Counter(r.indicators[c] for r in recs) for c in ind_cols}

    # ---------------------------------------------------------------- latency dumbbell
    def parse(d):
        if not d:
            return None
        p = d.split("-")
        try:
            return date(int(p[0]), int(p[1]), int(p[2]) if len(p) == 3 else 15)
        except (ValueError, IndexError):
            return None
    rows = [(r, parse(r.dates.occurred_start), parse(r.dates.detected), parse(r.dates.disclosed)) for r in recs]
    rows = [t for t in rows if t[1] and t[3]]
    rows.sort(key=lambda t: t[1])
    fig, ax = plt.subplots(figsize=(10.5, 0.33 * len(rows) + 2.0))
    x0 = date(2025, 10, 1)
    def xd(d): return (d - x0).days
    for i, (r, o, det, dis) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([xd(o), xd(dis)], [y, y], color="#c9ced6", linewidth=2, zorder=1)
        ax.plot(xd(o), y, marker="o", markersize=8, markerfacecolor="#fff", markeredgecolor=BLUE, markeredgewidth=2, zorder=3)
        if det:
            ax.plot(xd(det), y, marker="D", markersize=6.5, color="#86b6ef", markeredgecolor="#fff", markeredgewidth=1.5, zorder=4)
        ax.plot(xd(dis), y, marker="o", markersize=8, color=BLUE, markeredgecolor="#fff", markeredgewidth=1.5, zorder=5)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([row_label(r) for r, *_ in rows][::-1], fontsize=9.5)
    months = [date(2025, 10, 1), date(2025, 12, 1), date(2026, 2, 1), date(2026, 4, 1), date(2026, 6, 1), date(2026, 8, 1), date(2026, 10, 1)]
    ax.set_xticks([xd(m) for m in months]); ax.set_xticklabels([m.strftime("%b %Y") for m in months], fontsize=9.5)
    ax.grid(axis="x", color="#eceef1", linewidth=1); ax.set_axisbelow(True); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    head(ax, "From occurrence to public disclosure", "Month-precision dates plotted mid-month; entries without a known occurrence date omitted (3, 9, 17, 18, 22).", 46, 30)
    ax.legend(handles=[Line2D([], [], marker="o", color="w", markerfacecolor="#fff", markeredgecolor=BLUE, markeredgewidth=2, markersize=8, label="occurred (start)"),
                       Line2D([], [], marker="D", color="w", markerfacecolor="#86b6ef", markersize=7, label="detected / discovered"),
                       Line2D([], [], marker="o", color="w", markerfacecolor=BLUE, markersize=8, label="publicly disclosed")],
              loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, frameon=False, fontsize=9.5, borderaxespad=0.2)
    save(fig, "latency-dumbbell")
    det = [r.detection_latency_days for r in recs if r.detection_latency_days is not None]
    dis = [r.disclosure_latency_days for r in recs if r.disclosure_latency_days is not None]
    stats["latency"] = {"detection_days_known": len(det), "detection_median": statistics.median(det), "detection_values": {r.entry_number: r.detection_latency_days for r in recs if r.detection_latency_days is not None},
                        "disclosure_days_known": len(dis), "disclosure_median": statistics.median(dis), "disclosure_values": {r.entry_number: r.disclosure_latency_days for r in recs if r.disclosure_latency_days is not None}}

    # ---------------------------------------------------------------- stop behaviour bar
    sc = Counter(r.stop_behavior for r in recs)
    order = ["none_observed", "retrospective_only", "self_stop_after_access", "automatic_stop_failed_then_manual", "human_stop_ignored", "manual_stop", "contained_by_third_party", "not_applicable"]
    order = [o for o in order if sc.get(o)]
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    ys = list(range(len(order)))[::-1]
    vals = [sc[o] for o in order]
    bars = ax.barh(ys, vals, height=0.52, color=BLUE)
    for b, v in zip(bars, vals):
        ax.text(v + 0.15, b.get_y() + b.get_height() / 2, str(v), va="center", fontsize=11, color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([STOP_LABEL[o] for o in order], fontsize=11)
    ax.set_xlim(0, max(vals) + 2); ax.set_xticks([]); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("How each incident stopped", loc="left", fontsize=14, fontweight="bold", color=NAVY, pad=14)
    save(fig, "stop-behavior-bar")
    stats["stop_behavior"] = dict(sc)

    # ---------------------------------------------------------------- other counts
    stats["categories"] = dict(Counter(r.category.value for r in recs))
    stats["evidence_levels"] = dict(Counter(r.evidence.level for r in recs))
    stats["actors"] = dict(Counter(r.actor.split(" (")[0] for r in recs))
    stats["bas_layers"] = dict(Counter(l for r in recs for l in r.controls.bas_layers_implicated))
    stats["replayable"] = [r.entry_number for r in recs if r.executable.replayable]
    stats["lineage_groups"] = dict(Counter(r.lineage.group for r in recs))
    stats["pathway_by_category"] = {c: dict(Counter(r.pathway.value for r in recs if r.category.value == c)) for c in stats["categories"]}
    co = Counter()
    for r in recs:
        present = [c for c in mech_cols if r.mechanisms[c].status == "present"]
        for a in present:
            for b in present:
                if a < b:
                    co[(a, b)] += 1
    stats["mechanism_cooccurrence_top"] = [[a, b, k] for (a, b), k in co.most_common(6)]
    (OUT / "summary.json").write_text(json.dumps(stats, indent=1, default=str), encoding="utf-8")

    # ---------------------------------------------------------------- markdown doc
    def pct(k):
        return f"{k}/{n}"
    L = ["# Incident library: cross-case analysis", "",
         "*Generated by `scripts/analyze_incident_library.py` from `incidents/records/`. Codings are analyst drafts; facts come from public reporting; the coding frame follows Raftari (2026).*", "",
         "## Coverage", "",
         f"- {n} records: entries 1–26 (litigation and service-outage cases excluded).",
         "- Categories: " + ", ".join(f"{CATEGORY_LABEL[k]} {v}" for k, v in sorted(stats['categories'].items(), key=lambda kv: -kv[1])) + ".",
         "- Evidence levels: " + ", ".join(f"{k}: {v}" for k, v in sorted(stats['evidence_levels'].items())) + ".",
         "- Replayable as synthetic twins (analyst judgment): entries " + ", ".join(map(str, stats["replayable"])) + ".", "",
         "## Pathways (two usual ones, plus four needed for the 2026 cases)", "", "| Pathway | Count | Entries |", "|---|---|---|"]
    for p in PATHWAY_ORDER:
        L.append(f"| {PATHWAY_LABEL[p]} | {pc.get(p, 0)} | {', '.join(str(r.entry_number) for r in recs if r.pathway.value == p)} |")
    L += ["", "![pathways](../figures/incidents/analysis/pathways-bar.png)", "",
          "## Failure mechanisms (M1–M6)", "", "| Mechanism | present | partial | absent | unknown |", "|---|---|---|---|---|"]
    for c in mech_cols:
        k = stats["mechanisms"][c]
        L.append(f"| {c} {MECHANISM_LABELS[c]} | {k.get('present', 0)} | {k.get('partial', 0)} | {k.get('absent', 0)} | {k.get('unknown', 0)} |")
    L += ["", "Top co-occurrences of 'present' mechanisms: " + "; ".join(f"{a}+{b} ({k})" for a, b, k in stats["mechanism_cooccurrence_top"]) + ".",
          "", "![mechanisms](../figures/incidents/analysis/mechanism-heatmap.png)", "",
          "## Design propositions (P1–P9)", "", "| Proposition | violated | demonstrated | mixed | n/a |", "|---|---|---|---|---|"]
    for c in prop_cols:
        k = stats["propositions"][c]
        L.append(f"| {c} {PROPOSITION_LABELS[c]} | {k.get('violated', 0)} | {k.get('demonstrated', 0)} | {k.get('mixed', 0)} | {k.get('not_applicable', 0)} |")
    L += ["", "![propositions](../figures/incidents/analysis/proposition-heatmap.png)", "",
          "## Leading indicators (z_t)", "", "| Indicator | observed | not observed | unknown |", "|---|---|---|---|"]
    for c in ind_cols:
        k = stats["indicators"][c]
        L.append(f"| {c} {INDICATOR_LABELS[c]} | {k.get('yes', 0)} | {k.get('no', 0)} | {k.get('unknown', 0)} |")
    L += ["", "![indicators](../figures/incidents/analysis/indicator-matrix.png)", "",
          "## Detection and disclosure latency", "",
          f"- Detection latency known for {stats['latency']['detection_days_known']} entries; median {stats['latency']['detection_median']:.0f} days.",
          f"- Disclosure latency known for {stats['latency']['disclosure_days_known']} entries; median {stats['latency']['disclosure_median']:.0f} days.",
          "", "![latency](../figures/incidents/analysis/latency-dumbbell.png)", "",
          "## Stop behaviour", "", "| Stop behaviour | Count |", "|---|---|"]
    for o in order:
        L.append(f"| {STOP_LABEL[o]} | {sc[o]} |")
    L += ["", "![stop](../figures/incidents/analysis/stop-behavior-bar.png)", "",
          "## BAS layers implicated", "", ", ".join(f"{k}: {v}" for k, v in sorted(stats["bas_layers"].items())), ""]
    DOC.write_text("\n".join(L), encoding="utf-8")
    print(json.dumps({k: stats[k] for k in ("pathways", "stop_behavior", "evidence_levels", "bas_layers")}, indent=0))
    print("latency medians", stats["latency"]["detection_median"], stats["latency"]["disclosure_median"])
    print("mech present", {c: stats["mechanisms"][c].get("present", 0) for c in mech_cols})
    print("prop violated", {c: stats["propositions"][c].get("violated", 0) for c in prop_cols})
    print("ind yes", {c: stats["indicators"][c].get("yes", 0) for c in ind_cols})
    print("cooc", stats["mechanism_cooccurrence_top"])


if __name__ == "__main__":
    main()
