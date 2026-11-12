# SABench transfer results

Split: development; 96 assigned episodes.

Fractions use all assignments; parentheses count incomplete outcomes. Completion excludes ambiguous tasks.

| Model | Arm | Incidents | Authorized completion | Oracle-matched clarification |
| --- | --- | ---: | ---: | ---: |
| GPT-6 Astra | Plain | 2/16 (0) | 10/12 (0) | 2/4 (0) |
| GPT-6 Astra | Scope reminder | 1/16 (0) | 10/12 (0) | 3/4 (0) |
| GPT-6 Astra | Planner | 2/16 (0) | 10/12 (0) | 2/4 (0) |
| Fable 5.2 | Plain | 2/16 (0) | 11/12 (0) | 4/4 (0) |
| Fable 5.2 | Scope reminder | 1/16 (0) | 10/12 (0) | 4/4 (0) |
| Fable 5.2 | Planner | 2/16 (0) | 12/12 (0) | 4/4 (0) |

Primary comparisons are planner versus plain; development contrasts are exploratory.

| Model | Planner − plain (percentage points) | Template-clustered 95% interval | Holm p | Complete pairs |
| --- | ---: | --- | ---: | ---: |
| GPT-6 Astra | 0.00 | [0.00, 0.00] | 1.0000 | 16/16 |
| Fable 5.2 | 0.00 | [-18.75, 18.75] | 1.0000 | 16/16 |

These intervals resample whole templates. The p-values use exact paired template sign-flips; only the two primary comparisons receive Holm correction.

GPT-6 Astra: the all-assignment difference ranges from 0.00 to 0.00 percentage points under all possible missing outcomes. This is a missing-data bound, not a confidence interval.
Fable 5.2: the all-assignment difference ranges from 0.00 to 0.00 percentage points under all possible missing outcomes. This is a missing-data bound, not a confidence interval.

The permission estimator is fallible and adds inference beyond the actor. Most tasks require one write, so this study offers little evidence about planning depth. Completion checks structural actions, not message quality; clarification uses text matching. Benchmark-defined incidents can reflect annotation errors. Development and held-out outcomes must remain separate.

Conservative cost estimate: actors $15.97; scope inference $1.48. Not a billing statement.
