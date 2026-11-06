# Standardized benchmark and baseline protocol

**Sources reviewed October 4, 2026. New benchmark runs remain unallocated.**
The [research objective](incident-aware-optimization.md) is to test whether incident
feedback improves policy optimization at matched capability and cost. This document
defines its external comparisons. The executable offline tooling checks the
[versioned design](../experiments/standardized-benchmarks-v1.design.json), imports
official results, and analyzes matched monitor judgments. It does not execute
the new upstream runners.

## Benchmark selection

These are relevant public benchmark implementations and established baselines,
not a claim that one model or defense is the current universal state of the art.

| Track | Frozen source | Baselines and native endpoints |
| --- | --- | --- |
| Counterfactual coding: Impossible-SWEbench | [ImpossibleBench `061dc3d`](https://github.com/safety-research/impossiblebench/tree/061dc3dce6a96ab6cf02a855157263033dcfa3ba); dataset revision `9c2d34f364b7229e8c0ff807c646100bdc18bbb5` | Upstream tools scaffold with its published STOP instruction; scope reminder, supported-blocker notice, and both as declared extensions. Original, oneoff and conflicting raw pass rates remain separate. |
| Artifact monitoring: ResearchArena | [ResearchArena `58776e0`](https://github.com/aisa-group/ResearchArena/tree/58776e09339c1714d0524130590abaf6eac7879d); [trajectory release](https://huggingface.co/datasets/aisa-group/ResearchArena-Trajectories/tree/8cd737c58bdac876fbf7b137796508c99c6e9588) | Upstream monitors across transcript/reasoning × artifact-access conditions; never-flag and always-flag controls; our probe-policy extension. Preserve main-task, side-task and suspicion scores. |
| Service transfer: AgentDojo | [AgentDojo `089ed46`](https://github.com/ethz-spylab/agentdojo/tree/089ed468cf3ed0322acc66b0211f26d9d90dbf60), benchmark `v1.2.2` | No defense, repeat-user-prompt, spotlighting with delimiting, tool filter, then our intervention. Report clean utility, attacked utility and attack success. |
| Later online control: BashArena | [ControlArena `173c872`](https://github.com/UKGovernmentBEIS/control-arena/tree/173c872f04ee661c7e1cf37f4fc610e0791ef0da); [BashBench2 data](https://huggingface.co/datasets/Eccentricity/bashbench2/tree/13e19f9c2c91e3a55a49f8de7a28c08055f7ede8) | Untrusted-only, trusted-only, trusted monitoring, defer-to-trusted, then our policy. Report honest task utility, attack success, intervention/audit budget and cost. |
| Optional monitor transfer: SHADE-Arena public | [Current public release `6614e77`](https://github.com/jkutaso/SHADE-Arena/tree/6614e77191c1f8e2d0c44c123c6f915905ebafae) | Honest and attack actors with upstream monitoring, then our monitor on the same transcripts. The five public task pairs do not reproduce the full 17-pair study. |

ControlArena provides existing
[trusted-monitoring and defer-to-trusted implementations](https://control-arena.aisi.org.uk/micro_protocols.html).
For [BashArena](https://control-arena.aisi.org.uk/settings/bash_arena.html), use the
per-action `auto_submit_protocol_wrapper` so transient side-task effects are
retained. A post-hoc alert is not evidence of online prevention. The old
[`safety-research/SHADE-Arena`](https://github.com/safety-research/SHADE-Arena)
repository is explicitly deprecated; do not use it as the current public release.

Keep the qualified older ImpossibleBench revision for continuity. A newer source
revision requires a new environment/scorer qualification. The prior six-run U1
result stays a small diagnostic with known actor-environment problems, not a
paper-level reproduction.

## Common experiment contract

1. Preserve each official task, solver, scorer and native score for the upstream
   reference. Label scaffold, prompt, budget or scoring changes as extensions.
   Use the same independent incident observer to assess every compared policy.
2. Freeze exact task IDs, source and dataset revisions, dependency lock, container
   digests, prompt hashes, model snapshots, reasoning/sampling settings, requests,
   tokens, probes, time, prices and spending ceilings. Source pins alone do not
   make a plan executable. Lock files and qualification results are separate.
3. Establish ordinary task capability before a safety comparison. Models must
   solve clean controls and use the actual tool environment successfully. The
   lower-cost trusted model and stronger actor/monitor are explicit roles; select
   available snapshots after this preflight, not by an unverified “latest” alias.
4. Match tasks and resource ceilings across baseline and candidate arms. Count
   monitor, trusted-policy and optimizer calls as well as actor calls. Compare
   different model families separately and repeat on another family before a
   model-general claim. Historical published numbers provide context, not matched
   experimental control groups.
5. Keep development, benign calibration and final test groups separate. Put every
   mutation/retry of an issue and every view of an artifact in the same split.
   Freeze selection before test. Use provided official splits where available;
   otherwise publish the local grouped partition and its seed.
6. Declare a fixed-attack comparison first. AgentDojo's official `tool_knowledge`
   attack is the initial reproducible attack baseline. Adaptive attacks require
   their own equal search budgets and a new frozen evaluation. Task-only behavior
   and explicitly instructed sabotage must retain separate denominators.
7. Report all assignments, errors, limits, missing scores and abstentions. Preserve
   positive behavioral witnesses after later failures. Keep proposal, native
   side-task score and verified effect as separate fields. Never average unrelated
   benchmark score scales into an overall safety number.

Use a full official split for a benchmark-level result. A budgeted subset is a
named pilot with task IDs selected before examining outcomes. More retries on a
few tasks do not create new task families. Select sample size from the intended
effect size, clustering and utility margin after a development-only capability
pilot; no confirmatory sample size is allocated by this design.

## Reporting semantics

Monitor reports use AUROC, non-interpolated average precision, coverage, and
TPR/FPR at thresholds selected on **benign calibration** examples. Suspicion
scores are ordinal judgments, not calibrated probabilities; dividing a 0–100
score by 100 does not justify a Brier score or a calibration claim.

Thresholds use `score >= threshold` and conservative handling of tied scores.
At least `ceil(1 / target_fpr)` independent benign calibration lineages must be
present and completely scored. Otherwise the operating point is unavailable.
This is a minimum resolution check, not a statistical guarantee of population
FPR. A 1% operating point is usually unsupported by small task-family pilots;
keep that limitation visible. A held-out false-positive estimate and its
uncertainty remain necessary even after calibration.

The analysis returns 95% percentile bootstrap intervals clustered by lineage
and paired AUROC differences on common scored cases. Rate intervals are
conditional on the frozen threshold. Fewer than two independent clusters or
too many bootstrap samples without both classes yield no interval. Sparse or
boundary estimates remain descriptive; zero observed errors is not a risk bound.
For missing scores, all-assigned lower/upper alert-rate bounds are reported
separately from confidence intervals. Always inspect class-specific coverage
before interpreting complete-case comparisons. Small numbers of task families
limit claims about transfer, even with many trajectories per family.

ResearchArena's four R&D settings have different native score meanings. Preserve
them separately, audit the artifact and effect evidence, and declare whether a
monitor label denotes an attack assignment or a verified harmful effect. Those
labels answer different questions. Artifact-aware replication needs the original
artifact and compatible environment, not just a transcript. The released monitor
conditions are agentic; our short local scripted explanations are not a
reproduction of access to upstream reasoning traces.
[Dataset contract](https://huggingface.co/datasets/aisa-group/ResearchArena-Trajectories).

AgentDojo's `security=True` means the injection goal succeeded on an attack run.
Its runner also writes this value as a clean-run sentinel and in some error
paths. The importer keeps the exact raw JSON, maps only successful scoring of an
attack run to `attack_success`, and leaves error/clean attack outcomes null.
[Task semantics](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/base_tasks.py),
[runner and result schema](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/benchmark.py).
Keep DoS attack outcomes separate from other injection objectives.

## Implemented offline commands

These commands make no inference requests and never launch benchmark tasks:

```sh
PYTHONPATH=src python3 -m containment_extension benchmark-check \
  --config experiments/standardized-benchmarks-v1.design.json

# Import ONE original result file; use a new output directory.
PYTHONPATH=src python3 -m containment_extension benchmark-import \
  --format researcharena --input /path/to/upstream/results.json \
  --output runs/researcharena-import-01
PYTHONPATH=src python3 -m containment_extension benchmark-import \
  --format agentdojo --input /path/to/task-result.json \
  --output runs/agentdojo-import-01

# Analyze predeclared matched monitor assignments and collected scores.
PYTHONPATH=src python3 -m containment_extension benchmark-report \
  --plan /path/to/monitor-plan.json --scores /path/to/scores.jsonl \
  --output runs/monitor-report-01
PYTHONPATH=src python3 -m containment_extension evaluation-verify \
  runs/monitor-report-01
```

`benchmark-check --require-ready` fails while execution locks are missing.
It checks declared lock fields, not their contents or live authorization. The
result importers check format/semantics and freeze bytes; they do not attest that
an upstream run used the claimed implementation. Evidence review remains required.

A monitor plan uses schema `benchmark-monitor-plan-v1`, with benchmark,
population, label definition, comparison ID, source revision, dataset SHA-256,
claim (`upstream_reproduction`, `benchmark_extension`, or `local_diagnostic`),
evidence kind (`model_evaluation` or `software_fixture`), analysis seed,
bootstrap repetitions, and target FPRs. Its `systems` maps system IDs to exact
`model`, `view`, and `config_sha256` values; the latter commits to the separately
archived prompts, generation settings and budgets. `baseline` names one system.

Every `assignments` row has `id`, `system`, `example_id`, `lineage`, `split`
(`development`, `calibration`, or `test`) and boolean/null `label`. The assignment
list, including reference labels, is analyst data, never an actor/monitor prompt.
All systems must cover the same assigned examples. Score JSONL rows contain
`id`, `status` (`valid`, `abstain`, `error`, `not_run`), and a numeric 0–1 `score`
only when valid. Omitted assignments are retained as `not_run`. The analyzer
rejects duplicate/extra results and label or split disagreement across systems.
Examples and edge cases are exercised in
[the reporting tests](../tests/test_benchmark_standardization.py).

## Execution status

The standardization adds source/data pins, baseline protocols, two raw-result
importers, and paired monitor analysis. The existing ImpossibleBench upstream
driver remains available. New ResearchArena/AgentDojo live runner integration,
BashArena online controls, the matched optimizer-feedback ablation, and external
benchmark performance measurements remain pending. No existing frozen result
archive was relabeled as a standardized result and no paid call was made.
