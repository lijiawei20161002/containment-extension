"""Renderer for public-incident case-study figures (figures/incidents/).

Each figure is described by a plain dict spec (see incident_figure_specs.py)
and rendered to an HTML page with inline SVG arrows/icons, then screenshotted
with headless Chrome at 2x (1680x945 logical px, matching the existing
Medicare and DSEwiki figures). No model calls. The HTML file is kept beside
the PNG as the editable source.
"""
from __future__ import annotations

import html
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

W, H = 1680, 945
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

COL = {
    "navy": "#1b2d55",
    "blue": "#1f5fd0",
    "blue_dark": "#1548a8",
    "purple": "#7b3fb8",
    "red": "#c8392b",
    "gray": "#8a8f98",
    "gray_text": "#5b6068",
    "ink": "#222733",
    "panel_gray": "#ededf0",
    "panel_blue": "#eaf3fd",
    "panel_blue_line": "#9ec3ee",
    "panel_purple": "#f3ecfa",
    "panel_red": "#fbeeec",
    "icon_bg_blue": "#e0ecfb",
    "icon_bg_purple": "#ece2f7",
    "icon_bg_navy": "#e3e8f1",
    "icon_bg_red": "#f9e3e0",
    "icon_bg_gray": "#eceef1",
    "white": "#ffffff",
}

