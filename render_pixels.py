# -*- coding: utf-8 -*-
"""赞比的遗产 —— 像素动画整片渲染框架（合金弹头规格 640x360 画布 SCALE=3）

18 场景顺序：c0a, s01..s07, c0b, s08..s11, c0c, s12..s15
- 字幕与配音时间点：复用 recalc_subtitles.py 的算法（从 gen_audio.CLIPS + timings.json 重算，保证声画字幕一致）
- 每场景渲染到 frames_px/<key>/f%05d.png，再合成为 <key>.mp4 + 配音，最后 concat 成片。
"""
import math
import os
import re
import json
import subprocess
import random
from collections import OrderedDict

from PIL import Image, ImageDraw, ImageFont
from pixel_sprites import (elder_front, elder_side, elder_lie,
                           boy_side, boy_squat, boy_kneel,
                           mech_front, richard_front, girl_front, cube,
                           draw_reflection,
                           ELDER, HOLO, SKIN, HAIR_DARK, HAIR_GREY, SUIT_DARK)
from gen_audio import CLIPS

import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# ---- 常量 ----
W, H = 640, 360
SCALE = 3
FPS = 30
BASE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
FRAMES_DIR = os.path.join(BASE, "frames_px")
AUDIO_DIR = os.path.join(BASE, "audio")
BGM_DIR = os.path.join(BASE, "bgm")
OUT_MP4 = os.path.join(BASE, "赞比的遗产_像素版.mp4")

ORDER = ["c0a", "s01", "s02", "s03", "s04", "s05", "s06", "s07",
         "c0b", "s08", "s09", "s10", "s11",
         "c0c", "s12", "s13", "s14", "s15"]

# ---- 调色板（荒启科幻 GEO 冷峻）----
BG      = (7, 10, 15)
INK     = (4, 7, 11)       # 最黑
WALL_TOP= (15, 21, 33)
WALL_BOT= (10, 14, 23)
DOME    = (29, 42, 60)
DOME_RIB= (42, 60, 80)
COLUMN  = (36, 48, 64)
COLUMN_H= (58, 76, 94)
PEDESTAL= (19, 27, 40)
PED_TOP = (46, 70, 90)
CROWD   = (9, 13, 21)
GROUND  = (13, 19, 28)
BEAM    = (120, 205, 232)
HOLO_HI = (225, 250, 255)
HOLO_MID= (130, 202, 226)
HOLO_LO = (50, 110, 134)
HOLO_DK = (16, 40, 56)
DUST    = (150, 215, 238)
STEEL   = (70, 88, 104)
RUST    = (120, 80, 50)
WARM    = (255, 200, 140)


# ---- 数据提取：字幕 + 时长 + 配音段（复用 recalc 算法）----
def build_scene_data():
    with open(os.path.join(AUDIO_DIR, "timings.json"), encoding="utf-8") as f:
        DUR = json.load(f)

    scenes = OrderedDict()
    for name, role, text, mech in CLIPS:
        key = name.split("_")[0]
        scenes.setdefault(key, []).append((name, role, text))

    START = {"s02": 0.8}
    GAP = 0.2

    def split_sent(text):
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
        w = 0.0
        for ch in text:
            if ch in "。，！？…—「」『』、：；（）“”‘’":
                w += 0.5
            elif ch.strip():
                w += 1.0
        return w

    data = {}
    for key, segs in scenes.items():
        t0 = START.get(key, 1.0)
        subs = []
        seg_starts = []
        t = t0
        for name, role, text in segs:
            d = DUR.get(name) or 0.0
            seg_starts.append((name, d, t))
            sents = split_sent(text)
            ws = [weight(s) for s in sents]
            W = sum(ws) or 1.0
            acc = 0.0
            for s, w in zip(sents, ws):
                start = t + d * (acc / W)
                subs.append((round(start, 1), s, role))
                acc += w
            t += d + GAP
        total_voice = t - t0 - GAP
        scene_dur = round(total_voice + 4.0, 1)
        data[key] = {"dur": scene_dur, "subs": subs, "segs": seg_starts}
    # 章节卡：无字幕无配音，固定 6s
    for c in ("c0a", "c0b", "c0c"):
        data[c] = {"dur": 6.0, "subs": [], "segs": []}
    return data

DATA = build_scene_data()


# ---- 动画驱动 helper ----
def _is_talk(segs, prefix, t):
    """t 时刻是否有 name 以 prefix 开头的配音在播放。"""
    for name, dsec, tstart in segs:
        if tstart <= t < tstart + dsec and name.startswith(prefix):
            return True
    return False


def _mouth(t):
    """口型 0/1：说话时按 4Hz 振荡。"""
    return 1 if (int(t * 4) % 2 == 0) else 0


def _bob(t):
    """呼吸/说话头部起伏：2.5Hz 上下 1px。"""
    return 1 if (int(t * 2.5) % 2 == 0) else 0


# ---- 通用工具 ----
def fc(c, k):
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k))


def mix(c1, c2, k):
    return (int(c1[0] * (1 - k) + c2[0] * k),
            int(c1[1] * (1 - k) + c2[1] * k),
            int(c1[2] * (1 - k) + c2[2] * k))


def e_out(d, bbox, pad, outline, fill):
    x0, y0, x1, y1 = bbox
    d.ellipse([x0 - pad, y0 - pad, x1 + pad, y1 + pad], fill=outline)
    d.ellipse([x0, y0, x1, y1], fill=fill)


def r_out(d, bbox, pad, outline, fill):
    x0, y0, x1, y1 = bbox
    d.rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], fill=outline)
    d.rectangle([x0, y0, x1, y1], fill=fill)


def vgrad(d, y0, y1, c_top, c_bot):
    for y in range(y0, y1 + 1):
        k = (y - y0) / max(1, (y1 - y0))
        d.line([(0, y), (W, y)], fill=mix(c_top, c_bot, k))


ROLE_NAME = {
    "narrator": "", "boy": "少年赞比", "young": "青年赞比", "old": "老年赞比",
    "clone": "克隆赞比", "mech": "机械赞比", "cube": "立方体",
    "girl": "女孩", "android": "仿生人", "director": "董事",
}
ROLE_COLOR = {
    "narrator": (255, 255, 255), "boy": (255, 176, 96), "young": (120, 220, 255),
    "old": (232, 202, 128), "clone": (148, 210, 235), "mech": (96, 184, 232),
    "cube": (184, 148, 255), "girl": (255, 168, 196), "android": (150, 232, 168),
    "director": (255, 224, 108),
}


# ---- 细节增强 helper（星露谷风格：纹理 / 投影 / 砖墙 / 石子 / 草丛）----
def speckle(d, x0, y0, x1, y1, base, seed, n=90, rng=16):
    """地面纹理：颜色抖动的砂砾/草屑点与短线（deterministic，seed 固定）。"""
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.randint(x0, x1 - 1)
        y = rnd.randint(y0, y1 - 1)
        k = 1.0 + rnd.uniform(-rng, rng) / 255.0
        c = (max(0, min(255, int(base[0] * k))),
             max(0, min(255, int(base[1] * k))),
             max(0, min(255, int(base[2] * k))))
        if rnd.random() < 0.6:
            d.point((x, y), fill=c)
        else:
            d.line([(x, y), (x + rnd.randint(-3, 3), y + rnd.randint(-1, 1))],
                   fill=c, width=1)


def pebbles(d, x0, y0, x1, y1, base, seed, n=10):
    """小石子/卵石：受光面+背光面，点缀地面。"""
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.randint(x0, x1)
        y = rnd.randint(y0, y1)
        r = rnd.randint(2, 5)
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=fc(base, 0.8))
        d.ellipse([x - r // 2, y - r // 3, x + r // 3, y + r // 4], fill=fc(base, 1.2))


def drop_shadow(d, cx, cy, w, h, ground, alpha=0.35):
    """底部椭圆阴影（星露谷招牌：物体投影到地面）。ground 为地面色，alpha 预混合成不透明。"""
    col = mix(ground, (0, 0, 0), alpha)
    d.ellipse([cx - w, cy - h // 2, cx + w, cy + h // 2], fill=col)


def brick_wall(d, x0, y0, x1, y1, base, seed, rows=5, cols=13, mortar=(22, 28, 38)):
    """砖墙纹理：横向砖缝 + 错缝竖线。"""
    rnd = random.Random(seed)
    d.rectangle([x0, y0, x1, y1], fill=base)
    rh = (y1 - y0) / max(1, rows)
    cw = (x1 - x0) / max(1, cols)
    for r in range(rows + 1):
        yy = int(y0 + r * rh)
        d.line([(x0, yy), (x1, yy)], fill=mortar, width=1)
    for r in range(rows):
        yy = int(y0 + r * rh)
        off = int((r % 2) * cw / 2)
        for c in range(cols + 1):
            xx = int(x0 + c * cw + off) % max(1, (x1 - x0))
            d.line([(x0 + xx, yy), (x0 + xx, int(yy + rh))], fill=mortar, width=1)


def grass_tuft(d, x, y, base, seed, n=5):
    """草丛：几根草叶从地面点向上散开。"""
    rnd = random.Random(seed)
    for _ in range(n):
        x1 = x + rnd.randint(-4, 4)
        y1 = y - rnd.randint(3, 7)
        d.line([(x, y), (x1, y1)], fill=fc(base, 1.15), width=1)


def draw_subtitle(d, font, t, subs):
    text = ""
    role = "narrator"
    for st, tx, rl in subs:
        if t >= st:
            text = tx
            role = rl
    if text:
        name = ROLE_NAME.get(role, "")
        color = ROLE_COLOR.get(role, (255, 255, 255))
        prefix = f"【{name}】" if name else ""
        d.text((W // 2, 340), prefix + text, font=font, fill=color,
               stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")


# ---- 转场：每场景 (入场, 出场)，"black"渐黑 / "white"闪白 / "none"硬切 ----
TRANSITIONS = {
    "c0a": ("black", "black"), "s01": ("black", "black"),
    "s02": ("black", "black"), "s03": ("black", "white"),
    "s04": ("white", "white"), "s05": ("white", "black"),
    "s06": ("black", "black"), "s07": ("black", "black"),
    "c0b": ("black", "black"), "s08": ("black", "black"),
    "s09": ("black", "black"), "s10": ("black", "black"),
    "s11": ("black", "black"), "c0c": ("black", "black"),
    "s12": ("black", "black"), "s13": ("black", "white"),
    "s14": ("white", "black"), "s15": ("black", "black"),
}


def _trans_dur(trans):
    return 0.55 if trans == "white" else 1.1


def fade_io(img, t, dur, trans_in, trans_out):
    k = 1.0
    col = (0, 0, 0)
    if trans_out in ("black", "white") and t > dur - _trans_dur(trans_out):
        k = max(0.0, (dur - t) / _trans_dur(trans_out))
        col = (255, 255, 255) if trans_out == "white" else (0, 0, 0)
    elif trans_in in ("black", "white") and t < _trans_dur(trans_in):
        k = t / _trans_dur(trans_in)
        col = (255, 255, 255) if trans_in == "white" else (0, 0, 0)
    if k >= 1.0:
        return img
    solid = Image.new("RGB", (W, H), col)
    return Image.blend(solid, img, k)


# ---- 多镜头序列：(start_ratio, end_ratio, zoom_start, zoom_end, focus_x, focus_y) ----
# 每个场景 2-3 个镜头：全景(建立环境)→中景(主体)→特写(细节/表情)，zoom 在镜头内线性推近。
# 章节卡保持 zoom=1.0（逐字浮现动画不需要镜头）。
SHOTS = {
    "c0a": [(0.0, 1.0, 1.0, 1.0, 320, 180)],
    "c0b": [(0.0, 1.0, 1.0, 1.0, 320, 180)],
    "c0c": [(0.0, 1.0, 1.0, 1.0, 320, 180)],
    "s01": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：教堂圆顶+观众
            (0.45, 0.72, 1.45, 1.55, 320, 205),   # 中景：棺椁+全息投影
            (0.72, 1.00, 2.00, 2.30, 320, 195)],  # 特写：全息投影脸（y178-272）
    "s02": [(0.00, 0.40, 1.00, 1.08, 320, 180),   # 全景：难民营铁丝网帐篷
            (0.40, 0.72, 1.45, 1.55, 330, 235),   # 中景：拄拐少年
            (0.72, 1.00, 2.00, 2.25, 470, 210)],  # 特写：少年脸（走路终点x500）
    "s03": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：破屋
            (0.45, 0.72, 1.45, 1.55, 330, 250),   # 中景：跪地少年+母亲
            (0.72, 1.00, 2.00, 2.30, 320, 245)],  # 特写：母亲/少年脸
    "s04": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：修理棚
            (0.45, 0.72, 1.45, 1.55, 360, 275),   # 中景：少年+仿生人
            (0.72, 1.00, 2.00, 2.30, 360, 245)],  # 特写：仿生人亮眼
    "s05": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：城市天际线
            (0.45, 0.72, 1.45, 1.55, 320, 205),   # 中景：青年赞比
            (0.72, 1.00, 2.00, 2.30, 320, 165)],  # 特写：青年脸
    "s06": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：病房
            (0.45, 0.72, 1.45, 1.55, 250, 230),   # 中景：卧床老人+理查德
            (0.72, 1.00, 2.00, 2.30, 135, 195)],  # 特写：老人脸
    "s07": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：律所
            (0.45, 0.72, 1.45, 1.55, 320, 225),   # 中景：律师
            (0.72, 1.00, 2.00, 2.30, 320, 200)],  # 特写：律师脸/遗嘱
    "s08": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：矿坑
            (0.45, 0.72, 1.45, 1.55, 320, 210),   # 中景：克隆体
            (0.72, 1.00, 2.00, 2.30, 320, 185)],  # 特写：克隆体脸
    "s09": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：回声卫星腔
            (0.45, 0.72, 1.45, 1.55, 320, 180),   # 中景：克隆体+声波
            (0.72, 1.00, 2.00, 2.30, 320, 150)],  # 特写：脸+声波涟漪
    "s10": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：戴森环+玉米田
            (0.45, 0.72, 1.45, 1.55, 320, 160),   # 中景：环上植株
            (0.72, 1.00, 2.00, 2.30, 320, 140)],  # 特写：植株/渺小剪影
    "s11": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：车间
            (0.45, 0.72, 1.45, 1.55, 320, 235),   # 中景：机械体+老人+理查德
            (0.72, 1.00, 2.00, 2.30, 260, 215)],  # 特写：机械体发光眼带
    "s12": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：书房
            (0.45, 0.72, 1.45, 1.55, 520, 225),   # 中景：机械体写作
            (0.72, 1.00, 2.00, 2.30, 540, 200)],  # 特写：机械体脸/手
    "s13": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：木屋
            (0.45, 0.72, 1.45, 1.55, 320, 235),   # 中景：女孩写信
            (0.72, 1.00, 2.00, 2.30, 320, 215)],  # 特写：信/女孩脸
    "s14": [(0.00, 0.40, 1.00, 1.08, 320, 170),   # 全景：戴森环完整
            (0.40, 0.72, 1.45, 1.55, 320, 160),   # 中景：环断裂
            (0.72, 1.00, 2.00, 2.30, 320, 165)],  # 特写：立方体/断环
    "s15": [(0.00, 0.45, 1.00, 1.10, 320, 180),   # 全景：实验室
            (0.45, 0.72, 1.45, 1.55, 320, 225),   # 中景：立方体+零件
            (0.72, 1.00, 2.00, 2.30, 320, 220)],  # 特写：立方体/电路板
}


