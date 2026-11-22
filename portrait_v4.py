# -*- coding: utf-8 -*-
"""老年赞比像素立绘 v4 —— 有机轮廓 + 斜向簇状明暗（真正像素风）。

核心改进（相对 v3 的"几何渐变"）：
- 轮廓用多点多边形（秃顶+颧骨+方下巴等解剖特征），非椭圆；
- 明暗按固定光照方向（左上 45°）分 4 层簇状色块（分界是斜线），
  非径向/对角数学渐变；
- 细节：发丝、皱纹、服装褶皱、金链、纽扣、裤缝。
"""
from pixel_engine import Canvas, upscale

# ---- 有限调色板（每材质 4 层明暗） ----
OUT = (40, 34, 32)
SKIN = [(240, 202, 170), (218, 178, 148), (188, 148, 118), (152, 114, 90)]
WHITE = [(246, 240, 232), (220, 210, 200), (180, 168, 156), (132, 122, 112)]
EYE_I = (64, 108, 150); EYE_P = (28, 36, 52); EYE_W = (255, 255, 255)
SUIT = [(104, 126, 162), (76, 94, 128), (52, 66, 96), (32, 42, 62)]
SHIRT = [(252, 252, 252), (228, 228, 232), (204, 204, 210), (168, 168, 176)]
TIE = [(200, 86, 96), (152, 54, 60), (108, 36, 42), (80, 26, 32)]
GOLD = [(252, 216, 132), (212, 174, 92), (160, 124, 62), (120, 92, 46)]
PANTS = [(64, 74, 94), (46, 54, 70), (30, 36, 48), (20, 24, 32)]
SHOE = [(56, 46, 42), (42, 34, 30), (30, 24, 22), (22, 18, 16)]


def point_in_poly(px, py, pts):
    n = len(pts)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def shade_poly(cv, pts, pal, outline=None):
    """多边形内斜向簇状明暗（光照左上 45°，t=x+y 分层）。"""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    hi, mid, lo, dk = pal
    # 光照投影范围
    tmin = min(x + y for x, y in pts)
    tmax = max(x + y for x, y in pts)
    trange = max(1, tmax - tmin)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not point_in_poly(x, y, pts):
                continue
            t = x + y
            f = (t - tmin) / trange  # 0=左上亮，1=右下暗
            if f < 0.30:
                c = hi
            elif f < 0.55:
                c = mid
            elif f < 0.78:
                c = lo
            else:
                c = dk
            cv.set(x, y, c)
    if outline:
        n = len(pts)
        for i in range(n):
            cv.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0], pts[(i + 1) % n][1], outline)


def poly(cv, pts, pal, outline=OUT):
    shade_poly(cv, pts, pal, outline)


