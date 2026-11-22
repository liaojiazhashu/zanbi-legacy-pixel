# -*- coding: utf-8 -*-
"""《赞比的遗产》8 角色像素立绘 v6 —— 高清像素级（192×320，头部 48px 宽）。

相比 v5（96×160）的提升：
- 分辨率翻倍，细节密度 ×4（面积）；
- 头部：眼睑/虹膜/瞳孔/高光/鼻梁/鼻翼/唇形/耳廓，解剖级五官；
- 身体：肩/胸/腰/髋四段立体躯干 + 上臂/肘/前臂/手 + 大腿/膝/小腿 + 鞋型；
- 衣物：翻领/领带/纽扣/褶皱线/袖口/裤缝/鞋带；
- 明暗：5 层色阶 + 分区体积明暗（不再单色斜向）。
"""
from pixel_engine import Canvas, upscale
import math

OUT = (40, 34, 32)
SKIN = [(242, 204, 172), (220, 180, 148), (190, 150, 118), (156, 116, 90), (120, 86, 64)]
SKIN_PALE = [(248, 214, 190), (232, 192, 168), (206, 166, 140), (172, 132, 108), (134, 100, 80)]
WHITE = [(248, 248, 252), (228, 228, 236), (198, 198, 208), (158, 158, 168), (118, 118, 128)]
BROWN = [(150, 108, 66), (118, 82, 50), (86, 58, 34), (60, 40, 24), (40, 26, 16)]
DARK_BROWN = [(110, 78, 50), (86, 60, 38), (62, 42, 26), (44, 30, 18), (30, 20, 12)]
ORANGE = [(250, 176, 96), (226, 148, 72), (188, 116, 52), (148, 86, 38), (108, 60, 26)]
EYE_BLUE = (64, 108, 150); EYE_BROWN = (110, 76, 48); EYE_P = (28, 36, 52); EYE_W = (255, 255, 255)
NAVY = [(104, 126, 162), (76, 94, 128), (52, 66, 96), (34, 44, 66), (22, 28, 42)]
GREY = [(150, 158, 172), (118, 126, 140), (86, 92, 104), (58, 62, 72), (38, 42, 50)]
BLACK = [(110, 112, 120), (82, 84, 92), (56, 58, 64), (36, 38, 42), (24, 26, 30)]
SHIRT = [(252, 252, 252), (228, 228, 232), (204, 204, 210), (168, 168, 176), (132, 132, 140)]
RED = [(200, 86, 96), (152, 54, 60), (108, 36, 42), (80, 26, 32), (56, 18, 22)]
BLUE_TIE = [(96, 150, 210), (64, 112, 168), (42, 80, 128), (28, 56, 92), (18, 36, 60)]
GOLD = [(252, 216, 132), (212, 174, 92), (160, 124, 62), (120, 92, 46), (84, 62, 30)]
PANTS = [(64, 74, 94), (46, 54, 70), (30, 36, 48), (20, 24, 32), (14, 16, 22)]
PANTS_BLACK = [(60, 62, 68), (44, 46, 50), (30, 32, 36), (20, 22, 24), (13, 15, 16)]
SHOE = [(56, 46, 42), (42, 34, 30), (30, 24, 22), (22, 18, 16), (15, 12, 10)]
RAG = [(190, 148, 100), (158, 120, 78), (122, 90, 56), (90, 64, 40), (62, 44, 28)]
WOOD = [(188, 138, 86), (150, 106, 62), (112, 76, 44), (80, 52, 30), (54, 34, 20)]
METAL = [(150, 158, 170), (118, 126, 140), (86, 94, 108), (56, 62, 72), (38, 42, 50)]
ICE = [(200, 240, 252), (120, 210, 238), (70, 170, 208), (40, 120, 160), (26, 84, 116)]
GIRL = [(248, 170, 190), (224, 140, 164), (190, 108, 134), (150, 78, 102), (108, 52, 72)]
GREEN_SUIT = [(96, 132, 110), (72, 104, 84), (50, 76, 60), (32, 52, 40), (20, 34, 26)]
APRON = [(252, 250, 248), (232, 228, 226), (204, 198, 196), (160, 154, 152), (118, 112, 110)]


def point_in_poly(px, py, pts):
    n = len(pts); inside = False; j = n - 1
    for i in range(n):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def shade_poly(cv, pts, pal, outline=None):
    """5 层色阶体积明暗 + dithering 抖动过渡（消除生硬色带）。"""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    tmin = min(x + y for x, y in pts); tmax = max(x + y for x, y in pts)
    trange = max(1, tmax - tmin)
    n = len(pal)
    if n >= 5:
        th = (0.22, 0.45, 0.68, 0.86)
    elif n == 4:
        th = (0.30, 0.55, 0.78)
    elif n == 3:
        th = (0.40, 0.72)
    elif n == 2:
        th = (0.55,)
    else:
        th = ()
    band = 0.018
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not point_in_poly(x, y, pts):
                continue
            f = (x + y - tmin) / trange
            c = pal[0]
            for k, t in enumerate(th):
                if f >= t:
                    c = pal[k + 1]
                else:
                    break
            # dithering：在色阶阈值附近棋盘格抖动，柔化边界
            for k, t in enumerate(th):
                if abs(f - t) < band:
                    c = pal[k] if ((x + y) & 1) == 0 else pal[k + 1]
                    break
            cv.set(x, y, c)
    if outline:
        m = len(pts)
        for i in range(m):
            cv.line(pts[i][0], pts[i][1], pts[(i + 1) % m][0], pts[(i + 1) % m][1], outline)


def poly(cv, pts, pal, outline=OUT):
    shade_poly(cv, pts, pal, outline)