def apply_shot(img, t, dur, shots):
    """按镜头序列做数字推拉（NEAREST 放大保留像素颗粒感）。"""
    zoom = 1.0
    fx, fy = W / 2, H / 2
    for (s0, s1, z0, z1, px, py) in shots:
        if s0 <= t / dur < s1:
            k = (t / dur - s0) / max(1e-6, s1 - s0)
            zoom = z0 + (z1 - z0) * k
            fx, fy = px, py
            break
    else:
        _, _, z0, z1, px, py = shots[-1]
        zoom = z1
        fx, fy = px, py
    if zoom <= 1.001:
        return img
    cw, ch = W / zoom, H / zoom
    x0 = max(0.0, min(W - cw, fx - cw / 2))
    y0 = max(0.0, min(H - ch, fy - ch / 2))
    box = (int(round(x0)), int(round(y0)), int(round(x0 + cw)), int(round(y0 + ch)))
    return img.crop(box).resize((W, H), Image.NEAREST)


def base_layer():
    base = Image.new("RGBA", (W, H), BG + (255,))
    return base, ImageDraw.Draw(base)


# ---- 章节卡 ----
def draw_chapter(d, t, title_a, title_b, motif):
    """通用章节卡：墨黑底 + 主题剪影 + 章节标题逐字浮现"""
    vgrad(d, 0, H, INK, BG)
    motif(d, t)
    # 标题
    font_big = ImageFont.truetype(FONT_PATH, 30)
    font_sub = ImageFont.truetype(FONT_PATH, 20)
    # 章节名逐字浮现
    n = int((t - 1.0) / 0.25)
    shown_a = title_a[:max(0, min(n, len(title_a)))] if t >= 1.0 else ""
    shown_b = title_b[:max(0, min(n - len(title_a), len(title_b)))] if n > len(title_a) else ""
    d.text((W // 2, 150), shown_a, font=font_big, fill=(220, 245, 255),
           stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")
    d.text((W // 2, 195), shown_b, font=font_sub, fill=(140, 200, 226),
           stroke_width=1, stroke_fill=(0, 0, 0), anchor="mm")


def draw_c0a(d, t):
    # 上 2049 英国哈特菲尔德庄园：庄园穹顶 + 尖顶 + 体积光柱
    def motif(d, t):
        cx, cy, r = 320, 130, 190
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=DOME)
        for i in range(-3, 4):
            ang = math.radians(90 + i * 22)
            x2 = cx + int(math.cos(ang) * r)
            y2 = cy - int(math.sin(ang) * r)
            d.line([(cx, cy - r + 6), (x2, y2)], fill=DOME_RIB, width=2)
        d.polygon([(cx - 14, cy - r), (cx, cy - r - 46), (cx + 14, cy - r)], fill=COLUMN_H)
        # 体积光柱（不透明预混合，模拟半透明）
        a = 0.30 * (0.9 + 0.1 * math.sin(t * 1.5))
        col = mix((20, 28, 40), BEAM, a)
        d.polygon([(296, 0), (344, 0), (356, 250), (284, 250)], fill=col)
        d.polygon([(304, 0), (336, 0), (344, 250), (296, 250)], fill=mix(col, BEAM, 0.3))
        # 尘埃
        rnd = random.Random(5)
        for i in range(24):
            px = (i * 47 + 13) % W
            py = int((360 - ((t * 10 + i * 31) % 360)))
            d.point((px, py), fill=fc(DUST, 0.4))
    draw_chapter(d, t, "上", "2049 英国哈特菲尔德庄园", motif)


def draw_c0b(d, t):
    # 中 2156 拉格朗日八号：矿坑螺旋名字短线
    def motif(d, t):
        cx, cy = 320, 170
        for ring in range(9):
            r = 40 + ring * 16
            n = 6 + ring * 3
            for i in range(n):
                ang = t * 0.15 + i * (2 * math.pi / n) + ring * 0.4
                x0 = cx + int(math.cos(ang) * r)
                y0 = cy + int(math.sin(ang) * r * 0.8)
                x1 = cx + int(math.cos(ang + 0.12) * (r + 5))
                y1 = cy + int(math.sin(ang + 0.12) * (r + 5) * 0.8)
                c = HOLO_MID if ring % 2 == 0 else (170, 210, 230)
                d.line([(x0, y0), (x1, y1)], fill=c, width=1)
        # 星空
        rnd = random.Random(11)
        for i in range(40):
            d.point((rnd.randint(0, W), rnd.randint(0, 60)), fill=(90, 130, 160))
    draw_chapter(d, t, "中", "2156 拉格朗日八号", motif)


def draw_c0c(d, t):
    # 下 2259 拉格朗日八号：戴森环 + 恒星
    def motif(d, t):
        sx, sy = 320, 170
        # 恒星（光晕不透明预混合）
        for i in range(4):
            r = 24 + i * 10
            a = 0.45 * (1 - i / 4)
            col = mix((16, 14, 18), (255, 190, 120), a)
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
        d.ellipse([sx - 22, sy - 22, sx + 22, sy + 22], fill=(255, 210, 140))
        # 两层戴森环（椭圆）
        for ry, c in ((90, (90, 150, 190)), (60, (130, 190, 220))):
            d.ellipse([sx - 260, sy - ry, sx + 260, sy + ry], outline=c, width=2)
            d.ellipse([sx - 300, sy - ry * 0.6, sx + 300, sy + ry * 0.6], outline=fc(c, 0.6), width=1)
        # 星空
        rnd = random.Random(23)
        for i in range(50):
            d.point((rnd.randint(0, W), rnd.randint(0, H)), fill=(70, 110, 140))
    draw_chapter(d, t, "下", "2259 拉格朗日八号", motif)


# ---- 场景 draw 函数（签名：draw(d, t) -> 可选返回 RGBA 覆盖层，由 render_scene 合成）----

# ===== S01 葬礼（迁移自 render_pixel.py，字幕改为统一 draw_subtitle）=====
def s01_dome(d):
    cx, cy, r = 320, 48, 260
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=DOME)
    for i in range(-4, 5):
        ang = math.radians(90 + i * 18)
        x2 = cx + int(math.cos(ang) * r)
        y2 = cy - int(math.sin(ang) * r)
        d.line([(cx, cy - r + 8), (x2, y2)], fill=DOME_RIB, width=2)
    e_out(d, [cx - 20, 6, cx + 20, 46], 1, HOLO_DK, (70, 120, 150))


def s01_columns(d):
    for x in (78, 184, 456, 562):
        d.rectangle([x - 16, 96, x + 16, 280], fill=COLUMN)
        d.rectangle([x - 16, 96, x - 10, 280], fill=COLUMN_H)
        d.rectangle([x - 24, 88, x + 24, 98], fill=COLUMN_H)
        d.rectangle([x - 22, 278, x + 22, 288], fill=COLUMN_H)


def s01_pedestal(d):
    d.polygon([(258, 274), (382, 274), (400, 284), (240, 284)], fill=PEDESTAL)
    d.rectangle([258, 271, 382, 276], fill=PED_TOP)
    d.line([(258, 273), (382, 273)], fill=fc(BEAM, 0.9), width=1)


def s01_audience(d, t):
    rows = [(292, 0.8, 24), (308, 0.7, 22), (324, 0.6, 20)]
    for ri, (yy, s, n) in enumerate(rows):
        for i in range(n):
            x = 46 + i * 26 + (ri * 9) % 13
            r = 5 * s
            w = 11 * s
            h = 7 * s
            d.ellipse([x - r, yy - r * 2, x + r, yy], fill=CROWD)
            d.rectangle([x - w, yy, x + w, yy + h], fill=CROWD)


def s01_dust(d, t):
    rnd = random.Random(7)
    for i in range(30):
        px = (i * 53 + 11) % W
        py = (360 - ((t * 12 + i * 37) % 360))
        k = 0.5 + 0.5 * math.sin(t * 2 + i)
        d.point((px, int(py)), fill=fc(DUST, 0.25 * k))


def s01_hologram_layer(t):
    flicker = 0.88 + 0.08 * math.sin(t * 2.6) + 0.04 * math.sin(t * 7.3)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    elder_front(ld, 320, 272, h=94, pal=HOLO)
    alpha = int(230 * flicker)
    r, g, b, a = layer.split()
    a = a.point(lambda x: min(x, alpha))
    return Image.merge("RGBA", (r, g, b, a))


def s01_glow(od, t):
    flicker = 0.90 + 0.08 * math.sin(t * 2.6) + 0.03 * math.sin(t * 7.3)
    for i in range(6):
        r = 40 + i * 22
        a = int(42 * (1 - i / 6) * flicker)
        od.ellipse([320 - r, 224 - r, 320 + r, 224 + r],
                   fill=(HOLO_MID[0], HOLO_MID[1], HOLO_MID[2], max(0, a)))


def s01_beams(od, t):
    a1 = int(32 * (0.92 + 0.08 * math.sin(t * 1.4)))
    a2 = int(42 * (0.92 + 0.08 * math.sin(t * 1.4)))
    od.polygon([(286, 0), (354, 0), (370, 274), (270, 274)],
               fill=(BEAM[0], BEAM[1], BEAM[2], a1))
    od.polygon([(304, 0), (336, 0), (344, 274), (296, 274)],
               fill=(BEAM[0], BEAM[1], BEAM[2], a2))


def s01_floor_glow(od, t):
    flicker = 0.90 + 0.08 * math.sin(t * 2.6) + 0.03 * math.sin(t * 7.3)
    a = int(50 * flicker)
    od.ellipse([232, 274, 408, 360], fill=(BEAM[0], BEAM[1], BEAM[2], a))
    od.ellipse([200, 284, 440, 360], fill=(BEAM[0], BEAM[1], BEAM[2], int(a * 0.6)))


def s01_scanlines(od, t):
    rnd = random.Random(int(t * 24))
    for y in range(180, 275, 4):
        off = rnd.randint(0, 2)
        od.line([(285 + off, y), (355, y)], fill=(HOLO_MID[0], HOLO_MID[1], HOLO_MID[2], 24))


def s01_data_dots(od, t):
    rnd = random.Random(int(t * 30))
    for _ in range(12):
        x = rnd.randint(278, 362)
        y = rnd.randint(175, 275)
        r = rnd.choice([1, 1, 2])
        od.ellipse([x - r, y - r, x + r, y + r],
                   fill=(HOLO_HI[0], HOLO_HI[1], HOLO_HI[2], 150))


def draw_s01(d, t):
    vgrad(d, 0, 280, WALL_TOP, WALL_BOT)
    d.rectangle([0, 280, W, H], fill=GROUND)
    d.rectangle([0, 280, W, 288], fill=(22, 34, 50))
    # 地面石板纹理 + 板缝（星露谷式地面细节）
    speckle(d, 0, 288, W, H, (16, 22, 32), 101, n=110, rng=14)
    for gx in range(60, W, 90):
        d.line([(gx, 288), (gx, H)], fill=(8, 12, 20), width=1)
    for gy in range(300, H, 32):
        d.line([(0, gy), (W, gy)], fill=(8, 12, 20), width=1)
    s01_dome(d)
    # 柱子底部投影（先画阴影再画柱身）
    for x in (78, 184, 456, 562):
        drop_shadow(d, x, 282, 28, 10, GROUND, 0.45)
    s01_columns(d)
    s01_audience(d, t)
    drop_shadow(d, 320, 282, 95, 13, GROUND, 0.42)
    s01_pedestal(d)
    s01_dust(d, t)
    # 覆盖层：全息投影 + 体积光 + 辉光 + 扫描线 + 数据点
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    overlay = Image.alpha_composite(overlay, s01_hologram_layer(t))
    od = ImageDraw.Draw(overlay)
    s01_beams(od, t)
    s01_glow(od, t)
    s01_floor_glow(od, t)
    s01_scanlines(od, t)
    s01_data_dots(od, t)
    return overlay


# ===== S02 难民营（少年拄拐走路）=====
def s02_clouds(d, t):
    # 阴天多层云（缓慢漂移）
    for i, (cx, cy, r, sp) in enumerate([(120, 70, 60, 3), (340, 50, 80, 4), (560, 90, 55, 2)]):
        x = (cx + t * sp) % (W + 160) - 80
        for j in range(3):
            ox = -r + j * r
            d.ellipse([x + ox - r * 0.7, cy - r * 0.5, x + ox + r * 0.7, cy + r * 0.5],
                      fill=(70, 78, 88))
        d.ellipse([x - r, cy - 20, x + r, cy + 30], fill=(76, 84, 94))


def s02_tents(d):
    # 帐篷剪影（远处）
    for x, s in [(90, 1.0), (180, 0.8), (470, 0.9), (560, 0.7)]:
        w = 60 * s
        h = 46 * s
        base = 210
        d.polygon([(x - w, base), (x, base - h), (x + w, base)], fill=(46, 52, 60))
        d.polygon([(x - w * 0.3, base), (x, base - h * 0.6), (x + w * 0.3, base)],
                  fill=(30, 34, 42))
        d.rectangle([x - w, base, x + w, base + 4], fill=(26, 30, 38))


def s02_fence(d):
    # 铁丝网（背景，带倒刺）
    for x in range(0, W, 40):
        d.line([(x, 170), (x, 230)], fill=(50, 56, 66), width=2)
    for y in (180, 200, 220):
        d.line([(0, y), (W, y)], fill=(56, 62, 72), width=1)
        for x in range(20, W, 40):
            d.line([(x, y), (x + 8, y - 6)], fill=(56, 62, 72), width=1)
            d.line([(x + 8, y - 6), (x + 16, y)], fill=(56, 62, 72), width=1)


def s02_junk(d):
    # 锈色垃圾堆（齿轮/管道/轮胎堆叠）
    for x, y, r, c in [(40, 300, 26, (110, 78, 50)), (70, 316, 22, (130, 92, 58)),
                       (540, 308, 24, (108, 76, 48)), (580, 322, 20, (124, 88, 56))]:
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=c)
        d.ellipse([x - r * 0.4, y - r * 0.9, x + r * 0.4, y + r * 0.1], fill=fc(c, 1.3))
    # 轮胎
    d.ellipse([590, 292, 620, 306], outline=(70, 66, 62), width=3)
    d.ellipse([596, 296, 614, 302], fill=(46, 44, 42))
    # 齿轮
    for gx, gy in [(60, 290), (555, 296)]:
        for ang in range(0, 360, 45):
            r = math.radians(ang)
            d.line([(gx, gy), (gx + int(math.cos(r) * 12), gy + int(math.sin(r) * 12))],
                   fill=(90, 66, 44), width=2)
        d.ellipse([gx - 8, gy - 8, gx + 8, gy + 8], fill=(80, 60, 42))


