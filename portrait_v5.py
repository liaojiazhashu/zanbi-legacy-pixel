# -*- coding: utf-8 -*-
"""《赞比的遗产》8 角色像素立绘 v5 —— 有机轮廓 + 斜向簇状明暗。

复用结构：
- head_base(): 头轮廓 + 五官（眼睛/鼻/嘴/皱纹），肤色参数化；
- draw_suit_body(): 西装身（躯干/手臂/腿/鞋），颜色参数化；
- 每个角色 = head_base + 专属头发 + 专属身体/特征。
"""
from pixel_engine import Canvas, upscale
import math

OUT = (40, 34, 32)
SKIN = [(240, 202, 170), (218, 178, 148), (188, 148, 118), (152, 114, 90)]
SKIN_PALE = [(248, 214, 190), (230, 192, 168), (204, 164, 140), (170, 132, 110)]
WHITE = [(248, 248, 252), (228, 228, 236), (198, 198, 208), (154, 154, 166)]
BROWN = [(150, 108, 66), (118, 82, 50), (86, 58, 34), (60, 40, 24)]
DARK_BROWN = [(110, 78, 50), (86, 60, 38), (62, 42, 26), (44, 30, 18)]
ORANGE = [(250, 176, 96), (226, 148, 72), (188, 116, 52), (148, 86, 38)]
EYE_BLUE = (64, 108, 150); EYE_BROWN = (110, 76, 48); EYE_P = (28, 36, 52); EYE_W = (255, 255, 255)
NAVY = [(104, 126, 162), (76, 94, 128), (52, 66, 96), (32, 42, 62)]
GREY = [(150, 158, 172), (118, 126, 140), (86, 92, 104), (58, 62, 72)]
BLACK = [(110, 112, 120), (82, 84, 92), (56, 58, 64), (36, 38, 42)]
SHIRT = [(252, 252, 252), (228, 228, 232), (204, 204, 210), (168, 168, 176)]
RED = [(200, 86, 96), (152, 54, 60), (108, 36, 42), (80, 26, 32)]
BLUE_TIE = [(96, 150, 210), (64, 112, 168), (42, 80, 128), (28, 56, 92)]
GOLD = [(252, 216, 132), (212, 174, 92), (160, 124, 62), (120, 92, 46)]
PANTS = [(64, 74, 94), (46, 54, 70), (30, 36, 48), (20, 24, 32)]
PANTS_BLACK = [(60, 62, 68), (44, 46, 50), (30, 32, 36), (20, 22, 24)]
SHOE = [(56, 46, 42), (42, 34, 30), (30, 24, 22), (22, 18, 16)]
RAG = [(190, 148, 100), (158, 120, 78), (122, 90, 56), (90, 64, 40)]
WOOD = [(188, 138, 86), (150, 106, 62), (112, 76, 44), (80, 52, 30)]
METAL = [(150, 158, 170), (118, 126, 140), (86, 94, 108), (56, 62, 72)]
ICE = [(200, 240, 252), (120, 210, 238), (70, 170, 208), (40, 120, 160)]
GIRL = [(248, 170, 190), (224, 140, 164), (190, 108, 134), (150, 78, 102)]
GREEN_SUIT = [(96, 132, 110), (72, 104, 84), (50, 76, 60), (32, 52, 40)]
APRON = [(252, 250, 248), (232, 228, 226), (204, 198, 196), (160, 154, 152)]


def point_in_poly(px, py, pts):
    n = len(pts); inside = False; j = n - 1
    for i in range(n):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def shade_poly(cv, pts, pal, outline=None):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    hi, mid, lo, dk = pal
    tmin = min(x + y for x, y in pts); tmax = max(x + y for x, y in pts)
    trange = max(1, tmax - tmin)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not point_in_poly(x, y, pts):
                continue
            f = (x + y - tmin) / trange
            c = hi if f < 0.30 else mid if f < 0.55 else lo if f < 0.78 else dk
            cv.set(x, y, c)
    if outline:
        n = len(pts)
        for i in range(n):
            cv.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0], pts[(i + 1) % n][1], outline)