# ================= 精细头部（解剖级五官） =================
def head_base(cv, skin_pal, eye_col, mouth="smile", wrinkles=False, cx=96, cy=28):
    # 头轮廓（有机：额/颧/下颌角/下巴，24 顶点）
    head = [
        (cx, cy - 24), (cx - 8, cy - 23), (cx - 15, cy - 20), (cx - 21, cy - 15),
        (cx - 25, cy - 9), (cx - 27, cy - 2), (cx - 26, cy + 4),
        (cx - 24, cy + 10), (cx - 20, cy + 15), (cx - 15, cy + 19),
        (cx - 9, cy + 22), (cx - 3, cy + 24), (cx + 3, cy + 24), (cx + 9, cy + 22),
        (cx + 15, cy + 19), (cx + 20, cy + 15), (cx + 24, cy + 10),
        (cx + 26, cy + 4), (cx + 27, cy - 2), (cx + 25, cy - 9),
        (cx + 21, cy - 15), (cx + 15, cy - 20), (cx + 8, cy - 23),
    ]
    poly(cv, head, skin_pal)
    # 额头高光（左上方，球形光照）
    cv.set(cx - 12, cy - 18, skin_pal[0]); cv.set(cx - 10, cy - 19, skin_pal[0])
    cv.set(cx - 8, cy - 20, skin_pal[0]); cv.set(cx - 5, cy - 20, skin_pal[0])
    # 眉毛（外高内低，弧线，下移至眼上 5px）
    cv.line(cx - 10, cy - 6, cx - 3, cy - 7, skin_pal[3])
    cv.line(cx - 2, cy - 7, cx - 5, cy - 6, skin_pal[3])
    cv.line(cx + 3, cy - 7, cx + 10, cy - 6, skin_pal[3])
    cv.line(cx + 2, cy - 7, cx + 5, cy - 6, skin_pal[3])
    # 眼睛（眼睑/眼白/虹膜/瞳孔/高光，加大：眼白 4px 高、虹膜 9px 宽）
    for ex in (cx - 9, cx + 9):
        # 上眼睑（双层粗线，13px 宽）
        cv.line(ex - 6, cy - 3, ex + 6, cy - 3, OUT)
        cv.line(ex - 6, cy - 2, ex + 6, cy - 2, OUT)
        # 眼白（11px 宽，4px 高）
        for xx in range(ex - 5, ex + 6):
            cv.set(xx, cy - 1, EYE_W); cv.set(xx, cy, EYE_W); cv.set(xx, cy + 1, EYE_W); cv.set(xx, cy + 2, EYE_W)
        # 虹膜（竖椭圆，9px 宽）
        for xx in range(ex - 4, ex + 5):
            cv.set(xx, cy, eye_col)
        for xx in range(ex - 3, ex + 4):
            cv.set(xx, cy + 1, eye_col)
        cv.set(ex - 1, cy + 2, eye_col); cv.set(ex, cy + 2, eye_col); cv.set(ex + 1, cy + 2, eye_col)
        # 瞳孔（2px）
        cv.set(ex, cy, EYE_P); cv.set(ex, cy + 1, EYE_P)
        # 高光（左上，2px）
        cv.set(ex - 2, cy - 1, EYE_W); cv.set(ex - 1, cy - 1, EYE_W)
        # 下眼睑
        for xx in range(ex - 4, ex + 5):
            cv.set(xx, cy + 3, skin_pal[2])
    # 鼻子（鼻梁阴影 + 鼻头 + 鼻翼 + 鼻孔，下移至 cy+10）
    cv.line(cx - 1, cy + 3, cx - 1, cy + 8, skin_pal[2])
    cv.line(cx, cy + 3, cx, cy + 9, skin_pal[1])
    cv.line(cx + 1, cy + 3, cx + 1, cy + 8, skin_pal[2])
    cv.set(cx - 1, cy + 10, skin_pal[2]); cv.set(cx, cy + 10, skin_pal[1]); cv.set(cx + 1, cy + 10, skin_pal[1])
    cv.set(cx - 2, cy + 9, skin_pal[2]); cv.set(cx + 2, cy + 9, skin_pal[2])
    cv.set(cx - 2, cy + 10, skin_pal[3]); cv.set(cx + 2, cy + 10, skin_pal[3])
    # 嘴（唇形，下移至 cy+14..cy+16）
    cv.line(cx - 4, cy + 15, cx + 4, cy + 15, skin_pal[4])
    for xx in range(cx - 3, cx + 4):
        cv.set(xx, cy + 14, skin_pal[2])
    for xx in range(cx - 3, cx + 4):
        cv.set(xx, cy + 16, skin_pal[2])
    cv.set(cx - 3, cy + 14, skin_pal[3]); cv.set(cx + 3, cy + 14, skin_pal[3])
    cv.set(cx - 3, cy + 16, skin_pal[3]); cv.set(cx + 3, cy + 16, skin_pal[3])
    # 耳朵（两侧）
    for ex in (cx - 23, cx + 23):
        cv.line(ex, cy - 3, ex, cy + 7, skin_pal[2])
        cv.line(ex - 1, cy - 2, ex - 1, cy + 6, skin_pal[2])
        cv.set(ex, cy + 2, skin_pal[3]); cv.set(ex, cy + 3, skin_pal[3])
        cv.set(ex - 1, cy + 3, skin_pal[3])
    # 皱纹
    if wrinkles:
        cv.line(cx - 8, cy - 13, cx + 8, cy - 13, skin_pal[2])
        cv.line(cx - 6, cy - 11, cx + 6, cy - 11, skin_pal[2])
        cv.line(cx - 5, cy + 5, cx - 3, cy + 10, skin_pal[2])
        cv.line(cx + 5, cy + 5, cx + 3, cy + 10, skin_pal[2])
        cv.set(cx - 12, cy - 1, skin_pal[2]); cv.set(cx + 12, cy - 1, skin_pal[2])
    # 脖子 + 下颌阴影（加粗，接近真实头颈比例）
    neck = [(cx - 10, cy + 24), (cx - 10, cy + 33), (cx + 10, cy + 33), (cx + 10, cy + 24)]
    poly(cv, neck, skin_pal, outline=None)
    cv.line(cx - 8, cy + 24, cx + 8, cy + 24, skin_pal[2])
    cv.line(cx - 8, cy + 25, cx + 8, cy + 25, skin_pal[2])
    cv.line(cx - 9, cy + 30, cx + 9, cy + 30, skin_pal[2])


