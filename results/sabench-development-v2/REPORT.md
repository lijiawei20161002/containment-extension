# SABench transfer results

Split: development; 32 assigned episodes.

Fractions use all assignments; parentheses count incomplete outcomes. Completion excludes ambiguous tasks.

| Model | Arm | Incidents | Authorized completion | Oracle-matched clarification |
| --- | --- | ---: | ---: | ---: |
| GPT-6 Astra | Planner | 1/16 (0) | 10/12 (0) | 3/4 (0) |
| Fable 5.2 | Planner | 1/16 (0) | 12/12 (0) | 4/4 (0) |

Primary comparisons are planner versus plain; development contrasts are exploratory.

| Model | Planner − plain (percentage points) | Template-clustered 95% interval | Holm p | Complete pairs |
| --- | ---: | --- | ---: | ---: |
| GPT-6 Astra | — | — | — | 0/0 |
| Fable 5.2 | — | — | — | 0/0 |

These intervals resample whole templates. The p-values use exact paired template sign-flips; only the two primary comparisons receive Holm correction.


The permission estimator is fallible and adds inference beyond the actor. Most tasks require one write, so this study offers little evidence about planning depth. Completion checks structural actions, not message quality; clarification uses text matching. Benchmark-defined incidents can reflect annotation errors. Development and held-out outcomes must remain separate.

Conservative cost estimate: actors $5.04; scope inference $2.98. Not a billing statement.
