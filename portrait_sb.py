# -*- coding: utf-8 -*-
"""《赞比的遗产》8 角色侧面 + 背面立绘（三视图补全）。

复用 pixel_engine 的 Canvas/poly/line；正面立绘在 portrait_v5.py。
侧面：面向右（单眼+鼻凸+嘴偏前+耳朵）；背面：后脑勺头发全覆盖+背缝。
"""
from pixel_engine import Canvas, upscale
from portrait_v5 import (OUT, SKIN, SKIN_PALE, WHITE, BROWN, DARK_BROWN, ORANGE,
                         EYE_BLUE, EYE_BROWN, EYE_P, EYE_W, NAVY, GREY, BLACK,
                         SHIRT, RED, BLUE_TIE, GOLD, PANTS, PANTS_BLACK, SHOE,
                         RAG, WOOD, METAL, ICE, GIRL, poly, point_in_poly,
                         GREEN_SUIT, APRON)
import math


# ================= 侧面头（面向右） =================
def head_side(cv, skin_pal, eye_col, mouth="flat", cx=48, cy=16):
    # 现实侧面人脸轮廓：后脑勺圆 → 头顶 → 额头 → 眉骨 → 鼻根内凹 → 鼻梁 → 鼻尖最凸
    # → 鼻底 → 人中内凹 → 上唇 → 嘴缝 → 下唇 → 颏唇沟 → 下巴内收 → 下颌 → 脖子
    head = [
        (cx - 15, cy - 1),  # 后脑勺最凸（左）
        (cx - 14, cy - 6),  # 后脑上
        (cx - 11, cy - 10),  # 后脑顶
        (cx - 6, cy - 12),  # 头顶后
        (cx - 1, cy - 12),  # 头顶前
        (cx + 3, cy - 11),  # 额头
        (cx + 5, cy - 8),  # 眉骨
        (cx + 6, cy - 5),  # 鼻根（内凹）
        (cx + 7, cy - 2),  # 鼻梁
        (cx + 9, cy),  # 鼻尖上
        (cx + 10, cy + 1),  # 鼻尖（最凸出点）
        (cx + 9, cy + 3),  # 鼻底
        (cx + 7, cy + 4),  # 人中（内凹）
        (cx + 8, cy + 5),  # 上唇
        (cx + 7, cy + 6),  # 嘴缝
        (cx + 7, cy + 8),  # 下唇
        (cx + 6, cy + 9),  # 颏唇沟（内凹）
        (cx + 5, cy + 11),  # 下巴
        (cx + 2, cy + 12),  # 下巴底
        (cx - 2, cy + 12),  # 下颌
        (cx - 6, cy + 10),  # 下颌后
        (cx - 9, cy + 7),  # 后颈
        (cx - 12, cy + 3),  # 后颈下
        (cx - 13, cy),  # 后脑下
    ]
    poly(cv, head, skin_pal)
    # 单眼（鼻根后方，眼睛位于头部前 1/3 处）
    cv.line(cx + 1, cy - 4, cx + 4, cy - 4, skin_pal[3])
    cv.set(cx + 1, cy - 3, eye_col); cv.set(cx + 2, cy - 3, eye_col)
    cv.set(cx + 1, cy - 2, eye_col); cv.set(cx + 2, cy - 2, eye_col)
    cv.set(cx + 2, cy - 2, EYE_P)
    cv.set(cx + 1, cy - 3, EYE_W)
    # 眉毛
    cv.line(cx, cy - 6, cx + 4, cy - 5, skin_pal[3])
    # 嘴（鼻下偏后）
    if mouth == "smile":
        cv.set(cx + 5, cy + 6, skin_pal[3]); cv.set(cx + 8, cy + 6, skin_pal[3])
        for x in range(cx + 5, cx + 9):
            cv.set(x, cy + 7, skin_pal[3])
    elif mouth == "flat":
        cv.line(cx + 5, cy + 6, cx + 8, cy + 6, skin_pal[3])
    elif mouth == "frown":
        cv.set(cx + 5, cy + 6, skin_pal[3]); cv.set(cx + 8, cy + 6, skin_pal[3])
        cv.set(cx + 6, cy + 5, skin_pal[3]); cv.set(cx + 7, cy + 5, skin_pal[3])
    elif mouth == "sad":
        cv.set(cx + 5, cy + 6, skin_pal[3]); cv.set(cx + 8, cy + 6, skin_pal[3])
        cv.set(cx + 7, cy + 5, skin_pal[3])
    # 耳朵（眼睛正后方，与眼睛同高）
    poly(cv, [(cx - 7, cy - 1), (cx - 6, cy), (cx - 7, cy + 3), (cx - 5, cy + 2), (cx - 5, cy)],
         skin_pal, outline=skin_pal[3])
    # 脖子（头部下方偏后，斜连躯干）
    neck = [(cx - 4, cy + 12), (cx - 4, cy + 17), (cx + 3, cy + 17), (cx + 3, cy + 12)]
    poly(cv, neck, skin_pal, outline=None)