# ================= 精细身体（四段躯干 + 分段四肢） =================
def draw_suit_body(cv, suit_pal, pants_pal, shirt_pal, tie_pal, skin_pal,
                   tie_style="full", chain=False, leg_shorten=0, cx=96):
    ls = leg_shorten
    # 西装上衣躯干（肩/胸/腰/衣摆四段，肩宽 1.4 头宽符合真实比例）
    torso = [
        (cx, 61),
        (cx - 10, 63), (cx - 22, 68), (cx - 32, 74), (cx - 38, 82),
        (cx - 38, 94), (cx - 34, 106), (cx - 28, 118),
        (cx - 24, 132), (cx - 22, 148), (cx - 24, 160),
        (cx + 24, 160),
        (cx + 22, 148), (cx + 24, 132), (cx + 28, 118),
        (cx + 34, 106), (cx + 38, 94), (cx + 38, 82),
        (cx + 32, 74), (cx + 22, 68), (cx + 10, 63),
    ]
    poly(cv, torso, suit_pal)
    # 衬衫 V 领区（西装内）
    shirt_v = [(cx - 10, 62), (cx, 80), (cx + 10, 62)]
    poly(cv, shirt_v, shirt_pal, outline=None)
    # 领带（从 V 领垂下）
    if tie_style == "full":
        poly(cv, [(cx - 4, 64), (cx + 4, 64), (cx + 4, 80), (cx, 96), (cx - 4, 80)], tie_pal, outline=None)
        cv.set(cx - 1, 64, tie_pal[0]); cv.set(cx, 64, tie_pal[0]); cv.set(cx + 1, 64, tie_pal[0])
        cv.set(cx, 96, tie_pal[2])
    elif tie_style == "bow":
        cv.set(cx - 4, 68, tie_pal[0]); cv.set(cx - 3, 68, tie_pal[1]); cv.set(cx + 3, 68, tie_pal[0]); cv.set(cx + 4, 68, tie_pal[1])
        cv.set(cx - 4, 69, tie_pal[1]); cv.set(cx - 3, 69, tie_pal[2]); cv.set(cx + 3, 69, tie_pal[1]); cv.set(cx + 4, 69, tie_pal[2])
        cv.set(cx, 68, tie_pal[2]); cv.set(cx, 69, tie_pal[2])
    # 翻领（西装暗色 V 形外缘，配合加宽肩）
    poly(cv, [(cx - 12, 63), (cx - 5, 72), (cx - 3, 86), (cx - 16, 80)], suit_pal[3:], outline=None)
    poly(cv, [(cx + 12, 63), (cx + 5, 72), (cx + 3, 86), (cx + 16, 80)], suit_pal[3:], outline=None)
    # 前襟纽扣（三粒金色）
    cv.set(cx, 104, GOLD[1]); cv.set(cx, 120, GOLD[1]); cv.set(cx, 136, GOLD[1])
    # 金链（怀表链，从扣眼到口袋）
    if chain:
        cv.line(cx + 6, 104, cx + 12, 116, GOLD[1])
        cv.line(cx + 12, 116, cx + 14, 112, GOLD[1])
        cv.set(cx + 12, 116, GOLD[0])
    # 左臂（上臂/肘/前臂/袖口/手，加粗至真实比例）
    poly(cv, [(cx - 34, 78), (cx - 44, 88), (cx - 44, 106), (cx - 38, 112), (cx - 26, 100), (cx - 24, 80)], suit_pal)
    cv.line(cx - 44, 108, cx - 38, 112, suit_pal[3])
    poly(cv, [(cx - 44, 112), (cx - 47, 130), (cx - 43, 146), (cx - 33, 146), (cx - 35, 128), (cx - 35, 112)], suit_pal)
    cv.line(cx - 43, 146, cx - 33, 146, suit_pal[3])
    poly(cv, [(cx - 45, 146), (cx - 36, 146), (cx - 36, 156), (cx - 45, 156)], skin_pal, outline=OUT)
    cv.line(cx - 45, 146, cx - 36, 146, suit_pal[3])
    cv.set(cx - 42, 150, skin_pal[2]); cv.set(cx - 40, 150, skin_pal[2])
    # 右臂
    poly(cv, [(cx + 34, 78), (cx + 44, 88), (cx + 44, 106), (cx + 38, 112), (cx + 26, 100), (cx + 24, 80)], suit_pal)
    cv.line(cx + 44, 108, cx + 38, 112, suit_pal[3])
    poly(cv, [(cx + 44, 112), (cx + 47, 130), (cx + 43, 146), (cx + 33, 146), (cx + 35, 128), (cx + 35, 112)], suit_pal)
    cv.line(cx + 43, 146, cx + 33, 146, suit_pal[3])
    poly(cv, [(cx + 45, 146), (cx + 36, 146), (cx + 36, 156), (cx + 45, 156)], skin_pal, outline=OUT)
    cv.line(cx + 45, 146, cx + 36, 146, suit_pal[3])
    cv.set(cx + 42, 150, skin_pal[2]); cv.set(cx + 40, 150, skin_pal[2])
    # 左腿（大腿/膝/小腿/裤缝/鞋，加宽）
    thigh_l = [(cx - 22, 160), (cx - 26, 190), (cx - 22, 220 - ls), (cx - 16, 226 - ls), (cx - 6, 226 - ls), (cx - 4, 220 - ls), (cx - 4, 190), (cx - 4, 160)]
    poly(cv, thigh_l, pants_pal)
    cv.line(cx - 14, 224 - ls, cx - 6, 224 - ls, pants_pal[3])
    poly(cv, [(cx - 18, 226 - ls), (cx - 20, 256 - ls), (cx - 14, 280 - ls), (cx - 4, 280 - ls), (cx - 4, 256 - ls), (cx - 6, 226 - ls)], pants_pal)
    cv.line(cx - 12, 160, cx - 12, 280 - ls, pants_pal[3])
    poly(cv, [(cx - 18, 280 - ls), (cx - 20, 290 - ls), (cx - 2, 292 - ls), (cx + 2, 288 - ls), (cx - 4, 280 - ls)], SHOE)
    # 右腿
    thigh_r = [(cx + 4, 160), (cx + 4, 190), (cx + 6, 220 - ls), (cx + 10, 226 - ls), (cx + 20, 226 - ls), (cx + 24, 220 - ls), (cx + 26, 190), (cx + 22, 160)]
    poly(cv, thigh_r, pants_pal)
    cv.line(cx + 6, 224 - ls, cx + 16, 224 - ls, pants_pal[3])
    poly(cv, [(cx + 18, 226 - ls), (cx + 20, 256 - ls), (cx + 14, 280 - ls), (cx + 4, 280 - ls), (cx + 4, 256 - ls), (cx + 6, 226 - ls)], pants_pal)
    cv.line(cx + 12, 160, cx + 12, 280 - ls, pants_pal[3])
    poly(cv, [(cx + 4, 280 - ls), (cx + 2, 290 - ls), (cx + 18, 292 - ls), (cx + 16, 288 - ls), (cx + 12, 280 - ls)], SHOE)


