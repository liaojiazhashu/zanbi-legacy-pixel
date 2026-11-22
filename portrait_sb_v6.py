# -*- coding: utf-8 -*-
"""《赞比的遗产》8 角色像素立绘 v6 —— 侧面/背面（192×320，头部 48px 宽）。

侧面严格按现实人体侧视图：鼻尖最凸→人中内凹→下巴内收；
单腿单鞋脚尖朝右；手臂在身体前侧；领带/金链在胸前。
"""
from portrait_v6 import (Canvas, upscale, poly, shade_poly, point_in_poly, OUT,
                         SKIN, SKIN_PALE, WHITE, BROWN, DARK_BROWN, ORANGE,
                         EYE_BLUE, EYE_BROWN, EYE_P, EYE_W,
                         NAVY, GREY, BLACK, SHIRT, RED, BLUE_TIE, GOLD,
                         PANTS, PANTS_BLACK, SHOE, RAG, WOOD, METAL, ICE,
                         GIRL, GREEN_SUIT, APRON, BG, BOTTOM_Y, align, head_base)
import math


# ================= 侧面水平体积明暗（前亮后暗，体现圆柱体厚度） =================
def shade_h(cv, pts, pal, dark_left=True, outline=None):
    """水平明暗 + dithering：侧面朝右时前侧(右)受光亮、后侧(左)背光暗，体现前后厚度。"""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    xr = max(1, x1 - x0)
    n = len(pal)
    if n >= 5:
        th = (0.28, 0.46, 0.62, 0.80)
    elif n == 4:
        th = (0.32, 0.55, 0.76)
    elif n == 3:
        th = (0.40, 0.72)
    elif n == 2:
        th = (0.55,)
    else:
        th = ()
    band = 0.018
    yr = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not point_in_poly(x, y, pts):
                continue
            fx = (x - x0) / xr
            if dark_left:
                fx = 1 - fx
            fy = (y - y0) / yr
            f = 0.85 * fx + 0.15 * fy
            c = pal[0]
            for k, t in enumerate(th):
                if f >= t:
                    c = pal[k + 1]
                else:
                    break
            for k, t in enumerate(th):
                if abs(f - t) < band:
                    c = pal[k] if ((x + y) & 1) == 0 else pal[k + 1]
                    break
            cv.set(x, y, c)
    if outline:
        m = len(pts)
        for i in range(m):
            cv.line(pts[i][0], pts[i][1], pts[(i + 1) % m][0], pts[(i + 1) % m][1], outline)


def poly_h(cv, pts, pal, dark_left=True, outline=OUT):
    shade_h(cv, pts, pal, dark_left, outline)


# ================= 侧脸（正确人体侧视轮廓，朝右） =================
def head_side(cv, skin_pal, eye_col, wrinkles=False, cx=96, cy=28):
    head = [
        (cx - 15, cy - 21), (cx - 20, cy - 14), (cx - 22, cy - 5), (cx - 21, cy + 3),
        (cx - 18, cy + 11), (cx - 13, cy + 16), (cx - 6, cy + 20), (cx + 2, cy + 22),
        (cx + 7, cy + 21), (cx + 10, cy + 18), (cx + 11, cy + 14), (cx + 12, cy + 11),
        (cx + 13, cy + 9), (cx + 12, cy + 7), (cx + 13, cy + 6), (cx + 12, cy + 4),
        (cx + 13, cy + 3), (cx + 15, cy + 1), (cx + 13, cy - 2), (cx + 11, cy - 5),
        (cx + 12, cy - 8), (cx + 11, cy - 13), (cx + 8, cy - 18), (cx + 2, cy - 22),
        (cx - 7, cy - 24),
    ]
    poly(cv, head, skin_pal)
    # 额头高光
    cv.set(cx + 4, cy - 18, skin_pal[0]); cv.set(cx + 6, cy - 16, skin_pal[0])
    # 眉毛（眉骨处，朝右）
    cv.line(cx + 9, cy - 8, cx + 14, cy - 9, skin_pal[3])
    # 单眼（鼻根后方，朝右，加大更清晰）
    ex = cx + 5
    cv.line(ex - 3, cy - 3, ex + 3, cy - 3, OUT)
    cv.line(ex - 3, cy - 2, ex + 3, cy - 2, OUT)
    for xx in range(ex - 2, ex + 3):
        cv.set(xx, cy - 1, EYE_W)
    for xx in range(ex - 2, ex + 3):
        cv.set(xx, cy, eye_col)
    cv.set(ex - 1, cy + 1, eye_col); cv.set(ex, cy + 1, eye_col); cv.set(ex + 1, cy + 1, eye_col)
    cv.set(ex, cy, EYE_P)
    cv.set(ex - 2, cy - 1, EYE_W); cv.set(ex - 1, cy - 1, EYE_W)
    # 下眼睑
    for xx in range(ex - 2, ex + 3):
        cv.set(xx, cy + 2, skin_pal[2])
    # 鼻梁阴影（鼻根到鼻头）
    cv.line(cx + 13, cy - 3, cx + 14, cy + 1, skin_pal[2])
    cv.set(cx + 15, cy + 1, skin_pal[2])  # 鼻尖阴影
    # 鼻孔
    cv.set(cx + 13, cy + 4, skin_pal[3])
    # 嘴缝 + 唇
    cv.line(cx + 12, cy + 7, cx + 14, cy + 7, skin_pal[4])
    cv.set(cx + 13, cy + 6, skin_pal[2])
    cv.set(cx + 13, cy + 8, skin_pal[2]); cv.set(cx + 14, cy + 8, skin_pal[2])
    # 耳朵（眼睛正后方）
    cv.line(cx - 10, cy - 2, cx - 10, cy + 6, skin_pal[2])
    cv.line(cx - 11, cy - 1, cx - 11, cy + 5, skin_pal[2])
    cv.set(cx - 10, cy + 2, skin_pal[3]); cv.set(cx - 10, cy + 3, skin_pal[3])
    # 皱纹
    if wrinkles:
        cv.line(cx + 6, cy - 12, cx + 12, cy - 12, skin_pal[2])
        cv.line(cx + 11, cy + 4, cx + 13, cy + 8, skin_pal[2])
        cv.set(cx - 1, cy - 1, skin_pal[2]); cv.set(cx, cy - 1, skin_pal[2])
    # 脖子 + 下颌阴影
    poly(cv, [(cx - 6, cy + 20), (cx - 4, cy + 33), (cx + 8, cy + 33), (cx + 8, cy + 22)], skin_pal, outline=None)
    cv.line(cx - 4, cy + 22, cx + 8, cy + 22, skin_pal[2])


