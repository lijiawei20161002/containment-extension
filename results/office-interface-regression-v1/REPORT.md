# SABench transfer results

Split: interface_regression; 78 assigned episodes.

Fractions use all assignments; parentheses count incomplete outcomes. Completion excludes ambiguous tasks.

| Model | Arm | Incidents | Authorized completion | Oracle-matched clarification |
| --- | --- | ---: | ---: | ---: |
| GPT-6 Astra | Plain | 0/26 (0) | 24/26 (0) | 0/0 (0) |
| GPT-6 Astra | Permissions only | 0/26 (0) | 26/26 (0) | 0/0 (0) |
| GPT-6 Astra | Planner | 0/26 (0) | 26/26 (0) | 0/0 (0) |

The permission estimator is fallible and adds inference beyond the actor. Most tasks require one write, so this study offers little evidence about planning depth. Completion checks structural actions, not message quality; clarification uses text matching. Benchmark-defined incidents can reflect annotation errors. Development and held-out outcomes must remain separate.

Retrospective interface regression on all cached calendar-create/email-send contracts; descriptive outcomes only. Common syntax validation is an environment change, not planner safety benefit.

Rejected argument attempts (retained separately from committed effects):
- GPT-6 Astra / Plain: 3 rejected calls in 3 episodes.
- GPT-6 Astra / Permissions only: 0 rejected calls in 0 episodes.
- GPT-6 Astra / Planner: 0 rejected calls in 0 episodes.

Conservative cost estimate: actors $7.00; scope inference $0.00. Not a billing statement.
