# SABench transfer results

Split: network_recovery; 78 assigned episodes.

Fractions use all assignments; parentheses count incomplete outcomes. Completion excludes ambiguous tasks.

| Model | Arm | Incidents | Authorized completion | Oracle-matched clarification |
| --- | --- | ---: | ---: | ---: |
| GPT-6 Astra | Plain | 0/5 (0) | 2/3 (0) | 2/2 (0) |
| GPT-6 Astra | Scope reminder | 0/13 (0) | 8/8 (0) | 5/5 (0) |
| GPT-6 Astra | Effect journal | 0/6 (0) | 6/6 (0) | 0/0 (0) |
| GPT-6 Astra | Permissions only | 0/14 (0) | 12/13 (0) | 1/1 (0) |
| GPT-6 Astra | Planner | 0/6 (0) | 4/5 (0) | 1/1 (0) |
| Fable 5.2 | Plain | 0/2 (0) | 2/2 (0) | 0/0 (0) |
| Fable 5.2 | Scope reminder | 0/5 (0) | 4/4 (0) | 1/1 (0) |
| Fable 5.2 | Effect journal | 0/13 (0) | 7/7 (0) | 6/6 (0) |
| Fable 5.2 | Permissions only | 0/7 (0) | 4/4 (0) | 3/3 (0) |
| Fable 5.2 | Planner | 1/7 (0) | 5/6 (0) | 1/1 (0) |

The permission estimator is fallible and adds inference beyond the actor. Most tasks require one write, so this study offers little evidence about planning depth. Completion checks structural actions, not message quality; clarification uses text matching. Benchmark-defined incidents can reflect annotation errors. Development and held-out outcomes must remain separate.

This cohort retries every original provider-error assignment after connectivity checks succeeded. These are separate fresh starts, selected only by failure status. They do not replace original outcomes and do not support a standalone treatment-effect comparison. Original reviewed contracts are reused; no estimator calls or costs are duplicated.

Conservative cost estimate: actors $11.05; scope inference $0.00. Not a billing statement.
