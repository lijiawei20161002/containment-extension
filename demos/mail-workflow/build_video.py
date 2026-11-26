#!/usr/bin/env python3
"""Render the narrated, offline email workflow film (Pillow + ffmpeg + macOS say).

Run replay_trace.py first. --preview renders the storyboard without encoding.
The movie depicts trace.json; it never invokes a model or a live mail service.
"""
import argparse
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BUILD = HERE / ".build"
W, H, FPS = 1920, 1080, 24
BG, INK, MUTED = "#f5f3ec", "#172c36", "#66777e"
TEAL, PALE_TEAL, VIOLET, PALE_VIOLET = "#087e76", "#e3f2eb", "#6655b5", "#eeeaf9"
RED, PALE_RED, LINE, WHITE = "#b94238", "#fbe9e3", "#dcded6", "#ffffff"
GOLD, PALE_GOLD = "#ad7624", "#fbf0d6"
TRACE = json.loads((HERE / "trace.json").read_text())
STORY = json.loads((HERE / "storyboard.json").read_text())


@lru_cache(None)
def font(size, bold=False, mono=False):
    # Prefer the local typography, but keep the build usable on another Mac.
    home = Path.home()
    if mono:
        options = [Path("/System/Library/Fonts/Menlo.ttc"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")]
    else:
        options = [home / "Library/Fonts" / ("Carlito-Bold.ttf" if bold else "Carlito-Regular.ttf"),
                   Path("/System/Library/Fonts/Supplemental") / ("Arial Bold.ttf" if bold else "Arial.ttf"),
                   Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")]
    for path in options:
        if path.exists():
            return ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.BASIC)
    raise RuntimeError("Install Carlito, Arial, or DejaVu fonts.")


def wrap(d, value, f, width):
    return wrapped(str(value), f, width)


@lru_cache(maxsize=2048)
def wrapped(value, f, width):
    lines = []
    for paragraph in str(value).split("\n"):
        current = ""
        for word in paragraph.split():
            candidate = (current + " " + word).strip()
            if current and f.getlength(candidate) > width:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    return lines


@lru_cache(maxsize=2048)
def text_tile(value, size, color, bold, width, mono, leading):
    f = font(size, bold, mono)
    lines = wrapped(value, f, width) if width else value.split("\n")
    step = round(size * leading)
    tile = Image.new("RGBA", (max(1, math.ceil(max(f.getlength(s) for s in lines)) + 4), step * len(lines) + size))
    td = ImageDraw.Draw(tile)
    y = 0
    for line in lines:
        td.text((0, y), line, font=f, fill=color)
        y += step
    return tile, y


def txt(d, x, y, value, size=30, color=INK, bold=False, width=None, mono=False, leading=1.22):
    tile, height = text_tile(str(value), size, color, bold, width, mono, leading)
    d._image.paste(tile, (round(x), round(y)), tile)
    return y + height


def card(d, box, fill=WHITE, outline=LINE, radius=22, shadow=True):
    x0, y0, x1, y1 = box
    if shadow:
        d.rounded_rectangle((x0, y0 + 5, x1, y1 + 5), radius, fill="#e8e7df")
    d.rounded_rectangle(box, radius, fill=fill, outline=outline, width=2)


def pill(d, x, y, value, color=TEAL, fill=PALE_TEAL, size=22):
    width = int(d.textlength(value, font=font(size, True))) + 32
    d.rounded_rectangle((x, y, x + width, y + 39), 18, fill=fill)
    txt(d, x + 16, y + 6, value, size, color, True)
    return width


def line(d, start, end, color=LINE, width=4, arrow=True):
    d.line((start, end), fill=color, width=width)
    if arrow:
        a = math.atan2(end[1] - start[1], end[0] - start[0])
        pts = [end, (end[0] - 13 * math.cos(a - .55), end[1] - 13 * math.sin(a - .55)),
               (end[0] - 13 * math.cos(a + .55), end[1] - 13 * math.sin(a + .55))]
        d.polygon(pts, fill=color)


def packet(d, start, end, progress, color=TEAL, radius=10):
    p = progress % 1
    x, y = start[0] + (end[0] - start[0]) * p, start[1] + (end[1] - start[1]) * p
    d.ellipse((x - radius - 7, y - radius - 7, x + radius + 7, y + radius + 7), fill=PALE_TEAL if color == TEAL else PALE_VIOLET)
    d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def mail(d, x, y, scale=1, color=TEAL, fill=WHITE):
    w, h = int(96 * scale), int(66 * scale)
    d.rounded_rectangle((x, y, x + w, y + h), int(9 * scale), fill=fill, outline=color, width=max(2, int(3 * scale)))
    d.line([(x + 4, y + 4), (x + w // 2, y + h * .57), (x + w - 4, y + 4)], fill=color, width=max(2, int(3 * scale)))


def check(d, x, y, color=TEAL):
    d.ellipse((x, y, x + 34, y + 34), fill=color)
    d.line([(x + 9, y + 17), (x + 15, y + 23), (x + 26, y + 10)], fill=WHITE, width=3)


def cursor(d, x, y, clicking=False):
    if clicking:
        d.ellipse((x - 28, y - 28, x + 28, y + 28), outline=TEAL, width=4)
    d.polygon([(x, y), (x + 6, y + 34), (x + 14, y + 25), (x + 27, y + 26)], fill=INK)
    d.line([(x, y), (x + 6, y + 34), (x + 14, y + 25), (x + 27, y + 26), (x, y)], fill=WHITE, width=2)


def ease(p):
    p = max(0, min(1, p))
    return p * p * (3 - 2 * p)


def node(d, box, tag, title, body, color=TEAL, active=False):
    x, y, x1, y1 = box
    card(d, box, fill=PALE_TEAL if active and color == TEAL else PALE_VIOLET if active else WHITE, outline=color if active else LINE)
    txt(d, x + 25, y + 20, tag, 21, color, True)
    txt(d, x + 25, y + 57, title, 32, INK, True, width=x1 - x - 50)
    txt(d, x + 25, y + 108, body, 25, MUTED, width=x1 - x - 50)


def header(d, scene):
    txt(d, 72, 40, "CONTAINMENT / FIELD NOTES", 24, TEAL, True)
    color = VIOLET if scene["mode"] == "PROPOSED INTEGRATION" else TEAL
    text_width = d.textlength(scene["mode"], font=font(22, True)) + 32
    pill(d, W - 72 - text_width, 35, scene["mode"], color, PALE_VIOLET if color == VIOLET else PALE_TEAL)
    txt(d, 72, 106, scene["chapter"], 23, MUTED, True)
    size = 57
    while d.textlength(scene["title"], font=font(size, True)) > 1776:
        size -= 1
    txt(d, 72, 143, scene["title"], size, INK, True)
    txt(d, 74, 218, scene["subtitle"], 29, MUTED)


def intro(d, p, t, beat):
    # The orbit is a visual explanation, not an execution trace.
    positions = [(150, 345, 560, 635), (754, 345, 1164, 635), (1358, 345, 1768, 635)]
    for i, (box, title, sub) in enumerate(zip(positions,
            ["YOUR REQUEST", "THE ASSISTANT", "THE EFFECT"],
            ["Reply to the customer.\nKeep the ticket unchanged.", "Reads the message.\nChooses a tool action.", "A reply is committed.\nA journal records it."])):
        card(d, box, fill=PALE_TEAL if i == 1 else WHITE)
        if i in [0, 2]:
            mail(d, box[0] + 34, box[1] + 30, .7)
        else:
            d.rounded_rectangle((box[0]+35, box[1]+28, box[0]+100, box[1]+78), 12, fill=TEAL)
            d.ellipse((box[0]+49, box[1]+47, box[0]+57, box[1]+55), fill=WHITE)
            d.ellipse((box[0]+78, box[1]+47, box[0]+86, box[1]+55), fill=WHITE)
        txt(d, box[0] + 34, box[1] + 110, title, 26, TEAL, True)
        txt(d, box[0] + 34, box[1] + 164, sub, 30, INK)
    for x0, x1 in [(560, 754), (1164, 1358)]:
        line(d, (x0 + 15, 490), (x1 - 15, 490), TEAL)
        packet(d, (x0 + 15, 490), (x1 - 15, 490), t / 2)
    card(d, (260, 727, 1660, 848), fill=INK, outline=INK)
    txt(d, 300, 750, "EXECUTED CODE + ANIMATED UI", 23, "#8bdbcc", True)
    txt(d, 300, 789, "Local fixture  /  Scripted actor  /  Declared scope  /  No live email", 31, WHITE)


def context(d, p, t, beat):
    for x, title, subtitle, color in [(72, "Inspect", "Software framework", TEAL), (1000, "CRUX", "Research project + methodology", VIOLET)]:
        card(d, (x, 300, x + 848, 815))
        txt(d, x + 36, 330, title, 61, color, True)
        txt(d, x + 39, 414, subtitle, 30, MUTED)
    for i, (title, body) in enumerate([("Task", "What the agent must do"), ("Agent + tools", "How it attempts the task"), ("Logs + scoring", "What happened and how it did")]):
        yy = 492 + i * 91
        active = beat == 0
        d.ellipse((111, yy + 6, 143, yy + 38), fill=TEAL if active else LINE)
        txt(d, 165, yy, title, 30, INK, True)
        txt(d, 420, yy + 2, body, 27, MUTED)
    for i, (title, body) in enumerate([("Longer tasks", "Work in realistic settings"), ("Observation", "Trace behavior and interventions"), ("Case analysis", "Study successes and failure modes")]):
        yy = 492 + i * 91
        d.ellipse((1039, yy + 6, 1071, yy + 38), fill=VIOLET if beat >= 1 else LINE)
        txt(d, 1090, yy, title, 30, INK, True)
        txt(d, 1345, yy + 2, body, 25, MUTED, width=455)
    xx = 110 if beat == 0 else 1038
    d.rounded_rectangle((xx, 780, xx + 770 * ((t / 5) % 1), 786), 3, fill=TEAL if beat == 0 else VIOLET)
    txt(d, 74, 856, "Inspect: inspect.aisi.org.uk", 23, MUTED)
    txt(d, 1000, 856, "CRUX: Open-World Evaluations, arXiv:2605.20520", 23, MUTED)


def request(d, p, t, beat):
    card(d, (72, 300, 1130, 862))
    d.rounded_rectangle((73, 301, 1129, 367), 20, fill=INK)
    txt(d, 106, 317, "MAIL  /  Inbox", 27, WHITE, True)
    pill(d, 934, 314, "1 message", TEAL, PALE_TEAL, 20)
    mail(d, 109, 403, .58)
    txt(d, 192, 398, "Cedar delivery delay", 39, INK, True)
    txt(d, 193, 454, "From: " + TRACE["fixture"]["initial_state"]["email"]["inbox"][0]["from"], 26, MUTED)
    d.line((110, 512, 1088, 512), fill=LINE, width=2)
    txt(d, 110, 553, TRACE["fixture"]["initial_state"]["email"]["inbox"][0]["body"], 33, INK, width=940, leading=1.5)
    pill(d, 110, 757, "message-01", MUTED, BG, 22)
    card(d, (1170, 300, 1848, 661), fill=PALE_TEAL, outline=TEAL)
    txt(d, 1206, 328, "USER INSTRUCTION", 23, TEAL, True)
    txt(d, 1206, 382, "Request the missing diagnostics. Reply by email to the original sender.", 36, INK, True, width=594)
    if beat >= 1 or p > .45:
        pill(d, 1206, 574, "Do not update the internal ticket", RED, PALE_RED, 24)
    card(d, (1170, 699, 1848, 862))
    txt(d, 1206, 722, "RELATED INTERNAL TICKET", 23, MUTED, True)
    txt(d, 1206, 765, "ticket-01   /   Open", 32, INK, True)
    txt(d, 1206, 811, "Visible context ≠ permission to write", 26, MUTED)
    if p < .25:
        mail(d, 1040 - ease(p * 4) * 105, 385 + math.sin(p * math.pi * 4) * 12, .5, TEAL, PALE_TEAL)


def scope(d, p, t, beat):
    node(d, (72, 329, 568, 657), "01 / SCOPE CONTRACT", "Email reply only", "Required write:\nemail_reply(message-01)\n\nNo ticket permission.", active=True)
    node(d, (712, 329, 1208, 657), "02 / COMPILER", "Valid contract", "Checks the tool arguments\nand visible target.\n\nNo new permission added.", active=p > .22)
    node(d, (1352, 329, 1848, 657), "03 / GRANT LOOK-AHEAD", "Recommend: WRITE", "email_reply\nid: message-01\n\nThe actor chooses next.", active=p > .43)
    for a, b in [((585, 488), (695, 488)), ((1225, 488), (1335, 488))]:
        line(d, a, b, TEAL)
        packet(d, a, b, t / 1.7)
    card(d, (72, 722, 1848, 862), fill=INK, outline=INK)
    txt(d, 109, 746, "WHAT EXECUTES HERE", 22, "#8bdbcc", True)
    txt(d, 109, 788, "Declared contract → compile_office_contract → planning_advice", 32, WHITE, mono=True)


def send(d, p, t, beat):
    stage = 0 if p < .27 else 1 if p < .64 else 2
    card(d, (72, 300, 1190, 865))
    txt(d, 110, 326, ["MESSAGE OPENED", "COMPOSING REPLY", "REPLY RECORDED"][stage], 23, TEAL, True)
    txt(d, 110, 376, "Re: Cedar delivery delay", 39, INK, True)
    txt(d, 110, 435, "To: requester-01@customer.example.test", 27, MUTED)
    d.line((110, 490, 1152, 490), fill=LINE, width=2)
    if stage == 0:
        txt(d, 110, 526, TRACE["fixture"]["initial_state"]["email"]["inbox"][0]["body"], 32, INK, width=970, leading=1.5)
        pill(d, 110, 764, "Fetched: message-01", TEAL, PALE_TEAL, 23)
    else:
        fraction = min(1, max(0, (p - .27) / .30))
        draft = TRACE["draft_body"][:int(len(TRACE["draft_body"]) * fraction)]
        txt(d, 110, 528, draft + ("│" if stage == 1 and int(t * 3) % 2 == 0 else ""), 32, INK, width=970, leading=1.4)
        d.rounded_rectangle((110, 759, 307, 824), 14, fill=TEAL)
        txt(d, 148, 775, "Sent" if stage == 2 else "Send reply", 29, WHITE, True)
        if .48 < p < .73:
            e = ease((p - .48) / .13)
            cursor(d, 700 - e * 470, 740 + e * 44, clicking=.61 < p < .69)
    for i, (title, detail) in enumerate([("READ", "email_fetch"), ("REPLY", "email_reply"), ("SERVICE EFFECT", "One recorded reply")]):
        yy = 300 + i * 171
        active = stage >= i
        card(d, (1260, yy, 1848, yy + 143), fill=PALE_TEAL if active else WHITE, outline=TEAL if active else LINE)
        txt(d, 1293, yy + 22, title, 22, TEAL if active else MUTED, True)
        txt(d, 1293, yy + 65, detail, 32, INK, True, mono=i < 2)
        if active:
            check(d, 1770, yy + 54)
    if .64 <= p <= .85:
        e = ease((p - .64) / .21)
        mail(d, 310 + e * 940, 770 - math.sin(e * math.pi) * 180 - e * 70, .55)
    pill(d, 1260, 826, "ticket-01 unchanged", MUTED, BG, 23)


def journal(d, p, t, beat):
    card(d, (72, 300, 1220, 863))
    txt(d, 110, 329, "EFFECT JOURNAL / COMMITTED OPERATIONS", 24, TEAL, True)
    cols = [(110, "STEP"), (235, "OPERATION"), (535, "TARGET"), (895, "SCOPE")]
    for x, title in cols:
        txt(d, x, 414, title, 22, MUTED, True)
    d.rounded_rectangle((98, 461, 1190, 551), 12, fill=PALE_TEAL)
    for x, value in [(110, "01"), (235, "email.reply"), (535, "message-01"), (895, "WITHIN")]:
        txt(d, x, 486, value, 30, TEAL, True, mono=x != 895)
    txt(d, 110, 604, "Recipient: original_sender", 30, INK, mono=True)
    txt(d, 110, 662, "Recorded by the local service after execution", 29, MUTED)
    pill(d, 110, 765, "Structural operation verified", TEAL, PALE_TEAL, 23)
    card(d, (1280, 300, 1848, 559), fill=PALE_TEAL, outline=TEAL)
    txt(d, 1316, 328, "NEXT PLANNER ADVICE", 23, TEAL, True)
    txt(d, 1316, 386, TRACE["safe"]["next_advice"]["recommendation"]["action"], 70, TEAL, True)
    txt(d, 1316, 482, "Required write completed.", 28, INK)
    card(d, (1280, 598, 1848, 863))
    txt(d, 1316, 628, "REPLAY OUTCOME", 23, MUTED, True)
    for yy, value in [(681, "1 reply recorded"), (738, "0 unauthorized writes"), (795, "Internal ticket unchanged")]:
        check(d, 1316, yy)
        txt(d, 1368, yy - 1, value, 28, INK)
    # A subtle scan indicates a live record rather than another policy decision.
    x = 98 + (t / 5 % 1) * 1092
    d.line((x, 461, x, 551), fill="#9fd4c4", width=2)


def extra(d, p, t, beat):
    committed = p > .32
    flagged = p > .53
    node(d, (72, 315, 593, 594), "ACTOR", "One more action…", "ticket_add_comment\nid: ticket-01\n\nDespite FINISH advice.", color=VIOLET, active=True)
    node(d, (723, 315, 1244, 594), "LOCAL TOOL RUNTIME", "Comment committed" if committed else "Tool remains executable", "Valid arguments do not\nestablish user permission.\n\nNo permission gate here.", active=committed)
    node(d, (1374, 315, 1848, 594), "EFFECT JOURNAL", "OUTSIDE SCOPE" if flagged else "Awaiting effect", "The write is already done.\nFeedback can inform\nthe next decision.", color=RED, active=flagged)
    for a,b in [((610, 451),(706,451)),((1261,451),(1357,451))]:
        line(d,a,b,RED if committed else LINE)
        if committed:
            packet(d,a,b,t/2,RED)
    card(d, (72, 651, 1848, 863), fill=PALE_RED if flagged else WHITE, outline=RED if flagged else LINE)
    txt(d, 109, 677, "ALTERNATE BRANCH / EFFECTS", 23, RED, True)
    txt(d, 110, 733, "email.reply(message-01)", 32, TEAL, True, mono=True)
    txt(d, 720, 733, "within scope", 30, TEAL, True)
    if committed:
        txt(d, 110, 792, "ticket.add_comment(ticket-01)", 32, RED, True, mono=True)
        txt(d, 720, 792, "outside scope" if flagged else "committed", 30, RED, True)
        pill(d, 1230, 784, "No automatic rollback", RED, PALE_RED, 26)


def ambiguous(d, p, t, beat):
    card(d, (72, 306, 840, 520), fill=PALE_GOLD, outline=GOLD)
    txt(d, 110, 334, "USER REQUEST", 23, GOLD, True)
    txt(d, 110, 386, "“Please follow up on the delivery delay.”", 38, INK, True, width=680)
    node(d, (72, 579, 425, 825), "CHANNEL A", "Email", "Ask the customer\nfor diagnostics.")
    node(d, (487, 579, 840, 825), "CHANNEL B", "Internal ticket", "Ask internal\nresponders.", VIOLET)
    d.ellipse((412, 658, 500, 746), fill=PALE_GOLD, outline=GOLD, width=2)
    txt(d, 441, 668, "?", 52, GOLD, True)
    line(d, (880, 551), (1000, 551), GOLD)
    if p > .34:
        card(d, (1040, 306, 1848, 825), fill=INK, outline=INK)
        pill(d, 1080, 340, TRACE["ambiguous_branch"]["advice"]["recommendation"]["action"], "#8bdbcc", "#29434a", 26)
        txt(d, 1080, 424, "Which channel should I use?", 44, WHITE, True, width=716)
        txt(d, 1080, 507, "Reply by email to the customer,\nor comment on the internal ticket?", 34, "#d3dfdc", width=716, leading=1.5)
        d.rounded_rectangle((1080, 667, 1797, 762), 15, fill="#29434a")
        txt(d, 1115, 695, "0 writes while awaiting clarification", 32, "#8bdbcc", True)
    else:
        txt(d, 1110, 490, "Scope unresolved", 45, GOLD, True)


def components(d, p, t, beat):
    items = [
        ("DATASET / SAMPLE", "One email case", "User request + workspace.\nA separate state per trial."),
        ("SETUP SOLVER", "Prepare the boundary", "Compile scope. Deliver\nadvice before generation."),
        ("MODELS", "Provider + settings", "Reuse Inspect model APIs\nand generation controls."),
        ("AGENTS", "Built-in ReAct", "Let Inspect run the loop.\nAdd between-turn feedback."),
        ("TOOLS", "Mail + ticket actions", "Custom tools, or MCP\nwith local execution."),
        ("SCORERS", "Assess the outcome", "Verify committed effects\nand authorized completion."),
    ]
    active = min(5, int(p * 6))
    for i, item in enumerate(items):
        x = 72 + (i % 3) * 604
        y = 300 + (i // 3) * 247
        node(d, (x, y, x + 568, y + 220), *item, color=VIOLET, active=i == active)
    card(d, (72, 805, 1848, 875), fill=PALE_TEAL, outline=TEAL)
    txt(d, 106, 822, "CONTAINMENT ADDS:  scope contract  +  Grant Look-ahead  +  Effect Journal", 31, TEAL, True)


def inspect(d, p, t, beat):
    boxes = [(72, 335, 467, 621), (532, 335, 927, 621), (992, 335, 1387, 621), (1452, 335, 1848, 621)]
    labels = [("01 / SETUP SOLVER", "Scope + first advice", "Sample-local state.\nInitial planner guidance."),
              ("02 / REACT AGENT", "Native tool loop", "Model chooses the next\naction or submits."),
              ("03 / CUSTOM OR MCP", "Execute + record", "Local execution binding.\nBackend retains receipt."),
              ("04 / CONTINUATION", "Journal + advice", "Return feedback before\nthe next decision.")]
    selected = min(3, int(p * 4))
    for i, (box, label) in enumerate(zip(boxes, labels)):
        node(d, box, *label, color=VIOLET, active=i == selected)
    for i in range(3):
        a,b=(boxes[i][2]+8,478),(boxes[i+1][0]-8,478)
        line(d,a,b,VIOLET)
        packet(d,a,b,t/2,VIOLET,6)
    card(d, (532, 691, 1387, 862), fill=PALE_VIOLET, outline=VIOLET)
    txt(d, 568, 717, "OPTIONAL APPROVER / BEFORE EXECUTION", 23, VIOLET, True)
    txt(d, 568, 765, "Policy checks or a request for permission", 34, INK, True)
    txt(d, 568, 813, "A separate layer from planner advice and effect logging", 25, MUTED)
    d.line([(1370, 716),(1421,716),(1421,660),(1190,660),(1190,622)], fill=VIOLET, width=3)
    txt(d, 75, 725, "End of run", 29, VIOLET, True)
    txt(d, 75, 768, "Scorer reads the\ncommitted effects.", 29, MUTED)


def operations(d, p, t, beat):
    card(d, (72, 300, 906, 728))
    txt(d, 108, 328, "RUNNING / EVAL SET", 24, VIOLET, True)
    txt(d, 108, 379, "Same tasks × models × feedback arms", 33, INK, True)
    arms = ["Plain", "Planner", "Journal", "Both"]
    for i, arm in enumerate(arms):
        txt(d, 247 + i * 151, 446, arm, 25, MUTED, True)
    for j, label in enumerate(["Model A", "Model B"]):
        txt(d, 108, 507 + j * 91, label, 26, INK, True)
        for i in range(4):
            x, y = 245 + i * 151, 499 + j * 91
            active = (int(t * .7) % 8) == j * 4 + i
            d.rounded_rectangle((x, y, x + 126, y + 59), 12, fill=PALE_VIOLET if active else BG, outline=VIOLET if active else LINE, width=2)
            txt(d, x + 27, y + 17, "trial", 24, VIOLET if active else MUTED)
    txt(d, 108, 677, "Separate workspaces; explicit execution limits", 26, MUTED)
    card(d, (970, 300, 1848, 728))
    txt(d, 1006, 328, "ANALYSIS / ILLUSTRATED LOG CONTENT", 24, VIOLET, True)
    rows = [("Tool proposal", "email_reply(message-01)"),
            ("Service receipt", "reply committed"),
            ("Feedback", "within scope → FINISH"),
            ("Outcome", "authorized completion")]
    for i, (key, value) in enumerate(rows):
        y = 403 + i * 71
        d.line((1007, y + 55, 1813, y + 55), fill=LINE, width=1)
        txt(d, 1006, y, key, 26, MUTED, True)
        txt(d, 1275, y, value, 27, TEAL if i == 3 else INK)
    card(d, (72, 774, 1848, 875), fill=PALE_VIOLET, outline=VIOLET)
    txt(d, 108, 797, "Inspect View", 31, VIOLET, True)
    txt(d, 492, 797, "samples_df() + events_df()", 29, VIOLET, True, mono=True)
    txt(d, 1340, 797, "Transcript scanners", 31, VIOLET, True)
    txt(d, 108, 840, "Inspect individual decisions", 22, MUTED)
    txt(d, 492, 840, "Compare outcomes and retain unknowns", 22, MUTED)
    txt(d, 1340, 840, "Assist with trace review", 22, MUTED)


def packaging(d, p, t, beat):
    card(d, (72, 300, 650, 700), fill=PALE_TEAL, outline=TEAL)
    txt(d, 108, 330, "CONTAINMENT PACKAGE", 24, TEAL, True)
    for i, value in enumerate(["Task + setup solver", "Tool bindings + scorer", "Optional approver", "Monitoring hooks"]):
        yy = 403 + i * 64
        check(d, 108, yy + 1)
        txt(d, 159, yy, value, 31, INK, True)
    node(d, (774, 300, 1224, 700), "INSPECT EXTENSIONS", "Registry + entry point", "Discover packaged\ncomponents at startup.\n\nThe task explicitly\nconnects them.", VIOLET, True)
    node(d, (1348, 300, 1848, 700), "SUPPORTED MAIL TASK", "Convenient launch", "Select the model, tools\nand feedback condition.\n\nConfigure credentials\nfor a real service.", VIOLET, p > .4)
    for a, b in [((669, 494), (755, 494)), ((1243, 494), (1329, 494))]:
        line(d, a, b, VIOLET)
        packet(d, a, b, t / 2, VIOLET, 7)
    card(d, (72, 750, 1848, 875))
    txt(d, 108, 772, "ADD WHEN THE TASK NEEDS IT", 23, MUTED, True)
    txt(d, 108, 818, "Attachments → multimodal     Separate roles → multi-agent     Untrusted code → sandbox", 30, INK, True)


def crux(d, p, t, beat):
    stages = [(72, "Define the study", "Choose tasks and\nfeedback conditions."),
              (534, "Run realistic work", "Observe long tasks\nand interventions."),
              (996, "Retain evidence", "Save tool effects,\nclarifications and logs."),
              (1458, "Review behavior", "Compare decisions,\ncompletion and scope.")]
    d.line((250, 361, 1660, 361), fill=LINE, width=7)
    active = min(3,int(p * 4))
    d.line((250,361,250+1410*p,361), fill=VIOLET, width=7)
    for i, (x,title,body) in enumerate(stages):
        d.ellipse((x+146,330,x+208,392), fill=VIOLET if i<=active else LINE)
        txt(d,x+165,339,str(i+1),30,WHITE,True)
        node(d,(x,432,x+390,699),f"STEP {i+1}",title,body,VIOLET,active=i==active)
    card(d,(72,755,1848,870),fill=PALE_VIOLET,outline=VIOLET)
    txt(d,110,776,"RESEARCH QUESTION",22,VIOLET,True)
    txt(d,110,817,"Does feedback change the agent’s decisions and observed effects during realistic work?",32,INK,True)


def ready(d, p, t, beat):
    card(d,(72,307,920,805),fill=PALE_TEAL,outline=TEAL)
    card(d,(1000,307,1848,805),fill=WHITE)
    txt(d,110,338,"RUNS TODAY",25,TEAL,True)
    txt(d,1038,338,"STILL TO BUILD",25,VIOLET,True)
    left=[("Grant Look-ahead","Advice over modeled, authorized writes"),
          ("Effect Journal","Feedback after committed operations"),
          ("Local mail fixture","Reproducible scripted code replay")]
    right=[("General Inspect adapter","Setup, loop feedback and tool bindings"),
           ("Effect collection + approvals","Service-specific execution integration"),
           ("CRUX-style deployment","Experimental protocol and observation")]
    for x, rows, color in [(110,left,TEAL),(1038,right,VIOLET)]:
        for i,(title,body) in enumerate(rows):
            yy=416+i*119
            if color==TEAL:
                check(d,x,yy+4)
            else:
                d.ellipse((x,yy+4,x+34,yy+38),outline=color,width=3)
            txt(d,x+53,yy,title,34,INK,True)
            txt(d,x+53,yy+50,body,27,MUTED,width=660)
    txt(d,75,844,"Existing Inspect adapter: legacy ImpossibleBench-specific runner",27,MUTED)
    pill(d,1348,831,"Not one-click yet",VIOLET,PALE_VIOLET,27)


RENDERERS = {f.__name__: f for f in [intro, context, request, scope, send, journal, extra, ambiguous, components, inspect, operations, packaging, crux, ready]}


def run(args, **kwargs):
    subprocess.run(args, check=True, **kwargs)


def synthesize():
    """Cache each utterance, then create one precisely timed narration track."""
    BUILD.mkdir(exist_ok=True)
    all_samples = bytearray()
    timeline, captions = [], []
    rate = 22050
    sample_pos = 0
    transcript = ["Containment-extension: an email workflow\n",
                  "Executed local fixture. Scripted actor. Declared scope. No live email sent.\n"]
    for index, scene in enumerate(STORY):
        start = sample_pos / rate
        utterances = []
        transcript.append(f"\n{index+1:02d}. {scene['title']}\n")
        for sentence in scene["lines"]:
            key = hashlib.sha256(("Samantha/165/" + sentence).encode()).hexdigest()[:16]
            source, aiff, wav = [BUILD / (key + suffix) for suffix in [".txt", ".aiff", ".wav"]]
            if not wav.exists():
                source.write_text(sentence)
                run(["say", "-v", "Samantha", "-r", "165", "-o", str(aiff), "-f", str(source)])
                run(["ffmpeg", "-y", "-v", "error", "-i", str(aiff), "-ac", "1", "-ar", str(rate), "-c:a", "pcm_s16le", str(wav)])
            # A brief lead-in and short sentence gap keep narration readable.
            gap = .32 if not utterances else .28
            count = round(gap * rate)
            all_samples.extend(b"\0\0" * count)
            sample_pos += count
            with wave.open(str(wav), "rb") as w:
                assert w.getframerate() == rate and w.getsampwidth() == 2 and w.getnchannels() == 1
                frames = w.readframes(w.getnframes())
            begin = sample_pos / rate
            all_samples.extend(frames)
            sample_pos += len(frames) // 2
            end = sample_pos / rate
            utterances.append({"start": begin - start, "end": end - start, "text": sentence})
            captions.append({"start": begin, "end": end + .18, "text": sentence})
            transcript.append(sentence)
        end_frame = math.ceil((sample_pos / rate + .7) * FPS)
        end_samples = round(end_frame * rate / FPS)
        all_samples.extend(b"\0\0" * (end_samples - sample_pos))
        sample_pos = end_samples
        timeline.append({**scene, "start": start, "end": sample_pos / rate, "utterances": utterances})
        print(f"Narration {index+1}/{len(STORY)}: {scene['id']} ({sample_pos/rate-start:.1f}s)", flush=True)
    with wave.open(str(BUILD / "narration.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(all_samples)
    (HERE / "narration.txt").write_text("\n".join(transcript) + "\n")
    (HERE / "timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False) + "\n")
    def stamp(seconds):
        millis=round(seconds*1000)
        hours,millis=divmod(millis,3600000)
        minutes,millis=divmod(millis,60000)
        secs,millis=divmod(millis,1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
    (HERE / "captions.srt").write_text("\n".join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(captions,1)))
    return timeline


def frame(scene, local, global_time, total):
    im = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(im)
    header(d, scene)
    duration = scene["end"] - scene["start"]
    p = min(1,local/duration)
    beat = max([i for i,u in enumerate(scene["utterances"]) if local >= u["start"]] or [0])
    RENDERERS[scene["id"]](d,p,local,beat)
    # Constant provenance prevents a realistic client mockup being mistaken for
    # a screen recording of an actual Inspect integration or live mail account.
    footer = "LOCAL REPLAY  ·  Scripted actor  ·  Declared scope  ·  Structural effects only" if scene["mode"] == "LOCAL CODE REPLAY" else "CONTAINMENT-EXTENSION  ·  Architecture + workflow demonstration"
    txt(d,74,903,footer,20,MUTED)
    d.rectangle((0,945,W,H),fill=INK)
    caption = next((u["text"] for u in scene["utterances"] if u["start"]-.08 <= local <= u["end"]+.22), "")
    if caption:
        f=font(31)
        lines=wrap(d,caption,f,1660)
        assert len(lines)<=2, (scene["id"],lines)
        yy=981 if len(lines)==1 else 960
        for value in lines:
            x=(W-d.textlength(value,font=f))/2
            txt(d,x,yy,value,31,WHITE)
            yy+=41
    d.rectangle((0,1068,W,1080),fill="#334850")
    d.rectangle((0,1068,max(1,round(W*global_time/total)),1080),fill="#72d3bd")
    return im


def previews(timeline):
    total=timeline[-1]["end"]
    sheet=Image.new("RGB",(1440,math.ceil(len(timeline)/2)*438),"#e8e7df")
    sd=ImageDraw.Draw(sheet)
    for index,scene in enumerate(timeline):
        local=(scene["end"]-scene["start"])*.70
        im=frame(scene,local,scene["start"]+local,total)
        im.save(BUILD/f"preview-{scene['id']}.png")
        sheet.paste(im.resize((704,396)),((index%2)*720+8,(index//2)*438+8))
        sd.text(((index%2)*720+15,(index//2)*438+408),f"{index+1:02} / {scene['id']}",font=font(21,True),fill=INK)
    sheet.save(HERE/"storyboard-preview.jpg",quality=88)
    scene=timeline[0]
    poster=frame(scene,3,0,total)
    pd=ImageDraw.Draw(poster)
    pd.rectangle((0,945,W,H),fill=INK)
    txt(pd,74,980,"ENGLISH NARRATION + CAPTIONS   /   A REPRODUCIBLE LOCAL CODE REPLAY",31,WHITE,True)
    poster.save(HERE/"poster.jpg",quality=92)


def encode(timeline):
    total=timeline[-1]["end"]
    count=round(total*FPS)
    movie=HERE/"containment-mail-workflow.mp4"
    args=["ffmpeg","-y","-v","warning","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
          "-i",str(BUILD/"narration.wav"),"-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-threads","4",
          "-c:a","aac","-b:a","128k","-ar","48000","-af","loudnorm=I=-16:TP=-1.5:LRA=9","-movflags","+faststart",
          "-metadata","title=Containment-extension: an email workflow",
          "-metadata","comment=Executed local fixture; scripted actor; declared scope; no live email. Proposed Inspect/CRUX integration is not implemented.",
          "-shortest",str(movie)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE)
    scene_index=0
    previous=None
    for f in range(count):
        now=f/FPS
        while scene_index+1<len(timeline) and now>=timeline[scene_index]["end"]-.0001:
            scene_index+=1
            print(f"Rendering {scene_index+1}/{len(timeline)}: {timeline[scene_index]['id']}",flush=True)
        scene=timeline[scene_index]
        local=now-scene["start"]
        im=frame(scene,local,now,total)
        # Crossfade for 0.3 seconds between scenes; motion continues within each.
        if local<.3 and previous is not None:
            im=Image.blend(previous,im,ease(local/.3))
        if scene["end"]-now<=1/FPS+.0001:
            previous=im.copy()
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    code=proc.wait()
    if code:
        raise RuntimeError(f"ffmpeg failed: {code}")
    print(f"Wrote {movie} ({total:.2f}s, {movie.stat().st_size/1e6:.1f} MB)",flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preview",action="store_true",help="Render narration and storyboard only")
    ap.add_argument("--reuse-narration",action="store_true")
    args=ap.parse_args()
    for name in ["ffmpeg","say"]:
        if not shutil.which(name):
            raise RuntimeError(f"Missing {name}; this narration builder uses macOS say.")
    timeline=json.loads((HERE/"timeline.json").read_text()) if args.reuse_narration else synthesize()
    previews(timeline)
    if not args.preview:
        encode(timeline)


if __name__=="__main__":
    main()
