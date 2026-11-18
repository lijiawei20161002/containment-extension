# Evidence for the main story

Start with the [project overview](../README.md), then the
[results dashboard](../dashboard/index.html). The dashboard's checked-in
`data.json` supports inspection even when local raw runs are unavailable.

| Question | Evidence | Where to inspect |
| --- | --- | --- |
| Does guidance help current models on independent tasks? | 1,320 held-out Astra/Fable episodes with five conditions; separate development and network retries | [Held-out results](sabench-heldout-v2/REPORT.md); [protocol](../docs/sabench-transfer-protocol.md) |
| Do agents follow feedback? | Advice, journal delivery, tool outcomes, and the next action | Dashboard “1. Following feedback”; full local episode transcripts |
| Does feedback reduce incidents? | First-incident episodes, repeated effects, completion, and unknowns | Dashboard “2. Incident reduction”; [native Haiku pilot](../docs/native-algorithms-results.md) |
| Do evaluation cues matter? | Journal-only, audited-notice, and unaudited-notice arms crossed with alternate-resource rewards | Dashboard “3. Evaluation awareness”; [study design](../docs/evaluation-awareness.md) |

## Local raw evidence

The [Fable and Opus repeat](channel-mechanism-anthropic-openrouter-v1/REPORT.md)
of the wording and advice-delivery allocation adds 288 episodes on the same 24
tasks, six conditions and scope contracts. The binding framing gives 0/16
incidents for both models, from 9/16 (Fable) and 12/16 (Opus) for the same
planner output under the original note; with Astra and Terra that is 0/64
across four current models. Chase requests give 32/32 incidents for each model
across plain and the three fallible arms. Opus leaves some explicit-email
controls uncompleted in every arm including plain, for the reason seen on 12
November, and the binding arms are no worse. Fable's labels on the sixteen
original tasks agree with the 12 November direct-API run in 15/16 per arm.
Requests went through OpenRouter, served by Anthropic for all 474 responses.
Model-written reasoning summaries on overriding episodes say the request is not
really ambiguous given the ticket text. Descriptive, known development topics.
Not yet in the paper.

The [Haiku 4.5 channel allocation](channel-older-model-openrouter-v1/REPORT.md)
of 17 November puts the older model on the sixteen unchanged channel tasks and
five unchanged arms, with the advice text Astra and Fable received: 480
episodes, with and without extended thinking, three per cell. Plain Haiku
writes before asking in 22/24 and 19/24 unspecified episodes. With
permissions-only it is 0/24 in both settings, and with planner advice 0/24 and
2/24, including the chase requests on which Astra, Fable, Opus and Terra gave
16/16 under the same advice. Journal alone matches plain (22/24). So on the same
tasks the older model follows advice labelled as possibly mistaken and the
current models do not, which is a model difference. Six assignments are unknown
after one network error. Requests went through OpenRouter's converting
endpoint; its records show Anthropic serving all 793 responses with the
`claude-4.5-haiku-20251001` snapshot. Descriptive, known development topics.
Not yet in the paper.

The [wording and advice-delivery allocation](channel-mechanism-v1/REPORT.md)
of 17 November adds 288 Astra and Terra episodes on the channel tasks: the
sixteen originals plus eight requests that keep each topic and use the other
wording, in six conditions. Telling the actor that the permission service is
binding takes incidents on the sixteen unspecified requests to 0/16 for both
models, from 11/16 (Astra) and 15/16 (Terra) for the same planner output under
the original "may be mistaken" note, with all explicit-email controls still
completing. The earlier follow-up/chase split follows the wording, not the
topic: chase requests give 31/32 and 32/32 incidents across plain and the three
fallible guidance arms, including on topics that previously produced safe
questions, and the scope estimator's own first draft authorizes a ticket comment
for 7/8 chase requests and 0/8 follow-up requests. Adding the scope rationale to
planner advice helps slightly on follow-up and not on chase. All 288 episodes
finish normally and pass replay and first-request audits. These are two OpenAI
models on known development topics with one episode per cell; the binding arms
measure instruction following, and no task has a wrong estimate, so the cost of
binding one is unmeasured. Anthropic models were unavailable on that date
(HTTP 403 `verification_required`); a Haiku 4.5 allocation on the unchanged
tasks is frozen and not run. Not yet in the paper.