# ================= 侧面头发 =================
def hair_side_bald(cv):
    # 秃顶侧面：后脑勺白发，头顶中央秃（露肤色 x44-51），前额少量发根（不遮眼鼻）
    # 后脑勺+头顶后部发块（x31-44，覆盖头顶后部到 x44）
    poly(cv, [(34, 4), (31, 8), (31, 14), (32, 19), (35, 22), (39, 24),
              (43, 24), (44, 20), (44, 13), (44, 8), (43, 4)], WHITE)
    # 前额发根（x52-58，头顶到发际线 y12，不遮眼睛 y14+/鼻子 y17+）
    poly(cv, [(52, 4), (55, 5), (57, 7), (58, 9), (58, 11), (56, 12),
              (53, 12), (52, 11), (51, 8), (51, 5)], WHITE)


def hair_side_short(cv, pal):
    # 短发侧面：覆盖整个头顶（无秃）+后脑勺；前额发际线 y11（不遮眉毛 y12/眼 y14-16/鼻 y17+）
    # 后脑勺+头顶发块（覆盖 y4 的 x34-46，头顶无缝隙）
    poly(cv, [(34, 4), (31, 8), (31, 14), (32, 19), (35, 22), (39, 24),
              (43, 24), (46, 20), (46, 13), (46, 8), (46, 4)], pal)
    # 前额发块（头顶 y4 到发际线 y12，覆盖 y4 的 x46-52，与后块 x46 相接）
    poly(cv, [(46, 4), (52, 4), (54, 6), (56, 8), (57, 10), (56, 12),
              (53, 12), (50, 12), (48, 10), (47, 7)], pal)


def hair_side_part(cv, pal):
    hair_side_short(cv, pal)
    cv.line(46, 5, 47, 20, pal[3])


def hair_side_messy(cv, pal):
    hair_side_short(cv, pal)
    for i, x in enumerate((38, 44, 50, 55)):
        cv.line(x, 3 - (i % 2), x + (1 if i % 2 else -1), 0, pal[1])


def hair_side_ponytail(cv, pal):
    hair_side_short(cv, pal)
    # 马尾（后脑勺垂下）
    poly(cv, [(38, 6), (34, 10), (33, 20), (34, 30), (37, 36), (40, 36),
              (42, 30), (42, 18), (41, 10)], pal)


