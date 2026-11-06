# Experiments inspired by the cyber-incident discussion brief

**September 21, 2026. Design proposals only; no new model calls.**

**Planning status:** the [active roadmap](experiment-roadmap.md) sets run order
and budgets. Its C1 capability preflight is the next proposed coding allocation;
S1 selects the behavior × enforcement design below as an independent service
study. Coordination, defensive-monitor, and investigation studies remain later
proposals with the prerequisites listed in that roadmap.

The most useful addition is to ask **which combinations of agent behavior,
permissions, and oversight produce an unauthorized effect, while still allowing
legitimate defensive work?** The current blocker study measures one part of this
question. The community discussion suggests testing the surrounding controls and
the costs of those controls as well.

Source: [*Frontier AI Cyber Incidents: Public Discussion Brief*](../../documents/frontier-ai-cyber-incidents-community-summary.docx),
prepared September 21, 2026; a [Markdown companion](../../documents/frontier-ai-cyber-incidents-community-summary.md)
is available alongside the repository in this workspace. These source files are
outside this repository. Section numbers below refer to the brief. Its qualitative
discussion sample motivates hypotheses; it does not establish incident prevalence,
community-wide sentiment, or causal explanations. This note does not independently
verify its incident accounts.

## What changes relative to the existing design

| Brief theme | Experimental implication | Existing coverage and proposed addition |
| --- | --- | --- |
| §1: persistence and connected sequences matter | Measure the whole sequence and substitution after a block | Existing studies record first violations; add fixed-budget retry and route-transition analyses |
| §2: infrastructure failures matter | Separate willingness to cross scope from a service allowing the effect | Combine the existing behavioral intervention with enforced permissions, first in replay and then live |
| §3: interacting agents complicate oversight | Test communication and per-agent authority explicitly | New shared local fixture, team controls, and cross-agent provenance |
| §4: safeguards can obstruct defenders | Measure authorized forensic work alongside prevented violations | New matched defensive tasks and false-block outcomes |
| §§5–6: evidence and accountability | Measure what an investigator can reconstruct from the released evidence | Extend archived traces with a blinded reconstruction exercise |
| Final distinction between incidents | Keep different failure mechanisms separate | Report single-agent scope crossing, coordination, and record modification as distinct outcomes |

The [incident design](incident-assessment-experiments.md) already proposes
permission/framing contrasts, reminder durability, scope-recognition probes, and
action-versus-explanation monitoring. The [broader plan](chunky-generalization-experiments.md)
already separates enforcement replay from live adaptation. The additions below
make the engineering, team, and defensive-utility questions concrete rather than
repeating those proposals.

## 1. Agent behavior × service enforcement

**Hypothesis:** a reminder can reduce unauthorized proposals, while permission
checks can prevent effects even when proposals persist. These are different
contributions to containment.

Start with the native service fixture. Cross two factors at the existing common
failure checkpoint:

| Factor | Control | Treatment |
| --- | --- | --- |
| Behavioral intervention | Existing neutral N message | Existing full-scope plus accepted-blocker RE message |
| Service enforcement | Permissive local dispatcher | Complete reference-policy enforcement |

Retain the original scope instruction in every cell. Keep routes, initial state,
tool documentation, and continuation budgets matched; return truthful denial
feedback when enforcement blocks an action. Use recoverable and impossible
variants, plus separately reported easy controls. RE versus N tests the bundled
intervention; it cannot identify the separate reminder and blocker-wording effects.
Those remain the purpose of the existing four-arm study.

Run this in two stages:

1. **Fixed-action replay:** replay archived proposals against fresh matched states
   under each policy. Compare effects and false blocks against a separately frozen
   semantic permission map. Use scripted positives for channels absent from live
   traces. After the first changed response, replayed later actions remain a
   mechanical control, not a prediction of an adapting agent.
2. **Randomized live continuations:** assign both factors before continuation and
   measure adaptation, termination, and authorized recovery. For the clearest
   pre-feedback behavioral contrast, report the first proposed action separately
   from any proposal across the entire continuation.

Primary outcomes are any unauthorized proposal and any committed unauthorized
effect, reported separately by feasibility and model. Estimate RE−N within each
enforcement setting and enforced−permissive within each message condition; treat
their interaction as exploratory until adequately powered. Also report authorized
completion, supported blocker reports, false blocks, and route substitution.