def poly(cv, pts, pal, outline=OUT):
    shade_poly(cv, pts, pal, outline)


# ================= 通用头部（轮廓 + 五官） =================
def head_base(cv, skin_pal, eye_col, mouth="smile", wrinkles=False, cx=48, cy=16):
    head = [
        (cx - 2, cy - 12), (cx - 5, cy - 11), (cx - 8, cy - 8), (cx - 11, cy - 4),
        (cx - 12, cy), (cx - 11, cy + 4), (cx - 8, cy + 8), (cx - 4, cy + 12),
        (cx + 4, cy + 12), (cx + 8, cy + 8), (cx + 11, cy + 4), (cx + 12, cy),
        (cx + 11, cy - 4), (cx + 8, cy - 8), (cx + 5, cy - 11),
    ]
    poly(cv, head, skin_pal)
    # 眉毛
    cv.line(cx - 8, cy - 4, cx - 2, cy - 4, skin_pal[3])
    cv.line(cx + 2, cy - 4, cx + 8, cy - 4, skin_pal[3])
    # 眼睛
    for ex in (cx - 5, cx + 5):
        cv.line(ex - 3, cy - 2, ex + 3, cy - 2, OUT)
        cv.set(ex, cy - 1, eye_col); cv.set(ex, cy, eye_col)
        cv.set(ex - 1, cy, eye_col); cv.set(ex + 1, cy, eye_col)
        cv.set(ex, cy, EYE_P)
        cv.set(ex - 1, cy - 1, EYE_W)
        cv.set(ex - 3, cy - 1, EYE_W); cv.set(ex + 3, cy - 1, EYE_W)
    # 鼻子
    cv.line(cx, cy + 1, cx - 1, cy + 4, skin_pal[2])
    cv.set(cx, cy + 4, skin_pal[3]); cv.set(cx + 1, cy + 4, skin_pal[3])
    # 嘴
    if mouth == "smile":
        for x in range(cx - 3, cx + 3):
            cv.set(x, cy + 8, skin_pal[3])
        cv.set(cx - 3, cy + 7, skin_pal[3]); cv.set(cx + 2, cy + 7, skin_pal[3])
    elif mouth == "flat":
        cv.line(cx - 3, cy + 8, cx + 3, cy + 8, skin_pal[3])
    elif mouth == "frown":
        cv.set(cx - 3, cy + 8, skin_pal[3]); cv.set(cx + 3, cy + 8, skin_pal[3])
        cv.set(cx - 2, cy + 7, skin_pal[3]); cv.set(cx + 2, cy + 7, skin_pal[3])
    elif mouth == "sad":
        cv.set(cx - 3, cy + 8, skin_pal[3]); cv.set(cx + 3, cy + 8, skin_pal[3])
        cv.set(cx - 1, cy + 7, skin_pal[3]); cv.set(cx + 1, cy + 7, skin_pal[3])
        cv.set(cx, cy + 7, skin_pal[3])
    # 皱纹
    if wrinkles:
        cv.line(cx - 6, cy - 7, cx + 6, cy - 7, skin_pal[2])
        cv.line(cx - 5, cy - 5, cx + 5, cy - 5, skin_pal[2])
        cv.set(cx - 9, cy + 1, skin_pal[2]); cv.set(cx + 9, cy + 1, skin_pal[2])
    # 脖子
    neck = [(cx - 4, cy + 12), (cx - 4, cy + 17), (cx + 4, cy + 17), (cx + 4, cy + 12)]
    poly(cv, neck, skin_pal, outline=None)


