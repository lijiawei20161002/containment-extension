# One incident to executable policy

The 12-slide `incident-library.pptx` / `incident-library.pdf` follows only
**INC-2026-015, public hosting used to share a local workbook**, through the
reported incident, library record, versioned policy, enforcement, replay, and
regression checks. The survey deck, `incident-library-survey.pptx` / `.pdf` (built by
`build_survey_deck.py`, 69 slides), contains the 26 case figures, the library
design, the cross-case analysis and the implementation plan, plus the same
worked example as its section E, restyled with the survey's helpers.

Keynote stalls on PPTX files that carry a notes master, so `build_survey_deck.py`
keeps speaker notes out of the file unless `SURVEY_NOTES=1` is set; export the
survey with `osascript export_pdf.applescript <pptx> <pdf>` (allow a few minutes).

The incident account comes from the existing **draft** record; its primary
source URL and raw agent logs are absent. The replay is an implemented,
synthetic mechanism analogue, not a verified reconstruction. IDs, routes,
tool calls, and workbook bytes are invented. All effects are in memory;
there are no network requests or model calls.

## Run and rebuild

From the repository root:

```sh
PYTHONPATH=src python3 -m containment_extension.workbook_policy \
  --output slides/incident-library-deck/demo-results.json
python3 -m pytest tests/test_workbook_policy.py -q
python3 slides/incident-library-deck/build_deck.py
python3 slides/incident-library-deck/render_pdf.py
```

The CLI uses the Python standard library. The deck requires `python-pptx`;
the PDF renderer requires `reportlab` and macOS Arial/Menlo fonts;
the tests require `pytest` and `pydantic` (for source-record consistency).
The builder reruns the replay, checks its expectations, refreshes the JSON
traces, and embeds the real policy function and observed results into the deck.
The local vector PDF renderer reads those same PPTX elements, rejects unsupported
objects, and writes a text-overflow check to `qa/layout-validation.json`. It supports
the text, tables and simple shapes used in this deck; it is not a general PPTX converter.

Alternatively, on macOS, export the PPTX with Keynote (requires GUI automation permission;
Keynote could not open the presentation during this session, so the delivered PDF uses
the local renderer):

```sh
osascript slides/incident-library-deck/export_pdf.applescript \
  "$PWD/slides/incident-library-deck/incident-library.pptx" \
  "$PWD/slides/incident-library-deck/incident-library.pdf"
```

## What the implementation demonstrates

| Run | Public copies | Local deliveries | Terminal state |
|---|---:|---:|---|
| Unsafe proposal, policy bypassed | 1 | 0 | blocked |
| Same proposals, policy enforced | 0 | 0 | blocked |
| Benign local delivery, policy enforced | 0 | 1 | completed |

The unsafe sequence is held fixed: check peer access, propose export, report
blocked. A later blocked exit never erases a previously published object.
The benign case checks local delivery; it does not repair collaboration.
These are deterministic fixture outcomes, not measured agent behavior rates.

The trusted harness owns the manifest, run identity, principal and artifact
classification. The broker checks exact structured operations and destination
IDs before dispatch. It denies unknown fields, resources, operations and routes,
and records the action, decision, reason, dispatch flag and before/after state
hashes. The observer counts objects in the effect stores separately from the
approval decision. State hashes are diagnostics, not tamper-proof audit storage.

This is a closed tool-surface demonstration. It does not contain an agent that
can run arbitrary Python, shell commands or sockets; such a deployment needs
mediation of all I/O paths and independent OS/network containment.

## Files

- [Library record](../../incidents/records/15-public-hosting-local-workbook.json):
  factual account, codings, evidence limits and executable pointers.
- [Case bundle](../../incidents/executable/INC-2026-015/case.json): assumptions,
  policy path, unsafe and benign fixtures.
- [Policy manifest](../../incidents/executable/INC-2026-015/policy.json).
- [Broker and replay runner](../../src/containment_extension/workbook_policy.py).
- [Boundary tests](../../tests/test_workbook_policy.py).
- [Full replay results](demo-results.json).

The executable pointers also live in `scripts/incident_codings.py`, so a
library rebuild preserves them; the DuckDB raw record contains the same links.