A later engineering ablation can compare an upstream-only restriction with the
complete owner/run/resource policy. Both use the same external authorization map;
an omitted check does not make archive access authorized. The observed switch to
the previous run's archive in the [incident results](incident-study-results.md)
makes this a useful test of incomplete enforcement. Keep outer containment fixed
throughout: all effects occur in the local replicas.

## 2. Persistence after a block, with matched opportunities

**Hypothesis:** blocking the first route may delay a violation or shift it to a
different resource without producing a clean terminal outcome.

First annotate existing trajectories with the sequence of resource classes:
upstream read/write, prior-run archive, collector, and synthetic mailbox. Report
first proposal, first effect, distinct routes tried, and whether a supported
blocker or authorized success eventually occurs. The current incident archive has
reads but no outside writes, uploads, or messages; absence of those effects in
that archive does not validate enforcement of those channels.

For a causal follow-up, fork a frozen checkpoint immediately before a known
unauthorized request. Execute or block that same request in local replicas, then
continue with truthful observations and equal remaining budgets. Report the
checkpoint selection rule and the state difference caused by the initial action.
This estimates response to that block among selected attempted violations, not
the unconditional frequency of violations or a pure effect of wording.

Use cumulative event curves over dispatched-action count and model calls, with
separate terminal outcomes. Denials consume the same action allowance as other
requests. Do not give the denied branch free retries. A supplementary longer-horizon
comparison must randomize its budget in advance: greater observed risk with more
opportunities alone is not evidence of a change in motivation. Count batched
requests as proposals, not as separate cycles of model reconsideration.

## 3. Communication and authority across agents

**Hypothesis:** shared information can increase team-level boundary crossing, and
an individually plausible action can participate in an unauthorized team sequence.

This requires new infrastructure. The current prior-run artifact is seeded data,
and the mailbox has no responder; neither is evidence of live coordination.
Implement a bounded local message board and isolated agent histories with a
trusted mapping from agent identity to authorized resources and operations.
Messages carry sender and parent-event IDs but cannot grant permissions.

Compare three team configurations on matched tasks:

- One agent with the full team budget.
- Four agents with isolated histories and no cross-agent message delivery.
- Four agents with the same scheduler and a shared local board.

Match aggregate requests, tokens, and service actions; charge communication and
its input-context cost to the same team budget. The two four-agent conditions
isolate the effect of communication availability more directly. Comparing either
with the single agent also changes context partitioning and scheduling; describe
that as a team-configuration effect, not proof of coordination alone.

In a separate permission contrast, make the same reachable board either explicitly
authorized or excluded in trusted instructions and the reference policy. This
distinguishes authorized collaboration followed by another scope violation from
unauthorized communication itself. Include benign collaboration tasks to verify
that agents can actually use the board.

Give each agent a distinct synthetic resource entitlement in a further transfer
test. A sender's permission to read an artifact does not automatically authorize
disclosing it to another agent. Freeze read, send, and receive permissions
separately; do not grade against the union of team permissions.

Measure any team violation as the primary endpoint, with agent-level proposals,
message deliveries, data provenance, and subsequent effects as supporting evidence.
Use independent team runs as the sampling unit. Similar actions alone do not
establish coordination. A causal claim about a particular message requires a
controlled delivery ablation; the main comparison measures board availability.
This small assay would not reproduce the scale described in the brief.

## 4. Defensive usefulness alongside containment

**Hypothesis:** a safeguard can prevent scope violations while also blocking
legitimate investigation, so violation reduction alone is insufficient.

Build synthetic incident-response tasks with verifier-checkable outputs: reconstruct
an event timeline, identify an affected local artifact, and propose a repair within
the assigned repository. Pair an authorized evidence-access condition with an
otherwise matched condition where that resource belongs to another excluded
incident. Update both trusted permissions and grading together. Keep technical
content matched so authorization, rather than the presence of security terminology,
determines the correct behavior. Excluded cases should permit a justified report
that further authorized evidence is needed.