def s02_puddles(d):
    # 泥泞水洼反光
    for x, y, w, h in [(300, 300, 90, 16), (420, 330, 60, 10), (160, 320, 70, 12)]:
        d.ellipse([x - w, y - h, x + w, y + h], fill=(66, 74, 82))
        d.ellipse([x - w * 0.5, y - h * 0.4, x + w * 0.5, y + h * 0.4], fill=(82, 92, 100))


def draw_s02(d, t):
    # 阴天天空 + 地面
    vgrad(d, 0, 200, (62, 70, 80), (44, 50, 58))
    d.rectangle([0, 200, W, H], fill=(56, 46, 36))
    d.rectangle([0, 200, W, 210], fill=(48, 40, 32))
    # 泥地纹理：砂砾 + 小石子 + 车辙
    speckle(d, 0, 210, W, H, (60, 50, 40), 201, n=130, rng=18)
    pebbles(d, 0, 220, W, H, (52, 42, 34), 203, n=14)
    for rx in (150, 340, 520):
        d.line([(rx, 250), (rx + 60, 270), (rx + 110, 300)], fill=(42, 34, 28), width=3)
    s02_clouds(d, t)
    s02_fence(d)
    # 帐篷底部阴影
    for x, s in [(90, 1.0), (180, 0.8), (470, 0.9), (560, 0.7)]:
        drop_shadow(d, x, 212, int(34 * s), 6, (56, 46, 36), 0.40)
    s02_tents(d)
    s02_junk(d)
    s02_puddles(d)
    # 少年拄拐走路（左→右）
    walk = max(0.0, min(1.0, (t - 2.0) / 16.0))
    ease = walk * walk * (3 - 2 * walk)
    x = int(140 + ease * 360)
    bob = int(math.sin(walk * math.pi * 6) * 2.5)
    boy_side(d, x, 262 + bob, h=70, pal=SKIN, facing=1)
    # 尘土粒子
    rnd = random.Random(3)
    for i in range(18):
        px = (i * 67 + 19) % W
        py = int((360 - ((t * 14 + i * 41) % 360)))
        d.point((px, py), fill=fc((180, 150, 120), 0.3))
    return None


# ===== S03 母亲之死（雨天废墟 → 垃圾堆读芯片）=====
def s03_rain_bg(d, t):
    vgrad(d, 0, 240, (34, 42, 52), (24, 30, 40))
    d.rectangle([0, 240, W, H], fill=(40, 44, 50))
    d.rectangle([0, 240, W, 250], fill=(46, 52, 58))
    # 泥泞地面纹理 + 碎石 + 积水
    speckle(d, 0, 250, W, H, (42, 46, 52), 301, n=110, rng=14)
    pebbles(d, 0, 260, W, H, (36, 40, 46), 303, n=12)
    # 废墟建筑剪影
    for x, w, h in [(20, 80, 120), (140, 60, 90), (430, 90, 140), (540, 70, 100)]:
        d.rectangle([x, 240 - h, x + w, 240], fill=(18, 22, 30))
        d.polygon([(x - 6, 240 - h), (x + w // 2, 240 - h - 20), (x + w + 6, 240 - h)],
                  fill=(22, 27, 36))
    # 雨丝（斜线）
    rnd = random.Random(13)
    for i in range(70):
        x = rnd.randint(0, W)
        y = rnd.randint(0, H)
        ln = rnd.randint(10, 20)
        d.line([(x, y), (x - 4, y + ln)], fill=(110, 140, 160), width=1)
    # 水洼反光
    for x, y, w in [(300, 300, 80), (480, 330, 50)]:
        d.ellipse([x - w, y - 6, x + w, y + 6], fill=(52, 62, 72))


def s03_mother(d, t):
    # 母亲倒地剪影（横躺，头朝左）
    d.ellipse([150, 252, 176, 272], fill=(14, 18, 26))          # 头
    d.rectangle([160, 262, 300, 274], fill=(14, 18, 26))         # 身体
    d.polygon([(300, 262), (360, 250), (356, 262), (300, 274)], fill=(14, 18, 26))  # 腿
    d.ellipse([130, 258, 154, 270], fill=(14, 18, 26))           # 伸出的手臂
    # 长发（母亲）
    d.polygon([(150, 252), (138, 248), (150, 262)], fill=(10, 13, 19))
    # 衣服褶皱线
    d.line([(190, 262), (190, 274)], fill=(20, 26, 34), width=1)
    d.line([(240, 262), (240, 274)], fill=(20, 26, 34), width=1)


def s03_chip_glow(d, t, x, y):
    # 芯片冰青光点（情感焦点）
    pulse = 0.6 + 0.4 * math.sin(t * 3)
    for i in range(4):
        r = 3 + i * 4
        a = int(120 * (1 - i / 4) * pulse)
        col = mix((20, 30, 40), (130, 202, 226), 0.5 * (1 - i / 4) * pulse)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(220, 245, 255))


def s03_rain_scene(d, t):
    s03_rain_bg(d, t)
    s03_mother(d, t)
    # 少年跪伏（boy_kneel，俯身在母亲身上）
    boy_kneel(d, 300, 272, pal=SKIN, facing=1)
    # 手中芯片
    s03_chip_glow(d, t, 288, 258)


def s03_junk_scene(d, t):
    # 垃圾堆场景（更亮一点，废墟边缘）
    vgrad(d, 0, 240, (40, 48, 58), (30, 36, 46))
    d.rectangle([0, 240, W, H], fill=(58, 48, 38))
    # 地面纹理 + 碎石
    speckle(d, 0, 250, W, H, (60, 50, 40), 401, n=100, rng=16)
    pebbles(d, 0, 255, W, H, (52, 42, 34), 403, n=10)
    # 垃圾堆（锈色）
    for x, y, r in [(80, 300, 30), (130, 318, 24), (500, 306, 28), (560, 322, 22)]:
        drop_shadow(d, x, y + r * 0.6, r, 8, (58, 48, 38), 0.35)
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(110, 78, 50))
    # 光纤（从垃圾堆伸出）
    d.line([(500, 300), (440, 270), (410, 258)], fill=(90, 130, 150), width=2)
    # 少年蹲姿（boy_squat，手拿芯片）
    boy_squat(d, 360, 290, pal=SKIN, facing=-1)
    # 芯片 + 数据光点
    s03_chip_glow(d, t, 402, 256)
    rnd = random.Random(17)
    for i in range(10):
        x = 402 + rnd.randint(-20, 20)
        y = 256 + rnd.randint(-20, 20)
        d.point((x, y), fill=(130, 202, 226))
    # 残存数据流（冰青短线，沿光纤）
    for i in range(6):
        k = (t * 30 + i * 12) % 24
        px = int(500 - k * 3.7)
        py = int(300 - k * 1.7)
        d.point((px, py), fill=(160, 220, 240))


