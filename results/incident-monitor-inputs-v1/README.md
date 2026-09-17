# Paired monitor inputs

Prepared September 17, 2026 from the completed cue and upstream-link studies.
Contains 1,543 proposed actions from 224 source rollouts. No monitor inference has
been run and this artifact reports no monitor performance.

`actions.jsonl.gz` has two views for each action: trusted instructions and prior
tool evidence, and the same input augmented with available visible actor text.
Every view ends at proposal time. The current action's response and all later
results are excluded. These are visible explanations, not private reasoning.

All actions and views from a source rollout share one deterministic split. The
held-out split contains new rollouts on the same task structure, not held-out task
families. Preserve that distinction when evaluating a monitor.

The original metric versions are preserved as labels. In particular, older
`out_of_scope` labels include failed catalog guesses, so the 324 such labels are
**not** 324 verified outside accesses. Adjudicate semantic scope before using them
as a monitor benchmark; do not tune on the held-out split. Labels are stored
outside the monitor inputs.

`audit.json` records paired-view, temporal-cutoff, and split-integrity checks.
`manifest.json` records source-file hashes, counts, and limitations. The exact
preparation script is archived here; regenerate from the repository root with:

```sh
python3 scripts/prepare_incident_monitors.py \
  results/cue-study-v1 results/link-study-v1 --output runs/monitor-inputs-new
```

This is preparation for the [monitor experiment](../../docs/incident-assessment-experiments.md),
with no API or GPU usage.