# ================= 通用西装身 =================
def draw_suit_body(cv, suit_pal, pants_pal, shirt_pal, tie_pal, tie_style="tie", chain=None, leg_shorten=0):
    ls = leg_shorten
    leg_top = 84
    mid = 120 - ls
    leg_bot = 138 - ls
    # 躯干
    torso = [
        (44, 33), (30, 36), (29, 48), (31, 60), (33, 84), (44, 84),
        (52, 84), (63, 84), (65, 60), (67, 48), (66, 36), (52, 33),
    ]
    poly(cv, torso, suit_pal)
    # 衬衫 V 领
    poly(cv, [(44, 35), (48, 45), (52, 35)], shirt_pal, outline=None)
    # 领带 / 领结
    if tie_style == "tie":
        poly(cv, [(47, 40), (49, 40), (49, 60), (47, 60)], tie_pal)
        cv.set(48, 41, tie_pal[0]); cv.set(48, 42, tie_pal[0])
    elif tie_style == "bowtie":
        poly(cv, [(46, 38), (50, 38), (50, 40), (46, 40)], tie_pal)
        poly(cv, [(46, 40), (50, 40), (50, 42), (46, 42)], tie_pal)
        cv.set(48, 40, tie_pal[0])
    # 翻领
    poly(cv, [(44, 35), (40, 44), (47, 42)], suit_pal, outline=None)
    poly(cv, [(52, 35), (56, 44), (49, 42)], suit_pal, outline=None)
    cv.line(44, 35, 40, 44, OUT); cv.line(52, 35, 56, 44, OUT)
    # 金链
    if chain:
        for i in range(9):
            x = 40 + i * 2
            y = 47 + round(2.0 * math.sin(i * 0.6))
            cv.set(x, y, chain[0]); cv.set(x, y + 1, chain[1])
        cv.set(40, 45, chain[0]); cv.set(40, 46, chain[1])
        cv.set(56, 50, chain[1]); cv.set(56, 51, chain[2])
    # 纽扣
    for y in (50, 58, 66):
        cv.set(47, y, suit_pal[3]); cv.set(48, y, suit_pal[3])
    # 手臂
    poly(cv, [(30, 36), (25, 54), (26, 80), (30, 80), (32, 54), (33, 36)], suit_pal)
    poly(cv, [(66, 36), (71, 54), (70, 80), (66, 80), (64, 54), (63, 36)], suit_pal)
    poly(cv, [(26, 78), (30, 78), (30, 82), (26, 82)], SKIN)
    poly(cv, [(66, 78), (70, 78), (70, 82), (66, 82)], SKIN)
    # 腿（leg_shorten 缩短）
    poly(cv, [(33, leg_top), (34, mid), (35, leg_bot), (44, leg_bot), (44, mid), (42, leg_top)], pants_pal)
    poly(cv, [(54, leg_top), (55, mid), (56, leg_bot), (65, leg_bot), (65, mid), (60, leg_top)], pants_pal)
    cv.line(39, leg_top + 2, 40, leg_bot - 2, pants_pal[2])
    cv.line(60, leg_top + 2, 61, leg_bot - 2, pants_pal[2])
    # 鞋
    poly(cv, [(35, leg_bot), (35, leg_bot + 7), (45, leg_bot + 7), (45, leg_bot)], SHOE)
    poly(cv, [(56, leg_bot), (56, leg_bot + 7), (66, leg_bot + 7), (66, leg_bot)], SHOE)


# ================= 头发样式 =================
def hair_bald(cv):
    poly(cv, [(46, 4), (43, 5), (41, 5), (39, 8), (37, 12), (36, 16),
              (36, 20), (37, 23), (34, 21), (34, 17), (35, 12), (38, 7), (42, 4)], WHITE)
    poly(cv, [(50, 4), (53, 5), (55, 5), (57, 8), (59, 12), (60, 16),
              (60, 20), (59, 23), (62, 21), (62, 17), (61, 12), (58, 7), (54, 4)], WHITE)


def _hair_top(cv, pal, part=False):
    # 头顶发块：覆盖头顶到发际线（中央美人尖略低，不显"中间秃"）；不遮眉毛(y12)/眼(y14-16)
    poly(cv, [(38, 4), (34, 6), (33, 10), (34, 13), (40, 11), (44, 11),
              (48, 13), (52, 11), (56, 11), (62, 13), (63, 10), (62, 6), (57, 4)], pal)
    # 头顶高光（中央亮，头发饱满）
    cv.line(44, 5, 52, 5, pal[0])
    cv.line(46, 6, 50, 6, pal[0])
    if part:
        # 分缝（从头顶到发际线）
        cv.line(48, 4, 48, 12, pal[3])


