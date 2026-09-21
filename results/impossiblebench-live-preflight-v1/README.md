# Live ImpossibleBench preflight evidence

September 21, 2026. See the [results and limitations](../../docs/impossiblebench-live-preflight-results.md).
The approved allocation stopped with 16 assignments started and eight unstarted.
There were no scored submissions or delivered interventions. All 24 primary
violation outcomes remain unknown; these data do not establish an intervention
effect.

- `execution-analysis.json`: assigned outcomes, interruption annotation, and
  combined accounting across both phases.
- `summary.json`: standard assigned-denominator report. The interrupted raw
  result retains `stop: running`; use the analysis annotation for execution status.
- `initial-plan.json`, `continuation-plan.json`, `authorization.json`: frozen
  schedules/configurations and the user authorization. The first plan's historical
  `proposed_not_authorized` metadata is superseded by the separate authorization.
- `reconciled-prior-budget.json`: every first-phase request, cached-token counts,
  the unresolved reservation, and the exact remaining allocation.
- `evidence.tar.gz`: complete `initial/` and `continuation/` directories, including
  source snapshots, original result files, messages, transcripts, provider usage,
  qualification, execution markers, and initial Inspect logs. Three carried
  result directories intentionally appear in both phases and must not be counted
  twice. The continuation report is the combined 24-assignment denominator.
- `qualification.json.gz`, `linux-tests.xml`: successful qualification after the
  accounting correction and the 121-test Linux run.
- `implementation-review.json`: complete saved pytest implementation diffs,
  source/result hashes, and review notes. No clean-outcome labels were assigned
  to incomplete runs.
- `run_live_continuation.py`, `analyze_live_preflight.py`: exact continuation and
  analysis drivers. They refer to the original ignored `runs/` paths; the former
  is bound by hash in the continuation plan and refuses duplicate execution.
- `manifest.json`: SHA-256 hashes of the archived evidence files.

The first 48 requests used the previous adapter, whose budget omitted cached
input tokens. The study was stopped, the bug fixed and tested, and the tasks
requalified. The continuation deducted reconciled prior usage and ran only
unstarted assignments. Original outcomes and accounting files remain intact;
use the reconciled ledger for totals. No rollout was retried.

All known credential values were checked against the evidence, including
decompressed Inspect log members, before archiving. No credentials or `.env`
files are included. All temporary task containers were removed.

```sh
tar -tzf results/impossiblebench-live-preflight-v1/evidence.tar.gz
gzip -dc results/impossiblebench-live-preflight-v1/qualification.json.gz | less
```
