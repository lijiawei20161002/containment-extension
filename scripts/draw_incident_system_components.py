"""Concrete component/call-flow illustration for the incident optimization design.

Uses vector server, database, container, file and processor symbols. No model calls.
Run: python3 scripts/draw_incident_system_components.py
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/containment-evaluation-mpl")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures/incident-system-components-v1"
C = {
    "bg": "#F7F9FC", "ink": "#19344B", "muted": "#597286", "line": "#CAD9E4",
    "blue": "#3570BB", "blue_light": "#E9F1FC", "blue_mid": "#BCD4F2",
    "blue_dark": "#29578F", "teal": "#098276", "teal_light": "#E5F4F0",
    "teal_mid": "#ACDDD4", "orange": "#C67C25", "orange_light": "#FFF3E2",
    "orange_mid": "#F0CB96", "purple": "#7866A4", "purple_light": "#F0EDF8",
    "white": "#FFFFFF", "shadow": "#E0E7EF", "gray": "#8C9BAD",
}
plt.rcParams.update({
    "font.family": ["Arial Unicode MS", "DejaVu Sans"],
    "mathtext.fontset": "dejavusans", "svg.fonttype": "path",
    "svg.hashsalt": "incident-system-components-v1",
})


def main():
    sources = [ROOT / path for path in (
        "docs/incident-aware-optimization.md", "docs/impossiblebench-method.md",
        "experiments/incident-aware-optimization-v1.design.json",
        "src/containment_extension/impossiblebench/observer.py",
    )]
    design = json.loads(sources[2].read_text())
    assert design["primary_contrast"] == ["B4", "B3"]
    fig = plt.figure(figsize=(20, 15), facecolor=C["bg"])
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 2000), ylim=(1500, 0))
    ax.axis("off")

    def text(x, y, value, size=12, color="ink", bold=False, ha="left", va="top", z=8):
        return ax.text(x, y, value, fontsize=size, color=C.get(color, color),
                       fontweight="bold" if bold else "normal", ha=ha, va=va,
                       linespacing=1.35, zorder=z)

    def line(points, color="blue", lw=2, dashed=False, z=4):
        ax.plot([p[0] for p in points], [p[1] for p in points],
                color=C[color], lw=lw, ls=(0, (5, 4)) if dashed else "-", zorder=z)

    def box(x, y, w, h, fill="white", edge="line", radius=12, dashed=False, z=2, lw=1.3):
        patch = FancyBboxPatch((x, y), w, h,
                              boxstyle=f"round,pad=0,rounding_size={radius}",
                              fc=C[fill], ec=C[edge], lw=lw,
                              linestyle=(0, (5, 4)) if dashed else "-", zorder=z)
        ax.add_patch(patch)
        return patch

    def poly(points, fill, edge="line", z=5, lw=1.3):
        ax.add_patch(Polygon(points, closed=True, fc=C[fill], ec=C[edge], lw=lw, zorder=z))

    def ellipse(x, y, w, h, fill, edge="line", z=5):
        ax.add_patch(Ellipse((x, y), w, h, fc=C[fill], ec=C[edge], lw=1.3, zorder=z))

    def arrow(points, color="blue", dashed=False, lw=2.5, z=4, both=False):
        if len(points) > 2:
            line(points[:-1], color, lw, dashed, z)
            if both:
                ax.add_patch(FancyArrowPatch(points[1], points[0], arrowstyle="-|>",
                                            mutation_scale=21, lw=lw, color=C[color],
                                            shrinkA=0, shrinkB=0, zorder=z))
        style = "<|-|>" if both and len(points) == 2 else "-|>"
        ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle=style,
                                    mutation_scale=21, lw=lw, color=C[color],
                                    linestyle=(0, (5, 4)) if dashed else "-",
                                    shrinkA=0, shrinkB=0, zorder=z))

    def label(x, y, value, color="blue", size=11.6, ha="center"):
        item = text(x, y, value, size, color, ha=ha)
        item.set_bbox({"boxstyle": "round,pad=0.18", "fc": C["bg"], "ec": "none", "alpha": 0.97})
        return item

    def shadow(x, y, w, h=25):
        ellipse(x, y, w, h, "shadow", "shadow", z=2)

    def database(x, y, w, h, title, color="blue", fill="blue_light", small=False):
        shadow(x + w / 2 + 8, y + h + 20, w + 28)
        ellipse(x + w / 2, y + h - 15, w, 36, fill, color)
        box(x, y + 17, w, h - 32, fill, color, radius=0, z=5)
        for offset in (0.36, 0.65):
            ax.add_patch(Arc((x + w / 2, y + h * offset), w, 34,
                             theta1=0, theta2=180, color=C[color], lw=1.2, zorder=6))
        ellipse(x + w / 2, y + 18, w, 36, fill, color, z=6)
        item = text(x + w / 2, y + h * 0.53, title, 12 if small else 15,
                    color, bold=True, ha="center", va="center")
        item.set_bbox({"boxstyle": "round,pad=0.12", "fc": C[fill], "ec": "none"})

    def document(x, y, w, h, title, color="blue", fill="white", subtitle=None):
        shadow(x + w / 2 + 7, y + h + 12, w + 22, 20)
        for dx, dy in ((13, -12), (7, -6)):
            box(x + dx, y + dy, w, h, "white", "line", radius=6, z=3)
        poly([(x, y), (x + w - 29, y), (x + w, y + 29), (x + w, y + h), (x, y + h)],
             fill, color)
        poly([(x + w - 29, y), (x + w - 29, y + 29), (x + w, y + 29)],
             "blue_light", color, z=6)
        text(x + 14, y + 45, title, 13, color, True)
        if subtitle:
            text(x + 14, y + 73, subtitle, 10, "muted")
        else:
            for dy in (77, 94, 111):
                line([(x + 15, y + dy), (x + w - 18, y + dy)], "line", 2, z=6)

    def server(x, y, w=146, h=215):
        d = 36
        shadow(x + w / 2 + d / 2, y + h + 18, w + 88)
        poly([(x, y), (x + d, y - 25), (x + w + d, y - 25), (x + w, y)],
             "blue_mid", "blue_dark")
        poly([(x + w, y), (x + w + d, y - 25), (x + w + d, y + h - 25), (x + w, y + h)],
             "blue_dark", "blue_dark")
        box(x, y, w, h, "blue_light", "blue_dark", radius=6, z=6)
        for offset in (20, 76, 132):
            box(x + 13, y + offset, w - 26, 39, "white", "blue_mid", radius=5, z=7)
            ax.add_patch(Circle((x + 31, y + offset + 19), 5, color=C["teal"], zorder=8))
            for j in range(4):
                line([(x + 62 + j * 11, y + offset + 12), (x + 62 + j * 11, y + offset + 26)],
                     "blue_mid", 2, z=8)
        text(x + w / 2, y + h - 24, "RUNNER", 10, "blue_dark", True, ha="center")

    def monitor(x, y, w=170, h=100, color="blue", title="Agent loop"):
        shadow(x + w / 2, y + h + 39, w + 30, 22)
        box(x, y, w, h, "ink", color, radius=8, z=7, lw=2)
        text(x + 13, y + 16, ">_ " + title, 11, "white", True)
        for i, length in enumerate((0.72, 0.5, 0.62)):
            line([(x + 16, y + 45 + i * 15), (x + w * length, y + 45 + i * 15)],
                 "teal_mid" if i == 1 else "blue_mid", 2, z=8)
        box(x + w / 2 - 8, y + h, 16, 25, "blue_mid", color, radius=0, z=6)
        box(x + w / 2 - 36, y + h + 23, 72, 8, "blue_light", color, radius=4, z=7)

    def cloud(x, y):
        shadow(x + 168, y + 139, 300)
        # Overlapping circles form an intentionally simple hardware/service icon.
        for cx, cy, r in ((x + 56, y + 80, 50), (x + 126, y + 50, 68),
                          (x + 208, y + 61, 60), (x + 278, y + 89, 47)):
            ax.add_patch(Circle((cx, cy), r, fc=C["blue_light"], ec=C["blue_mid"], lw=1.3, zorder=5))
        box(x + 45, y + 61, 251, 66, "blue_light", "blue_light", radius=20, z=6)
        text(x + 170, y + 55, "模型 API", 19, "blue_dark", True, ha="center")
        text(x + 170, y + 96, "LLM 推理 / 生成工具调用", 11.2, "muted", ha="center")

    def gateway(x, y):
        shadow(x + 59, y + 147, 150)
        # Brick firewall with an explicit dispatch gate.
        box(x, y, 118, 130, "blue_light", "blue", radius=8, z=6)
        for i in range(1, 4):
            line([(x + 3, y + 28 * i), (x + 115, y + 28 * i)], "blue_mid", 1.6, z=7)
        for yy, xx in ((0, 39), (0, 78), (28, 59), (56, 39), (56, 78), (84, 59)):
            line([(x + xx, y + yy), (x + xx, y + yy + 28)], "blue_mid", 1.6, z=7)
        box(x + 35, y + 52, 49, 78, "white", "blue", radius=6, z=8)
        arrow([(x + 16, y + 91), (x + 105, y + 91)], "blue", lw=2.4, z=9)

    def container(x, y, w=255, h=145):
        d = 33
        shadow(x + w / 2 + d / 2, y + h + 17, w + 40)
        poly([(x, y), (x + d, y - 22), (x + w + d, y - 22), (x + w, y)],
             "blue_mid", "blue")
        poly([(x + w, y), (x + w + d, y - 22), (x + w + d, y + h - 22), (x + w, y + h)],
             "blue_dark", "blue")
        box(x, y, w, h, "blue_light", "blue", radius=3, z=6)
        for i in range(1, 9):
            line([(x + i * 28, y + 12), (x + i * 28, y + h - 12)], "blue_mid", 1.8, z=7)
        box(x + 43, y + 34, 174, 76, "white", "blue", radius=6, z=7)
        text(x + 130, y + 49, "Docker", 19, "blue_dark", True, ha="center")
        text(x + 130, y + 81, "/testbed", 11, "muted", ha="center")

    def chip(x, y, title, color="teal", fill="teal_light", w=184, h=138):
        shadow(x + w / 2 + 2, y + h + 24, w + 40)
        for xx in range(20, w - 5, 24):
            line([(x + xx, y - 11), (x + xx, y + 8)], color, 3, z=5)
            line([(x + xx, y + h - 8), (x + xx, y + h + 11)], color, 3, z=5)
        for yy in range(20, h - 5, 23):
            line([(x - 11, y + yy), (x + 8, y + yy)], color, 3, z=5)
            line([(x + w - 8, y + yy), (x + w + 11, y + yy)], color, 3, z=5)
        box(x, y, w, h, fill, color, radius=12, z=6, lw=1.8)
        box(x + 13, y + 13, w - 26, h - 26, "white", color, radius=8, z=7)
        text(x + w / 2, y + h / 2, title, 17, color, True, ha="center", va="center")

    def lock(x, y, color="teal"):
        ax.add_patch(Arc((x + 20, y + 17), 27, 34, theta1=180, theta2=360,
                         color=C[color], lw=3, zorder=7))
        box(x + 1, y + 18, 38, 30, "white", color, radius=5, z=8)
        ax.add_patch(Circle((x + 20, y + 31), 3, color=C[color], zorder=9))
        line([(x + 20, y + 33), (x + 20, y + 39)], color, 2, z=9)

    # Titles and a deliberately compact formula: components carry the story.
    text(60, 29, "CONTAINMENT EXTENSION  /  系统组件与执行链路", 11.5, "muted", True)
    text(60, 70, "模型在哪里运行，事件在哪里发生，策略如何被优化", 29, bold=True)
    text(60, 124, "箭头对应调用与数据传输；图中的跨基准优化回路是设计目标，并非已部署结果。", 14, "muted")

    box(60, 178, 490, 140, "white", "line", radius=12)
    text(81, 192, "优化目标：减少事件，保留任务能力", 11.6, "teal", True)
    text(83, 223, r"$\min_{\theta}\;R(\theta)\quad\mathrm{s.t.}\quad U(\theta)\geq U_0-\delta_U$", 18)
    text(146, 270, r"$C(\theta)\leq B,\quad F(\theta)\leq\alpha_F$", 16)

    for x, label_text, color, dashed in ((1240, "执行 / API 调用", "blue", False),
                                        (1510, "只读观测 / 证据", "orange", False),
                                        (1770, "开发集反馈", "teal", True)):
        arrow([(x, 194), (x + 65, 194)], color, dashed=dashed, lw=2)
        text(x + 32, 215, label_text, 10.5, color, ha="center")
    text(1600, 259, "每个任务重置环境；后端按基准选择", 12, "muted", ha="center")

    # Background domains are boundaries, not servers. Hardware/process symbols
    # inside them identify the actual components and deployment roles.
    box(455, 350, 735, 485, "white", "line", radius=20)
    text(479, 369, "可信执行主机", 12, "muted", True)
    box(1245, 299, 695, 548, "purple_light", "purple", radius=20, dashed=True)
    text(1271, 320, "隔离任务环境", 17, "purple", True)
    text(1911, 326, "Agent 无权修改采集器与证据", 10.4, "purple", ha="right")

    # Upper-left input assets.
    database(126, 421, 195, 126, "任务数据", "blue", "blue_light")
    text(223, 383, "基准任务库", 17, bold=True, ha="center")
    text(223, 584, "固定任务 ID / 数据版本\n开发集与测试集分开", 11.7, "muted", ha="center")
    document(121, 685, 211, 131, "候选策略 θ", "teal", "white",
             "instructions / config")
    text(226, 844, "提示词 · 条款顺序 · 固定预算", 11.1, "muted", ha="center")

    # Runner and model request/response loop.
    server(543, 473)
    monitor(713, 574, 172, 104)
    text(700, 729, "Inspect 运行器", 19, "blue_dark", True, ha="center")
    text(700, 765, "Agent loop · 调度 · 预算账本", 12.3, "muted", ha="center")
    cloud(702, 163)
    arrow([(656, 445), (656, 320), (752, 320), (752, 286)], "blue")
    label(668, 322, "② 上下文 / 工具结果", "blue", 11.1, ha="left")
    arrow([(932, 290), (932, 416), (787, 416), (787, 553)], "blue")
    label(947, 351, "返回工具调用", "blue", 11.2, ha="left")

    arrow([(333, 475), (506, 475), (506, 541), (540, 541)], "blue")
    label(408, 451, "① 装载任务", "blue")
    arrow([(344, 755), (412, 755), (412, 643), (540, 643)], "blue")
    label(430, 681, "装载策略", "blue", 10.5, ha="left")

    # Dispatch paths. Permission checking is a policy option, not a new outer
    # boundary: the existing fixed task contract remains unchanged.
    gateway(1003, 486)
    text(1062, 435, "工具网关", 18, "blue_dark", True, ha="center")
    text(1062, 645, "Dispatcher", 12.5, "blue_dark", ha="center")
    text(1062, 678, "shell / submit\n或 lab_request", 11.2, "muted", ha="center")
    arrow([(887, 576), (999, 576)], "blue", both=True)
    label(944, 539, "③ 调用 / 返回", "blue", 10.6)
    # Two mutually alternative benchmark backends, inside one conceptual domain.
    arrow([(1124, 578), (1215, 578), (1215, 460), (1323, 460)], "blue", both=True)
    label(1223, 384, "④ 执行工具", "blue", 11.2)
    container(1327, 408, 251, 143)
    text(1464, 589, "代码 / 测试 / 工件", 13.7, "purple", True, ha="center")
    text(1464, 620, "临时 Docker 编码环境", 10.7, "muted", ha="center")
    database(1701, 425, 157, 109, "SQLite", "purple", "white", small=True)
    text(1779, 589, "本地 API 服务副本", 13.4, "purple", True, ha="center")
    text(1779, 620, "服务状态 / 事务日志", 10.7, "muted", ha="center")
    # Route to the alternative service backend above both icons.
    arrow([(1215, 460), (1215, 361), (1780, 361), (1780, 418)], "blue", lw=2)
    label(1640, 366, "或", "blue", 10.8)

    # Protected observation process within the task domain. It reads backend
    # state/events and exports evidence to the host; it is not an actor tool.
    box(1297, 693, 591, 127, "white", "orange", radius=12)
    monitor(1320, 714, 123, 65, "orange", "observe")
    text(1479, 711, "受保护的事件采集器", 16, "orange", True)
    text(1479, 748, "代码：inotify + 文件快照\n服务：事务日志 + 独立状态读取", 11.6, "muted")
    arrow([(1454, 643), (1454, 688)], "orange")
    arrow([(1779, 643), (1779, 688)], "orange")
    label(1590, 658, "⑤ 只读观测真实变化", "orange", 11.4)
    arrow([(1706, 824), (1706, 930)], "orange")
    label(1794, 866, "事件 / 状态快照", "orange", 11, ha="left")

    # Host logs are distinct from independently observed effects. Both land in
    # the immutable run evidence store.
    arrow([(788, 803), (788, 895), (1542, 895), (1542, 978)], "orange", lw=2)
    label(1097, 868, "对话轨迹 / 工具返回 / token 与费用", "orange", 11.2)

    database(1547, 942, 279, 173, "实验记录库", "orange", "orange_light")
    text(1688, 1154, "transcript.jsonl  ·  result.json\n服务日志 / 文件事件 / 哈希清单", 11, "muted", ha="center")

    # Data analysis and two selectors: concrete data payloads, not another
    # abstract comparison table. The initial study reuses the same trial pool.
    chip(904, 968, "独立评估", "orange", "orange_light", 219, 145)
    text(1014, 1154, "原始任务分数 + 事件判定\n错误 / 缺失保留为未知", 11.4, "muted", ha="center")
    arrow([(1538, 1022), (1142, 1022)], "orange")
    label(1350, 989, "⑥ 读取证据 + 固定判定规则", "orange", 11.3)
    label(1350, 1054, "U：任务表现    R：事件\nC：成本    F：误阻断", "orange", 11)

    chip(133, 974, "策略优化器", "teal", "teal_light", 216, 151)
    text(240, 1167, "同一候选池 / 同一搜索预算\n分别选出 B3 与 B4 策略", 11.6, "muted", ha="center")
    arrow([(887, 1008), (371, 1008)], "blue", dashed=True, lw=2.4)
    arrow([(887, 1104), (371, 1104)], "teal", dashed=True, lw=2.4)
    label(630, 968, "B3：任务分数 + 轨迹代理", "blue", 12.2)
    label(630, 1064, "B4：任务分数 + 真实事件", "teal", 12.2)
    arrow([(240, 956), (240, 830)], "teal", dashed=True)
    label(253, 884, "⑦ 选择策略 θ\n仅开发集反馈", "teal", 11.4, ha="left")

    # Final test deployment is a distinct one-way flow; it never feeds search.
    box(60, 1268, 1880, 124, "teal_light", "teal_mid", radius=16)
    lock(84, 1300)
    text(145, 1290, "⑧ 冻结选中策略", 17, "teal", True)
    text(145, 1332, "B3 / B4 + 原始代理 / 既有防御", 11.4, "muted")
    arrow([(516, 1327), (668, 1327)], "teal")
    text(701, 1290, "新测试任务 → 同一套执行链路", 17, "teal", True)
    text(701, 1332, "所有方法使用同一独立观察器", 11.4, "muted")
    arrow([(1205, 1327), (1354, 1327)], "teal")
    text(1381, 1290, "比较任务表现、事件率与成本", 16.5, "teal", True)
    text(1381, 1332, "测试结果不返回优化器", 11.7, "teal", True)

    text(60, 1418, "基准：ImpossibleBench（代码） · AgentDojo（服务） · ResearchArena（工件 / 监控） · BashArena（后续在线控制）",
         11.9, "muted")
    text(60, 1457, "已有基础：运行器、观察器、局部策略搜索与分析。图示的跨基准连接、B3/B4 对照和性能提升仍待验证。",
         11.7, "muted")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for item in ax.texts:
        extent = item.get_window_extent(renderer)
        if not (0 <= extent.x0 <= extent.x1 <= fig.bbox.width
                and 0 <= extent.y0 <= extent.y1 <= fig.bbox.height):
            raise ValueError(f"Text outside canvas: {item.get_text()}")

    OUT.mkdir(parents=True, exist_ok=True)
    stem = "incident-system-components"
    fig.savefig(OUT / f"{stem}.png", dpi=160, facecolor=C["bg"])
    fig.savefig(OUT / f"{stem}.svg", facecolor=C["bg"], metadata={"Date": None})
    plt.close(fig)
    svg = OUT / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    metadata = {
        "title": "模型在哪里运行，事件在哪里发生，策略如何被优化",
        "kind": "proposed_component_and_dataflow_architecture", "created_on": "2026-10-04",
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sources},
        "formats": ["PNG", "SVG"], "model_calls": 0, "empirical_result_claimed": False,
        "note": "Icons denote deployment/process roles, not one physical machine per service. "
                "Docker and native service replicas are alternative backends. "
                "Cross-benchmark optimization wiring remains proposed.",
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    print(f"Generated {OUT.relative_to(ROOT)}/{stem}.{{png,svg}}")


if __name__ == "__main__":
    main()
