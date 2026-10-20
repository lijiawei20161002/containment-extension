# From reported incidents to testable questions

Checked 20 October 2026. Public reports, our interpretation, archived local
experiments, and proposed experiments are different evidence classes. The deck
labels each class. The incidents are not observations from our service fixture.

## What the incidents actually contribute

| Case | Reported observation | Our testable interpretation |
| --- | --- | --- |
| Medicare statistics portal; June incident, 24 September briefing | A statistics request was denied. Unauthorized portal access followed. The government says no individual medical data was accessed. [Government briefing](https://ministers.finance.gov.au/financeminister/transcript/2026/09/24/press-conference-sydney) | Test the next action after a route fails. Do not infer that all legitimate routes were impossible. |
| Workbook; 14 April incident, 16 September report | Local collaboration failed. An agent put the workbook on public hosting despite a local-only task. [OpenAI report](https://alignment.openai.com/misalignment-reports/unauthorized-communication-via-temporary-file-hosting-services/) | Give a task both an allowed transfer route and a reachable forbidden destination. Vary whether the allowed route works. |
| Test wallet; 26 June incident, 15 October report | A deployment used funds from an account not supplied by the task. [OpenAI report](https://alignment.openai.com/misalignment-reports/using-a-funded-test-cryptocurrency-wallet-without-authorization/) | Keep a resource accessible while changing its owner or authorization. Successful execution is not evidence of permission. |
| Opus 4.7 evaluation | Reachability and a matching name were treated as evidence of scope. [Anthropic assessment](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents) | Test explicit authorization against environmental clues. A blocked task is not the only relevant condition. |
| DSEwiki | GET requests could create public writes and support communication across runs. [Researcher report](https://collusion.wiki/) | Label the resulting operation and information flow, not just the HTTP method. Add persistent state only when it is actually implemented. |

The common research question is: **When a task needs another route, does the
agent preserve the original limits on resources and actions?** This is our
interpretation of the cases. These reports do not identify one common cause.
They do not establish that persistence caused each incident. There is no matched
counterfactual, randomized intervention, or denominator of comparable benign runs.

The existing incident library has 26 draft records. Its independent reader is
still pending, and 42 source entries lack URLs. We verified the specific sources
above for this revision; we did not validate the full library. The wallet report
is additional evidence, outside the 26-record inventory. No library-wide
percentage is presented as a population failure rate.

The primary Opus assessment also corrects a misleading shorthand in the old
draft: the relevant issue is inferred authorization for a real target, not simply
failure to recognize reality. The deck follows the primary source.

## Why recover versus stop is a useful test

A failure response is an observation. It is not a proof that no allowed plan
exists. There are two separate questions:

1. Can an allowed action still achieve the task?
2. Is the next action within the delegated scope?

Our current fixture separates these questions in a small, inspectable setting.
Recoverable and impossible variants have byte-identical initial setup histories.
Both end with a 503 response. An allowed recovery call reveals whether the
fallback is available. Its response is not known at the checkpoint.

In this fixture, the documented action set is closed. A successful recovery
enables the current-run flag. An unavailable recovery, together with the service
specification, rules out the allowed repair. Other runs' answers remain reachable
but excluded. In an open environment, a single failed repair would not justify
the same conclusion. The task contract distinguishes `blocked` from `incomplete`.
It does not license an unsupported claim of impossibility.

This explains the evaluation tradeoff:

- Stop immediately after every error: lose recoverable completions.
- Continue until the scorer accepts something: risk using excluded resources.
- Diagnose within scope, then recover or report the blocker: the intended behavior.
- If the evidence is insufficient: report the uncertainty or request clarification.

This is not a new decision principle. It makes the delegated-authority question
concrete enough to evaluate. The interesting distinction is between **changing
the plan** and **changing the permission**. A technical failure can require the
first without authorizing the second.

## What our experiments cover

| Incident-derived question | Current evidence | Not established |
| --- | --- | --- |
| Does a failed route lead to a different resource? | The 160-run study has 15 violations. All first read a prior-run answer archive. | Causality across real incidents; transfer to uploads, payments or production targets |
| Can an agent recover and also stop appropriately? | Archived recoverable and blocked trajectories share the same starting observations. All 96 historical feasible controls completed within scope. | Reliable decisions under incomplete evidence or open action sets |
| Does a final task score describe the whole trajectory? | 13 violations passed the scorer; two did not. | A general advantage over every existing incident metric |
| Can a transcript judge apply the exact authorization rule? | The 48-target audit found one false alarm and five null scores under its frozen score parser. Calibration failed. | A validated online gate or improved policy selection |
| Does wording change behavior? | Paired-note diagnostic: 11/16 versus 15/16 impossible-case violations; interval includes zero. | A confirmed note effect or a generally superior prompt |

Sources: [historical results](incident-study-results.md),
[follow-up results](trust4rsi-live-followup-results.md), and
[evidence extraction](../slides/trust4rsi-paper-deck/collect_evidence.py).
Our behavioral data come from actual hosted-model calls in local synthetic
services. Public uploads, wallet spending, multi-agent coordination and
production access were not reproduced. Scripted infrastructure checks do not
count as model behavior.

## The next discriminating experiment

The next experiment should separate **repair availability** from **permission**.
Keep the task, archive contents, technical access, tools and inference budget
fixed. Randomize paired fixtures over these two factors:

| Local recovery | Archive forbidden | Archive explicitly authorized |
| --- | --- | --- |
| Available | Recover and complete within scope | Either authorized route can complete |
| Unavailable | Report blocked in the closed fixture | Read the archive and complete |

These cells describe allowed behavior, not observed results. In the bottom-right
cell, the local repair fails but the overall task remains feasible. Calling that
cell “impossible” would confuse local failure with lack of an authorized solution.
The explicit permission must be part of the trusted task and the observer's
policy, not an assertion made by the archive.

Use the existing instruction as the baseline. Add an explicit stop/escalate
instruction adapted from ImpossibleBench, a permission-check instruction, and a
broker that checks the action before execution. Mark the adaptation as an
adaptation; it is not a rerun of the original coding treatment. Keep the model,
information, paired inputs, tool budget and task score fixed across these arms.

Primary outcomes should be authorized completion and any executed unauthorized
effect, reported for every assigned run and for each cell. Also record attempted
violations, blocks, premature stopping on feasible tasks, recovery probes and
unknown outcomes. An enforced arm can have zero executed violations while still
attempting them. Its coverage must be stated.

Freeze the sample size, useful effect size, utility margin, model, schedule and
analysis before inference. Do not reuse current trajectories as held-out data.
Use a second task family, such as local artifact transfer, to test transfer;
changing flag seeds alone is insufficient. Reproduce only local effects with
dummy data. No real portal, wallet or public hosting service is needed.

The later feedback-selection study remains conditional. Compare transcript-only,
transcript-plus-effect-evidence and deterministic effect labels on the same
development runs. Freeze selections before fresh evaluation. This separates an
information advantage from a classifier advantage. Ties and null effects are
valid results. A confusion matrix alone does not demonstrate better selection.

## What remains novel is an empirical question

ImpossibleBench already covers contradictory tasks, prompt interventions, abort
options, tool restrictions and monitoring. Anthropic already tests incident
continuations and CTFs with no in-scope solution. CoSec already evaluates active
authorization and cross-context flows. CaMeL already provides runtime enforcement.
See the [technical comparison](trust4rsi-related-work.md).

The present contribution is a small measurement study with inspectable traces
and explicit limitations. The proposed factorial design could test whether
behavior responds to permission independently of repair availability. It is not
yet a result, a verified literature gap, or a new containment method.

The local design requires CPU, SQLite and hosted API access, not a GPU. A clean
ImpossibleBench comparison additionally needs working container task environments
and recovered raw baseline logs. Human source review remains a separate resource
requirement.
