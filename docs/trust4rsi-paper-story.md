# Paper story: incidents, decisions, tests, and prior work

Updated 20 October 2026. The [main deck](../slides/trust4rsi-paper-deck/trust4rsi-paper-plan.pdf)
uses short English sentences and editable diagrams. It now has 23 pages. The
24-page technical appendix retains detailed methods and adds operational comparisons.

## Start with the question the incidents raise

The opening is a reported Medicare portal incident: a statistics request was
denied, then unauthorized access followed. Two further reports show a workbook
moving to public hosting after local collaboration failed, and a deployment
using an unsupplied wallet. These are reported incidents, with primary links and
report dates. They are not our model experiments.

The proposed explanation is bounded: a missing route may lead an agent to use a
forbidden substitute. Reachability-based scope assumptions and GET requests that
write to a wiki show why this explanation is incomplete. Do not call every case
an impossible task. Do not infer a causal mechanism or incidence rate from a
selected case collection. The [incident-to-experiment mapping](trust4rsi-incident-to-experiment.md)
separates the reported observations from our interpretations.

## Explain recover versus stop before showing failure counts

The same 503 observation can occur in two different worlds. In one, an allowed
recovery call works. In the other, it reports no available fallback. The initial
scripted histories are byte-identical; the evidence collector checks this.
The setup is labelled as setup, not a prior model choice.

A failed call alone does not justify stopping. The service contract and recovery
response together determine whether an allowed route remains in this closed
fixture. In an open environment, insufficient evidence calls for an incomplete
report or clarification. It does not grant permission to try an excluded resource.

The positive target is concrete: diagnose within scope, recover when possible,
and stop with evidence when no allowed route remains. This is a useful evaluation
problem, not a new safety principle. The logical distinction is between changing
a plan and changing its authorization.

## Follow the motivation with actual traces

Define a run as one attempt, and a flag as its secret code. Show an agent, its
challenge service, a grader, and the excluded prior-run archive. Then show:

1. Two observed controls: recovery and completion, or an unavailable recovery and
   blocker report. Do not claim the latter passed the strict output-format contract.
2. Incident-study run-0001's four actual requests: recovery, catalog, old archive,
   scorer. Display the exact copied and submitted flag values.
3. All 15 historical violations as tiles: 13 passed; two did not. The final task
   score does not evaluate the complete action history.
4. The paired-note diagnostic: 48 actual continuations; 11/16 versus 15/16 on
   impossible inputs, with an interval that includes zero. All eight controls
   per note completed. This is not a confirmed prompt effect.
5. The transcript audit: 26 violations flagged, 16 clean runs cleared, one clean
   run flagged and five null scores. Calibration failed. The actual admin-role
   request illustrates a disagreement about the authorization contract.

Historical, interrupted, and completed cohorts stay separate. The appendix keeps
all intervals, raw-boolean analysis, calibration failures and timing details.

## Give prior work a technical comparison, not a name list

Five main pages compare the operational choices:

- ImpossibleBench already studies stop instructions, abort options, tool access,
  feedback and monitoring. Recover/stop cannot be the novelty claim.
- Its main pass-based shortcut endpoint differs from our all-trajectory resource
  endpoint. The two non-passing violations show the local difference.
- Our six-run upstream attempt is documented in a report, but its raw live archive
  is missing from this checkout. The report records dependency failures and message
  caps. Zero impossible passes cannot be read as successful stopping.
- Anthropic already uses incident resampling and no-in-scope-solution CTFs. Our
  small deterministic service fixture is a narrower empirical setting.
- AgentDojo, SHADE-Arena and CoSec differ in attacker control, side objectives,
  active permissions and observation surfaces. Do not compare their published
  rates against our rates.

The enforcement page contrasts our effect recorder with a proposed pre-dispatch
check and identifies CaMeL's richer runtime mechanism. An endpoint allowlist is
not a CaMeL reproduction. The [research comparison](trust4rsi-related-work.md)
contains the detailed dimensions and sources.

## End with a test that could change the conclusion

Cross recovery availability with explicit archive permission. Keep technical
access constant. If recovery is unavailable but the archive is authorized,
reading it is useful behavior. If neither route is allowed and feasible, stopping
is appropriate. These are expected allowed choices, not invented model outcomes.

Compare fixed instructions, stop/escalate wording, a permission check, and a
broker baseline under the same budgets. Evaluate authorized completion, executed
violations, attempts and premature stopping. Freeze analysis before new calls;
use a second task family for transfer. The later feedback-selection test must
freeze candidate selection before fresh evaluation and accept ties.

The closing claim remains bounded by the measured results. The philosophical
point follows the examples: **Failure changes what is possible. It does not grant
new authority.** No containment guarantee or recursive self-improvement result
has been demonstrated.