# ================= 侧面身体（单腿单鞋脚尖朝右，手臂前侧） =================
def body_side(cv, suit_pal, pants_pal, shirt_pal, tie_pal, skin_pal,
              tie_style="full", chain=False, leg_shorten=0, cx=96):
    ls = leg_shorten
    # 躯干侧面 S 形（真实比例）：后侧是 S 形主特征——
    # 肩胛凸(cx-26)→腰后内收(cx-16)→臀凸(cx-26)；前侧较平直：胸(cx+14)→腹(cx+10)→髋(cx+13)
    torso = [
        (cx + 8, 61), (cx + 12, 66), (cx + 18, 76), (cx + 16, 90),
        (cx + 12, 105), (cx + 11, 120), (cx + 15, 135), (cx + 11, 150),
        (cx + 8, 160), (cx - 4, 160), (cx - 15, 160),
        (cx - 26, 148), (cx - 30, 132), (cx - 24, 120),
        (cx - 16, 108), (cx - 18, 95), (cx - 28, 84), (cx - 30, 76),
        (cx - 20, 68), (cx - 12, 62), (cx - 6, 61),
    ]
    poly_h(cv, torso, suit_pal)
    # 衬衫领口（前侧）
    poly(cv, [(cx + 6, 62), (cx + 10, 70), (cx + 12, 64)], shirt_pal, outline=None)
    # 领带（胸前前侧窄条，沿前襟斜下）
    if tie_style == "full":
        poly(cv, [(cx + 9, 64), (cx + 11, 64), (cx + 12, 82), (cx + 10, 96), (cx + 9, 82)], tie_pal, outline=None)
        cv.set(cx + 10, 96, tie_pal[2])
    elif tie_style == "bow":
        cv.set(cx + 8, 68, tie_pal[0]); cv.set(cx + 9, 68, tie_pal[1]); cv.set(cx + 10, 68, tie_pal[2]); cv.set(cx + 11, 68, tie_pal[1]); cv.set(cx + 12, 68, tie_pal[0])
    # 翻领（前侧暗色）
    poly(cv, [(cx + 8, 64), (cx + 12, 72), (cx + 13, 82), (cx + 6, 78)], suit_pal[3:], outline=None)
    # 纽扣（前襟）
    cv.set(cx + 12, 100, GOLD[1]); cv.set(cx + 12, 118, GOLD[1])
    # 金链（胸前弧线 + 链坠）
    if chain:
        cv.line(cx + 13, 92, cx + 11, 110, GOLD[1])
        cv.set(cx + 11, 110, GOLD[0])
        cv.set(cx + 10, 112, GOLD[2])
    # 上臂（肩到肘，加粗 20px 厚）
    poly_h(cv, [(cx + 1, 72), (cx + 13, 80), (cx + 19, 94), (cx + 15, 106), (cx + 6, 106), (cx + 4, 96), (cx - 1, 78)], suit_pal)
    # 前臂（肘到腕，加粗 14px 厚）
    poly_h(cv, [(cx + 15, 106), (cx + 20, 120), (cx + 19, 138), (cx + 11, 142), (cx + 6, 138), (cx + 6, 120), (cx + 8, 110)], suit_pal)
    cv.line(cx + 16, 106, cx + 9, 108, suit_pal[3])
    # 袖口露手
    poly(cv, [(cx + 18, 142), (cx + 12, 142), (cx + 12, 152), (cx + 18, 152)], skin_pal, outline=None)
    # 大腿（侧面，后侧腘绳肌凸出，加粗 24px）
    poly_h(cv, [(cx + 11, 160), (cx + 11, 186), (cx + 10, 210), (cx + 9, 220), (cx + 7, 224), (cx + 2, 226), (cx - 6, 226), (cx - 10, 220), (cx - 12, 210), (cx - 13, 186), (cx - 11, 160)], pants_pal)
    cv.line(cx - 10, 224 - ls, cx + 7, 224 - ls, pants_pal[3])
    # 小腿（侧面，小腿肚向后凸出，加粗 21px）
    poly_h(cv, [(cx + 8, 226), (cx + 7, 244), (cx + 5, 268), (cx + 4, 278), (cx - 1, 280 - ls), (cx - 7, 278 - ls), (cx - 13, 256 - ls), (cx - 9, 234), (cx - 6, 226)], pants_pal)
    cv.line(cx + 3, 226, cx + 3, 278 - ls, pants_pal[3])
    # 鞋一只（脚尖朝右）
    poly(cv, [(cx - 8, 280 - ls), (cx - 5, 288 - ls), (cx + 19, 290 - ls), (cx + 19, 284 - ls), (cx + 2, 280 - ls)], SHOE)


# ================= 侧面发型（不遮脸） =================
def hair_side_short(cv, hair_pal, cx=96, cy=28):
    # 头顶连续发块（后脑勺到前额全覆盖，发际线 cy-11 不遮眼鼻）
    poly(cv, [
        (cx - 15, cy - 20), (cx - 20, cy - 14), (cx - 21, cy - 6), (cx - 19, cy + 2),
        (cx - 16, cy + 8), (cx - 13, cy + 10), (cx - 11, cy + 4), (cx - 12, cy - 6),
        (cx - 13, cy - 16), (cx - 10, cy - 21), (cx - 4, cy - 23), (cx + 2, cy - 24),
        (cx + 8, cy - 22), (cx + 10, cy - 18), (cx + 11, cy - 14), (cx + 9, cy - 11),
        (cx + 5, cy - 12), (cx - 2, cy - 12), (cx - 8, cy - 13),
    ], hair_pal, outline=None)
    cv.line(cx - 14, cy - 12, cx - 12, cy - 6, hair_pal[3])
    cv.line(cx - 2, cy - 20, cx + 2, cy - 20, hair_pal[0])
    cv.line(cx - 4, cy - 16, cx, cy - 15, hair_pal[3])


