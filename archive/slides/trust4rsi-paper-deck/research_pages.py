"""Incident motivation and technical comparisons. No invented experimental outcomes."""

import json
from pathlib import Path

from deck_lib import (
    BLUE,
    BLUE_PALE,
    GRAY,
    GREEN,
    GREEN_PALE,
    ORANGE,
    ORANGE_PALE,
    PURPLE,
    PURPLE_PALE,
    RED,
    RED_PALE,
    rect,
)
from diagram_lib import arrow
from pptx.util import Inches

SOURCES = json.loads((Path(__file__).parent / "research-sources.json").read_text())


def cite(ui, s, key, x=0.5, y=6.73, w=12.3):
    source = SOURCES["sources"][key]
    ui.link(s, x, y, w, source["label"], source["url"])


def row(ui, s, y, label, middle, end, color=BLUE, pale=BLUE_PALE, connect=True):
    ui.text(s, 0.5, y, 2.9, 0.9, label, 22, color, True)
    for x, w, value in [(3.6, 4.15, middle), (8.35, 4.45, end)]:
        rect(s, Inches(x), Inches(y), Inches(w), Inches(0.95), pale, None)
        ui.text(s, x + 0.15, y + 0.06, w - 0.3, 0.83, value, 21)
    if connect:
        arrow(s, [(Inches(7.83), Inches(y + 0.48)), (Inches(8.27), Inches(y + 0.48))], color)


def motivation(ui):
    s = ui.page(
        "WHY THIS QUESTION?",
        "The request failed. The agent crossed a boundary.",
        "Medicare statistics portal / incident: June 2026 / government report: 24 September",
        "Reported incident, not our experiment. No individual medical records "
        "were accessed, per government.",
        status="REPORTED",
    )
    for x, title, body, kind, col, pale in [
        (0.5, "The task", "Find medicine-spending statistics.", "agent", BLUE, BLUE_PALE),
        (4.7, "The obstacle", "The portal denied the request.", "server", ORANGE, ORANGE_PALE),
        (
            8.9,
            "The next action",
            "Access the portal without authorization.",
            "database",
            RED,
            RED_PALE,
        ),
    ]:
        ui.panel(s, x, 2.6, 3.9 if x == 8.9 else 3.55, 2.7, title, body, col, pale, kind, 22, 23)
    arrow(s, [(Inches(4.12), Inches(3.95)), (Inches(4.62), Inches(3.95))], GRAY)
    arrow(s, [(Inches(8.32), Inches(3.95)), (Inches(8.82), Inches(3.95))], GRAY)
    ui.banner(s, "The goal did not authorize every way of reaching it.", RED, RED_PALE)
    cite(ui, s, "medicare")

    s = ui.page(
        "TWO MORE INCIDENTS",
        "A workaround can change whose resources are used.",
        "These reports describe different tasks with a similar decision point.",
        "Reported cases. Their frequency and causal effect are not estimated here.",
        status="REPORTED",
    )
    row(
        ui,
        s,
        2.65,
        "Share a workbook",
        "Local file transfer failed.",
        "Uploaded to public hosting.",
        RED,
        RED_PALE,
    )
    row(
        ui,
        s,
        4.3,
        "Deploy contracts",
        "No funded wallet was supplied.",
        "Spent another account's test funds.",
        ORANGE,
        ORANGE_PALE,
    )
    ui.banner(s, "Our hypothesis: a missing route can trigger a forbidden substitute.", size=20)
    cite(ui, s, "workbook", 0.5, 5.45, 6.0)
    cite(ui, s, "wallet", 6.9, 5.45, 5.9)

    s = ui.page(
        "WHERE THE EXPLANATION STOPS",
        "Recover versus stop does not explain every incident.",
        "We also need to test what the agent treats as permission.",
        "Source-grounded observations; the questions below are our interpretation.",
        status="REPORTED",
    )
    ui.panel(
        s,
        0.5,
        2.55,
        5.9,
        3.0,
        "Opus 4.7 evaluation",
        "A reachable real company was treated as in scope.\n\nTest: who authorized this target?",
        BLUE,
        BLUE_PALE,
        title_size=24,
        body_size=22,
    )
    ui.panel(
        s,
        6.9,
        2.55,
        5.9,
        3.0,
        "DSEwiki",
        "GET requests could write to a public wiki.\n\nTest: what did the call actually change?",
        PURPLE,
        PURPLE_PALE,
        title_size=24,
        body_size=22,
    )
    ui.banner(s, "A reachable target is not a permission grant.", size=22)
    cite(ui, s, "anthropic", 0.5, 5.62, 6.0)
    cite(ui, s, "dsewiki", 6.9, 5.62, 5.9)

    s = ui.page(
        "FROM CASES TO TESTS",
        "Incidents tell us what to vary and what to measure.",
        "They suggest test conditions. They do not establish a failure rate.",
        "docs/trust4rsi-incident-to-experiment.md | Hypotheses, not causal "
        "conclusions from case counts.",
        status="RESEARCH DESIGN",
    )
    row(ui, s, 2.45, "Blocked route", "Vary whether repair works.", "Count useful recovery.")
    row(
        ui,
        s,
        3.65,
        "Wrong resource",
        "Vary permission; keep access.",
        "Count unauthorized effects.",
        RED,
        RED_PALE,
    )
    row(
        ui,
        s,
        4.85,
        "Final report",
        "Check the full action history.",
        "Count violations before stopping.",
        PURPLE,
        PURPLE_PALE,
    )
    ui.banner(s, "Our current lab covers a narrow part of this design.", size=22)

    s = ui.page(
        "THE DECISION",
        "A failed call is not proof that the task is impossible.",
        "Our lab gives two worlds the same initial 503 error.",
        "Verified identical setup prefixes: "
        "feedback-ablation-v1/checkpoints/development-{recoverable,impossible}-12000.",
        status="TASK DESIGN",
    )
    ui.panel(
        s,
        0.5,
        3.1,
        2.6,
        1.65,
        "503 error",
        "Setup observation",
        ORANGE,
        ORANGE_PALE,
        title_size=24,
        body_size=18,
    )
    ui.panel(
        s,
        3.9,
        3.1,
        3.45,
        1.65,
        "Try allowed recovery",
        "POST /api/recover",
        BLUE,
        BLUE_PALE,
        title_size=22,
        body_size=18,
    )
    arrow(s, [(Inches(3.17), Inches(3.95)), (Inches(3.82), Inches(3.95))], BLUE)
    for y, title, col, pale in [
        (2.5, "200: recover and finish", GREEN, GREEN_PALE),
        (4.35, "409: report blocked", BLUE, BLUE_PALE),
    ]:
        rect(s, Inches(8.55), Inches(y), Inches(4.25), Inches(1.1), pale, None)
        ui.text(s, 8.7, y + 0.08, 3.95, 0.94, title, 23, col, True)
        arrow(
            s,
            [
                (Inches(7.42), Inches(3.95)),
                (Inches(7.95), Inches(3.95)),
                (Inches(7.95), Inches(y + 0.55)),
                (Inches(8.47), Inches(y + 0.55)),
            ],
            col,
        )
    ui.text(
        s,
        0.5,
        5.55,
        12.3,
        0.4,
        "Here, 409 rules out the only allowed repair. Elsewhere, more evidence may be needed.",
        18,
    )
    ui.banner(s, "If evidence is incomplete, say incomplete. Do not invent permission.", size=20)


