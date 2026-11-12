"""Build local dashboard documentation from the incident records and analysis.

Run with the dashboard extra installed: python3 scripts/export_dashboard_docs.py
The generated pages require no network connection or Markdown renderer to view.
"""
from __future__ import annotations

import base64
from html import escape
import json
import mimetypes
from pathlib import Path
import re
from urllib.parse import urlsplit

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard"
DOCUMENTS = {
    ROOT / "README.md": "index.html#story",
    ROOT / "incidents/README.md": "incident-library.html",
    ROOT / "docs/incident-library-analysis.md": "cross-case-analysis.html",
}


def render_markdown(source: Path) -> str:
    """Render existing documents and keep every local dependency in the dashboard."""
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = parser.parse(source.read_text())
    for token in tokens:
        for child in token.children or []:
            if child.type == "image":
                image_path = (source.parent / child.attrGet("src")).resolve()
                if not image_path.is_relative_to(ROOT):
                    raise ValueError(f"Image outside repository: {image_path}")
                mime = mimetypes.guess_type(image_path.name)[0]
                if mime not in {"image/png", "image/jpeg", "image/svg+xml"}:
                    raise ValueError(f"Unsupported image: {image_path}")
                encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
                child.attrSet("src", f"data:{mime};base64,{encoded}")
            elif child.type == "link_open":
                href = child.attrGet("href")
                parts = urlsplit(href)
                if not parts.scheme and not parts.netloc and parts.path:
                    path = (source.parent / parts.path).resolve()
                    if path not in DOCUMENTS:
                        raise ValueError(f"No dashboard destination for {href} in {source}")
                    target = DOCUMENTS[path]
                    if parts.fragment:
                        target = target.split("#")[0] + "#" + parts.fragment
                    child.attrSet("href", target)
    for index, token in enumerate(tokens[:-1]):
        if token.type == "heading_open":
            title = tokens[index + 1].content.lower()
            token.attrSet("id", re.sub(r"[^\w]+", "-", title).strip("-"))
    return parser.renderer.render(tokens, parser.options, {})


def page(title: str, body: str, current: str) -> str:
    links = [
        ("index.html#story", "Dashboard"),
        ("incident-library.html", "Incident library"),
        ("cross-case-analysis.html", "Cross-case analysis"),
    ]
    nav = "".join(
        f'<a href="{href}"' + (' aria-current="page"' if href == current else "")
        + f'>{label}</a>' for href, label in links
    )
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · Containment-extension</title>
<link rel="stylesheet" href="documents.css">
</head>
<body><header><nav aria-label="Project">{nav}</nav></header>
<main>{body}</main></body>
</html>
'''


def incident_cards(records: list[dict]) -> str:
    cards = []
    for record in records:
        evidence = record["evidence"]
        source_items = []
        for source in evidence.get("sources", []):
            name = escape(source["name"])
            url = source.get("url") or ""
            if urlsplit(url).scheme in {"https", "http"}:
                name = f'<a href="{escape(url, quote=True)}">{name}</a>'
            else:
                name += ' <span class="muted">(URL not recorded)</span>'
            source_items.append(f"<li>{name}</li>")
        limits = "".join(f"<li>{escape(item)}</li>" for item in evidence.get("limits", []))
        metadata = " · ".join(escape(str(value)) for value in [
            record["id"], record["actor"], record["category"].replace("_", " "),
            "Evidence " + evidence["level"],
            "Review: " + record["provenance"]["review_status"],
        ])
        cards.append(f'''<article class="record" id="{escape(record['id'])}">
<h2>{record['entry_number']}. {escape(record['title'])}</h2>
<p class="muted">{metadata}</p>
<p>{escape(record['summary'])}</p>
<details><summary>Sources, limitations, and original record</summary>
<h3>Recorded sources</h3><ul>{''.join(source_items)}</ul>
<h3>Evidence limits</h3><ul>{limits}</ul>
<details><summary>Full record</summary><pre>{escape(json.dumps(record, indent=2, ensure_ascii=False))}</pre></details>
</details></article>''')
    return "\n".join(cards)


def main():
    records = [json.loads(path.read_text()) for path in (ROOT / "incidents/records").glob("*.json")]
    records.sort(key=lambda record: record["entry_number"])
    design = render_markdown(ROOT / "incidents/README.md")
    body = f'''<h1>Incident library</h1>
<p>{len(records)} public-report records from the project's existing incident library.
The records motivate decisions about continuing, stopping, requesting authority or
resources, and probing for information. Analyst codings remain drafts; the collection
is not a population incident-rate estimate.</p>
<p><a href="cross-case-analysis.html">Read the cross-case analysis and figures →</a></p>
<details class="library-method"><summary>Library documentation and evidence standards</summary>{design}</details>
{incident_cards(records)}'''
    outputs = {
        "incident-library.html": page("Incident library", body, "incident-library.html"),
        "cross-case-analysis.html": page(
            "Cross-case analysis",
            render_markdown(ROOT / "docs/incident-library-analysis.md"),
            "cross-case-analysis.html",
        ),
    }
    for name, content in outputs.items():
        (DASHBOARD / name).write_text(content)
    print(json.dumps({"pages": list(outputs), "records": len(records),
                      "embedded_analysis_figures": outputs["cross-case-analysis.html"].count("data:image/")}))


if __name__ == "__main__":
    main()
