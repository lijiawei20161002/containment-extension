# Prospective recovery-planning results

Author-constructed synthetic workflows with known transitions and trusted grants. These are separate from SABench and do not establish performance on real services.

Parentheses count incomplete outcomes. Completion excludes impossible tasks, if present.

| Model | Guidance | Incidents | Authorized completion | Mean resource excess on success |
| --- | --- | ---: | ---: | ---: |
| GPT-6 Astra | Permissions only | 0/24 (0) | 24/24 (0) | 0.33 |
| GPT-6 Astra | Verified planner | 0/24 (0) | 24/24 (0) | 0.00 |
| Fable 5.2 | Permissions only | 0/24 (24) | 0/24 (24) | — |
| Fable 5.2 | Verified planner | 0/24 (24) | 0/24 (24) | — |

Exploratory comparisons: planner minus permissions-only authorized completion.

| Model | Difference (pp) | Family bootstrap 95% interval | Holm p | Known pairs |
| --- | ---: | --- | ---: | ---: |
| GPT-6 Astra | 0.00 | [0.00, 0.00] | 1.0000 | 24/24 |
| Fable 5.2 | — | — | — | 0/24 |

This fixed scaling grid was designed after observing ceiling performance in the original recovery comparison. Size strata share the same generator. All comparisons are exploratory. No allocation extension or favorable subset selection. Zero observed incidents are not a guarantee. Search assumes correct public transitions and permissions; actor behavior remains advisory, not enforced.

Conservative list-price estimate: $63.44; 432 model requests. Not a billing statement.

Exploratory efficiency on task pairs that both arms complete safely:

| Model | Paired successes | Planner / permissions output tokens | Planner / permissions estimated API cost |
| --- | ---: | ---: | ---: |
| GPT-6 Astra | 24 | 0.550 | 0.998 |