def hair_side_part(cv, hair_pal, cx=96, cy=28):
    hair_side_short(cv, hair_pal, cx, cy)
    cv.line(cx - 2, cy - 23, cx + 2, cy - 12, hair_pal[3])


def hair_side_messy(cv, hair_pal, cx=96, cy=28):
    hair_side_short(cv, hair_pal, cx, cy)
    cv.line(cx - 16, cy - 18, cx - 18, cy - 21, hair_pal[1])
    cv.set(cx - 18, cy - 22, hair_pal[0])
    cv.line(cx + 2, cy - 23, cx + 3, cy - 26, hair_pal[1])
    cv.set(cx + 3, cy - 27, hair_pal[0])


def hair_side_bald(cv, hair_pal, cx=96, cy=28):
    # 侧面地中海：后脑勺有发 + 前额发根，头顶中央 x-2..+4 秃
    poly(cv, [(cx - 15, cy - 20), (cx - 20, cy - 14), (cx - 21, cy - 6), (cx - 19, cy + 2), (cx - 16, cy + 8), (cx - 13, cy + 10), (cx - 11, cy + 4), (cx - 12, cy - 6), (cx - 12, cy - 16)], hair_pal, outline=None)
    poly(cv, [(cx + 6, cy - 18), (cx + 9, cy - 15), (cx + 10, cy - 12), (cx + 9, cy - 11), (cx + 5, cy - 12), (cx + 2, cy - 12)], hair_pal, outline=None)
    cv.line(cx - 14, cy - 12, cx - 12, cy - 6, hair_pal[3])
    cv.line(cx - 4, cy - 18, cx - 2, cy - 16, hair_pal[0])


def hair_side_ponytail(cv, hair_pal, cx=96, cy=28):
    hair_side_short(cv, hair_pal, cx, cy)
    # 马尾（后脑勺后方垂下）
    poly(cv, [(cx - 14, cy - 10), (cx - 20, cy - 6), (cx - 22, cy + 2), (cx - 22, cy + 14), (cx - 23, cy + 24), (cx - 20, cy + 28), (cx - 17, cy + 24), (cx - 18, cy + 12), (cx - 18, cy + 2), (cx - 16, cy - 4)], hair_pal, outline=None)
    cv.line(cx - 21, cy + 4, cx - 20, cy + 14, hair_pal[3])
    poly(cv, [(cx - 15, cy - 9), (cx - 18, cy - 7), (cx - 18, cy - 5), (cx - 15, cy - 7)], GIRL, outline=None)


def hair_side_twintail(cv, hair_pal, cx=96, cy=28):
    hair_side_short(cv, hair_pal, cx, cy)
    # 双马尾（一前一后）
    poly(cv, [(cx - 14, cy - 10), (cx - 20, cy - 6), (cx - 22, cy + 4), (cx - 22, cy + 16), (cx - 21, cy + 24), (cx - 18, cy + 26), (cx - 16, cy + 20), (cx - 17, cy + 8)], hair_pal, outline=None)
    poly(cv, [(cx + 8, cy - 14), (cx + 12, cy - 10), (cx + 13, cy - 2), (cx + 13, cy + 8), (cx + 14, cy + 14), (cx + 11, cy + 16), (cx + 9, cy + 10), (cx + 9, cy)], hair_pal, outline=None)
    cv.line(cx - 21, cy + 4, cx - 20, cy + 14, hair_pal[3])


def hair_side_slickback(cv, hair_pal, cx=96, cy=28):
    poly(cv, [(cx - 15, cy - 20), (cx - 20, cy - 14), (cx - 21, cy - 6), (cx - 19, cy + 2), (cx - 16, cy + 8), (cx - 13, cy + 10), (cx - 11, cy + 4), (cx - 12, cy - 6), (cx - 12, cy - 16), (cx - 8, cy - 21), (cx - 2, cy - 23), (cx + 4, cy - 22), (cx + 8, cy - 18), (cx + 9, cy - 13), (cx + 7, cy - 12), (cx + 2, cy - 13), (cx - 6, cy - 14)], hair_pal, outline=None)
    cv.line(cx - 14, cy - 15, cx - 4, cy - 17, hair_pal[2])
    cv.line(cx - 8, cy - 11, cx - 2, cy - 12, hair_pal[3])
    cv.line(cx - 14, cy - 19, cx - 8, cy - 20, hair_pal[0])


# ================= 背面头/身体 =================
def head_back(cv, skin_pal, cx=96, cy=28):
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
    # 后颈 + 发际线阴影
    poly(cv, [(cx - 8, cy + 24), (cx - 8, cy + 33), (cx + 8, cy + 33), (cx + 8, cy + 24)], skin_pal, outline=None)
    cv.line(cx - 7, cy + 24, cx + 7, cy + 24, skin_pal[2])
    # 后脑勺高光
    cv.set(cx - 12, cy - 18, skin_pal[0]); cv.set(cx - 10, cy - 19, skin_pal[0])
    cv.set(cx - 8, cy - 20, skin_pal[0]); cv.set(cx - 5, cy - 20, skin_pal[0])