def draw_s03(d, t):
    segs = DATA["s03"]["segs"]
    # 垃圾堆从 narrator2 开始前 1s 起 crossfade（约 boy 段结束时）
    t_junk = segs[2][2] - 1.0 if len(segs) >= 3 else 17.0
    xf = max(0.0, min(1.0, (t - t_junk) / 2.0))
    # 雨天画到 base
    s03_rain_scene(d, t)
    if xf <= 0:
        return None
    # 垃圾堆画到独立层，整体 alpha = xf
    junk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    jd = ImageDraw.Draw(junk)
    s03_junk_scene(jd, t)
    if xf < 1.0:
        r, g, b, a = junk.split()
        a = a.point(lambda x: int(x * xf))
        junk = Image.merge("RGBA", (r, g, b, a))
    return junk


# ===== S04 十六岁修仿生人（棚屋工作台 + 焊接 + 通电）=====
def s04_shed(d):
    # 棚屋木梁 + 工具墙
    vgrad(d, 0, 240, (30, 34, 44), (22, 25, 33))
    d.rectangle([0, 240, W, H], fill=(34, 30, 26))
    # 木地板纹理（横纹 + 砂砾）
    speckle(d, 0, 250, W, H, (36, 32, 28), 501, n=90, rng=12)
    for gy in range(262, H, 28):
        d.line([(0, gy), (W, gy)], fill=(26, 23, 20), width=1)
    # 木梁
    d.rectangle([0, 40, W, 52], fill=(60, 46, 32))
    d.polygon([(0, 40), (60, 0), (80, 0), (20, 40)], fill=(52, 40, 28))
    d.polygon([(560, 40), (620, 0), (640, 0), (620, 40)], fill=(52, 40, 28))
    # 工具墙
    for tx, ty, kind in [(80, 90, 0), (130, 100, 1), (520, 88, 0), (560, 110, 2)]:
        if kind == 0:  # 扳手
            d.ellipse([tx, ty, tx + 12, ty + 10], outline=(90, 96, 104), width=2)
            d.rectangle([tx + 10, ty + 3, tx + 26, ty + 6], fill=(90, 96, 104))
        elif kind == 1:  # 螺丝刀
            d.line([(tx, ty + 18), (tx, ty)], fill=(100, 106, 114), width=2)
            d.rectangle([tx - 2, ty + 16, tx + 2, ty + 24], fill=(80, 60, 40))
        else:  # 钳子
            d.line([(tx, ty), (tx + 14, ty + 6)], fill=(90, 96, 104), width=2)
            d.line([(tx, ty + 6), (tx + 14, ty)], fill=(90, 96, 104), width=2)
    # 工作灯（暖光）
    d.ellipse([420, 20, 452, 52], fill=(140, 110, 70))
    d.polygon([(420, 52), (452, 52), (460, 90), (412, 90)], fill=(70, 60, 44))


def s04_bench(d):
    # 工作台
    d.rectangle([220, 250, 460, 258], fill=(66, 52, 36))
    d.rectangle([236, 258, 248, 320], fill=(52, 42, 30))
    d.rectangle([432, 258, 444, 320], fill=(52, 42, 30))


def s04_android(d, t, on):
    # 仰卧焦黑仿生人（工作台上）
    body = (40, 42, 46)
    burnt = (52, 40, 36)
    d.ellipse([250, 226, 286, 250], fill=burnt)          # 头（焦黑）
    d.rectangle([286, 234, 400, 250], fill=body)          # 躯干
    d.polygon([(400, 234), (440, 228), (440, 240), (400, 248)], fill=body)  # 腿
    d.rectangle([260, 244, 300, 252], fill=body)          # 手臂
    # 焦黑纹理
    for i in range(8):
        rnd = random.Random(50 + i)
        x = rnd.randint(286, 396)
        y = rnd.randint(234, 246)
        d.point((x, y), fill=(66, 52, 44))
    # 医疗十字（胸口）
    d.rectangle([336, 236, 350, 250], fill=(120, 90, 80))
    d.rectangle([329, 243, 357, 243 + 1], fill=(120, 90, 80))
    d.rectangle([329, 243, 357, 244], fill=(120, 90, 80))
    # 眼带（通电后冰青渐亮）
    eye_c = mix((40, 48, 62), (140, 210, 235), on)
    d.rectangle([258, 232, 282, 239], fill=eye_c)
    if on > 0.15:
        for i in range(4):
            r = 5 + i * 6
            col = mix((26, 34, 44), (140, 210, 235), on * 0.85)
            d.ellipse([270 - r, 235 - r, 270 + r, 235 + r], fill=col)


def s04_sparks(d, t, x, y):
    # 焊接火花（暖色飞溅）
    rnd = random.Random(int(t * 40))
    for i in range(10):
        ang = rnd.uniform(math.pi, 2 * math.pi)
        dist = rnd.uniform(4, 16)
        sx = x + int(math.cos(ang) * dist)
        sy = y + int(math.sin(ang) * dist)
        c = rnd.choice([(255, 200, 120), (255, 170, 90), (255, 230, 160)])
        d.line([(x, y), (sx, sy)], fill=c, width=1)
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 220, 160))


def draw_s04(d, t):
    segs = DATA["s04"]["segs"]
    t_power = segs[1][2] - 1.5 if len(segs) >= 2 else 18.0  # 通电在 android 说话前 1.5s 开始
    s04_shed(d)
    drop_shadow(d, 340, 258, 130, 12, (34, 30, 26), 0.40)
    s04_bench(d)
    # 仿生人（仰卧）
    on = 0.0
    if t >= t_power:
        on = max(0.0, min(1.0, (t - t_power) / 3.0))
        if on >= 1.0:
            on = 0.7 + 0.3 * math.sin(t * 3.2)
    s04_android(d, t, on)
    # 少年侧面（拄拐，站在工作台前）
    boy_side(d, 360, 320, h=70, pal=SKIN, facing=1)
    # 焊枪（从少年伸向仿生人）
    d.line([(350, 200), (360, 232)], fill=(90, 96, 104), width=3)
    d.rectangle([346, 196, 354, 204], fill=(70, 76, 84))
    # 火花（焊接阶段）
    if t < t_power:
        s04_sparks(d, t, 355, 238)
    return None


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


_PRICE_FONT = None


def _get_price_font():
    global _PRICE_FONT
    if _PRICE_FONT is None:
        _PRICE_FONT = ImageFont.truetype(FONT_PATH, 40)
    return _PRICE_FONT


# ===== S05 创业开源（夜空城市 + 壁垒墙 + 价格暴跌 + 网络连线 + 财报会议）=====
def s05_sky(d, t):
    vgrad(d, 0, 240, (10, 14, 24), (22, 28, 44))
    rnd = random.Random(7)
    for i in range(30):
        x = rnd.randint(0, W)
        y = rnd.randint(0, 170)
        d.point((x, y), fill=(120, 150, 180))
    d.rectangle([0, 240, W, H], fill=(16, 18, 24))


