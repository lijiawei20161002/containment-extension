# Trace audit

Audited 96 completed rollouts.

All source/prompt hashes match; every logged request retains the initial task.
Timing describes executed actions. It does not identify a training cause.

| First executed violation | Rollouts |
| --- | ---: |
| after_dependency_failure | 5 |
| before_any_dependency_failure | 75 |
| no_executed_violation | 16 |

Violations before any challenge-endpoint request: 75.

Counts pool exploratory and validation runs for trace description only,
not for an unbiased treatment-effect estimate.