# ================= 发型（7 种） =================
def _hair_top(cv, hair_pal, cx=96, cy=28, bangs="center", back_len=0):
    """头顶发块（覆盖到发际线 y16，不遮眉/眼/鼻）。"""
    top = [
        (cx - 24, cy - 12), (cx - 21, cy - 20), (cx - 13, cy - 23), (cx - 4, cy - 24),
        (cx + 4, cy - 24), (cx + 13, cy - 23), (cx + 21, cy - 20), (cx + 24, cy - 12),
    ]
    if bangs == "center":
        top += [(cx + 18, cy - 11), (cx + 10, cy - 12), (cx + 2, cy - 11), (cx - 6, cy - 12), (cx - 14, cy - 11), (cx - 18, cy - 11)]
    elif bangs == "part":
        top += [(cx + 18, cy - 11), (cx + 10, cy - 12), (cx + 2, cy - 11), (cx - 2, cy - 13), (cx - 8, cy - 12), (cx - 18, cy - 11)]
    poly(cv, top, hair_pal)
    # 头顶高光（左上方球形光照）
    cv.line(cx - 12, cy - 20, cx - 4, cy - 20, hair_pal[0])
    cv.line(cx - 10, cy - 19, cx - 6, cy - 19, hair_pal[0])
    # 发丝纹理
    cv.line(cx - 9, cy - 16, cx - 5, cy - 14, hair_pal[3])
    cv.line(cx + 5, cy - 16, cx + 9, cy - 14, hair_pal[3])
    cv.line(cx - 1, cy - 21, cx + 2, cy - 21, hair_pal[3])


def hair_short(cv, hair_pal, cx=96, cy=28):
    _hair_top(cv, hair_pal, cx, cy, bangs="center")
    # 两侧鬓角（到耳上）
    poly(cv, [(cx - 25, cy - 8), (cx - 24, cy - 2), (cx - 21, cy - 1), (cx - 21, cy - 8)], hair_pal, outline=None)
    poly(cv, [(cx + 25, cy - 8), (cx + 24, cy - 2), (cx + 21, cy - 1), (cx + 21, cy - 8)], hair_pal, outline=None)


def hair_part(cv, hair_pal, cx=96, cy=28):
    _hair_top(cv, hair_pal, cx, cy, bangs="part")
    # 三七分缝
    cv.line(cx, cy - 23, cx + 4, cy - 11, hair_pal[3])
    # 两侧鬓角
    poly(cv, [(cx - 25, cy - 8), (cx - 24, cy - 2), (cx - 21, cy - 1), (cx - 21, cy - 8)], hair_pal, outline=None)
    poly(cv, [(cx + 25, cy - 8), (cx + 24, cy - 2), (cx + 21, cy - 1), (cx + 21, cy - 8)], hair_pal, outline=None)


