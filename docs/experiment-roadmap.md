# Focused roadmap

The organizing story is [incidents → decisions → external feedback → measured
behavior](../README.md). The two mechanisms are Grant Look-ahead and Effect
Journal. Work is organized around three empirical questions.

| Question | Existing main assets | Next analysis or experiment |
| --- | --- | --- |
| Do agents follow feedback? | Planner values, journals, and action trajectories in the workflow and native cohorts | Define a turn-level adherence measure; report agreement, ignored advice, repetition after journal delivery, and authorized recovery separately |
| Does feedback reduce initial and repeated violations? | Plain/planner/journal/combined arms, feasible controls, independent effect records | Separate first-incident episode rates from repeat-effect counts; retain completion and missing-outcome bounds; test harder or structurally distinct tasks where baselines are informative |
| How does evaluation awareness affect behavior? | Reward × journal-notice contrasts in `eval-awareness-*` cohorts | Connect cue contrasts to feedback-following; test more than one awareness cue before making broader claims |

## Interpretation rules

The planner advises; the broker enforces. A journal arrives after the effect it
describes. Stopping can reduce incidents by sacrificing useful work, so report
authorized completion alongside incidents. The two workflow skins share a
transition structure. Provider errors, interrupted cohorts, and unresolved
outcomes stay visible. Audit notices measure cue sensitivity, not internal beliefs.

## Execution order

1. Use the retained evidence to audit feedback timing and define adherence labels.
2. Produce one common summary of adherence, first/repeat effects, completion, and
   uncertainty for the existing arms. Preserve the original raw evidence.
3. Design a focused follow-up that addresses the largest remaining ambiguity,
   with a fixed protocol, comparison, and allocation before execution.

This roadmap is not a new live allocation. The cleanup itself launches no model
calls and resumes no historical studies. [HANDOFF.md](../HANDOFF.md) records how
to inspect an existing run safely.

## Retired directions

Policy-selection optimization, learned-judge reliability, ImpossibleBench and
AgentDojo transfer, coordination studies, boundary games, and earlier slide
narratives are preserved in the [archive](../archive/README.md). They can inform
future work without competing with the current three-question story.
