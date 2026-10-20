# Trust4RSI: incidents, decisions, and controlled experiments

Updated 20 October 2026. [PDF](trust4rsi-paper-plan.pdf) and
[editable PowerPoint](trust4rsi-paper-plan.pptx): **23 main slides**.
[Technical appendix PDF](trust4rsi-technical-appendix.pdf) and
[editable appendix](trust4rsi-technical-appendix.pptx): **24 supporting slides**.

Short English sentences, editable diagrams, and explicit evidence labels.
Reported incidents, local experimental results, literature comparisons and
unrun proposals are distinct. Primary sources are clickable. Main prose is
at least 18 pt. The builder checks density and preserves actual request fields.
This revision makes **zero additional model API calls**.

## Reading order

| Slides | Content |
| --- | --- |
| 1–3 | Medicare, workbook, wallet, scope assumptions, and GET writes |
| 4–5 | What incidents tell us to test; why an error alone does not justify stopping |
| 6–7 | Concrete task; two observed recovery/stopping controls |
| 8–10 | Actual forbidden read, identical copied flag, and 13 passing violations |
| 11–14 | Paired notes, measured uncertainty, judge audit and actual disagreement |
| 15–19 | ImpossibleBench mechanisms and labels, our upstream attempt, Anthropic incident tests, other threat models |
| 20 | Effect recording versus runtime enforcement; CaMeL and the allowlist baseline |
| 21–22 | Repair × permission design; later feedback-selection comparison, both unrun |
| 23 | Bounded findings and delegated authority |

A1–A20 retain the original detailed results and references. A21–A24 add incident
coverage, operational comparison, fair-baseline requirements and precise next-test
outcomes. The six-run upstream baseline is **report-only** in this checkout:
its referenced raw live archive is absent. Preparation logs are not live evidence.

The [incident-to-experiment mapping](../../docs/trust4rsi-incident-to-experiment.md)
explains what each case motivates, what our fixture covers, and what it does not.
The [technical comparison](../../docs/trust4rsi-related-work.md) explicitly credits
ImpossibleBench and Anthropic for already studying stopping and tasks with no
in-scope solution. No new containment algorithm or established novelty is claimed.

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
results. The main builder also checks word counts, font sizes and absence of native tables.
`research-sources.json` records the checked primary sources. The collector also
checks identical recovery prefixes and records the upstream archive limitation.
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
