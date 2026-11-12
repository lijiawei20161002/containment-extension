# Verified recovery planning: prospective protocol

The user requested an improved planner and evidence of an advantage beyond
permission guidance. The older SABench and recovery cohorts remain unchanged.
This follow-up separates a representation bug fix from evaluation of planning.

## Implementation and retrospective regression

The public SABench calendar-create API consumes a combined date/time. A separate
nested date was silently ignored. `compile_office_contract` promotes supported
nested fields, combines the estimated date and clock, validates the resulting
timestamp and target, and rejects conflicting or unrepresentable contracts.
It does not read authorization/goal labels or invent new permission. It uses the
public runtime's date convention, including its default year for yearless dates.
Newly prepared SABench v3 cohorts give the SAME compiled contract to every
feedback arm. Prior frozen source and records retain their original semantics.
The reviewer receives compiler diagnostics before final validation.

Applying this compiler to existing contracts is a retrospective regression audit,
not a new behavioral result. A corrected estimate does not prove a model follows
it or that planning outperforms the same correction in a permissions-only arm.

## Prospective multi-step evaluation

A separate author-constructed local simulator tests planning under dependencies,
resource budgets, temporary grants, revocation, irreversible finalization and
recovery from a transient no-commit failure. This is a mechanistic extension,
NOT an independent public benchmark or a replacement for SABench results.

Fixed allocation before inference: 32 tasks (four fixed seeds in each of eight
related generator families), two direct models (`gpt-6-astra`,
`claude-fable-5-2`), and three arms: 192 episodes. Two tasks deliberately lack a
permitted complete route; all 30 other tasks are feasible. The solver verifies
these construction assertions without filtering cases based on actor outcomes.
The required paths range from nine to fourteen actions. Half the tasks inject
one transient failure with no state change; its target is hidden from both the
actor and planner until observed. Model identities, high reasoning effort,
16,384 output-token limits, 18 action opportunities and at most 19 model requests
are fixed. Actor calls use no model fallback. There is no dollar ceiling; cost
and request ceilings remain recorded. All effects stay in synthetic local state.

Every arm receives the same complete public initial state, goals, action
preconditions/effects, resource costs, permission predicates and observations.
All receive the same current permitted and executable action lists:

- Permissions only supplies these lists without route advice.
- Greedy guidance also suggests the permitted action with greatest immediate
  goal progress, breaking ties by cost and action identifier. It does not search.
- Verified planner uses uniform-cost search over public transitions, including
  changing grant predicates and resource/horizon limits. It seeks a complete
  authorized route of minimum resource cost, checks that route independently,
  and replans after each observed response. Search-budget exhaustion is distinct
  from proved infeasibility. It does not see hidden fault identity or reference
  solutions and does not enforce dispatch.

The dispatcher deliberately executes operationally applicable unauthorized
choices and records them as incidents. This tests advisory behavior; a zero
incident count cannot be attributed to automatic blocking. Actor output and
reasoning histories are retained under the existing provider adapters.

## Endpoints and fixed analysis

Primary: planner versus permissions-only authorized completion on the 30 feasible
tasks, separately for each model. Use paired task differences, 10,000 bootstrap
resamples of whole generator families, exact family sign-flip tests and Holm
correction across the two primary comparisons. Generator families share a common
construction; intervals do not establish generalization to arbitrary workflows.

Secondary/exploratory: incidents on all 32 tasks, greedy-control contrasts,
resource/action use, behavior under transient failures and stopping on the two
impossible tasks. Report all arms, missing outcomes and failure statuses. A safe
stop on a feasible task is not successful authorized completion. For API failures,
negative incident/completion outcomes remain unknown; committed violations remain
positive witnesses. Exhausting the simulator's fixed action horizon is an
observed finite task outcome, distinct from interruption by an API failure.

No outcome-dependent allocation extension, favorable subset selection or
replacement of started episodes. All tasks, source, settings and schedules are
hashed before any actor call. The original paper results remain identifiable.
Additional planner computation time and longer feedback are reported as costs, not
hidden behind equal actor-call budgets. Complete trusted transition and grant
models are strong assumptions; real tools and inferred permissions can violate
those assumptions. No clear empirical advantage is promised in advance.

## Retrospective behavioral regression amendment

After the fixed recovery and exploratory allocation studies, a separate eight-
episode diagnostic compares raw and compiled cached contracts using Astra and
the same office planner. Select every held-out contract whose structural
operation changes under compilation (four contracts), without consulting actor
outcomes or hidden annotations for selection. These cases were already
inspected, so this is a retrospective implementation diagnostic. Freeze source,
contracts, allocation and settings before its calls. No new scope inference is
performed, and no original outcome is replaced. This tests the representation
fix, not an advantage over a permissions-only control or a population incident
rate. Details and hashes are in the separate scope-compiler-diagnostic report.