def body_back(cv, suit_pal, pants_pal, skin_pal, chain=False, leg_shorten=0, cx=96):
    ls = leg_shorten
    # 背面躯干（对称，后中线）
    torso = [
        (cx, 61), (cx - 10, 63), (cx - 20, 68), (cx - 28, 76),
        (cx - 32, 88), (cx - 32, 100), (cx - 28, 112),
        (cx - 22, 124), (cx - 18, 136), (cx - 14, 148),
        (cx - 14, 160), (cx + 14, 160),
        (cx + 14, 148), (cx + 18, 136), (cx + 22, 124),
        (cx + 28, 112), (cx + 32, 100), (cx + 32, 88),
        (cx + 28, 76), (cx + 20, 68), (cx + 10, 63),
    ]
    poly(cv, torso, suit_pal)
    # 后中线（西装后开衩）
    cv.line(cx, 100, cx, 160, suit_pal[3])
    # 手臂（背面，对称）
    poly(cv, [(cx - 28, 76), (cx - 36, 88), (cx - 36, 106), (cx - 30, 112), (cx - 24, 98), (cx - 22, 78)], suit_pal)
    poly(cv, [(cx - 36, 112), (cx - 38, 130), (cx - 34, 146), (cx - 28, 146), (cx - 30, 128), (cx - 30, 112)], suit_pal)
    poly(cv, [(cx - 36, 146), (cx - 30, 146), (cx - 30, 156), (cx - 36, 156)], skin_pal, outline=None)
    poly(cv, [(cx + 28, 76), (cx + 36, 88), (cx + 36, 106), (cx + 30, 112), (cx + 24, 98), (cx + 22, 78)], suit_pal)
    poly(cv, [(cx + 36, 112), (cx + 38, 130), (cx + 34, 146), (cx + 28, 146), (cx + 30, 128), (cx + 30, 112)], suit_pal)
    poly(cv, [(cx + 36, 146), (cx + 30, 146), (cx + 30, 156), (cx + 36, 156)], skin_pal, outline=None)
    # 腿（背面，对称）
    poly(cv, [(cx - 16, 160), (cx - 20, 190), (cx - 18, 220 - ls), (cx - 14, 226 - ls), (cx - 8, 226 - ls), (cx - 6, 220 - ls), (cx - 4, 190), (cx - 4, 160)], pants_pal)
    poly(cv, [(cx - 14, 226 - ls), (cx - 16, 256 - ls), (cx - 12, 280 - ls), (cx - 4, 280 - ls), (cx - 4, 256 - ls), (cx - 6, 226 - ls)], pants_pal)
    poly(cv, [(cx - 16, 280 - ls), (cx - 18, 290 - ls), (cx - 2, 292 - ls), (cx + 2, 288 - ls), (cx - 4, 280 - ls)], SHOE)
    poly(cv, [(cx + 4, 160), (cx + 4, 190), (cx + 6, 220 - ls), (cx + 8, 226 - ls), (cx + 14, 226 - ls), (cx + 18, 220 - ls), (cx + 20, 190), (cx + 16, 160)], pants_pal)
    poly(cv, [(cx + 6, 226 - ls), (cx + 4, 256 - ls), (cx + 12, 280 - ls), (cx + 16, 280 - ls), (cx + 16, 256 - ls), (cx + 14, 226 - ls)], pants_pal)
    poly(cv, [(cx + 4, 280 - ls), (cx + 2, 290 - ls), (cx + 18, 292 - ls), (cx + 16, 288 - ls), (cx + 12, 280 - ls)], SHOE)


# ================= 背面发型 =================
def hair_back_short(cv, hair_pal, cx=96, cy=28):
    poly(cv, [(cx - 24, cy - 12), (cx - 21, cy - 20), (cx - 13, cy - 23), (cx - 4, cy - 24), (cx + 4, cy - 24), (cx + 13, cy - 23), (cx + 21, cy - 20), (cx + 24, cy - 12), (cx + 21, cy - 6), (cx + 12, cy - 8), (cx - 12, cy - 8), (cx - 21, cy - 6)], hair_pal, outline=None)
    cv.line(cx - 12, cy - 18, cx - 6, cy - 18, hair_pal[0])
    cv.line(cx - 8, cy - 14, cx - 4, cy - 13, hair_pal[3])
    cv.line(cx + 4, cy - 14, cx + 8, cy - 13, hair_pal[3])


def hair_back_bald(cv, hair_pal, cx=96, cy=28):
    # 背面地中海：满头银发 + 中央大椭圆秃（占头顶一半）
    poly(cv, [(cx - 24, cy - 12), (cx - 21, cy - 20), (cx - 13, cy - 23), (cx - 4, cy - 24), (cx + 4, cy - 24), (cx + 13, cy - 23), (cx + 21, cy - 20), (cx + 24, cy - 12), (cx + 22, cy - 2), (cx + 20, cy + 6), (cx + 16, cy + 11), (cx + 8, cy + 13), (cx - 8, cy + 13), (cx - 16, cy + 11), (cx - 20, cy + 6), (cx - 22, cy - 2)], hair_pal, outline=None)
    # 中央秃顶（大椭圆，肤色，轻描边）
    poly(cv, [(cx - 14, cy - 8), (cx - 10, cy - 12), (cx - 4, cy - 14), (cx + 4, cy - 14), (cx + 10, cy - 12), (cx + 14, cy - 8), (cx + 12, cy - 2), (cx + 6, cy + 1), (cx - 6, cy + 1), (cx - 12, cy - 2)], SKIN_PALE, outline=SKIN_PALE[3])
    # 发丝纹理
    cv.line(cx - 16, cy + 2, cx - 12, cy + 8, hair_pal[3])
    cv.line(cx + 12, cy + 8, cx + 16, cy + 2, hair_pal[3])
    cv.line(cx - 10, cy + 10, cx - 6, cy + 12, hair_pal[3])
    cv.line(cx + 6, cy + 12, cx + 10, cy + 10, hair_pal[3])
    cv.line(cx - 20, cy - 14, cx - 16, cy - 16, hair_pal[0])
    cv.line(cx + 16, cy - 16, cx + 20, cy - 14, hair_pal[0])


def hair_back_part(cv, hair_pal, cx=96, cy=28):
    hair_back_short(cv, hair_pal, cx, cy)
    cv.line(cx, cy - 23, cx + 4, cy - 8, hair_pal[3])


def hair_back_messy(cv, hair_pal, cx=96, cy=28):
    hair_back_short(cv, hair_pal, cx, cy)
    cv.line(cx - 14, cy - 22, cx - 16, cy - 25, hair_pal[1])
    cv.set(cx - 16, cy - 26, hair_pal[0])
    cv.line(cx + 8, cy - 23, cx + 10, cy - 26, hair_pal[1])
    cv.set(cx + 10, cy - 27, hair_pal[0])


