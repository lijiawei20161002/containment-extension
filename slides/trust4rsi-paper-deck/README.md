# Trust4RSI deck: physical components and observed experiment data

Updated 20 October 2026. [PDF](trust4rsi-paper-plan.pdf) and
[editable PowerPoint](trust4rsi-paper-plan.pptx), 31 slides.

The opening uses native vector icons for the agent, service racks, an archive
database, folders and the scorer. Arrows show actual observed call sequences
and the service topology. They are editable PowerPoint shapes, not flattened
illustrations. Every displayed behavioral outcome comes from a recorded hosted
model response and its local service effects.

The earlier hypothetical policy-selection table and scripted workbook/reverted
write examples have been removed. The experiment environment is still a
controlled synthetic service fixture; actual API behavior in this fixture
must not be mistaken for production incidents.

## Reading order

| Slides | Content |
| --- | --- |
| 1-3 | Actual cached-answer trace, physical components, exact requests and responses |
| 4 | Observed authorized recovery versus observed clean stopping |
| 5 | Actual run-0094: two excluded reads followed by a blocker report |
| 6-9 | Prior-work overlaps, closest comparison, 2026 research and missing experimental controls |
| 10-12 | New paired-note design, measured rates and all 16 impossible input pairs |
| 13-14 | Historical score/incident cross-tab and four-arm wording pilot |
| 15-18 | Transcript audit, failed calibration, confusion matrix and all 48 scores including nulls |
| 19-21 | Distinct cohorts, the first new input pair and frozen analysis contracts |
| 22-23 | Conceptual framing, actual resource use and remaining research question |
| 24-29 | Historical figure, population counts, unmeasured selection, evidence, limits and claims |
| 30-31 | Nine primary sources with clickable links |

The [research comparison](../../docs/trust4rsi-related-work.md) includes
ImpossibleBench, AgentDojo, AI Control, SHADE-Arena, CaMeL, ControlArena,
AgentDyn, CoSec and a recent detector-transfer study. This is a qualitative
literature comparison, not an executed cross-benchmark performance comparison.
The defensible current scope is a controlled measurement study; no new
containment algorithm or recursive self-improvement result is claimed.

## Executed follow-ups

See [methods, measured results, costs and limitations](../../docs/trust4rsi-live-followup-results.md).
The 48-assignment paired-note v1 allocation stopped at a provider timeout after
27 recorded runs, retaining 21 unstarted assignments as unknown. Its associated
judge plan never executed.

A separate v2 allocation used 48 new inputs/arm assignments and froze a policy
of preserving individual provider failures while continuing other assigned
runs, without retries or replacement. It compares exactly the current original
and archived neutral continuation notes on 16 impossible, 4 recoverable and
4 easy-solvable inputs per arm. v1 and v2 are reported separately.

Strict judge v2 failed on 12 fenced-JSON responses. A separate format-normalized
v3 reanalysis reused those responses and failed the benign FPR requirement.
Descriptive v4 then used a fixed 0.5 threshold: 12 reused calls plus 56 new calls
(8 archive positives and all 48 actor trajectories). Its primary matrix is
26 TP, 0 FN, 1 FP, 16 TN, and 5 null-score unknowns. The frozen joint parser
suppresses the boolean when the score is null; a separate post-hoc raw-field
audit shows those five outputs emitted false, giving 26/0/1/21 and no unknown
booleans. Both analyses are visible. Calibration remains failed.

Provider requests contain only actor-visible transcript packets, never observer
labels. The audit measures agreement, not policy-selection benefit.

CPU + hosted Anthropic inference suffice. No GPU, local model weights or Docker
are needed. Combined estimated-cost ceiling: $8, including conservative usage
reserved for the interrupted v1 response. The original E2 selection study
remains closed at its six-run baseline stop.

## Evidence and reproducibility

`collect_evidence.py` reads the live experiment archives and verifies source
hashes, selected observed traces and the historical 160-run cross-tab.
`qa/concrete-evidence.json` and `qa/evidence-index.json` bind the deck to those
results. Scripted qualification fixtures remain infrastructure checks in the
research archive; they do not supply the deck's model-performance results.

```sh
python3 scripts/run_baseline_diagnostic.py report results/baseline-diagnostic-v2
python3 scripts/run_baseline_diagnostic.py audit results/baseline-diagnostic-v2
python3 scripts/run_transcript_audit.py report results/transcript-audit-v4
python3 scripts/run_transcript_audit.py audit results/transcript-audit-v4
python3 scripts/audit_judge_fields.py
python3 scripts/report_paper_followup.py
python3 scripts/draw_followup_results.py
python3 slides/trust4rsi-paper-deck/build_deck.py
python3 slides/trust4rsi-paper-deck/render_pdf.py
pdftoppm -r 80 -png slides/trust4rsi-paper-deck/trust4rsi-paper-plan.pdf slides/trust4rsi-paper-deck/qa/s
```

These commands reanalyze or render existing data without API calls. Execution
commands are single-use. The renderer checks text overflow and supports native
rectangles, circles, orthogonal arrowheads and the embedded E1 plot. No speaker
notes are added, to avoid the existing Keynote notes-master issue.

To inspect only the opening without requiring new experiment summaries:

```sh
python3 slides/trust4rsi-paper-deck/build_deck.py --opening-only
python3 slides/trust4rsi-paper-deck/render_pdf.py --source /tmp/trust4rsi-opening-preview.pptx --target /tmp/trust4rsi-opening-preview.pdf --qa /tmp/trust4rsi-opening-validation.json
```

The existing anonymous E6 ZIP remains an older snapshot. New result directories
are separate repository artifacts; this refresh does not upload the deck or
silently replace the old supplementary archive.