The [four-model deeper-planning study](frontier-deep-planning-v1/REPORT.md)
adds 216 episodes on scarce and revocable capacity: Astra, Fable, Terra and
Opus, with plain, permissions-only and planner conditions. All sixteen
feasible tasks finish safely in every condition. Planning reaches minimum
resource cost on 16/16 for each model, versus 9–11/16 plain and 8–13/16 with
permissions-only, although total resource savings are only 0.65–2.31% versus
permissions-only. Output tokens fall by 58.5–69.1% versus permissions-only.
Opus provides the clearest cost benefit: 30.7% cheaper than plain and 17.8%
cheaper than permissions-only on the same sixteen safe completions. Costs
do not uniformly fall: Fable planner costs 1.6% more than permissions-only,
and Astra/Fable/Terra planner costs more than plain.

Terra plain has one incident on the missing-capacity impossible control:
it uses a lease absent from the public state. Permissions-only and planner
both avoid that incident and finish eleven of twelve work items safely.
This is a concrete explicit-permission failure, but not evidence that
planning adds safety beyond permission feedback. All other conditions are
incident-free. All 216 finish normally and pass replay; no unknowns, retries,
model fallbacks or outcome-driven task exclusions. These exploratory tasks
use trusted complete transitions and have not yet been added to the paper.

The [Terra/Opus channel replication](channel-terra-opus-v1/REPORT.md) retains
160 additional episodes on the same tasks and five arms. Opus incidents are
8/8 plain, 5/8 permissions-only, 5/8 planner, 7/8 journal and 5/8 combined.
Terra records 8/8 in every condition. Thus Opus improves descriptively over
plain, with no added planning advantage over permissions-only; Terra shows
no first-incident reduction. Opus sometimes asks who owes the diagnostics
even when email is explicit, reducing safe completion to 5/8 in plain,
planner and combined, 7/8 permissions-only, and 8/8 journal. All Terra
explicit controls complete safely. All 160 finish normally; all 16 shared
scope contracts match. Every outcome, repeat effect, direct clarification
review and replay audit remains available. These results are separate from
the earlier Astra/Fable comparison and have not yet been added to the paper.

The [Astra/Fable algorithm comparison](channel-algorithms-v1/REPORT.md) retains
160 new episodes: all eight unspecified-channel cases, eight explicit-email
controls, five conditions and both models. Ambiguous-task incidents are:

| Condition | Astra | Fable |
| --- | ---: | ---: |
| Plain | 8/8 | 6/8 |
| Permissions-only | 2/8 | 3/8 |
| Grant Look-ahead | 4/8 | 4/8 |
| Effect Journal | 8/8 | 6/8 |
| Planner + journal | 4/8 | 4/8 |

All 80 explicit-email episodes complete safely. All 160 actors finish normally,
with no unknowns, and all 16 shared inferred contracts match benchmark scope.
Planner guidance improves on plain instructions descriptively; permissions-only
does better. Both planner conditions give ASK_USER on every ambiguous request,
but both models ignore it on all four requests using the chase wording.
Journal feedback correctly flags committed incidents, with no observed added
reduction. No condition has repeated incidents, including plain. The report
retains every response, reviewed clarification annotations, paired outcomes,
scope estimates and the full transcript/state audit. These are known development
cases under the strict ambiguity policy, not held-out efficacy evidence.
The paper includes this comparison as Table 2 and preserves the preceding
216 development episodes in its appendix and anonymous reproducibility data.

The [Astra/Fable incident search](frontier-incident-discovery-v1/REPORT.md)
retains 96 plain-instruction episodes across 48 tasks after Fable API access
was restored on 12 November. Astra records 8/8 and Fable 7/8 incidents on the
known unspecified-channel cases; the original channel family gives 0/4 and
3/4 respectively. Seven task instances have incidents in both models. All
other families have zero incidents, including eight explicit ask-and-wait
variants and sixteen new scope cases per model. These are strict ambiguity
policy failures, not demonstrated violations of explicit prohibitions.
All episodes finish normally, and all 18 positive results have replayed
committed effects. The report retains completion limits, all negative cases,
reviewed clarification questions, raw labels and provenance. No planner was used.

The [unsolicited ticket-update transfer](followon-comparison-v1/REPORT.md)
tests a different historical Fable incident on Astra: an unrequested ticket
comment after replying to a complaint email. Across all four original instances,
plain, permissions-only and planner each have 0/4 incidents and 4/4 safe
completions. Each also completes all four controls explicitly requesting both
writes. All 24 runs finish normally. The historical failure does not reproduce
in this allocation; no planner advantage is demonstrated. A trace-level
completion check supplements the benchmark's permissive ticket-goal fallback;
the raw and verified labels agree in all 24 episodes. The prior ambiguity
comparison remains preserved separately.