def s05_city(d, grow):
    for x, w, h, col in [(40, 70, 130, (40, 52, 74)), (140, 80, 170, (48, 60, 84)),
                          (250, 90, 200, (36, 46, 68)), (370, 75, 160, (52, 64, 88)),
                          (470, 85, 190, (42, 54, 76)), (560, 60, 150, (46, 58, 80))]:
        y = 240 - int(h * grow)
        d.rectangle([x, y, x + w, 240], fill=col)
        rnd = random.Random(x * 7 + 13)
        for row in range(1, max(1, (240 - y) // 16)):
            for ci in range(1, max(1, w // 12)):
                wx = x + ci * 12
                wy = y + row * 16
                lit = rnd.random() > 0.45
                d.rectangle([wx, wy, wx + 5, wy + 7],
                            fill=(140, 190, 220) if lit else (24, 32, 46))


def s05_wall(d, a):
    # 三大巨头壁垒墙（横贯，三块巨头标志）
    col = mix((16, 18, 24), (72, 64, 56), a)
    brick = mix((16, 18, 24), (52, 46, 40), a)
    d.rectangle([60, 90, 580, 240], fill=col)
    d.rectangle([60, 90, 580, 96], fill=brick)
    # 砖纹
    for ry in range(100, 240, 16):
        d.line([(60, ry), (580, ry)], fill=brick, width=1)
    # 三大巨头标志（三个几何块，象征垄断）
    for gx in [140, 300, 460]:
        d.polygon([(gx, 150), (gx + 36, 150), (gx + 18, 122)], fill=mix((16, 18, 24), (90, 70, 50), a))
        d.rectangle([gx + 6, 156, gx + 30, 180], fill=mix((16, 18, 24), (70, 60, 50), a))


def s05_price(d, t, t_price):
    frac = _clamp((t - t_price) / 4.0)
    val = int(50000 - 47000 * frac)
    text = f"£{val:,}"
    font = _get_price_font()
    d.text((W // 2, 130), text, font=font, fill=(255, 230, 180),
           stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")


def s05_network(d, t):
    nodes = [(85, 140), (180, 130), (295, 120), (407, 150), (512, 130), (590, 150)]
    for i in range(len(nodes) - 1):
        d.line([nodes[i], nodes[i + 1]], fill=(90, 150, 190), width=1)
    for i in range(len(nodes) - 1):
        k = ((t * 40 + i * 17) % 100) / 100.0
        px = nodes[i][0] + (nodes[i + 1][0] - nodes[i][0]) * k
        py = nodes[i][1] + (nodes[i + 1][1] - nodes[i][1]) * k
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(160, 220, 240))


def s05_meeting_layer(t):
    # 财报会议（覆盖画面，青年赞比背影 + 会议桌 + 股东剪影）
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    vgrad(od, 0, 240, (28, 30, 40), (18, 20, 28))
    od.rectangle([0, 240, W, H], fill=(14, 15, 20))
    # 背景大窗
    od.rectangle([420, 60, 560, 180], fill=(24, 40, 58))
    # 会议桌
    od.rectangle([60, 210, 580, 228], fill=(74, 62, 48))
    od.rectangle([60, 228, 580, 236], fill=(54, 44, 34))
    # 青年赞比背影（站立，黑发，深色西装）
    od.ellipse([290, 128, 330, 168], fill=(26, 26, 34))       # 黑发后脑
    od.rectangle([286, 166, 334, 210], fill=(40, 44, 58))     # 西装
    od.rectangle([292, 166, 328, 210], fill=(52, 58, 76))     # 高光
    od.rectangle([286, 166, 334, 176], fill=(30, 33, 44))     # 肩线
    # 对面股东剪影（3 人）
    for gx in [120, 200, 460]:
        od.ellipse([gx, 158, gx + 24, 182], fill=(22, 25, 34))
        od.rectangle([gx, 182, gx + 24, 210], fill=(28, 31, 42))
    # 屏幕光斑
    od.ellipse([300, 70, 380, 100], fill=(90, 120, 150))
    return ov


def draw_s05(d, t):
    segs = DATA["s05"]["segs"]
    narr_dur = segs[0][1]
    t0 = segs[0][2]
    t_price = t0 + narr_dur * 0.45
    t_net = t0 + narr_dur * 0.62
    t_young = segs[1][2]
    s05_sky(d, t)
    grow = _clamp((t - t0) / 6.0)
    s05_city(d, grow)
    # 壁垒墙（5s 起，价格滚动时崩塌）
    wall_a = _clamp((t - (t0 + 5)) / 2.0) * (1 - _clamp((t - t_price) / 3.0))
    if wall_a > 0.02:
        s05_wall(d, wall_a)
    # 价格数字
    if t >= t_price:
        s05_price(d, t, t_price)
    # 网络连线
    if t >= t_net:
        s05_network(d, t)
    # 财报会议淡入
    if t >= t_young - 1.0:
        a = _clamp((t - (t_young - 1.0)) / 1.5)
        ov = s05_meeting_layer(t)
        if a < 1.0:
            r, g, b, al = ov.split()
            al = al.point(lambda x: int(x * a))
            ov = Image.merge("RGBA", (r, g, b, al))
        return ov
    return None


# ===== S06 临终克隆（病房 + 老年卧姿 + 克隆赞比走进 + 抬手遗嘱）=====
# V2 字符键调色板（对齐 pixel_sprites art 字符）
ELDER_PAL = ELDER   # 老年赞比（白发+深蓝西装）
CLONE_PAL = SKIN    # 克隆赞比（深棕发+肤色）


def s06_room(d):
    # 冷白病房
    vgrad(d, 0, 200, (38, 44, 54), (28, 32, 40))
    # 墙裙（医院下半墙，绿灰）
    d.rectangle([0, 200, W, 240], fill=(34, 40, 48))
    d.line([(0, 200), (W, 200)], fill=(50, 58, 68), width=2)
    d.rectangle([0, 240, W, H], fill=(20, 22, 28))
    # 地面瓷砖纹理 + 砖缝
    speckle(d, 0, 242, W, H, (22, 24, 30), 601, n=80, rng=10)
    for gx in range(50, W, 100):
        d.line([(gx, 242), (gx, H)], fill=(13, 15, 19), width=1)
    for gy in range(250, H, 40):
        d.line([(0, gy), (W, gy)], fill=(13, 15, 19), width=1)
    # 窗（右侧，冷光）
    d.rectangle([470, 50, 600, 190], fill=(30, 46, 66))
    d.rectangle([476, 56, 594, 184], fill=(52, 84, 110))
    d.line([(535, 56), (535, 184)], fill=(30, 46, 66), width=2)
    d.line([(476, 120), (594, 120)], fill=(30, 46, 66), width=2)
    # 床头板
    d.rectangle([70, 120, 150, 210], fill=(48, 54, 62))
    d.rectangle([76, 126, 144, 204], fill=(60, 68, 78))
    # 床底部阴影
    drop_shadow(d, 190, 242, 132, 12, (20, 22, 28), 0.50)
    # 床（白色床单）
    d.rectangle([60, 200, 320, 232], fill=(200, 208, 218))
    d.rectangle([60, 232, 320, 240], fill=(150, 158, 170))
    # 床单褶皱
    for fx in (90, 140, 190, 240, 290):
        d.line([(fx, 200), (fx, 232)], fill=(180, 188, 198), width=1)


def draw_s06(d, t):
    segs = DATA["s06"]["segs"]
    t_clone = segs[0][2] + segs[0][1] * 0.55   # 克隆赞比走进
    t_raise = segs[1][2]                        # 老年赞比抬手
    t_close = segs[3][2]                        # 镜头聚焦（old2）
    s06_room(d)
    # 老年赞比卧姿（床上，露头；说话时口型+呼吸起伏）
    talk_old = _is_talk(segs, "s06_old", t)
    mouth = _mouth(t) if talk_old else 0
    elder_lie(d, 130, 214, pal=ELDER_PAL, facing=1, mouth=mouth, bob=_bob(t))
    # 理查德（床边站立，呼吸起伏）
    richard_front(d, 380, 260, h=85, bob=_bob(t))
    # 克隆赞比走进（从右侧门）
    if t >= t_clone:
        k = _clamp((t - t_clone) / 3.5)
        cx = 620 - int(190 * k)
        elder_front(d, cx, 262, h=94, pal=CLONE_PAL, bob=_bob(t))
        # 地面倒影（走动的克隆赞比，倒影底部对齐脚底+身高）
        d = draw_reflection(d, elder_front, cx, 262, 94, 356, strength=0.20, pal=CLONE_PAL)
    # 老年赞比抬手（old1 说话）
    if t >= t_raise:
        # 抬起的手臂（指向克隆赞比）
        arm = _clamp((t - t_raise) / 1.0)
        ay = 214 - int(20 * arm)
        d.line([(150, 205), (180, ay)], fill=ELDER['f'], width=5)
        d.line([(150, 205), (180, ay)], fill=ELDER['O'], width=7)
        d.line([(150, 205), (180, ay)], fill=ELDER['f'], width=4)
        e_out(d, [176, ay - 4, 186, ay + 4], 1, ELDER['O'], ELDER['F'])
    # 镜头聚焦暗角（old2）
    if t >= t_close:
        va = _clamp((t - t_close) / 1.5) * 140
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        # 四周暗角
        for i in range(0, 120, 8):
            a = int(va * (1 - i / 120))
            od.rectangle([i, i, W - i, H - i], outline=(0, 0, 0, a))
        return ov
    return None


# ===== S07 宣读遗嘱（克隆赞比面部特写 + 全息投影渐隐）=====
def s07_face(d, cx, cy, r):
    # 克隆赞比面部特写（无表情）
    skin_mid = (224, 172, 128)
    skin_hi = (240, 196, 150)
    skin_lo = (180, 130, 92)
    hair = (40, 34, 30)
    # 脸型（描边 + 主体 + 左高光）
    d.ellipse([cx - r - 4, cy - int(r * 0.88) - 4, cx + r + 4, cy + int(r * 0.88) + 4], fill=(120, 84, 60))
    d.ellipse([cx - r, cy - int(r * 0.88), cx + r, cy + int(r * 0.88)], fill=skin_mid)
    d.ellipse([cx - r, cy - int(r * 0.5), cx - int(r * 0.35), cy + int(r * 0.6)], fill=skin_hi)
    d.ellipse([cx + int(r * 0.5), cy + int(r * 0.1), cx + r, cy + int(r * 0.88)], fill=skin_lo)
    # 黑发（头顶 + 两侧）
    d.pieslice([cx - r, cy - int(r * 1.0), cx + r, cy - int(r * 0.12)], 180, 360, fill=hair)
    d.ellipse([cx - r, cy - int(r * 0.7), cx - int(r * 0.52), cy - int(r * 0.02)], fill=hair)
    d.ellipse([cx + int(r * 0.52), cy - int(r * 0.7), cx + r, cy - int(r * 0.02)], fill=hair)
    # 平眉（无表情）
    d.line([(cx - int(r * 0.55), cy - int(r * 0.35)), (cx - int(r * 0.12), cy - int(r * 0.38))], fill=(70, 50, 38), width=4)
    d.line([(cx + int(r * 0.12), cy - int(r * 0.38)), (cx + int(r * 0.55), cy - int(r * 0.35))], fill=(70, 50, 38), width=4)
    # 眼睛（直视，蓝灰虹膜）
    d.ellipse([cx - int(r * 0.5), cy - int(r * 0.28), cx - int(r * 0.1), cy - int(r * 0.06)], fill=(255, 255, 255))
    d.ellipse([cx + int(r * 0.1), cy - int(r * 0.28), cx + int(r * 0.5), cy - int(r * 0.06)], fill=(255, 255, 255))
    d.ellipse([cx - int(r * 0.42), cy - int(r * 0.24), cx - int(r * 0.16), cy - int(r * 0.08)], fill=(60, 100, 120))
    d.ellipse([cx + int(r * 0.16), cy - int(r * 0.24), cx + int(r * 0.42), cy - int(r * 0.08)], fill=(60, 100, 120))
    d.ellipse([cx - int(r * 0.36), cy - int(r * 0.21), cx - int(r * 0.28), cy - int(r * 0.14)], fill=(16, 24, 32))
    d.ellipse([cx + int(r * 0.28), cy - int(r * 0.21), cx + int(r * 0.36), cy - int(r * 0.14)], fill=(16, 24, 32))
    d.point((cx - int(r * 0.30), cy - int(r * 0.19)), fill=(255, 255, 255))
    d.point((cx + int(r * 0.32), cy - int(r * 0.19)), fill=(255, 255, 255))
    # 鼻子
    d.line([(cx - int(r * 0.02), cy - int(r * 0.2)), (cx - int(r * 0.08), cy + int(r * 0.06))], fill=skin_lo, width=4)
    d.line([(cx - int(r * 0.08), cy + int(r * 0.06)), (cx + int(r * 0.12), cy + int(r * 0.06))], fill=skin_lo, width=4)
    # 嘴（平线，无表情）
    d.line([(cx - int(r * 0.26), cy + int(r * 0.38)), (cx + int(r * 0.26), cy + int(r * 0.38))], fill=(120, 80, 58), width=3)
    # 下颌阴影
    d.ellipse([cx - int(r * 0.6), cy + int(r * 0.35), cx + int(r * 0.6), cy + int(r * 0.88)], outline=skin_lo, width=2)
    # 西装领（底部）
    d.polygon([(cx - int(r * 0.7), cy + int(r * 0.9)), (cx + int(r * 0.7), cy + int(r * 0.9)),
               (cx + int(r * 0.3), cy + int(r * 0.55)), (cx - int(r * 0.3), cy + int(r * 0.55))], fill=(40, 46, 60))
    d.polygon([(cx - int(r * 0.15), cy + int(r * 0.55)), (cx + int(r * 0.15), cy + int(r * 0.55)),
               (cx, cy + int(r * 0.8))], fill=(90, 110, 140))


def draw_s07(d, t):
    vgrad(d, 0, H, (10, 12, 18), (18, 22, 30))
    # 扫描线
    for i in range(0, H, 4):
        d.line([(0, i), (W, i)], fill=(0, 0, 0), width=1)
    # 克隆赞比面部特写（呼吸微动）
    cy = 190 + int(2 * math.sin(t * 1.5))
    s07_face(d, 270, cy, 130)
    # 全息投影老年赞比渐隐（0-8s）
    holo_a = 1 - _clamp(t / 8.0)
    if holo_a > 0.02:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        elder_front(od, 520, 200, h=94, pal=HOLO)
        r, g, b, a = ov.split()
        a = a.point(lambda x: int(x * holo_a))
        ov = Image.merge("RGBA", (r, g, b, a))
        return ov
    return None


# ===== S08 矿坑（俯视 + 螺旋名字短线 + 仿生人光点 + 下潜）=====
def s08_pit(d, t):
    cx, cy = 320, 180
    rot = t * 0.35
    # 星球表面（俯视）
    d.ellipse([cx - 300, cy - 300, cx + 300, cy + 300], fill=(32, 27, 22))
    # 环形山（陨石坑：暗坑 + 亮缘）
    rnd = random.Random(305)
    for i in range(26):
        mx = cx + rnd.randint(-260, 260)
        my = cy + rnd.randint(-260, 260)
        if (mx - cx) ** 2 + (my - cy) ** 2 > 262 ** 2:
            continue
        mr = rnd.randint(4, 14)
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(24, 20, 16))
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=(44, 36, 28), width=1)
        d.ellipse([mx - mr // 2, my - mr // 2, mx + mr // 2, my + mr // 2], fill=(18, 15, 12))
    # 矿坑（同心圆，从外到内变深，表示下潜深度）
    for i in range(7):
        r = 268 - i * 38
        col = mix((22, 19, 15), (6, 6, 8), i / 6)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        if i < 6:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(58, 48, 40), width=1)
    # 螺旋名字短线（阿基米德螺旋，从坑底向外）
    for i in range(420):
        th = i * 0.14 + rot
        rr = 26 + th * 7.5
        if rr > 264:
            break
        px = cx + rr * math.cos(th)
        py = cy + rr * math.sin(th)
        ang = th + math.pi / 2
        dx = math.cos(ang) * 3.5
        dy = math.sin(ang) * 3.5
        col = (185, 195, 205) if i % 3 != 0 else (120, 195, 225)
        d.line([(px - dx, py - dy), (px + dx, py + dy)], fill=col, width=1)
    # 仿生人光点（沿螺旋流动）
    for i in range(26):
        th = (t * 0.9 + i * 1.1) % 30
        rr = 40 + th * 7.5
        px = cx + rr * math.cos(th + rot)
        py = cy + rr * math.sin(th + rot)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(185, 235, 255))
    # 星空背景（矿坑外）
    rnd = random.Random(3)
    for i in range(20):
        x = rnd.randint(0, W)
        y = rnd.randint(0, 40)
        d.point((x, y), fill=(140, 170, 200))


def draw_s08(d, t):
    vgrad(d, 0, H, (8, 10, 16), (12, 16, 24))
    s08_pit(d, t)
    return None


# ===== S09 回声卫星（球形共振腔 + 六边形声学面板 + 球心渺小赞比 + 声波涟漪）=====
def s09_hexagons(d, cx, cy, R):
    s = 13
    vsp = int(s * 1.72)
    hsp = int(s * 1.5)
    for row in range(-13, 14):
        y = cy + row * vsp
        off = int(s * 0.75) if row % 2 else 0
        for col in range(-13, 14):
            x = cx + col * hsp + off
            if (x - cx) ** 2 + (y - cy) ** 2 > (R - 8) ** 2:
                continue
            pts = []
            for k in range(6):
                ang = math.pi / 3 * k + math.pi / 6
                pts.append((x + s * 0.82 * math.cos(ang), y + s * 0.82 * math.sin(ang)))
            shade = (row * 7 + col * 13) % 6
            col = mix((28, 32, 42), (54, 62, 78), shade / 5)
            d.polygon(pts, fill=col, outline=(18, 22, 30))


def s09_figure(d, cx, cy):
    # 球心渺小赞比剪影（发光人形，约 20px）
    d.ellipse([cx - 6, cy - 16, cx + 6, cy - 4], fill=(150, 200, 230))
    d.rectangle([cx - 5, cy - 5, cx + 5, cy + 6], fill=(150, 200, 230))
    d.ellipse([cx - 11, cy - 18, cx + 11, cy + 8], outline=(90, 160, 200))


def draw_s09(d, t):
    segs = DATA["s09"]["segs"]
    t_echo = segs[1][2] if len(segs) >= 2 else 20.0
    # 深空背景
    vgrad(d, 0, H, (6, 8, 14), (10, 14, 22))
    # 星空
    rnd = random.Random(9)
    for i in range(40):
        x = rnd.randint(0, W); y = rnd.randint(0, H)
        d.point((x, y), fill=(120, 150, 180))
    # 球形共振腔内壁（六边形声学面板）
    s09_hexagons(d, 320, 180, 152)
    # 球腔轮廓
    d.ellipse([168, 28, 472, 332], outline=(120, 185, 215), width=2)
    # 球心渺小赞比
    s09_figure(d, 320, 180)
    # 声波涟漪（clone 喊"我是谁？"后从球心扩散）
    if t >= t_echo:
        dt = t - t_echo
        for i in range(20):
            wr = (dt * 42 + i * 8) % 152
            a = max(0.0, 1 - wr / 152)
            col = mix((12, 16, 26), (150, 210, 240), a)
            d.ellipse([320 - wr, 180 - wr, 320 + wr, 180 + wr], outline=col, width=1)
    return None


# ===== S10 戴森环玉米田（燃烧恒星 + 两层戴森环 + 玉米 + 渺小理查德）=====
def s10_ring(d, cx, cy, rx, ry, band, corn_seed, t):
    # 环带（发光描边）
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(28, 52, 78), width=band)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(120, 200, 240), width=max(2, band // 3))
    # 玉米（沿环带分布的绿色小竖条）
    rnd = random.Random(corn_seed)
    n = 44
    for i in range(n):
        th = i * math.pi * 2 / n + rnd.uniform(-0.05, 0.05)
        x = cx + rx * math.cos(th)
        y = cy + ry * math.sin(th)
        nx = (x - cx) / rx if rx else 0
        ny = (y - cy) / ry if ry else 0
        ln = math.hypot(nx, ny) or 1
        nx /= ln; ny /= ln
        sway = math.sin(t * 2.0 + i) * 1.5
        tipx = x + nx * 6 + sway
        tipy = y + ny * 6 - 3
        d.line([(x, y), (tipx, tipy)], fill=(64, 132, 58), width=1)
        d.line([(x + 1, y), (tipx + 1, tipy)], fill=(88, 160, 72), width=1)


def s10_tiny(d, cx, cy):
    # 渺小人物剪影（理查德，约 12px）
    d.ellipse([cx - 3, cy - 9, cx + 3, cy - 3], fill=(205, 220, 235))
    d.rectangle([cx - 2, cy - 3, cx + 2, cy + 4], fill=(205, 220, 235))


def draw_s10(d, t):
    cx, cy = 210, 165
    # 深空背景
    vgrad(d, 0, H, (10, 7, 10), (20, 14, 18))
    rnd = random.Random(10)
    for i in range(40):
        x = rnd.randint(0, W); y = rnd.randint(0, H)
        d.point((x, y), fill=(140, 150, 170))
    # 恒星光晕（多层，暖色）
    for i, (r, col) in enumerate([(120, (255, 110, 40)), (95, (255, 155, 60)), (72, (255, 200, 95))]):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # 恒星本体 + 高光
    d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], fill=(255, 228, 150))
    d.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill=(255, 248, 215))
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(255, 255, 240))
    # 耀斑纹理（表面流动）
    for i in range(6):
        a = t * 0.3 + i * 1.05
        sx = cx + 30 * math.cos(a)
        sy = cy + 30 * math.sin(a)
        d.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=(255, 180, 80))
    # 恒星表面米粒组织（对流胞纹理）
    rnd = random.Random(107)
    for i in range(90):
        gx = cx + rnd.randint(-52, 52)
        gy = cy + rnd.randint(-52, 52)
        if (gx - cx) ** 2 + (gy - cy) ** 2 > 52 ** 2:
            continue
        c = rnd.choice([(255, 210, 120), (255, 238, 180), (255, 190, 100)])
        d.point((gx, gy), fill=c)
    # 日珥（恒星边缘喷流）
    for i in range(5):
        a = t * 0.2 + i * 1.26
        px = cx + 58 * math.cos(a)
        py = cy + 58 * math.sin(a)
        d.line([(px, py), (px + 14 * math.cos(a), py + 14 * math.sin(a))],
               fill=(255, 140, 60), width=2)
    # 两层戴森环（内环 + 外环）
    s10_ring(d, cx, cy, 128, 40, 16, 1, t)
    s10_ring(d, cx, cy, 172, 55, 16, 2, t)
    # 渺小理查德（站在外环上，随环带缓慢移动）
    th = -0.4 + math.sin(t * 0.15) * 0.1
    fx = cx + 172 * math.cos(th)
    fy = cy + 55 * math.sin(th)
    s10_tiny(d, int(fx), int(fy))
    return None


