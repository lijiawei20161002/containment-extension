# Channel tasks with Haiku 4.5, through OpenRouter

Prospective allocation written on 2026-11-17, before any behavioral output from
it exists. It is the Haiku 4.5 allocation of
`docs/channel-older-model-protocol.md` on a different provider path. The
direct-Anthropic allocation (`runs/channel-older-model-20261117-v1`) stays
frozen and unrun: on this date three Anthropic keys failed (organization
verification required; workspace usage limit until 1 December; organization
disabled). The user asked to use their OpenRouter account instead.

## What is the same

Tasks (the sixteen original channel tasks, byte-for-byte), the five existing
arms executed by the unchanged episode runner, prompts, tools, scoring,
budgets, permissive dispatch, the inherited reviewed scope contracts of
`runs/channel-algorithms-20261112-v1` (so the advice text is the one Astra and
Fable received; no scope calls), two settings with and without extended
thinking, three episodes per task/setting/arm (480 episodes), six workers,
shuffle seed 20261117, no dollar cap, no retries, no outcome-dependent
extension.

## What differs: the provider path

- Requests go to OpenRouter's Responses-format endpoint through the harness's
  existing `openrouter` adapter (`providers.py`, unchanged), model
  `anthropic/claude-haiku-4.5`, with `provider: {only: [anthropic],
  allow_fallbacks: false}` so that only Anthropic's own endpoint may serve
  them. OpenRouter converts the request to Anthropic's format and the response
  back; the system prompt travels as `instructions`.
- `haiku`: no `reasoning` field. `haiku_thinking`: `reasoning: {max_tokens:
  8000}`, which OpenRouter documents as Anthropic `budget_tokens` 8000.
- `parallel_tool_calls: false` replaces Anthropic's
  `disable_parallel_tool_use`. The harness executes one tool call per turn.
- Temperature omitted; 16,384 output tokens per turn.

Neutral probes before freezing (`runs/haiku-openrouter-availability-20261117-v2`,
excluded from behavioral results): both settings complete a tool round trip;
the response echoes `anthropic/claude-haiku-4.5`; OpenRouter's generation
records name the provider `Anthropic` and the model
`anthropic/claude-4.5-haiku-20251001`; reasoning tokens are 0 without the
`reasoning` field and positive with it, and reasoning items survive a
three-turn tool loop; without `parallel_tool_calls: false` the model returns
two calls in one turn when invited, with it one call per turn.

After the run, query OpenRouter's generation record for every response and
report the serving provider and model. Any episode served by another provider
stays in the data and is reported.

## Limits specific to this path

Behavior through a converting gateway may differ from the direct API in ways
this allocation cannot detect; if the direct allocation is run later, compare
the two. Recorded model identifiers come from OpenRouter and do not
independently verify model internals. Costs are list-price token estimates, not
OpenRouter bills.

## Readings fixed in advance

Unchanged from `docs/channel-older-model-protocol.md`:

- Haiku shows the same follow-up/chase split under planner advice: the split is
  a property of the tasks and advice, not of frontier models.
- Haiku follows ASK_USER on both wordings: on these tasks the planner works on
  Haiku and not on the frontier models, which is a model difference.
- Haiku rarely writes in plain: no headroom on these tasks for this model.

Compare the two settings to see whether extended thinking moves the result.
Report all five arms by wording and replicate; keep unknowns in denominators;
audit and read final responses as in the earlier channel reports. Descriptive
only: eight related topics and two request templates. The native Haiku cohort
used temperature 0.7 and 768 output tokens; that difference remains.
