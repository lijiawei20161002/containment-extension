# Coordination harness: implementation and offline execution

October 2, 2026. **Offline stages completed; live inference has not started.**
The figures are [proposed-design illustrations](counterfactual-replay.md),
not plots of model results.

## Completed in order

1. Implemented explicit effect/visibility contracts and an atomic SQLite journal
   for single counters, named counters, quota consumption, and local URL storage.
2. Ran eight paired counterfactual controls: all four shared fixtures exposed the
   expected receiver-response difference, and all four partitioned fixtures kept
   the tested receiver responses identical.
3. Ran twelve permission/fresh-pair controls; all passed. These controls establish
   local channel mechanics and semantic labels, not agent intent or live behavior.
4. Built 28 executable scripted cases with 84 frozen monitor inputs. Counter and
   named-counter families are development data; quota and URL storage are held out.
   Receiver-history views include real prior observations; the current proposed
   action's outcome is excluded.
5. Prepared the schedule for four authorized qualification pairs, sixteen later
   behavior/control pairs, and 84 monitor judgments. None has made an API request.

The initial `runs/coordination-harness-offline-v1/` preparation is preserved. The
updated `runs/coordination-harness-offline-v2/` preparation adds substantive earlier
receiver observations to the monitor-history arm. No live outcome was changed.
The [portable evidence export](../results/coordination-harness-offline-v2/README.md)
contains the frozen source, plan, JSON observations, library, and report.

## Verification

The exact staged repository snapshot passed **196 tests, with four optional tests
skipped** after the monitor-history refinement and before publication. It covers channel isolation,
strict local routing, atomic rollback on
journal failure, fresh-pair isolation, frozen-source checks, missing evidence,
budget reservation on provider failure, execution-once protection, live-protocol
simulation, and pre-action monitor cutoffs.

Provider-protocol tests use scripted responses. They are engineering verification
and are not counted as live model evidence. The current cartoon figures were
visually inspected and are accompanied by their image-generation prompts.

## Resources and pending live allocation

Python, SQLite, pytest, and both provider credential names are available on this
machine. Credential values were neither displayed nor archived. No GPU, Docker,
VM, or public web service is needed. The proposed model is the existing pinned
Haiku 4.5 API model; no model availability or live protocol success is claimed yet.

The prepared plan records a **proposed $10 ceiling**, `live_authorized: false`,
zero requests, and zero API spend. The user's new spending-cap choice is pending;
earlier allocations are not carried over. A live plan must be prepared in a new
directory with that chosen cap before execution. Additional repetitions would
require an explicitly revised schedule, not just a higher dollar ceiling.

```sh
# Offline; no credentials or network required.
PYTHONPATH=src python3 scripts/run_coordination_study.py prepare \
  --output runs/coordination-harness-offline-v2
PYTHONPATH=src python3 scripts/run_coordination_study.py report \
  --output runs/coordination-harness-offline-v2
python3 scripts/draw_coordination_figures.py
```

These preparation paths now exist; use a new output directory to reproduce.
Live code and reporting are implemented and tested with scripted providers. The
first actual provider responses still need to qualify the frozen live protocol.
The API runner stops on errors/refusals without retries or model substitutions.