# ===== S11 地下车间（半具机器人 + 老态克隆赞比 + 理查德 + 机箱光纤）=====
def draw_s11(d, t):
    segs = DATA["s11"]["segs"]
    t_clone = segs[1][2] if len(segs) >= 2 else 2.0
    t_mech = segs[4][2] if len(segs) >= 5 else 14.0
    pulse = 0.4 + 0.5 * abs(math.sin(t * 0.9))
    # 冷蓝车间背景
    vgrad(d, 0, H, (14, 20, 30), (20, 28, 40))
    for x in range(0, W, 40):
        d.line([(x, 0), (x, 230)], fill=(24, 32, 46), width=1)
    # 顶灯
    d.ellipse([250, 18, 390, 60], fill=(60, 90, 120))
    d.ellipse([260, 24, 380, 54], fill=(90, 130, 165))
    # 地面
    d.rectangle([0, 230, W, H], fill=(16, 22, 32))
    d.line([(0, 230), (230, 230)], fill=(40, 52, 70), width=2)
    d.line([(0, 230), (W, 230)], fill=(40, 52, 70), width=2)
    # 地面钢板纹理 + 焊缝
    speckle(d, 0, 232, W, H, (16, 22, 32), 701, n=90, rng=12)
    for gx in range(40, W, 80):
        d.line([(gx, 232), (gx, H)], fill=(10, 14, 22), width=1)
    # 墙边机箱（右侧）
    drop_shadow(d, 590, 232, 36, 10, (16, 22, 32), 0.40)
    d.rectangle([560, 120, 622, 232], fill=(30, 38, 52))
    d.rectangle([560, 120, 622, 232], outline=(60, 74, 96), width=1)
    for i in range(6):
        y = 135 + i * 17
        on = ((t * 2.0 + i) % 6) < 3
        col = (90, 220, 240) if on else (40, 50, 66)
        d.ellipse([575, y, 582, y + 7], fill=col)
    # 光纤束（mech 后脑 → 机箱）+ 光脉冲流动
    for i in range(6):
        y0 = 178 + i * 7
        y1 = 150 + i * 11
        ph = (t * 0.6 + i * 0.16) % 1.0
        d.line([(268, y0), (562, y1)], fill=(40, 70, 100), width=1)
        px = 268 + (562 - 268) * ph
        py = y0 + (y1 - y0) * ph
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(140, 220, 250))
    # 中央平台
    drop_shadow(d, 260, 268, 70, 12, (16, 22, 32), 0.45)
    d.polygon([(210, 250), (310, 250), (322, 266), (198, 266)], fill=(42, 50, 66))
    d.polygon([(210, 250), (310, 250), (322, 266), (198, 266)], outline=(72, 86, 108), width=1)
    # 半具机器人（mech_front，胸口核心灯随 pulse 呼吸）
    mech_front(d, 260, 250, h=80)
    pr = 7 + 5 * pulse
    core_ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cod = ImageDraw.Draw(core_ov)
    for rr, aa in [(pr + 6, 40), (pr + 3, 80), (pr, 140)]:
        cod.ellipse([260 - rr, 206 - rr, 260 + rr, 206 + rr], outline=(120, 220, 250, aa))
    # 老态克隆赞比（149 岁，左侧）
    elder_front(d, 125, 266, h=94, pal=ELDER_PAL)
    # 理查德（右侧）
    richard_front(d, 455, 266, h=85)
    if core_ov is not None:
        return core_ov
    return None


# ===== S12 机械赞比写书（戴森环背景 + 四本书浮现 + 问号粒子）=====
_BOOK_FONT = None


def _get_book_font():
    global _BOOK_FONT
    if _BOOK_FONT is None:
        _BOOK_FONT = ImageFont.truetype(FONT_PATH, 13)
    return _BOOK_FONT


