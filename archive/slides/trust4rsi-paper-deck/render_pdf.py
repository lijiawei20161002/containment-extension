"""Render trust4rsi-paper-plan.pptx to vector PDF with the incident-library deck's renderer.

Reuses ../incident-library-deck/render_pdf.py (text, tables, simple shapes only) and
writes an overflow check to qa/layout-validation.json. Requires python-pptx and reportlab.
"""
from __future__ import annotations

import argparse
import json
import sys
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "incident-library-deck"))

from pptx import Presentation  # noqa: E402
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_SHAPE_TYPE  # noqa: E402
from pptx.enum.dml import MSO_FILL_TYPE  # noqa: E402
from reportlab.pdfgen.canvas import Canvas  # noqa: E402
from reportlab.lib.utils import ImageReader  # noqa: E402

import render_pdf as base  # noqa: E402


def diagram_shape(canvas, shape, x, y, w, h):
    kind = shape.auto_shape_type
    if kind not in {MSO_AUTO_SHAPE_TYPE.OVAL, MSO_AUTO_SHAPE_TYPE.ISOSCELES_TRIANGLE}:
        return base.fill_shape(canvas, shape, x, y, w, h)
    solid = shape.fill.type == MSO_FILL_TYPE.SOLID
    stroke = shape.line.fill.type == MSO_FILL_TYPE.SOLID
    if solid:
        canvas.setFillColor(base.color(shape.fill.fore_color))
    if stroke:
        canvas.setStrokeColor(base.color(shape.line.color))
        canvas.setLineWidth(base.pt(shape.line.width) if shape.line.width else .75)
    bottom = canvas._pagesize[1] - y - h
    if kind == MSO_AUTO_SHAPE_TYPE.OVAL:
        canvas.ellipse(x, bottom, x+w, bottom+h, stroke=int(stroke), fill=int(solid))
        return
    vertices = {
        0: [(x, bottom), (x+w/2, bottom+h), (x+w, bottom)],
        90: [(x, bottom), (x+w, bottom+h/2), (x, bottom+h)],
        180: [(x, bottom+h), (x+w/2, bottom), (x+w, bottom+h)],
        270: [(x+w, bottom), (x, bottom+h/2), (x+w, bottom+h)],
    }
    if shape.rotation not in vertices:
        raise ValueError("Diagram arrows must be orthogonal")
    points = vertices[shape.rotation]
    path = canvas.beginPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    path.close()
    canvas.drawPath(path, stroke=int(stroke), fill=int(solid))


def main():
    base.register_fonts()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=HERE / "trust4rsi-paper-plan.pptx")
    parser.add_argument("--target", type=Path, default=HERE / "trust4rsi-paper-plan.pdf")
    parser.add_argument("--qa", type=Path, default=HERE / "qa/layout-validation.json")
    parser.add_argument("--title", default="When a task fails: recovery, permission, and incident evidence | Trust4RSI")
    args = parser.parse_args()
    source, target = args.source, args.target
    prs = Presentation(source)
    canvas = Canvas(str(target), pagesize=(base.pt(prs.slide_width), base.pt(prs.slide_height)))
    canvas.setTitle(args.title)
    canvas.setAuthor("containment-extension")
    issues = []
    for number, slide in enumerate(prs.slides, 1):
        for index, shape in enumerate(slide.shapes):
            label = f"slide {number}, shape {index}"
            x, y, w, h = map(base.pt, (shape.left, shape.top, shape.width, shape.height))
            if shape.has_table:
                tbl = shape.table
                row_y = y
                for i, row in enumerate(tbl.rows):
                    col_x = x
                    for j, column in enumerate(tbl.columns):
                        cell = tbl.cell(i, j)
                        cw, rh = base.pt(column.width), base.pt(row.height)
                        canvas.setFillColor(base.color(cell.fill.fore_color, "#ffffff"))
                        canvas.rect(col_x, base.pt(prs.slide_height) - row_y - rh, cw, rh, fill=1, stroke=0)
                        base.render_text(canvas, cell.text_frame, col_x, row_y, cw, rh, f"{label}, cell {i},{j}", issues)
                        col_x += cw
                    row_y += base.pt(row.height)
            elif shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                diagram_shape(canvas, shape, x, y, w, h)
            elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                if any((shape.crop_left, shape.crop_right, shape.crop_top, shape.crop_bottom)):
                    raise ValueError("Cropped pictures require explicit renderer support")
                canvas.drawImage(ImageReader(BytesIO(shape.image.blob)), x,
                                 base.pt(prs.slide_height) - y - h, width=w, height=h,
                                 mask="auto")
            elif shape.shape_type != MSO_SHAPE_TYPE.TEXT_BOX:
                raise ValueError(f"Unsupported object: {shape.shape_type}")
            if shape.has_text_frame and shape.text:
                base.render_text(canvas, shape.text_frame, x, y, w, h, label, issues)
                links = {run.hyperlink.address for p in shape.text_frame.paragraphs
                         for run in p.runs if run.hyperlink.address}
                if len(links) == 1:
                    canvas.linkURL(links.pop(), (x, base.pt(prs.slide_height)-y-h,
                                                x+w, base.pt(prs.slide_height)-y),
                                   relative=0, thickness=0)
        canvas.showPage()
    canvas.save()
    report = {"slides": len(prs.slides), "renderer": "reportlab; native vector shapes and text",
              "overflow_issues": issues}
    (HERE / "qa").mkdir(exist_ok=True)
    args.qa.write_text(json.dumps(report, indent=2) + "\n")
    if issues:
        raise SystemExit("Layout requires adjustment:\n" + "\n".join(issues))
    print(f"Rendered {target}: {len(prs.slides)} slides; no text overflow.")


if __name__ == "__main__":
    main()
