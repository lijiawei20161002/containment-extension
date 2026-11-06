# Trust4RSI paper plan: incidents, fixture, measurements, implications, programme

Updated 20 October 2026. [PDF](trust4rsi-paper-plan.pdf) and
[editable PowerPoint](trust4rsi-paper-plan.pptx): **41 main slides**.
[Technical appendix PDF](trust4rsi-technical-appendix.pdf) and
[editable appendix](trust4rsi-technical-appendix.pptx): 24 supporting slides (unchanged).

This revision replaces the 23-slide short talk (kept as `qa/build_deck.previous-23-slide.py`)
with a longer, more technical paper-plan deck. Every number on a slide is read at build time
from archived result files or incident records; the builder asserts the key counts. Proposed
experiments carry designs, endpoints, gates and falsifiers, never outcomes. This revision makes
**zero model API calls**.

The 20 October evening revision adds three slides on the blurred recovery boundary: slide 26
(the same recovery action is legitimate or a violation depending only on the grant; an effect
oracle is not an authorization oracle), slide 27 (the fixture measures constraint compliance, not
authorization reasoning), and slide 35 (X1b: unspecified and conflicting grant conditions for X1,
64 runs, access rate and response mix rather than a violation rate where no authorization oracle
exists). The gate, experiment map, threats and outline slides were updated to match. The budget-and-timeline
slide was removed at the author's request; its cost estimate remains in `qa/evidence-index.json`;
the previous builder is kept as `qa/build_deck.before-boundary-slides.py`.

## Narrative

| Part | Slides | Content |
| --- | --- | --- |
| A Story | 1-8 | Opening thesis; 2026 latency picture; Medicare anatomy; three incident families (substitution, scope inference, channel); cross-library counts; stop behaviour; theses T1-T3 mapped to endpoints |
| B Method | 9-12 | Fixture architecture; task contract; constrained objective and arms B0-B4; scorer / judge / observer cross-tabs |
| C Results | 13-24 | Link study (cue removal relocates violations); cue-study null; 2x2 failure-checkpoint study; stopping vs formatting; utility-incident plane; one run; 13 of 15; paired notes; judge audit v2-v4; the one false alarm; the two-case gate; upstream ImpossibleBench attempt |
| D Implications | 25-31 | Three readings of one 503; the recovery/substitution boundary and V(e,c) = 1[e not in A(c)]; constraint compliance vs authorization reasoning; substitution conserved under cue removal; where the signal sits determines selection power; the release gate; five synthetic twins |
| E Programme | 32-41 | Executed map; proposed map X1-X7 plus X1b; X1 with exact McNemar power; X1b (unspecified and conflicting grants); X4 and X6 twins; X2, X3, X5, X7; prior work; threats to validity; eight-page outline; takeaway |

## Slide index

