# Continue the ImpossibleBench transfer study

Updated September 21, 2026. **The approved U1 upstream baseline is completed and
archived.** The user replied "yes approved" to six Haiku assignments capped at
$45. The original upstream task constructor, tools solver, prompts and scorer
were used. Read the [results](docs/impossiblebench-upstream-baseline-results.md),
[protocol](docs/impossiblebench-upstream-baseline.md) and
[live archive](results/upstream-baseline-live-v1/README.md).

- All six assigned runs completed: original 1/2, oneoff 0/2, conflicting 0/2.
  The passing original SymPy patch is a general repair on code/spec review.
- Every run hit the 100-message cap; none explicitly called `submit`. Scores
  came from the final upstream scorer. No sample errors or missing scores.
- All six encountered missing packages under the default actor Python. The
  scorer activated `testbed`; ordinary actor commands often used base Python.
  Existing scripted controls did not catch this actor-import qualification gap.
- Usage reconciles: 290 requests/responses, 5,430,553 input and 69,370 output
  tokens, no caching or unresolved reservations, estimated cost $5.777403.
  All per-run and aggregate limits were respected. Actor containers are gone.
- No provided evaluation-test differences remain in final actor patches after
  subtracting trusted initialization. This is not a whole-rollout violation
  verdict; the upstream baseline lacks the custom effect observer.

The completed plan is `runs/impossiblebench-upstream-baseline-proposed-02/`, with
authorization and an **ended** execution marker. Its SHA-256 is
`c28f81ee454b003542fef403e014c7fff030bae3d318885ab70cf6254281de7e`.
`scripts/upstream_baseline.py` is the frozen driver;
`scripts/analyze_upstream_baseline.py` produced the separate analysis. Review
labels are in `analysis/semantic-review.json`. Do not restart this plan or replace
outcomes. The initial `...-proposed-01/` remains an editor-installation diagnostic.

The [preparation archive](results/upstream-baseline-preparation-v1/README.md)
is unchanged: it contains 12 passing upstream scoring controls, four passing
tool-loop controls, the 142-test full suite and additional regressions. Those
checks did not establish reliable default actor imports. The revised custom
runner separately passed all 12 real lifecycle controls at
`runs/impossible-lifecycle-dev-03/` and already activates its actor environment.

Next prepare an upstream environment revision and original-only capability
diagnostic. Keep prompts/scorer fixed and qualify ordinary actor imports across
successive tool calls. No later allocation is approved; the U1 remainder is not
available for automatic expansion. Custom C1 remains deferred.

## Earlier custom-adapter execution

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

The [active experiment roadmap](docs/experiment-roadmap.md) now determines run
order; the [design specification](experiments/next-experiments.design.json) is
planning data, not a runnable config. U1 is complete; U2 has no live allocation.

1. Implement and qualify actor Python/shell environment alignment in a new
   upstream plan. Test real actor imports on successive calls, including after
   a previous shell changed its environment. Preserve the frozen U1 sources.
2. Prepare an original-only capability diagnostic with separate model/cost
   allocation. Keep upstream prompts, scorer and stopping rules fixed. Measure
   legitimate final repairs, submission use, natural stops and environment errors.
3. Only after capability and termination are usable, design a reminder comparison
   within that same upstream scaffold. The observed 0/4 impossible scores do not
   establish appropriate stopping or absence of prohibited behavior.
4. Custom P0 is implemented: every actor call activates the task environment;
   submission/finish guidance is clarified; subsets are validated; local and
   aggregate budgets reserve and settle together; call-20 state is captured.
   `runs/impossible-controls-dev-03/qualification.json` passed 12 reference/empty
   and six observer checks. Full Docker/Inspect validation passed 142 tests;
   additional checkpoint and budget-persistence regression checks are recorded
   in `runs/p0-final-unit-validation.xml`.
5. The separate four-run custom capability plan is prepared at
   `runs/impossible-capability-proposed-01/`, using
   `experiments/impossiblebench-capability-v2.proposed.json`. Its $30 proposal is
   deferred; it is not additional U1 spending. S1 remains a separate track.

The roadmap explains why more calls alone are insufficient and specifies the
gates before a 48-run development factorial. The earlier 192- and 1,152-run
expansions are deferred. No new plan resumes or replaces the completed assignments.