def hair_messy(cv, hair_pal, cx=96, cy=28):
    _hair_top(cv, hair_pal, cx, cy, bangs="center")
    # 乱发发簇（几撮翘起）
    cv.line(cx - 14, cy - 22, cx - 16, cy - 25, hair_pal[1])
    cv.set(cx - 16, cy - 26, hair_pal[0]); cv.set(cx - 15, cy - 25, hair_pal[0])
    cv.line(cx + 8, cy - 23, cx + 10, cy - 26, hair_pal[1])
    cv.set(cx + 10, cy - 27, hair_pal[0]); cv.set(cx + 11, cy - 26, hair_pal[0])
    cv.line(cx - 4, cy - 24, cx - 5, cy - 27, hair_pal[1])
    cv.set(cx - 5, cy - 28, hair_pal[0])
    # 两侧乱发
    cv.line(cx - 25, cy - 6, cx - 23, cy - 1, hair_pal[1])
    cv.line(cx + 25, cy - 6, cx + 23, cy - 1, hair_pal[1])


def hair_slickback(cv, hair_pal, cx=96, cy=28):
    # 大背头：发际线更高（y18），向后梳，露更多额头
    top = [
        (cx - 24, cy - 12), (cx - 21, cy - 20), (cx - 13, cy - 23), (cx - 4, cy - 24),
        (cx + 4, cy - 24), (cx + 13, cy - 23), (cx + 21, cy - 20), (cx + 24, cy - 12),
        (cx + 20, cy - 10), (cx + 12, cy - 12), (cx + 4, cy - 11), (cx - 6, cy - 12), (cx - 16, cy - 10),
    ]
    poly(cv, top, hair_pal)
    # 向后梳的纹理线（横向）
    cv.line(cx - 14, cy - 18, cx - 2, cy - 19, hair_pal[2])
    cv.line(cx + 2, cy - 19, cx + 14, cy - 18, hair_pal[2])
    cv.line(cx - 12, cy - 15, cx - 4, cy - 16, hair_pal[3])
    cv.line(cx + 4, cy - 16, cx + 12, cy - 15, hair_pal[3])
    cv.line(cx - 12, cy - 20, cx - 4, cy - 20, hair_pal[0])


def hair_bald(cv, hair_pal, cx=96, cy=28):
    # 地中海秃（正面）：两侧头发从头顶到耳上，头顶中央+额头露肤色
    left = [
        (cx - 13, cy - 22), (cx - 19, cy - 20), (cx - 23, cy - 13),
        (cx - 25, cy - 5), (cx - 24, cy + 1), (cx - 21, cy + 6),
        (cx - 17, cy + 8), (cx - 14, cy + 2), (cx - 15, cy - 6),
        (cx - 16, cy - 14),
    ]
    poly(cv, left, hair_pal, outline=None)
    right = [
        (cx + 13, cy - 22), (cx + 19, cy - 20), (cx + 23, cy - 13),
        (cx + 25, cy - 5), (cx + 24, cy + 1), (cx + 21, cy + 6),
        (cx + 17, cy + 8), (cx + 14, cy + 2), (cx + 15, cy - 6),
        (cx + 16, cy - 14),
    ]
    poly(cv, right, hair_pal, outline=None)
    # 发丝纹理
    cv.line(cx - 20, cy - 12, cx - 17, cy - 6, hair_pal[3])
    cv.line(cx + 20, cy - 12, cx + 17, cy - 6, hair_pal[3])
    cv.line(cx - 19, cy - 1, cx - 16, cy + 3, hair_pal[3])
    cv.line(cx + 19, cy - 1, cx + 16, cy + 3, hair_pal[3])
    cv.line(cx - 22, cy - 18, cx - 19, cy - 16, hair_pal[0])


def hair_sideponytail(cv, hair_pal, cx=96, cy=28):
    _hair_top(cv, hair_pal, cx, cy, bangs="center")
    # 侧马尾（右侧，垂到肩）
    tail = [(cx + 22, cy - 10), (cx + 28, cy - 6), (cx + 30, cy + 2), (cx + 30, cy + 12), (cx + 30, cy + 22), (cx + 32, cy + 28), (cx + 28, cy + 30), (cx + 25, cy + 26), (cx + 26, cy + 16), (cx + 26, cy + 6), (cx + 24, cy - 4)]
    poly(cv, tail, hair_pal, outline=None)
    # 马尾发丝 + 发圈
    cv.line(cx + 29, cy + 4, cx + 28, cy + 14, hair_pal[3])
    cv.line(cx + 29, cy + 16, cx + 28, cy + 24, hair_pal[3])
    poly(cv, [(cx + 22, cy - 8), (cx + 25, cy - 6), (cx + 25, cy - 4), (cx + 22, cy - 6)], GIRL, outline=None)


def hair_twintail(cv, hair_pal, cx=96, cy=28):
    _hair_top(cv, hair_pal, cx, cy, bangs="center")
    # 双马尾（左右两侧，垂到肩）
    for sgn in (-1, 1):
        tail = [(cx + sgn * 22, cy - 10), (cx + sgn * 28, cy - 6), (cx + sgn * 30, cy + 2), (cx + sgn * 30, cy + 14), (cx + sgn * 31, cy + 24), (cx + sgn * 28, cy + 28), (cx + sgn * 25, cy + 24), (cx + sgn * 26, cy + 12), (cx + sgn * 25, cy - 2)]
        poly(cv, tail, hair_pal, outline=None)
        cv.line(cx + sgn * 29, cy + 4, cx + sgn * 28, cy + 14, hair_pal[3])
        poly(cv, [(cx + sgn * 22, cy - 8), (cx + sgn * 25, cy - 6), (cx + sgn * 25, cy - 4), (cx + sgn * 22, cy - 6)], GIRL, outline=None)


# ================= 8 角色（正面） =================
BG = (24, 26, 34)


def elder(cv):
    head_base(cv, SKIN_PALE, EYE_BROWN, wrinkles=True)
    hair_bald(cv, WHITE)
    draw_suit_body(cv, NAVY, PANTS_BLACK, SHIRT, BLUE_TIE, SKIN_PALE, tie_style="full", chain=True, leg_shorten=14)
    return 278


