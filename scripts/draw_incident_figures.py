"""Build public-incident case-study figures into figures/incidents/.

Usage: python3 scripts/draw_incident_figures.py [slug-or-number ...]
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from incident_figure_lib import build  # noqa: E402
from incident_figure_specs import SPECS  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "figures" / "incidents"

if __name__ == "__main__":
    sel = set(sys.argv[1:])
    for spec in SPECS:
        if sel and spec["slug"] not in sel and str(spec["n"]) not in sel:
            continue
        print(build(spec, OUT))
