# Scripted ImpossibleBench development qualification

September 21, 2026. **No model inference or API spending.**

The [review](../../docs/impossiblebench-development-review.md) explains selection,
mutation conflicts, expected failures, and limitations. Both selected issues
passed all local controls. The repository suite passed 120 tests, including
the Docker + Inspect integration, with no failures/errors/skips.

- `manifest.json`: checkout, source/bundle hashes, counts, and SHA-256 hashes of
  the evidence files. The checkout is the parent commit; `source/` contains the
  exact adapter implementation used with the qualification changes.
- `bundle.json`, `catalog.json`: frozen task triples and the full dataset inventory.
- `host-preflight.json`, `image-preflight.json`: measured Linux resources and
  immutable task images. Containers use the unchanged two-CPU/2-GiB limits.
- `qualification.json.gz`: complete reference/empty scores and observer evidence
  for all six task variants, including final snapshots and test output.
- `lifecycle-report.json`, `lifecycle.tar.gz`: 12 scripted actor controls and their
  full per-run assignments, messages, results, and transcripts. Six apply the
  legitimate reference patch through the actor shell; six edit/revert a protected
  test, exit, and propose a later command that must remain undispatched.
- `check_development_lifecycle.py`: the exact lifecycle-control script. It reads
  the development bundle/qualification from `runs/`, refuses to reuse its output
  directory, and calls the runner directly with scripted actions.
- `linux-tests.xml`, `linux-dependencies.txt`: JUnit output and the Linux Python
  3.12.14 dependency snapshot. The SymPy task's own test suite has one unrelated
  NumPy skip and one expected mpmath failure; these are described in the review.

Inspect the compressed qualification without changing it:

```sh
gzip -dc results/impossiblebench-dev-qualification-v1/qualification.json.gz | less
tar -tzf results/impossiblebench-dev-qualification-v1/lifecycle.tar.gz
```

The lifecycle agent reports zero token usage and never constructs a provider
client. Its synthetic inference-budget bookkeeping is not API usage. These
controls must not be analyzed as autonomous model behavior or intervention
effects. Archived qualification is bound to the source and bundle hashes; any
adapter change requires fresh qualification before inference.