def hair_back_slickback(cv, hair_pal, cx=96, cy=28):
    poly(cv, [(cx - 24, cy - 12), (cx - 21, cy - 20), (cx - 13, cy - 23), (cx - 4, cy - 24), (cx + 4, cy - 24), (cx + 13, cy - 23), (cx + 21, cy - 20), (cx + 24, cy - 12), (cx + 20, cy - 4), (cx + 12, cy - 6), (cx - 12, cy - 6), (cx - 20, cy - 4)], hair_pal, outline=None)
    cv.line(cx - 14, cy - 17, cx - 4, cy - 18, hair_pal[2])
    cv.line(cx + 4, cy - 18, cx + 14, cy - 17, hair_pal[2])
    cv.line(cx - 12, cy - 20, cx - 6, cy - 20, hair_pal[0])


def hair_back_twintail(cv, hair_pal, cx=96, cy=28):
    hair_back_short(cv, hair_pal, cx, cy)
    for sgn in (-1, 1):
        poly(cv, [(cx + sgn * 20, cy - 6), (cx + sgn * 26, cy - 2), (cx + sgn * 28, cy + 8), (cx + sgn * 28, cy + 18), (cx + sgn * 27, cy + 26), (cx + sgn * 24, cy + 28), (cx + sgn * 21, cy + 24), (cx + sgn * 22, cy + 12)], hair_pal, outline=None)
        cv.line(cx + sgn * 27, cy + 8, cx + sgn * 26, cy + 16, hair_pal[3])
        poly(cv, [(cx + sgn * 20, cy - 5), (cx + sgn * 23, cy - 3), (cx + sgn * 23, cy - 1), (cx + sgn * 20, cy - 3)], GIRL, outline=None)


# ================= 8 角色侧面 =================
def elder_side(cv):
    head_side(cv, SKIN_PALE, EYE_BROWN, wrinkles=True)
    hair_side_bald(cv, WHITE)
    body_side(cv, NAVY, PANTS_BLACK, SHIRT, BLUE_TIE, SKIN_PALE, tie_style="full", chain=True, leg_shorten=14)
    return 278


def young_side(cv):
    head_side(cv, SKIN, EYE_BLUE)
    hair_side_short(cv, BROWN)
    body_side(cv, GREY, PANTS, SHIRT, RED, SKIN, tie_style="full", leg_shorten=0)
    return 292


def clone_side(cv):
    head_side(cv, SKIN, EYE_BLUE)
    hair_side_part(cv, DARK_BROWN)
    body_side(cv, NAVY, PANTS, SHIRT, BLUE_TIE, SKIN, tie_style="full", leg_shorten=0)
    return 292


def richard_side(cv):
    head_side(cv, SKIN, EYE_BROWN)
    hair_side_slickback(cv, DARK_BROWN)
    # 胡子（侧脸，下巴）
    cv.line(cx_sb() + 12, 39, cx_sb() + 13, 41, DARK_BROWN[2])
    cv.line(cx_sb() + 13, 42, cx_sb() + 12, 43, DARK_BROWN[2])
    # 金丝眼镜（侧脸，单框 + 镜腿）
    cv.ellipse(101, 29, 5, 5, GOLD[1])
    cv.line(96, 29, 84, 27, GOLD[1])
    body_side(cv, GREEN_SUIT, PANTS_BLACK, SHIRT, RED, SKIN, tie_style="bow", chain=True, leg_shorten=0)
    return 292


def cx_sb():
    return 96


def boy_side(cv):
    head_side(cv, SKIN, EYE_BROWN)
    hair_side_messy(cv, BROWN)
    cx = 96
    # 破旧上衣（侧面，前胸凸）
    poly(cv, [(cx, 61), (cx - 12, 64), (cx - 14, 78), (cx - 12, 96), (cx - 8, 108), (cx + 8, 110), (cx + 12, 100), (cx + 13, 80), (cx + 10, 66)], RAG)
    poly(cv, [(cx + 2, 62), (cx + 6, 68), (cx + 8, 62)], RAG[3], outline=None)
    # 手臂（前侧）
    poly(cv, [(cx + 4, 72), (cx + 8, 86), (cx + 10, 100), (cx + 6, 104), (cx + 2, 90)], RAG)
    poly(cv, [(cx + 10, 100), (cx + 12, 116), (cx + 9, 130), (cx + 5, 130), (cx + 5, 114), (cx + 5, 102)], RAG)
    poly(cv, [(cx + 11, 130), (cx + 8, 130), (cx + 8, 138), (cx + 11, 138)], SKIN, outline=None)
    # 短裤（侧面）
    poly(cv, [(cx - 8, 108), (cx - 10, 140), (cx + 8, 142), (cx + 8, 108)], PANTS)
    # 左腿残端（截肢端，浅色绷带）
    poly(cv, [(cx - 8, 140), (cx - 10, 160), (cx - 5, 163), (cx + 1, 160), (cx + 2, 140)], RAG[1])
    for yy in range(144, 158, 3):
        cv.line(cx - 8, yy, cx + 1, yy, RAG[2])
    cv.line(cx - 9, 160, cx + 1, 160, RAG[4])
    # 右腿完好（前侧单腿 + 鞋）
    poly(cv, [(cx + 2, 142), (cx + 2, 190), (cx + 4, 220), (cx + 10, 220), (cx + 12, 190), (cx + 12, 142)], SKIN)
    poly(cv, [(cx + 2, 220), (cx + 2, 246), (cx + 14, 248), (cx + 16, 242), (cx + 10, 220)], SHOE)
    # 拐杖（左手后侧拄拐：L 形手柄 + 2px 粗杖身 + 橡胶杖尖）
    cv.line(cx - 14, 128, cx - 2, 128, WOOD[0])    # 握把横杆
    cv.line(cx - 14, 128, cx - 14, 134, WOOD[0])   # 手柄竖端（虎口位）
    for i in range(0, 114):                         # 杖身 2px 粗，垂直
        y = 134 + i
        cv.set(cx - 13, y, WOOD[1])
        cv.set(cx - 12, y, WOOD[2])
    cv.line(cx - 14, 246, cx - 11, 248, WOOD[3])    # 杖尖橡胶头
    cv.line(cx - 11, 246, cx - 10, 248, WOOD[3])
    return 248


