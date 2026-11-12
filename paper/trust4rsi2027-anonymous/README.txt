External Feedback for Scope-Respecting Agent Decisions
Anonymous AAAI 2027 workshop manuscript

RUNTIME PLACEMENT AND REPOSITORY ARTIFACT - 9 NOVEMBER 2026
Moves the runtime-interface diagram into the algorithms discussion, now
Figure 2 on page 4, adjacent to Algorithm 1 on page 3. The incident diagram
now appears first as Figure 1 on page 2. Rewrites Appendix G around the
containment-extension code repository: implementations, configurations,
runners, tests, dashboard, saved-data analyses, and evidence availability.
Removes the Overleaf-project description from the paper. This ZIP remains
manuscript source; the research artifact is the code repository. The main
text remains eight pages; all experimental data and figures are unchanged.

CHALLENGE FRAMING AND NEW FIGURE 7 - 9 NOVEMBER 2026
Reframes the abstract around the challenge of maintaining useful task progress
while respecting delegated authority. Aligns the introduction with that
problem, the four policy choices, proactive/reactive feedback, and the three
empirical questions. Replaces the repeated workbook diagram in Figure 7 with
library entry 20, the UK AISI social-engineering and attempted software-
compromise incident. Figure 2 remains the detailed workbook example. Figures
6 and 7 still share page 20; the main text ends on page 8. Results are unchanged.

DETAILED FIGURE 2 UPDATE - 9 NOVEMBER 2026
Replaces the compact three-card Figure 2 with the same detailed diagram
format used by Figures 6 and 7: grouped agent/service panels, numbered arrows,
a blocked local path, an incident timeline, evidence notes, and a legend.
Keeps the source-supported uploader verification and marks the policy choices
as proposed alternatives. Moves the full experimental setup into Appendix A,
with a concise main-text summary, to retain eight main-text pages. Figures 6
and 7 still share page 20. Data, results, and the abstract are unchanged.

FRAMING AND FIGURE UPDATE - 9 NOVEMBER 2026
States the four policy choices and three empirical questions in the abstract
and introduction. Adds a compact vector adaptation of the workbook-sharing
incident as main-text Figure 2, with an explicit link to recovery, probing,
permission requests, and stopping. The full library diagrams are retained.
Fixes the judge legend's clipped outline and separates the right-column
headers (formerly Figure 3, now Figure 4). Reduces vertical whitespace in
both library diagrams and places them in one float (formerly Figures 5/6,
now Figures 6/7). Moves the longer engineering-review discussion to the
engineering appendix and condenses repeated background to retain eight main
pages. Experimental data and results are unchanged; no new inference was run.

ABSTRACT UPDATE - 9 NOVEMBER 2026
Reframes the abstract from recent incidents to the agent decision-policy
problem, grant-constrained planning and effect feedback, and proposed
engineering integration. Removes the final incident-prevention disclaimer
from the abstract. The manuscript body and experimental results are unchanged.

REVISION 8 - 9 NOVEMBER 2026
Opens the abstract with one sentence naming the motivating incidents. Redraws
the judge-reliability matrix (Figure 3) in the archived YES/NO badge style and
the incident pathway diagram (Figure 4) as matching cards. Adds the complete
26-record motivating incident library to the appendix as two tables (facts and
dates; draft codings) generated from data/incident_library.csv, plus two
library diagrams (entries 14 and 15) rendered as vector figures from their
stored specifications. Experimental outcomes, result tables, and the native
and workflow figures are unchanged. No new inference was run.

REVISION 7 - 9 NOVEMBER 2026
Broadens the abstract to recent agent incidents generally. OpenAI/Hugging Face
remains one example in the introduction. Adds contextual-integrity and
incentive-theory references to connect social norms, institutional authority,
accountability, and completion incentives to the engineering problem.

Restores the original runtime-interface diagram as Figure 1 in the main paper.
Adds Algorithm 1: a memoized grant-constrained planner and the combined
actor/dispatch/effect-journal loop, including independent broker behavior and
preservation of recorded effects on unresolved continuations. The incident
pathway diagram and extended conceptual discussion are retained in appendices.
Original experimental outcomes, result tables, and figures are unchanged.
No new inference was run. Inspect/CRUX integration remains proposed future work.

