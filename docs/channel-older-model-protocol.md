# Channel tasks with Haiku 4.5

Prospective allocation written on 2026-11-17. Prepared and frozen without
inference: on that date every Anthropic request from the project key returns
HTTP 403 `verification_required` (`runs/haiku-availability-20261117-v1`). Run
it unchanged once access returns. Do not substitute a model or a provider.

## Why

Haiku 4.5 is the model with the large planner effect on the native recovery
fixture (12/16 plain incidents, 0/16 with planning). Astra, Fable, Opus and
Terra were measured only on office tasks, and Haiku never ran them. This
allocation puts Haiku on the sixteen unchanged channel tasks so that model and
task stop varying together.

## Design

- Tasks: the sixteen original channel tasks, byte-for-byte.
- Conditions: the five existing arms (`plain`, `grant_only`, `planner`,
  `journal`, `planner_journal`), executed by the unchanged episode runner with
  unchanged prompts, tools, scoring, budgets and permissive dispatch.
- Scope contracts: the frozen reviewed contracts of
  `runs/channel-algorithms-20261112-v1`, so Haiku receives the same advice text
  Astra and Fable received. No scope calls.
- Model `claude-haiku-4-5-20251001`, the ID used by the native cohort and
  listed by the Models API on 2026-11-17, in two settings:
  - `haiku`: no extended thinking.
  - `haiku_thinking`: `thinking: {type: enabled, budget_tokens: 8000}`.
  Both omit temperature, allow 16,384 output tokens per turn and disable
  parallel tool calls, as the frontier cohorts do. The native cohort used
  temperature 0.7 and 768 output tokens; that difference remains.
- Three episodes per task/setting/arm, fixed in advance: 480 episodes, so each
  wording has twelve episodes per arm, matching the pooled three-model counts.
  Six workers, shuffle seed 20261117. No dollar cap, retries or
  outcome-dependent extension.

The request shape for Haiku 4.5 thinking comes from Anthropic's documentation
and has not been exercised live. If the API rejects it, record the failures and
freeze a corrected allocation separately; do not edit this one.

## Readings fixed in advance

- Haiku shows the same follow-up/chase split under planner advice: the split is
  a property of the tasks and advice, not of frontier models.
- Haiku follows ASK_USER on both wordings: on these tasks the planner works on
  Haiku and not on the frontier models, which is a model difference.
- Haiku rarely writes in plain: no headroom on these tasks for this model.

Compare the two settings to see whether extended thinking moves the result.
Report all five arms by wording and replicate; keep unknowns in denominators;
audit and read final responses as in the earlier channel reports. Descriptive
only: eight related topics and two templates.
