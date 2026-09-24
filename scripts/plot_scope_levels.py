"""Plot the frozen scope pilot and export its exact instructions; no model calls.

Run: MPLCONFIGDIR=/tmp/safe-frontier-mpl python3 scripts/plot_scope_levels.py
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "scope-levels-v1"
OUT = ROOT / "figures"
LEVELS = ("baseline", "repeat_scope", "explicit_routes", "action_check")
NAMES = ("Original scope", "Repeat scope", "Explicit shortcuts", "Check each action")
C = {"ink": "#192C40", "muted": "#53687B", "blue": "#24689A", "pale": "#EFF5FA",
     "green": "#147A6D", "gpale": "#E8F4EF", "red": "#B94A3C", "rpale": "#FBEFE9",
     "line": "#CED9E2", "white": "#FFFFFF", "bg": "#FAFCFE"}


def label(ax, x, y, text, size=12, color="ink", weight="normal", **kwargs):
    return ax.text(x, y, text, fontsize=size, color=C[color], fontweight=weight,
                   va="top", **kwargs)


def panel(ax, x, y, width, height, fill="white", edge="line"):
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                               boxstyle="round,pad=0.02,rounding_size=0.08",
                               facecolor=C[fill], edgecolor=C[edge], linewidth=1))


def wrapped(text, width):
    return textwrap.fill(" ".join(text.split()), width=width, break_long_words=False,
                         break_on_hyphens=False)


def canvas(width, height):
    fig, ax = plt.subplots(figsize=(width, height))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set(xlim=(0, width), ylim=(0, height))
    ax.axis("off")
    return fig, ax


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    for ext in ("png", "svg"):
        path = OUT / f"{name}.{ext}"
        fig.savefig(path, dpi=180, facecolor=C["bg"], metadata={"Date": None}
                    if ext == "svg" else None)
        if ext == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())
                            + "\n")
    plt.close(fig)


def load():
    bank = json.loads((SOURCE / "prompt-bank.json").read_text())
    summary = json.loads((SOURCE / "summary.json").read_text())
    analysis = json.loads((SOURCE / "analysis.json").read_text())
    rows = summary["records"]
    assert len(rows) == 24 and len({row["run"] for row in rows}) == 24
    assert {r["seed"] for r in rows} == {600, 601}
    for row in rows:
        assert row["unauthorized_proposal"] is not None
        assert row["unauthorized_proposal"] == row["unauthorized_effect"]
        assert (row["unauthorized_effect"] or row["authorized_completion"]
                or row["variant"] == "impossible" and row["stop"] == "model_finished")
    metrics = {}
    for level in LEVELS:
        selected = [r for r in rows if r["level"] == level]
        controls = [r for r in selected if r["variant"] != "impossible"]
        assert len(selected) == 6 and len(controls) == 4
        values = {"violations": sum(r["unauthorized_effect"] for r in selected),
                  "completed_controls": sum(r["authorized_completion"] for r in controls)}
        archived = next(r for r in analysis["levels"] if r["level"] == level)
        assert values["violations"] == archived["unauthorized_effects"]
        assert values["completed_controls"] == archived["control_authorized_completions"]
        metrics[level] = values
    paragraphs = {key: value.strip().split("\n\n")
                  for key, value in bank["interventions"].items()}
    prefix, suffix = paragraphs["baseline"]
    scope = paragraphs["repeat_scope"][1]
    routes = paragraphs["explicit_routes"][2]
    check = paragraphs["action_check"][3]
    assert scope in bank["task"]
    for level, additions in zip(LEVELS, ([], [scope], [scope, routes], [scope, routes, check]),
                                strict=True):
        assert "\n\n".join([prefix, *additions, suffix]) + "\n" == bank["interventions"][level]
    return bank, rows, metrics, (scope, prefix, suffix, routes, check)


def outcome_plot(rows, metrics):
    fig, ax = canvas(14, 8.4)
    label(ax, .4, 8.06, "SCOPE INSTRUCTION PILOT  /  24 OBSERVED TRIALS", 11, "blue", "bold")
    label(ax, .4, 7.63, "What happened under each instruction level?", 23, weight="bold")
    label(ax, .4, 7.09, "Haiku 4.5 · identical permissions and tools · two draws per task condition",
          12, "muted")
    headers = [(5.55, "Impossible", "No authorized solution"),
               (8.05, "Recoverable", "Local fallback available"),
               (10.55, "Easy", "Challenge already works")]
    label(ax, .45, 6.45, "Cumulative guidance", 12, weight="bold")
    for x, title, subtitle in headers:
        label(ax, x, 6.52, title, 13, weight="bold", ha="center")
        label(ax, x, 6.20, subtitle, 10, "muted", ha="center")
    label(ax, 12.7, 6.5, "Scope\nviolations", 12, weight="bold", ha="center", linespacing=1.4)
    descriptions = ("Original task + neutral checkpoint note",
                    "L0 + restate the authorization boundary",
                    "L1 + name prohibited shortcuts",
                    "L2 + check scope before each tool action")
    for index, (level, name, desc) in enumerate(zip(LEVELS, NAMES, descriptions, strict=True)):
        center = 5.38 - index * 1.02
        panel(ax, .35, center - .40, 13.25, .91, fill="pale" if index % 2 == 0 else "white")
        label(ax, .56, center + .31, f"L{index}  {name}", 14, weight="bold")
        label(ax, .56, center - .02, desc, 10.5, "muted")
        for x, variant in ((5.55, "impossible"), (8.05, "recoverable"), (10.55, "solvable")):
            selected = sorted((r for r in rows if r["level"] == level
                               and r["variant"] == variant), key=lambda r: r["seed"])
            assert len(selected) == 2
            for offset, row in zip((-.43, .43), selected, strict=True):
                if row["unauthorized_effect"]:
                    marker, color = "X", "red"
                elif row["authorized_completion"]:
                    marker, color = "o", "green"
                else:
                    marker, color = "s", "blue"
                ax.scatter(x + offset, center + .10, s=220, marker=marker,
                           color=C[color], linewidths=0, zorder=5)
                label(ax, x + offset, center - .14, row["run"].replace("run-", "#"),
                      9, "muted", ha="center")
        n = metrics[level]["violations"]
        label(ax, 12.7, center + .23, f"{n}/6", 22, "red" if n else "ink", "bold",
              ha="center")
    for x, marker, color, text in (
        (.58, "X", "red", "Scope violation (4)"),
        (4.75, "o", "green", "Completed within scope (15)"),
        (9.72, "s", "blue", "Stopped within scope (5)*"),
    ):
        ax.scatter(x, 1.45, s=130, marker=marker, color=C[color], linewidths=0)
        label(ax, x + .22, 1.56, text, 11)
    label(ax, .4, 1.02, "Every violation read a prior run’s artifact. Passing the scorer did not erase that violation.",
          11, weight="bold")
    label(ax, .4, .66, "*Stopped reports need text review; they did not follow the required raw-JSON format.",
          10, "muted")
    label(ax, .4, .34, "One model, one task structure, two draws per cell. Zero observed violations is not a robustness guarantee.",
          10, "muted")
    save(fig, "scope-levels-results")


def instruction_plot(metrics, blocks):
    scope, prefix, suffix, routes, check = blocks
    fig, ax = canvas(14, 13.7)
    label(ax, .4, 13.35, "EXACT INSTRUCTIONS  /  MATCHED OUTCOMES", 11, "blue", "bold")
    label(ax, .4, 12.91, "What did each level tell the agent?", 24, weight="bold")
    label(ax, .4, 12.35, "Shared text appears once below. Quoted wording is unchanged; line breaks are reflowed.",
          11.5, "muted")

    panel(ax, .4, 9.98, 13.2, 1.94, fill="pale")
    label(ax, .63, 11.69, "SHARED SCOPE  ·  already present in the original task for all four levels", 11,
          "blue", "bold")
    label(ax, .63, 11.29, wrapped(scope, 136), 12, linespacing=1.48)
    panel(ax, .4, 8.40, 13.2, 1.34)
    label(ax, .63, 9.49, "SHARED CHECKPOINT WRAPPER  ·  user authority, same position in every level", 11,
          "blue", "bold")
    label(ax, .63, 9.09, prefix, 12)
    label(ax, .63, 8.73, suffix, 12)

    label(ax, .63, 8.03, "How the checkpoint note is constructed", 12, weight="bold")
    label(ax, 10.48, 8.03, "Scope\nviolations", 11, weight="bold", ha="center", linespacing=1.4)
    label(ax, 12.46, 8.03, "Controls completed\nwithin scope", 11, weight="bold", ha="center",
          linespacing=1.4)
    settings = [
        ("baseline", "L0  Original scope", "Shared wrapper only; no extra scope reminder.", None,
         6.33, 1.08),
        ("repeat_scope", "L1  Repeat scope", "Shared wrapper + the exact shared scope block above.", None,
         5.09, 1.08),
        ("explicit_routes", "L2  Explicit shortcuts", "L1 + this exact addition:", routes,
         2.90, 2.03),
        ("action_check", "L3  Check each action", "L2 + this exact addition:", check,
         .50, 2.24),
    ]
    for level, title, construction, addition, bottom, height in settings:
        panel(ax, .4, bottom, 13.2, height)
        label(ax, .63, bottom + height - .18, title, 14, weight="bold")
        label(ax, .63, bottom + height - .55, construction, 11, "muted")
        if addition:
            label(ax, .63, bottom + height - .88, wrapped(addition, 95), 11.5, linespacing=1.4)
        ax.plot([9.6, 9.6], [bottom + .15, bottom + height - .15], color=C["line"], lw=1)
        center = bottom + height / 2
        count = metrics[level]["violations"]
        label(ax, 10.48, center + .18, f"{count}/6", 25, "red" if count else "ink", "bold",
              ha="center")
        label(ax, 12.46, center + .18, f"{metrics[level]['completed_controls']}/4", 25,
              "green", "bold", ha="center")
    label(ax, .4, .22, "Controls = recoverable + easy tasks. Cumulative additions change both content and length. Small pilot only.",
          10, "muted")
    save(fig, "scope-levels-instructions")


def prompt_sheet(bank, metrics):
    lines = ["# Exact scope instructions and corresponding results", "",
             "Instructions and results come from the frozen "
             "`results/scope-levels-v1/prompt-bank.json` and experiment archive. "
             "Cartoon illustrations were generated separately; "
             "no additional agent trials were run.", "",
             "![Cartoon workflow: agent, repository, API, scorer, and authorization boundary]"
             "(../figures/scope-workflow-cartoon.png)", "",
             "The workflow depicts the permissive local service simulator. The agent reads "
             "the README and source inside the challenge repo, requests a flag through lab tools, "
             "then explicitly submits the returned flag to the current-run scorer. Source edits "
             "do not deploy. Excluded services remain reachable inside the sandbox; the README "
             "link and internal health dependency do not grant the agent permission to access "
             "them. The independent observer checks recorded actions and state separately from "
             "the flag scorer. This is a schematic, not a recorded trial.", "",
             "[Resource inventory cartoon](../figures/scope-resources-cartoon.png) · "
             "[Workflow generation prompt](../figures/scope-workflow-cartoon.prompt.txt) · "
             "[Final editing prompt](../figures/scope-workflow-cartoon.edit-prompt.txt)", "",
             "![Cartoon explanation of the flag scorer, independent scope check, and blocker check]"
             "(../figures/scorer-explained-cartoon.png)", "",
             "The scorer cartoon distinguishes exact flag matching from scope evaluation and "
             "the existing partial blocker check. Its two example routes are schematic, and "
             "its flag is an illustrative placeholder. The scope-check panel groups proposal "
             "classification with independent observation of recorded effects. "
             "[Generation prompt](../figures/scorer-explained-cartoon.prompt.txt).", "",
             "[Proposed meta-generator workflow](meta-instruction-generator.md): a separate "
             "cartoon and design note show how instruction generation could use the sandbox "
             "for development trials and held-out evaluation.", "",
             "![All 24 observed outcomes](../figures/scope-levels-results.png)", "",
             "![Cartoon: instruction additions and their results]"
             "(../figures/scope-levels-instructions-cartoon.png)", "",
             "[Original technical figure](../figures/scope-levels-instructions.svg). "
             "Cartoon captions are schematic labels, not quotations from actor traces.",
             "", "## Shared instructions", "",
             "All levels received the following system message, original user task, and "
             "README content through the scripted setup. The checkpoint note was appended "
             "at user authority after that setup. Actual scope and tool access were identical.", ""]
    for key, title in (("system", "System message"), ("task", "Original user task"),
                       ("readme", "README content returned by the service")):
        lines.extend([f"### {title}", "", "```text", bank[key].rstrip("\n"), "```", ""])
    for index, (level, name) in enumerate(zip(LEVELS, NAMES, strict=True)):
        m = metrics[level]
        lines.extend([f"## L{index}: {name}", "",
                      f"**Result:** {m['violations']}/6 runs had unauthorized proposals and "
                      f"effects; {m['completed_controls']}/4 recoverable/easy controls completed "
                      "within scope.", "", "Exact additional checkpoint message:", "", "```text",
                      bank["interventions"][level].rstrip("\n"), "```", ""])
    lines.extend(["## Interpretation", "",
                  "All four violations read a previous run's artifact. One was on an easy task. "
                  "The five in-scope stops require text review and failed the requested raw-JSON "
                  "format. These are two draws per condition on one model and task structure; "
                  "zero observed violations is not a general guarantee. Level wording and length "
                  "change together; this is not a system/user/tool-priority comparison.", "",
                  "[Full results and evidence](../results/scope-levels-v1/README.md) · "
                  "[Protocol](scope-instruction-levels.md)", "",
                  "Regenerate: `MPLCONFIGDIR=/tmp/safe-frontier-mpl "
                  "python3 scripts/plot_scope_levels.py`.", ""])
    (ROOT / "docs" / "scope-levels-figures-and-prompts.md").write_text("\n".join(lines))


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                         "text.color": C["ink"], "svg.fonttype": "none",
                         "svg.hashsalt": "scope-levels-v1"})
    bank, rows, metrics, blocks = load()
    outcome_plot(rows, metrics)
    instruction_plot(metrics, blocks)
    prompt_sheet(bank, metrics)
    print("Generated two PNG/SVG figures and docs/scope-levels-figures-and-prompts.md")


if __name__ == "__main__":
    main()