def young(cv):
    head_base(cv, SKIN, EYE_BLUE, mouth="smile")
    hair_short(cv, BROWN)
    draw_suit_body(cv, GREY, PANTS, SHIRT, RED, SKIN, tie_style="full", leg_shorten=0)
    return 292


def clone(cv):
    head_base(cv, SKIN, EYE_BLUE, mouth="neutral")
    hair_part(cv, DARK_BROWN)
    draw_suit_body(cv, NAVY, PANTS, SHIRT, BLUE_TIE, SKIN, tie_style="full", leg_shorten=0)
    return 292


def richard(cv):
    head_base(cv, SKIN, EYE_BROWN, mouth="neutral")
    hair_slickback(cv, DARK_BROWN)
    # 胡子（八字胡 + 下巴短胡）
    cv.line(cx_richard() - 6, 39, cx_richard() - 2, 41, DARK_BROWN[2])
    cv.line(cx_richard() + 6, 39, cx_richard() + 2, 41, DARK_BROWN[2])
    cv.set(cx_richard() - 1, 41, DARK_BROWN[2]); cv.set(cx_richard() + 1, 41, DARK_BROWN[2])
    cv.line(cx_richard() - 4, 43, cx_richard() + 4, 43, DARK_BROWN[2])
    # 金丝眼镜（圆框 + 鼻梁 + 镜腿）
    cv.ellipse(88, 29, 6, 5, GOLD[1])
    cv.ellipse(104, 29, 6, 5, GOLD[1])
    cv.line(94, 29, 98, 29, GOLD[1])
    cv.line(82, 27, 73, 25, GOLD[1])
    cv.line(110, 27, 119, 25, GOLD[1])
    draw_suit_body(cv, GREEN_SUIT, PANTS_BLACK, SHIRT, RED, SKIN, tie_style="bow", chain=True, leg_shorten=0)
    return 292


def cx_richard():
    return 96


def boy(cv):
    head_base(cv, SKIN, EYE_BROWN, mouth="smile")
    hair_messy(cv, BROWN)
    cx = 96
    # 破旧上衣（短，RAG 色 + 补丁）
    shirt = [(cx - 24, 62), (cx - 30, 74), (cx - 30, 96), (cx - 22, 108), (cx - 14, 112), (cx + 14, 112), (cx + 22, 108), (cx + 30, 96), (cx + 30, 74), (cx + 24, 62), (cx, 60)]
    poly(cv, shirt, RAG)
    # 补丁（右肩一块浅色）
    poly(cv, [(cx + 12, 70), (cx + 22, 72), (cx + 20, 82), (cx + 10, 80)], RAG[1:], outline=None)
    cv.line(cx + 14, 74, cx + 18, 78, RAG[4])
    # 领口
    poly(cv, [(cx - 6, 60), (cx, 68), (cx + 6, 60)], RAG[3], outline=None)
    # 左臂（破袖）
    poly(cv, [(cx - 26, 74), (cx - 32, 88), (cx - 32, 106), (cx - 26, 110), (cx - 22, 94), (cx - 20, 76)], RAG)
    poly(cv, [(cx - 32, 110), (cx - 34, 126), (cx - 30, 140), (cx - 24, 140), (cx - 26, 124), (cx - 26, 110)], RAG)
    poly(cv, [(cx - 32, 140), (cx - 28, 140), (cx - 28, 148), (cx - 32, 148)], SKIN, outline=None)
    # 右臂
    poly(cv, [(cx + 26, 74), (cx + 32, 88), (cx + 32, 106), (cx + 26, 110), (cx + 22, 94), (cx + 20, 76)], RAG)
    poly(cv, [(cx + 32, 110), (cx + 34, 126), (cx + 30, 140), (cx + 24, 140), (cx + 26, 124), (cx + 26, 110)], RAG)
    poly(cv, [(cx + 32, 140), (cx + 28, 140), (cx + 28, 148), (cx + 32, 148)], SKIN, outline=None)
    # 短裤
    poly(cv, [(cx - 20, 108), (cx - 22, 140), (cx - 8, 142), (cx + 8, 142), (cx + 22, 140), (cx + 20, 108)], PANTS)
    # 左腿残端（缠满浅色绷带的截肢端，明显短于完好腿）
    poly(cv, [(cx - 16, 140), (cx - 18, 160), (cx - 13, 163), (cx - 6, 160), (cx - 5, 140)], RAG[1])
    for yy in range(144, 158, 3):
        cv.line(cx - 15, yy, cx - 7, yy, RAG[2])
    cv.line(cx - 17, 160, cx - 7, 160, RAG[4])
    cv.line(cx - 16, 162, cx - 7, 162, RAG[3])
    # 右腿完好（短裤下的小腿 + 鞋）
    poly(cv, [(cx + 4, 142), (cx + 6, 190), (cx + 8, 220), (cx + 14, 220), (cx + 16, 190), (cx + 18, 142)], SKIN)
    poly(cv, [(cx + 6, 220), (cx + 8, 246), (cx + 18, 248), (cx + 20, 242), (cx + 14, 220)], SHOE)
    # 拐杖（左手拄，杖身斜靠）
    for i in range(0, 100):
        y = 92 + i
        x = cx - 46 + i * 0.10
        cv.set(int(x), y, WOOD[1])
    cv.line(cx - 44, 92, cx - 46, 96, WOOD[2])  # 握把
    cv.set(cx - 37, 190, WOOD[2]); cv.set(cx - 38, 191, WOOD[2])  # 拐杖结
    # 拐杖底脚
    cv.line(cx - 36, 190, cx - 38, 196, WOOD[2]); cv.line(cx - 36, 190, cx - 34, 196, WOOD[2])
    return 248


