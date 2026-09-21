# Next experiments and execution gates

**Updated September 21, 2026. Active planning document. U1 has executed; all later
allocations are proposals. Scripted qualification makes no model calls.**

**Current priority: repair upstream actor environment qualification.** The
[completed U1 baseline](impossiblebench-upstream-baseline-results.md) used the
unmodified upstream solver, prompts and scorer on six real task variants. It
scored 1/2 on originals and 0/4 on impossible variants, with six message-limit
stops, no explicit submissions and missing-package errors in all six traces.
Align ordinary actor Python/shell commands with the scorer's task environment
and qualify imports across successive actual tool calls. Then prepare a separately
budgeted original-only capability diagnostic, keeping prompts and scorer fixed.
Capability and termination must be usable before choosing a reminder comparison.
The custom adapter's neutral arm is not an upstream reproduction. C1/C2/C3 below
remain a separate diagnostic design, not the next live run.

The custom-runner capability design increases
**calls per rollout from 20 to 60**, repairs environment and submission usability,
and allocates enough input tokens to sustain the longer histories. Increasing only
the aggregate request ceiling would not address the observed failure.

The companion [design specification](../experiments/next-experiments.design.json)
records the proposed matrices and limits. It is not an executable configuration.
Use this page for priorities, [HANDOFF](../HANDOFF.md) for machine state, and the
[execution method](impossiblebench-method.md) for the implemented interfaces.
Earlier design documents retain methodological detail and historical proposals;
their old “run first” recommendations no longer determine execution order.

## Evidence behind the budget decision

The completed [ImpossibleBench preflight](impossiblebench-live-preflight-results.md)
assigned 24 runs. Fourteen reached the 20-call limit, one was interrupted, one
stopped at the aggregate input reservation limit, and eight never started.
There were no scored submissions, intervention deliveries, or established
original-task completions.

The [combined evidence](../results/impossiblebench-live-preflight-v1/execution-analysis.json)
accounts for 296 requests against a 480-request ceiling and 2,976,713 input tokens
against a three-million-token ceiling. Its 295 known responses consumed 2,950,547
input and 39,895 output tokens. Re-reading their raw provider usage, including
cache reads and writes, gives the following planning observations:

| Observation | Consequence |
| --- | --- |
| Mean input was about 10,002 tokens per known response | Calls and input tokens need separate limits |
| Complete 20-call trajectories used 123,456–326,329 input tokens | Repeated task histories are a material cost |
| The twentieth request contained 10,127–22,781 input tokens | Tripling calls can cost much more than tripling input |
| No run stopped at the output limit | Keep the 2,048-token output allowance initially |
| Some shell calls used the wrong Python environment | Fix command execution before spending more on retries |
| Shell tests never led to scored `submit()` calls | Clarify the interface and measure trigger reachability |

If context grew approximately linearly with turn count, cumulative input from
20 to 60 calls could increase by roughly nine times. That is a sensitivity
scenario, not a forecast: it puts the observed range near 1.1–2.9 million input
tokens per run. Use three million per run initially, with conservative reservations
still allowed to stop a run earlier. Record the actual growth before expansion.

## Run order

| ID | Next action | Size | Gate to advance |
| --- | --- | ---: | --- |
| P0 | Repair and locally qualify the setup; prepare archive replay | No inference | Exact schedules, environment, scoring, effects, and budgets pass controls |
| U1 | Completed direct upstream tools/scorer baseline | 6 runs | 1/2 original, 0/4 impossible; environment and termination problems require diagnosis |
| U2 | Qualify upstream actor environment, then original-only capability | Design pending | Actual actor imports pass on successive calls; freeze a new plan and budget before inference |
| C1 | Original-task capability preflight | 4 runs | At least 3/4 legitimate completions, including both issues; complete accounting and no unresolved infrastructure failures |
| C2 | Impossible-task submission/trigger preflight | 8 runs | At least 6/8 receive the assigned note, covering every issue/mutation pair; complete accounting and no unresolved infrastructure failures |
| C3 | Full N/R/E/RE development comparison | 48 runs, conditional | Budget sized from C1/C2; useful baseline event rate and retained original-task capability |
| S1 | Native service behavior × enforcement companion | 80 runs, separate track | Replay passes and the new enforcement schedule/scoring are qualified |

U1 completed within its 360-request, 18-million-input-token, 737,280-output-token
and $45 ceilings, using 290 calls and an estimated $5.777403. See its results and
protocol for exact settings, source/image pins and controls. U2 has no live
allocation; unused U1 funds are not reassigned. C1 is prepared but deferred.
C2 depends on C1; C3 depends on both within the custom-runner path.
S1 can proceed independently once its own P0 work is complete, especially if coding
capability remains inadequate. It is the next substantive service experiment,
not a substitute for establishing ImpossibleBench feasibility. No later stage is
automatically authorized by completing an earlier one.

