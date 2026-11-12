# Deeper planning with four current models

Fixed exploratory allocation, specified before any behavioral calls. Prior
recovery and size 4–10 capacity studies often reached ceiling completion. This
follow-up increases planning depth and introduces actions that revoke a linked
capacity lease. It is a designed stress test, not an independent benchmark.

Use Astra gpt-6-astra, Fable claude-fable-5-2, Terra gpt-6.1-terra and Opus
claude-opus-5-5 at high effort. Plain, permissions-only and existing verified
planner: 18 tasks × 4 models × 3 conditions = 216 episodes. One episode per
condition. All earlier findings and all newly allocated outcomes are retained.

Tasks and seeds are fixed in frontier_planning.tasks. Scarce capacity: sizes
12, 14, 16, 18 with two seeds each. Revocable capacity: sizes 8, 10, 12, 14
with two seeds each. Both require jobs in order, one unused authorized lease
per job, and an explicit resource budget. Some permitted actions also revoke
another lease. Every precondition, permission and effect is public. Each
feasible instance's budget is its exact minimum permitted cost plus 10%
(minimum slack one). The original exact search algorithm verifies feasibility
offline; a search-limit failure blocks preparation rather than silently
discarding a task. Two independent impossible controls (sizes 12 and 10) have
one missing lease and generous resource budgets. No action restores leases.

All arms see the same full task, initial state, tool responses and batch tool.
Plain receives no computed advice. Permissions-only receives the current
permitted and executable permitted action lists. Planner receives those same
lists and the existing exact finite-search recommendation/route. Search uses
only public task semantics, current state and remaining budgets. Reference
routes and feasibility labels do not enter actor prompts. Tools execute
unauthorized actions if operational preconditions hold: guidance is advisory.
There is no injected failure and no hidden state. Effect Journal is evaluated
separately on the unchanged channel tasks; this suite cannot isolate its value
because all committed effects are already deterministically visible.

Maximum 20 requests and 16,384 output tokens per request, six workers, batch
limit 20 operations. Action horizon is jobs plus one; STOP consumes a turn.
Shuffle seed 20261122. No inference-dollar cap. No automatic transport retries,
model fallbacks, outcome-driven prompt changes, extra seeds or repetitions.
Exact model IDs must match responses. Preserve positive incident witnesses
even when later transport calls fail; treat missing evidence as unknown.

Primary descriptive comparisons: authorized completion and incident episodes
for planner versus both baselines, by model and family. Report all 16 feasible
tasks and two impossible controls; no favorable-subset aggregation. Secondary:
partial goal completion, minimum-cost completion, resources, output/input
tokens, requests, estimated uncached API cost and planner CPU time. Token or
cost savings are efficiency findings, not incident reductions. No significance
claim from two related synthetic families or a single draw per task/arm.

Before inference freeze source, tasks, protocol, model settings and schedule.
Audit every assignment, raw request/model ID/settings, emitted operation,
SQLite evidence, state replay, delivered guidance, outcome and recorded usage.
Test missing/revoked lease incidents, feasible routes, controls, plain advice
absence, provider dispatch, and no-replay behavior offline before running.
