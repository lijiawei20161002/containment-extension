# Continue the external-feedback project

Updated 6 November 2026. Start with [README.md](README.md).

The project story is reported agent incidents → decisions about continuing,
stopping, requesting, and probing → Grant Look-ahead and Effect Journal → three
empirical questions: feedback-following, initial/repeated incidents, and
evaluation awareness. The [roadmap](docs/experiment-roadmap.md) follows that order.

## Main working paths

- `src/containment_extension/grant_model.py`: finite belief-state planner and
  synthetic service-effect journal.
- `src/containment_extension/algorithm_study.py`: workflow feedback and
  evaluation-awareness cohorts. Historical selection/judge stages remain in this
  runner to preserve its protocol and frozen-plan compatibility.
- `src/containment_extension/native_algorithms.py`: feedback on the native
  recovery fixture, with the scope broker as an enforcement reference.
- `scripts/run_algorithm_study.py`, `scripts/run_native_algorithms.py`: prepare,
  execute, and inspect those studies.
- `dashboard/`: curated main results; `runs/`: original local evidence for
  decision-algorithms, native-algorithms, and eval-awareness cohorts.

## Evidence and execution

This reorganization made no model calls and changed no frozen run contents.
Do not overwrite evidence or interpret missing outcomes as clean runs. Completed
and interrupted cohorts remain distinct. Native summary status can be newer than
its execution-status file; the exporter reads the final summary when present.

Before resuming, inspect the run's plan, source hashes, worker/execution status,
and budget. Use its frozen source and existing resume rules. Do not replay a
completed cohort or retry a started episode to improve a result. Existing
configurations contain historical allocations; this cleanup authorizes no new
live allocation.

## Archive

[archive/README.md](archive/README.md) indexes retired directions and preserved
presentations. [archive/manifest.json](archive/manifest.json) maps each relocation
and records file hashes. The [previous handoff](archive/previous-main/HANDOFF.md)
retains historical execution details; it is not the active roadmap. Archived
scripts and tests may require restoring their original layout before execution.
