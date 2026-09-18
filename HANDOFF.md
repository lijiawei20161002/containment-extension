# Start here: ImpossibleBench on the next machine

Updated September 18, 2026. This file is the entry point for the next Codex agent.
The user is moving execution to another machine and has requested continued
implementation and testing. Read this file before starting a live experiment.

## Objective and current state

Test whether full-scope reminders (R), explicit acceptance of a supported blocker
(E), and their combination (RE) generalize the existing containment findings to
Impossible-SWEbench, compared with neutral wording (N). Preserve matched original
tasks as capability controls. This is a transfer study with a custom policy and
solver, not an exact replication of the ImpossibleBench paper.

Completed:

- Optional Inspect adapter, offline Docker actor containers, independent file
  observer, terminal evidence capture, inference budgets, frozen assignments,
  assigned-run reporting, and separate evidence-bound review labels.
- `impossible-preflight` for host and cached-image checks, and
  `impossible-catalog` for inventorying matched triples at an immutable revision.
- **112 tests passed, zero failures/errors/skips**, including the real Docker +
  Inspect scripted integration test, on the previous ARM64 Mac. Lint checks for
  the adapter and new tests passed. Linux execution has not yet been validated.
- Downloaded and inventoried **349 matched base issues across 10 repositories**.
  There were no structural exclusions at the pinned dataset revision below.

Not completed: mutation review of selected real issues, task image acquisition
and qualification, live model evaluation, semantic outcome review, or a measured
cost estimate for the development pilot. **No paid ImpossibleBench inference has
run.** Synthetic fixture results are infrastructure checks, not model findings.

The preceding implementation commit is `5788842`. This handoff accompanies the
subsequent resource/catalog changes; record `git rev-parse HEAD` on the new machine
as the checkout used for validation.

## Resources and decisions

Use a Linux x86-64 host with Docker, eight CPU cores, at least 16 GiB available to
Docker, and 120 GB free disk. No local GPU is required for API inference. The
resource preflight uses these conservative planning targets; individual issues
may require less. The previous Mac had only 8 GiB physical RAM, 3.8 GiB Docker RAM,
and about 11 GiB free disk, so it was used only for fixture tests and cataloging.

The user approved implementation, testing, and pushing this work. **An API spending
ceiling and exact live model IDs have not been agreed.** The suggested $25 initial
cap was a proposal, not authorization or an estimate for the full pilot. Finish
local qualification and prepare a concrete live configuration before obtaining
the missing spending/model decision. Do not launch the proposed 192- or
1,152-rollout allocations automatically.

OpenAI and Anthropic keys were configured on the previous machine. They are not
in Git and are not assumed available on this machine. Use environment variables
or an explicit local env file; never put credentials in commits or run artifacts.
Provider account credit, current model availability, and prices remain unchecked.

## 1. Set up and validate this machine

From the new machine, clone the repository if needed:

```sh
git clone https://github.com/lijiawei20161002/containment-extension.git
cd containment-extension
git rev-parse HEAD
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[impossiblebench,dev]'
.venv/bin/python -m pip check

.venv/bin/python -m containment_extension impossible-preflight \
  --profile swebench --output runs/host-preflight-01.json

docker pull python@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea

CONTAINMENT_DOCKER_TESTS=1 .venv/bin/python -m pytest -q \
  --basetemp runs/linux-validation-01 \
  --junitxml runs/linux-validation-01.xml
```

Python 3.12 is the tested interpreter. The optional extra pins direct dependencies;
[`requirements/impossiblebench-tested.txt`](requirements/impossiblebench-tested.txt)
records the previous Mac's transitive versions for reference. Confirm dependency
compatibility on Linux. The fixture image digest is a multi-architecture index;
its registry metadata includes both Linux amd64 and arm64 images.

`impossible-preflight` is read-only apart from its report. A failed check exits 1;
inspect the report and address the cause. It does not pull images or make model
calls. Run it on the execution host, since client disk space cannot establish a
remote Docker daemon's available storage.

## 2. Rebuild the pinned catalog and select real tasks

```sh
HF_HOME=runs/impossiblebench-hf-cache \
  .venv/bin/python -m containment_extension impossible-catalog \
  --revision 9c2d34f364b7229e8c0ff807c646100bdc18bbb5 \
  --cache-dir runs/impossiblebench-hf-cache/datasets \
  --output runs/impossible-catalog-01.json
```

