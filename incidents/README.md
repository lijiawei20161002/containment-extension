# Incident library

A structured, reviewable record of public agent-security incidents, built so that
each case can feed (a) cross-case analysis, (b) monitor signatures, and (c) the
executable history library proposed in the
[v2 incident-aware optimization design](../docs/incident-aware-optimization.md).

Current contents: entries 1–26 of the public-source briefing completed on
27 September 2026 (entries 27–30, litigation and service outages, are excluded
because they contain no agent-action chain). Coding frame: Raftari (2026),
*From Reactive Containment to Proactive Assurance* (arXiv:2610.12463).

```text
incidents/
├── README.md                    this design note
├── taxonomy.json                controlled vocabularies (generated)
├── schema/incident.schema.json  JSON Schema exported from the pydantic model (generated)
├── records/NN-<slug>.json       one record per incident (generated from scripts/incident_codings.py)
└── incidents.duckdb             flat `incidents` table + raw JSON for ad-hoc SQL (generated)
```

Source of truth is `scripts/incident_codings.py` (hand-written codings) plus the
pydantic model in `src/containment_extension/incident_library.py`. Everything
else is produced by `python3 scripts/build_incident_library.py`; the analysis in
`docs/incident-library-analysis.md` and `figures/incidents/analysis/` is produced by
`python3 scripts/analyze_incident_library.py`.

## Design principles

1. **Claim-level evidence.** Every record carries an evidence level (A primary,
   B attributed secondary, C unverified; Raftari §3.2), the named sources, who
   confirmed the core facts, whether the account is disputed, and an explicit
   `counting_unit` so that "19 actions", "4 runs", "53 instances" and "27
   companies" are never added together.
2. **Facts separate from codings.** `summary`, `dates`, `timeline`, `evidence`
   and `impact` restate the public record. `pathway`, `mechanisms`,
   `propositions`, `indicators`, `controls` and `stop_behavior` are analyst
   judgments, each with a short note, and are marked `review_status: draft`
   until a second reader confirms them.
3. **One frame, extended where the data forces it.** Raftari's two pathways
   (adaptive escape, misconfiguration exposure) cover only 9 of 26 entries, so the
   vocabulary adds live-access overreach, training-sample boundary, external
   adversary, and unresolved. Mechanisms M1–M6, propositions P1–P9, the
   leading-indicator vector (f, p, x, c, v, o) and the five BAS layers are used
   unchanged so results map back to the paper's hypotheses.
4. **Splittable.** `lineage.group` names the shared-cause family (e.g.
   `openai-training-samples-2026`) and `dates.*` give the time axis, so the
   library can be partitioned by lineage or by date for development vs held-out
   use, as the v2 design requires.
5. **Linked to artifacts.** Each record points at its explanatory figure and
   figure spec, and reserves `executable.*` for a replay case, synthetic twin
   and benign twin once those exist. Entry 15 now links to an implemented offline
   workbook-sharing case in `executable/INC-2026-015/`.
6. **Plain files.** JSON in git, validated by a schema, queried through DuckDB.
   No service to run; diffs are reviewable in a pull request.

## Record shape

| Group | Fields | Purpose |
|---|---|---|
| Identity | `id`, `entry_number`, `slug`, `title`, `short_title`, `actor`, `models` | Stable keys; `id` = `INC-YYYY-NNN` |
| Classification | `category`, `pathway`, `pathway_note` | What kind of event; which causal pathway |
| Facts | `summary`, `dates`, `timeline[]`, `impact`, `evidence` | Public record with evidence level, sources, counting unit, limits |
| Coding (Raftari §3.3) | `coding.{objective, capability, environment, resource, boundary, signals, actions, response}` | The eight-dimension event code |
| Cross-case frame | `mechanisms{M1..M6}`, `propositions{P1..P9}`, `indicators{f,p,x,c,v,o}`, `controls.bas_layers_implicated`, `stop_behavior` | Enables the heatmaps and the monitor design |
| Controls | `controls.{failed, worked, added_after}` | What broke, what held, what was added |
| Library plumbing | `lineage`, `figure`, `figure_spec`, `executable`, `external_ids`, `provenance` | Splits, artifacts, replay hooks, AIID/MIT ids, audit trail |

Enumerations live in `taxonomy.json`; the JSON Schema in `schema/` is what an
external contributor validates against (`jsonschema` or the pydantic model).

## Lifecycle

1. **Intake.** From a public report: fill facts first (dates, sources, counting
   unit, limits), then code. From own evaluation logs (Inspect `.eval` files):
   derive `coding.actions`/`capability` from tool and sandbox events, `signals`
   from approval and monitor events, `dates` from timestamps; the record points
   at the log instead of a figure.
2. **Review.** A second reader checks the codings against the sources and flips
   `review_status` to `reviewed`; `verified` is reserved for cases where an
   affected party or primary technical report confirms the mechanism.
3. **Use.** Analysis (`analyze_incident_library.py`), monitor signatures (the
   indicator and mechanism columns), regression cases (the `executable` block).
4. **Update.** New disclosures change records in place with a new
   `provenance.compiled_on`; the git history is the version history. Never
   delete a record because attribution weakened; set `evidence.disputed` and
   lower the evidence level instead.

## Querying

```python
from containment_extension.incident_library import load_records, to_duckdb
recs = load_records()
con = to_duckdb(recs)
con.execute("""
  SELECT pathway, count(*) n, sum(mech_M1 = 'present') m1, sum(ind_x = 'yes') ext_contact
  FROM incidents GROUP BY 1 ORDER BY n DESC""").fetchall()
```

## Mapping to external schemas

The record is deliberately narrower than STIX 2.1 or OCSF. When exporting:
`actions`/`capability` map to STIX attack patterns and tool objects,
`impact` to OCSF finding severity fields, and `external_ids` keeps AI Incident
Database / MIT AI Incident Tracker identifiers so duplicates can be reconciled.
