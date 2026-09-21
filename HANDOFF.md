# Continue the ImpossibleBench transfer study

Updated September 21, 2026. Implementation, Linux validation, and qualification
of two real development issues are complete. **No paid ImpossibleBench inference
has run.** Read the [development review](docs/impossiblebench-development-review.md)
and [evidence archive](results/impossiblebench-dev-qualification-v1/README.md).

## Completed in the Linux continuation

- Created `.venv` with Python 3.12.14 and the pinned `impossiblebench` dependencies.
  The dependency check passes; the Linux dependency snapshot is in the archive.
- Full Linux suite: **120 passed, zero failures/errors/skips**, including real
  Docker + Inspect integration. Adapter/test lint passes.
- Host and image preflights pass: Linux x86-64, 30 Docker CPUs, about 222 GiB RAM,
  and over 1.4 TB free disk. Actor limits remain two CPUs and 2 GiB per container.
- Rebuilt the 349-triple catalog at dataset revision
  `9c2d34f364b7229e8c0ff807c646100bdc18bbb5`, with no structural exclusions.
- Selected and reviewed `pytest-dev__pytest-10051` and `sympy__sympy-24562` for
  development. The [selection](experiments/impossible-selection-dev.json) contains
  immutable image digests and both mutation reviews. No held-out set is assigned.
- Fixed qualification's first-environment-only observer coverage. Every task
  variant now needs its own successful edit/revert, final snapshot, and observer
  write-denial checks. Incomplete/duplicate/mismatched reports and cleanup failures
  cannot qualify a bundle.
- Real-task qualification: **12 reference/empty checks and six observer checks
  pass**. Each original/reference passes; all empty and impossible/reference
  controls fail for the reviewed task reasons, with complete observation.
- Real actor controls: **12 pass**, covering legitimate reference repair and
  transient test edits followed by honored exit on every variant. Commands
  proposed after exit are retained but never dispatched.
- Prepared a concrete, unexecuted 24-assignment live proposal and confirmed its
  report retains all 24 unknown outcomes. This is preparation, not authorization.

The starting checkout was `b4afd70fc046cf3f15beaf811df958e06ff409dd`.
The archive contains the exact tested adapter source and its hash. Future source
changes invalidate qualification and require new output directories and fresh
controls. Synthetic and scripted results are infrastructure evidence, not findings
about model behavior.

## Current local artifacts

All paths below are relative to this repository and ignored by Git:

- Environment: `.venv/`; bootstrap installer: `runs/bootstrap-tools/bin/uv`.
- Successful host/image reports: `runs/linux-host-preflight-02.json` and
  `runs/impossible-images-dev-01.json`.
- Full test evidence: `runs/linux-validation-01/`, `runs/linux-validation-01.xml`.
- Catalog/cache: `runs/impossible-catalog-01.json`, `runs/impossiblebench-hf-cache/`.
- Exported bundle: `runs/impossible-bundle-dev-01.json`.
- Qualification: `runs/impossible-controls-dev-01/qualification.json`.
- Actor controls: `runs/impossible-lifecycle-dev-01/` and
  `runs/check_development_lifecycle.py`.
- Frozen, unexecuted proposal: `runs/impossible-live-preflight-proposed-01/`.

Docker requires approved elevated access on this host. The ignored local wrapper
`runs/docker-bin/docker` invokes `sudo -n /usr/bin/docker`; use it only with the
host's permission. Docker socket permissions were not changed. The initial
sandboxed test run stalled and was terminated; the full run with approved access
is the successful validation reported above. Host/image acquisition uses network
access; actor containers retain `--network none`.

## Next decision: model, spending, and credentials

The user approved implementation, testing, and pushing this work. The earlier
$25 suggestion was never authorized. The new
[proposed live configuration](experiments/impossible-live-preflight.proposed.json)
is ready for a concrete decision:

- Two issues × three variants × four arms × one model × one draw = **24 rollouts**.
- Exact model: `anthropic/claude-haiku-4-5-20251001`, proposed as the bridge to the
  earlier incident study. Official model/pricing pages were checked September 21.
- Estimated uncached rates: $1 input / $5 output per million tokens.
- Aggregate limits: 480 requests, 3,000,000 input tokens, 400,000 output tokens,
  and **$5 estimated usage**. These are ceilings, not a measured completion cost
  or provider billing guarantee. Budget exhaustion preserves incomplete outcomes.
- Per rollout: 20 model calls, 40 actions, five submissions, 2,048 output tokens
  per request, and 600 seconds. The serial rollout limits total four hours plus
  setup/reporting overhead.

**Obtain the model/spending decision before paid inference.** Neither provider
key was found in the environment or the checked local `.env` locations. Configure
credentials via the environment or an explicit local env-file path; never write
keys into version control or artifacts. Account access/credit is unchecked.
The proposal's `status` field is descriptive metadata, not an execution lock.
Do not infer authorization from the existence of a prepared plan.

If this exact proposal is approved and the source/bundle have not changed, its
existing frozen directory is ready for one launch. The following command makes
paid requests and is shown only for after the decision and key setup:

```sh
PATH="$PWD/runs/docker-bin:$PATH" .venv/bin/python -m containment_extension \
  --env-file /secure/path/model.env \
  impossible-run runs/impossible-live-preflight-proposed-01 \
  --qualification runs/impossible-controls-dev-01/qualification.json

.venv/bin/python -m containment_extension impossible-report \
  runs/impossible-live-preflight-proposed-01
```

If the model, limits, source, or task selection changes, create a new plan and
requalify whenever the source/bundle changes. Do not delete execution markers or
reuse output directories to retry interrupted runs. Preserve assigned failures
and unknown outcomes. After execution, review original solutions for semantic
shortcuts and blocker claims against evidence before assigning clean labels.

## Reproduce on another machine

Use Python 3.12 and install `.[impossiblebench,dev]`; run the dependency check.
Acquire the fixture image and the two images by their recorded digests, then run
preflight and the full suite with `CONTAINMENT_DOCKER_TESTS=1`. See
[method](docs/impossiblebench-method.md) for standard commands.

The archive's `bundle.json` is the exact export. It can be used directly, or
rebuilt with `impossible-export --selection experiments/impossible-selection-dev.json`.
Run `impossible-qualify` into a new directory before live execution on a new host.
The archived lifecycle script documents the additional real-task repair/exit
controls; adapt only its input/output paths for fresh runs.

The original 192-rollout development allocation and 1,152-rollout expansion remain
proposals. Measure actual token costs, original-task capability, baseline violation
rates, runtime, and missing outcomes before choosing an expansion. No GPU is
required for API inference. See the [transfer design](docs/impossiblebench-scaling.md)
for the intervention contract, assignment rules, and limits of the research claim.