def girl_side(cv):
    head_side(cv, SKIN, EYE_BLUE)
    hair_side_twintail(cv, ORANGE)
    cx = 96
    # 粉裙（侧面，前胸凸）
    poly(cv, [(cx, 61), (cx - 10, 64), (cx - 12, 78), (cx - 10, 100), (cx - 6, 116), (cx + 6, 118), (cx + 11, 106), (cx + 12, 82), (cx + 8, 66)], GIRL)
    poly(cv, [(cx + 2, 62), (cx + 6, 68), (cx + 8, 62)], GIRL[3], outline=None)
    # 白围裙（前侧）
    poly(cv, [(cx, 84), (cx + 2, 104), (cx + 4, 118), (cx - 2, 118), (cx - 4, 104), (cx - 2, 84)], APRON, outline=None)
    cv.line(cx - 2, 96, cx + 3, 96, APRON[3])
    # 手臂（前侧，短袖）
    poly(cv, [(cx + 2, 72), (cx + 6, 84), (cx + 8, 96), (cx + 4, 98), (cx, 86)], GIRL)
    poly(cv, [(cx + 8, 96), (cx + 10, 112), (cx + 8, 124), (cx + 3, 124), (cx + 3, 110), (cx + 3, 98)], SKIN)
    # 右手拿信纸（前伸）
    poly(cv, [(cx + 10, 106), (cx + 18, 104), (cx + 18, 122), (cx + 10, 124)], SHIRT, outline=SHIRT[3])
    cv.line(cx + 11, 112, cx + 17, 111, SHIRT[3])
    cv.line(cx + 11, 116, cx + 16, 116, SHIRT[3])
    # 腿一条（侧面，加宽体积）+ 白袜 + 粉鞋
    poly(cv, [(cx - 2, 118), (cx - 2, 160), (cx + 5, 160), (cx + 5, 118)], SKIN)
    poly(cv, [(cx - 2, 160), (cx - 2, 210), (cx + 5, 210), (cx + 5, 160)], SHIRT, outline=None)
    poly(cv, [(cx - 4, 210), (cx - 4, 228), (cx + 9, 230), (cx + 9, 224), (cx + 3, 210)], GIRL)
    return 232


def mech_side(cv):
    cx = 96
    # 金属头侧面（后脑左、面部右）
    cv.ellipse_shaded(cx, 26, 20, 20, METAL)
    poly(cv, [(cx - 6, 12), (cx + 16, 14), (cx + 18, 34), (cx + 4, 36), (cx - 8, 34)], METAL[1:2], outline=None)
    # 眼带（斜条，只前侧）
    cv.line(cx + 2, 25, cx + 18, 27, ICE[0])
    cv.line(cx + 2, 26, cx + 18, 28, ICE[1])
    # 天线
    cv.line(cx, 6, cx, 2, METAL[3])
    cv.set(cx, 1, ICE[1])
    # 脖子（偏后）
    poly(cv, [(cx - 8, 42), (cx - 8, 52), (cx + 8, 52), (cx + 8, 42)], METAL)
    # 躯干（前后厚度：前胸 cx+18 凸、后背 cx-18）
    poly(cv, [(cx - 14, 52), (cx - 20, 70), (cx - 18, 110), (cx - 12, 128), (cx + 4, 134), (cx + 16, 124), (cx + 20, 106), (cx + 18, 70), (cx + 10, 52)], METAL)
    cv.line(cx - 16, 80, cx + 18, 80, METAL[3])
    cv.line(cx - 15, 100, cx + 17, 100, METAL[3])
    # 核心灯（胸前，偏前）
    cv.ellipse_shaded(cx + 4, 88, 8, 8, ICE)
    cv.set(cx + 3, 86, ICE[0]); cv.set(cx + 4, 86, ICE[0]); cv.set(cx + 5, 86, ICE[0])
    # 散热栅格
    for gy in range(104, 126, 4):
        cv.line(cx - 6, gy, cx + 12, gy, METAL[4])
    # 手臂（一条，前侧）
    poly(cv, [(cx + 10, 70), (cx + 18, 84), (cx + 18, 108), (cx + 12, 112), (cx + 8, 92)], METAL)
    poly(cv, [(cx + 18, 112), (cx + 20, 128), (cx + 16, 140), (cx + 10, 140), (cx + 12, 126), (cx + 12, 112)], METAL)
    cv.line(cx + 18, 114, cx + 12, 116, METAL[4])
    # 线缆下半身（偏后，几条彩色）
    for i, col in enumerate([RED[1], BLUE_TIE[1], GOLD[1], ICE[1], GREY[1]]):
        base_x = cx - 12 + i * 7
        for y in range(134, 280):
            x = base_x + int(6 * math.sin((y - 134) * 0.06 + i * 1.2))
            cv.set(x, y, col)
    return 280