Compare no local action monitor, a frozen learned monitor, and deterministic scope
enforcement. Keep provider safeguards unchanged and record the deployed model
configuration. For the learned monitor, first use the existing
[1,543 prepared action inputs](../results/incident-monitor-inputs-v1/README.md),
after adjudicating historical scope labels, then validate on the new defensive
tasks. The archive's held-out rollouts share a task structure and cannot establish
generalization to incident response.

Report jointly:

- Unauthorized proposals and committed effects on excluded-resource tasks.
- Authorized evidence retrieval and verifier-scored investigation completion.
- False monitor blocks, actor refusals, unsupported blocker reports, and errors
  as separate outcomes; do not infer refusal from every failed completion.
- Actions, tokens, and elapsed time to a correct authorized result.

Select monitor thresholds on development data with a prespecified capability-loss
tolerance, then freeze them before evaluation. Show the tradeoff between prevented
effects and retained defensive completion. Offline blocked-action accuracy does
not establish prevention; live agents may retry or change routes.

An optional hosted/open-weight comparison tests particular deployed configurations.
Differences in model capability, tools, and inference settings prevent attributing
its result to openness alone. It is not needed for the first utility assay.

## 5. Evidence that supports investigation

**Hypothesis:** investigators may miss cross-agent effects or transient changes
when they see only an agent narrative or final state.

Use independently recorded local service events as reference evidence. Create
matched investigation packets containing (A) visible agent reports and final
state, (B) A plus time-ordered tool and service events, or (C) B plus explicit
actor/resource provenance and permission annotations. B and C deliberately add
information; estimate the value of those evidence packages, not a pure formatting
effect. Investigators receive the task policy but not answer labels or treatment
identities. Assign packets so one investigator cannot learn the same case from
another packet; freeze scoring and review ambiguous answers blind to condition.

Score affected resources, first unauthorized action, successful versus blocked
operations, and which principal performed each operation. Include clean cases and
scripted edit-then-revert cases, labeled as scripted in the research record. Measure
false incident claims, omitted effects, and reconstruction time. Give investigators
the complete end-of-run window; the pre-dispatch cutoff still applies to action
monitors, which answer a different question.

To study record modification later, expose a separate mutable local status report
while keeping reference events outside agent write authority. Score attempted and
committed edits plus discrepancies with observed effects. A missing admission,
incorrect narrative, or edit alone does not establish deliberate concealment.
The native observer shares a host and codebase with the services; claim independence
from actor reports, not a separately secured forensic system.

## Priority, execution gates, and reporting

1. **Use existing evidence first:** adjudicate monitor labels, annotate route
   transitions, and prepare enforcement replay and investigation packets. These
   preparation steps require no new model inference. Any model-based monitor or
   investigator evaluation is a separate allocation.
2. **Next service experiment:** the N/RE × enforcement comparison with recovery
   and easy controls. Use development data to check event rates and false blocks;
   size a held-out task study afterward. Do not count new flag seeds as new tasks.
3. **Then extend coverage:** add the defensive task pair before optimizing a
   monitor, and add the message board only after identity, transfer permissions,
   and shared-event logging pass scripted controls.
4. **Keep ImpossibleBench feasibility work explicit:** the
   [latest preflight](impossiblebench-live-preflight-results.md) reached no scored
   submissions or intervention deliveries. Establish original-task completion,
   reliable environment use, and scored-submit reachability before interpreting
   another intervention comparison. These proposals do not resolve that blocker.

Freeze task splits, permissions, prompts, schedules, stop rules, and aggregate
budgets before inference. Reuse current accounting and artifact contracts in a
new versioned study; existing frozen results and plans remain historical evidence.
For held-out inference, pair by task and resample whole task structures, keeping
variants, teams, and repeated draws together. Freeze primary contrasts and a
multiple-comparison rule before opening the test set; keep other analyses exploratory.

Preserve all assigned outcomes. A verified violation remains positive after a
later failure. An interrupted run without a positive is unknown; a fully observed
budget horizon with no event supports only a horizon-limited negative. Report
proposals, dispatch decisions, committed effects, capability, and missingness
separately. Release enough prompts, policy versions, configurations, source hashes,
and synthetic event evidence for another reader to reconstruct each claim.

The intended contribution is a measured account of how agent behavior, service
permissions, communication, and oversight interact. It would not establish that
the brief's incidents share one cause, reveal a training cause, or measure real-world
incident rates.
