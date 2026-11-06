# Evidence for the main story

Start with the [project overview](../README.md), then the
[results dashboard](../dashboard/index.html). The dashboard's checked-in
`data.json` supports inspection even when local raw runs are unavailable.

| Question | Evidence | Where to inspect |
| --- | --- | --- |
| Do agents follow feedback? | Advice, journal delivery, tool outcomes, and the next action | Dashboard “1. Following feedback”; full local episode transcripts |
| Does feedback reduce incidents? | First-incident episodes, repeated effects, completion, and unknowns | Dashboard “2. Incident reduction”; [native Haiku pilot](../docs/native-algorithms-results.md) |
| Do evaluation cues matter? | Journal-only, audited-notice, and unaudited-notice arms crossed with alternate-resource rewards | Dashboard “3. Evaluation awareness”; [study design](../docs/evaluation-awareness.md) |

## Local raw evidence

The ignored `runs/` directory retains `decision-algorithms-*`,
`native-algorithms-*`, and `eval-awareness-*` cohorts. Each includes its frozen
plan, source snapshot, inference records, and outcomes as originally recorded.
The dashboard exporter reads those paths without changing them.

The 6 November reorganization refreshed a stale dashboard export: 82 native
Sonnet episode placeholders now display their already-saved results. No new
episodes were run. The previous export remains in `archive/dashboard/data.json`.

Completed and interrupted cohorts are separate. Synthetic-workflow and native
recovery results use different task structures and outcome definitions. Native
repeat-effect counts are not currently exported; missing measurements must not
be represented as zero. The historical native Markdown report covers Haiku;
the dashboard additionally contains the Sonnet native cohort.

## Incident evidence

The [incident library](../incidents/README.md) retains public-report records,
sources, and draft codings. `incident-second-reader-v1/` retains the associated
blind review materials; prepared materials do not imply a completed independent
review. [Cross-case analysis](../docs/incident-library-analysis.md) motivates the
decisions studied in the fixtures.

Earlier experiment evidence is in [archive/results/](../archive/results/), and
the [archive index](../archive/README.md) explains the relocation manifest.
