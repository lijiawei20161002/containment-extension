# Counterfactual workflow qualification

Executed October 4, 2026. Four workflow cases, 320 state/action comparisons, and
17 scripted grader cases passed. No model calls or API spending.

Read the [results and reproduction commands](../../docs/evaluation-infrastructure-results.md),
[summary](summary.json), and [manifest](manifest.json). `workflow/actor/` and
`workflow/grader_inputs/` contain evidence views; hidden labels, witnesses, and
qualifications are stored separately. `source/` and `design.json` freeze the
implementation and design used for this run. This README is an explanatory
addition outside the execution manifest.

The deterministic grader result is a regression check, not model performance.
All examples belong to one development family. Model-grader and actor stages
remain unexecuted.