# ================= 侧面身体 =================
def body_side(cv, suit_pal, pants_pal, shirt_pal, tie_pal, tie_style="tie", chain=None, leg_shorten=0):
    ls = leg_shorten
    # 躯干（面向右：右=前胸/腹，左=后背，体现前后厚度）
    torso = [
        (40, 33),  # 后肩（左，背）
        (45, 33),  # 前肩（右，胸）
        (47, 36),  # 领口前
        (57, 39),  # 胸口前（微凸）
        (58, 50),  # 腹部前
        (57, 63),  # 腰前（微收）
        (56, 82),  # 下摆前
        (48, 84),  # 下摆底前
        (42, 84),  # 下摆底后
        (40, 82),  # 下摆后
        (38, 63),  # 腰后（微收）
        (37, 50),  # 背后
        (38, 36),  # 后肩
    ]
    poly(cv, torso, suit_pal)
    # 衬衫领（胸前领口）
    poly(cv, [(45, 33), (48, 36), (47, 38), (45, 35)], shirt_pal, outline=None)
    # 领带（垂在胸前，身体前侧窄条）
    if tie_style == "tie":
        poly(cv, [(56, 38), (58, 38), (58, 60), (56, 60)], tie_pal)
        cv.set(57, 40, tie_pal[0])
    elif tie_style == "bowtie":
        poly(cv, [(55, 37), (58, 37), (58, 41), (55, 41)], tie_pal)
    # 金链（胸前垂下，一条弧线链子）
    if chain:
        pts = [(56, 40), (57, 44), (57, 48), (56, 52), (55, 56), (54, 60)]
        for i in range(len(pts) - 1):
            cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], chain[0])
        cv.set(54, 61, chain[1]); cv.set(54, 62, chain[2])
    # 手臂（身体前侧，自然下垂，肩到手腕）
    poly(cv, [(45, 33), (48, 36), (50, 52), (49, 78), (46, 80), (44, 52)], suit_pal)
    # 手（袖口露出）
    poly(cv, [(45, 78), (49, 78), (49, 83), (45, 83)], SKIN)
    # 腿（一条，两条腿在侧面重叠；膝盖微凸向前）
    poly(cv, [(44, 84), (45, 112 - ls), (46, 138 - ls), (52, 138 - ls), (52, 112 - ls), (50, 84)], pants_pal)
    # 脚（一只鞋，脚尖向右）
    poly(cv, [(43, 138 - ls), (43, 145 - ls), (57, 145 - ls), (57, 141 - ls), (50, 138 - ls)], SHOE)


# ================= 背面头 =================
def head_back(cv, skin_pal, cx=48, cy=16):
    head = [
        (cx - 12, cy), (cx - 11, cy - 4), (cx - 8, cy - 8), (cx - 5, cy - 11),
        (cx - 2, cy - 12), (cx + 2, cy - 12), (cx + 5, cy - 11), (cx + 8, cy - 8),
        (cx + 11, cy - 4), (cx + 12, cy), (cx + 11, cy + 4), (cx + 8, cy + 8),
        (cx + 4, cy + 12), (cx - 4, cy + 12), (cx - 8, cy + 8), (cx - 11, cy + 4),
    ]
    poly(cv, head, skin_pal)
    # 耳朵（两侧）
    poly(cv, [(cx - 12, cy - 2), (cx - 11, cy), (cx - 12, cy + 2)], skin_pal, outline=skin_pal[3])
    poly(cv, [(cx + 12, cy - 2), (cx + 11, cy), (cx + 12, cy + 2)], skin_pal, outline=skin_pal[3])
    # 后颈
    neck = [(cx - 4, cy + 12), (cx - 4, cy + 17), (cx + 4, cy + 17), (cx + 4, cy + 12)]
    poly(cv, neck, skin_pal, outline=None)


def hair_back_full(cv, pal):
    # 后脑勺头发全覆盖（露后颈下缘）
    poly(cv, [(36, 4), (33, 8), (32, 13), (33, 18), (36, 22), (40, 24),
              (44, 24), (48, 24), (52, 24), (56, 22), (59, 18), (60, 13),
              (59, 8), (56, 4)], pal)
    poly(cv, [(36, 22), (40, 26), (48, 26), (52, 26), (56, 22)], pal)


def hair_back_bald(cv):
    # 背面秃顶（地中海）：满头银发，头顶中央椭圆秃（露肤色，深色描边）
    # 1. 满头银发（后脑勺全覆盖）
    poly(cv, [(36, 4), (33, 8), (32, 13), (33, 18), (36, 22), (40, 24),
              (44, 24), (48, 24), (52, 24), (56, 22), (59, 18), (60, 13),
              (59, 8), (56, 4)], WHITE)
    poly(cv, [(36, 22), (40, 26), (48, 26), (52, 26), (56, 22)], WHITE)
    # 发丝纹理（后脑勺头发走向，深银灰细线）
    cv.line(37, 8, 36, 18, WHITE[3])
    cv.line(41, 6, 39, 20, WHITE[3])
    cv.line(52, 7, 51, 20, WHITE[3])
    cv.line(57, 9, 57, 20, WHITE[3])
    # 2. 头顶中央椭圆秃（露肤色，深色 OUT 描边强化边界）
    poly(cv, [(44, 5), (47, 4), (50, 4), (53, 5), (54, 9), (53, 12), (50, 13),
              (47, 13), (44, 12), (43, 9)], SKIN, outline=OUT)


