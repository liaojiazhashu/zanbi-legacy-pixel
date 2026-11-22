# -*- coding: utf-8 -*-
"""《赞比的遗产》8 角色像素立绘 —— 程序化像素美术（96×160）。

统一角色框架：椭圆脸 + 4 层明暗 + 抖动 + 服装细节。
"""
from pixel_engine import Canvas, upscale

OUTLINE = (44, 36, 30)
SKIN = [(246, 202, 168), (226, 178, 146), (196, 148, 118), (158, 112, 88)]
EYE_W = (250, 250, 250)
IRIS = (88, 138, 178)
PUPIL = (40, 50, 70)

WHITE_HAIR = [(250, 248, 246), (226, 222, 216), (178, 170, 162), (122, 114, 106)]
BROWN_HAIR = [(120, 82, 56), (96, 62, 42), (70, 44, 30), (46, 28, 20)]
NAVY = [(110, 130, 165), (82, 98, 132), (58, 72, 100), (36, 46, 66)]
GREY = [(150, 152, 158), (118, 120, 128), (86, 88, 98), (56, 58, 66)]
BLACK = [(110, 110, 116), (82, 82, 90), (58, 58, 66), (36, 36, 42)]
SHIRT = (246, 246, 246)
SHIRT_LO = (200, 200, 206)
RED_TIE = [(196, 84, 92), (150, 52, 58), (108, 36, 42)]
BLUE_TIE = [(90, 140, 190), (60, 100, 150), (40, 70, 110)]
BLACK_TIE = [(70, 70, 76), (46, 46, 52), (30, 30, 36)]
GOLD = [(250, 210, 120), (196, 158, 84)]
SILVER = [(220, 224, 230), (170, 176, 184)]


def draw_head(cv, cx, cy, hair, hair_style, wrinkles, mouth, eye_col=IRIS):
    """通用头部：椭圆脸 + 发型 + 五官。hair_style: bald/short/part/clone"""
    # 后脑+两侧头发
    cv.ellipse_shaded(cx, cy - 4, 29, 34, hair)
    # 脸
    cv.ellipse_shaded(cx, cy + 3, 24, 30, SKIN, OUTLINE)

    if hair_style == 'bald':
        # 秃顶：两侧+后脑白发，顶部露皮肤
        cv.fill(cx - 21, cy - 28, cx - 12, cy - 21, hair[1])
        cv.fill(cx + 12, cy - 28, cx + 21, cy - 21, hair[1])
        cv.fill(cx - 7, cy - 31, cx + 7, cy - 25, hair[2])
    elif hair_style == 'short':
        # 整齐短发：顶部全覆盖
        cv.fill(cx - 24, cy - 32, cx + 24, cy - 22, hair[1])
        cv.fill(cx - 26, cy - 30, cx + 26, cy - 26, hair[0])
        cv.fill(cx - 20, cy - 24, cx + 20, cy - 20, hair[1])
    elif hair_style == 'part':
        # 三七分
        cv.fill(cx - 24, cy - 32, cx + 24, cy - 22, hair[1])
        cv.fill(cx - 26, cy - 30, cx + 26, cy - 26, hair[0])
        cv.line(cx - 8, cy - 32, cx - 4, cy - 20, hair[3])  # 发缝
        cv.fill(cx - 4, cy - 30, cx + 4, cy - 20, hair[2])
    else:
        cv.fill(cx - 24, cy - 32, cx + 24, cy - 22, hair[1])
        cv.fill(cx - 26, cy - 30, cx + 26, cy - 26, hair[0])

    # 耳
    cv.ellipse_shaded(cx - 25, cy + 2, 4, 6, SKIN, OUTLINE)
    cv.ellipse_shaded(cx + 25, cy + 2, 4, 6, SKIN, OUTLINE)

    # 皱纹
    if wrinkles:
        for i in range(3):
            y = cy - 8 + i * 4
            cv.line(cx - 12, y, cx + 12, y, (200, 160, 130))
        cv.line(cx - 20, cy + 8, cx - 15, cy + 10, (200, 160, 130))
        cv.line(cx + 20, cy + 8, cx + 15, cy + 10, (200, 160, 130))

    # 眉毛
    brow = hair[3] if wrinkles else hair[2]
    cv.line(cx - 15, cy - 6, cx - 3, cy - 3, brow)
    cv.line(cx + 15, cy - 6, cx + 3, cy - 3, brow)

    # 眼睛
    for ex in (cx - 9, cx + 9):
        cv.ellipse(ex, cy + 1, 3, 4, eye_col)
        cv.ellipse(ex, cy + 1, 1, 2, PUPIL)
        cv.set(ex + 1, cy - 1, (252, 252, 255))
        cv.line(ex - 4, cy - 3, ex + 4, cy - 3, OUTLINE)
        cv.line(ex - 4, cy - 2, ex + 4, cy - 2, OUTLINE)
        cv.line(ex - 4, cy + 5, ex + 4, cy + 5, SKIN[3])
        cv.set(ex - 3, cy + 1, EYE_W)
        cv.set(ex + 3, cy + 1, EYE_W)

    # 鼻子
    cv.line(cx, cy + 2, cx - 2, cy + 10, SKIN[2])
    cv.line(cx, cy + 2, cx + 2, cy + 10, SKIN[3])
    cv.line(cx - 2, cy + 10, cx + 2, cy + 10, SKIN[3])
    cv.set(cx, cy + 11, SKIN[3])

    # 嘴
    if mouth == 'smile':
        cv.line(cx - 8, cy + 17, cx, cy + 20, (156, 92, 78))
        cv.line(cx, cy + 20, cx + 8, cy + 17, (156, 92, 78))
    elif mouth == 'flat':
        cv.line(cx - 6, cy + 18, cx + 6, cy + 18, (128, 72, 60))
    elif mouth == 'frown':
        cv.line(cx - 8, cy + 19, cx, cy + 17, (156, 92, 78))
        cv.line(cx, cy + 17, cx + 8, cy + 19, (156, 92, 78))


