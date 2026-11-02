# Results dashboard

Static page over `data.json`, which `scripts/export_dashboard_data.py` rebuilds from `runs/*-20261031`.

```sh
.venv/bin/python scripts/export_dashboard_data.py --output dashboard/data.json
python3 -m http.server 8765 --directory dashboard   # then open http://localhost:8765
```

Views: incident reduction by arm and model, paired contrasts, evaluation-awareness dials,
INCIDENT-SELECT selections and judge qualification, an episode explorer with full trajectories,
and the archived E1 decision-story results.