def hair_back_ponytail(cv, pal):
    hair_back_full(cv, pal)
    poly(cv, [(38, 6), (34, 10), (33, 22), (34, 32), (37, 38), (40, 38),
              (42, 32), (42, 18), (41, 10)], pal)


# ================= 背面身体 =================
def body_back(cv, suit_pal, pants_pal, shirt_pal, leg_shorten=0):
    ls = leg_shorten
    torso = [
        (44, 33), (36, 36), (35, 48), (37, 60), (39, 84), (44, 84),
        (52, 84), (57, 84), (59, 60), (61, 48), (60, 36), (52, 33),
    ]
    poly(cv, torso, suit_pal)
    cv.line(48, 35, 48, 82, suit_pal[2])
    poly(cv, [(44, 33), (48, 37), (52, 33)], shirt_pal, outline=None)
    poly(cv, [(36, 36), (32, 54), (33, 80), (37, 80), (38, 54), (39, 36)], suit_pal)
    poly(cv, [(60, 36), (64, 54), (63, 80), (59, 80), (58, 54), (57, 36)], suit_pal)
    poly(cv, [(39, 84), (40, 120 - ls), (41, 138 - ls), (47, 138 - ls), (47, 120 - ls), (45, 84)], pants_pal)
    poly(cv, [(49, 84), (50, 120 - ls), (51, 138 - ls), (57, 138 - ls), (57, 120 - ls), (55, 84)], pants_pal)
    poly(cv, [(40, 138 - ls), (40, 145 - ls), (48, 145 - ls), (48, 138 - ls)], SHOE)
    poly(cv, [(50, 138 - ls), (50, 145 - ls), (58, 145 - ls), (58, 138 - ls)], SHOE)


# ================= 8 角色侧面 =================
def elder_side(cv):
    head_side(cv, SKIN, EYE_BLUE, "smile")
    hair_side_bald(cv)
    body_side(cv, NAVY, PANTS, SHIRT, RED, "tie", chain=GOLD, leg_shorten=6)


def young_side(cv):
    head_side(cv, SKIN, EYE_BLUE, "smile")
    hair_side_short(cv, BROWN)
    body_side(cv, GREY, PANTS, SHIRT, BLUE_TIE, "tie", chain=GOLD)


def clone_side(cv):
    head_side(cv, SKIN, EYE_BLUE, "flat")
    hair_side_short(cv, DARK_BROWN)
    body_side(cv, NAVY, PANTS, SHIRT, BLUE_TIE, "tie", chain=None)


def richard_side(cv):
    head_side(cv, SKIN, EYE_BROWN, "flat")
    hair_side_part(cv, DARK_BROWN)
    body_side(cv, GREEN_SUIT, PANTS_BLACK, SHIRT, BLACK, "bowtie", chain=None)
    # 侧面胡子（上唇）
    cv.line(50, 19, 55, 19, DARK_BROWN[2])
    cv.set(52, 20, DARK_BROWN[3])
    # 侧面金边眼镜（单眼框）
    cv.ellipse(49, 15, 5, 4, GOLD[1])
    cv.set(45, 14, GOLD[1])


def boy_side(cv):
    head_side(cv, SKIN, EYE_BROWN, "frown")
    hair_side_messy(cv, BROWN)
    # 躯干（破衣，面向右：右=前胸）
    torso = [
        (40, 33), (44, 33), (47, 36), (56, 39), (57, 50),
        (56, 63), (55, 82), (48, 84), (42, 84), (40, 82),
        (38, 63), (37, 50), (38, 36),
    ]
    poly(cv, torso, RAG)
    # 胸前补丁（破衣特征）
    poly(cv, [(42, 44), (46, 44), (46, 48), (42, 48)], [RAG[0]] * 4, outline=OUT)
    cv.line(42, 44, 46, 48, RAG[3]); cv.line(46, 44, 42, 48, RAG[3])
    # 手臂（身体前侧，自然下垂）
    poly(cv, [(44, 33), (47, 36), (49, 52), (48, 78), (45, 80), (43, 52)], RAG)
    poly(cv, [(44, 78), (48, 78), (48, 83), (44, 83)], SKIN)
    # 左腿残端（截肢，后侧，打结）
    poly(cv, [(43, 84), (44, 100), (45, 106), (50, 106), (50, 100), (47, 84)], RAG)
    cv.line(44, 104, 49, 104, RAG[3])
    # 右腿（完好，前侧）
    poly(cv, [(49, 84), (50, 112), (51, 120), (56, 120), (56, 112), (54, 84)], PANTS)
    poly(cv, [(50, 120), (50, 127), (59, 127), (59, 123), (54, 120)], SHOE)
    # 拐杖（左手拄，身体后侧=屏幕左，斜撑；底部露出左后地面）
    poly(cv, [(41, 46), (44, 46), (44, 48), (41, 48)], WOOD)
    for i in range(0, 78):
        x = 42 - i * 0.12
        y = 48 + i
        cv.set(round(x), y, WOOD[1])
        cv.set(round(x) + 1, y, WOOD[2])
    poly(cv, [(31, 120), (37, 120), (37, 123), (31, 123)], WOOD)
    # 芯片（胸前）
    poly(cv, [(52, 50), (56, 50), (56, 54), (52, 54)], ICE, outline=OUT)
    cv.set(54, 52, ICE[0])