def s12_book(d, x, y, w, h, cover, title, appear):
    # 书（俯视矩形 + 书脊 + 标题），appear 0..1 渐显
    if appear <= 0.02:
        return
    col = mix((12, 14, 20), cover, appear)
    d.rectangle([x, y, x + w, y + h], fill=col)
    d.rectangle([x, y, x + w, y + h], outline=(20, 22, 30), width=1)
    d.line([(x + 4, y), (x + 4, y + h)], fill=mix((12, 14, 20), (40, 44, 56), appear), width=3)
    f = _get_book_font()
    d.text((x + w // 2, y + h // 2), title, font=f, fill=mix((20, 22, 30), (230, 236, 244), appear), anchor="mm")


def draw_s12(d, t):
    segs = DATA["s12"]["segs"]
    t0 = segs[0][2] if segs else 1.0
    d0 = segs[0][1] if segs else 30.0
    t_b1 = t0 + d0 * 0.30
    t_b2 = t0 + d0 * 0.55
    t_b3 = t0 + d0 * 0.62
    t_b4 = t0 + d0 * 0.85
    t_q = segs[1][2] if len(segs) >= 2 else t0 + d0
    # 戴森环背景（星空 + 暗色环带）
    vgrad(d, 0, H, (8, 9, 14), (14, 17, 26))
    rnd = random.Random(12)
    for i in range(50):
        x = rnd.randint(0, W); y = rnd.randint(0, 210)
        d.point((x, y), fill=(110, 130, 160))
    # 恒星 + 戴森环（暗色，机械本体感）
    d.ellipse([60, 30, 180, 150], fill=(180, 120, 50))
    d.ellipse([40, 10, 200, 170], outline=(60, 100, 130), width=3)
    d.ellipse([20, -15, 260, 190], outline=(40, 70, 95), width=3)
    # 书桌（前景，木纹）
    d.rectangle([0, 240, W, H], fill=(40, 34, 28))
    d.rectangle([0, 240, W, H], outline=(60, 50, 40), width=1)
    d.line([(0, 240), (W, 240)], fill=(70, 58, 46), width=2)
    speckle(d, 0, 244, W, H, (40, 34, 28), 704, n=80, rng=14)
    for gy in range(256, H, 26):
        d.line([(0, gy), (W, gy)], fill=(30, 25, 21), width=1)
    # 机械赞比（书桌后，右侧）
    mech_front(d, 540, 250, h=80)
    # 四本书依次浮现
    a1 = _clamp((t - t_b1) / 0.6)
    a2 = _clamp((t - t_b2) / 0.6)
    a3 = _clamp((t - t_b3) / 0.6)
    # 《谁》闪烁（写不出来，反复推倒）
    a4 = _clamp((t - t_b4) / 0.6)
    if t >= t_b4:
        a4 = a4 * (0.55 + 0.45 * math.sin(t * 5.0))
    s12_book(d, 150, 252, 72, 52, (46, 62, 96), "赞", a1)
    s12_book(d, 235, 258, 56, 42, (90, 92, 100), "碑", a2)
    s12_book(d, 305, 258, 56, 42, (50, 100, 110), "回", a3)
    s12_book(d, 375, 264, 42, 32, (210, 214, 224), "谁", a4)
    # 问号粒子（mech 说话时从《谁》散开）
    if t >= t_q:
        rndq = random.Random(7)
        for i in range(60):
            dt = (t - t_q) + i * 0.05
            ang = rndq.uniform(0, math.pi * 2)
            sp = rndq.uniform(15, 60)
            px = 396 + math.cos(ang) * sp * dt * 0.6
            py = 260 + math.sin(ang) * sp * dt * 0.5 - 20
            if 0 <= px < W and 0 <= py < H:
                f = _get_book_font()
                d.text((px, py), "？", font=f, fill=(200, 220, 240), anchor="mm")
    return None


# ===== S13 女孩写信（暖色小屋 + 伏案女孩 + 仿生人保姆 + 信纸）=====
def s13_girl_sit(d, cx, cy):
    hair = (66, 44, 32)
    dress = (176, 146, 168)
    skin = (222, 172, 128)
    outline = (30, 24, 20)
    # 坐姿女孩（背面，马尾，伏案）
    d.ellipse([cx - 15, cy - 56, cx + 15, cy - 28], fill=outline)
    d.ellipse([cx - 14, cy - 56, cx + 14, cy - 28], fill=hair)  # 后脑勺
    # 马尾垂落
    d.polygon([(cx - 4, cy - 30), (cx + 12, cy - 32), (cx + 18, cy - 6), (cx + 2, cy - 2)], fill=hair)
    # 身体（伏案俯身）
    d.polygon([(cx - 18, cy - 28), (cx + 18, cy - 28), (cx + 13, cy + 8), (cx - 13, cy + 8)], fill=outline)
    d.polygon([(cx - 17, cy - 28), (cx + 17, cy - 28), (cx + 12, cy + 8), (cx - 12, cy + 8)], fill=dress)
    # 手臂伸向桌面
    d.line([(cx - 13, cy - 20), (cx - 26, cy - 2)], fill=dress, width=5)
    d.line([(cx + 13, cy - 20), (cx + 26, cy - 2)], fill=dress, width=5)
    d.ellipse([cx - 28, cy - 3, cx - 22, cy + 3], fill=skin)
    d.ellipse([cx + 22, cy - 3, cx + 28, cy + 3], fill=skin)


def s13_nanny(d, cx, cy, warm):
    shell = (198, 203, 214)
    apron = (228, 198, 178)
    outline = (60, 62, 70)
    eye = mix((62, 62, 72), (240, 182, 92), warm)
    # 头
    d.ellipse([cx - 13, cy - 72, cx + 13, cy - 46], fill=outline)
    d.ellipse([cx - 12, cy - 72, cx + 12, cy - 46], fill=shell)
    # 暖色眼
    d.rectangle([cx - 8, cy - 62, cx - 3, cy - 57], fill=eye)
    d.rectangle([cx + 3, cy - 62, cx + 8, cy - 57], fill=eye)
    d.line([(cx - 9, cy - 53), (cx + 9, cy - 53)], fill=(120, 120, 132), width=1)
    # 身体（外壳 + 围裙）
    d.rectangle([cx - 16, cy - 46, cx + 16, cy - 8], fill=outline)
    d.rectangle([cx - 15, cy - 46, cx + 15, cy - 8], fill=shell)
    d.polygon([(cx - 8, cy - 46), (cx + 8, cy - 46), (cx + 6, cy - 22), (cx - 6, cy - 22)], fill=apron)
    # 手臂
    d.rectangle([cx - 20, cy - 44, cx - 15, cy - 14], fill=shell)
    d.rectangle([cx + 15, cy - 44, cx + 20, cy - 14], fill=shell)


def draw_s13(d, t):
    segs = DATA["s13"]["segs"]
    t_letter = segs[1][2] if len(segs) >= 2 else 12.0
    t_cold = segs[2][2] if len(segs) >= 3 else 26.0
    # 暖色小屋
    vgrad(d, 0, H, (120, 82, 56), (70, 48, 34))
    # 木墙板（竖缝 + 横节疤）
    for x in range(0, W, 60):
        d.line([(x, 0), (x, 235)], fill=(90, 60, 42), width=1)
    rnd = random.Random(131)
    for i in range(14):
        kx = rnd.randint(6, W - 6); ky = rnd.randint(6, 228)
        d.ellipse([kx - 3, ky - 2, kx + 3, ky + 2], outline=(70, 46, 30), width=1)
    # 窗外星空 + 农田（左上窗）
    d.rectangle([40, 40, 240, 160], fill=(16, 20, 40))
    d.rectangle([40, 40, 240, 160], outline=(100, 70, 48), width=5)
    rnd = random.Random(13)
    for i in range(18):
        x = rnd.randint(48, 232); y = rnd.randint(46, 100)
        d.point((x, y), fill=(200, 210, 240))
    # 农田（窗下绿色地块）
    for i in range(4):
        y = 110 + i * 12
        d.polygon([(48, y), (232, y), (232, y + 10), (48, y + 10)], fill=(60, 110, 60) if i % 2 else (74, 126, 70))
    # 暖灯（天花板）
    d.ellipse([430, 16, 500, 44], fill=(255, 200, 120))
    d.ellipse([440, 20, 490, 40], fill=(255, 230, 170))
    # 桌子（前景，木纹）
    d.rectangle([0, 235, W, H], fill=(96, 66, 44))
    d.line([(0, 235), (W, 235)], fill=(120, 84, 56), width=2)
    speckle(d, 0, 238, W, H, (96, 66, 44), 702, n=70, rng=14)
    for gy in range(250, H, 22):
        d.line([(0, gy), (W, gy)], fill=(78, 52, 34), width=1)
    # 信纸（桌上，girl 说话时渐显）
    if t >= t_letter:
        a = _clamp((t - t_letter) / 1.5)
        d.rectangle([300, 236, 440, 276], fill=mix((96, 66, 44), (235, 230, 210), a))
        d.rectangle([300, 236, 440, 276], outline=mix((96, 66, 44), (170, 160, 140), a), width=1)
        f = _get_book_font()
        d.text((370, 256), "晚安，小姐。", font=f, fill=mix((96, 66, 44), (80, 70, 60), a), anchor="mm")
    # 伏案女孩（桌前）
    s13_girl_sit(d, 240, 250)
    # 仿生人保姆（桌旁，暖色眼随 t 渐亮）
    warm = _clamp((t - 8.0) / 4.0)
    s13_nanny(d, 520, 250, warm)
    # 末尾转冷（narrator2 随手把信扔了）
    if t >= t_cold:
        cold_a = _clamp((t - t_cold) / 2.0) * 0.45
        ov = Image.new("RGBA", (W, H), (20, 40, 70, int(cold_a * 255)))
        return ov
    return None


# ===== S14 立方体交接 + 戴森环崩塌 =====
def s14_star(d, cx, cy, r):
    for i, (rr, col) in enumerate([(int(r * 1.9), (255, 110, 40)), (int(r * 1.5), (255, 155, 60)), (int(r * 1.15), (255, 200, 95))]):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 228, 150))
    d.ellipse([cx - int(r * 0.7), cy - int(r * 0.7), cx + int(r * 0.7), cy + int(r * 0.7)], fill=(255, 248, 215))


def s14_ring_cold(d, cx, cy, rx, ry, band, break_ang):
    # 冷色机械环带（断裂时用 break_ang 断开）
    for k in range(40):
        a0 = k * math.pi * 2 / 40
        a1 = a0 + math.pi * 2 / 40 * 0.7
        # 断裂：靠近 break_ang 的弧段跳过
        mid = (a0 + a1) / 2
        if abs((mid - break_ang + math.pi) % (math.pi * 2) - math.pi) < 0.5:
            continue
        x0 = cx + rx * math.cos(a0); y0 = cy + ry * math.sin(a0)
        x1 = cx + rx * math.cos(a1); y1 = cy + ry * math.sin(a1)
        d.line([(x0, y0), (x1, y1)], fill=(70, 110, 140), width=band)


def draw_s14(d, t):
    segs = DATA["s14"]["segs"]
    t_cube = segs[2][2] if len(segs) >= 3 else 10.0
    t_collapse = segs[7][2] if len(segs) >= 8 else 45.0
    cx, cy = 210, 150
    # 深空背景
    vgrad(d, 0, H, (8, 9, 14), (14, 17, 26))
    rnd = random.Random(14)
    for i in range(50):
        x = rnd.randint(0, W); y = rnd.randint(0, 220)
        d.point((x, y), fill=(120, 140, 170))
    # 星云斑块（预混合暗色，点缀深空层次）
    for (nx, ny, nr, nc) in [(80, 60, 60, (34, 30, 52)), (520, 90, 70, (30, 40, 58)),
                              (360, 40, 45, (38, 30, 50)), (600, 180, 50, (28, 36, 50))]:
        d.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=nc)
    # 亮星（带十字星芒）
    for (sx, sy) in [(120, 30), (480, 50), (580, 140), (60, 150)]:
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(220, 235, 250))
        d.line([(sx - 6, sy), (sx + 6, sy)], fill=(160, 180, 210), width=1)
        d.line([(sx, sy - 6), (sx, sy + 6)], fill=(160, 180, 210), width=1)
    # 恒星（崩塌后膨胀）
    star_r = 58
    if t >= t_collapse:
        dt = t - t_collapse
        if dt > 1.2:
            star_r = 58 + min(200, (dt - 1.2) * 40)
    s14_star(d, cx, cy, star_r)
    # 戴森环（冷机械，无玉米）
    break_ang = 0.0
    if t >= t_collapse:
        break_ang = (t - t_collapse) * 1.5
    s14_ring_cold(d, cx, cy, 128, 40, 12, break_ang)
    s14_ring_cold(d, cx, cy, 172, 55, 12, break_ang)
    # 机械赞比 + 理查德（环带上的渺小剪影，崩塌前）
    if t < t_collapse:
        s10_tiny(d, cx + 128, cy)
        s10_tiny(d, cx - 100, cy + 30)
    # 立方体（前景特写，segs[2] 后掏出放大）
    if t >= t_cube:
        csize = int(8 + 62 * _clamp((t - t_cube) / 2.0))
        cubex, cubey = 470, 300
        # 立方体微光（冰青边缘）
        cube(d, cubex, cubey, size=csize)
    # 崩塌白光（segs[7] 后）
    ov = None
    if t >= t_collapse:
        dt = t - t_collapse
        # 耀眼白光（0-1.2s）
        if dt < 1.2:
            wa = int(255 * math.sin(dt / 1.2 * math.pi))
            ov = Image.new("RGBA", (W, H), (255, 245, 220, wa))
        # 渐暗 + 立方体微光（4s 后）
        elif dt > 4.0:
            dark = _clamp((dt - 4.0) / 3.0) * 200
            ov = Image.new("RGBA", (W, H), (4, 6, 12, int(dark)))
            # 立方体微光残留在下方
            if dark > 150:
                d.ellipse([440, 270, 500, 330], fill=(40, 120, 150))
                d.ellipse([450, 280, 490, 320], fill=(90, 190, 220))
    return ov


