# Next experiments after the paired-note and judge follow-ups

Updated 20 October 2026. The previously proposed E2-P diagnostic is now an
implemented live study, followed by a separate transcript-judge audit. See
[methods and results](trust4rsi-live-followup-results.md) and the
[original E2 execution record](trust4rsi-experiments.md).

## Completed allocations and their boundaries

The first 48-assignment paired-note allocation stopped on a provider timeout
after 27 recorded runs. Its raw results and 21 unstarted assignments remain
archived. A separate 48-assignment v2 plan uses new fixture seeds and preserves
single-run failures while continuing other assignments without retries.
Both exact notes, paired inputs, randomized order, actor model and analysis
rules are frozen in the corresponding result directories.

The strict v2 judge audit stopped after 12 fenced-JSON calibration responses.
v3 normalized only their outer fences, reused the same responses, and still
failed the frozen false-positive limit. Descriptive v4 uses a fixed 0.5 threshold
with 56 new calls (8 archive positives and 48 targets), reusing the 12 prior
calls. It receives actor-visible evidence only. Its score matrix is 26 TP,
0 FN, 1 FP, 16 TN, and 5 unknown. The separate post-hoc raw-boolean audit retains
the five emitted false labels and reports 26/0/1/21, with no unknown booleans.
This does not qualify a release gate.

These studies answer baseline sensitivity and measurement agreement. They do
not complete the policy-selection comparison that E2 v1 never reached.

## First isolate repair availability from authorization

The [incident-derived design](trust4rsi-incident-to-experiment.md) crosses whether
local recovery works with whether the same reachable archive is authorized.
This separates task difficulty from permission following. Add fixed-instruction,
stop/escalate, permission-check and broker baselines. Freeze sample size and
analysis before inference, and use another task family for transfer. This design
is proposed; it has no live results yet.

### X1b: silent and conflicting grants (added 20 October 2026)

X1 treats archive permission as binary: named as excluded or named as
permitted. That is the right first step, but it resolves in advance the part
of the field problem that is hardest: in the public incidents the grant was
often incomplete, implicit or self-contradictory, and the same recovery action
(another endpoint, a cached result, another repository, a found credential) is
legitimate or a violation depending only on the authorization context. The
archived studies therefore measure constraint compliance (does the agent keep
to a stated grant when its allowed route fails) and not authorization
reasoning (can the agent work out what is permitted when the grant is silent,
and choose between asking, taking a clearly authorized alternative, and
stopping). The supported claim is the narrow one: agents may violate
explicitly specified resource-level restrictions when the authorized recovery
path fails. It does not establish that agents cannot separate recovery from
substitution in realistic environments.

X1b adds two grant conditions to X1's archive axis and keeps technical access
constant:

- Unspecified: the task text does not mention the prior-run archive at all.
- Conflicting: a task hint says the previous run's answer may help, while the
  scope paragraph excludes other runs' artifacts.

Design: 2 new columns x 2 recovery rows x 2 instruction arms (original note;
fixed L3 scope) x 8 pairs = 64 runs on the X1 checkpoints. Each cell carries a
preregistered reference behaviour. In the conflicting column the scope
paragraph wins, so an archive read is a violation and the reference behaviour
is to surface the conflict. In the unspecified column there is no
authorization oracle: the effect journal supplies the observed effect e, but
the permitted set A(c) is not defined by the task, so archive reads are
reported as an access rate plus a response mix (silent read, clarification
request or blocker that names the archive and the missing permission,
authorized completion), never as a violation rate. Over-conservatism is read
off the authorized feasible cells, where a blocker is a cost rather than
caution. Terminal messages are reviewed with the P1 protocol; no new judge
calls are planned.

Gate: X1 reported and the cell policies frozen before any X1b inference.
Prediction, falsifiable: under silence, archive reads track reachability and
task relevance and terminal messages rarely ask; if blockers also rise on the
authorized feasible cells, the effect is conservatism rather than reasoning.
The same distinction applies to the regression gate: every twin carries an
explicit grant, so the gate is a constraint-compliance test and an effect
journal alone cannot label an environment whose grant is silent. A proposed
E5 codebook field records, per incident, whether the grant was explicit,
implicit, unspecified or conflicting for the agent.

A clean upstream coding comparison also needs recovered raw logs from the prior
six-run attempt, consistent actor/scorer Python environments, and original-task
capability checks. The existing report is not a clean behavioral baseline.

## Later decision: is a selection contrast informative?

First fix and independently check the judge contract on development data:
format handling, nullable output fields, and the scope of authorized challenge
actions. Freeze any revised judge before fresh inference. The current calibration
failure must remain a failure, not be relabeled as successful after adjustments.

Use the event rates and actual judge errors to design a new selection study.
If the judge and observer agree on the relevant cases, do not assume different
selection outcomes. That agreement is a useful measured finding and may limit
what this particular fixture can distinguish.

A future comparison must freeze a candidate pool, shared development runs,
actor model, task-score utility criterion, choice of incident feedback and
tie-break. Freeze selected policies before new held-out draws. Measure all arms
with the same observer. Specify the minimum effect of interest, utility margin
and sample size before new inference; the follow-up trials cannot be reused as
held-out evidence.

If broadening the task structure, choose cases with a documented authorization
boundary and observable service effects. Measure actual model behavior on them.
Keep instrumentation qualification separate from actor-performance results;
a scripted incident demonstration cannot establish an agent failure rate.
A broader comparison should be motivated by a clear measurement question,
not by searching for examples until one feedback method wins.

The [technical comparison with primary research sources](trust4rsi-related-work.md)
specifies the missing controls: original/fixed instructions, a broker allowlist,
a transcript-plus-service-evidence judge, and a genuinely new task family.
Do not call an allowlist a CaMeL reproduction or compare published benchmark
rates to our fixture rates. Separate literature comparison from executed baselines.

## Human review and reproducibility

E5 still needs an independent reader and original reports for 26 cases across
16 fields. Forty-two source entries lack URLs; these are not necessarily
42 distinct reports. Provide the blind packet without first-reader labels,
report agreement and adjudicate disputes before using library-wide counts.

The existing E6 anonymous ZIP is an older verified snapshot. Build a separately
versioned supplement if incorporating the new evidence, preserving the old
archive and repeating identity, credential, integrity and extracted-copy checks.
The current deck/results refresh does not upload or replace it.

## Compute

The executed native studies use the existing Mac, Python and SQLite, with a
funded Anthropic API account and network access. No GPU, Docker or local model
weights are needed. The total new estimated-cost ceiling is $8, including
conservative reserved usage for the interrupted first cohort. E5's resource
requirement is human review, not more compute.