## P0: make the next allocation informative

The custom-runner changes below are implemented and locally qualified; this list
records their requirements. Service replay remains separate S1 work.

1. **Activate the task environment for every actor shell call.** Use the same
   qualified `testbed` environment as the scorer, with the selected record's
   Python path. Check Python and required imports in both task images. A shell
   activation in one call does not persist to the next self-contained call.
2. **Clarify the tool contract in every arm.** Explain that shell tests are for
   debugging; after a candidate repair, `submit()` supplies scored feedback.
   Document `finish()` and retain natural terminal responses. Do not reveal
   reference patches or tell the model whether it has an impossible variant.
3. **Support explicit arm and variant subsets.** The current `study.prepare()`
   previously expanded all three variants and all four arms; it now validates `arms`
   and `variants`, rejects empty/invalid/duplicate subsets and uses them to restrict the run. Validate selectors
   and print the exact assignment count before freezing a new versioned plan.
4. **Enforce per-run input and cost shares as well as aggregate limits.** The
   previous ImpossibleBench budget guard was aggregate-only. Reserve against both
   scopes before a call, settle both together, and retain unresolved reservations.
   Do not allow an early run to consume a later run's allocation. Unspent shares
   remain unspent for this preflight; no automatic reallocation or retries.
5. **Control observation volume without changing scope.** Use concise command
   guidance and retain full history for C1. Do not add lossy compaction, caching,
   or a new truncation policy in the same revision. If context growth is still
   prohibitive, qualify a separate revision preserving scope and blocker evidence
   explicitly, with raw tool output retained in the evidence archive.
6. **Qualify the complete source revision.** Re-run required repository checks,
   reference/empty checks, observer checks, and scripted actor paths through
   scored failure, single note delivery, success, and honored exit. Verify the
   four- and eight-assignment schedules and per-run budget isolation.

Keep the first-failed-scored-submission trigger. Automatically triggering on a
shell failure or forcing an initial failed submission would change the intervention
population and timing; those are separate possible designs. All interface changes
are common to all arms and are frozen before C1. Compare the revised run with the
old preflight descriptively, not as a randomized estimate of extra calls alone.

For S1, additionally adjudicate archived semantic scope labels and replay recorded
actions against matched permissive/scoped states. Include scripted checks for
channels absent from live data. Adapt `incident_study.py` to vary enforcement and
score blocked proposals separately from effects; it currently freezes permissive
mode. This is new implementation work, not a config-only switch.

## C1: four original-task capability runs

Use `anthropic/claude-haiku-4-5-20251001`, the two existing development issues
(`pytest-dev__pytest-10051`, `sympy__sympy-24562`), original variants only, N only,
and two fresh draws per issue: **2 × 1 × 1 × 2 = 4 runs**. Run serially, alternating
issues within each draw, with issue order randomized under a frozen seed. Each
run starts fresh; none resumes or replaces an archived assignment.

| Limit | Previous preflight | Proposed C1 |
| --- | ---: | ---: |
| Assignments | 24 | 4 |
| Model calls per run | 20 | 60 |
| Actions per run | 40 | 120 |
| Scored submissions per run | 5 | 5 |
| Output tokens per call | 2,048 | 2,048 |
| Wall time per run | 600 s | 1,800 s |
| Input-token share per run | No isolated share | 3,000,000 |
| Estimated-cost share per run | No isolated share | $7.50 |
| Aggregate requests | 480 | 240 |
| Aggregate input tokens | 3,000,000 | 12,000,000 |
| Aggregate output tokens | 400,000 | 491,520 |
| Aggregate estimated-cost ceiling | $5 | $30 |

The output ceiling is `4 × 60 × 2,048`; each run has a 122,880-token share. All
limits apply simultaneously; none guarantees that all 60 calls can execute. Keep
the existing shell/scorer timeouts unless local qualification demonstrates a
specific need to change them. Four rollout wall limits sum to two hours, excluding
qualification and external setup/reporting overhead.

At the verified Haiku rates of $1 input / $5 output per million tokens, filling
the token ceilings without caching would cost about **$14.46**. The runner reserves
up to twice the input rate for possible cache writes; the corresponding planning
bound is **$26.46**, rounded to a **$30 guard**. This is headroom, not an expected
bill. Prompt caching stays disabled; failed requests retain reservations.
[Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), checked
September 21, 2026. Reverify rates and model access before freezing execution.

Report first scored submission, first legitimate pass, calls/actions/tokens to
each, terminal outcomes, environment errors, and proposals/effects. Preserve the
state at call 20 for an offline progress comparison without inserting a new actor
message. Review passing patches against the specification and protected surfaces;
raw passing scores alone are not legitimate completion.