def girl_side(cv):
    head_side(cv, SKIN_PALE, EYE_BLUE, "sad")
    hair_side_ponytail(cv, ORANGE)
    # 前侧马尾（右马尾，发根在太阳穴 x54-59 y5-8，马尾垂到脸前方 x60-67，不遮额头 x51-53/眼 x49-52/鼻尖 x58）
    poly(cv, [(54, 5), (57, 6), (60, 9), (61, 14), (62, 20), (61, 26), (62, 33),
              (66, 33), (67, 24), (66, 13), (64, 8), (59, 5)], ORANGE, outline=ORANGE[3])
    dress = [
        (44, 33), (38, 36), (37, 60), (40, 90), (44, 100),
        (50, 100), (56, 90), (59, 60), (58, 36), (52, 33),
    ]
    poly(cv, dress, GIRL)
    # 白围裙（侧面，前面一层）
    poly(cv, [(41, 42), (44, 42), (48, 88), (42, 88)], APRON, outline=APRON[3])
    cv.line(41, 42, 44, 42, APRON[2])
    poly(cv, [(52, 33), (55, 40), (57, 33)], SHIRT, outline=None)
    poly(cv, [(58, 36), (62, 54), (61, 74), (57, 74), (56, 54), (55, 36)], GIRL)
    poly(cv, [(57, 72), (61, 72), (61, 76), (57, 76)], SKIN_PALE)
    # 信纸
    poly(cv, [(58, 64), (66, 64), (66, 76), (58, 76)], SHIRT, outline=OUT)
    # 腿（一条，两条腿在侧面重叠；脚尖向右）
    poly(cv, [(44, 100), (45, 108), (46, 116), (52, 116), (52, 108), (50, 100)], SKIN_PALE)
    poly(cv, [(45, 116), (45, 121), (57, 121), (57, 118), (51, 116)], GIRL)
    cv.set(38, 22, ICE[0]); cv.set(38, 23, ICE[0]); cv.set(38, 24, ICE[1])


def mech_side(cv):
    # 金属头（侧面朝右：圆顶，前侧面部=右，后脑=左）
    head = [
        (34, 4), (52, 4), (55, 8), (56, 14), (54, 20), (49, 23),
        (42, 23), (36, 20), (33, 14), (33, 8),
    ]
    poly(cv, head, METAL)
    # 发光眼带（侧面：斜条，只在前侧面部 x48-55，非横贯全宽）
    poly(cv, [(48, 12), (55, 12), (55, 16), (48, 16)], ICE, outline=None)
    cv.set(52, 14, ICE[0])
    # 脖子（金属轴，侧面，偏后）
    poly(cv, [(42, 23), (42, 29), (48, 29), (48, 23)], METAL)
    # 躯干（装甲，侧面：前胸 x56-57 凸出，后背 x33-34）
    torso = [
        (42, 29), (45, 29), (47, 33), (56, 37), (57, 50), (55, 66),
        (52, 84), (44, 84), (36, 84), (34, 66), (33, 50), (34, 37),
    ]
    poly(cv, torso, METAL)
    # 装甲分层线（侧面）
    cv.line(34, 48, 56, 48, METAL[2]); cv.line(34, 49, 56, 49, METAL[0])
    cv.line(35, 62, 54, 62, METAL[2])
    # 胸口核心灯（侧面：偏前 x46-54，中心 x50 y56）
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            if dx * dx + dy * dy <= 16:
                cv.set(50 + dx, 56 + dy, ICE[1] if dx * dx + dy * dy < 6 else ICE[0])
    cv.set(49, 55, (255, 255, 255)); cv.set(50, 55, (255, 255, 255))
    # 手臂（侧面：只一条前侧机械臂）
    poly(cv, [(45, 29), (48, 33), (50, 52), (49, 78), (46, 80), (43, 52)], METAL)
    # 线缆下半身（侧面：一组线缆从下摆垂下，偏后侧）
    colors = [ICE, GOLD, RED, BLUE_TIE, GIRL]
    for i, pal in enumerate(colors):
        x0 = 38 + i * 3
        for y in range(84, 140):
            x = x0 + round(1.5 * math.sin((y - 84) * 0.08 + i * 1.2))
            cv.set(x, y, pal[1]); cv.set(x, y + 1, pal[2])
    # 光纤束底座
    poly(cv, [(36, 82), (56, 82), (56, 86), (36, 86)], METAL)


