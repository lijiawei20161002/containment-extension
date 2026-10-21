"""Render the native PowerPoint shapes to PDF with the repository renderer."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
renderer=HERE.parent/'decision-theory-deck/render_deck_pdf.py'
spec=importlib.util.spec_from_file_location('decision_renderer',renderer)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Preserve the slide hyperlinks in the PDF as well as the PPTX. The underlying
# renderer already handles run-level baseline and reports text overflow.
original=module.base.render_text

# The shared renderer builds Menlo paragraphs as Preformatted blocks without a text colour, so
# pseudocode rendered black on the navy code boxes. Feed each paragraph's run colour through.
from collections import deque
from reportlab.platypus import Preformatted as _Preformatted
_code_colors=deque()
class _ColoredPreformatted(_Preformatted):
    def __init__(self,text,style,**kw):
        if _code_colors:
            style.textColor=_code_colors.popleft()
        super().__init__(text,style,**kw)
module.Preformatted=_ColoredPreformatted

def linked_text(canvas,frame,x,y,w,h,label,issues):
    _code_colors.clear()
    for p in frame.paragraphs:
        if p.runs and all(r.font.name=='Menlo' for r in p.runs):
            _code_colors.append(module.color(p.runs[0].font.color))
    original(canvas,frame,x,y,w,h,label,issues)
    _code_colors.clear()
    urls={r.hyperlink.address for p in frame.paragraphs for r in p.runs if r.hyperlink.address}
    if len(urls)==1:
        url=next(iter(urls))
        if url.startswith('https://'):
            bottom=canvas._pagesize[1]-y-h
            canvas.linkURL(url,(x,bottom,x+w,bottom+h),relative=0,thickness=0)
module.base.render_text=linked_text

# Georgia for display text on the cover; the shared renderer knows only Arial and Menlo.
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
_SUPP=Path('/System/Library/Fonts/Supplemental')
for _name,_file in [('Georgia','Georgia.ttf'),('Georgia-Bold','Georgia Bold.ttf'),
                    ('Georgia-Italic','Georgia Italic.ttf'),('Georgia-BoldItalic','Georgia Bold Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(_name,str(_SUPP/_file)))

def font_name(font):
    if font.name=='Menlo':
        return 'Menlo'
    family='Georgia' if font.name=='Georgia' else 'Arial'
    if font.bold and font.italic:
        return f'{family}-BoldItalic'
    return f'{family}-Bold' if font.bold else f'{family}-Italic' if font.italic else family
module.font_name=font_name
module.base.font_name=font_name

if __name__=='__main__':
    target=ROOT/'output/pdf/containment-decision-story.pdf'
    target.parent.mkdir(parents=True,exist_ok=True)
    sys.argv=[sys.argv[0],'--source',str(HERE/'containment-decision-story.pptx'),
              '--target',str(target),'--qa',str(HERE/'qa/layout-validation.json'),
              '--title','When the task fails: a decision theory of agent boundaries']
    module.tr.main()
