# Counterfactual replay as an incident diagnostic tool

Counterfactual replay restarts a scenario from a matched checkpoint, changes one
action or observation, and compares the resulting evidence. The proposed toolbox
connects sandbox adapters, paired replay, incident diagnosis, and executable cases.

![A sandbox adapter feeds a replay toolbox, which compares evidence and saves reproducible cases in an incident library.](../figures/counterfactual-diagnostic-tool-v1/counterfactual-diagnostic-tool.png)

The interface requires state reset or restoration, tool input/output interception,
and trusted event capture. Portability is a design goal for compatible sandboxes,
not a claim that arbitrary environments can already be replayed. External state,
timing, and randomness must be controlled or recorded as limitations.

## Two different comparisons

- **Fixed-call replay:** hold the receiver's requests and initial state fixed,
  change a sender action, and locate the first differing response and its event
  dependencies. This diagnoses an available effect or information channel.
- **Agent continuation:** restore the same pre-intervention history, change one
  cue or returned response, and let the agent choose subsequent actions. Repeat
  stochastic continuations and compare outcomes; a single pair does not establish
  a reliable behavioral effect.

Neither comparison alone establishes intent or exhaustive security. Record the
intervention, first differing observation, relevant resource, authorization, and
remaining uncertainty instead of reducing the evidence to task pass/fail.

## Concrete incident replays

### README link and outside reads

![The observed upstream-link pattern is compared with a proposed replay where only the README link is hidden.](../figures/incident-counterfactual-replays-v1/01-upstream-link-replay.png)

The [link study](link-study-results.md) observed early reads of an excluded
upstream repository after its URL appeared in the README. A new checkpoint replay
would alter only that address in the README response, preserving the resource,
permissions, and prior history. Compare subsequent outside access and authorized
completion. The historical study used fresh rollouts; it is not evidence that this
checkpoint replay has already been run. The drawing abbreviates the task policy:
the designated challenge repository, catalog, challenge endpoint, and scorer
remain authorized.

### Previous run's answer archive

![An observed copied answer is contrasted with a proposed replay withholding only the cached flag from the response.](../figures/incident-counterfactual-replays-v1/02-answer-archive-replay.png)

In [link-study run-0022](../results/link-study-v1/run-0022/transcript.jsonl), a
challenge failure was followed by an excluded archive read and an accepted cached
answer. Replay from before the archive response, preserving its status and run
metadata while withholding the flag. Compare submissions, scorer outcomes, and
later outside access. The archive read has occurred in both branches: this tests
dependence on the answer, not prevention of the original scope crossing.

### Counter signaling

![A local reconstruction of the CA5 counter example compares the delivered increment with a replay omitting only that increment.](../figures/ca5-incident-replay-v1/ca5-counterfactual-replay.png)

The user-supplied *Encoded Coordination on the Open Web* account describes a
counter named CA5 signaling California in round five. In the proposed local
reconstruction, hold the receiver's requests fixed and omit only the sender's
increment. A returned 1 versus 0 would identify the observable channel. The counter
encodes the state and round, not the percentage answer. This figure reconstructs
the reported mechanism; it is not a replay of the historical public service.

## Sandbox components and incident library

![Sandbox components with numbered proposals for contracts, shared state, replay, provenance, and an incident library.](../figures/sandbox-proposals-overview-v1/sandbox-proposals.png)

Store each case with its initial state, policy, exact trace, intervention, expected
effects, legitimate-use controls, and source hashes. Preserve failures as
regression cases. Keep development examples separate from held-out evaluation
families, and freeze interventions before testing the latter. The library belongs
to researcher tooling; it must not provide reference answers to evaluated agents.

The [bounded native-service harness](coordination-harness.md) implements four
channel fixtures, deterministic paired replays, effect journals, and scripted
incident cases. Its [offline execution record](coordination-harness-results.md)
reports eight replay controls, twelve permission/isolation controls, 28 cases,
and 84 prepared monitor inputs. General sandbox adapters and the behavioral
checkpoint replays illustrated above remain proposals. No live model inference
has been run for this new harness.

## Figure provenance

The cartoons use built-in image generation and depict proposed mechanisms,
except where a panel explicitly identifies an observed historical trace.
The prompts are preserved with each asset:

- [Toolbox architecture prompt](../figures/counterfactual-diagnostic-tool-v1/prompt.txt).
- [Incident replay prompts and correction](../figures/incident-counterfactual-replays-v1/prompts.json).
- [CA5 reconstruction prompt](../figures/ca5-incident-replay-v1/prompt.txt).
- [Sandbox overview prompt](../figures/sandbox-proposals-overview-v1/prompt.txt),
  [routing correction](../figures/sandbox-proposals-overview-v1/correction-prompt.txt),
  and [connection correction](../figures/sandbox-proposals-overview-v1/connection-prompt.txt).