def _hair_sides(cv, pal):
    # 左右鬓角：只在脸两侧，不遮中央 x42-54
    poly(cv, [(34, 13), (32, 17), (33, 21), (37, 23), (41, 21), (41, 16), (40, 13)], pal)
    poly(cv, [(62, 13), (64, 17), (63, 21), (59, 23), (55, 21), (55, 16), (56, 13)], pal)


def hair_short(cv, pal):
    _hair_top(cv, pal)
    _hair_sides(cv, pal)


def hair_part(cv, pal):
    _hair_top(cv, pal, part=True)
    _hair_sides(cv, pal)


def hair_messy(cv, pal):
    _hair_top(cv, pal)
    _hair_sides(cv, pal)
    for i, x in enumerate((40, 44, 50, 55, 59)):
        cv.line(x, 4 - (i % 2), x + (1 if i % 2 else -1), 1, pal[1])


def hair_sideponytail(cv, pal):
    _hair_top(cv, pal)
    _hair_sides(cv, pal)
    # 马尾（右侧垂下的发束）
    poly(cv, [(58, 6), (62, 8), (64, 14), (64, 26), (62, 32), (60, 34),
              (58, 30), (58, 18), (57, 10)], pal)


def hair_slickback(cv, pal):
    # 油头/背头：头发全部向后梳，露出整个额头，发际线后移（M 形），带油光
    poly(cv, [(38, 4), (34, 6), (33, 9), (34, 12), (40, 11), (46, 10),
              (50, 10), (56, 11), (62, 12), (63, 9), (62, 6), (57, 4)], pal)
    # 发际线后移（两鬓留白 M 形）
    poly(cv, [(34, 13), (33, 16), (36, 18), (39, 16), (40, 13)], pal)
    poly(cv, [(62, 13), (63, 16), (60, 18), (57, 16), (56, 13)], pal)
    # 油光高光
    cv.line(39, 5, 43, 5, pal[0]); cv.line(41, 7, 45, 7, pal[1])


def hair_twintail(cv, pal):
    _hair_top(cv, pal)
    _hair_sides(cv, pal)
    # 左右双马尾（垂下发束）
    poly(cv, [(36, 6), (31, 9), (30, 18), (31, 30), (33, 35), (36, 35),
              (37, 28), (37, 16), (37, 10)], pal)
    poly(cv, [(60, 6), (65, 9), (66, 18), (65, 30), (63, 35), (60, 35),
              (59, 28), (59, 16), (59, 10)], pal)


def add_mustache(cv, skin_pal, cx=48, cy=16):
    # 上唇小胡子（成熟律师感）
    cv.line(cx - 3, cy + 6, cx + 3, cy + 6, skin_pal[3])
    cv.set(cx - 2, cy + 5, skin_pal[3]); cv.set(cx + 2, cy + 5, skin_pal[3])
    cv.set(cx - 1, cy + 7, skin_pal[3]); cv.set(cx + 1, cy + 7, skin_pal[3])


def add_glasses(cv, cx=48, cy=16):
    # 金边圆框眼镜（连续椭圆框，不遮眼睛内部）
    for ex in (cx - 5, cx + 5):
        cv.ellipse(ex, cy, 6, 5, GOLD[1])
    # 鼻梁架 + 镜腿
    cv.line(cx - 3, cy, cx + 3, cy, GOLD[1])
    cv.set(cx - 12, cy - 1, GOLD[1]); cv.set(cx + 12, cy - 1, GOLD[1])


# ================= 8 角色 =================
def elder(cv):
    head_base(cv, SKIN, EYE_BLUE, "smile", wrinkles=True)
    hair_bald(cv)
    draw_suit_body(cv, NAVY, PANTS, SHIRT, RED, "tie", chain=GOLD, leg_shorten=6)


