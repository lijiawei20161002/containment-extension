"""Rebuild external-guidance-paper-deck.pdf from the deck source in source/.

    python3 slides/external-guidance-paper-deck/build_pdf.py

The deck is a Slides artifact (https://claude.ai/artifact/3bMWxX3EjaMmTU7kxjTycy).
source/project/ mirrors its files: deck.json (order, typefaces), deck.css (the
shared look) and one slides/<id>.html per slide. Edit those, rerun this script
for the PDF, and republish them to the artifact to update the online deck.

The script joins the slides into one print page (build/deck.html) and prints it
with headless Google Chrome. Fonts load from Google Fonts, so it needs a network
connection. Three things are swapped for print only:

- images: the artifact's /_blob/<id> addresses become the PNGs in source/figures/
- connectors: <x-connector> lines in the diagram become SVG arrows
- the cover's gradient heading: one solid colour per letter, because PDF viewers
  disagree on gradient-filled text
"""
import json
import math
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE / "source"
FIGS = ROOT / "figures"
BUILD = HERE / "build"
PDF = HERE / "external-guidance-paper-deck.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BLOBS = {
    "0fae21a0f60e233613d049b2dacdb745": "featured-workbook.png",  # paper Figure 1
    "639e095abe280a7e228cb3d9ce00d835": "native-bounds.png",  # paper Figure 3
    "13abdf92b82e32e24c67bcbefa77247d": "judge-reliability.png",  # paper Figure 4
}

PRINT_CSS = """@page { size: 1920px 1080px; margin: 0 }
* { margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact }
body { font: 32px/1.2 sans-serif }
body > section { width: 1920px !important; height: 1080px !important; overflow: hidden !important; box-sizing: border-box !important; position: relative; isolation: isolate; break-after: page; page-break-after: always; break-inside: avoid }
aside { display: none !important }
h1 { font-size: 96px; font-weight: 600 } h2 { font-size: 64px; font-weight: 600 } h3 { font-size: 44px; font-weight: 600 }
p, li, h1, h2, h3, td, th { overflow-wrap: break-word; text-wrap: pretty }
table { width: 100%; border-collapse: separate; border-spacing: 0; border: solid #0003; border-width: 2px 0 0 2px }
th, td { padding: .35em .6em; text-align: left; border: solid #0003; border-width: 0 2px 2px 0 }"""

WIRE = "#6F82B0"
GRADIENT = [(0.0, (0x1F, 0x55, 0x94)), (0.6, (0x3B, 0x86, 0xCC)), (1.0, (0x4B, 0x9B, 0xD9))]

connectors = 0


def connector(match):
    """Draw one <x-connector> as an SVG polyline with an arrowhead."""
    global connectors
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', match.group(0)))
    x1, y1, x2, y2 = (float(attrs[k]) for k in ("x1", "y1", "x2", "y2"))
    route = attrs.get("route", "straight")
    if route == "vh":
        points = [(x1, y1), (x1, y2), (x2, y2)]
    elif route == "hv":
        points = [(x1, y1), (x2, y1), (x2, y2)]
    else:
        points = [(x1, y1), (x2, y2)]
    (px, py), (ex, ey) = points[-2], points[-1]
    length = math.hypot(ex - px, ey - py)
    points[-1] = (ex - (ex - px) / length * 10, ey - (ey - py) / length * 10)
    path = " ".join(f"{x:g},{y:g}" for x, y in points)
    connectors += 1
    marker = f"ah{connectors}"
    return (
        '<svg style="position:absolute;left:0;top:0;overflow:visible" width="1664" height="600">'
        f'<defs><marker id="{marker}" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" '
        f'refX="4" refY="7" orient="auto"><path d="M0 0 L14 7 L0 14 Z" fill="{WIRE}"/></marker></defs>'
        f'<polyline points="{path}" fill="none" stroke="{WIRE}" stroke-width="3" '
        f'stroke-linejoin="round" marker-end="url(#{marker})"/></svg>'
    )


def gradient_colour(fraction):
    fraction = max(0.0, min(1.0, fraction))
    for (f0, c0), (f1, c1) in zip(GRADIENT, GRADIENT[1:]):
        if fraction <= f1:
            t = (fraction - f0) / (f1 - f0)
            return "#%02X%02X%02X" % tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))


def letter_width(ch):
    """Rough advance width in ems, enough to place each letter on the gradient."""
    if ch == " ":
        return 0.25
    if ch in "ilj.,":
        return 0.27
    if ch in "ft-r":
        return 0.37
    if ch in "mM":
        return 0.85
    if ch in "wW":
        return 0.78
    if ch.isupper():
        return 0.65
    return 0.56


def gradient_heading(match):
    """Replace the two-line gradient heading with per-letter solid colours."""
    lines = [match.group(1), match.group(2)]
    widths = [sum(letter_width(c) for c in line) for line in lines]
    widest = max(widths)
    out = []
    for line, width in zip(lines, widths):
        x = (widest - width) / 2
        spans = []
        for ch in line:
            colour = gradient_colour((x + letter_width(ch) / 2) / widest)
            spans.append(f'<span style="color:{colour}">{ch}</span>')
            x += letter_width(ch)
        out.append("".join(spans))
    return '<h1 style="padding-bottom:10px">' + "<br>".join(out) + "</h1>"


def main():
    deck = json.loads((ROOT / "project/deck.json").read_text())
    css = (ROOT / "project/deck.css").read_text()
    links = "".join(f'<link rel="stylesheet" href="{face["href"]}">' for face in deck["faces"].values())
    slides = []
    for slide_id in deck["order"]:
        html = (ROOT / f"project/slides/{slide_id}.html").read_text()
        for blob, name in BLOBS.items():
            html = html.replace("/_blob/" + blob, (FIGS / name).as_uri())
        html = re.sub(r'<h1 class="grad">(.*?)<br>(.*?)</h1>', gradient_heading, html)
        slides.append(re.sub(r"<x-connector[^>]*></x-connector>", connector, html))
    BUILD.mkdir(exist_ok=True)
    page = BUILD / "deck.html"
    page.write_text(
        f'<!doctype html><meta charset="utf-8"><title>{deck["title"]}</title>{links}'
        f'<style>{PRINT_CSS}\n{css}</style><body>{"".join(slides)}</body>'
    )
    print(f"{len(slides)} slides, {connectors} connectors -> {page}")
    if not pathlib.Path(CHROME).exists():
        sys.exit(f"Google Chrome not found at {CHROME}; print {page} to PDF by hand.")
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         "--virtual-time-budget=10000", f"--print-to-pdf={PDF}", page.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"wrote {PDF}")


if __name__ == "__main__":
    main()
