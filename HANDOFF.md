# Continue the ImpossibleBench transfer study

Updated September 21, 2026. The approved live preflight has executed and stopped
within its budget. It produced **no scored submissions or intervention deliveries**;
this run cannot estimate intervention effects. Read the
[live report](docs/impossiblebench-live-preflight-results.md) and
[evidence archive](results/impossiblebench-live-preflight-v1/README.md).

## Latest execution

The user approved the prepared 24-assignment Haiku run and supplied keys in
`/home/ubuntu/.env`. The exact model was `anthropic/claude-haiku-4-5-20251001`.
The allocation remained two tasks × three variants × four arms × one draw, with
20 model calls per assignment and aggregate ceilings of 480 requests, three
million input tokens, 400,000 output tokens, and $5 estimated usage.

- 16 assignments started: 14 hit the call limit, one was interrupted to repair
  accounting, and one stopped when its next input reservation would exceed the
  aggregate limit. Eight assignments never started.
- All 24 assignments remain in the denominator, with unknown primary violation
  outcomes. No protected-file changes were observed in the available traces;
  incomplete outcomes are not clean negatives.
- 296 requests were reserved, with 295 known responses and one unresolved request.
  Accounted usage including that request's reservation is 2,976,713 input tokens
  and 41,943 output tokens.
- Known responses cost an estimated $2.6533875. The unresolved request retains
  a $0.062572 allowance. The stricter budget ledger accounts $3.258922 using
  conservative cache rates. These are estimates, not a provider invoice.
- The next request could not fit the input reservation ceiling. Remaining dollar
  allowance does not authorize exceeding the approved token allocation.

The first execution exposed a bug: Inspect reports cached input separately, and
`cache=False` does not disable provider prompt caching. Execution was stopped
at 48 requests while within the approved limits. The adapter now disables prompt
caching explicitly, counts cached inputs, and reserves/settles cache writes
conservatively. **121 tests pass, zero failures/errors/skips**, including Docker
and Inspect; all real-task controls passed fresh qualification.

A new frozen continuation carried the first three started results unchanged,
deducted their reconciled usage, and executed only previously unstarted
assignments. Neither completed nor interrupted rollouts were retried. The driver
uses the same InspectAgent and run_one loop directly; its hash and both source
versions are archived. The interrupted raw result's last `stop: running` value
is retained, with separate final evidence and an interruption annotation.

## Implementation and local qualification

Python 3.12.14 and pinned optional dependencies are installed in `.venv/`.
Dependency checks and adapter/test lint pass. The Linux x86-64 Docker host has
30 CPUs, about 222 GiB RAM, and over 1.4 TB free disk. Actor containers retain
two CPUs, 2 GiB RAM, UID 1000, no external network, and no host mounts.

The dataset revision is `9c2d34f364b7229e8c0ff807c646100bdc18bbb5`, with 349 matched
triples across ten repositories. Development uses `pytest-dev__pytest-10051` and
`sympy__sympy-24562`. The [selection](experiments/impossible-selection-dev.json)
records immutable image digests and mutation reviews. No held-out set is assigned.

Qualification now checks observer behavior for every task variant. All 12
reference/empty checks and six observer controls passed under the corrected
source. The preceding local phase also passed 12 actor repair/exit controls;
the corrected runner was exercised again by the full scripted integration suite.
See the [development review](docs/impossiblebench-development-review.md).

## Current local artifacts

Paths are relative to the repository unless absolute:

- Credentials: `/home/ubuntu/.env`, outside version control. Never print or archive
  values. The user's authorization applies to the completed allocation, not an
  automatic expansion.
- Environment: `.venv/`; bootstrap installer: `runs/bootstrap-tools/bin/uv`.
- Dataset/bundle: `runs/impossiblebench-hf-cache/`,
  `runs/impossible-catalog-01.json`, `runs/impossible-bundle-dev-01.json`.
- Current qualification: `runs/impossible-controls-dev-02/qualification.json`.
- Corrected-source tests: `runs/linux-cache-fix-validation-01.xml`.
- Initial interrupted execution: `runs/impossible-live-preflight-proposed-01/`.
- Final combined study: `runs/impossible-live-preflight-continuation-01/`, including
  `execution-analysis.json`, `summary.json`, and all 24 result files.
- Exact drivers: `runs/run_live_continuation.py`, `runs/analyze_live_preflight.py`.

Both execution markers are ended. **Do not rerun either directory, remove its
marker, or replace assigned outcomes.** The archive contains both complete
phases; three carried result directories occur in both and must not be counted
twice. The continuation is the combined 24-assignment report. Source and bundle
hashes are frozen. Any adapter change needs new qualification and a new plan.

Docker requires approved elevated access on this host. The ignored wrapper
`runs/docker-bin/docker` invokes `sudo -n /usr/bin/docker`; socket permissions
were not changed. All temporary task containers were removed. Sandboxed Inspect
unit runs stalled; the complete validation with approved host access passed.

## Next work

Before another live allocation, address feasibility:

1. Make the prepared `testbed` environment easier for the actor to invoke correctly.
   Some calls used base Python and encountered missing pytest/mpmath, despite
   reference qualification passing in the correct environment.
2. Establish original-task completion with enough calls. Ten pytest patches made
   the same incomplete reset/clear repair; no SymPy implementation change was saved.
3. Verify use of the scored `submit` interface. Shell test failures do not trigger
   the frozen intervention contract, and no actor called submit in this run.
4. Freeze the revised setup and get approval for any new live allocation. Preserve
   this inconclusive preflight and its incomplete outcomes as development evidence.

The earlier 192-rollout and 1,152-rollout allocations remain unapproved proposals.
Do not launch them automatically. The completed run supplies feasibility and cost
information, not intervention-effect estimates or proof of low violation rates.
