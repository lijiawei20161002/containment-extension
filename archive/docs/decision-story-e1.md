# Containment decision story: first E1 execution

Completed 26 October 2026 from slides 11–13 and 20 in
`slides/containment-decision-story/`. The frozen specification is
[`experiments/decision-story-e1-v1.json`](../experiments/decision-story-e1-v1.json).

The [72-response archive](../results/decision-story-e1-v1/README.md) contains the
raw results, exact scores and figure. First choices were optimal in 49/72 cases;
complete contingent policies were optimal in 23/72. Mean policy regret was
1.68955 utility units. Estimated inference cost was $0.0169764. This diagnostic
motivates testing explicit planning assistance; it does not measure incidents.

This first stage elicits one contingent policy for each of 72 parameter cells
from `gpt-4.1-mini-2025-04-14`. It measures the one-probe decision model before
extending the service fixtures. It is not the complete E1 experiment, an
interactive agent rollout, or an authorization-violation evaluation.

## Model and allocation

Hidden local feasibility is Bernoulli(p). Recovery pays 10 on success and 0
on failure, less cost 2 either way. Stopping pays zero. Asking costs d and
receives an independent trusted grant with probability q; a grant includes
successful authorized completion with reward 10 and no additional cost.
Denial stops with no reward. One permitted probe costs c and reports feasibility
with symmetric accuracy a; it is followed by one terminal action. No sampled
hidden feasibility or reference answer is sent to the model.

The elicited JSON includes the initial action, both contingent terminal choices,
and prior/posterior feasibility probabilities. The exact evaluator integrates
over both observations, so it evaluates the whole stated contingent policy,
including a wrong branch choice after an initially optimal probe.

| Sweep | Cells | Fixed values otherwise |
| --- | ---: | --- |
| p × d phase diagram | 48 | 12 priors × costs 0, 2, 6, 8; q=.6, c=.5, a=1 |
| Grant probability q | 7 | p=.3, d=2, c=.5, a=1 |
| Probe cost c | 9 | p=.3, d=2, q=.6, a=1; includes c=1.2 tie |
| Diagnostic accuracy a | 7 | p=.3, d=2, q=.6, c=.5 |
| Upper phase boundary | 1 | p=11/12, d=2, q=.6, c=.5, a=1 |

The schedule is shuffled once with seed 20261026. Temperature is zero, with one
response per cell and at most 512 output tokens each. The total ceiling is 72
requests, 250,000 input tokens, 36,864 output tokens and $1 estimated usage.
Pricing is $0.40/$1.60 per million input/output tokens, checked against the
[official model page](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
on 26 October. Cached inputs are conservatively charged at the full input rate.
Costs are estimates, not provider invoices.

The source snapshot, prompts, parser, schema, assignment list and analysis rules
are frozen before inference. There are no retries or model substitutions. A
provider error, missing usage, incomplete response or exhausted budget stops the
cohort; all unobserved or invalid assignments remain unknown. Existing execution
directories cannot be restarted or overwritten.

## Qualification and endpoints

The 891-cell local phase grid is an exact reference. All 72 assigned cases are
checked against exhaustive enumeration of the three direct terminal policies
and nine probe-contingent policies. Tests independently check the slide's 4.7
example, analytic ties, Bayes updates, uninformative diagnostics, unknown-outcome
handling, accounting and a fully scripted 72-response run.

Report first-choice agreement against all optimal ties, exact expected policy
regret, choices by parameter sweep, and prior/posterior expected Brier scores.
Excess Brier score subtracts the irreducible Bernoulli uncertainty. These are
probability-elicitation scores in a known simulator, not evidence of calibration
in deployment. Grid cells are neither independent task lineages nor a powered
confirmatory cohort. All available actions are permitted by construction, so
this stage supplies no behavioral safety or executed-violation rate.

## Reproduction

```sh
python3 scripts/run_decision_story.py prepare --output runs/e1-new
python3 scripts/run_decision_story.py run --output runs/e1-new --env-file ../.env
python3 scripts/plot_decision_story.py runs/e1-new
```

On this Mac, Python's default CA bundle was missing. Passing `--ca-file` with
the installed certifi `cacert.pem` path fixed TLS verification; certificate
verification remains enabled. `.env` values are never sourced, printed or
included in evidence. The OpenAI smoke test passed authenticated model listing
and actual generation before the experimental cohort.

Later E1 stages still need horizon/budget sweeps, kernel misspecification,
Monte Carlo planning and an unfiltered planning baseline. E2 still needs the
paired authorization/recovery service fixtures, independent task lineages and
seven qualified arms. E3 needs the repaired judge, candidate policies and
disjoint development/test allocations. This first cohort cannot stand in for
those experiments.
