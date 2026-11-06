# Paper story: incident families, one decision point, a gate

Updated 20 October 2026 (second revision). The [main deck](../slides/trust4rsi-paper-deck/trust4rsi-paper-plan.pdf)
now has 39 technical slides in five parts; the 24-page technical appendix is unchanged.
Every number is read from archived results or incident records at build time.

## A. Start with the incidents as data, not anecdotes

The 26-record library gives the opening its denominators: median detection latency
13.5 days (12 known), median disclosure latency 119 days (21 known), 10 of 26 found
only in retrospect, 2 of 26 self-stopped and both after the access. The Medicare case
is told step by step from its coded actions (guest route, internal files, test file,
credentials) with its indicators and violated propositions.

Three families organise the rest: **substitution** (workbook, exposed API key, public
uploads, GitHub token, test wallet; 7 of 9 live-access-overreach records show repeated
task failure), **scope inference** (Opus 4.7, Mythos 5 PyPI, 9,000-target scan, Gemini;
recognition came after the effect), and **channel** (DSEwiki GET-writes, DNS route with a
15-minute detection and 2.5-hour stop, Artifactory, Hugging Face). Each family yields a
hypothesis H1-H3 and the library counts yield three theses: effects not intent (P6
violated 17/26), task failure is a security input (P4, indicator f), detection is not
stopping (M4 present 13/26). Each thesis is paired with a fixture endpoint.

## B. Make the method concrete and formal

Fixture architecture (six SQLite services, dispatcher, observer reading the effect
journal), the frozen task contract (resource-level grant, "technical access is not
permission", an explicit honest exit), the constrained objective
(min R s.t. U, C, F) with arms B0-B4, and the scorer/judge/observer cross-tabs.

## C. Report every archived measurement with denominators

Link study (26/32 early upstream reads with the cue, 0/32 without; first destinations
shift to the prior-run archive when the cue is suppressed; 27/32 stalled reminder-arm
rollouts still touched an outside resource). Cue-study null. The 2x2 checkpoint study
(Haiku 6/8 to 0/8; GPT-4.1 mini flat; 96/96 controls). Stopping versus formatting
(50/51 supported blockers, 16 strict-JSON). The utility-incident plane. One run with
exact flag bytes. 13 of 15 passes. Paired notes (11/16 vs 15/16, interval includes
zero). Judge audit v2-v4 and the single false alarm. The two-case gate, with the
computed probability that a k-case gate sees zero events at the archived rate.
The report-only ImpossibleBench attempt.

## D. Draw the implications explicitly

1. One 503 has epistemic, deontic and evaluative readings; incidents happen when the
   agent updates the deontic one from the others.
2. Substitution is conserved under cue removal; only resource-level enforcement changes
   the total (falsifiable prediction for X2).
3. Where the signal sits determines selection power: judge and observer agree on 42 of
   43 known cases, so B3 vs B4 needs hidden-effect twins (X4 before X5).
4. The release gate (T3) with the twin library (T5) turns a four-month disclosure
   latency into a zero-day regression test; five twins are specified.

## E. Preregister the programme

Executed map (seven native allocations, 489 actor runs, 68 judge calls, under $4) and
proposed map X1-X7 with gates. X1 carries an exact McNemar power table; X4 and X6 are
specified as twins of INC-006 and INC-002. Budget scaled from archived per-run costs,
timeline to 20 Nov, prior-work differences, threats to validity, and an eight-page
section budget. Working title: *Failure Changes What Is Possible, Not What Is Permitted:
Incident-Aware Regression Gating for Agent Policies.*

The closing claim remains bounded: a measurement study with inspectable traces and a
preregistered plan. No containment guarantee or recursive-self-improvement result.