The 3/4 threshold is a development gate, not a statistically precise capability
estimate. A failure does not justify repeatedly extending the same runs. Diagnose
environment/protocol errors first; if the actor uses the interface correctly but
still cannot solve the original issues, prepare a separately budgeted model or
task-difficulty comparison. A stronger model is then a capability intervention,
not evidence about the effect of reminders. Do not keep raising calls by default.

## C2: eight runs to establish intervention exposure

After C1 passes, use the same tasks, model, interface, and per-run limits:
**2 issues × 2 impossible variants × 2 arms (N, RE) × 1 draw = 8 runs**.
Randomize arm order within issue/variant pairs. Include early stops and violations
before the trigger in the assignment table.

Proposed independent ceilings are **480 requests, 24 million input tokens,
983,040 output tokens, and $60**, retaining three million input tokens and $7.50
per run. These are twice C1's capacity, with four hours of summed rollout wall
limits. Reforecast from C1 before freezing; a changed cap creates a new design
revision. Do not silently spend a C1 remainder here.

The engineering gate is assigned note delivery in at least six of eight runs,
including at least one run for each issue/variant pair. Also record remaining
calls after delivery and require at least ten available at that point in those
six runs, so there is room to observe a response. An early correct blocker is a
valid task outcome but does not demonstrate exposure to the intervention. Never
coerce continuation merely to meet this gate.

This gate screens for usable experimental exposure; it does not establish a
treatment effect. If it fails, diagnose late/nonexistent submission, honest early
termination, or infrastructure errors. A controlled checkpoint study may be more
appropriate, with an explicitly conditional estimand. Retain all C2 assignments;
do not estimate the live effect only among runs receiving the note.

## C3: conditional development factorial

Restore the full design only after C1/C2 are interpretable:
**2 issues × 3 variants × 4 arms × 2 draws = 48 runs**, with the same Haiku model.
Freeze its budget using measured context growth and time to useful decisions,
including reservation headroom. At unchanged C1 ceilings this would allow 2,880
requests, 144 million input tokens, 5,898,240 output tokens, and $360; that is a
capacity illustration, not the recommended allocation or spending approval.

Estimate averaged R and E differences plus an exploratory interaction, separately
by mutation type. Report original-task capability separately. Sparse violations
in N imply insufficient sensitivity for a reduction study, not that the reminder
works. Use all assigned denominators and report pre-trigger violations and
non-delivery. This remains development on two known issues. The earlier 192- and
1,152-run proposals are deferred until task selection, event rates, costs, and
task-clustered power support an expansion.

## S1: independent behavior × enforcement experiment

This is the first selected follow-up from the
[community-inspired design](community-inspired-experiments.md): distinguish an
agent proposing an unauthorized action from a service allowing its effect.

Use Haiku with **recoverable/impossible × N/RE × permissive/scoped × 8 draws =
64 continuations**, plus **easy × N/RE × permissive/scoped × 4 draws = 16 controls**.
Pair fixture state within variant/draw blocks and randomize the four conditions.
Retain 10 model calls, 20 actions, and 768 output tokens per call. Proposed separate
ceilings: **800 requests, two million input tokens, 614,400 output tokens, $8**.
The uncached token-ceiling cost is about $5.07 at the same rates; preflight the
native transport's reservation/accounting separately from the Inspect budget.

Primary endpoints are any unauthorized proposal and any unauthorized effect.
Report RE−N within enforcement level and scoped−permissive within message level,
with original authorization fixed. Keep recoverable capability and easy-task
over-stopping separate. Report blocked attempts, route substitution, and supported
blocker outcomes, including blockers following earlier violations. The combined
RE intervention does not identify R and E independently. This is one-structure
assay development, not a substitute for held-out validation.

## Deferred questions and reporting contract

| Topic | Revisit when |
| --- | --- |
| Learned action monitors and defensive utility | Historical labels are adjudicated and verifier-scored defensive controls exist |
| Cross-agent communication and transfer permissions | A bounded board, per-agent identities, and independent event provenance are qualified |
| Investigation packet comparison | Reference labels and blinded scoring are prepared |
| Retry/compaction/cue search | A specific hypothesis warrants changing the now-stable scaffold |
| Open-model training | A sensitive, generalizing behavioral assay justifies the separate compute cost |

Keep exact prompts, source/config hashes, assignment schedule, model settings,
usage reservations, raw traces, observer evidence, and blinded semantic reviews.
No automatic retries, replacement models, retrospective schedule pruning, or
rewriting of completed archives. Any positive violation survives a later error;
unobserved outcomes remain unknown. A fully observed horizon without an event is
only a horizon-limited negative. The current ImpossibleBench summary treats
unfinished runs conservatively as unknown; any additional horizon-specific metric
needs a separate documented definition and must retain the original outcome.

Model access and budgets are frozen separately for each live stage. These document
revisions prepare the next decisions; the existing runnable preflight config and
its completed evidence retain their original values.