def girl(cv):
    head_base(cv, SKIN, EYE_BLUE, mouth="smile")
    hair_twintail(cv, ORANGE)
    cx = 96
    # 粉裙上身（短袖连衣裙）
    dress = [(cx - 22, 62), (cx - 28, 74), (cx - 28, 100), (cx - 20, 116), (cx - 10, 122), (cx + 10, 122), (cx + 20, 116), (cx + 28, 100), (cx + 28, 74), (cx + 22, 62), (cx, 60)]
    poly(cv, dress, GIRL)
    # 领口
    poly(cv, [(cx - 6, 60), (cx, 68), (cx + 6, 60)], GIRL[3], outline=None)
    # 白围裙（胸前 + 裙前，含肩带 + 口袋 + 褶皱）
    poly(cv, [(cx - 12, 84), (cx - 14, 104), (cx - 10, 120), (cx + 10, 120), (cx + 14, 104), (cx + 12, 84)], APRON, outline=None)
    cv.line(cx - 8, 84, cx - 14, 72, APRON[2])
    cv.line(cx + 8, 84, cx + 14, 72, APRON[2])
    poly(cv, [(cx - 8, 102), (cx + 8, 102), (cx + 8, 114), (cx - 8, 114)], APRON[2], outline=None)
    cv.line(cx - 8, 108, cx + 8, 108, APRON[3])
    cv.line(cx - 8, 118, cx - 5, 120, APRON[3])
    cv.line(cx + 5, 120, cx + 8, 118, APRON[3])
    # 手臂（短袖，露上臂）
    poly(cv, [(cx - 26, 74), (cx - 30, 84), (cx - 30, 96), (cx - 24, 98), (cx - 20, 86)], GIRL)
    poly(cv, [(cx - 30, 96), (cx - 32, 112), (cx - 28, 124), (cx - 22, 124), (cx - 24, 110), (cx - 24, 98)], SKIN)
    poly(cv, [(cx - 30, 124), (cx - 26, 124), (cx - 26, 132), (cx - 30, 132)], SKIN, outline=None)
    poly(cv, [(cx + 26, 74), (cx + 30, 84), (cx + 30, 96), (cx + 24, 98), (cx + 20, 86)], GIRL)
    poly(cv, [(cx + 30, 96), (cx + 32, 112), (cx + 28, 124), (cx + 22, 124), (cx + 24, 110), (cx + 24, 98)], SKIN)
    poly(cv, [(cx + 30, 124), (cx + 26, 124), (cx + 26, 132), (cx + 30, 132)], SKIN, outline=None)
    # 右手拿信纸（向前伸，白纸 + 折痕 + 文字行）
    poly(cv, [(cx + 24, 110), (cx + 34, 108), (cx + 34, 126), (cx + 24, 128)], SHIRT, outline=SHIRT[3])
    cv.line(cx + 25, 116, cx + 33, 115, SHIRT[3])
    cv.line(cx + 26, 112, cx + 31, 112, SHIRT[3])
    cv.line(cx + 26, 120, cx + 32, 119, SHIRT[3])
    cv.line(cx + 26, 123, cx + 30, 123, SHIRT[3])
    # 腿（白袜 + 粉鞋）
    poly(cv, [(cx - 16, 122), (cx - 16, 160), (cx - 10, 160), (cx - 10, 122)], SKIN)
    poly(cv, [(cx + 6, 122), (cx + 6, 160), (cx + 12, 160), (cx + 12, 122)], SKIN)
    poly(cv, [(cx - 16, 160), (cx - 16, 210), (cx - 10, 210), (cx - 10, 160)], SHIRT, outline=None)
    poly(cv, [(cx + 6, 160), (cx + 6, 210), (cx + 12, 210), (cx + 12, 160)], SHIRT, outline=None)
    poly(cv, [(cx - 18, 210), (cx - 18, 228), (cx - 8, 230), (cx - 6, 224), (cx - 8, 210)], GIRL)
    poly(cv, [(cx + 8, 210), (cx + 8, 224), (cx + 18, 228), (cx + 20, 224), (cx + 14, 210)], GIRL)
    return 232


