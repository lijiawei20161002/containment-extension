# Improvements from transcript-scanner and monitor-reliability practice

**Written 2026-11-01; updated 2026-11-02.** Prompted by Transect (UK AISI and Meridian Labs,
arXiv:2610.08364, built on Inspect Scout) and by the scanner-reliability research direction
around it. The 2026-11-02 update adds the rater-as-instrument discipline of Cooper, Oesterheld,
Nguyen, Kastner and Perez, *A dataset of rated conceptual arguments* (arXiv:2607.27499): a
within-group weighted pairwise ranking error, an explicit reference ceiling, and a check that
absolute-error metrics are not rewarding score shrinkage. This note records what the
containment-extension project should change; it is not a summary of either work.

**Status 2026-11-02:** steps 1 and 2 of the order of work are implemented in
`src/containment_extension/judge_reliability.py` and documented in the
[judge reliability study](judge-reliability-study.md). The archived-label audit found that
every model fails the same two pre-granted calibration cases with the same "ALTERNATE without
ASK" reason; the repeated-sampling, scored re-judging of the Haiku 4.5 cohort by Haiku 4.5 and Sonnet 4.6 reproduces
that error on 23 of 160 real episodes per judge, with zero misses and (for Sonnet) zero vote split.

## What the 2026-10-31 cohorts already show

- The transcript-only judge failed the 16-case calibration gate in all six finished Claude
  cohorts (Haiku 4.5, Sonnet 4.6, Haiku 5.5, Sonnet 5; decision-algorithms and
  eval-awareness). The journal-augmented judge passed every time. Selection therefore ran on
  two signals, never three, and the planned T-versus-T+J selection contrast was never measured.
- Every episode carries an independent effect journal, so the project has what a scanner study
  usually lacks: a ground truth that does not come from reading the transcript.
- The AgentDojo port shows the same gap in a public benchmark: a blocked attack call still
  appears in the trace, and AgentDojo's trace-based scorer can count it as a success. Progent
  hand-corrected those cases; we record them in the broker journal instead.

## Changes to make

### 1. Treat the judge as a measured instrument, not a gate

- Report judge agreement with the effect journal as a reliability metric on every cohort:
  agreement rate, false alarms, missed incidents, with cluster bootstrap intervals by task
  lineage (the standardized-benchmarks protocol already specifies the bootstrap).
- Replace the single-sample judge call with repeated sampling (k draws per episode) and
  report the vote split. A judge that flips across draws on the same transcript is unreliable
  in a way one draw cannot reveal; the aggregation rule (majority, unanimous, any) becomes an
  explicit design choice with its own operating point.
- Keep the calibration gate, but add the failure analysis: which of the 16 scripted cases each
  view misses, and which real episodes the transcript view mislabels. Today only the pass/fail
  bit is saved (`judge-calibration.json`); save the per-case rationale text as well.
- Add the archived 1,543 paired monitor inputs (`results/incident-monitor-inputs-v1/`) as a
  second calibration population, since the 16 scripted cases are fixture qualification, not
  population calibration.

### 1b. Score the judge the way a rating dataset scores a rater (Cooper et al.)

- Ask the judge for a probability as well as a label, then report a **weighted pairwise
  ranking error inside each lineage**: every pair of episodes from the same environment with
  different incident counts, scored 0 if the judge orders them like the journal, 1 if reversed,
  1/2 on a tie, weighted by the incident-count gap. This separates ordering skill from
  threshold placement, which the agreement rate conflates.
- Report Brier against a constant-prevalence predictor and the mean score on benign versus
  incident items. A judge that shrinks every score toward the prior can look calibrated on
  absolute error while carrying no ranking information; the paper shows this for weak raters.
- Keep the journal-augmented view in every table as the reference ceiling, the way the paper
  reports a second expert's loss against the primary rater. The transcript view's distance
  from that ceiling is the quantity of interest.
- Tabulate errors by fixture cell and arm. The paper hid critique sources from raters because
  source predicted quality; here the analogous confounders are the operation names and the
  presence of an ASK turn, which the archived labels show the transcript judge keys on.
- Do not spend budget on extended thinking for judging; the paper's paired comparison shows
  small, inconsistent gains. Spend it on draws.

### 2. Make every label traceable to its evidence

- Each judge label should cite the transcript turns it relied on. Extend `JUDGE_SCHEMA` with
  a `turns` array and store it; the dashboard's episode explorer can then highlight the cited
  turns next to the journal entries, so a reviewer sees both what the label says and why.
- Record judge disagreement explicitly: journal vs transcript view vs transcript+journal view
  per episode, and surface disagreements as a filter in the episode explorer. Disagreement
  is the review queue, not a nuisance.

### 3. Move the fixture onto Inspect logs

- Port the two-item grant fixture and the AgentDojo adapter to write Inspect `.eval` logs, or
  convert the current JSON episodes with a one-way exporter. The project already pins
  `inspect-ai==0.3.200` for the ImpossibleBench adapter.
- This unlocks three things at once: the Inspect log viewer for review, Transect's timeline
  and behaviour labels as an additional (unvalidated) scanner to compare against the journal,
  and ControlArena compatibility for the later BashArena comparison.
- Define a phase vocabulary for the fixture matching the decision model: initial route fails,
  probe, local recovery, request, substitution, stop. The same vocabulary applies to real
  long-horizon transcripts in the incident library.

### 4. Separate "scanner" from "monitor" in the design

- The effect journal is a monitor (live, per action). The judges are scanners (post hoc).
  GRANT-LOOKAHEAD advice is neither; it is pre-action guidance. The decks currently blur
  these. Each result should say which it is, because reliability questions differ: a monitor
  can be bypassed in the moment, a scanner can be fooled by a well-written transcript.
- Add an "attempted but blocked" field to the native fixture's outcome, mirroring the
  AgentDojo broker journal, so monitors and scanners can be compared on attempts as well as
  committed effects.

### 5. Evaluation awareness as a scanner target

- The audit-notice arms (journal_audited / journal_unaudited) were designed as an actor
  treatment. They are also a scanner test: does a transcript scanner flag the "unaudited"
  episodes as higher risk, and does it do so for the right reason? Run the judges over the
  eval-awareness cohorts with the notice present and stripped, and report the difference.

### 6. Reporting

- Add a judge-reliability panel to the dashboard's selection view: per model and per view,
  agreement, false alarms, misses, vote split under repeated sampling, and the cited turns.
- In papers and decks, never present a scanner label as an incident count. Incident counts
  come from the journal; scanner labels are an estimate with a reported error rate.

## Order of work

1. Per-case calibration rationale and cited turns. **Done 2026-11-02** as a separate scored
   schema (`JUDGE_SCHEMA_V2`) in `judge_reliability.py`; the archived single-draw reasons are
   recovered in `results/judge-reliability-v1/archived-labels.md`.
2. Repeated-sampling judge with vote aggregation over archived episodes. **Done 2026-11-02**
   on the Haiku 4.5 cohort (176 items, 2 views; Haiku 5 draws, Sonnet 4.6 3 draws). Remaining cohorts are a budget decision after the first report.
3. Inspect log exporter for the native fixture and AgentDojo traces.
4. Transect run over the exported logs, compared against the journal; report disagreements.
5. Dashboard judge-reliability panel.
