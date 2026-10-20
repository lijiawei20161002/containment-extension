# Trust4RSI: a short visual talk and a separate technical appendix

Updated 20 October 2026. [PDF](trust4rsi-paper-plan.pdf) and
[editable PowerPoint](trust4rsi-paper-plan.pptx): **13 main slides**.
[Technical appendix PDF](trust4rsi-technical-appendix.pdf) and
[editable appendix](trust4rsi-technical-appendix.pptx): **20 supporting slides**.

The main deck uses short English sentences, large counts, actual request fields,
and editable diagrams. One page makes one point. There are no main-deck tables.
Main prose is at least 18 pt; raw request text is 16–18 pt. Main pages contain
37–67 words each, including titles and subtitles but excluding source footers.

The first three pages follow one actual run. They show the exact flag read from
the old archive and the same value accepted by the current grader. New extraction
checks assert that these values match. The opening defines “run” and “flag”
before using them. The judge disagreement shows the actual admin-role request.
All observed behavior still comes from hosted-model calls to controlled local
services, not production incidents or invented examples. This revision made
**zero additional API calls**.

## Reading order

| Slides | Content |
| --- | --- |
| 1 | The concrete task and the forbidden resource |
| 2–3 | Four real calls; the same copied flag in the read and submission |
| 4 | Fifteen observed violations as fifteen tiles; thirteen passed |
| 5 | Two real controls: recover successfully or report the blocker |
| 6–7 | Two actual notes, 48 runs, and every impossible input as a square |
| 8–9 | Plain-language judge counts and one actual permission disagreement |
| 10 | Three closest prior-work ideas; clickable primary papers |
| 11–12 | Two unrun tests, explicitly labelled “NOT RUN YET”; no invented winners |
| 13 | Three bounded findings and one plain-language statement about permission |

The appendix carries the dense material: A1–A2 compare research; A3–A9 show
intervals, all pairs, historical counts, calibration failures, raw booleans and
scores; A10–A18 give cohorts, methods, evidence and limits; A19–A20 contain nine
primary references. Null scores, failed calibration and the post-hoc boolean
analysis remain visible there. This split changes presentation, not the results.

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

`collect_evidence.py` reads the live experiment archives and records source
hashes, checks selected observed traces and verifies the historical 160-run cross-tab.
`qa/concrete-evidence.json` and `qa/evidence-index.json` bind the deck to those
results. The main builder also checks word counts, font sizes and absence of tables.
Scripted qualification fixtures remain infrastructure checks in the
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
python3 slides/trust4rsi-paper-deck/build_technical_appendix.py
python3 slides/trust4rsi-paper-deck/render_pdf.py --source slides/trust4rsi-paper-deck/trust4rsi-technical-appendix.pptx --target slides/trust4rsi-paper-deck/trust4rsi-technical-appendix.pdf --qa slides/trust4rsi-paper-deck/qa/appendix-layout-validation.json --title "Trust4RSI technical appendix"
pdftoppm -r 80 -png slides/trust4rsi-paper-deck/trust4rsi-paper-plan.pdf slides/trust4rsi-paper-deck/qa/s
```

These commands reanalyze or render existing data without API calls. Execution
commands are single-use. The renderer checks text overflow and supports native
rectangles, circles, orthogonal arrowheads and the embedded E1 plot. No speaker
notes are added, to avoid the existing Keynote notes-master issue.

To render only the first five main slides:

```sh
python3 slides/trust4rsi-paper-deck/build_deck.py --opening-only
python3 slides/trust4rsi-paper-deck/render_pdf.py --source /tmp/trust4rsi-opening-preview.pptx --target /tmp/trust4rsi-opening-preview.pdf --qa /tmp/trust4rsi-opening-validation.json
```

The existing anonymous E6 ZIP remains an older snapshot. New result directories
are separate repository artifacts; this refresh does not upload the deck or
silently replace the old supplementary archive.
