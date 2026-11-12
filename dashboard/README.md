# External feedback results dashboard

The dashboard follows the [project story](../README.md): incidents motivate
decisions about continuing, stopping, requesting, and probing; Grant Look-ahead
provides proactive guidance and Effect Journal provides reactive feedback.

Its views are **Story**, **1. Following feedback**, **2. Incident reduction**,
**3. Evaluation awareness**, and **Method**. Following feedback exposes the
recorded sequence for inspection; it is not an aggregate causal adherence score.
Incident views retain authorized completion and missing outcomes. Awareness views
compare evaluation cues rather than claiming to observe private beliefs.

From the repository root:

```sh
python3 -m http.server 8765
```

Open `http://localhost:8765/dashboard/`. The checked-in `data.json` is sufficient
for viewing. Rebuild it from the retained local evidence without model calls:

```sh
python3 scripts/export_dashboard_data.py --output dashboard/data.json
```

The Story view opens local `incident-library.html` and `cross-case-analysis.html`
pages. The library includes all 26 records, their recorded sources and evidence
limits, and the library documentation. The analysis includes its six figures.
These pages work when only `dashboard/` is served at `http://localhost:8765/`
and when the repository is served at `http://localhost:8765/dashboard/`.
They need no GitHub access or network connection; analysis figures are embedded.

After changing the source records or analysis, rebuild the local pages with the
`dashboard` optional dependency installed (`python3 -m pip install -e '.[dashboard]'`):

```sh
python3 scripts/export_dashboard_docs.py
```

Viewing the generated HTML requires only the static server, without Python
Markdown dependencies.

The exporter includes workflow, native recovery, and evaluation-awareness
cohorts. It preserves interrupted cohorts for inspection. Historical selection,
judge, E1, AgentDojo, and boundary-game views are preserved in the
[archived dashboard](../archive/dashboard/index.html).