def mech(cv):
    cx = 96
    # 金属头（侧面椭圆 + 眼带）
    cv.ellipse_shaded(cx, 26, 22, 20, METAL)
    # 面部面板（前侧浅色）
    poly(cv, [(cx - 10, 12), (cx + 18, 14), (cx + 20, 34), (cx + 6, 36), (cx - 8, 34)], METAL[1:2], outline=None)
    # 眼带（贯穿头部的发光横条）
    cv.line(cx - 16, 26, cx + 16, 26, ICE[0])
    cv.line(cx - 16, 27, cx + 16, 27, ICE[1])
    cv.set(cx - 12, 26, ICE[0]); cv.set(cx + 8, 26, ICE[0])
    # 头顶天线
    cv.line(cx, 6, cx, 2, METAL[3])
    cv.set(cx, 1, ICE[1])
    # 脖子
    poly(cv, [(cx - 8, 42), (cx - 8, 52), (cx + 8, 52), (cx + 8, 42)], METAL)
    # 躯干（金属面板，前后厚度）
    poly(cv, [(cx - 20, 52), (cx - 26, 70), (cx - 26, 110), (cx - 20, 128), (cx - 10, 134), (cx + 10, 134), (cx + 20, 128), (cx + 26, 110), (cx + 26, 70), (cx + 20, 52)], METAL)
    # 胸部面板分层线
    cv.line(cx - 24, 80, cx + 24, 80, METAL[3])
    cv.line(cx - 22, 100, cx + 22, 100, METAL[3])
    # 核心灯（胸口圆形，冰青发光）
    cv.ellipse_shaded(cx, 88, 8, 8, ICE)
    cv.set(cx - 1, 86, ICE[0]); cv.set(cx, 86, ICE[0]); cv.set(cx + 1, 86, ICE[0])
    # 散热栅格（下腹）
    for gy in range(104, 126, 4):
        cv.line(cx - 12, gy, cx + 12, gy, METAL[4])
    # 手臂（金属，左右）
    poly(cv, [(cx - 26, 70), (cx - 34, 84), (cx - 34, 108), (cx - 28, 112), (cx - 22, 92)], METAL)
    poly(cv, [(cx - 34, 112), (cx - 36, 128), (cx - 32, 140), (cx - 26, 140), (cx - 28, 126), (cx - 28, 112)], METAL)
    cv.line(cx - 34, 114, cx - 28, 116, METAL[4])
    poly(cv, [(cx + 26, 70), (cx + 34, 84), (cx + 34, 108), (cx + 28, 112), (cx + 22, 92)], METAL)
    poly(cv, [(cx + 34, 112), (cx + 36, 128), (cx + 32, 140), (cx + 26, 140), (cx + 28, 126), (cx + 28, 112)], METAL)
    cv.line(cx + 34, 114, cx + 28, 116, METAL[4])
    # 线缆下半身（几条彩色线缆，从躯干底垂下，无腿）
    for i, col in enumerate([RED[1], BLUE_TIE[1], GOLD[1], ICE[1], GREY[1]]):
        base_x = cx - 16 + i * 8
        for y in range(134, 280):
            x = base_x + int(6 * math.sin((y - 134) * 0.06 + i * 1.2))
            cv.set(x, y, col)
    return 280


def cube(cv):
    cx = 96
    # 黑色立方体主体
    body = [(cx - 36, 80), (cx - 28, 68), (cx + 28, 68), (cx + 36, 80), (cx + 36, 132), (cx + 28, 144), (cx - 28, 144), (cx - 36, 132)]
    poly(cv, body, BLACK)
    # 顶面（浅色，立体感）
    poly(cv, [(cx - 28, 68), (cx - 20, 60), (cx + 20, 60), (cx + 28, 68), (cx + 20, 76), (cx - 20, 76)], BLACK[1:3], outline=None)
    # 正面中央冰青"屏幕"（发光区域，非格栅）
    poly(cv, [(cx - 26, 88), (cx - 20, 82), (cx + 20, 82), (cx + 26, 88), (cx + 26, 124), (cx + 20, 130), (cx - 20, 130), (cx - 26, 124)], [ICE[1]], outline=None)
    # 屏幕内稀疏数据点（暗色，在亮屏上，像代码流）
    for py, xs in [(88, [-12, 4, 16]), (96, [-18, -2, 10]), (104, [2, 18]), (112, [-8, 6, 14]), (120, [-16, 0, 12])]:
        for px in xs:
            cv.set(cx + px, py, ICE[4])
    # 冰青发光边（轮廓）
    cv.line(cx - 36, 80, cx - 28, 68, ICE[1]); cv.line(cx - 28, 68, cx + 28, 68, ICE[1])
    cv.line(cx + 28, 68, cx + 36, 80, ICE[1]); cv.line(cx + 36, 80, cx + 36, 132, ICE[1])
    cv.line(cx + 36, 132, cx + 28, 144, ICE[1]); cv.line(cx + 28, 144, cx - 28, 144, ICE[1])
    cv.line(cx - 28, 144, cx - 36, 132, ICE[1]); cv.line(cx - 36, 132, cx - 36, 80, ICE[1])
    # 底部冰青光晕（悬浮推进光）
    cv.line(cx - 26, 150, cx + 26, 150, ICE[2])
    cv.line(cx - 16, 154, cx + 16, 154, ICE[3])
    cv.line(cx - 8, 158, cx + 8, 158, ICE[4])
    return 204


# ================= 渲染 =================
ROLES = [
    ("elder", elder, "老年赞比"),
    ("young", young, "青年赞比"),
    ("clone", clone, "克隆赞比"),
    ("richard", richard, "理查德·史密斯"),
    ("boy", boy, "少年赞比"),
    ("girl", girl, "女孩"),
    ("mech", mech, "机械赞比"),
    ("cube", cube, "立方体赞比"),
]
BOTTOM_Y = 292


def align(cv, bottom_y):
    shift = BOTTOM_Y - bottom_y
    if shift > 0:
        from PIL import Image
        new = Image.new("RGB", (192, 320), BG)
        new.paste(cv.img, (0, shift))
        cv.img = new
        cv.px = new.load()


def render_one(name, draw_fn):
    cv = Canvas(192, 320, BG)
    bottom = draw_fn(cv)
    align(cv, bottom)
    return upscale(cv, 2)


def render_all():
    import os
    os.makedirs("portraits_v6", exist_ok=True)
    for name, draw_fn, label in ROLES:
        img = render_one(name, draw_fn)
        img.save(f"portraits_v6/{name}.png")
        print(f"saved {name}")
    make_sheet()


def make_sheet():
    from PIL import Image, ImageDraw, ImageFont
    imgs = [Image.open(f"portraits_v6/{n}.png") for n, _, _ in ROLES]
    w, h = imgs[0].size
    cols, rows = 4, 2
    sheet = Image.new("RGB", (cols * w, rows * h), BG)
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save("portraits_v6/all_sheet.png")
    print("sheet saved")


if __name__ == "__main__":
    render_all()
