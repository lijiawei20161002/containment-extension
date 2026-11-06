"""Render decision-theory.pptx to vector PDF.

Reuses ../trust4rsi-paper-deck/render_pdf.py (which in turn reuses the incident-library
renderer) and adds one thing the deck needs: run-level sub/superscripts, stored in the
PPTX as the ``baseline`` attribute and emitted to reportlab as <sub>/<super>.

Build:   ~/Desktop/.venv/bin/python slides/decision-theory-deck/build_deck.py
Render:  ~/Desktop/.venv/bin/python slides/decision-theory-deck/render_deck_pdf.py
"""
from __future__ import annotations

import importlib.util
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = HERE.parent / "trust4rsi-paper-deck"

spec = importlib.util.spec_from_file_location("trust4rsi_render_pdf", SHARED / "render_pdf.py")
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)
base = tr.base

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.platypus import Paragraph, Preformatted  # noqa: E402

pt, color, font_name = base.pt, base.color, base.font_name


def render_text(canvas, frame, x, y, width, height, label, issues):
    """Copy of the base renderer's text path plus <sub>/<super> from the run baseline."""
    left, right = pt(frame.margin_left), pt(frame.margin_right)
    top, bottom = pt(frame.margin_top), pt(frame.margin_bottom)
    available = width - left - right
    blocks = []
    for paragraph in frame.paragraphs:
        if not paragraph.runs:
            continue
        sizes = [pt(run.font.size) if run.font.size else 14 for run in paragraph.runs]
        size = max(sizes)
        spacing = paragraph.line_spacing or 1.1
        leading = size * spacing if isinstance(spacing, float) else pt(spacing)
        if not leading:
            leading = size * 1.1
        align = {PP_ALIGN.LEFT: 0, PP_ALIGN.CENTER: 1, PP_ALIGN.RIGHT: 2}.get(paragraph.alignment, 0)
        style = ParagraphStyle(label, fontName=font_name(paragraph.runs[0].font),
                               fontSize=size, leading=leading, alignment=align)
        if all(run.font.name == "Menlo" for run in paragraph.runs):
            text_ = paragraph.text
            measured = pdfmetrics.stringWidth(text_, "Menlo", size)
            if measured > available + .5:
                issues.append(f"{label}: code width {measured:.1f} > {available:.1f}: {text_[:65]}")
            block = Preformatted(text_ or " ", style)
        else:
            spans = []
            for run, run_size in zip(paragraph.runs, sizes, strict=True):
                c = color(run.font.color).hexval().replace("0x", "#")
                body = escape(run.text).replace("\v", "<br/>")
                baseline = int(run.font._element.get("baseline") or 0)
                if baseline < 0:
                    body = f"<sub>{body}</sub>"
                elif baseline > 0:
                    body = f"<super>{body}</super>"
                spans.append(f'<font name="{font_name(run.font)}" size="{run_size}" color="{c}">'
                             + body + "</font>")
            block = Paragraph("".join(spans), style)
        _, block_height = block.wrap(available, 10000)
        before = pt(paragraph.space_before) if paragraph.space_before else 0
        after = pt(paragraph.space_after) if paragraph.space_after else 0
        blocks.append((block, block_height, before, after))
    used = sum(h + before + after for _, h, before, after in blocks)
    room = height - top - bottom
    if used > room + .5:
        issues.append(f"{label}: text height {used:.1f} > {room:.1f}: {frame.text[:70]}")
    offset = max(0, room-used)
    anchor = frame.vertical_anchor
    cursor = y + top + (offset/2 if anchor == MSO_ANCHOR.MIDDLE else offset if anchor == MSO_ANCHOR.BOTTOM else 0)
    for block, h, before, after in blocks:
        cursor += before
        block.drawOn(canvas, x+left, canvas._pagesize[1]-cursor-h)
        cursor += h + after


base.render_text = render_text

if __name__ == "__main__":
    sys.argv = [sys.argv[0],
                "--source", str(HERE / "decision-theory.pptx"),
                "--target", str(HERE / "decision-theory.pdf"),
                "--qa", str(HERE / "qa/layout-validation.json"),
                "--title", "Decision theory for delegated agents: six usable results"]
    tr.main()