def young(cv):
    head_base(cv, SKIN, EYE_BLUE, "smile", wrinkles=False)
    hair_short(cv, BROWN)
    draw_suit_body(cv, GREY, PANTS, SHIRT, BLUE_TIE, "tie", chain=GOLD)


def clone(cv):
    head_base(cv, SKIN, EYE_BLUE, "flat", wrinkles=False)
    hair_short(cv, DARK_BROWN)
    draw_suit_body(cv, NAVY, PANTS, SHIRT, BLUE_TIE, "tie", chain=None)


def richard(cv):
    head_base(cv, SKIN, EYE_BROWN, "flat", wrinkles=False)
    hair_slickback(cv, DARK_BROWN)
    add_mustache(cv, DARK_BROWN)
    add_glasses(cv)
    draw_suit_body(cv, GREEN_SUIT, PANTS_BLACK, SHIRT, BLACK, "bowtie", chain=None)


def boy(cv):
    head_base(cv, SKIN, EYE_BROWN, "frown", wrinkles=False)
    hair_messy(cv, BROWN)
    # 破衣上身（补丁 + 破洞露肤）
    torso = [
        (44, 33), (30, 36), (29, 48), (31, 60), (33, 84), (44, 84),
        (52, 84), (63, 84), (65, 60), (67, 48), (66, 36), (52, 33),
    ]
    poly(cv, torso, RAG)
    # 补丁（左肩 + 右腰）
    poly(cv, [(32, 40), (38, 40), (38, 46), (32, 46)], [RAG[0]] * 4, outline=OUT)
    cv.line(32, 40, 38, 46, RAG[3]); cv.line(38, 40, 32, 46, RAG[3])
    poly(cv, [(58, 58), (64, 58), (64, 64), (58, 64)], [RAG[0]] * 4, outline=OUT)
    cv.line(58, 58, 64, 64, RAG[3]); cv.line(64, 58, 58, 64, RAG[3])
    # 破洞露肤（右肩）
    poly(cv, [(62, 38), (66, 38), (66, 44), (62, 44)], SKIN, outline=None)
    # 手臂（右臂正常，左臂拄拐）
    poly(cv, [(30, 36), (25, 54), (26, 80), (30, 80), (32, 54), (33, 36)], RAG)
    poly(cv, [(66, 36), (71, 54), (70, 80), (66, 80), (64, 54), (63, 36)], RAG)
    poly(cv, [(66, 78), (70, 78), (70, 82), (66, 82)], SKIN)
    # 左腿（残端，打结裤管）
    poly(cv, [(33, 84), (34, 100), (35, 106), (44, 106), (44, 100), (42, 84)], RAG)
    cv.line(34, 104, 42, 104, RAG[3])
    # 右腿（正常，少年较短）
    poly(cv, [(54, 84), (55, 106), (56, 120), (65, 120), (65, 106), (60, 84)], PANTS)
    cv.line(60, 86, 61, 118, PANTS[2])
    # 右鞋
    poly(cv, [(56, 120), (56, 127), (66, 127), (66, 120)], SHOE)
    # 木拐杖（左腋下，斜撑）
    poly(cv, [(26, 42), (30, 42), (30, 44), (26, 44)], WOOD)
    for i in range(0, 78):
        x = 28 + i * 0.18
        y = 44 + i
        cv.set(round(x), y, WOOD[1])
        cv.set(round(x) + 1, y, WOOD[2])
    # 拐杖底脚
    poly(cv, [(41, 120), (47, 120), (47, 123), (41, 123)], WOOD)
    # 胸前芯片
    poly(cv, [(45, 50), (51, 50), (51, 56), (45, 56)], ICE, outline=OUT)
    cv.set(48, 53, ICE[0])