# ================= 老年赞比（96×160，头身比 1:6） =================
def elder(cv):
    # ---- 头部（秃顶老人，有机轮廓：秃顶+颧骨+方下巴） ----
    head = [
        (46, 4), (43, 5), (40, 8), (37, 12), (36, 16), (37, 20),
        (40, 24), (44, 28), (52, 28), (56, 24), (59, 20), (60, 16),
        (59, 12), (56, 8), (53, 5),
    ]
    poly(cv, head, SKIN)

    # ---- 白发（稀疏发束簇，两侧+后脑，头顶秃） ----
    hairL = [(46, 4), (43, 5), (41, 5), (39, 8), (37, 12), (36, 16),
             (36, 20), (37, 23), (34, 21), (34, 17), (35, 12), (38, 7), (42, 4)]
    hairR = [(50, 4), (53, 5), (55, 5), (57, 8), (59, 12), (60, 16),
             (60, 20), (59, 23), (62, 21), (62, 17), (61, 12), (58, 7), (54, 4)]
    poly(cv, hairL, WHITE)
    poly(cv, hairR, WHITE)

    # ---- 五官 ----
    # 眉毛（稀疏白眉）
    cv.line(40, 12, 46, 12, WHITE[2])
    cv.line(50, 12, 56, 12, WHITE[2])
    # 眼睛（深色虹膜竖椭圆 + 瞳孔 + 高光）
    for cx in (43, 53):
        cv.line(cx - 3, 14, cx + 3, 14, OUT)  # 上眼睑
        for dy in (0, 1, 2):
            cv.set(cx, 14 + dy, EYE_I)
        cv.set(cx - 1, 15, EYE_I); cv.set(cx + 1, 15, EYE_I)
        cv.set(cx, 15, EYE_P)          # 瞳孔
        cv.set(cx - 1, 14, EYE_W)      # 高光
        cv.set(cx - 3, 15, EYE_W); cv.set(cx + 3, 15, EYE_W)  # 眼角
    # 鼻子（老年略大）
    cv.line(48, 16, 47, 20, SKIN[2])
    cv.set(48, 20, SKIN[3]); cv.set(49, 20, SKIN[3])
    # 嘴（微笑）
    for x in range(45, 51):
        cv.set(x, 24, SKIN[3])
    cv.set(45, 23, SKIN[3]); cv.set(50, 23, SKIN[3])
    # 皱纹（额头横线 + 眼角）
    cv.line(42, 9, 54, 9, SKIN[2])
    cv.line(43, 11, 53, 11, SKIN[2])
    cv.set(39, 17, SKIN[2]); cv.set(57, 17, SKIN[2])

    # ---- 脖子 ----
    neck = [(44, 28), (44, 33), (52, 33), (52, 28)]
    poly(cv, neck, SKIN)

    # ---- 躯干（西装，垫肩 + 收腰） ----
    torso = [
        (44, 33), (30, 36), (29, 48), (31, 60), (33, 84), (44, 84),
        (52, 84), (63, 84), (65, 60), (67, 48), (66, 36), (52, 33),
    ]
    poly(cv, torso, SUIT)

    # ---- 衬衫 V 领 + 领带 ----
    shirt = [(44, 35), (48, 45), (52, 35)]
    poly(cv, shirt, SHIRT, outline=None)
    tie = [(47, 40), (49, 40), (49, 60), (47, 60)]
    poly(cv, tie, TIE)
    # 领带结
    cv.set(48, 41, TIE[0]); cv.set(48, 42, TIE[0])

    # ---- 西装翻领 ----
    lapelL = [(44, 35), (40, 44), (47, 42)]
    lapelR = [(52, 35), (56, 44), (49, 42)]
    poly(cv, lapelL, SUIT, outline=None)
    poly(cv, lapelR, SUIT, outline=None)
    cv.line(44, 35, 40, 44, OUT); cv.line(52, 35, 56, 44, OUT)

    # ---- 金怀表链（纯金链节弧线，无偏红） ----
    import math
    for i in range(9):
        x = 40 + i * 2
        y = 47 + round(2.0 * math.sin(i * 0.6))
        cv.set(x, y, GOLD[0])
        cv.set(x, y + 1, GOLD[1])
    cv.set(40, 45, GOLD[0]); cv.set(40, 46, GOLD[1])
    cv.set(56, 50, GOLD[1]); cv.set(56, 51, GOLD[2])

    # ---- 纽扣（西装单排） ----
    for y in (50, 58, 66):
        cv.set(47, y, SUIT[3]); cv.set(48, y, SUIT[3])

    # ---- 手臂（下垂） ----
    armL = [(30, 36), (25, 54), (26, 80), (30, 80), (32, 54), (33, 36)]
    armR = [(66, 36), (71, 54), (70, 80), (66, 80), (64, 54), (63, 36)]
    poly(cv, armL, SUIT)
    poly(cv, armR, SUIT)
    # 手（肤色）
    poly(cv, [(26, 78), (30, 78), (30, 82), (26, 82)], SKIN)
    poly(cv, [(66, 78), (70, 78), (70, 82), (66, 82)], SKIN)

    # ---- 腿（裤） ----
    legL = [(33, 84), (34, 120), (35, 138), (44, 138), (44, 120), (42, 84)]
    legR = [(54, 84), (55, 120), (56, 138), (65, 138), (65, 120), (60, 84)]
    poly(cv, legL, PANTS)
    poly(cv, legR, PANTS)
    # 裤缝线
    cv.line(39, 86, 40, 136, PANTS[2])
    cv.line(60, 86, 61, 136, PANTS[2])

    # ---- 鞋 ----
    poly(cv, [(35, 138), (35, 145), (45, 145), (45, 138)], SHOE)
    poly(cv, [(56, 138), (56, 145), (66, 145), (66, 138)], SHOE)


if __name__ == "__main__":
    cv = Canvas(96, 160)
    elder(cv)
    upscale(cv, 5).save("portraits/elder_v4.png")
    print("elder_v4 saved:", cv.w, "x", cv.h)
