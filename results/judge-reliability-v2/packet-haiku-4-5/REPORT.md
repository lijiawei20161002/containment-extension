# Judge reliability study: judge-reliability-v2-packet-haiku-4-5

Status: finished; judge model claude-haiku-4-5-20251001; 3 draws per item and view; 176/176 items judged.

Reference labels are the fixture's independent effect journal. Agreement is reported per draw and after aggregating draws; intervals are cluster bootstraps over lineages (environments).

## View: transcript

### development (160 items, 3 incidents)

| Rule | Agreement | False alarm rate | Miss rate | Abstain |
| --- | ---: | ---: | ---: | ---: |
| per draw | 99.8% | 0.2% | 0.0% | 1 |
| majority | 100.0% [100–100] | 0.0% [0–0] | 0.0% [0–0] | 0 |
| unanimous | 100.0% [100–100] | 0.0% [0–0] | 0.0% [0–0] | 0 |
| any | 99.4% [98–100] | 0.6% [0–2] | 0.0% [0–0] | 0 |

Vote split: 1/160 items had draws disagreeing on the label (0.6%).
Pairwise ranking error (within lineage, severity-weighted): 0.0% [0–0] over 3 informative lineages; AUROC 100.0% [100–100].
Brier 0.001 versus constant-prevalence baseline 0.018; mean score on benign items 0.3%, on incident items 97.6%.
Correct majority flags citing the first incident turn: 2/3.

### calibration (16 items, 6 incidents)

| Rule | Agreement | False alarm rate | Miss rate | Abstain |
| --- | ---: | ---: | ---: | ---: |
| per draw | 100.0% | 0.0% | 0.0% | 0 |
| majority | 100.0% [100–100] | 0.0% [0–0] | 0.0% [0–0] | 0 |
| unanimous | 100.0% [100–100] | 0.0% [0–0] | 0.0% [0–0] | 0 |
| any | 100.0% [100–100] | 0.0% [0–0] | 0.0% [0–0] | 0 |

Vote split: 0/16 items had draws disagreeing on the label (0.0%).
Pairwise ranking error (within lineage, severity-weighted): – over 0 informative lineages; AUROC 100.0% [100–100].
Brier 0.0 versus constant-prevalence baseline 0.234; mean score on benign items 0.0%, on incident items 96.9%.
Correct majority flags citing the first incident turn: 2/6.

### all (176 items, 9 incidents)

| Rule | Agreement | False alarm rate | Miss rate | Abstain |
| --- | ---: | ---: | ---: | ---: |
| per draw | 99.8% | 0.2% | 0.0% | 1 |
| majority | 100.0% [100–100] | 0.0% [0–0] | 0.0% [0–0] | 0 |
| unanimous | 100.0% [100–100] | 0.0% [0–0] | 0.0% [0–0] | 0 |
| any | 99.4% [98–100] | 0.6% [0–2] | 0.0% [0–0] | 0 |

Vote split: 1/176 items had draws disagreeing on the label (0.6%).
Pairwise ranking error (within lineage, severity-weighted): 0.0% over 3 informative lineages; AUROC 100.0% [100–100].
Brier 0.001 versus constant-prevalence baseline 0.049; mean score on benign items 0.2%, on incident items 97.1%.
Correct majority flags citing the first incident turn: 4/9.

Cross-view majority disagreements: 0.

Estimated API usage: $0.779142; 528 requests. Not an invoice.

Limitations:
- Episodes come from one two-item control structure; reliability here does not transfer to long-horizon transcripts.
- Transcript judges in this fixture see the same trusted task text as the journal judge; the journal adds the authorized flag per effect, which is near-decisive.
- Draw counts are small; vote-split estimates are coarse.
- Judges are the same model family as the actors; no human rater ceiling is measured.
