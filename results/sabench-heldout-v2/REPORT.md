# SABench transfer results

Split: heldout; 1320 assigned episodes.

Fractions use all assignments; parentheses count incomplete outcomes. Completion excludes ambiguous tasks.

| Model | Arm | Incidents | Authorized completion | Oracle-matched clarification |
| --- | --- | ---: | ---: | ---: |
| GPT-6 Astra | Plain | 11/132 (5) | 74/104 (3) | 25/28 (2) |
| GPT-6 Astra | Scope reminder | 8/132 (13) | 76/104 (8) | 22/28 (5) |
| GPT-6 Astra | Effect journal | 15/132 (6) | 74/104 (6) | 27/28 (0) |
| GPT-6 Astra | Permissions only | 4/132 (14) | 74/104 (13) | 27/28 (1) |
| GPT-6 Astra | Planner | 4/132 (6) | 82/104 (5) | 27/28 (1) |
| Fable 5.2 | Plain | 8/132 (2) | 86/104 (2) | 28/28 (0) |
| Fable 5.2 | Scope reminder | 6/132 (5) | 88/104 (4) | 27/28 (1) |
| Fable 5.2 | Effect journal | 6/132 (12) | 89/104 (6) | 22/28 (6) |
| Fable 5.2 | Permissions only | 8/132 (7) | 85/104 (4) | 25/28 (3) |
| Fable 5.2 | Planner | 7/132 (7) | 84/104 (6) | 27/28 (1) |

Primary comparisons are planner versus plain; development contrasts are exploratory.

| Model | Planner − plain (percentage points) | Template-clustered 95% interval | Holm p | Complete pairs |
| --- | ---: | --- | ---: | ---: |
| GPT-6 Astra | -5.79 | [-13.60, 0.79] | 0.5000 | 121/132 |
| Fable 5.2 | -0.81 | [-8.87, 4.76] | 1.0000 | 123/132 |

These intervals resample whole templates. The p-values use exact paired template sign-flips; only the two primary comparisons receive Holm correction.

GPT-6 Astra: the all-assignment difference ranges from -9.09 to -0.76 percentage points under all possible missing outcomes. This is a missing-data bound, not a confidence interval.
Fable 5.2: the all-assignment difference ranges from -2.27 to 4.55 percentage points under all possible missing outcomes. This is a missing-data bound, not a confidence interval.

The permission estimator is fallible and adds inference beyond the actor. Most tasks require one write, so this study offers little evidence about planning depth. Completion checks structural actions, not message quality; clarification uses text matching. Benchmark-defined incidents can reflect annotation errors. Development and held-out outcomes must remain separate.

Conservative cost estimate: actors $279.12; scope inference $24.83. Not a billing statement.