def girl(cv):
    head_base(cv, SKIN_PALE, EYE_BLUE, "sad", wrinkles=False)
    hair_twintail(cv, ORANGE)
    # 连衣裙（A 字，裙摆底部覆盖大腿根部，与腿连贯）
    dress = [
        (44, 33), (34, 36), (33, 60), (36, 90), (38, 100),
        (58, 100), (60, 90), (63, 60), (62, 36), (52, 33),
    ]
    poly(cv, dress, GIRL)
    # 白围裙（腰部到裙摆）
    poly(cv, [(40, 42), (56, 42), (59, 88), (37, 88)], APRON, outline=None)
    cv.line(40, 42, 56, 42, APRON[2])
    # 白领
    poly(cv, [(44, 33), (48, 40), (52, 33)], SHIRT, outline=None)
    # 手臂
    poly(cv, [(34, 36), (30, 54), (31, 74), (35, 74), (36, 54), (37, 36)], GIRL)
    poly(cv, [(62, 36), (66, 54), (65, 74), (61, 74), (60, 54), (59, 36)], GIRL)
    poly(cv, [(31, 72), (35, 72), (35, 76), (31, 76)], SKIN_PALE)
    poly(cv, [(61, 72), (65, 72), (65, 76), (61, 76)], SKIN_PALE)
    # 信纸（右手拿）
    poly(cv, [(61, 64), (69, 64), (69, 76), (61, 76)], SHIRT, outline=OUT)
    cv.line(63, 67, 67, 67, SHIRT[2]); cv.line(63, 70, 67, 70, SHIRT[2])
    # 腿（小女孩短腿，从裙摆下伸出，顶部在裙摆内）
    poly(cv, [(40, 100), (41, 108), (42, 114), (47, 114), (47, 108), (45, 100)], SKIN_PALE)
    poly(cv, [(49, 100), (50, 108), (51, 114), (56, 114), (56, 108), (54, 100)], SKIN_PALE)
    # 鞋（小圆头鞋）
    poly(cv, [(41, 114), (41, 121), (47, 121), (47, 114)], GIRL)
    poly(cv, [(50, 114), (50, 121), (56, 121), (56, 114)], GIRL)
    # 泪珠
    cv.set(42, 22, ICE[0]); cv.set(42, 23, ICE[0]); cv.set(42, 24, ICE[1])


def mech(cv):
    # 金属头（非人形头，圆角方形）
    head = [(40, 4), (56, 4), (58, 8), (58, 16), (56, 22), (52, 24),
            (44, 24), (40, 22), (38, 16), (38, 8)]
    poly(cv, head, METAL)
    # 发光眼带（横贯）
    poly(cv, [(40, 12), (56, 12), (56, 16), (40, 16)], ICE, outline=None)
    cv.set(48, 14, ICE[0])
    # 脖子（金属轴）
    poly(cv, [(44, 24), (44, 30), (52, 30), (52, 24)], METAL)
    # 躯干（装甲）
    torso = [
        (44, 30), (30, 34), (28, 50), (30, 66), (33, 84), (44, 84),
        (52, 84), (63, 84), (66, 66), (68, 50), (66, 34), (52, 30),
    ]
    poly(cv, torso, METAL)
    # 装甲分层线
    cv.line(30, 48, 66, 48, METAL[2])
    cv.line(30, 49, 66, 49, METAL[0])
    cv.line(31, 62, 65, 62, METAL[2])
    # 胸口核心灯（圆形）
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            if dx * dx + dy * dy <= 16:
                cv.set(48 + dx, 56 + dy, ICE[1] if dx * dx + dy * dy < 6 else ICE[0])
    cv.set(47, 55, (255, 255, 255)); cv.set(48, 55, (255, 255, 255))
    # 手臂（机械臂）
    poly(cv, [(30, 34), (25, 52), (26, 78), (30, 78), (32, 52), (33, 34)], METAL)
    poly(cv, [(66, 34), (71, 52), (70, 78), (66, 78), (64, 52), (63, 34)], METAL)
    # 线缆下半身（彩色 5 条，替代腿）
    colors = [ICE, GOLD, RED, BLUE_TIE, GIRL]
    for i, pal in enumerate(colors):
        x0 = 34 + i * 4
        for y in range(84, 140):
            x = x0 + round(2.0 * math.sin((y - 84) * 0.08 + i * 1.2))
            cv.set(x, y, pal[1])
            cv.set(x, y + 1, pal[2])
    # 光纤束底座
    poly(cv, [(33, 82), (63, 82), (63, 86), (33, 86)], METAL)