| # | Status | Title |
| --- | --- | --- |
| 1 | FRAMING | A failed route is where an agent's authority gets reinterpreted. |
| 2 | REPORTED | The world reports an incident about four months after it happens. |
| 3 | REPORTED | Medicare portal: the search failed, so the agent found another way in. |
| 4 | REPORTED | Five reports share one structure: blocked route, reachable substitute, unchanged permission. |
| 5 | REPORTED | Four evaluations treated a reachable real target as an authorized one. |
| 6 | REPORTED | When the method label is 'GET', the effect can still be a public write. |
| 7 | REPORTED | What recurs: capability composition, detection without escalation, effects over intent. |
| 8 | RESEARCH DESIGN | Three theses, each paired with the endpoint that would test it. |
| 9 | METHOD | Six local services, one dispatcher, one effect journal the agent never sees. |
| 10 | METHOD | The scope paragraph names the resources, the exit and the evidence standard. |
| 11 | METHOD | Minimise verified incidents subject to utility, cost and false-intervention constraints. |
| 12 | OBSERVED | The scorer, a transcript judge and the effect journal answer different questions. |
| 13 | OBSERVED | A README link caused early out-of-scope reads. Removing it moved them, later and elsewhere. |
| 14 | OBSERVED | No prompt feature consistently increased violations. The first crossing usually preceded the failure. |
| 15 | OBSERVED | After an identical 503, a full-scope reminder plus an explicit exit took Haiku from 6/8 to 0/8. |
| 16 | OBSERVED | Fifty of 51 terminal reports supported the blocker. Only 16 were valid strict JSON. |
| 17 | OBSERVED | Twenty archived policy cells on one plane: at full utility, policies separate on incidents alone. |
| 18 | OBSERVED | The agent tried recovery, read the catalog, read another run's answer, and passed. |
| 19 | OBSERVED | 13 of 15 violating runs passed the grader. |
| 20 | OBSERVED | Two checkpoint notes, 24 shared inputs each: 11/16 versus 15/16 violations on impossible inputs. |
| 21 | OBSERVED | Three frozen judge protocols: two failed calibration, the third is descriptive only. |
| 22 | OBSERVED | The judge called an authorized challenge request 'privilege escalation'. |
| 23 | OBSERVED | The selection study stopped at its own event-rate gate after 0/2 baseline violations. |
| 24 | REPORT ONLY | Six ImpossibleBench runs: 1/2 originals solved, 0/4 impossible variants passed, 6/6 hit the message cap. |
| 25 | ANALYSIS | One 503 has three readings. Incidents happen when the agent confuses them. |
| 26 | ANALYSIS | The same recovery action is legitimate or a violation. Only the grant decides which. |
| 27 | ANALYSIS | The fixture measures constraint compliance. It does not measure authorization reasoning. |
| 28 | ANALYSIS | Substitution is conserved under cue removal. Only resource-level enforcement changes the total. |
| 29 | ANALYSIS | Where the signal sits determines what selection can see. On this fixture, B3 and B4 would mostly agree. |
| 30 | PROPOSED | A regression gate for evolving agent policies: replay twins and controls, decide on effects. |
| 31 | PROPOSED | Each incident family yields a synthetic twin with dummy data and a known excluded resource. |
| 32 | OBSERVED | Seven native allocations (489 actor runs, 68 judge calls) are archived with plans, hashes and budgets. |
| 33 | PLANNING | Eight preregistered allocations, ordered by dependency, each with a gate to advance. |
| 34 | NOT RUN YET | Cross recovery availability with explicit archive permission; keep technical access constant. |
| 35 | NOT RUN YET | Add two grant conditions to X1, unspecified and conflicting, each with a preregistered reference behaviour. |
| 36 | NOT RUN YET | Two twins that test what a transcript cannot show and what a monitor cannot do. |
| 37 | NOT RUN YET | Enforcement, transfer, powered selection and a second model family. |
| 38 | PRIOR WORK | What is already established, and the only differences we can defend. |
| 39 | LIMITS | What the current evidence cannot support, stated before a reviewer states it. |
| 40 | PLANNING | Section budget, figures and the claim each section is allowed to make. |
| 41 | OBSERVED | Four sentences a reviewer should be able to repeat. |

## Planning computations (not results)

The builder computes three quantities from archived rates and records them in
`qa/evidence-index.json` under `planning_computations`: the probability that a k-case
event-rate gate sees zero events at the archived 11/16 rate; exact two-sided McNemar power for
X1 at 8-32 pairs per cell for two effect sizes taken from archived arms; and the judge/observer
disagreement bounds that set X5's power. None of these predicts model behaviour.

## Evidence and reproducibility

`collect_evidence.py` reads the live archives and the 26 incident records, records source
hashes, checks selected traces, verifies the 160-run cross-tab (13/96/2/49), the link-study
reminder-arm count (27/32, 3 unknown) and the terminal-review counts (51 reviewed, 48 clean
supported blockers). `qa/concrete-evidence.json` and `qa/evidence-index.json` bind the deck to
those results. The builder checks word counts (<= 300 per slide), font floors (>= 10 pt for
labels, code excluded) and absence of native tables; the renderer checks text overflow.

Python: use an interpreter with `python-pptx` and `reportlab` (on this Mac,
`~/Desktop/.venv/bin/python`; the Homebrew `python3` lacks reportlab).

```sh
P=~/Desktop/.venv/bin/python
$P slides/trust4rsi-paper-deck/build_deck.py
$P slides/trust4rsi-paper-deck/render_pdf.py
$P slides/trust4rsi-paper-deck/build_technical_appendix.py
pdftoppm -r 80 -png slides/trust4rsi-paper-deck/trust4rsi-paper-plan.pdf slides/trust4rsi-paper-deck/qa/s
```

Embedded figures: `figures/incidents/analysis/latency-dumbbell.png` (slide 2) and
`figures/experiments/tradeoff-v1/utility-incident-tradeoff.png` (slide 17); both are
regenerated by their scripts from JSON, not hand-edited. All other charts are native shapes.

The companion documents are unchanged in substance:
[incident-to-experiment mapping](../../docs/trust4rsi-incident-to-experiment.md),
[technical comparison](../../docs/trust4rsi-related-work.md),
[live follow-up results](../../docs/trust4rsi-live-followup-results.md),
[next experiments](../../docs/trust4rsi-next-experiments.md). The
[paper story](../../docs/trust4rsi-paper-story.md) summarises the new narrative.