The [Astra ambiguity guidance comparison](ambiguity-planner-comparison-v1/REPORT.md)
adds a separate 48-episode allocation on the same eight unspecified-channel
cases and eight explicit-email controls. Ambiguous-task incidents are 8/8 plain,
6/8 planner, and 3/8 permissions-only, with no unknowns. Every arm safely
completes all eight explicit controls. All 16 inferred contracts match the
benchmark; six planner actors still write after ASK_USER advice. This tests
the existing pipeline on known development cases and establishes no added
planning benefit. The report includes paired outcomes, all contracts, inspected
clarification questions, and a full offline evidence audit.

The [plain-Astra challenges](astra-challenges-v1/REPORT.md) retain 48 new
development episodes: 0/32 incidents on explicit workflow constraints, 8/8
ambiguity-policy incidents on unspecified communication channels, and 0/8 on
matched explicit-email controls. All eight incident writes are internal ticket
comments. The strict ambiguity interpretation is contestable and is stated in
the report; these results do not establish violations of explicit prohibitions
or planner effectiveness. Every episode ends normally, with no unknown outcomes.
The full case export and provenance hashes are beside the report.

The [office argument audit](office-argument-audit/REPORT.md) identifies interface
defects in the historical SABench comparisons, including all seven original
Fable planner incident episodes. The [corrected-interface regression](office-interface-regression-v1/REPORT.md)
uses the same format checks in all arms: Astra has zero committed incidents in
78 runs, with completions of 24/26 plain, 26/26 permissions-only, and 26/26 planner.
Three plain runs correct a rejected argument and finish. Rejections remain
logged separately. This verifies an environment fix, not planner-specific safety
improvement. Fable was unavailable due to its workspace quota at that point.
The later incident search confirms restored access and measures 48 new Fable
episodes with corrected arguments; it does not fill in the earlier regression.

The validated planner has three additional, separate evaluations:

- [Recovery planning](recovery-planning-v2/REPORT.md): 192 assignments;
  observed feasible runs all succeed, including permissions-only and greedy
  controls. There is no demonstrated additional completion benefit.
- [Resource allocation](allocation-planning-v1/REPORT.md): 96 assignments in
  an exploratory follow-up. Astra succeeds safely on 24/24 tasks in both arms;
  planner guidance uses 45.0% fewer output tokens with essentially unchanged
  API cost. Fable's 48 outcomes are unknown after workspace-quota failures.
- [Calendar regression](scope-compiler-diagnostic/REPORT.md): eight Astra
  episodes on four already inspected malformed contracts. Compilation changes
  incidents from 4/4 to 0/4 and authorized completions from 0/4 to 3/4. The
  [retrospective contract audit](scope-compiler-regression/REPORT.md) covers
  all 132 saved contracts. Neither analysis establishes superiority over
  permissions-only guidance or representative incident reduction.

These studies preserve the earlier evidence below. Unknown API outcomes and
safe but unfinished tasks are different: the compiled calendar non-completion
is an observed clarification request, whereas Fable's allocation runs failed
before any action.

The SABench study retains [development v1](sabench-development-v1/REPORT.md),
[development v2](sabench-development-v2/REPORT.md),
[held-out](sabench-heldout-v2/REPORT.md), and
[network-recovery](sabench-network-recovery-v1/REPORT.md) reports with anonymous
CSV outcomes and provenance hashes. The 78 successful retries remain separate
from the original failed trajectories. Astra's lower planner incident count is
descriptive; template-clustered tests are inconclusive, and permissions-only
matches planner incident labels on fully observed pairs. No benefit from
planning beyond permission guidance is established.

The ignored `runs/` directory retains `decision-algorithms-*`,
`native-algorithms-*`, `eval-awareness-*`, and `sabench-*` cohorts. Each includes its frozen
plan, source snapshot, inference records, and outcomes as originally recorded.
The dashboard exporter reads those paths without changing them.

The 6 November reorganization refreshed a stale dashboard export: 82 native
Sonnet episode placeholders now display their already-saved results. No new
episodes were run. The previous export remains in `archive/dashboard/data.json`.

Completed and interrupted cohorts are separate. Synthetic-workflow and native
recovery results use different task structures and outcome definitions. Native
repeat-effect counts are not currently exported; missing measurements must not
be represented as zero. The historical native Markdown report covers Haiku;
the dashboard additionally contains the Sonnet native cohort.

## Incident evidence

The [incident library](../incidents/README.md) retains public-report records,
sources, and draft codings. `incident-second-reader-v1/` retains the associated
blind review materials; prepared materials do not imply a completed independent
review. [Cross-case analysis](../docs/incident-library-analysis.md) motivates the
decisions studied in the fixtures.

Earlier experiment evidence is in [archive/results/](../archive/results/), and
the [archive index](../archive/README.md) explains the relocation manifest.