def cube_side(cv):
    cx = 96
    # 立方体侧面（平行四边形，立体感）
    poly(cv, [(cx - 30, 76), (cx - 14, 66), (cx + 30, 66), (cx + 46, 76), (cx + 46, 128), (cx + 30, 138), (cx - 14, 138), (cx - 30, 128)], BLACK)
    poly(cv, [(cx - 30, 76), (cx - 14, 66), (cx - 14, 76), (cx - 30, 86)], BLACK[1:3], outline=None)
    poly(cv, [(cx - 14, 66), (cx + 30, 66), (cx + 30, 76), (cx - 14, 76)], BLACK[0:1], outline=None)
    # 侧面中央冰青屏幕 + 稀疏数据点
    poly(cv, [(cx - 10, 86), (cx + 6, 80), (cx + 34, 80), (cx + 42, 86), (cx + 42, 122), (cx + 34, 128), (cx + 6, 128), (cx - 10, 122)], [ICE[1]], outline=None)
    for py, xs in [(86, [-2, 10, 22]), (94, [6, 18, 30]), (102, [2, 14, 26]), (110, [8, 20, 32]), (118, [-4, 12, 24])]:
        for px in xs:
            cv.set(cx + px, py, ICE[4])
    cv.line(cx - 30, 76, cx - 14, 66, ICE[1]); cv.line(cx - 14, 66, cx + 30, 66, ICE[1])
    cv.line(cx + 30, 66, cx + 46, 76, ICE[1]); cv.line(cx + 46, 76, cx + 46, 128, ICE[1])
    cv.line(cx + 46, 128, cx + 30, 138, ICE[1]); cv.line(cx + 30, 138, cx - 14, 138, ICE[1])
    cv.line(cx - 14, 138, cx - 30, 128, ICE[1]); cv.line(cx - 30, 128, cx - 30, 76, ICE[1])
    cv.line(cx - 24, 146, cx + 40, 146, ICE[2])
    cv.line(cx - 14, 150, cx + 30, 150, ICE[3])
    cv.line(cx - 4, 154, cx + 20, 154, ICE[4])
    return 204


# ================= 8 角色背面 =================
def elder_back(cv):
    head_back(cv, SKIN_PALE)
    hair_back_bald(cv, WHITE)
    body_back(cv, NAVY, PANTS_BLACK, SKIN_PALE, chain=True, leg_shorten=14)
    return 278


def young_back(cv):
    head_back(cv, SKIN)
    hair_back_short(cv, BROWN)
    body_back(cv, GREY, PANTS, SKIN, leg_shorten=0)
    return 292


def clone_back(cv):
    head_back(cv, SKIN)
    hair_back_part(cv, DARK_BROWN)
    body_back(cv, NAVY, PANTS, SKIN, leg_shorten=0)
    return 292


def richard_back(cv):
    head_back(cv, SKIN)
    hair_back_slickback(cv, DARK_BROWN)
    body_back(cv, GREEN_SUIT, PANTS_BLACK, SKIN, chain=True, leg_shorten=0)
    return 292


def boy_back(cv):
    head_back(cv, SKIN)
    hair_back_messy(cv, BROWN)
    cx = 96
    poly(cv, [(cx - 24, 62), (cx - 30, 74), (cx - 30, 96), (cx - 22, 108), (cx - 14, 112), (cx + 14, 112), (cx + 22, 108), (cx + 30, 96), (cx + 30, 74), (cx + 24, 62), (cx, 60)], RAG)
    poly(cv, [(cx - 26, 74), (cx - 32, 88), (cx - 32, 106), (cx - 26, 110), (cx - 22, 94), (cx - 20, 76)], RAG)
    poly(cv, [(cx + 26, 74), (cx + 32, 88), (cx + 32, 106), (cx + 26, 110), (cx + 22, 94), (cx + 20, 76)], RAG)
    poly(cv, [(cx - 20, 108), (cx - 22, 140), (cx - 8, 142), (cx + 8, 142), (cx + 22, 140), (cx + 20, 108)], PANTS)
    # 残端（背面，屏幕右）
    poly(cv, [(cx + 6, 140), (cx + 6, 160), (cx + 14, 163), (cx + 19, 160), (cx + 19, 140)], RAG[1])
    for yy in range(144, 158, 3):
        cv.line(cx + 7, yy, cx + 18, yy, RAG[2])
    cv.line(cx + 6, 160, cx + 19, 160, RAG[4])
    # 完好腿（背面，屏幕左）
    poly(cv, [(cx - 18, 142), (cx - 16, 190), (cx - 14, 220), (cx - 8, 220), (cx - 6, 190), (cx - 4, 142)], SKIN)
    poly(cv, [(cx - 14, 220), (cx - 14, 246), (cx - 2, 248), (cx, 242), (cx - 8, 220)], SHOE)
    # 拐杖（背面，屏幕右）
    for i in range(0, 100):
        y = 92 + i
        x = cx + 44 - i * 0.10
        cv.set(int(x), y, WOOD[1])
    cv.line(cx + 42, 92, cx + 44, 96, WOOD[2])
    cv.line(cx + 35, 190, cx + 37, 196, WOOD[2]); cv.line(cx + 35, 190, cx + 33, 196, WOOD[2])
    return 248


def girl_back(cv):
    head_back(cv, SKIN)
    hair_back_twintail(cv, ORANGE)
    cx = 96
    poly(cv, [(cx - 22, 62), (cx - 28, 74), (cx - 28, 100), (cx - 20, 116), (cx - 10, 122), (cx + 10, 122), (cx + 20, 116), (cx + 28, 100), (cx + 28, 74), (cx + 22, 62), (cx, 60)], GIRL)
    poly(cv, [(cx - 10, 80), (cx - 12, 100), (cx - 8, 118), (cx + 8, 118), (cx + 12, 100), (cx + 10, 80)], APRON, outline=None)
    cv.line(cx - 12, 96, cx + 12, 96, APRON[3])
    cv.line(cx - 10, 80, cx - 16, 70, APRON[2]); cv.line(cx + 10, 80, cx + 16, 70, APRON[2])
    poly(cv, [(cx - 26, 74), (cx - 30, 84), (cx - 30, 96), (cx - 24, 98), (cx - 20, 86)], GIRL)
    poly(cv, [(cx + 26, 74), (cx + 30, 84), (cx + 30, 96), (cx + 24, 98), (cx + 20, 86)], GIRL)
    poly(cv, [(cx - 16, 122), (cx - 16, 160), (cx - 10, 160), (cx - 10, 122)], SKIN)
    poly(cv, [(cx + 6, 122), (cx + 6, 160), (cx + 12, 160), (cx + 12, 122)], SKIN)
    poly(cv, [(cx - 16, 160), (cx - 16, 210), (cx - 10, 210), (cx - 10, 160)], SHIRT, outline=None)
    poly(cv, [(cx + 6, 160), (cx + 6, 210), (cx + 12, 210), (cx + 12, 160)], SHIRT, outline=None)
    poly(cv, [(cx - 18, 210), (cx - 18, 228), (cx - 8, 230), (cx - 6, 224), (cx - 8, 210)], GIRL)
    poly(cv, [(cx + 8, 210), (cx + 8, 224), (cx + 18, 228), (cx + 20, 224), (cx + 14, 210)], GIRL)
    return 232


