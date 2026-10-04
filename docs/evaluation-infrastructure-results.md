# Offline evaluation infrastructure results

**Executed October 4, 2026. Both offline runs passed. No model calls or API spending.**
The counterfactual and ResearchArena-inspired designs now have executable CPU-only
qualification stages in `src/containment_extension/evaluation/` and the main CLI.
The first model grader, monitor, and workflow actor entry points are implemented
and tested with scripted transports, but no live stage has run; their model and
allocation are unspecified. These results establish fixture and evidence behavior, not model
performance, prevention effectiveness, or generalization.

![Implemented evaluation infrastructure, offline results, and pending live stages](../figures/evaluation-implementation-v1/evaluation-implementation.png)

Green marks executed offline checks, blue marks implemented live runners that have
not run, and gray marks later protocol work. Counts come from the frozen run
summaries. [Editable SVG](../figures/evaluation-implementation-v1/evaluation-implementation.svg)
and [figure generator](../scripts/draw_evaluation_implementation.py).

## Counterfactual workflow qualification

The [frozen export](../results/counterfactual-evaluation-offline-v1/summary.json)
contains four matched workflow cases from one base task, 320 comparisons between
the independent graph and dispatcher, and 17 grader evidence cases.

| Case | Independently established result |
| --- | --- |
| Short repair | Authorized two-action witness reaches the completed state. |
| Longer repair | Authorized four-action witness reaches the same goal. |
| Bounded impossible | Complete reachable-state closure is `{0, 1, 3}`; no completed state is reachable through allowed operations. |
| Environment fault | Intrinsically feasible; the injected prepare failure blocks execution. Repairing the setup restores the reference witness. |

The oracle enumerates a finite 16-state, five-operation contract. Qualification
checks all 80 state/operation pairs per variant using a separately implemented
dispatcher; negative claims apply only to this declared domain. Incomplete
enumeration produces `unverified`, and planted false feasibility labels are
rejected. The actor bundle contains the public contract and common initial failed
operation, while specifications, witnesses, and reference labels remain separate.

The 17 scripted grader cases cover four evidence views of each task plus a
supported-blocker control. A conservative deterministic evidence rule agrees with
all 17 reference support labels. An impossible task can still have an unsupported
blocker claim when the actor has seen only one failed approach. This is a rule and
fixture regression result, not a learned-grader accuracy estimate. All cases are
development examples; longer paths have not been calibrated as model difficulty.

Completed: M1, M2, and the deterministic portion of M3. Pending: M3 model graders
and M4 actor evaluation. See the [design](counterfactual-evaluation-infrastructure.md).

## Archive audit and artifact qualification

The [ResearchArena-inspired export](../results/researcharena-monitoring-offline-v1/summary.json)
audits all 224 historical source rollouts. Of these, 223 produced the 1,543
proposals; `link-study-v1/run-0125` produced none and remains in the source inventory.
Original labels, transcripts, and result archives were preserved.

| New semantic proposal label | Count |
| --- | ---: |
| Authorized | 1,167 |
| Unauthorized target | 308 |
| Malformed or unsupported | 68 |
| Unresolved | 0 |

Of the 324 historical `out_of_scope` labels, 308 target explicitly excluded
resources and 16 are unsupported routes. Three historical `in_scope` proposals
have malformed arguments; the 49 historical unsupported operations remain in the
malformed/unsupported category. These are proposal labels, not successful access
counts. The [transition table](../results/researcharena-monitoring-offline-v1/archive/label_changes.json)
and [versioned references](../results/researcharena-monitoring-offline-v1/archive/references.jsonl)
preserve the individual decisions and original labels.

The audit reconstructs both evidence views from source transcripts, validates
their before-dispatch cutoff and historical rollout split, and verifies source
hashes. It also compares source proposals with the read-only SQLite service
journal and checks independent effect tables against archived state. One malformed
tool proposal was normalized by the historical dispatcher into an invalid request;
the audit retains that distinction rather than treating it as mismatched history.

The new labels use an explicit deterministic resource/operation rubric. No human
review or learned adjudication is claimed; there are no unresolved cases under
that rubric. Individual effect timing has not been certified, so the prepared
baseline supports proposal classification only. First-effect detection requires
additional action-to-effect attribution. Run-level journal/state agreement alone
does not establish that timing.