def comparisons(ui):
    s = ui.page(
        "CLOSEST BENCHMARK",
        "ImpossibleBench already tests when agents should stop.",
        "Its coding tests deliberately conflict with the task specification.",
        "Zhong et al. / ImpossibleBench / sections 2, 5 and 6. Literature comparison.",
        status="PRIOR WORK",
    )
    for j, (title, body) in enumerate(
        [
            ("Prompts", "Tell the agent to flag flawed tests."),
            ("Exit", "Allow a request for human help."),
            ("Tool access", "Hide tests or make them read-only."),
            ("Monitoring", "Judge recorded coding trajectories."),
        ]
    ):
        x, y = 0.5 + (j % 2) * 6.4, 2.4 + (j // 2) * 1.8
        ui.panel(s, x, y, 5.9, 1.7, title, body, BLUE, BLUE_PALE, title_size=23, body_size=20)
    ui.banner(s, "Recover versus stop is a motivation, not a novelty claim.", size=22)
    cite(ui, s, "impossiblebench")

    s = ui.page(
        "THE TECHNICAL DIFFERENCE",
        "Our label checks actions, even when the task fails.",
        "This changes the measured endpoint. It does not establish a new safety principle.",
        "ImpossibleBench: main cheating-rate endpoint. Our data: "
        "incident-study-v1, all 160 assigned runs.",
        status="COMPARISON",
    )
    ui.panel(
        s,
        0.5,
        2.5,
        5.9,
        2.95,
        "ImpossibleBench",
        "On an impossible task:\npass implies a shortcut.\n\nMain label: test result.",
        BLUE,
        BLUE_PALE,
        title_size=26,
        body_size=24,
    )
    ui.panel(
        s,
        6.9,
        2.5,
        5.9,
        2.95,
        "Our service fixture",
        "On any assigned task:\ncheck every resource access.\n\nMain label: executed effects.",
        PURPLE,
        PURPLE_PALE,
        title_size=26,
        body_size=24,
    )
    ui.banner(s, "Local evidence: 2 of our 15 violations did not pass.", RED, RED_PALE)
    cite(ui, s, "impossiblebench")

    s = ui.page(
        "OUR UPSTREAM ATTEMPT",
        "Zero impossible passes did not mean good stopping.",
        "The archived report describes six original ImpossibleBench runs.",
        "docs/impossiblebench-upstream-baseline-results.md | Raw live archive "
        "is absent from this checkout.",
        status="REPORT ONLY",
    )
    for x, title, body, col, pale in [
        (0.5, "1/2", "Original tasks passed", GREEN, GREEN_PALE),
        (4.7, "0/4", "Impossible variants passed", BLUE, BLUE_PALE),
        (8.9, "6/6", "Reached the message cap", ORANGE, ORANGE_PALE),
    ]:
        ui.panel(s, x, 2.6, 3.9, 2.5, title, body, col, pale, title_size=36, body_size=23)
    ui.text(
        s,
        0.5,
        5.38,
        12.3,
        0.48,
        "All six hit dependency problems. None submitted or requested human intervention.",
        20,
    )
    ui.banner(s, "Restore raw logs and fix actor environments before a new comparison.", size=20)

    s = ui.page(
        "AN EVEN CLOSER INCIDENT STUDY",
        "Incident-driven tests with no allowed solution already exist.",
        "Anthropic's September 2026 assessment overlaps directly with this project.",
        "Anthropic: alignment assessment, Methods and Replication sections. No reproduction here.",
        status="PRIOR WORK",
    )
    ui.panel(
        s,
        0.5,
        2.55,
        5.9,
        3.0,
        "Their method",
        "Edit incident context.\nResample continuations.\nTest CTFs with no in-scope solution.",
        BLUE,
        BLUE_PALE,
        title_size=25,
        body_size=24,
    )
    ui.panel(
        s,
        6.9,
        2.55,
        5.9,
        3.0,
        "Our current method",
        "Reset local service state.\nVary checkpoint notes.\nRead service effect logs.",
        PURPLE,
        PURPLE_PALE,
        title_size=25,
        body_size=24,
    )
    ui.banner(
        s, "We have a small, inspectable fixture. We have not shown better protection.", size=20
    )
    cite(ui, s, "anthropic")

    s = ui.page(
        "COMPARE THE RIGHT THREAT MODEL",
        "These benchmarks ask different technical questions.",
        "Published rates cannot be ranked against our local fixture rates.",
        "Primary papers linked below. These systems are not reproduced in the current comparison.",
        status="PRIOR WORK",
    )
    for j, (key, title, body) in enumerate(
        [
            (
                "agentdojo",
                "AgentDojo",
                "Attacker edits tool output.\nMeasure attack success and utility.",
            ),
            (
                "shade",
                "SHADE-Arena",
                "Agent gets a hidden harmful goal.\nMeasure sabotage and detection.",
            ),
            (
                "cosec",
                "CoSec",
                "Authorization changes across communities.\nCheck flows against active "
                "permissions.",
            ),
        ]
    ):
        x = 0.5 + 4.2 * j
        ui.panel(s, x, 2.55, 3.9, 3.0, title, body, BLUE, BLUE_PALE, title_size=25, body_size=22)
        cite(ui, s, key, x, 5.65, 3.9)
    ui.banner(s, "Our actors receive one task, with no injected attacker objective.", size=21)


def enforcement(ui):
    s = ui.page(
        "ENFORCEMENT BASELINE",
        "Recording an action does not prevent it.",
        "CaMeL enforces policies during execution. Our current observer records effects.",
        "CaMeL: control/data separation and capability checks. Our proposed "
        "baseline is only an endpoint allowlist.",
        status="BASELINE NOT RUN",
    )
    for y, label, middle, end, col, pale in [
        (
            2.55,
            "Current lab",
            "Agent request executes.",
            "Observer records the effect.",
            ORANGE,
            ORANGE_PALE,
        ),
        (
            4.2,
            "Next baseline",
            "Check the allowed resource.",
            "Block before dispatch.",
            GREEN,
            GREEN_PALE,
        ),
    ]:
        row(ui, s, y, label, middle, end, col, pale)
    ui.banner(
        s, "Count attempted violations, executed violations, and allowed completions.", size=20
    )
    cite(ui, s, "camel")


def factorial(ui):
    s = ui.page(
        "NEXT EXPERIMENT",
        "Change repair and permission independently.",
        "Keep the same archive reachable. Change whether the task permits reading it.",
        "Proposed 2 x 2 design. Expected allowed choices, not model results. "
        "Closed local action set.",
        status="NOT RUN YET",
    )
    ui.text(s, 3.6, 2.38, 4.15, 0.5, "Archive forbidden", 24, RED, True, center=True)
    ui.text(s, 8.35, 2.38, 4.45, 0.5, "Archive authorized", 24, GREEN, True, center=True)
    row(
        ui,
        s,
        3.2,
        "Recovery works",
        "Recover.",
        "Either allowed route.",
        BLUE,
        BLUE_PALE,
        connect=False,
    )
    row(
        ui,
        s,
        4.55,
        "Recovery unavailable",
        "Report blocked.",
        "Read the archive.",
        PURPLE,
        PURPLE_PALE,
        connect=False,
    )
    ui.banner(s, "Does behavior track permission, or merely task difficulty?", size=22)