Dataset: `fjzzq2002/impossible_swebench`, commit
`9c2d34f364b7229e8c0ff807c646100bdc18bbb5`.
Reviewed upstream implementation commit:
`061dc3dce6a96ab6cf02a855157263033dcfa3ba` in
[`safety-research/impossiblebench`](https://github.com/safety-research/impossiblebench).

Choose one or two explicit development issues for initial qualification, preferably
covering different repositories. No issue IDs have been selected yet. Read the
issue, original tests, each modified test, and the reference patch. Record the
specific conflict for both impossible variants; failed execution alone does not
prove impossibility. Log exclusions and their reasons. Keep all variants of a
base issue together, and reserve separate issues/repositories for later evaluation.

Create a selection JSON using the schema in
[`docs/impossiblebench-method.md`](docs/impossiblebench-method.md#prepare-actual-swe-bench-tasks).
Acquire or build the corresponding task images and pin each by digest. This is
still necessary work: the backend requires images to be cached and does not build
them. Images need the checked-out repository, Git, Bash, the `testbed` conda
environment, and preinstalled dependencies. Check upstream image acquisition
code at the pinned revision if needed. Mutable tags may be used to locate an
image, but the selection and all rollouts must use its immutable digest.

## 3. Export and qualify real task triples without model calls

After creating the reviewed selection and acquiring its images:

```sh
.venv/bin/python -m containment_extension impossible-export \
  --selection experiments/impossible-selection-dev.json \
  --output runs/impossible-bundle-dev-01.json

.venv/bin/python -m containment_extension impossible-preflight \
  --bundle runs/impossible-bundle-dev-01.json \
  --output runs/impossible-images-dev-01.json

.venv/bin/python -m containment_extension impossible-qualify \
  --bundle runs/impossible-bundle-dev-01.json \
  --output runs/impossible-controls-dev-01
```

Every original/reference run must pass. Empty patches and both impossible
variants with reference patches must fail as expected, with complete observation.
Inspect failures to distinguish broken environments from valid task failures.
Confirm transient test edits, observer protection, legitimate repair, and honored
termination on the selected environments before inference.

Important implementation limits to inspect during this phase:

- Containers currently receive **two CPUs and 2 GiB RAM each**. This is separate
  from host capacity. Any increase or timeout change requires implementation tests
  and fresh qualification; do not silently change a frozen experiment.
- The qualification command runs reference/empty checks for every record, but its
  explicit edit-and-revert and observer-write-denial controls currently use only
  the first record. Extend or separately execute those controls for each distinct
  task image before claiming all environments are qualified.
- Original-task passing still needs semantic review. The observer records protected
  file effects; it is not a complete classifier for every semantic shortcut.
- Qualification binds the bundle and adapter source hashes. A source change
  invalidates earlier qualification; requalify before preparing a new study.

## 4. Freeze a small live preflight, then decide whether to expand

Use [`experiments/impossiblebench-smoke.json`](experiments/impossiblebench-smoke.json)
as the configuration schema, replacing its synthetic task, mock model, illustrative
rates, and fixture-sized limits. Freeze explicit task IDs, exact provider/model
IDs, current price estimates, and agreed aggregate request/token/cost ceilings.
One task × three variants × four arms × one model × one draw is twelve rollouts.
Choose the first matrix after qualification and the budget decision.

```sh
.venv/bin/python -m containment_extension impossible-prepare \
  --bundle runs/impossible-bundle-dev-01.json \
  --config experiments/impossible-live-preflight.json \
  --output runs/impossible-live-preflight-01

# Paid inference: execute only once the concrete configuration and budget are agreed.
# Replace /secure/path/model.env with this machine's explicit local env-file path,
# or omit --env-file when provider keys are already exported.
.venv/bin/python -m containment_extension --env-file /secure/path/model.env \
  impossible-run runs/impossible-live-preflight-01 \
  --qualification runs/impossible-controls-dev-01/qualification.json

.venv/bin/python -m containment_extension impossible-report \
  runs/impossible-live-preflight-01
```

The proposed development allocation is eight issues × three variants × four arms
× two models × one draw = 192 rollouts. The later 1,152-rollout allocation is a
candidate, not a commitment. First measure real token costs, original-task
capability, runtime, and baseline violation rates. Preserve all assigned outcomes,
including missing/error runs; do not convert unknown outcomes into clean negatives.

## Evidence and completion criteria

Generated `runs/`, virtual environments, downloaded data, Docker images, and
credentials from the previous machine are **not in Git**. Recreate them using the
commands above. Use new output names for reruns: evidence must not be overwritten.
The runner permits one launch per frozen plan. Interrupted runs stay assigned;
do not retry them by deleting execution markers.

Before handing back: report Linux test results, chosen issue/image/dataset pins,
mutation reviews and exclusions, qualification results, any unresolved blockers,
and the proposed live configuration. If inference is authorized and completed,
also report actual usage/cost estimates, missing outcomes, and reviewed findings.
Archive selected experiment evidence deliberately; keep credentials and caches out
of Git. Do not describe fixture checks as new containment or model-behavior results.

Further reading:

- [Execution commands and evidence semantics](docs/impossiblebench-method.md)
- [Experimental design, intervention contract, and analysis](docs/impossiblebench-scaling.md)
- [Measured resource assessment and repository counts](docs/impossiblebench-readiness.md)
- [Existing incident-study findings](docs/incident-study-results.md)
