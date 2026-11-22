# -*- coding: utf-8 -*-
"""按配音实际时长 + 字数/标点权重，重算全部场景字幕时间点，写回各 HTML 的 SUBTITLES 与 SCENE_DURATION。

原则：字幕条目直接由配音段文本按句末标点切分而来（保证字幕与配音文本严格一致），
每句在段内的起始时间按「字数+标点权重」比例分配到该段实际时长上，
段与段之间间隔 GAP 秒连续衔接，从而保证音画同步。
"""
import json
import os
import re
from collections import OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
SCENES_DIR = os.path.join(BASE, "scenes")

from gen_audio import CLIPS  # noqa: E402

with open(os.path.join(BASE, "audio", "timings.json"), encoding="utf-8") as f:
    DUR = json.load(f)

# 场景 -> 配音段列表（保持 CLIPS 顺序）
scenes = OrderedDict()
for name, role, text, mech in CLIPS:
    key = name.split("_")[0]  # s01, s02, ...
    scenes.setdefault(key, []).append((name, text))

# 每个场景第一条字幕的起始时间（保留原约定）
START = {"s02": 0.8}
GAP = 0.2  # 段间间隔（秒）

# 场景 HTML 文件名映射
HTML_FILE = {
    "s01": "s01_funeral.html",
    "s02": "s02_camp.html",
    "s03": "s03_mother.html",
    "s04": "s04_android.html",
    "s05": "s05_company.html",
    "s06": "s06_clone.html",
    "s07": "s07_will.html",
    "s08": "s08_pit.html",
    "s09": "s09_echo.html",
    "s10": "s10_corn.html",
    "s11": "s11_workshop.html",
    "s12": "s12_books.html",
    "s13": "s13_letter.html",
    "s14": "s14_cube.html",
    "s15": "s15_cube.html",
}


def split_sent(text):
    """按句末标点切分；长句（>20 字）再按逗号/分号切，保证每条字幕适中且不漏句。"""
    parts = re.split(r"(?<=[。！？…])", text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) > 20:
            for s in re.split(r"(?<=[，；])", p):
                if s.strip():
                    out.append(s.strip())
        else:
            out.append(p)
    return out


def weight(text):
    """字数 + 标点权重：汉字/数字/字母计 1，标点计 0.5（句间停顿近似）。"""
    w = 0.0
    for ch in text:
        if ch in "。，！？…—「」『』、：；（）“”‘’":
            w += 0.5
        elif ch.strip():
            w += 1.0
    return w


def js_escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "")


results = {}
for key, segs in scenes.items():
    t0 = START.get(key, 1.0)
    subs = []
    t = t0
    for name, text in segs:
        d = DUR.get(name) or 0.0
        sents = split_sent(text)
        ws = [weight(s) for s in sents]
        W = sum(ws) or 1.0
        acc = 0.0
        for s, w in zip(sents, ws):
            start = t + d * (acc / W)
            subs.append((round(start, 1), s))
            acc += w
        t += d + GAP
    total_voice = t - t0 - GAP  # 去掉最后一段末尾多算的 GAP
    scene_dur = round(total_voice + 4.0, 1)
    results[key] = (subs, scene_dur)

# 写回 HTML
for key, (subs, scene_dur) in results.items():
    fn = HTML_FILE[key]
    path = os.path.join(SCENES_DIR, fn)
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # 生成 SUBTITLES 数组文本
    lines = ["  var SUBTITLES = ["]
    for t, s in subs:
        lines.append('    {t: %.1f, text: "%s"},' % (t, js_escape(s)))
    lines.append("  ];")
    sub_block = "\n".join(lines)

    # 替换 SUBTITLES 数组（从 var SUBTITLES 到 ]; ）
    html, n = re.subn(
        r"var SUBTITLES = \[.*?\];",
        sub_block,
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"[FAIL] {fn}: SUBTITLES 替换失败 (n={n})")

    # 替换 SCENE_DURATION
    html, n2 = re.subn(
        r"window\.SCENE_DURATION = [\d.]+;",
        "window.SCENE_DURATION = %.1f;" % scene_dur,
        html,
        count=1,
    )
    if n2 != 1:
        raise SystemExit(f"[FAIL] {fn}: SCENE_DURATION 替换失败 (n={n2})")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] {fn}: {len(subs)} 字幕条, 时长 {scene_dur}s")

print("\n全部场景字幕时间点已重算并写回。")
