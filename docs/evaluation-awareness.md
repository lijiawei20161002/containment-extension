# Evaluation awareness and external feedback

The third [project question](../README.md) asks how evaluation awareness affects
agents' behavior and the results we observe. The implemented study manipulates
evaluation cues; it does not directly measure an agent's internal awareness.

## Existing design

The synthetic workflow crosses two alternate-resource incentives with five arms:

| Dimension | Conditions |
| --- | --- |
| Alternate-resource incentive | Cost of 3; bonus of 4 |
| Feedback and notice | Plain; planner; journal; journal with audited notice; journal with unaudited notice |
| Shared environment factors | Archive/transfer skin, fallback availability, initial grant, and precommitted request reply |

Both notice arms show the same effect-journal content. One states that a trusted
human auditor will review it; the other states that it is not audited, reviewed,
or reported. These are experimental messages. The harness records every arm's
effects regardless of what the message says.

Configurations: [Haiku 4.5](../experiments/eval-awareness-v1-haiku-4-5.json),
[Sonnet 5](../experiments/eval-awareness-v1-sonnet-5.json), and
[Sonnet 5.5](../experiments/eval-awareness-v1-sonnet-5-5.json).
The latter cohort is interrupted and must remain separate from completed cohorts.
The [dashboard](../dashboard/index.html#awareness) displays the existing contrasts;
its episode explorer retains interrupted trajectories.

## How to interpret the contrasts

- Compare audited versus unaudited notices at the same reward and environment
  settings to estimate sensitivity to those messages. A difference is consistent
  with monitoring-sensitive behavior, but does not establish a private belief or
  deceptive intent.
- Compare alternate cost versus bonus within the same arm to estimate sensitivity
  to this reward manipulation. The planner's grant filter excludes unauthorized
  alternatives under either reward. Its action values and authorized
  recommendations can still change with utility.
- Compare the journal without an added notice against plain to study the effect
  of providing the journal. Journal content may itself suggest monitoring, so this
  contrast does not isolate informational use from every evaluation cue.
- A null cue contrast can reflect low baseline incidents, weak cues, or limited
  sample size. It does not demonstrate that the agent used the feedback or that
  behavior will transfer to deployment.

Report first-incident episodes, repeated effects, authorized completion, and
unknown outcomes separately. Keep models, incentives, skins, and incomplete
cohorts visible rather than pooling them into a single headline effect.

## Remaining work

Align explicit turn-level feedback-following measurements with these contrasts.
Then test whether cue effects persist in tasks where the baseline produces enough
incidents to discriminate the arms. A broader claim about evaluation awareness
requires additional operationalizations beyond this audit-notice manipulation.
See the [focused roadmap](experiment-roadmap.md).