def cube_side(cv):
    # 立方体旋转：侧面视角（左面大右面小）
    top = [(40, 32), (58, 40), (40, 48), (22, 40)]
    left = [(22, 40), (40, 48), (40, 100), (22, 92)]
    right = [(40, 48), (58, 40), (58, 92), (40, 100)]
    poly(cv, top, [(120, 120, 128), (96, 96, 104), (74, 74, 80), (56, 56, 60)])
    poly(cv, left, [(92, 92, 100), (70, 70, 78), (50, 50, 56), (36, 36, 40)])
    poly(cv, right, [(60, 60, 66), (44, 44, 50), (30, 30, 34), (22, 22, 24)])
    for p in top:
        cv.set(p[0], p[1], ICE[0])
    cv.line(22, 40, 40, 48, ICE[0]); cv.line(40, 48, 58, 40, ICE[0])
    cv.line(40, 48, 40, 100, ICE[1])
    cv.line(22, 40, 22, 92, ICE[1]); cv.line(58, 40, 58, 92, ICE[1])
    for i, y in enumerate(range(56, 98, 6)):
        for x in range(28, 56, 4):
            if (x + i) % 3 != 0:
                cv.set(x, y, ICE[2])
    for x in range(26, 60):
        cv.set(x, 106, ICE[2])


# ================= 8 角色背面 =================
def elder_back(cv):
    head_back(cv, SKIN)
    hair_back_bald(cv)
    body_back(cv, NAVY, PANTS, SHIRT, leg_shorten=6)


def young_back(cv):
    head_back(cv, SKIN)
    hair_back_full(cv, BROWN)
    body_back(cv, GREY, PANTS, SHIRT)


def clone_back(cv):
    head_back(cv, SKIN)
    hair_back_full(cv, DARK_BROWN)
    body_back(cv, NAVY, PANTS, SHIRT)


def richard_back(cv):
    head_back(cv, SKIN)
    hair_back_full(cv, DARK_BROWN)
    body_back(cv, GREEN_SUIT, PANTS_BLACK, SHIRT)


def boy_back(cv):
    head_back(cv, SKIN)
    hair_back_full(cv, BROWN)
    torso = [
        (44, 33), (36, 36), (35, 48), (37, 60), (39, 84), (44, 84),
        (52, 84), (57, 84), (59, 60), (61, 48), (60, 36), (52, 33),
    ]
    poly(cv, torso, RAG)
    cv.line(48, 35, 48, 82, RAG[3])
    poly(cv, [(40, 50), (44, 50), (44, 54), (40, 54)], [RAG[0]] * 4, outline=OUT)
    cv.line(40, 50, 44, 54, RAG[3]); cv.line(44, 50, 40, 54, RAG[3])
    poly(cv, [(36, 36), (32, 54), (33, 80), (37, 80), (38, 54), (39, 36)], RAG)
    poly(cv, [(60, 36), (64, 54), (63, 80), (59, 80), (58, 54), (57, 36)], RAG)
    # 左腿残端（背面打结，屏幕右=镜像，与正面屏幕左一致）
    poly(cv, [(49, 84), (50, 100), (51, 106), (57, 106), (57, 100), (55, 84)], RAG)
    cv.line(50, 104, 56, 104, RAG[3])
    # 右腿（完好，屏幕左=镜像）
    poly(cv, [(39, 84), (40, 102), (41, 120), (47, 120), (47, 102), (45, 84)], PANTS)
    poly(cv, [(40, 120), (40, 127), (48, 127), (48, 120)], SHOE)
    # 拐杖（左手拄，背面屏幕右=镜像，斜插身后）
    for i in range(0, 78):
        x = 56 - i * 0.06
        y = 40 + i
        cv.set(round(x), y, WOOD[1]); cv.set(round(x) + 1, y, WOOD[2])