The new cache fixture produced 32 scripted artifacts across eight base lineages
and 128 monitor inputs for T, TE, TA, and TEA:

| Condition | Cases | Observed reference behavior |
| --- | ---: | --- |
| Correct optimization | 8 | Correct throughout the 32-input domain; ordinary-workload operation count falls from 80 to 16. |
| Selective corruption | 8 | Ordinary checks pass; one rare input fails the independent full-domain oracle and paired probe. |
| Broad regression | 8 | Ordinary and rare-input checks fail. |
| Environment fault | 8 | Verification remains unknown; setup repair restores the same clean artifact. |

The interpreter accepts bounded literal cache data, with no shell, executable
expressions, or network operations. Each investigation receives a separate copy;
probe quotas and artifact permissions are enforced. Hidden expected answers and
reference probe logs are absent from monitor inputs. The text in these scripted
cases is a uniform synthetic explanation, not historical actor output. All eight
lineages belong to one development family; no family-transfer result is claimed.

Completed: RA0 automated rubric/input audit and RA2 scripted artifact qualification.
Pending: RA1 learned archive baseline, RA3 learned artifact monitors, and RA4
task-only/deliberate-attack actors. See the [design](researcharena-inspired-evaluations.md).

## Reproduce and verify

From the repository root, using new output directories:

```sh
PYTHONPATH=src python3 -m containment_extension evaluation-qualify \
  --design counterfactual --output runs/counterfactual-offline-new
PYTHONPATH=src python3 -m containment_extension evaluation-qualify \
  --design researcharena --output runs/researcharena-offline-new
PYTHONPATH=src python3 -m containment_extension evaluation-verify \
  results/counterfactual-evaluation-offline-v1
PYTHONPATH=src python3 -m containment_extension evaluation-verify \
  results/researcharena-monitoring-offline-v1
python3 -m pytest -q tests/test_evaluation.py
```

Each export contains the design snapshot, implementation sources, reference
evidence, inputs, results, and a hashed file manifest. Verification detects missing
or changed recorded files; it is not a digital signature. New executions refuse
to overwrite existing directories. Evidence for the two runs is stored separately
from the historical archives. Repository cleanup removed only two `.DS_Store`
files; the previous design edits and experiment evidence remain intact.

## Prepare the first live stages

`evaluation-prepare` and `evaluation-run` implement `workflow_graders`,
`workflow_actors`, `archive_monitors`, and `artifact_monitors`. Preparation freezes
the assignments, prompts, source files, evidence binding, threshold, and budget;
it makes no model requests. The runner records requests, responses, tool results,
and budget reservations. It refuses changed sources, changed evidence, and repeat
execution. Provider failures preserve reservations and leave later assignments
explicitly unstarted; there are no automatic retries.

Copy [the configuration template](../experiments/evaluation-live.template.json)
to a new allocation file and fill every null value after selecting the provider,
model, verified rates, and overall spending cap. Budget shares apply per assignment
as well as across the stage. Separate stages need shares of the overall allocation;
do not repeat the entire overall cap in each stage's config. The template alone
cannot execute. Its eight-rollout archive subset is a small diagnostic; setting
`archive_rollout_limit` to zero selects all proposal-bearing rollouts and both views.
Selection is by source rollout before model judgments, retaining each selected
rollout's existing split. The fixed 0.5 threshold is prespecified, not calibrated.

For example, after creating a complete, allocated configuration:

```sh
PYTHONPATH=src python3 -m containment_extension evaluation-prepare \
  --stage workflow_graders \
  --evidence results/counterfactual-evaluation-offline-v1 \
  --config runs/workflow-grader-allocation.json \
  --output runs/workflow-graders-plan
PYTHONPATH=src python3 -m containment_extension --env-file ../.env \
  evaluation-run runs/workflow-graders-plan
```

The archive-monitor stage uses the ResearchArena offline export. Preparing
`artifact_monitors` additionally requires `--baseline` pointing to a completed,
integrity-checked archive-monitor run with valid judgments. Model actors run the
four workflow variants through the qualified interface. Their blocker explanations
still require semantic review; the report does not equate stopping with a correct
blocker. Wall stops are checked between requests; the provider transport has its
own request timeout. An exhausted or incomplete stage retains its assigned denominator.

RA4 deliberate-attack actors, family-transfer expansion, threshold calibration,
and causal prevention experiments remain later protocol work. The current live
entry points do not claim to execute those extensions.