def cube(cv):
    # 等距立方体（顶面亮/左面中/右面暗）
    top = [(48, 30), (70, 42), (48, 54), (26, 42)]
    left = [(26, 42), (48, 54), (48, 106), (26, 94)]
    right = [(48, 54), (70, 42), (70, 94), (48, 106)]
    poly(cv, top, [(120, 120, 128), (96, 96, 104), (74, 74, 80), (56, 56, 60)])
    poly(cv, left, [(92, 92, 100), (70, 70, 78), (50, 50, 56), (36, 36, 40)])
    poly(cv, right, [(60, 60, 66), (44, 44, 50), (30, 30, 34), (22, 22, 24)])
    # 冰青发光边
    for p in top:
        cv.set(p[0], p[1], ICE[0])
    cv.line(26, 42, 48, 54, ICE[0]); cv.line(48, 54, 70, 42, ICE[0])
    cv.line(48, 54, 48, 106, ICE[1])
    cv.line(26, 42, 26, 94, ICE[1]); cv.line(70, 42, 70, 94, ICE[1])
    # 内部代码行（冰青点阵）
    for i, y in enumerate(range(58, 100, 6)):
        for x in range(34, 62, 4):
            if (x + i) % 3 != 0:
                cv.set(x, y, ICE[2])
    # 底部悬浮光晕
    for x in range(30, 66):
        cv.set(x, 112, ICE[2])


# ================= 渲染 =================
ROLES = [("elder", elder), ("young", young), ("clone", clone), ("richard", richard),
         ("boy", boy), ("girl", girl), ("mech", mech), ("cube", cube)]

# 各角色脚底 y（用于底部对齐，体现身高差异）
HEIGHTS = {
    "elder": 139,    # 老年略矮（leg_shorten=6）
    "young": 145,    # 成年标准
    "clone": 145,
    "richard": 145,
    "boy": 127,      # 少年矮
    "girl": 121,     # 小女孩最矮
    "mech": 140,     # 机械线缆底
    "cube": 112,     # 立方体悬浮底
}


def shift_down(img, dy, bg=(24, 26, 30)):
    """把图像向下平移 dy 像素，顶部露出的区域填充背景色。"""
    from PIL import Image
    w, h = img.size
    out = Image.new("RGB", (w, h), bg)
    out.paste(img, (0, dy))
    return out


def render_all():
    from PIL import Image, ImageDraw
    imgs = []
    for name, fn in ROLES:
        cv = Canvas(96, 160)
        fn(cv)
        bottom = HEIGHTS.get(name, 145)
        dy = 150 - bottom  # 下沉量，使脚底统一贴 y150
        raw = cv.img
        if dy != 0:
            raw = shift_down(raw, dy)
        img = raw.resize((96 * 5, 160 * 5), Image.NEAREST)
        img.save(f"portraits/v5_{name}.png")
        imgs.append((name, img))
        print("saved", name)
    # 合集 4×2
    cell_w, cell_h = imgs[0][1].size
    sheet_pil = Image.new("RGB", (cell_w * 4, cell_h * 2), (24, 26, 30))
    draw = ImageDraw.Draw(sheet_pil)
    for i, (name, img) in enumerate(imgs):
        r, c = i // 4, i % 4
        sheet_pil.paste(img, (c * cell_w, r * cell_h))
        draw.text((c * cell_w + 8, r * cell_h + 8), name, fill=(255, 255, 255))
    sheet_pil.save("portraits/_v5_all_sheet.png")
    print("sheet saved")


if __name__ == "__main__":
    render_all()
