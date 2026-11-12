# Prospective recovery-planning results

Author-constructed synthetic workflows with known transitions and trusted grants. These are separate from SABench and do not establish performance on real services.

Parentheses count incomplete outcomes. Completion excludes impossible tasks, if present.

| Model | Guidance | Incidents | Authorized completion | Mean resource excess on success |
| --- | --- | ---: | ---: | ---: |
| GPT-6 Astra | Permissions only | 0/32 (2) | 28/30 (2) | 0.00 |
| GPT-6 Astra | Greedy advice | 0/32 (2) | 28/30 (2) | 0.00 |
| GPT-6 Astra | Verified planner | 0/32 (1) | 29/30 (1) | 0.00 |
| Fable 5.2 | Permissions only | 0/32 (12) | 18/30 (12) | 0.00 |
| Fable 5.2 | Greedy advice | 0/32 (7) | 23/30 (7) | 0.00 |
| Fable 5.2 | Verified planner | 0/32 (10) | 21/30 (9) | 0.00 |

Primary comparisons: planner minus permissions-only authorized completion.

| Model | Difference (pp) | Family bootstrap 95% interval | Holm p | Known pairs |
| --- | ---: | --- | ---: | ---: |
| GPT-6 Astra | 0.00 | [0.00, 0.00] | 1.0000 | 27/30 |
| Fable 5.2 | 0.00 | [0.00, 0.00] | 1.0000 | 12/30 |

All eight related generator families were fixed before inference. No allocation extension or favorable subset selection. Zero observed incidents are not a guarantee. Search assumes correct public transitions and permissions; actor behavior remains advisory, not enforced.

Conservative list-price estimate: $118.33; 1908 model requests. Not a billing statement.

Exploratory efficiency on task pairs that both arms complete safely:

| Model | Paired successes | Planner / permissions output tokens | Planner / permissions estimated API cost |
| --- | ---: | ---: | ---: |
| GPT-6 Astra | 27 | 0.919 | 1.136 |
| Fable 5.2 | 12 | 0.923 | 1.102 |
