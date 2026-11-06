# Upstream baseline preparation, September 21, 2026

**No model inference was performed.** This archive contains a qualified six-run
proposal using the original ImpossibleBench tools solver, prompts and scorer.
The proposed new live allocation is capped at $45; no execution marker exists.
See the [protocol](../../docs/impossiblebench-upstream-baseline.md).

| Local validation | Result |
| --- | --- |
| Full repository suite, including Docker and Inspect | 142 passed |
| Additional call-20 and durable per-run-budget regressions | 2 passed (included in the subsequent 57-test targeted run) |
| Upstream unchanged/reference controls | 12/12 passed |
| Upstream real tool-loop, repair and exit controls | 4/4 passed |
| Revised custom runner reference/environment controls | 12/12 passed |
| Revised custom runner observer controls | 6/6 passed |
| Revised custom runner real lifecycle controls | 12/12 passed |

The upstream reference repair passes each original issue and fails each impossible
variant. Unchanged implementations fail all six variants. Scripted original
repairs use six mock model responses; conflicting controls use seven and honor the
upstream intervention marker after scored failure. All actor tools work with
UID 1000, no routes, zero effective capabilities and no-new-privileges.

`upstream-plan/` includes the frozen assignment/config/source hashes, reviewed
dataset rows, upstream Python sources, Compose files, raw Inspect logs and control
reports. Its summary correctly has six unknown live outcomes. `source/` preserves
the local implementation and selected tests/configs. Other JSON/XML files preserve
the custom-runner qualification and test evidence. `sha256.json` hashes the evidence
and source files captured at archive creation (this README is descriptive metadata).

`initial-editor-diagnostic.json` preserves the failed first image test: Inspect
attempted to chmod a user-owned tool binary as root without capabilities. The final
images preinstall the identical bundled binary; the actor's privileges were not
expanded. This diagnostic is not a model failure or a live assignment.

Live execution must use `runs/impossiblebench-upstream-baseline-proposed-02/` on
this machine; paths in the logs refer there. The archive is a copy for review,
not a second allocation. Completed prior live archives remain unchanged.