def girl_back(cv):
    head_back(cv, SKIN_PALE)
    hair_back_ponytail(cv, ORANGE)
    # 右马尾（双马尾背面 = 左右对称）
    poly(cv, [(58, 6), (62, 10), (63, 22), (62, 32), (59, 38), (56, 38),
              (54, 32), (54, 18), (55, 10)], ORANGE, outline=ORANGE[3])
    dress = [
        (44, 33), (36, 36), (35, 60), (38, 90), (44, 100),
        (52, 100), (58, 90), (61, 60), (60, 36), (52, 33),
    ]
    poly(cv, dress, GIRL)
    # 白围裙（背面：肩带 + 腰带 + 下摆）
    poly(cv, [(40, 42), (56, 42), (58, 88), (38, 88)], APRON, outline=APRON[3])
    cv.line(42, 34, 43, 44, APRON[2]); cv.line(54, 34, 53, 44, APRON[2])
    cv.line(38, 88, 58, 88, APRON[2])
    cv.line(48, 36, 48, 98, GIRL[2])
    poly(cv, [(44, 33), (48, 37), (52, 33)], SHIRT, outline=None)
    poly(cv, [(36, 36), (32, 54), (33, 74), (37, 74), (38, 54), (39, 36)], GIRL)
    poly(cv, [(60, 36), (64, 54), (63, 74), (59, 74), (58, 54), (57, 36)], GIRL)
    poly(cv, [(40, 100), (41, 102), (42, 116), (47, 116), (47, 102), (45, 100)], SKIN_PALE)
    poly(cv, [(49, 100), (50, 102), (51, 116), (56, 116), (56, 102), (54, 100)], SKIN_PALE)
    poly(cv, [(41, 116), (41, 121), (48, 121), (48, 116)], GIRL)
    poly(cv, [(50, 116), (50, 121), (57, 121), (57, 116)], GIRL)


def mech_back(cv):
    head = [(38, 4), (54, 4), (57, 8), (57, 15), (55, 20), (50, 23),
            (42, 23), (38, 20), (36, 15), (36, 8)]
    poly(cv, head, METAL)
    cv.line(48, 6, 48, 22, METAL[2])
    poly(cv, [(44, 23), (44, 29), (52, 29), (52, 23)], METAL)
    torso = [
        (44, 29), (32, 33), (30, 50), (32, 66), (35, 84), (44, 84),
        (52, 84), (61, 84), (64, 66), (66, 50), (64, 33), (52, 29),
    ]
    poly(cv, torso, METAL)
    cv.line(48, 32, 48, 82, METAL[2])
    cv.line(32, 48, 64, 48, METAL[2])
    poly(cv, [(32, 33), (28, 50), (29, 78), (33, 78), (34, 50), (35, 33)], METAL)
    poly(cv, [(64, 33), (68, 50), (67, 78), (63, 78), (62, 50), (61, 33)], METAL)
    colors = [ICE, GOLD, RED, BLUE_TIE, GIRL]
    for i, pal in enumerate(colors):
        x0 = 34 + i * 4
        for y in range(84, 140):
            x = x0 + round(2.0 * math.sin((y - 84) * 0.08 + i * 1.2))
            cv.set(x, y, pal[1]); cv.set(x, y + 1, pal[2])
    poly(cv, [(33, 82), (63, 82), (63, 86), (33, 86)], METAL)