def draw_suit_body(cv, bx, by, suit, tie, tie_color, chain, chain_color):
    """通用西装身体：翻领+衬衫+领带+纽扣+褶皱+手臂+裤+鞋"""
    # 躯干
    cv.rect_shaded(bx - 28, by, bx + 28, by + 62, suit, OUTLINE)
    # 翻领
    for i in range(12):
        cv.line(bx - 20 + i, by, bx - 8, by + 22 + i, suit[0] if i < 6 else suit[1])
        cv.line(bx + 20 - i, by, bx + 8, by + 22 + i, suit[2] if i < 6 else suit[3])
    # 衬衫 V 领
    cv.fill(bx - 8, by + 3, bx + 8, by + 18, SHIRT)
    cv.line(bx - 10, by + 2, bx, by + 20, SHIRT_LO)
    cv.line(bx + 10, by + 2, bx, by + 20, SHIRT_LO)
    # 领带/领结
    if tie == 'necktie':
        cv.fill(bx - 3, by + 3, bx + 3, by + 18, tie_color[1])
        cv.fill(bx - 2, by + 3, bx + 2, by + 12, tie_color[0])
        cv.fill(bx - 2, by + 19, bx + 2, by + 40, tie_color[1])
        cv.fill(bx - 2, by + 19, bx + 2, by + 30, tie_color[0])
        cv.fill(bx - 3, by + 16, bx + 3, by + 21, tie_color[2])
    elif tie == 'bowtie':
        cv.fill(bx - 5, by + 16, bx + 5, by + 19, tie_color[1])
        cv.fill(bx - 6, by + 17, bx + 6, by + 18, tie_color[0])
        cv.fill(bx - 1, by + 16, bx + 1, by + 19, tie_color[2])
    # 纽扣
    cv.set(bx - 10, by + 26, chain_color[1]); cv.set(bx + 10, by + 26, chain_color[1])
    cv.set(bx - 10, by + 40, chain_color[1]); cv.set(bx + 10, by + 40, chain_color[1])
    # 怀表链/胸针
    if chain:
        for i in range(10):
            x = bx - 16 + i * 2
            y = by + 44 - int((i - 5) ** 2 / 3)
            cv.set(x, y, chain_color[0])
            cv.set(x, y + 1, chain_color[1])
    # 口袋
    cv.line(bx - 20, by + 42, bx - 8, by + 42, suit[3])
    cv.line(bx - 20, by + 42, bx - 20, by + 50, suit[3])
    cv.line(bx - 20, by + 50, bx - 8, by + 50, suit[3])
    # 褶皱线
    for i in range(5):
        cv.line(bx - 22, by + 30 + i * 6, bx - 14, by + 34 + i * 6, suit[3])
    for i in range(5):
        cv.line(bx + 14, by + 30 + i * 6, bx + 22, by + 34 + i * 6, suit[3])
    # 手臂
    cv.rect_shaded(bx - 32, by + 4, bx - 24, by + 50, suit, OUTLINE)
    cv.rect_shaded(bx + 24, by + 4, bx + 32, by + 50, suit, OUTLINE)
    cv.ellipse_shaded(bx - 28, by + 53, 5, 4, SKIN, OUTLINE)
    cv.ellipse_shaded(bx + 28, by + 53, 5, 4, SKIN, OUTLINE)
    # 裤+鞋
    cv.fill(bx - 14, by + 62, bx - 2, by + 84, suit[2])
    cv.fill(bx + 2, by + 62, bx + 14, by + 84, suit[3])
    cv.line(bx - 14, by + 62, bx - 2, by + 84, suit[1])
    cv.line(bx + 14, by + 62, bx + 2, by + 84, suit[3])
    cv.line(bx, by + 62, bx, by + 84, OUTLINE)
    cv.fill(bx - 18, by + 84, bx - 2, by + 90, (66, 56, 50))
    cv.fill(bx + 2, by + 84, bx + 18, by + 90, (40, 32, 28))
    cv.fill(bx - 16, by + 84, bx - 4, by + 88, (90, 78, 70))