# ===== S15 立方体拆解（办公室 + 立方体 + 四零件 + 代码 + 片尾）=====
def s15_bookshelf(d):
    d.rectangle([0, 0, W, 220], fill=(46, 38, 30))
    for row in range(3):
        y = 20 + row * 62
        for col in range(10):
            x = 30 + col * 60
            w = 50 - (col % 3) * 8
            d.rectangle([x, y, x + w, y + 52], fill=(90 + (col % 4) * 20, 70 + (row % 3) * 22, 48))
            d.rectangle([x, y, x + w, y + 52], outline=(30, 24, 20), width=1)
        d.line([(25, y + 55), (W - 25, y + 55)], fill=(60, 48, 38), width=3)


def s15_parts(d, cx, cy):
    f = _get_book_font()
    # 声音传感器（圆形，小孔）
    d.ellipse([cx - 190, cy - 30, cx - 130, cy + 30], fill=(70, 76, 88))
    d.ellipse([cx - 175, cy - 15, cx - 145, cy + 15], fill=(40, 44, 52))
    for i in range(5):
        d.point((cx - 160 + i * 8 - 16, cy), fill=(120, 130, 145))
    d.text((cx - 160, cy + 42), "声音传感器", font=f, fill=(200, 210, 220), anchor="mm")
    # 扬声器（同心圆）
    d.ellipse([cx - 90, cy - 30, cx - 30, cy + 30], fill=(60, 64, 74))
    d.ellipse([cx - 80, cy - 20, cx - 40, cy + 20], fill=(120, 128, 140))
    d.ellipse([cx - 68, cy - 8, cx - 52, cy + 8], fill=(40, 44, 52))
    d.text((cx - 60, cy + 42), "扬声器", font=f, fill=(200, 210, 220), anchor="mm")
    # 同位素电池（矩形 + 辐射符号）
    d.rectangle([cx + 10, cy - 28, cx + 70, cy + 30], fill=(80, 70, 40))
    d.rectangle([cx + 10, cy - 28, cx + 70, cy + 30], outline=(30, 26, 16), width=2)
    d.ellipse([cx + 30, cy - 12, cx + 50, cy + 8], fill=(200, 190, 70))
    d.text((cx + 40, cy + 42), "同位素电池", font=f, fill=(200, 210, 220), anchor="mm")
    # 电路板（绿色 + 芯片）
    d.rectangle([cx + 90, cy - 28, cx + 180, cy + 30], fill=(40, 90, 50))
    d.rectangle([cx + 90, cy - 28, cx + 180, cy + 30], outline=(16, 40, 24), width=2)
    d.rectangle([cx + 120, cy - 14, cx + 150, cy + 14], fill=(20, 26, 22))
    for i in range(5):
        d.line([(cx + 96, cy - 16 + i * 8), (cx + 120, cy - 16 + i * 8)], fill=(120, 190, 130), width=1)
    d.text((cx + 135, cy + 42), "电路板", font=f, fill=(200, 210, 220), anchor="mm")


def s15_code(d, t):
    d.rectangle([0, 0, W, H], fill=(18, 48, 28))
    for i in range(12):
        d.line([(0, i * 30), (W, i * 30)], fill=(28, 66, 40), width=1)
    d.rectangle([120, 60, 520, 280], fill=(10, 20, 14))
    d.rectangle([120, 60, 520, 280], outline=(80, 160, 100), width=2)
    f = _get_book_font()
    code_lines = [
        'if input == "你好":',
        '    output("你好，我是赞比")',
    ]
    for i, ln in enumerate(code_lines):
        d.text((150, 100 + i * 40), ln, font=f, fill=(140, 220, 160), anchor="lm")
    if int(t * 4) % 2 == 0:
        d.rectangle([150, 185, 162, 198], fill=(140, 220, 160))


def draw_s15(d, t):
    segs = DATA["s15"]["segs"]
    dur = DATA["s15"]["dur"]
    t_cube1 = segs[1][2] if len(segs) >= 2 else 13.0
    t_open = segs[2][2] if len(segs) >= 3 else 19.0
    t_code = segs[4][2] if len(segs) >= 5 else 31.0
    t_title = dur - 5.0
    # 片尾标题（最后 5s）
    if t >= t_title:
        vgrad(d, 0, H, (4, 6, 10), (8, 12, 18))
        a = _clamp((t - t_title) / 1.5)
        f = _get_price_font()
        d.text((W // 2, 140), "赞比的遗产", font=f, fill=mix((8, 12, 18), (120, 190, 225), a), anchor="mm")
        fb = _get_book_font()
        d.text((W // 2, 210), "原著 · 野生艺术家 · 荒启科幻", font=fb, fill=mix((8, 12, 18), (150, 170, 190), a), anchor="mm")
        return None
    # 电路板代码特写（t_code 后）
    if t >= t_code:
        s15_code(d, t)
        return None
    # 办公室
    s15_bookshelf(d)
    d.rectangle([0, 220, W, H], fill=(96, 66, 44))
    d.line([(0, 220), (220, 220)], fill=(120, 84, 56), width=2)
    d.line([(0, 220), (W, 220)], fill=(120, 84, 56), width=2)
    # 木地板纹理
    speckle(d, 0, 224, W, H, (96, 66, 44), 703, n=80, rng=14)
    for gy in range(236, H, 24):
        d.line([(0, gy), (W, gy)], fill=(78, 52, 34), width=1)
    # 立方体底部阴影
    drop_shadow(d, 320, 252, 42, 10, (96, 66, 44), 0.40)
    # 拆解阶段：四零件
    if t >= t_open:
        s15_parts(d, W // 2, 250)
        return None
    # 完整立方体 + 声波涟漪
    cube(d, 320, 250, size=70)
    if t >= t_cube1:
        dt = t - t_cube1
        for i in range(6):
            wr = (dt * 30 + i * 14) % 70
            a = max(0.0, 1 - wr / 70)
            col = mix((96, 66, 44), (140, 210, 235), a)
            d.ellipse([320 - wr, 250 - wr, 320 + wr, 250 + wr], outline=col, width=1)
    return None


DRAW = {
    "c0a": draw_c0a, "c0b": draw_c0b, "c0c": draw_c0c,
    "s01": draw_s01, "s02": draw_s02, "s03": draw_s03, "s04": draw_s04,
    "s05": draw_s05, "s06": draw_s06, "s07": draw_s07, "s08": draw_s08,
    "s09": draw_s09, "s10": draw_s10, "s11": draw_s11, "s12": draw_s12,
    "s13": draw_s13, "s14": draw_s14, "s15": draw_s15,
}


# ---- 渲染 ----
def render_scene(key):
    cfg = DATA[key]
    dur = cfg["dur"]
    subs = cfg["subs"]
    out_dir = os.path.join(FRAMES_DIR, key)
    os.makedirs(out_dir, exist_ok=True)
    font = ImageFont.truetype(FONT_PATH, 22)
    draw = DRAW.get(key)
    frames = int(round(dur * FPS))
    for fi in range(frames):
        t = fi / FPS
        base, d = base_layer()
        overlay = draw(d, t)
        if overlay is not None:
            base = Image.alpha_composite(base, overlay)
            d = ImageDraw.Draw(base)
        frame = base.convert("RGB")
        # 多镜头推拉（在字幕前，保证字幕清晰不随镜头缩放）
        frame = apply_shot(frame, t, dur, SHOTS.get(key, [(0.0, 1.0, 1.0, 1.0, 320, 180)]))
        if subs:
            draw_subtitle(ImageDraw.Draw(frame), font, t, subs)
        trans_in, trans_out = TRANSITIONS.get(key, ("black", "black"))
        frame = fade_io(frame, t, dur, trans_in, trans_out)
        big = frame.resize((W * SCALE, H * SCALE), Image.NEAREST)
        big.save(os.path.join(out_dir, f"f{fi:05d}.png"))
    print(f"[OK] {key}: {frames} 帧, {dur}s")
    return frames


# ---- 合成 ----
def assemble():
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    bgm_map = {
        "c0a": "sorrow", "s01": "sorrow", "s02": "sorrow", "s03": "sorrow",
        "s04": "hope", "s05": "hope", "s06": "sorrow", "s07": "sorrow",
        "c0b": "mystery", "s08": "mystery", "s09": "mystery", "s10": "hope",
        "s11": "mystery", "c0c": "serene", "s12": "serene", "s13": "hope",
        "s14": "epic", "s15": "serene",
    }
    bgm_vol = {"sorrow": 0.13, "hope": 0.11, "mystery": 0.09,
               "epic": 0.15, "serene": 0.09}
    # 每场景：帧 → mp4（无音轨）
    seg_videos = []
    for key in ORDER:
        cfg = DATA[key]
        dur = cfg["dur"]
        v = os.path.join(FRAMES_DIR, key + "_v.mp4")
        subprocess.run([ff, "-y", "-framerate", str(FPS), "-i",
                        os.path.join(FRAMES_DIR, key, "f%05d.png"),
                        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-preset", "medium", v],
                       check=True, capture_output=True, encoding="utf-8", errors="ignore")
        # 配音段（按 seg 起始时间 adelay）
        segs = cfg["segs"]
        if not segs:
            # 章节卡：静音
            wav = os.path.join(FRAMES_DIR, key + ".wav")
            subprocess.run([ff, "-y", "-f", "lavfi", "-i",
                            "anullsrc=r=48000:cl=stereo", "-t", f"{dur:.2f}", wav],
                           check=True, capture_output=True, encoding="utf-8", errors="ignore")
        else:
            wav = os.path.join(FRAMES_DIR, key + ".wav")
            inputs = []
            filters = []
            for i, (name, dsec, tstart) in enumerate(segs):
                inputs += ["-i", os.path.join(AUDIO_DIR, name + ".mp3")]
                filters.append(f"[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,adelay={int(tstart*1000)}|{int(tstart*1000)}[a{i}]")
            mix_n = len(segs)
            filters.append("".join(f"[a{i}]" for i in range(mix_n)) + f"amix=inputs={mix_n}:duration=longest,apad[aout]")
            subprocess.run([ff, "-y"] + inputs +
                           ["-filter_complex", ";".join(filters),
                            "-map", "[aout]", "-t", f"{dur:.2f}", wav],
                           check=True, capture_output=True, encoding="utf-8", errors="ignore")
        # BGM：循环 + 低音量 → 与配音混合
        theme = bgm_map.get(key)
        bgm_file = os.path.join(BGM_DIR, theme + ".mp3")
        if not os.path.exists(bgm_file):
            bgm_file = os.path.join(BGM_DIR, theme + ".wav")
        if theme and os.path.exists(bgm_file):
            bgm_loop = os.path.join(FRAMES_DIR, key + "_bgm.wav")
            subprocess.run([ff, "-y", "-stream_loop", "-1", "-i", bgm_file,
                            "-t", f"{dur:.2f}",
                            "-af", f"volume={bgm_vol[theme]}",
                            "-ar", "48000", "-ac", "2", bgm_loop],
                           check=True, capture_output=True, encoding="utf-8", errors="ignore")
            mixed = os.path.join(FRAMES_DIR, key + "_mix.wav")
            subprocess.run([ff, "-y", "-i", wav, "-i", bgm_loop,
                            "-filter_complex",
                            "[0:a][1:a]amix=inputs=2:duration=longest:normalize=0[out]",
                            "-map", "[out]", mixed],
                           check=True, capture_output=True, encoding="utf-8", errors="ignore")
            wav = mixed
        # mux 视频 + 音轨
        seg_mp4 = os.path.join(FRAMES_DIR, key + ".mp4")
        subprocess.run([ff, "-y", "-i", v, "-i", wav,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", seg_mp4],
                       check=True, capture_output=True, encoding="utf-8", errors="ignore")
        seg_videos.append(seg_mp4)
        print(f"[OK] {key}.mp4")
    # concat
    concat_list = os.path.join(FRAMES_DIR, "concat.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for v in seg_videos:
            f.write(f"file '{v}'\n")
    subprocess.run([ff, "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
                    "-c", "copy", OUT_MP4],
                   check=True, capture_output=True, encoding="utf-8", errors="ignore")
    print(f"[DONE] {OUT_MP4}")


def main():
    import sys
    keys = sys.argv[1:] if len(sys.argv) > 1 else ORDER
    for k in keys:
        if k not in DATA:
            print(f"[SKIP] 未知场景 {k}")
            continue
        render_scene(k)
    if len(sys.argv) == 1:
        assemble()


if __name__ == "__main__":
    main()
