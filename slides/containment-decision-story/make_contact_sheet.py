"""Rasterise the rendered PDF (pdftoppm) and tile the pages into qa/contact-sheet.png plus per-slide PNGs."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PDF = ROOT / 'output/pdf/containment-decision-story.pdf'
QA = HERE / 'qa'
COLS = 3

if __name__ == '__main__':
    for old in QA.glob('slide-*.png'):
        old.unlink()
    subprocess.run(['pdftoppm', '-png', '-r', '60', str(PDF), str(QA / 'slide')], check=True)
    pages = sorted(QA.glob('slide-*.png'))
    if not pages:
        sys.exit('no pages rendered')
    images = [Image.open(p) for p in pages]
    w, h = images[0].size
    gap = 16
    rows = (len(images) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * w + (COLS + 1) * gap, rows * h + (rows + 1) * gap), (220, 224, 228))
    for i, im in enumerate(images):
        r, c = divmod(i, COLS)
        sheet.paste(im, (gap + c * (w + gap), gap + r * (h + gap)))
    sheet.save(QA / 'contact-sheet.png')
    print(f'{len(images)} pages → {QA / "contact-sheet.png"}')
