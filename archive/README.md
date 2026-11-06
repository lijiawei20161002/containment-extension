# Archived research assets

Archived 6 November 2026 to focus the [active project](../README.md) on reported
incidents, decisions about continuing/stopping/requesting/probing, Grant
Look-ahead, Effect Journal, and the three empirical questions.

These assets retain their historical content. Archiving marks their role in the
project, not their validity. No raw evidence or frozen source snapshot was edited
during relocation. Existing presentations are historical references; the
[active README](../README.md) is the current narrative.

| Location | Preserved material |
| --- | --- |
| [docs/](docs/) | Earlier benchmark, optimization, judge, coordination, and games narratives |
| [slides/](slides/) | Previous presentations, editable sources, PDFs, and layout checks |
| [figures/](figures/) | Previous experimental plots and architecture illustrations |
| [experiments/](experiments/) | Configurations for retired study directions |
| [scripts/](scripts/) and [tests/](tests/) | Their runners, analyses, and regression tests |
| [results/](results/) | Recorded historical results, manifests, and source snapshots |
| `runs/` | Local historical cohorts; remains ignored by Git |
| [dashboard/](dashboard/index.html) | Original dashboard plus judge and games pages/data |
| [previous-main/](previous-main/) | Original README, handoff, methods, and other edited entry points |
| [artifacts/](artifacts/) | Previous paper supplement |
| `output/`, `tmp/` | Existing local exports and working files, preserved and ignored by Git |
| [requirements/](requirements/) | Retired benchmark environment requirements |

## Finding and restoring an asset

[manifest.json](manifest.json) records every move and copy, original and archived
paths, SHA-256 checksums, file sizes, and whether each file was tracked at the time
of reorganization. All copied and moved files were hash-checked after relocation.

For a moved asset, its old repository-relative path is normally now under
`archive/` with the same suffix. Originals of rewritten main files are under
`archive/previous-main/`; the previous dashboard is under `archive/dashboard/`.
Nothing was deleted. The manifest includes local-only files that may not exist
in a fresh clone.

Verify the preserved files with `python3 archive/verify.py`. In a fresh clone,
use `python3 archive/verify.py --tracked-only` to omit originally local-only files.
The [reorganization checks](reorganization-checks.json) record the retained test
suite, offline runner checks, link checks, and dashboard validation.

Frozen evidence can contain historical relative or absolute paths. Those strings
and checksums were deliberately preserved. Use the relocation manifest to find
the files. Archived scripts, tests, and deck builders may need their original
layout restored into a separate checkout before running; they are not maintained
as active entry points. Do not overwrite current assets when restoring a copy.

The original dashboard can be viewed by serving the repository root and opening
`/archive/dashboard/`. Historical configurations and notes do not authorize new
model calls or resumption of completed experiments.