def draw_man(cv, *, hair, hair_style, wrinkles, mouth, suit, tie, tie_color, chain, chain_color):
    cx, cy = 48, 42
    draw_head(cv, cx, cy, hair, hair_style, wrinkles, mouth)
    # 脖子
    cv.fill(cx - 8, cy + 30, cx + 8, cy + 42, SKIN[1])
    cv.rect_shaded(cx - 9, cy + 30, cx + 9, cy + 40, SKIN, OUTLINE)
    draw_suit_body(cv, cx, cy + 42, suit, tie, tie_color, chain, chain_color)


# ===== 特殊角色 =====
RAG = [(150, 112, 80), (116, 82, 56), (86, 58, 38), (58, 38, 26)]
WOOD = [(196, 150, 96), (158, 116, 72), (118, 84, 50)]
CHIP = (140, 230, 180)
ORANGE = [(240, 150, 70), (205, 116, 48), (160, 84, 32), (120, 60, 24)]
PINK = [(240, 180, 190), (210, 140, 155), (170, 104, 120), (130, 74, 90)]
METAL = [(200, 206, 214), (156, 162, 172), (116, 122, 132), (78, 84, 94)]
ICE = (150, 240, 255)
ICE_LT = (220, 252, 255)


def draw_boy(cv):
    cx, cy = 48, 42
    draw_head(cv, cx, cy, BROWN_HAIR, 'short', False, 'flat')
    # 乱发翘起
    cv.fill(cx - 14, cy - 34, cx - 8, cy - 30, BROWN_HAIR[1])
    cv.fill(cx + 4, cy - 35, cx + 10, cy - 31, BROWN_HAIR[0])
    cv.fill(cx - 3, cy - 37, cx + 3, cy - 32, BROWN_HAIR[0])
    # 脖子
    cv.fill(cx - 8, cy + 30, cx + 8, cy + 42, SKIN[1])
    cv.rect_shaded(cx - 9, cy + 30, cx + 9, cy + 40, SKIN, OUTLINE)
    # 破衣（遮肩）
    by = cy + 42
    cv.rect_shaded(cx - 24, by, cx + 24, by + 52, RAG, OUTLINE)
    # 补丁
    cv.fill(cx - 19, by + 8, cx - 11, by + 18, (178, 142, 100))
    cv.line(cx - 19, by + 8, cx - 11, by + 18, (120, 90, 60))
    cv.line(cx - 11, by + 8, cx - 19, by + 18, (120, 90, 60))
    # 芯片（左胸，绿色）
    cv.fill(cx - 6, by + 12, cx - 1, by + 18, CHIP)
    cv.set(cx - 4, by + 14, (220, 255, 235))
    # 手臂
    cv.rect_shaded(cx - 28, by + 4, cx - 20, by + 40, RAG, OUTLINE)
    cv.rect_shaded(cx + 20, by + 4, cx + 28, by + 40, RAG, OUTLINE)
    cv.ellipse_shaded(cx - 24, by + 43, 5, 4, SKIN, OUTLINE)
    cv.ellipse_shaded(cx + 24, by + 43, 5, 4, SKIN, OUTLINE)
    # 左腿残端（裤管到膝盖打结）
    cv.fill(cx - 12, by + 52, cx - 2, by + 68, RAG[2])
    cv.fill(cx - 12, by + 66, cx - 2, by + 70, RAG[3])
    cv.line(cx - 12, by + 68, cx - 2, by + 68, OUTLINE)
    # 右腿完整 + 鞋
    cv.fill(cx + 2, by + 52, cx + 12, by + 84, RAG[3])
    cv.fill(cx + 2, by + 52, cx + 12, by + 70, RAG[2])
    cv.fill(cx + 2, by + 84, cx + 14, by + 90, (40, 32, 28))
    # 木拐杖（右腋下斜到右下）
    for i in range(42):
        cv.set(cx + 21 - i // 7, by + 2 + i, WOOD[0] if i % 4 else WOOD[1])
        cv.set(cx + 22 - i // 7, by + 2 + i, WOOD[1])
    cv.fill(cx + 14, by + 2, cx + 24, by + 5, WOOD[1])


def draw_girl(cv):
    cx, cy = 48, 42
    # 头
    cv.ellipse_shaded(cx, cy + 3, 22, 28, SKIN, OUTLINE)
    # 橙发（顶部+右侧马尾）
    cv.fill(cx - 22, cy - 28, cx + 22, cy - 20, ORANGE[1])
    cv.fill(cx - 24, cy - 26, cx + 24, cy - 22, ORANGE[0])
    cv.fill(cx + 20, cy - 22, cx + 29, cy + 18, ORANGE[1])
    cv.fill(cx + 22, cy - 20, cx + 27, cy + 16, ORANGE[0])
    cv.fill(cx + 26, cy + 16, cx + 31, cy + 22, ORANGE[2])
    cv.fill(cx + 27, cy + 18, cx + 30, cy + 21, ORANGE[1])
    # 耳
    cv.ellipse_shaded(cx - 23, cy + 2, 3, 5, SKIN, OUTLINE)
    # 眼睛（大眼）
    for ex in (cx - 8, cx + 8):
        cv.ellipse(ex, cy + 1, 3, 4, IRIS)
        cv.ellipse(ex, cy + 1, 1, 2, PUPIL)
        cv.set(ex + 1, cy - 1, (252, 252, 255))
        cv.line(ex - 4, cy - 3, ex + 4, cy - 3, OUTLINE)
        cv.line(ex - 4, cy - 2, ex + 4, cy - 2, OUTLINE)
        cv.set(ex - 3, cy + 1, EYE_W)
        cv.set(ex + 3, cy + 1, EYE_W)
    # 泪珠（左眼下）
    cv.fill(cx - 9, cy + 6, cx - 7, cy + 10, (130, 200, 255))
    cv.set(cx - 8, cy + 7, (220, 250, 255))
    # 鼻子
    cv.set(cx, cy + 5, SKIN[2])
    cv.set(cx, cy + 6, SKIN[3])
    # 嘴（微笑）
    cv.line(cx - 5, cy + 12, cx, cy + 14, (180, 100, 100))
    cv.line(cx, cy + 14, cx + 5, cy + 12, (180, 100, 100))
    # 脖子
    cv.fill(cx - 6, cy + 27, cx + 6, cy + 38, SKIN[1])
    cv.rect_shaded(cx - 7, cy + 27, cx + 7, cy + 36, SKIN, OUTLINE)
    # 粉裙（A 字）
    by = cy + 38
    cv.rect_shaded(cx - 16, by, cx + 16, by + 22, PINK, OUTLINE)
    # 白领
    cv.fill(cx - 8, by, cx + 8, by + 4, SHIRT)
    cv.line(cx - 8, by, cx, by + 6, SHIRT_LO)
    cv.line(cx + 8, by, cx, by + 6, SHIRT_LO)
    # 裙摆展开
    cv.rect_shaded(cx - 20, by + 22, cx + 20, by + 44, PINK, OUTLINE)
    for i in range(5):
        cv.line(cx - 18 + i * 2, by + 24, cx - 14 + i * 2, by + 44, PINK[3])
        cv.line(cx + 18 - i * 2, by + 24, cx + 14 - i * 2, by + 44, PINK[3])
    # 手臂
    cv.rect_shaded(cx - 20, by + 4, cx - 14, by + 20, PINK, OUTLINE)
    cv.rect_shaded(cx + 14, by + 4, cx + 20, by + 20, PINK, OUTLINE)
    cv.ellipse_shaded(cx - 17, by + 22, 4, 3, SKIN, OUTLINE)
    cv.ellipse_shaded(cx + 17, by + 22, 4, 3, SKIN, OUTLINE)
    # 信纸（手拿，白色小方块）
    cv.fill(cx - 12, by + 20, cx - 4, by + 28, (245, 245, 245))
    cv.line(cx - 12, by + 20, cx - 4, by + 28, (180, 180, 185))
    cv.line(cx - 4, by + 20, cx - 12, by + 28, (180, 180, 185))
    cv.line(cx - 11, by + 22, cx - 5, by + 22, (150, 150, 160))
    cv.line(cx - 11, by + 25, cx - 5, by + 25, (150, 150, 160))
    # 腿+鞋
    cv.fill(cx - 8, by + 44, cx - 1, by + 70, SKIN[2])
    cv.fill(cx + 1, by + 44, cx + 8, by + 70, SKIN[3])
    cv.fill(cx - 10, by + 70, cx - 1, by + 76, (180, 120, 140))
    cv.fill(cx + 1, by + 70, cx + 10, by + 76, (150, 90, 110))


def draw_mech(cv):
    cx, cy = 48, 40
    # 金属头
    cv.ellipse_shaded(cx, cy, 24, 27, METAL, OUTLINE)
    # 冰青发光眼带（横条）
    cv.fill(cx - 16, cy - 2, cx + 16, cy + 4, ICE)
    cv.fill(cx - 12, cy - 1, cx + 12, cy + 2, ICE_LT)
    cv.set(cx - 14, cy, (255, 255, 255)); cv.set(cx + 14, cy, (255, 255, 255))
    # 金属颈
    cv.fill(cx - 8, cy + 27, cx + 8, cy + 36, METAL[2])
    # 躯干（装甲）
    by = cy + 36
    cv.rect_shaded(cx - 24, by, cx + 24, by + 48, METAL, OUTLINE)
    # 装甲分层线
    for i in range(3):
        cv.line(cx - 20, by + 8 + i * 12, cx + 20, by + 8 + i * 12, METAL[3])
        cv.line(cx - 20, by + 9 + i * 12, cx + 20, by + 9 + i * 12, METAL[0])
    # 胸口核心灯（发光圆）
    cv.ellipse(cx, by + 18, 7, 7, ICE)
    cv.ellipse(cx, by + 18, 4, 4, ICE_LT)
    cv.set(cx - 1, by + 16, (255, 255, 255))
    # 肩甲
    cv.rect_shaded(cx - 30, by, cx - 22, by + 12, METAL, OUTLINE)
    cv.rect_shaded(cx + 22, by, cx + 30, by + 12, METAL, OUTLINE)
    # 手臂
    cv.rect_shaded(cx - 28, by + 12, cx - 20, by + 44, METAL, OUTLINE)
    cv.rect_shaded(cx + 20, by + 12, cx + 28, by + 44, METAL, OUTLINE)
    # 彩色线缆下半身
    cols = [(232, 92, 92), (92, 140, 232), (92, 200, 120), (232, 200, 92), (200, 120, 232)]
    for i, col in enumerate(cols):
        x0 = cx - 14 + i * 6
        for j in range(46):
            x = x0 + (j % 5 - 2 if j % 7 < 4 else 2 - j % 5)
            cv.set(x, by + 48 + j, col)
            if j % 9 == 0:
                cv.set(x, by + 48 + j, ICE_LT)


def draw_cube(cv):
    # 等距立方体（顶面亮+前面中+右面暗+冰青边）
    cx, cy = 48, 78
    # 前面（正方形，中灰）
    cv.fill(cx - 20, cy - 4, cx + 20, cy + 40, (56, 60, 68))
    # 顶面（平行四边形，亮灰）
    for i in range(14):
        cv.line(cx - 20 + i, cy - 4 - i // 2, cx + 20 + i, cy - 4 - i // 2, (80, 84, 92))
    # 右面（平行四边形，暗灰）
    for i in range(14):
        cv.line(cx + 20, cy - 4 + i, cx + 20 + (14 - i), cy - 4 - 7 + i + 7, (40, 44, 50))
    # 冰青边
    cv.line(cx - 20, cy - 4, cx + 20, cy - 4, ICE)
    cv.line(cx - 20, cy - 4, cx - 20, cy + 40, ICE)
    cv.line(cx - 20, cy + 40, cx + 20, cy + 40, ICE)
    cv.line(cx + 20, cy - 4, cx + 20, cy + 40, ICE)
    # 顶面边
    cv.line(cx - 20, cy - 4, cx - 6, cy - 11, ICE)
    cv.line(cx + 20, cy - 4, cx + 34, cy - 11, ICE)
    cv.line(cx - 6, cy - 11, cx + 34, cy - 11, ICE)
    # 右面边
    cv.line(cx + 20, cy + 40, cx + 34, cy + 33, ICE)
    cv.line(cx + 34, cy - 11, cx + 34, cy + 33, ICE)
    # 内部光晕
    cv.ellipse(cx, cy + 40, 24, 3, ICE)
    cv.ellipse(cx, cy + 40, 12, 2, ICE_LT)


if __name__ == "__main__":
    suits = [
        ('elder', dict(hair=WHITE_HAIR, hair_style='bald', wrinkles=True, mouth='smile',
                       suit=NAVY, tie='necktie', tie_color=RED_TIE, chain=True, chain_color=GOLD)),
        ('young', dict(hair=BROWN_HAIR, hair_style='short', wrinkles=False, mouth='smile',
                       suit=GREY, tie='necktie', tie_color=BLUE_TIE, chain=True, chain_color=SILVER)),
        ('clone', dict(hair=BROWN_HAIR, hair_style='short', wrinkles=False, mouth='flat',
                       suit=NAVY, tie='necktie', tie_color=BLUE_TIE, chain=True, chain_color=SILVER)),
        ('richard', dict(hair=BROWN_HAIR, hair_style='part', wrinkles=False, mouth='flat',
                        suit=BLACK, tie='bowtie', tie_color=BLACK_TIE, chain=True, chain_color=SILVER)),
    ]
    specials = [
        ('boy', draw_boy),
        ('mech', draw_mech),
        ('cube', draw_cube),
        ('girl', draw_girl),
    ]
    imgs = []
    for name, kw in suits:
        cv = Canvas(96, 160)
        draw_man(cv, **kw)
        im = upscale(cv, 4)
        im.save(f"portraits/v3_{name}.png")
        imgs.append((name, im))
        print(name, "OK", im.size)
    for name, fn in specials:
        cv = Canvas(96, 160)
        fn(cv)
        im = upscale(cv, 4)
        im.save(f"portraits/v3_{name}.png")
        imgs.append((name, im))
        print(name, "OK", im.size)

    # 合集 4x2
    from PIL import Image
    w, h = imgs[0][1].size
    sheet = Image.new("RGB", (w * 4 + 50, h * 2 + 30), (40, 40, 44))
    for i, (name, im) in enumerate(imgs):
        r, c = i // 4, i % 4
        sheet.paste(im, (10 + c * (w + 10), 10 + r * (h + 10)))
    sheet.save("portraits/_v3_all_sheet.png")
    print("sheet saved", sheet.size)
