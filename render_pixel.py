# -*- coding: utf-8 -*-
"""赞比的遗产 —— 像素动画渲染框架（合金弹头规格，640x360 画布 SCALE=3）
S01 葬礼正式版：全息投影用 sprite 库 elder_front（冰青单色半透明）+ 葬礼大厅 + 远景人群 + 统一字幕
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont
from pixel_sprites import elder_front, HOLO

W, H = 640, 360
SCALE = 3
DUR = 19.0
FPS = 30
FRAMES = int(DUR * FPS)
OUT = "frames_pixel"
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

# ---- 调色板（荒启科幻 GEO 冷峻：墨黑/冰青/雾蓝）----
BG      = (7, 10, 15)
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
# 全息冰青单色四层（描边→阴影→主体→高光）
HOLO_HI = (225, 250, 255)
HOLO_MID= (130, 202, 226)
HOLO_LO = (50, 110, 134)
HOLO_DK = (16, 40, 56)
DUST    = (150, 215, 238)

SUBS = [
    (1.0, "赞比是银河系中最富有的人。"),
    (3.9, "他去世的那天，银河系有三百亿人在哀悼。"),
    (8.1, "葬礼在赞比的家乡举行，"),
    (10.6, "全息投影把他生前的影像投射在半空中。"),
    (14.6, "没有人哭。"),
    (15.7, "因为来的，大部分都是仿生人。"),
]


def fc(c, k):
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k))


def mix(c1, c2, k):
    return (int(c1[0] * (1 - k) + c2[0] * k),
            int(c1[1] * (1 - k) + c2[1] * k),
            int(c1[2] * (1 - k) + c2[2] * k))


def e_out(d, bbox, pad, outline, fill):
    """椭圆：先外扩描边，再主体（合金弹头黑描边）"""
    x0, y0, x1, y1 = bbox
    d.ellipse([x0 - pad, y0 - pad, x1 + pad, y1 + pad], fill=outline)
    d.ellipse([x0, y0, x1, y1], fill=fill)


def r_out(d, bbox, pad, outline, fill):
    """矩形：先外扩描边，再主体"""
    x0, y0, x1, y1 = bbox
    d.rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], fill=outline)
    d.rectangle([x0, y0, x1, y1], fill=fill)


def draw_background(d):
    for y in range(0, 280):
        k = y / 280.0
        d.line([(0, y), (W, y)], fill=mix(WALL_TOP, WALL_BOT, k))
    d.rectangle([0, 280, W, H], fill=GROUND)
    d.rectangle([0, 280, W, 288], fill=(22, 34, 50))


def draw_dome(d):
    cx, cy, r = 320, 48, 260
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=DOME)
    for i in range(-4, 5):
        ang = math.radians(90 + i * 18)
        x2 = cx + int(math.cos(ang) * r)
        y2 = cy - int(math.sin(ang) * r)
        d.line([(cx, cy - r + 8), (x2, y2)], fill=DOME_RIB, width=2)
    # 顶部圆光
    e_out(d, [cx - 20, 6, cx + 20, 46], 1, HOLO_DK, (70, 120, 150))


def draw_columns(d):
    for x in (78, 184, 456, 562):
        d.rectangle([x - 16, 96, x + 16, 280], fill=COLUMN)
        d.rectangle([x - 16, 96, x - 10, 280], fill=COLUMN_H)
        d.rectangle([x - 24, 88, x + 24, 98], fill=COLUMN_H)
        d.rectangle([x - 22, 278, x + 22, 288], fill=COLUMN_H)


def draw_pedestal(d):
    d.polygon([(258, 274), (382, 274), (400, 284), (240, 284)], fill=PEDESTAL)
    d.rectangle([258, 271, 382, 276], fill=PED_TOP)
    d.line([(258, 273), (382, 273)], fill=fc(BEAM, 0.9), width=1)


def draw_hologram_layer(t):
    """全息投影老人：用 sprite 库 elder_front（冰青单色）画到半透明 RGBA 层，脚底 y=272"""
    flicker = 0.88 + 0.08 * math.sin(t * 2.6) + 0.04 * math.sin(t * 7.3)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    elder_front(ld, 320, 272, h=94, pal=HOLO)
    # 整体半透明（全息闪烁）
    alpha = int(230 * flicker)
    r, g, b, a = layer.split()
    a = a.point(lambda x: min(x, alpha))
    return Image.merge("RGBA", (r, g, b, a))


def draw_glow(od, t):
    flicker = 0.90 + 0.08 * math.sin(t * 2.6) + 0.03 * math.sin(t * 7.3)
    for i in range(6):
        r = 40 + i * 22
        a = int(42 * (1 - i / 6) * flicker)
        od.ellipse([320 - r, 224 - r, 320 + r, 224 + r],
                   fill=(HOLO_MID[0], HOLO_MID[1], HOLO_MID[2], max(0, a)))


def draw_beams(od, t):
    a1 = int(32 * (0.92 + 0.08 * math.sin(t * 1.4)))
    a2 = int(42 * (0.92 + 0.08 * math.sin(t * 1.4)))
    od.polygon([(286, 0), (354, 0), (370, 274), (270, 274)],
               fill=(BEAM[0], BEAM[1], BEAM[2], a1))
    od.polygon([(304, 0), (336, 0), (344, 274), (296, 274)],
               fill=(BEAM[0], BEAM[1], BEAM[2], a2))


def draw_floor_glow(od, t):
    flicker = 0.90 + 0.08 * math.sin(t * 2.6) + 0.03 * math.sin(t * 7.3)
    a = int(50 * flicker)
    od.ellipse([232, 274, 408, 360], fill=(BEAM[0], BEAM[1], BEAM[2], a))
    od.ellipse([200, 284, 440, 360], fill=(BEAM[0], BEAM[1], BEAM[2], int(a * 0.6)))


def draw_scanlines(od, t):
    rnd = random.Random(int(t * 24))
    for y in range(180, 275, 4):
        off = rnd.randint(0, 2)
        od.line([(285 + off, y), (355, y)], fill=(HOLO_MID[0], HOLO_MID[1], HOLO_MID[2], 24))


def draw_data_dots(od, t):
    rnd = random.Random(int(t * 30))
    for _ in range(12):
        x = rnd.randint(278, 362)
        y = rnd.randint(175, 275)
        r = rnd.choice([1, 1, 2])
        od.ellipse([x - r, y - r, x + r, y + r],
                   fill=(HOLO_HI[0], HOLO_HI[1], HOLO_HI[2], 150))


def draw_audience(d, t):
    """哀悼人群（远景小剪影，比例正确：主角 92 像素 vs 人群 10 像素）"""
    rows = [(292, 0.8, 24), (308, 0.7, 22), (324, 0.6, 20)]
    for ri, (yy, s, n) in enumerate(rows):
        for i in range(n):
            x = 46 + i * 26 + (ri * 9) % 13
            r = 5 * s
            w = 11 * s
            h = 7 * s
            d.ellipse([x - r, yy - r * 2, x + r, yy], fill=CROWD)
            d.rectangle([x - w, yy, x + w, yy + h], fill=CROWD)


def draw_dust(d, t):
    rnd = random.Random(7)
    for i in range(30):
        px = (i * 53 + 11) % W
        py = (360 - ((t * 12 + i * 37) % 360))
        k = 0.5 + 0.5 * math.sin(t * 2 + i)
        d.point((px, int(py)), fill=fc(DUST, 0.25 * k))


def draw_subtitle(d, font, t):
    text = ""
    for st, tx in SUBS:
        if t >= st:
            text = tx
    if text:
        d.text((W // 2, 340), text, font=font, fill=(255, 255, 255),
               stroke_width=2, stroke_fill=(0, 0, 0), anchor="mm")


def fade_io(img, t):
    k = 1.0
    if t < 1.6:
        k = t / 1.6
    elif t > DUR - 1.5:
        k = max(0.0, (DUR - t) / 1.5)
    if k >= 1.0:
        return img
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.blend(black, img, k)


def render_frame(t, font):
    base = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(base)
    draw_background(d)
    draw_dome(d)
    draw_columns(d)
    draw_audience(d, t)
    draw_pedestal(d)
    holo = draw_hologram_layer(t)
    base = Image.alpha_composite(base, holo)
    d = ImageDraw.Draw(base)  # alpha_composite 会新建 Image，须重建 ImageDraw
    draw_dust(d, t)
    draw_subtitle(d, font, t)

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    draw_beams(od, t)
    draw_glow(od, t)
    draw_floor_glow(od, t)
    draw_scanlines(od, t)
    draw_data_dots(od, t)

    final = Image.alpha_composite(base, ov).convert("RGB")
    return fade_io(final, t)


def main():
    os.makedirs(OUT, exist_ok=True)
    font = ImageFont.truetype(FONT_PATH, 24)
    print(f"canvas {W}x{H} SCALE={SCALE} DUR={DUR} FPS={FPS} frames={FRAMES}")
    for fi in range(FRAMES):
        t = fi / FPS
        frame = render_frame(t, font)
        big = frame.resize((W * SCALE, H * SCALE), Image.NEAREST)
        big.save(f"{OUT}/f{fi:05d}.png")
        if fi % 60 == 0:
            print(f"frame {fi}/{FRAMES} (t={t:.2f}s)")
    print(f"DONE: {FRAMES} frames -> {OUT}")


if __name__ == "__main__":
    main()
