# E1 one-probe pilot, 26 October 2026

Completed 72/72 responses from `gpt-4.1-mini-2025-04-14`, with no unknown outcomes.
49/72 first actions were optimal (all ties accepted), but only 23/72 complete
contingent policies were optimal. Mean policy regret was 1.68955 utility units.
26 responses had an optimal first action and a suboptimal continuation.

At the slide example p=.3, d=2, q=.6, c=.5, the model chose PROBE, then RECOVER
on a positive observation and STOP on a negative observation. Its expected
utility was 1.9, versus 4.7 for the optimal policy that asks after a negative
observation. This is a concrete motivation to test explicit planning support.

Usage: 30,609 input and 2,958 output tokens; estimated $0.0169764 (full uncached
input rates), excluding the separate 14-token smoke check. No retries or
substitutions. Source, plan, prompts, reservations and raw responses are saved.
21 focused tests passed. Raw response usage sums reconcile with the ledger.

[Methods](../../docs/decision-story-e1.md) · [Report](report.json) ·
[Per-case data](per-case.csv) · [Figure](figures/e1-first-stage.png)

This is one prompt and one elicited policy per synthetic parameter cell, not
an incident-rate study, an independent-lineage test, or the complete two-algorithm
study. No real systems or external effect destinations were exposed.