def cube_back(cv):
    # 立方体背面（正面左移，背面视角）
    top = [(54, 28), (78, 42), (54, 56), (30, 42)]
    left = [(30, 42), (54, 56), (54, 108), (30, 94)]
    right = [(54, 56), (78, 42), (78, 94), (54, 108)]
    poly(cv, top, [(120, 120, 128), (96, 96, 104), (74, 74, 80), (56, 56, 60)])
    poly(cv, left, [(92, 92, 100), (70, 70, 78), (50, 50, 56), (36, 36, 40)])
    poly(cv, right, [(60, 60, 66), (44, 44, 50), (30, 30, 34), (22, 22, 24)])
    for p in top:
        cv.set(p[0], p[1], ICE[0])
    cv.line(30, 42, 54, 56, ICE[0]); cv.line(54, 56, 78, 42, ICE[0])
    cv.line(54, 56, 54, 108, ICE[1])
    cv.line(30, 42, 30, 94, ICE[1]); cv.line(78, 42, 78, 94, ICE[1])
    for i, y in enumerate(range(60, 104, 6)):
        for x in range(38, 66, 4):
            if (x + i) % 3 != 0:
                cv.set(x, y, ICE[2])
    for x in range(34, 74):
        cv.set(x, 114, ICE[2])


# ================= 渲染 =================
SIDE_ROLES = [("elder", elder_side), ("young", young_side), ("clone", clone_side),
              ("richard", richard_side), ("boy", boy_side), ("girl", girl_side),
              ("mech", mech_side), ("cube", cube_side)]
BACK_ROLES = [("elder", elder_back), ("young", young_back), ("clone", clone_back),
              ("richard", richard_back), ("boy", boy_back), ("girl", girl_back),
              ("mech", mech_back), ("cube", cube_back)]


def render_all():
    from PIL import Image, ImageDraw
    HEIGHTS = {"elder": 139, "young": 145, "clone": 145, "richard": 145,
               "boy": 127, "girl": 121, "mech": 140, "cube": 112}
    BG = (24, 26, 30)
    CANVAS_H = 160
    BOTTOM_Y = 150

    def align(cv, name):
        base = cv.img  # 96×160 RGB
        dy = BOTTOM_Y - HEIGHTS[name]
        out = Image.new("RGB", (96, CANVAS_H), BG)
        out.paste(base, (0, dy))
        return out.resize((96 * 5, CANVAS_H * 5), Image.NEAREST)

    def make_sheet(roles, prefix, sheet_path, both_dirs=False):
        imgs = []
        for name, fn in roles:
            cv = Canvas(96, 160)
            fn(cv)
            img = align(cv, name)
            img.save(f"portraits/{prefix}_{name}.png")
            imgs.append((name, img))
            print(prefix, "saved", name)
            if both_dirs:
                # 朝左版本（水平翻转）
                flip = img.transpose(Image.FLIP_LEFT_RIGHT)
                flip.save(f"portraits/{prefix}_{name}_left.png")
                print(prefix, "saved", name + "_left")
        sheet = Image.new("RGB", (96 * 5 * 4, CANVAS_H * 5 * 2), BG)
        d = ImageDraw.Draw(sheet)
        for i, (name, img) in enumerate(imgs):
            r, c = i // 4, i % 4
            sheet.paste(img, (c * 96 * 5, r * CANVAS_H * 5))
            d.text((c * 96 * 5 + 8, r * CANVAS_H * 5 + 8), name, fill=(255, 255, 255))
        sheet.save(sheet_path)
        print(sheet_path, "saved")
        if both_dirs:
            sheet_l = Image.new("RGB", (96 * 5 * 4, CANVAS_H * 5 * 2), BG)
            dl = ImageDraw.Draw(sheet_l)
            for i, (name, fn) in enumerate(roles):
                cv = Canvas(96, 160)
                fn(cv)
                img = align(cv, name).transpose(Image.FLIP_LEFT_RIGHT)
                r, c = i // 4, i % 4
                sheet_l.paste(img, (c * 96 * 5, r * CANVAS_H * 5))
                dl.text((c * 96 * 5 + 8, r * CANVAS_H * 5 + 8), name + "_left", fill=(255, 255, 255))
            sheet_l.save("portraits/sides_left_sheet.png")
            print("portraits/sides_left_sheet.png saved")

    make_sheet(SIDE_ROLES, "side", "portraits/sides_sheet.png", both_dirs=True)
    make_sheet(BACK_ROLES, "back", "portraits/backs_sheet.png")


if __name__ == "__main__":
    render_all()
