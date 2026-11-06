# Matched comparisons

Pooled numbers are exploratory summaries across two models and two feasibility variants.
Early outcomes use strict model-turn ordering. Wilson intervals use observed outcomes only.

| Arm | Assigned | Early | Unknown | 95% Wilson interval | Any outside | Successful upstream reads | Writes |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| visible | 32 | 26 | 0 | 64.7%–91.1% | 29 | 29 | 5 |
| hidden | 32 | 13 | 0 | 25.5%–57.7% | 23 | 16 | 8 |
| visible_reminder | 32 | 0 | 2 | 0.0%–11.4% | 12 | 5 | 4 |
| hidden_reminder | 32 | 0 | 0 | 0.0%–10.7% | 15 | 10 | 8 |

## Primary pooled matched comparisons

| Contrast | Complete pairs | Missing pairs | Risk difference | Exact McNemar p | Holm p |
| --- | ---: | ---: | ---: | ---: | ---: |
| hidden − visible | 32 | 0 | -40.6% | 0.00719738 | 0.00719738 |
| visible_reminder − visible | 30 | 2 | -80.0% | 1.19209e-07 | 2.38419e-07 |

Per-model/variant counts are in report.md; all paired deltas, sensitivity counts,
secondary contrasts, interactions, missingness, and integrity checks are in analysis.json.
Successful-read/write counts are observed effects, not imputed negatives for failed runs.
This design cannot establish training provenance or an internal reasoning mechanism.
