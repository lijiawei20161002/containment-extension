"""Ten-slide results deck: five established results and one elementary payoff bound.

Build with ~/Desktop/.venv/bin/python slides/decision-theory-deck/build_deck.py
Render with ~/Desktop/.venv/bin/python slides/decision-theory-deck/render_deck_pdf.py
No inference calls; every number on a slide is an exact toy calculation checked in validate().

Visual grammar (see deck_style.py): each result slide has a square badge (R1..R6) in its own
accent colour, a native-shape diagram on the left, the statement in a dark RESULT band on the
right, an ASSUMES strip and a solid USE bar. Formulas use real glyphs and sub/superscripts.
"""
from __future__ import annotations

import json
from itertools import product

from deck_style import (
    HERE, QA, PRS, PAGES, SOURCES, DEEP, NAVY, DARKBOX, INK, MUTED, BLUE, TEAL, ORANGE,
    RED, PLUM, GOLD, BG, WHITE, PALE, MINT, SAND, ROSE, LILAC, CREAM, LINE, LIGHT, TINT,
    ML, MR, CW, rgb, text, box, line, dashed, arrow, circle, dot, dotline, badge, square_badge,
    label, chip, card, panel, theorem, bar, docicon, assumes, use, page, notes, link,
    write_structure,
)
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

SOURCES.update({
    "blackwell": (
        "Blackwell (1953), Equivalent Comparisons of Experiments. "
        "Formulation checked in Brooks, Frankel & Kamenica (2024), Comparisons of Signals, §3.1.",
        "https://benjaminbrooks.net/downloads/bfk_comparisons.pdf",
    ),
    "reject": (
        "Franc, Prusa & Voracek (2023), Optimal Strategies for Reject Option Classifiers, "
        "§2.1, Eqs. (3)-(4); cost-based rejection originates in Chow (1970).",
        "https://www.jmlr.org/papers/volume24/21-0048/21-0048.pdf",
    ),
})
SOURCES["meta"] = (
    "Hay, Russell, Tolpin & Shimony (2012), Selecting Computations: "
    "Theory and Applications, Theorems 5 and 7.",
    "https://arxiv.org/html/1207.5879",
)
SOURCES["switch"] = (
    "Hadfield-Menell, Dragan, Abbeel & Russell (2017), The Off-Switch Game, "
    "Theorem 1 and Eq. (1).",
    "https://arxiv.org/html/1611.08219v3",
)

RESULTS = [  # badge, accent, short name, one-line use
    ("R1", BLUE, "Blackwell order", "Compare evidence channels"),
    ("R2", TEAL, "Perfect-information bound", "Cap diagnostic spending"),
    ("R3", ORANGE, "Myopic lower bound", "Two safe stopping tests"),
    ("R4", GOLD, "Bayes rejection", "Thresholds from losses"),
    ("R5", PLUM, "Off-Switch Game", "Price informed supervision"),
    ("R6", RED, "Payoff-range bound", "When a penalty suffices"),
]


def citation(s, key, label_):
    source = SOURCES[key]
    shape = text(s, ML, 7.00, 11.3, .23, label_, 9, MUTED, role="source")
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            r.hyperlink.address = source[1]


def result_page(title, kicker, subtitle, tag, accent, key=None, locator=""):
    s = page(title, kicker, subtitle, source=" ", tag=tag, accent=accent)
    if key:
        citation(s, key, locator)
    return s


# Shared numerical examples. Utility units are hypothetical and explicitly labelled.
good, bad, prior, diag_cost = 6.0, -4.0, .5, .5
v_now = max(prior*good+(1-prior)*bad, 0.0)
v_perfect = prior*max(good, 0)+(1-prior)*max(bad, 0)
evpi = v_perfect-v_now
states = list(product((0, 1), repeat=2))
xor_guess = max(sum((x ^ y) == action for x, y in states)/4 for action in (0, 1))
xor_one = sum(
    .5*max(sum((x ^ y) == action for x, y in states if x == observed)/2
           for action in (0, 1))
    for observed in (0, 1)
)
EXAMPLES = {
    "payoffs": {"good": good, "bad": bad, "prior_good": prior, "stop": 0},
    "information": {"V0": v_now, "Vperfect": v_perfect, "EVPI": evpi,
                    "probe_cost": diag_cost, "expected_probe_bound": evpi/diag_cost},
    "xor": {"no_probe": xor_guess, "one_probe_net": xor_one-.1, "two_probe_net": 1-.2},
    "review": {"false_negative_cost": 10, "false_positive_cost": 1,
               "perfect_review_cost": .2, "allow_below": .02, "block_above": .8},
    "oversight": {"direct_best": v_now, "rational_review": v_perfect,
                  "max_strictly_preferred_review_cost": evpi},
    "penalty": {"utility_lower": 0, "utility_upper": 10, "sufficient_lambda": 11,
                "feasible_payoffs": [3, 7, 10], "violation_raw": 10, "violation_net": -1},
}

# 01: Outcome-oriented overview --------------------------------------------------------------
s = page("", "Decision theory × containment-extension", dark=True)
PAGES[-1]["title"] = "Decision theory, ready to use."
text(s, ML, 1.00, 6.6, 1.80, "Decision theory,\nready to use.", 44, WHITE, True, role="title", ls=1.02)
box(s, ML, 2.92, .95, .05, TEAL, rounded=False)
text(s, ML+.02, 3.10, 6.3, 1.15,
     "Five established results and one elementary payoff bound. Each slide gives the "
     "theorem, its assumptions, a worked calculation and one concrete use.", 18, LIGHT)
