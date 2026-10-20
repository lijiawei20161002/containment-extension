# Paper plan deck: containment-extension -> Trust4RSI-Agent (AAAI 2027)

`trust4rsi-paper-plan.pptx` / `.pdf` (16 slides, built 20 Oct 2026) plans how to
turn this repository into a full paper for the AAAI 2027 Workshop on Trustworthy
Evolution of AI Agents ("An Agent Operating System Perspective",
https://trust4rsi-agent.github.io/AAAI2027/; 8 pages, double-blind, OpenReview,
deadline 20 Nov 2026 AoE).

Slides 1-8 map repository components to the workshop's five topics, state the
claim and non-claims, give an eight-page outline, and collect the archived
evidence. Slides 9-13 list the experiments with a status tag on each:

| Tag | Meaning |
|---|---|
| DONE | archived evidence, reuse as-is |
| BUILD | implement, CPU only, no model calls |
| RUN | implement and run with live inference; frozen plan and approved ceiling first |
| HUMAN | analyst work (second-reader codings) |
| LATER | declared as future work only |

Required: E1 (archived-data trade-off figure), E2 (matched proxy-vs-incident
selection on the native fixture, the one live experiment), E5 (second-reader
incident codings), E6 (anonymized artifact). Optional: E3 (second model family),
E4 (regression gate through incident twins). Slides 14-16 cover the negative
result, the 31-day timeline and fallbacks.

Every count in the deck is copied from `docs/*-results.md` and `results/*/README.md`;
the deck makes no new measurement and no model call.

## Experiment execution (20 October 2026)

See [implementation, results and reproduction commands](../../docs/trust4rsi-experiments.md).
E1 is generated. E2 is implemented and its live baseline stopped at the frozen
zero-event gate: 0/2 impossible-task incidents, 4/4 controls completed in scope,
estimated cost $0.052442. The selection contrast remains unmeasured. E5's blind
worksheet and agreement tools are ready for an independent human reader; E6's
local anonymized supplement is built. Optional E3/E4 remain deferred. No GPU is
required for this plan.

## Rebuild

```sh
python3 slides/trust4rsi-paper-deck/build_deck.py          # needs python-pptx
python3 slides/trust4rsi-paper-deck/render_pdf.py          # needs python-pptx + reportlab, macOS Arial
pdftoppm -r 60 -png slides/trust4rsi-paper-deck/trust4rsi-paper-plan.pdf slides/trust4rsi-paper-deck/qa/s
```

`render_pdf.py` reuses the renderer in `../incident-library-deck/` and fails on
text overflow, writing `qa/layout-validation.json`. No speaker notes are written,
so Keynote can open the PPTX.