The first-page submission notice is suppressed with the template's
nocopyright command at the user's request. Anonymous submission mode remains
active, and the supplied style files themselves have not been edited.

Uses the exact, unmodified aaai2027.sty and aaai2027.bst from the supplied
AuthorKit27.zip. The archive and template hashes are in data/provenance.json.
The PDF has eight pages of main text and twenty pages including references
and appendices. The main text ends on page 8. All author information is anonymous.

OVERLEAF
1. Choose New Project > Upload Project and upload this ZIP.
2. Select main.tex as the main document if it is not selected automatically.
3. Use pdfLaTeX with a recent TeX Live version (2024 or newer).
4. Recompile. All tables, figures, references, and official style files are included.

The submission option is enabled in main.tex. The author field is anonymous;
there are no affiliations, acknowledgments, personal repository links, or local
workspace paths. The official aaai2027.sty and aaai2027.bst are unmodified.
Their internal upstream credits belong to the template, not this manuscript.

TARGET
Trust4RSI-Agent @ AAAI 2027
https://trust4rsi-agent.github.io/AAAI2027/
Checked 9 November 2026: anonymous English submissions, AAAI 2027 format,
full papers up to 8 pages, references/appendices usually excluded, single PDF.
Submission deadline: 20 November 2026, Anywhere on Earth.
The ZIP is the editable Overleaf project. Submit the compiled PDF to the venue.

BUILD LOCALLY
LC_ALL=C LANG=C latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

REPRODUCE THE ANALYSIS
python3 analysis/summarize.py
python3 analysis/figures.py
python3 analysis/judge_analysis.py
python3 analysis/incident_tables.py
python3 analysis/context_figures.py

The summarize, judge_analysis, and incident_tables scripts use only Python's
standard library. The two figure scripts require matplotlib. Neither makes model calls or network requests. Rebuilding figures
is optional for LaTeX compilation because the vector PDFs are included.

CONTENTS
main.tex                  Complete anonymous manuscript, references and appendix
references.bib            Bibliography; primary research sources
aaai2027.sty / .bst        Official AAAI 2027 author-kit files
figures/                  Seven vector PDF figures; featured incident is Figure 1, runtime diagram Figure 2
algorithms/combined.tex   Formal planner and effect-journal pseudocode
tables/                   Automatically generated LaTeX tables
data/episodes.csv         1,352 recorded development/native episodes
data/cohorts.csv          Ten cohort allocations and frozen-plan hashes
data/advice_transitions.csv  Delivered advice followed by a tool operation
data/action_traces.json   Minimal action traces without model prose
data/summary.json         Counts and exploratory paired contrasts
data/provenance.json      Extraction checks and author-kit provenance
data/DICTIONARY.txt       Endpoint definitions and missing-value semantics
data/judge_items.csv      1,584 case/configuration rows across nine configurations
data/judge_draws.csv      5,456 draw records; labels only, no provider payloads
data/judge_conditions.csv Judge inputs, model labels, stage, and draw allocation
data/judge_summary.json   Recomputed monitor error counts
data/judge_provenance.json Frozen report/plan/source/draw hashes and overlap notes
data/figure_provenance.json Source figure hashes and adaptation details
data/incident_library.csv  26 motivating public-report records (facts and draft codings)
data/incident_specs/       Figure specifications for the two redrawn library diagrams
analysis/                 Deterministic table/figure generation

EVIDENCE SCOPE
The manuscript reports retained experiments; no new inference was run.
Main comparisons use completed cohorts. Two interrupted cohorts are inventoried
separately; historical selectively assigned follow-up episodes are excluded
from actor arm comparisons. The judge diagnostic corpus separately reuses
128 development actor episodes and 32 historical selected-test episodes, plus
16 scripted cases. Repeated judgments are not additional actor trials. The
journal-assisted judge sees reference authorization information; its agreement
is not independent verification. Follow-ups are diagnostic, not held-out tests.
Journal effects differ by model and incentive. Zero observed planner incidents
is not zero risk. Native repeat effects are unmeasured. Audit notices test cue
sensitivity, not private beliefs. Completion and unknown outcomes are explicit.

This package reproduces the descriptive analysis from anonymous derived data.
It is not the complete model-serving harness or a claim that the experiment can
be replayed identically against changing provider APIs. Full provider payloads
and identifying repository links are intentionally omitted.