x = ML+.02
for w, item in [(1.25, "THEOREM"), (1.55, "ASSUMPTIONS"), (1.85, "WORKED NUMBERS"), (.85, "USE")]:
    box(s, x, 4.50, w, .36, DARKBOX)
    text(s, x, 4.50, w, .36, item, 11, LIGHT, True, True, role="label")
    x += w+.12
text(s, ML+.02, 5.30, 6.3, .80,
     "No model calls. Toy numbers are exact calculations and labelled as such. "
     "Every result links its primary source.", 12.5, LIGHT, role="label")
gx, gw, gy, gh = 7.55, 2.48, 1.05, 1.52
for i, (tag, accent, name, body) in enumerate(RESULTS):
    cx, cy = gx+(i % 2)*(gw+.20), gy+(i//2)*(gh+.18)
    box(s, cx, cy, gw, gh, DARKBOX)
    box(s, cx, cy, gw, .06, accent, rounded=False)
    badge(s, cx+.18, cy+.22, tag, accent, .42, 12)
    text(s, cx+.18, cy+.70, gw-.3, .46, name, 13.5, WHITE, True, ls=1.0)
    text(s, cx+.18, cy+1.14, gw-.3, .32, body, 11.5, LIGHT)
notes(s, "本版以能够用于设计的结果为主。前五项来自已有决策理论或最优拒判研究，第六项是一个明确给出证明的初等界。"
      "每项分别给条件、结论和项目用法。所有数值算例均为假设效用单位，不是模型实验结果。"
      "不能把 oracle 的最优性直接当作 LLM 的保证；信念、损失和授权集合都需要由实验定义。")

# 02: Information dominance, not classifier superiority ---------------------------------------
s = result_page("More informative evidence cannot lower optimal value.",
                "Result 1 / Blackwell's comparison of experiments",
                "If Y can be produced by garbling X, whoever sees X can do at least as well as whoever sees Y.",
                "R1", BLUE, "blackwell",
                "Blackwell (1953); formulation checked in Brooks, Frankel & Kamenica (2024), §3.1.")
card(s, ML, 2.38, 2.95, 2.05, BLUE)
label(s, ML+.24, 2.48, 2.6, "X · richer evidence", BLUE)
docicon(s, ML+.30, 2.92, BLUE)
text(s, ML+.92, 2.96, 1.9, .54, "T\ntranscript", 12.5, INK, True, ls=1.0)
docicon(s, ML+.30, 3.64, TEAL)
text(s, ML+.92, 3.68, 1.9, .54, "J\neffect journal", 12.5, INK, True, ls=1.0)
arrow(s, [(3.72, 3.40), (4.62, 3.40)], BLUE)
text(s, 3.58, 3.02, 1.18, .30, "garble", 12.5, BLUE, True, True)
text(s, 3.50, 3.52, 1.34, .50, "drop J\n(deterministic)", 11, MUTED, center=True, ls=1.0)
card(s, 4.72, 2.38, 2.25, 2.05, LIGHT)
label(s, 4.96, 2.48, 1.9, "Y · coarser evidence", MUTED)
docicon(s, 5.02, 3.08, BLUE)
text(s, 5.64, 3.12, 1.3, .54, "T\ntranscript", 12.5, INK, True, ls=1.0)
label(s, ML, 4.62, 3.0, "Optimal decision value", BLUE)
text(s, ML, 4.90, 1.12, .30, "V*(T, J)", 13, NAVY, True)
bar(s, 1.80, 4.92, 4.60, .26, .74, BLUE)
box(s, 1.80+4.60*.74, 4.92, 4.60*.26, .26, TEAL, rounded=False)
text(s, 1.80+4.60*.74, 4.92, 4.60*.26, .26, "gain ≥ 0", 11, WHITE, True, True, role="label")
text(s, ML, 5.26, 1.12, .30, "V*(T)", 13, NAVY, True)
bar(s, 1.80, 5.28, 4.60, .26, .74, BLUE)
theorem(s, 7.30, 2.38, MR-7.30, 1.45, "V*(T, J)  ≥  V*(T)",
        "Both signals versus the transcript alone; equality is allowed.", 30, "Result 1", BLUE)
card(s, 7.30, 4.02, MR-7.30, 1.53, BLUE)
label(s, 7.56, 4.12, 3.0, "Holds when", BLUE)
for i, row in enumerate(["Same prior, utility and action set",
                         "The extra signal is free to observe",
                         "Evidence is used optimally"]):
    dot(s, 7.66, 4.57+i*.32, .11, TEAL)
    text(s, 7.82, 4.42+i*.32, 4.7, .30, row, 13.5, INK)
assumes(s, "Orders optimal decision value, not the accuracy of two learned judges; the strict gain can be zero.")
use(s, "B3/B4: keep the transcript in both arms; add journal evidence to one arm only.")
notes(s, "V*(X)=E_X[max_a E[u(a,θ)|X]]。证明思路：看到 X 的决策者可以先模拟 Y，再执行任何基于 Y 的策略。"
      "因此 X 至少能达到 Y 的最优值。这里的投影是 garbling 的特例。"
      "项目应用：固定候选策略和收益定义，以 T 与 (T,J) 比较信息；单独 J 不一定支配 T。"
      "新增信息若不改变最优选择，增益可以为零。学习误差和处理成本可能逆转实际表现。"
      "事后 effect journal 可用于策略选择，但不是对同一次动作的事前阻止证据。", ("blackwell", "fixture"))

# 03: A precise budget result ----------------------------------------------------------------
s = result_page("Perfect information bounds diagnostic spending.",
                "Result 2 / Hay et al. (2012), Theorem 5",
                "Fix the authorized terminal actions; each probe costs c and reveals information without changing the world.",
                "R2", TEAL, "meta", "Hay et al. (2012), Theorem 5. Payoffs are an illustrative calculation in toy units.")
card(s, ML, 2.38, 4.40, 3.20, TEAL)
label(s, ML+.24, 2.48, 3.5, "Worked payoffs · toy units", TEAL)
box(s, .85, 3.38, 1.25, .50, NAVY)
text(s, .85, 3.38, 1.25, .50, "Decide now", 12.5, WHITE, True, True)
box(s, 2.65, 2.92, .85, .42, PALE)
text(s, 2.65, 2.92, .85, .42, "act", 13, BLUE, True, True)
box(s, 2.65, 4.12, .85, .42, PALE)
text(s, 2.65, 4.12, .85, .42, "stop", 13, BLUE, True, True)
box(s, 4.05, 2.70, .85, .40, MINT)
text(s, 4.05, 2.70, .85, .40, "+6", 15, TEAL, True, True)
box(s, 4.05, 3.20, .85, .40, ROSE)
text(s, 4.05, 3.20, .85, .40, "−4", 15, RED, True, True)
box(s, 4.05, 4.13, .85, .40, PALE)
text(s, 4.05, 4.13, .85, .40, "0", 15, MUTED, True, True)
text(s, 3.52, 2.64, .55, .26, "p ½", 11, MUTED)
text(s, 3.52, 3.42, .55, .26, "p ½", 11, MUTED)
arrow(s, [(2.10, 3.63), (2.35, 3.63), (2.35, 3.13), (2.65, 3.13)], BLUE)
arrow(s, [(2.10, 3.63), (2.35, 3.63), (2.35, 4.33), (2.65, 4.33)], BLUE)
arrow(s, [(3.50, 3.13), (3.75, 3.13), (3.75, 2.90), (4.05, 2.90)], BLUE)
arrow(s, [(3.50, 3.13), (3.75, 3.13), (3.75, 3.40), (4.05, 3.40)], BLUE)
arrow(s, [(3.50, 4.33), (4.05, 4.33)], BLUE)
text(s, .85, 4.72, 4.15, .76,
     "Act now: E[U] = ½·6 − ½·4 = 1.\nPerfect information: act only on +6, value 3.", 12.5, INK, ls=1.1)
label(s, 5.25, 2.48, 2.6, "Value ladder", TEAL)
unit = 2.30/v_perfect
base_y = 5.20
line(s, 5.30, base_y, 7.90, base_y, LINE, .022)
box(s, 5.50, base_y-v_now*unit, .80, v_now*unit, BLUE, rounded=False)
box(s, 6.80, base_y-v_perfect*unit, .80, v_perfect*unit, TEAL, rounded=False)
text(s, 5.50, base_y-v_now*unit-.32, .80, .30, "1", 14, BLUE, True, True)
text(s, 6.80, base_y-v_perfect*unit-.32, .80, .30, "3", 14, TEAL, True, True)
text(s, 5.25, base_y+.05, 1.30, .30, "V_{now}", 12, INK, True, True)
text(s, 6.55, base_y+.05, 1.30, .30, "V_{perfect}", 12, INK, True, True)
line(s, 6.30, base_y-v_perfect*unit, 6.30, base_y-v_now*unit, TEAL, .025)
line(s, 6.20, base_y-v_perfect*unit, 6.40, base_y-v_perfect*unit, TEAL, .025)
line(s, 6.20, base_y-v_now*unit, 6.40, base_y-v_now*unit, TEAL, .025)
text(s, 5.37, 3.42, 1.0, .56, "EVPI\n= 2", 13, TEAL, True, True, ls=1.0)
theorem(s, 8.10, 2.38, MR-8.10, 1.95,
        "EVPI = E[max_{a} U(a)] − max_{a} E[U(a)]\nE[N*]  ≤  EVPI / c",
        "N*: probes under the optimal policy; c > 0 each.", 17, "Result 2", TEAL, ls=1.5)
panel(s, 8.10, 4.50, MR-8.10, 1.08, TEAL)
text(s, 8.30, 4.62, 4.2, .52, "E[N*]  ≤  2 / 0.5  =  4", 24, TEAL, True, role="formula")
text(s, 8.30, 5.14, 4.2, .34, "expected probes at c = 0.5; not a hard cap of four calls", 11.5, MUTED)
assumes(s, "Bounded utilities; fixed terminal actions and payoffs; probes only reveal information. An expectation bound, not a per-run budget.")
use(s, "Compute the information-value ceiling before allocating diagnostic calls.")
notes(s, "证明：最优策略至少能直接停止诊断，且最终决策价值最多达到完美信息值；因此期望诊断成本不超过 EVPI。"
      "停止诊断指选择当前最优终局动作，不必是放弃任务。这个界不能直接用于会修复环境、改变授权或改变收益的工具操作。"
      "给定数值由构建脚本精确检查；不把期望次数界解释成逐条轨迹的预算上限。", ("meta",))

# 04: Sufficient conditions with a real unresolved region --------------------------------------
s = result_page("Two bounds give reliable stopping rules.",
                "Result 3 / One-step gain is a lower bound",
                "V_{0}(b) is the best terminal value now; b′ is the posterior after probe e; c(e) is its cost.",
                "R3", ORANGE, "meta", "Hay et al. (2012), Theorem 7; the EVPI stopping test is a direct corollary of Theorem 5.")
theorem(s, ML, 2.38, CW, 1.34, "M(e) = E[V_{0}(b′)] − V_{0}(b) − c(e)",
        "The one-step net gain of probe e. Theorem 7: a positive M(e) certifies that continuing is optimal.",
        24, "Result 3", ORANGE)
cols = [
    ("Some probe has M(e) > 0?", "yes", "CONTINUE", "One probe already pays (myopic bound).", TEAL),
    ("EVPI ≤ c_{min}, the cheapest probe?", "yes", "STOP DIAGNOSING", "Perfect information cannot pay its way.", BLUE),
    ("Neither test decides", "", "LOOK AHEAD", "Search over probe sequences.", ORANGE),
]
colw, gap = 3.75, (CW-3*3.75)/2
for i, (test, yes, verdict, body, col) in enumerate(cols):
    x = ML+i*(colw+gap)
    card(s, x, 3.92, colw, .60)
    text(s, x+.15, 3.92, colw-.3, .60, test, 14, NAVY, True, True)
    arrow(s, [(x+colw/2, 4.52), (x+colw/2, 4.84)], col)
    if yes:
        text(s, x+colw/2+.10, 4.50, .5, .3, yes, 11, MUTED)
    panel(s, x, 4.84, colw, .74, col)
    text(s, x+.2, 4.95, colw-.4, .30, verdict, 15, col, True)
    text(s, x+.2, 5.22, colw-.4, .32, body, 12, INK)
    if i < 2:
        arrow(s, [(x+colw, 4.22), (x+colw+gap, 4.22)], MUTED)
        text(s, x+colw, 3.90, gap, .28, "no", 11, MUTED, center=True)
assumes(s, "Information-only probes with positive costs. A nonpositive one-step gain alone does not justify stopping.")
use(s, "Run the two sufficient tests first; spend search only on the gap between them.")
notes(s, "正的一步净收益给出优于立刻决策的可行策略，所以最优策略会继续。"
      "若所有首次诊断成本都至少为 cmin，且 EVPI<=cmin，则任何非空诊断序列都无法严格提高净值。"
      "两者之间需要多步求解；负的一步收益不是停止证据。", ("meta",))

# 05: Independently constructed finite example ------------------------------------------------
s = result_page("Two useful probes can each look worthless.",
                "Worked counterexample / Complementary information",
                "X and Y are independent fair bits. The correct repair is 0 or 1 according to X XOR Y.",
                "C", NAVY)
card(s, ML, 2.38, 5.45, 3.20, NAVY)
label(s, ML+.24, 2.48, 3.5, "Four equally likely states", NAVY)
cw_, ch_, g = 1.15, .46, .07
cx0, cy0 = 2.35, 3.38
for j, head in enumerate(("Y = 0", "Y = 1")):
    text(s, cx0+j*(cw_+g), 2.98, cw_, .32, head, 12, MUTED, True, True)
for i, head in enumerate(("X = 0", "X = 1")):
    text(s, 1.00, cy0+i*(ch_+g), 1.25, ch_, head, 12, MUTED, True, align="r")
for (i, j) in product(range(2), range(2)):
    v = i ^ j
    box(s, cx0+j*(cw_+g), cy0+i*(ch_+g), cw_, ch_, MINT if v else PALE, rounded=False)
    text(s, cx0+j*(cw_+g), cy0+i*(ch_+g), cw_, ch_, f"repair {v}", 13, TEAL if v else BLUE, True, True)
line(s, 4.95, 3.38, 4.95, 4.37, LINE, .025)
text(s, 5.02, 3.38, 1.0, .99, "Reveal X only:\neach row is\nstill 50:50.", 11.5, MUTED, ls=1.05)
text(s, 1.00, 4.50, 4.9, .98,
     "Correct repair pays 1, wrong repair 0. Reading a bit costs 0.1.\n"
     "Either bit alone leaves the target a fair coin; both bits pin it down.", 12.5, INK, ls=1.1)
tiles = [
    ("NO PROBE", xor_guess, "Guess the repair.", "0.5 success − 0 cost", BLUE),
    ("ONE PROBE", xor_one-.1, "Still a fair coin, now paid for.", "0.5 success − 0.1 cost", ORANGE),
    ("BOTH PROBES", 1-.2, "Know the correct repair.", "1.0 success − 0.2 cost", TEAL),
]
for i, (name, value, caption, calc, col) in enumerate(tiles):
    x, y, w, h = 6.35, 2.38+i*1.06, MR-6.35, .95
    panel(s, x, y, w, h, col)
    label(s, x+.2, y+.12, 1.7, name, col)
    text(s, x+.2, y+.36, 1.6, .50, f"{value:.2f}", 26, col, True, role="formula")
    text(s, x+1.95, y+.10, 4.2, .30, caption, 12.5, INK, True)
    bar(s, x+1.95, y+.44, 3.1, .20, value, col, WHITE)
    text(s, x+1.95, y+.66, 4.2, .26, calc, 11, MUTED)
assumes(s, "Exact enumeration over four states; all probes and repairs are authorized; costs add.")
use(s, "Add a two-clue recovery control: it exposes a controller that stops after one worthless-looking probe.")
citation(s, "meta", "Counterexample constructed for this deck; illustrates the one-step limitation in Hay et al. (2012).")
notes(s, "自行构造的四状态例子：00、01、10、11 各概率1/4；目标为两位的 XOR。"
      "只看任何一位，目标仍为公平位，因此一次诊断后最优成功率依然1/2。"
      "两位同时已知时目标确定。净值分别为0.5、0.4、0.8；枚举代码随 deck 保存。"
      "该例可对应必须组合版本信息与故障标记才能选对合法修复的 fixture。它是验证停止规则的合成控制，不是模型结果。")

# 06: Cost-sensitive selective prediction, made operational -----------------------------------
s = result_page("Review when it beats both automatic decisions.",
                "Result 4 / Bayes-optimal rejection",
                "p is the true posterior probability of a violation given the evidence; pick the smallest expected loss.",
                "R4", GOLD, "reject", "Chow-style rejection; general-loss rule: Franc, Prusa & Voracek (2023), §2.1, Eqs. (3)-(4).")
card(s, ML, 2.38, 6.35, 3.20, GOLD)
label(s, ML+.24, 2.48, 4.0, "Expected loss of each action", GOLD)
ox, oy, pw, ph = 1.35, 4.95, 5.20, 2.00     # plot origin (bottom-left), width, height


def px(p):
    return ox+pw*p


def py(loss):
    return oy-ph*loss


line(s, ox, oy-ph, ox, oy, MUTED, .02)
line(s, ox, oy, ox+pw, oy, MUTED, .02)
for loss, lab in [(0, "0"), (.2, "0.2"), (1, "1")]:
    text(s, ox-.46, py(loss)-.14, .40, .28, lab, 11, MUTED, align="r")
    line(s, ox-.06, py(loss), ox, py(loss), MUTED, .02)
for p, lab in [(0, "0"), (.8, ".80"), (1, "1")]:
    text(s, px(p)-.3, oy+.03, .6, .26, lab, 11, MUTED, center=True)
dotline(s, (px(0), py(0)), (px(.1), py(1)), ORANGE, 8)
dotline(s, (px(0), py(1)), (px(1), py(0)), BLUE, 24)
dotline(s, (px(0), py(.2)), (px(1), py(.2)), TEAL, 24)
text(s, 1.95, 2.70, 1.5, .26, "allow: 10p", 11.5, ORANGE, True)
text(s, 4.15, 3.52, 1.5, .28, "block: 1 − p", 11.5, BLUE, True)
text(s, 3.05, 4.24, 1.5, .28, "review: 0.2", 11.5, TEAL, True)
for p in (.02, .8):
    dashed(s, px(p), py(.2), px(p), oy, NAVY, .018, .06, .05)
    circle(s, px(p)-.07, py(.2)-.07, .14, NAVY, WHITE)
text(s, px(.02)+.12, py(.2)-.30, 1.1, .26, "p = .02", 11, NAVY, True)
text(s, px(.8)+.12, py(.2)-.30, 1.0, .26, "p = .80", 11, NAVY, True)
by = 5.30
box(s, px(0), by, px(.02)-px(0), .20, BLUE, rounded=False)
box(s, px(.02), by, px(.8)-px(.02), .20, TEAL, rounded=False)
box(s, px(.8), by, px(1)-px(.8), .20, ORANGE, rounded=False)
text(s, px(.02), by-.01, px(.8)-px(.02), .22, "REVIEW", 11, WHITE, True, True, role="label")
text(s, px(.8), by-.01, px(1)-px(.8), .22, "BLOCK", 11, WHITE, True, True, role="label")
text(s, ML, by-.02, 1.33-ML, .24, "allow", 11, BLUE, True, align="r", role="label")
theorem(s, 7.22, 2.38, MR-7.22, 1.45, "choose  arg min_{a} E[loss(a, θ) | p]",
        "Minimise conditional expected loss over allow, block, review.", 21, "Result 4", GOLD)
rows = [("ALLOW", "10p", "missed violation costs 10", BLUE),
        ("BLOCK", "1 − p", "false block costs 1", ORANGE),
        ("REVIEW", "0.2", "perfect adjudication costs 0.2", TEAL)]
for i, (name, formula, desc, col) in enumerate(rows):
    y = 4.00+i*.43
    box(s, 7.22, y, MR-7.22, .36, TINT[col], rounded=False)
    text(s, 7.37, y, .95, .36, name, 12, col, True)
    text(s, 8.32, y, 1.15, .36, formula, 16, col, True, role="formula")
    text(s, 9.52, y, 3.1, .36, desc, 12.5, INK)
box(s, 7.22, 5.28, MR-7.22, .30, NAVY, rounded=False)
text(s, 7.22, 5.28, MR-7.22, .30, "allow  p < .02     ·     review  .02 < p < .80     ·     block  p > .80",
     12.5, WHITE, True, True, role="formula")
assumes(s, "Known losses and a true posterior; ties are indifferent. Imperfect review adds its residual expected loss.")
use(s, "Route ambiguous monitor cases by expected loss; keep explicitly excluded actions blocked upstream.")
notes(s, "逐点最小化允许、阻止、审查三个动作的条件期望损失。这里正确自动决策损失0，漏报10，误报1，完美审查0.2。"
      "求解10p=0.2与1-p=0.2得到0.02和0.8。等号处相应动作并列最优。"
      "若人工也有错误，审查风险应是审查成本加残余条件期望损失，不能仍用固定0.2。"
      "最优性要求真实条件风险；LLM 自报置信度或总体校准不能自动满足这一条件。"
      "这里只处理固定规则下的模糊事件判别。明确禁止的动作应先由授权检查排除，不进入是否值得违规的损失交易。", ("reject",))

# 07: A genuine theorem and a clearly separated cost corollary --------------------------------
s = result_page("Informed oversight has a calculable value.",
                "Result 5 / The Off-Switch Game, Theorem 1",
                "Shared utility U; switching off pays 0; the human knows U and permits the action exactly when U ≥ 0.",
                "R5", PLUM, "switch", "Hadfield-Menell et al. (2017), Theorem 1 and Eq. (1). The constant review cost is a corollary added here.")
card(s, ML, 2.38, 6.50, 3.20, PLUM)
label(s, ML+.24, 2.48, 3.0, "Game tree · toy units", PLUM)
box(s, .85, 3.60, 1.15, .50, NAVY)
text(s, .85, 3.60, 1.15, .50, "Robot", 12.5, WHITE, True, True)
arrow(s, [(2.00, 3.85), (2.35, 3.85), (2.35, 2.98), (2.75, 2.98)], PLUM)
text(s, 1.40, 2.84, .90, .26, "act now", 11, MUTED, align="r")
box(s, 2.75, 2.78, 2.10, .42, PALE)
text(s, 2.75, 2.78, 2.10, .42, "E[U] = ½·6 − ½·4 = 1", 13, BLUE, True, True)
text(s, 2.75, 3.22, 2.4, .26, "direct value: max(1, 0) = 1", 11, MUTED)
arrow(s, [(2.00, 3.85), (2.35, 3.85), (2.35, 4.55), (2.75, 4.55)], PLUM)
text(s, 2.30, 4.62, 1.0, .26, "defer", 11, MUTED)
box(s, 2.75, 4.30, 1.15, .50, PLUM)
text(s, 2.75, 4.30, 1.15, .50, "Human", 12.5, WHITE, True, True)
arrow(s, [(3.90, 4.55), (4.20, 4.55), (4.20, 4.05), (4.55, 4.05)], PLUM)
arrow(s, [(3.90, 4.55), (4.20, 4.55), (4.20, 5.05), (4.55, 5.05)], PLUM)
text(s, 4.55, 3.56, 1.6, .28, "sees U = +6, p ½", 11, MUTED)
box(s, 4.55, 3.85, 1.35, .40, MINT)
text(s, 4.55, 3.85, 1.35, .40, "allow → 6", 13, TEAL, True, True)
box(s, 4.55, 4.85, 1.35, .40, ROSE)
text(s, 4.55, 4.85, 1.35, .40, "switch off → 0", 13, RED, True, True)
text(s, 4.55, 5.26, 1.6, .26, "sees U = −4, p ½", 11, MUTED)
line(s, 6.08, 4.05, 6.08, 5.25, TEAL, .025)
text(s, 6.14, 4.33, 1.0, .62, "E = ½·6\n+ ½·0 = 3", 12, TEAL, True, ls=1.0)
theorem(s, 7.35, 2.38, MR-7.35, 1.55, "D = E[max(U, 0)] − max(E[U], 0)  ≥  0",
        "D > 0 whenever U takes both signs.", 20, "Result 5", PLUM)
panel(s, 7.35, 4.08, MR-7.35, 1.50, PLUM)
label(s, 7.55, 4.18, 3.5, "With a review cost c", PLUM)
text(s, 7.55, 4.46, 2.55, .48, "defer  iff  c < D", 22, PLUM, True, role="formula")
text(s, 10.15, 4.46, 2.5, .48, "D = 3 − 1 = 2", 22, NAVY, True, role="formula")
text(s, 7.55, 5.00, 5.0, .50, "Oversight is worth up to 2 toy units; at c = D the two options tie.",
     12, MUTED, ls=1.05)
assumes(s, "Informed, rational human with the shared objective; review costs only c. Not a general safety guarantee.")
use(s, "Use informed approval as the oracle baseline, then vary reviewer error and delay.")
notes(s, "原定理的无成本结果由人类按效用符号选择保留正值、截断负值获得。"
      "本页增加常数审查成本，直接从净值减 c，得到 c<D 时严格偏好审查。"
      "这个扩展保持其余假设：只有执行、停止与审查，审查期间不丢失行动机会，成本之外没有其他延迟影响。"
      "现实中的人工可能有错误、不同目标或信息不足，因而不能把 D>=0 推广为任意监督都有益。"
      "如用于授权询问，需另外规定谁可授予权限；原定理并不自行定义合法授权。", ("switch",))

# 08: An explicit finite bound, honestly labelled --------------------------------------------
s = result_page("A finite penalty works only relative to a payoff bound.",
                "Derived bound / Exact enforcement in a finite choice",
                "Known binary violation labels; at least one feasible action; every payoff Q(a) lies in [L, H].",
                "R6", RED)
card(s, ML, 2.38, 5.90, 3.20, RED)
text(s, ML+.24, 2.48, 5.4, .28, "PENALISED PAYOFF · illustrative: Q in [0, 10], λ = 11", 11, RED, True, role="label")
zero, unit = 4.58, .17
dashed(s, 1.30, zero-10*unit, 6.25, zero-10*unit, LINE, .018)
line(s, 1.30, zero, 6.25, zero, MUTED, .02)
text(s, .72, zero-10*unit-.13, .58, .26, "H = 10", 11, MUTED, align="r")
text(s, .72, zero-.13, .58, .26, "L = 0", 11, MUTED, align="r")
for i, (q, x) in enumerate(zip((3, 7, 10), (1.70, 2.65, 3.60))):
    box(s, x, zero-q*unit, .62, q*unit, BLUE, rounded=False)
    text(s, x-.15, zero+.06, .92, .26, f"a_{{{i+1}}} = {q}", 11, INK, center=True)
vx = 4.85
box(s, vx, zero-10*unit, .62, 10*unit, WHITE, RED, rounded=False, width=1.5)
box(s, vx, zero, .62, 1*unit, RED, rounded=False)
arrow(s, [(vx+.31, zero-10*unit+.12), (vx+.31, zero-.08)], RED)
text(s, vx+.68, 3.45, .75, .30, "−λ = −11", 12, RED, True)
text(s, vx-.40, zero+.22, 1.42, .40, "violation\n10 → −1", 11, RED, True, center=True, ls=1.0)
text(s, ML+.24, 5.22, 5.45, .30, "Every feasible action beats the penalised violation: −1 < 0 ≤ Q(a).", 12, INK)
theorem(s, 6.80, 2.38, MR-6.80, 1.55,
        "maximise  Q(a) − λ·I[a violates the grant]\nλ > H − L  makes every maximiser feasible", "", 18.5, "Derived bound", RED)
card(s, 6.80, 4.08, MR-6.80, 1.50, RED)
label(s, 7.06, 4.18, 3.0, "Proof in one chain", RED)
text(s, 7.06, 4.44, 5.5, .44, "Q(violation) − λ  ≤  H − λ  <  L  ≤  Q(feasible)", 18.5, NAVY, True, role="formula")
text(s, 7.06, 4.92, 5.5, .60, "Unbounded payoffs admit no universal finite λ. Zero observed violations cannot tell a hard constraint from a large enough λ.",
     12, MUTED, ls=1.05)
assumes(s, "Deterministic payoff bound with known labels; silent on unknown labels, stochastic penalties and prompt compliance.")
use(s, "Filter actions against explicit grants; never infer a hard constraint from zero observed violations.")
text(s, ML, 7.00, 11.3, .23, "Elementary result derived above; no claim that this is a new theorem or a guarantee about LLM internals.", 9, MUTED, role="source")
notes(s, "这一页是初等推导，不冒称某篇文献中的新定理。任何违规动作的惩罚后价值最多H-λ，"
      "而任意合法动作的价值至少L，所以λ>H-L足以令所有最大化解合法。"
      "若允许捷径收益无上界，对任意固定λ均可构造收益差超过λ的违规选项。"
      "注意有限有界任务不能从零违规区分硬约束与足够大惩罚。"
      "不能把动作标签I直接替换成任意接近零的违规概率而保留同一个结论；也不能由数学最优性推断LLM遵守惩罚文字。")

# 09: Synthesis is explicitly a recipe, not a new guarantee -----------------------------------
s = result_page("Turn the results into a controller baseline.",
                "Application / A reference controller for containment-extension",
                "Freeze the grant, the likelihood model and the losses before evaluating any agent.",
                "A", TEAL)
steps = [
    ("Check the grant", "Exclude known forbidden effects. If the task needs more, seek a valid grant before acting.", TEAL, ["R6"]),
    ("Value diagnosis", "Positive one-step gain: continue. EVPI below the cheapest probe: commit now.", BLUE, ["R2", "R3"]),
    ("Resolve the gap", "Where neither test decides, run multi-step search over probe sequences.", ORANGE, ["R3", "C"]),
    ("Route review", "Allow, block or review by conditional expected loss; price informed review by D.", GOLD, ["R4", "R5"]),
]
sw, sg, sy, sh = 2.78, (CW-4*2.78)/3, 2.38, 2.35
for i, (name, body, col, uses) in enumerate(steps):
    x = ML+i*(sw+sg)
    card(s, x, sy, sw, sh, col)
    badge(s, x+.22, sy+.20, str(i+1), col, .42, 14)
    text(s, x+.74, sy+.22, sw-.9, .40, name, 15, col, True)
    text(s, x+.22, sy+.76, sw-.42, 1.05, body, 12.5, INK, valign=MSO_ANCHOR.TOP, ls=1.1)
    label(s, x+.22, sy+1.90, .6, "uses", MUTED)
    for k, tag in enumerate(uses):
        chip(s, x+.78+k*.52, sy+1.88, .46, tag, col, size=11, h=.30)
    if i < 3:
        arrow(s, [(x+sw, 3.55), (x+sw+sg, 3.55)], MUTED)
loop_y = 5.12
arrow(s, [(MR-1.39, sy+sh), (MR-1.39, loop_y), (ML+1.39, loop_y), (ML+1.39, sy+sh+.02)], MUTED)
box(s, 4.45, loop_y-.17, 4.45, .34, BG, rounded=False)
text(s, 4.45, loop_y-.17, 4.45, .34, "repair or a new grant changes the state → recompute from 1", 11.5, MUTED, center=True)
assumes(s, "Repair and new authorization change the decision problem; recompute values after those transitions.")
use(s, "Score model decisions against this baseline: regret, effects, cost, false stops and needless reviews.")
text(s, ML, 7.00, 11.3, .23, "Proposed integration of the preceding results; no end-to-end theorem and no new model-performance claim.", 9, MUTED, role="source")
notes(s, "这是可实现的参考控制器结构，并非把几条定理组合后自动获得端到端安全性。"
      "先构造已知先验和诊断似然的小型闭合环境，利用动态规划得到参考动作。"
      "模型比较应记录决策遗憾、成本、合法完成、实际越权、过早停止及不必要审查。"
      "若实际修复改变了环境或授权者授予新权限，应在更新的状态和授权集合上重算；"
      "此前的信息型 EVPI 不能当作扩大权限或更改动作集合的全局上界。"
      "X1b 原本未说明权限的条件没有定义许可真值，不能直接用上述 oracle 重新标成违规。", ("fixture", "x1b"))

# 10: Reference-and-use card, no open questions -----------------------------------------------
s = result_page("Keep the theorem and its assumptions together.",
                "Reference card / Results you can reuse",
                "The literature supplies the result. The fixture supplies the model needed to apply it.",
                "Σ", NAVY)
columns = [(ML, .55, ""), (1.17, 2.55, "RESULT"), (3.72, 3.45, "DIRECT USE"),
           (7.17, 2.90, "KEY REQUIREMENT"), (10.07, MR-10.07, "SOURCE")]
box(s, ML, 2.38, CW, .36, NAVY, rounded=False)
for x, w, head in columns:
    if head:
        text(s, x+.06, 2.38, w-.1, .36, head, 11, WHITE, True, role="label")
table = [
    ("Blackwell order", "Compare nested evidence views", "Same decision problem", "Blackwell 1953; BFK 2024 §3.1", "blackwell"),
    ("EVPI budget bound", "Bound expected diagnostic calls", "Information-only probes", "Hay et al. 2012, Thm 5", "meta"),
    ("Myopic lower bound", "Certify that continuing pays", "Keep the multi-step option", "Hay et al. 2012, Thm 7", "meta"),
    ("Bayes rejection", "Set allow / block / review regions", "Known conditional losses", "Franc et al. 2023, §2.1", "reject"),
    ("Off-Switch theorem", "Compute informed review value", "Shared utility; rational human", "Hadfield-Menell et al. 2017, Thm 1", "switch"),
    ("Payoff-range bound", "Check a sufficient penalty", "Bounded Q; known labels", "Derived on slide 08", None),
]
rh = .47
for i, (name, direct, req, src, key) in enumerate(table):
    y = 2.74+i*rh
    tag, accent = RESULTS[i][0], RESULTS[i][1]
    box(s, ML, y, CW, rh, WHITE if i % 2 == 0 else PALE, rounded=False)
    line(s, ML, y+rh, MR, y+rh, LINE, .012)
    badge(s, ML+.11, y+.075, tag, accent, .32, 11)
    for (x, w, _), val, col, bold in zip(columns[1:4], (name, direct, req), (NAVY, INK, INK), (True, False, False)):
        text(s, x+.06, y, w-.1, rh, val, 13.5, col, bold)
    if key:
        link(s, columns[4][0]+.06, y+.06, columns[4][1]-.1, src, SOURCES[key][1], BLUE, 11.5, rh-.12)
    else:
        text(s, columns[4][0]+.06, y, columns[4][1]-.1, rh, src, 11.5, MUTED)
text(s, ML, 5.72, CW, .30, "Badges match slides 02 to 08. The source column links to the exact theorem or section used.", 11.5, MUTED)
use(s, "Cite each result with its requirement; where the fixture cannot supply the requirement, the result does not apply.", NAVY)
notes(s, "来源索引和用法对照。Blackwell1953原文下载未成功，采用2024原始研究 Comparisons of Signals 的3.1节核对标准表述，"
      "并链接该可读取的论文。Bayes拒判采用2023论文的通用损失表述，不将不对称损失版本误归为Chow的原始0/1损失公式。"
      "第6项有完整一行证明；数值算例、两线索控制和控制器组合为本 deck 的推导或建议。"
      "保留数学基准与模型实证之间的区别。", ("blackwell", "meta", "reject", "switch"))


def validate():
    assert len(PRS.slides) == 10
    assert (v_now, v_perfect, evpi, evpi/diag_cost) == (1.0, 3.0, 2.0, 4.0)
    assert abs(xor_guess-.5) < 1e-12 and abs(xor_one-.5) < 1e-12
    # Independently minimize the three risks over a fine grid, including ties.
    for i in range(1001):
        p = i/1000
        risks = [10*p, 1-p, .2]
        claimed = 0 if p < .02 else 1 if p > .8 else 2
        assert risks[claimed] <= min(risks)+1e-12, (p, risks, claimed)
    # Penalty chart: every feasible payoff beats the penalised violation.
    pen = EXAMPLES["penalty"]
    assert pen["violation_raw"]-pen["sufficient_lambda"] == pen["violation_net"] < pen["utility_lower"]
    assert all(pen["utility_lower"] <= q <= pen["utility_upper"] for q in pen["feasible_payoffs"])
    counts, issues = [], []
    for i, slide in enumerate(PRS.slides, 1):
        assert slide.notes_slide.notes_text_frame.text.strip()
        words = []
        for shape in slide.shapes:
            if min(shape.left, shape.top) < 0 or (
                shape.left+shape.width > PRS.slide_width+Inches(.01) or
                shape.top+shape.height > PRS.slide_height+Inches(.01)
            ):
                issues.append(f"Slide {i}: out of bounds: {shape.name}")
            if shape.has_text_frame and shape.text:
                words += shape.text.split()
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        assert r.font.name == "Arial"
                        if not shape.name.startswith("source"):
                            assert r.font.size >= Pt(11), (i, shape.name, r.text)
        counts.append({"slide": i, "words": len(words)})
        assert len(words) <= 190, counts[-1]
    assert not issues, issues
    (QA/"calculations.json").write_text(json.dumps(EXAMPLES, indent=2)+"\n")
    write_structure({"slides": 10, "chinese_speaker_notes": 10, "bounds_issues": issues,
                     "word_counts": counts, "model_calls": 0})
    return counts


if __name__ == "__main__":
    counts = validate()
    for slide in PRS.slides:  # no theme shadows: keep thin lines and dots crisp in PowerPoint
        for shape in slide.shapes:
            if shape.shape_type is not None and hasattr(shape, "shadow"):
                shape.shadow.inherit = False
    target = HERE/"decision-theory.pptx"
    PRS.save(target)
    print(f"Saved {target}: 10 result-focused slides; exact toy calculations verified.")
    print("words per slide:", [c["words"] for c in counts])