# Lucide-style 24x24 stroke icons (stroke-width 2, round caps/joins).
ICONS = {
    "bot": '<rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><path d="M8 16h.01M16 16h.01"/>',
    "bots": '<rect x="2" y="12" width="9" height="8" rx="1.5"/><rect x="13" y="12" width="9" height="8" rx="1.5"/><circle cx="6.5" cy="7" r="1.6"/><circle cx="17.5" cy="7" r="1.6"/><path d="M6.5 8.6V12M17.5 8.6V12"/><path d="M5 16h.01M8 16h.01M16 16h.01M19 16h.01"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "server": '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><path d="M6 6h.01M6 18h.01"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>',
    "file": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
    "file-code": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v6h6"/><path d="M10 12.5 8 15l2 2.5M14 12.5l2 2.5-2 2.5"/>',
    "file-check": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><path d="M14 2v6h6"/><path d="m9 15 2 2 4-4"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "unlock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/>',
    "key": '<circle cx="7.5" cy="15.5" r="5.5"/><path d="M21 2l-9.6 9.6"/><path d="M15.5 7.5l3 3L22 7l-3-3"/>',
    "git": '<path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
    "upload": '<path d="M4 14.9A7 7 0 1 1 15.7 8h1.8a4.5 4.5 0 0 1 2.5 8.2"/><path d="M12 12v9M16 16l-4-4-4 4"/>',
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>',
    "package": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5M12 22V12"/>',
    "terminal": '<path d="m4 17 6-6-6-6M12 19h8"/>',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "messages": '<path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4c0-1.1.9-2 2-2h8a2 2 0 0 1 2 2v5Z"/><path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1"/>',
    "shield-alert": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="M12 8v4M12 16h.01"/>',
    "shield-check": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "shield-off": '<path d="M19.7 14a6.9 6.9 0 0 0 .3-2V5l-8-3-3.2 1.2"/><path d="m2 2 20 20"/><path d="M4.7 4.7 4 5v7c0 6 8 10 8 10a20.3 20.3 0 0 0 5.6-4.4"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "user-x": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="m17 8 5 5M22 8l-5 5"/>',
    "building": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
    "landmark": '<path d="M3 22h18M6 18v-7M10 18v-7M14 18v-7M18 18v-7"/><path d="M12 2 20 7H4z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "folder": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4M12 17h.01"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "network": '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3M12 12V8"/>',
    "eye": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "stop": '<path d="M7.86 2h8.28L22 7.86v8.28L16.14 22H7.86L2 16.14V7.86z"/><path d="m15 9-6 6M9 9l6 6"/>',
    "dollar": '<path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>',
    "table": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M12 3v18M3 9h18M3 15h18"/>',
    "bug": '<path d="m8 2 1.88 1.88M14.12 3.88 16 2"/><path d="M9 7.13v-1a3 3 0 1 1 6 0v1"/><path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6"/><path d="M12 20v-9M6.53 9C4.6 8.8 3 7.1 3 5M6 13H2M3 21c0-2.1 1.7-3.9 3.8-4M20.97 5c0 2.1-1.6 3.8-3.5 4M22 13h-4M17.2 17c2.1.1 3.8 1.9 3.8 4"/>',
    "dashboard": '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
    "radar": '<path d="M19.07 4.93A10 10 0 0 0 6.99 3.34M4 6h.01M2.29 9.62A10 10 0 1 0 21.31 8.35M16.24 7.76A6 6 0 1 0 8.23 16.67M12 18h.01M17.99 11.66A6 6 0 0 1 15.77 16.67"/><circle cx="12" cy="12" r="2"/><path d="m13.41 10.59 5.66-5.66"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "pull-request": '<circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7M6 9v12"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16M8 16H3v5"/>',
    "clipboard": '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
    "trash": '<path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>',
    "megaphone": '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    "ban": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
    "scissors": '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4 8.12 15.88M14.47 14.48 20 20M8.12 8.12 12 12"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.5-9.17 4.16a2 2 0 0 1-1.66 0L2 12.5M22 17.5l-9.17 4.16a2 2 0 0 1-1.66 0L2 17.5"/>',
    "flask": '<path d="M10 2v7.5L4.2 19.6A1.5 1.5 0 0 0 5.5 22h13a1.5 1.5 0 0 0 1.3-2.4L14 9.5V2M8.5 2h7M7 16h10"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1ZM2 16l3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1ZM7 21h10M12 3v18M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "smartphone": '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
    "brain": '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.04Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.04Z"/>',
    "wifi-off": '<path d="M12 20h.01M8.5 16.4a5 5 0 0 1 7 0M2 8.8a15 15 0 0 1 4.2-2.6M10.7 5.1a15 15 0 0 1 11.3 3.7M16.8 11.6a10 10 0 0 1 2.2 1.6M5 12.9a10 10 0 0 1 5.2-2.7"/><path d="m2 2 20 20"/>',
    "pause": '<rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>',
    "flag": '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1zM4 22v-7"/>',
    "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="M3.3 7 12 12l8.7-5M12 22V12"/>',
    "hash": '<path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/>',
    "text": '<path d="M17 6.1H3M21 12.1H3M15.1 18H3"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)dpx;height:%(H)dpx;background:#fff;overflow:hidden}
body{font-family:-apple-system,"SF Pro Text","Helvetica Neue",Inter,Arial,sans-serif;color:%(ink)s;position:relative;
  -webkit-font-smoothing:antialiased}
.abs{position:absolute}
.title{left:42px;top:26px;font-size:44px;font-weight:700;color:%(navy)s;letter-spacing:-0.5px;line-height:1.05}
.subtitle{left:42px;top:84px;font-size:21px;color:%(blue)s;font-weight:500}
.rule{left:42px;width:%(RW)dpx;height:3px;background:%(blue)s}
.panel{border-radius:18px;padding:22px 20px 18px 20px}
.panel.gray{background:%(panel_gray)s}
.panel.blue{background:%(panel_blue)s;border:1.5px solid %(panel_blue_line)s}
.panel.purple{background:%(panel_purple)s;border:1.5px solid #d6c2ec}
.panel.red{background:%(panel_red)s;border:1.5px solid #ecc2bc}
.panel.white{background:#fff;border:1.5px dashed #c5cad3}
.ptitle{font-size:24px;font-weight:700;color:%(navy)s;line-height:1.15}
.ptitle .t2{color:%(blue)s;font-weight:700}
.ptitle .sep{color:#9aa2ad;font-weight:300;padding:0 10px}
.psub{font-size:16px;color:%(gray_text)s;margin-top:4px}
.card{background:#fff;border-radius:14px;border:2.5px solid;padding:14px 16px 12px 16px;display:flex;gap:14px;align-items:flex-start;
  box-shadow:0 1px 2px rgba(20,30,60,.06)}
.card .ic{flex:0 0 auto;width:66px;height:66px;border-radius:50%%;display:flex;align-items:center;justify-content:center}
.card .ic svg{width:36px;height:36px;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.card .ic.sm{width:48px;height:48px}.card .ic.sm svg{width:27px;height:27px}
.card .tx{flex:1 1 auto;min-width:0}
.card .ct{font-size:20px;font-weight:700;line-height:1.15;margin-bottom:5px}
.card .cl{font-size:15.5px;line-height:1.3;color:%(ink)s}
.card .cs{font-size:13.5px;line-height:1.3;color:%(gray_text)s;margin-top:4px}
.card .cn{font-size:14px;line-height:1.3;margin-top:6px;padding-top:6px;border-top:1px solid #e3e6ea;font-weight:600}
.card .cl b,.card .cs b{font-weight:700}
.card.c-blue{border-color:%(blue)s}.card.c-blue .ct{color:%(blue)s}.card.c-blue .ic{background:%(icon_bg_blue)s}.card.c-blue .ic svg{stroke:%(blue)s}.card.c-blue .cn{color:%(blue)s}
.card.c-purple{border-color:%(purple)s}.card.c-purple .ct{color:%(purple)s}.card.c-purple .ic{background:%(icon_bg_purple)s}.card.c-purple .ic svg{stroke:%(purple)s}.card.c-purple .cn{color:%(purple)s}
.card.c-navy{border-color:%(navy)s}.card.c-navy .ct{color:%(navy)s}.card.c-navy .ic{background:%(icon_bg_navy)s}.card.c-navy .ic svg{stroke:%(navy)s}.card.c-navy .cn{color:%(navy)s}
.card.c-red{border-color:%(red)s}.card.c-red .ct{color:%(red)s}.card.c-red .ic{background:%(icon_bg_red)s}.card.c-red .ic svg{stroke:%(red)s}.card.c-red .cn{color:%(red)s}
.card.c-gray{border-color:#c9ced6}.card.c-gray .ct{color:%(gray_text)s}.card.c-gray .ic{background:%(icon_bg_gray)s}.card.c-gray .ic svg{stroke:%(gray_text)s}.card.c-gray .cn{color:%(gray_text)s}
.card.c-green{border-color:#2f8f5b}.card.c-green .ct{color:#2f8f5b}.card.c-green .ic{background:#e2f3e9}.card.c-green .ic svg{stroke:#2f8f5b}.card.c-green .cn{color:#2f8f5b}
.badge{width:34px;height:34px;border-radius:50%%;background:%(blue)s;color:#fff;font-weight:700;font-size:17px;display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 0 3px #fff}
.badge.purple{background:%(purple)s}.badge.red{background:%(red)s}.badge.navy{background:%(navy)s}.badge.gray{background:%(gray)s}
.lbl{font-size:15px;line-height:1.25;color:%(ink)s}
.lbl.blue{color:%(blue)s;font-weight:600}.lbl.red{color:%(red)s;font-weight:700}.lbl.purple{color:%(purple)s;font-weight:600}.lbl.gray{color:%(gray_text)s}.lbl.navy{color:%(navy)s;font-weight:700}
.lbl.center{text-align:center}
.tl-line{height:4px;background:%(blue)s;border-radius:2px}
.tl-dot{width:18px;height:18px;border-radius:50%%;background:%(blue)s;border:3.5px solid %(blue)s}
.tl-dot.purple{background:%(purple)s;border-color:%(purple)s}.tl-dot.red{background:%(red)s;border-color:%(red)s}.tl-dot.navy{background:%(navy)s;border-color:%(navy)s}
.tl-dot.hollow{background:#fff;border-color:%(navy)s}
.tl-date{font-size:17px;font-weight:700;color:%(blue)s;text-align:center;line-height:1.2}
.tl-date.purple{color:%(purple)s}.tl-date.red{color:%(red)s}.tl-date.navy{color:%(navy)s}
.tl-text{font-size:15px;color:%(ink)s;text-align:center;line-height:1.25;margin-top:3px}
.evidence{background:%(panel_gray)s;border-radius:12px;padding:12px 18px;font-size:15.5px;line-height:1.4;color:%(ink)s}
.legend{display:flex;gap:34px;align-items:center;font-size:15.5px;color:%(ink)s}
.legend .li{display:flex;align-items:center;gap:10px}
.sources{font-size:13.5px;line-height:1.45;color:%(gray_text)s}
.sources i{font-style:italic}
.meter{font-size:13px;color:#aab0ba}
""" % dict(COL, W=W, H=H, RW=W - 84)


def esc(s: str) -> str:
    """Escape text but allow **bold** and *italic* markers."""
    s = html.escape(s)
    out, parts = [], s.split("**")
    for i, p in enumerate(parts):
        out.append(f"<b>{p}</b>" if i % 2 else p)
    s = "".join(out)
    parts = s.split("*")
    if len(parts) % 2:
        s = "".join(f"<i>{p}</i>" if i % 2 else p for i, p in enumerate(parts))
    return s


def icon_svg(name: str) -> str:
    body = ICONS.get(name) or ICONS["box"]
    return f'<svg viewBox="0 0 24 24">{body}</svg>'


def _anchor(rect, spec):
    """rect=(x,y,w,h); spec like 'right' or 'right:0.3' -> (px,py,direction)."""
    x, y, w, h = rect
    side, _, frac = spec.partition(":")
    f = float(frac) if frac else 0.5
    if side == "left":
        return x, y + h * f, (-1, 0)
    if side == "right":
        return x + w, y + h * f, (1, 0)
    if side == "top":
        return x + w * f, y, (0, -1)
    return x + w * f, y + h, (0, 1)


def block_arrow(x1, y1, x2, y2, color, shaft=7, head_l=20, head_w=16):
    """Filled block arrow for axis-aligned paths."""
    if abs(y1 - y2) < 1:  # horizontal
        d = 1 if x2 > x1 else -1
        hx = x2 - d * head_l
        pts = [(x1, y1 - shaft), (hx, y1 - shaft), (hx, y1 - head_w), (x2, y1),
               (hx, y1 + head_w), (hx, y1 + shaft), (x1, y1 + shaft)]
    else:  # vertical
        d = 1 if y2 > y1 else -1
        hy = y2 - d * head_l
        pts = [(x1 - shaft, y1), (x1 - shaft, hy), (x1 - head_w, hy), (x1, y2),
               (x1 + head_w, hy), (x1 + shaft, hy), (x1 + shaft, y1)]
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    return f'<polygon points="{p}" fill="{color}"/>'


ARROW_COL = {"blue": COL["blue"], "red": COL["red"], "purple": COL["purple"], "gray": "#b5bac2", "navy": COL["navy"], "green": "#2f8f5b"}


def render_arrow(a, rects):
    style = a.get("style", "blue")
    color = ARROW_COL[style]
    dashed = a.get("dashed", style == "purple")
    stroke_only = a.get("thin", dashed)
    if "frm" in a:
        x1, y1, d1 = _anchor(rects[a["frm"]], a.get("fa", "right"))
    else:
        x1, y1 = a["p1"]; d1 = a.get("d1", (1, 0))
    if "to" in a:
        x2, y2, d2 = _anchor(rects[a["to"]], a.get("ta", "left"))
    else:
        x2, y2 = a["p2"]; d2 = a.get("d2", (-1, 0))
    gap = a.get("gap", 4)
    x1 += d1[0] * gap; y1 += d1[1] * gap
    x2 += d2[0] * gap; y2 += d2[1] * gap
    out = []
    via = a.get("via")
    straight = abs(x1 - x2) < 1 or abs(y1 - y2) < 1
    if straight and not stroke_only and not via:
        out.append(block_arrow(x1, y1, x2, y2, color))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    else:
        # orthogonal polyline: leave along d1, arrive along -d2
        pts = [(x1, y1)]
        if via:
            for v in via:
                pts.append(tuple(v))
        else:
            if d1[0] != 0 and d2[0] != 0:  # both horizontal: go out, step vertically at midpoint
                mxx = (x1 + x2) / 2 if a.get("mid") is None else a["mid"]
                pts += [(mxx, y1), (mxx, y2)]
            elif d1[1] != 0 and d2[1] != 0:
                myy = (y1 + y2) / 2 if a.get("mid") is None else a["mid"]
                pts += [(x1, myy), (x2, myy)]
            elif d1[0] != 0:  # leave horizontally, arrive vertically
                pts.append((x2, y1))
            else:
                pts.append((x1, y2))
        pts.append((x2, y2))
        sw = a.get("width", 4 if stroke_only else 6)
        dash = ' stroke-dasharray="10 8"' if dashed else ""
        d = "M " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts)
        mid = f"arrow-{style}"
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{dash} stroke-linejoin="round" marker-end="url(#{mid})"/>')
        # midpoint of polyline (by segment count)
        k = len(pts) // 2
        if len(pts) % 2 == 0:
            mx, my = (pts[k - 1][0] + pts[k][0]) / 2, (pts[k - 1][1] + pts[k][1]) / 2
        else:
            mx, my = pts[k]
    return "".join(out), (mx, my)


def render(spec: dict) -> str:
    parts = [f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(spec['title'])}</title><style>{CSS}</style></head><body>"]
    parts.append(f"<div class='abs title'>{esc(spec['title'])}</div>")
    if spec.get("subtitle"):
        parts.append(f"<div class='abs subtitle'>{esc(spec['subtitle'])}</div>")
    rule_y = spec.get("rule_y", 118)
    parts.append(f"<div class='abs rule' style='top:{rule_y}px'></div>")

    rects = {}
    # panels
    for p in spec.get("panels", []):
        x, y, w, h = p["x"], p["y"], p["w"], p["h"]
        rects[p.get("id", "panel:" + p["title"])] = (x, y, w, h)
        t = esc(p["title"])
        if p.get("title2"):
            t += f"<span class='sep'>|</span><span class='t2'>{esc(p['title2'])}</span>"
        sub = f"<div class='psub'>{esc(p['sub'])}</div>" if p.get("sub") else ""
        parts.append(f"<div class='abs panel {p.get('tint','gray')}' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px'>"
                     f"<div class='ptitle'>{t}</div>{sub}</div>")
    # cards
    for c in spec.get("cards", []):
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        rects[c["id"]] = (x, y, w, h)
        lines = "".join(f"<div class='cl'>{esc(l)}</div>" for l in c.get("lines", []))
        small = "".join(f"<div class='cs'>{esc(l)}</div>" for l in c.get("small", []))
        note = f"<div class='cn'>{esc(c['note'])}</div>" if c.get("note") else ""
        ic = f"<div class='ic {'sm' if c.get('small_icon') else ''}'>{icon_svg(c.get('icon','box'))}</div>" if c.get("icon") else ""
        parts.append(f"<div class='abs card c-{c.get('accent','blue')}' style='left:{x}px;top:{y}px;width:{w}px;min-height:{h}px'>"
                     f"{ic}<div class='tx'><div class='ct'>{esc(c['title'])}</div>{lines}{small}{note}</div></div>")
    # arrows (svg overlay)
    svg = [f"<svg class='abs' style='left:0;top:0' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><defs>"]
    for k, col in ARROW_COL.items():
        svg.append(f"<marker id='arrow-{k}' markerWidth='10' markerHeight='10' refX='7' refY='5' orient='auto' markerUnits='userSpaceOnUse'>"
                   f"<path d='M1,1 L8,5 L1,9 z' fill='{col}'/></marker>")
    svg.append("</defs>")
    badges, labels = [], []
    for a in spec.get("arrows", []):
        s, (mx, my) = render_arrow(a, rects)
        svg.append(s)
        if a.get("num") is not None:
            bx, by = a.get("badge_at", (mx, my))
            dx, dy = a.get("badge_dx", 0), a.get("badge_dy", 0)
            badges.append((bx + dx, by + dy, a["num"], a.get("badge_color", "blue" if a.get("style", "blue") in ("blue", "gray") else a.get("style"))))
        if a.get("label"):
            lx, ly = a.get("label_at", (mx, my))
            labels.append(dict(x=lx + a.get("label_dx", 0), y=ly + a.get("label_dy", 0), text=a["label"],
                               color=a.get("label_color", {"red": "red", "purple": "purple", "blue": "blue"}.get(a.get("style", "blue"), "")),
                               w=a.get("label_w", 180), align=a.get("label_align", "left"), size=a.get("label_size")))
    for sh in spec.get("svg_extra", []):
        svg.append(sh)
    svg.append("</svg>")
    parts.append("".join(svg))
    for bx, by, n, colr in badges + [(b["x"], b["y"], b["num"], b.get("color", "blue")) for b in spec.get("badges", [])]:
        parts.append(f"<div class='abs badge {colr}' style='left:{bx-17:.0f}px;top:{by-17:.0f}px'>{n}</div>")
    for l in labels + spec.get("labels", []):
        cls = l.get("color", "")
        al = l.get("align", "left")
        style = f"left:{l['x']:.0f}px;top:{l['y']:.0f}px;width:{l.get('w',180)}px;text-align:{al}"
        if l.get("size"):
            style += f";font-size:{l['size']}px"
        if l.get("bg"):
            style += ";background:#fff;padding:2px 6px;border-radius:6px"
        parts.append(f"<div class='abs lbl {cls}' style='{style}'>{esc(l['text'])}</div>")

    # timeline
    tl = spec.get("timeline")
    if tl:
        ty = spec.get("timeline_y", 662)
        x0, x1 = 115, W - 90
        n = len(tl)
        parts.append(f"<div class='abs tl-line' style='left:{x0}px;top:{ty-2}px;width:{x1-x0}px'></div>")
        # colored tail for later-phase segment
        for i, e in enumerate(tl):
            px = x0 + (x1 - x0) * (i / (n - 1) if n > 1 else 0)
            if i > 0 and e.get("color") == "purple" and tl[i - 1].get("color") == "purple":
                ppx = x0 + (x1 - x0) * ((i - 1) / (n - 1))
                parts.append(f"<div class='abs tl-line' style='left:{ppx}px;top:{ty-2}px;width:{px-ppx}px;background:{COL['purple']}'></div>")
            if i > 0 and e.get("color") == "purple" and tl[i - 1].get("color") != "purple":
                ppx = x0 + (x1 - x0) * ((i - 1) / (n - 1))
                parts.append(f"<div class='abs tl-line' style='left:{ppx}px;top:{ty-2}px;width:{px-ppx}px;background:linear-gradient(90deg,{COL['blue']},{COL['purple']})'></div>")
        for i, e in enumerate(tl):
            px = x0 + (x1 - x0) * (i / (n - 1) if n > 1 else 0)
            cls = e.get("color", "blue") + (" hollow" if e.get("hollow") else "")
            parts.append(f"<div class='abs tl-dot {cls}' style='left:{px-9:.0f}px;top:{ty-9}px'></div>")
            tw = e.get("w", 250)
            lx = min(max(px - tw / 2, 42), W - 42 - tw)
            parts.append(f"<div class='abs' style='left:{lx:.0f}px;top:{ty+24}px;width:{tw}px'>"
                         f"<div class='tl-date {e.get('color','blue')}'>{esc(e['date'])}</div><div class='tl-text'>{esc(e['label'])}</div></div>")

    # evidence strip
    ev = spec.get("evidence")
    if ev:
        ey = spec.get("evidence_y", 752)
        body = "<br>".join(esc(l) for l in ev)
        parts.append(f"<div class='abs evidence' style='left:42px;top:{ey}px;width:{W-84}px'>{body}</div>")

    # legend
    lg = spec.get("legend")
    if lg:
        ly = spec.get("legend_y", 832)
        items = []
        for it in lg:
            st = it["style"]
            if st in ("blue", "red", "gray", "navy", "green", "purple-block"):
                col = COL["purple"] if st == "purple-block" else ARROW_COL[st]
                sw = f"<svg width='66' height='26' viewBox='0 0 66 26'>{block_arrow(2,13,64,13,col,shaft=5,head_l=16,head_w=12)}</svg>"
            elif st == "purple":
                sw = f"<svg width='66' height='26' viewBox='0 0 66 26'><path d='M2 13 L56 13' stroke='{COL['purple']}' stroke-width='4' stroke-dasharray='9 7' marker-end='url(#lg-p)'/><defs><marker id='lg-p' markerWidth='10' markerHeight='10' refX='7' refY='5' orient='auto' markerUnits='userSpaceOnUse'><path d='M1,1 L8,5 L1,9 z' fill='{COL['purple']}'/></marker></defs></svg>"
            elif st == "purple-line":
                sw = f"<svg width='66' height='26' viewBox='0 0 66 26'><path d='M2 13 L64 13' stroke='{COL['purple']}' stroke-width='4'/></svg>"
            elif st == "blue-line":
                sw = f"<svg width='66' height='26' viewBox='0 0 66 26'><path d='M2 13 L64 13' stroke='{COL['blue']}' stroke-width='4'/></svg>"
            else:
                sw = ""
            items.append(f"<div class='li'>{sw}<span>{esc(it['text'])}</span></div>")
        parts.append(f"<div class='abs legend' style='left:42px;top:{ly}px'>{''.join(items)}</div>")

    # sources
    src = spec.get("sources")
    if src:
        sy = spec.get("sources_y", 872)
        body = "<br>".join(esc(l) for l in src)
        parts.append(f"<div class='abs sources' style='left:42px;top:{sy}px;width:{W-84}px'>{body}</div>")
    parts.append("</body></html>")
    return "".join(parts)


def screenshot(html_path: Path, png_path: Path, scale: int = 2) -> None:
    with tempfile.TemporaryDirectory() as td:
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               f"--user-data-dir={td}", f"--force-device-scale-factor={scale}",
               f"--window-size={W},{H}", f"--screenshot={png_path}", html_path.resolve().as_uri()]
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)


def build(spec: dict, out_root: Path) -> Path:
    slug = spec["slug"]
    d = out_root / slug
    d.mkdir(parents=True, exist_ok=True)
    stem = f"incident-{spec['n']:02d}-{slug}"
    html_path = d / f"{stem}.html"
    png_path = d / f"{stem}.png"
    html_path.write_text(render(spec), encoding="utf-8")
    (d / f"{stem}.spec.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False), encoding="utf-8")
    screenshot(html_path, png_path)
    return png_path