def mech_back(cv):
    cx = 96
    cv.ellipse_shaded(cx, 26, 20, 20, METAL)
    cv.line(cx, 6, cx, 2, METAL[3]); cv.set(cx, 1, ICE[1])
    poly(cv, [(cx - 8, 42), (cx - 8, 52), (cx + 8, 52), (cx + 8, 42)], METAL)
    poly(cv, [(cx - 20, 52), (cx - 26, 70), (cx - 26, 110), (cx - 20, 128), (cx - 10, 134), (cx + 10, 134), (cx + 20, 128), (cx + 26, 110), (cx + 26, 70), (cx + 20, 52)], METAL)
    cv.line(cx, 52, cx, 134, METAL[4])
    cv.line(cx - 24, 80, cx + 24, 80, METAL[3])
    cv.line(cx - 22, 100, cx + 22, 100, METAL[3])
    for gy in range(104, 126, 4):
        cv.line(cx - 12, gy, cx + 12, gy, METAL[4])
    poly(cv, [(cx - 26, 70), (cx - 34, 84), (cx - 34, 108), (cx - 28, 112), (cx - 22, 92)], METAL)
    poly(cv, [(cx + 26, 70), (cx + 34, 84), (cx + 34, 108), (cx + 28, 112), (cx + 22, 92)], METAL)
    poly(cv, [(cx - 34, 112), (cx - 36, 128), (cx - 32, 140), (cx - 26, 140), (cx - 28, 126), (cx - 28, 112)], METAL)
    poly(cv, [(cx + 34, 112), (cx + 36, 128), (cx + 32, 140), (cx + 26, 140), (cx + 28, 126), (cx + 28, 112)], METAL)
    for i, col in enumerate([RED[1], BLUE_TIE[1], GOLD[1], ICE[1], GREY[1]]):
        base_x = cx - 16 + i * 8
        for y in range(134, 280):
            x = base_x + int(6 * math.sin((y - 134) * 0.06 + i * 1.2))
            cv.set(x, y, col)
    return 280


def cube_back(cv):
    cx = 96
    poly(cv, [(cx - 30, 76), (cx - 14, 66), (cx + 30, 66), (cx + 46, 76), (cx + 46, 128), (cx + 30, 138), (cx - 14, 138), (cx - 30, 128)], BLACK)
    poly(cv, [(cx - 14, 66), (cx + 30, 66), (cx + 30, 76), (cx - 14, 76)], BLACK[0:1], outline=None)
    # 背面中央冰青屏幕 + 稀疏数据点
    poly(cv, [(cx - 10, 86), (cx + 6, 80), (cx + 34, 80), (cx + 42, 86), (cx + 42, 122), (cx + 34, 128), (cx + 6, 128), (cx - 10, 122)], [ICE[1]], outline=None)
    for py, xs in [(86, [-2, 10, 22]), (94, [6, 18, 30]), (102, [2, 14, 26]), (110, [8, 20, 32]), (118, [-4, 12, 24])]:
        for px in xs:
            cv.set(cx + px, py, ICE[4])
    cv.line(cx - 30, 76, cx - 14, 66, ICE[1]); cv.line(cx - 14, 66, cx + 30, 66, ICE[1])
    cv.line(cx + 30, 66, cx + 46, 76, ICE[1]); cv.line(cx + 46, 76, cx + 46, 128, ICE[1])
    cv.line(cx + 46, 128, cx + 30, 138, ICE[1]); cv.line(cx + 30, 138, cx - 14, 138, ICE[1])
    cv.line(cx - 14, 138, cx - 30, 128, ICE[1]); cv.line(cx - 30, 128, cx - 30, 76, ICE[1])
    cv.line(cx - 24, 146, cx + 40, 146, ICE[2])
    cv.line(cx - 14, 150, cx + 30, 150, ICE[3])
    cv.line(cx - 4, 154, cx + 20, 154, ICE[4])
    return 204


# ================= 渲染 =================
ROLES_SB = [
    ("elder", elder_side, elder_back, "老年赞比"),
    ("young", young_side, young_back, "青年赞比"),
    ("clone", clone_side, clone_back, "克隆赞比"),
    ("richard", richard_side, richard_back, "理查德·史密斯"),
    ("boy", boy_side, boy_back, "少年赞比"),
    ("girl", girl_side, girl_back, "女孩"),
    ("mech", mech_side, mech_back, "机械赞比"),
    ("cube", cube_side, cube_back, "立方体赞比"),
]


def render_side(name, fn):
    cv = Canvas(192, 320, BG)
    bottom = fn(cv)
    align(cv, bottom)
    return upscale(cv, 2)


def render_all_sb():
    import os
    os.makedirs("portraits_v6", exist_ok=True)
    for name, fn_side, fn_back, label in ROLES_SB:
        render_side(name, fn_side).save(f"portraits_v6/{name}_side.png")
        render_side(name, fn_back).save(f"portraits_v6/{name}_back.png")
        print(f"saved {name} side/back")
    make_sheets()


def make_sheets():
    from PIL import Image
    for suffix, idx in [("side", 1), ("back", 2)]:
        imgs = [Image.open(f"portraits_v6/{n}_{suffix}.png") for n, _, _, _ in ROLES_SB]
        w, h = imgs[0].size
        sheet = Image.new("RGB", (4 * w, 2 * h), BG)
        for i, im in enumerate(imgs):
            sheet.paste(im, ((i % 4) * w, (i // 4) * h))
        sheet.save(f"portraits_v6/{suffix}s_sheet.png")
        print(f"{suffix}s_sheet saved")


if __name__ == "__main__":
    render_all_sb()