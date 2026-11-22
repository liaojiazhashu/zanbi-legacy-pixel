# -*- coding: utf-8 -*-
"""赞比的遗产 —— 像素 sprite 库 V2（字符串 art 手工像素 + 分层明暗 + 抖动 + 描边 + 轮廓光）

美学规范：见《像素风美学规范.md》
- 调色板：每类材质 5 层明暗（hi/light/mid/shadow/dk）+ outline，字符映射。
- 明暗：主光左上 45°；暗部向冷蓝偏移（色相偏移），亮部向暖偏移。
- 描边：主体外轮廓 1px 深色；内部结构线用暗 2 层色。
- 轮廓光：背光侧（右下）加冰青 1px rim。
- 逐帧动画：由上层（render 层）用姿势参数/多帧 art 实现。

约定：sprite 函数接受 PIL ImageDraw d + 脚底锚点 (bx,by)（y 向下），角色向上生长。
"""
from PIL import Image, ImageDraw

# ============================================================
# 调色板（字符映射 → RGB；'.' = 透明）
# ============================================================

# 老人（老年赞比 79 岁，实体）：白发 + 暖肤色 + 深蓝西装
ELDER = {
    '.': None,
    'O': (14, 20, 32),      # 描边墨黑偏蓝
    'H': (240, 244, 250),   # 发高光
    'h': (212, 220, 234),   # 发亮
    'm': (176, 186, 204),   # 发中
    's': (124, 136, 158),   # 发暗
    'F': (240, 206, 178),   # 肤高光（暖）
    'f': (216, 172, 142),   # 肤亮
    'e': (180, 136, 110),   # 肤中
    'd': (150, 120, 138),   # 肤暗（偏冷）
    'W': (242, 246, 252),   # 眼白
    'P': (64, 92, 140),     # 瞳孔蓝
    'Q': (255, 255, 255),   # 眼高光
    'B': (150, 152, 162),   # 眉灰
    'N': (170, 130, 120),   # 鼻影
    'K': (150, 108, 108),   # 嘴
    'G': (188, 194, 204),   # 胡茬灰
    'U': (116, 144, 182),   # 西服高光（藏青亮）
    'u': (84, 108, 146),    # 西服亮
    'v': (58, 76, 112),     # 西服中
    'w': (34, 46, 72),      # 西服暗
    'C': (232, 236, 242),   # 衬衫白
    'T': (150, 52, 58),     # 领带酒红
    'I': (79, 193, 224),    # 冰青轮廓光 rim
}

# 全息冰青（单色家族，用于全息投影）
HOLO = {
    '.': None,
    'O': (8, 22, 32),
    'H': (225, 250, 255),
    'h': (168, 224, 240),
    'm': (112, 178, 205),
    's': (56, 116, 145),
    'F': (200, 240, 250),
    'f': (150, 210, 228),
    'e': (104, 168, 192),
    'd': (58, 116, 142),
    'W': (220, 248, 255),
    'P': (40, 110, 150),
    'Q': (255, 255, 255),
    'B': (110, 170, 195),
    'N': (120, 160, 185),
    'K': (90, 150, 175),
    'G': (130, 190, 210),
    'U': (80, 150, 180),
    'u': (60, 120, 150),
    'v': (42, 90, 116),
    'w': (24, 58, 80),
    'C': (170, 225, 240),
    'T': (30, 80, 105),
    'I': (140, 235, 255),
}

# 少年赞比（深棕乱发 + 肤色 + 破旧棕衣补丁）
SKIN = {
    '.': None,
    'O': (36, 22, 16),
    'H': (140, 108, 84),
    'h': (104, 78, 58),
    'm': (70, 52, 38),
    's': (42, 30, 22),
    'F': (250, 216, 180),
    'f': (220, 176, 138),
    'e': (180, 138, 104),
    'd': (142, 116, 124),
    'W': (242, 246, 252),
    'P': (56, 74, 100),
    'Q': (255, 255, 255),
    'B': (120, 100, 86),
    'N': (168, 130, 118),
    'K': (150, 108, 100),
    'G': (0, 0, 0),
    'U': (150, 116, 84),
    'u': (118, 88, 62),
    'v': (84, 62, 44),
    'w': (52, 38, 28),
    'C': (196, 176, 148),
    'T': (60, 44, 32),
    'I': (79, 193, 224),
}

# 通用深发（克隆赞比/理查德深色头发）
HAIR_DARK = {
    'H': (120, 92, 74), 'h': (84, 62, 50), 'm': (54, 40, 32), 's': (30, 22, 18),
}
HAIR_GREY = {
    'H': (222, 226, 232), 'h': (168, 172, 180), 'm': (112, 118, 128), 's': (60, 64, 72),
}
SUIT_DARK = {
    'U': (92, 118, 150), 'u': (54, 74, 100), 'v': (34, 48, 68), 'w': (16, 24, 36),
}


def art_render(d, art, bx, by, pal, flip=False):
    """把字符串 art 渲染到 ImageDraw，底部对齐 (bx,by)（by 为 art 最下一行像素），水平居中 bx。"""
    rows = len(art)
    cols = len(art[0])
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch == '.' or ch == ' ':
                continue
            col = pal.get(ch)
            if col is None:
                continue
            if flip:
                xx = bx + cols - 1 - x
            else:
                xx = bx - cols // 2 + x
            d.point((xx, by - rows + 1 + y), fill=col)


def _rect(d, x0, y0, x1, y1, fill):
    """矩形（自动归一化 x0<=x1，供 facing 翻转时安全调用）。"""
    d.rectangle([min(x0, x1), y0, max(x0, x1), y1], fill=fill)


def _mouth_line(art, mouth, row=21, col=8, klen=6, open_ch='d'):
    """返回带口型的头部 art 副本。mouth 0=闭嘴 / 1=开口（嘴角 K + 中间暗色 open_ch）。"""
    if mouth <= 0:
        return art
    a = list(art)
    line = a[row]
    if klen >= 4:
        new = 'K' + open_ch * (klen - 2) + 'K'
    else:
        new = 'K' + open_ch * (klen - 1)
    a[row] = line[:col] + new + line[col + klen:]
    return a


def draw_reflection(d, fn, bx, by, h, ground_y, strength=0.22, W=640, H=360, **kwargs):
    """在角色脚下画垂直翻转的暗色倒影（镜面反射质感），返回重建后的 ImageDraw。

    原理：把角色画到临时层 → 垂直翻转 → alpha 降低到 strength → 平移到地面 ground_y，
    再用 base 图 alpha_composite 叠加。叠加后原 d 失效，故返回新 ImageDraw。
    """
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(tmp), bx, by, h=h, **kwargs)
    flip = tmp.transpose(Image.FLIP_TOP_BOTTOM)
    flip.putalpha(flip.getchannel('A').point(lambda a: int(a * strength)))
    # 平移：倒影"脚底"（翻转后原头顶 by-h）对齐 ground_y
    dy = ground_y - (H - 1 - (by - h))
    moved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    moved.paste(flip, (0, dy), flip)
    d._image.alpha_composite(moved)
    return ImageDraw.Draw(d._image)


# ============================================================
# 老人头部 art（26 宽 × 28 高）：白发 + 蓝眼 + 五官 + 下颌阴影
# ============================================================
ELDER_HEAD = [
    ".........HHHHHH.........",
    ".......HHHHHHHHHH.......",
    "......HHhhhhhhhhHH......",
    ".....HhhhhhhhhhhhhH.....",
    "....HhhhhhhhhhhhhhhH....",
    "...HhhhhhhhhhhhhhhhhH...",
    "..HhmmmmmmmmmmmmmmmmhH..",
    "..HhmffffffffffffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmffBBffffffBBffmmhH.",
    "..HhmffBBffffffBBffmmhH.",
    "..HhmffWWWffffWWWffmmhH.",
    "..HhmffWPQffffWPQffmmhH.",
    "..HhmffWWWffffWWWffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmfffffNNffffffmmhH..",
    "..HhmfffffNNffffffmmhH..",
    "..HhmffffffffffffffmmhH.",
    "..HhmfffKKKKKKfffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmddddddddddddddmmhH.",
    "...HhddddddddddddhmH....",
    "....HhddddddddddhhH.....",
    ".....HhddddddddhhhH.....",
    "......HHhhhhhhhhHH......",
]

# 老人身体 art（26 宽 × 36 高）：藏青西装翻领 + 白衬衫 V 领 + 酒红领带 + 手臂 + 裤 + 鞋
ELDER_BODY = [
    "......UUuuuuuuuuUU......",
    "....UUuuuuuuuuuuuuUU....",
    "...UuuuvvvvvvvvvvuuuuU..",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvwwvvvvvvvvwwvuuuU.",
    "..UuuvwCCvvvvvvCCwvuuuU.",
    "..UuuvwCCTvvvvTCCwvuuuU.",
    "..UuuvwCCTTvvTTCwvuuuU..",
    "..UuuvwCCTTTTTTCwvuuuU..",
    "..UuuvwCCvvTTvvCCwvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "...UuuvvvvvvvvvvvvuuuU..",
    "...UuuvvvvvvvvvvvvuuuU..",
    "...UuuvvvvvvvvvvvvuuuU..",
    "....UuuuvvvvvvvvuuuuU...",
    "....UuuuuuuuuuuuuuuuU...",
    "...UuuvvvvvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvvuuuU.",
    "...UuuvvvvvvvvvvvuuuU...",
    "...UuuvvvvvvvvvvvuuuU...",
    "....UuuuvvvvvvvvuuuU....",
    "....UuuuvvvvvvvvuuuU....",
    ".....UuuuuuuuuuuuU......",
    ".....UUuuuuuuuuuuUU.....",
    ".....wwwwwwwwwwwwww.....",
    "....wwwwwwwwwwwwwwww....",
    "...OwwwwwwwwwwwwwwwwO...",
    "...OOOOOOOOOOOOOOOOOO...",
]


def elder_front(d, bx, by, h=64, pal=ELDER, flip=False, mouth=0, bob=0):
    """正面站姿老人（白发 + 深蓝西装）。脚底 (bx,by)，头顶 by-h。
    mouth 0=闭嘴 / 1=开口（说话口型）；bob=头部上下起伏像素（呼吸/说话微动）。"""
    head = _mouth_line(ELDER_HEAD, mouth) if mouth else ELDER_HEAD
    art_render(d, head, bx, by - len(ELDER_BODY) + bob, pal, flip)
    art_render(d, ELDER_BODY, bx, by, pal, flip)


# ============================================================
# 老人侧面（facing=1 朝右；左=后脑白发，右=面部暖肤，鼻凸出）
# ============================================================
ELDER_SIDE_HEAD = [
    "......OOOOOOO.........",
    "....OOhhhhhhhO........",
    "...OhhhhhhhhhhO.......",
    "..OhhhhhhhhhhhhO......",
    "..OhhhhhhhhhhhhhO.....",
    "..OhhhhhhhhhhhhhO.....",
    "..OhhhhhhhhhhhhhO.....",
    "..OhhmmmmmmmmmmmO.....",
    "..OhhffffffffffO......",
    "..OhhffffffffffO......",
    "..OhhfffffBBBfO......",
    "..OhhfffffWWPfO......",
    "..OhhffffffffffO......",
    "..OhhffffffffffONNN...",
    "..OhhffffffffffONNNN..",
    "..OhhfffffKKffO.......",
    "..OhhfffffffffO......",
    "..OhhffffffffO.......",
    "..OhhddddddddO.......",
    "...OhhddddddddO......",
    "...OOhddddddddO......",
    "....OOhhhhhhhhhO.....",
    ".....OOOhhhhhhhO.....",
    "........................",
]

ELDER_SIDE_BODY = [
    ".....UUuuuuuuuuU.......",
    "....UUuuuuuuuuuuU......",
    "...UuuuvvvvvvvvvuU.....",
    "..UuuuvvvvvvvvvvvuuU...",
    "..UuuvvvvvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvuuuU..",
    "..UuuvCCvvvvvvvvvuuuU..",
    "..UuuvCCTvvvvvvvvvuuuU.",
    "..UuuvCCTvvvvvvvvvuuuU.",
    "..UuuvCCvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvuuuU..",
    "...UuuvvvvvvvvvvvuuuU..",
    "...UuuvvvvvvvvvvvuuuU..",
    "....UuuuvvvvvvvvuuuuU..",
    "....UuuuuuuuuuuuuuuU...",
    "...UuuvvvvvvvvvvuuuuU..",
    "..UuuvvvvvvvvvvvvuuuuU.",
    "..UuuvvvvvvvvvvvvuuuuU.",
    "..UuuvvvvvvvvvvvvuuuuU.",
    "..UuuvvvvvvvvvvvvuuuuU.",
    "..UuuvvvvvvvvvvvvuuuuU.",
    "..UuuvvvvvvvvvvvvuuuuU.",
    "..UuuvvvvvvvvvvvvuuuuU.",
    "..UuuvvvvvvvvvvvvuuuuU.",
    "...UuuvvvvvvvvvvuuuuU..",
    "...UuuvvvvvvvvvvuuuuU..",
    "....UuuuvvvvvvvuuuuuU..",
    "....UuuuvvvvvvvuuuuuU..",
    ".....UuuuuuuuuuuuuU....",
    ".....UUuuuuuuuuuuUU....",
    ".....wwwwwwwwwwwwww....",
    "....wwwwwwwwwwwwwwww...",
    "...OwwwwwwwwwwwwwwwwO..",
    "...OOOOOOOOOOOOOOOOOO..",
]


def elder_side(d, bx, by, h=64, pal=ELDER, facing=1, mouth=0, bob=0):
    """侧面站姿老人。facing=1 朝右，facing=-1 朝左（flip 镜像）。
    mouth 0=闭嘴/1=开口；bob=头部上下起伏。"""
    head = _mouth_line(ELDER_SIDE_HEAD, mouth, row=15, col=10, klen=2) if mouth else ELDER_SIDE_HEAD
    art_render(d, head, bx, by - len(ELDER_SIDE_BODY) + bob, pal, facing < 0)
    art_render(d, ELDER_SIDE_BODY, bx, by, pal, facing < 0)


# ============================================================
# 老人躺姿（卧床：枕头 + 被子隆起 + 露头肩臂 + 心电监护仪）
# ============================================================
def elder_lie(d, bx, by, pal=ELDER, facing=1, mouth=0, bob=0):
    """躺姿卧床老人：头在 bx 左侧，身体向右，被子盖到胸口。
    mouth 0=闭嘴/1=开口；bob=头部上下起伏。"""
    # 被子主体（from bx+6 到 bx+40，隆起）
    d.rectangle([bx + 6, by - 34, bx + 40, by], fill=pal['v'])
    d.rectangle([bx + 6, by - 34, bx + 40, by - 26], fill=pal['u'])  # 被子上部受光
    d.rectangle([bx + 6, by - 12, bx + 40, by], fill=pal['w'])      # 被子下部背光
    # 褶皱线
    for xx in range(bx + 12, bx + 40, 8):
        d.line([(xx, by - 30), (xx - 3, by - 4)], fill=pal['w'])
    # 头（用侧面头 art，缩小放置于枕头）
    head = _mouth_line(ELDER_SIDE_HEAD, mouth, row=15, col=10, klen=2) if mouth else ELDER_SIDE_HEAD
    art_render(d, head, bx + 12, by - 4 + bob, pal, facing < 0)
    # 露出的手臂（被子上方，向右伸出）
    d.rectangle([bx + 18, by - 26, bx + 34, by - 22], fill=pal['f'])
    d.rectangle([bx + 34, by - 26, bx + 38, by - 20], fill=pal['e'])
    # 心电监护仪（床右侧，立式小屏）
    d.rectangle([bx + 46, by - 30, bx + 58, by - 8], fill=(30, 38, 52))
    d.rectangle([bx + 48, by - 28, bx + 56, by - 14], fill=(10, 16, 24))
    d.line([(bx + 48, by - 22), (bx + 50, by - 22), (bx + 50, by - 18), (bx + 53, by - 18),
            (bx + 53, by - 24), (bx + 56, by - 24)], fill=(79, 193, 224))


# ============================================================
# 少年侧面拄拐（左腿残端悬空 + 右臂拄拐）
# ============================================================
BOY_SIDE_HEAD = [
    "......OOOOOOO.........",
    "....OOhhhhhhhO........",
    "...OhhhhhhhhhhO.......",
    "..OhhhhhhhhhhhhO......",
    "..OhhhhhhhhhhhhhO.....",
    "..OhhhhhhhhhhhhhO.....",
    "..OhhhhhhhhhhhhhO.....",
    "..OhhmmmmmmmmmmmO.....",
    "..OhhffffffffffO......",
    "..OhhffffffffffO......",
    "..OhhfffffBBBfO......",
    "..OhhfffffWWPfO......",
    "..OhhffffffffffO......",
    "..OhhffffffffffONNN...",
    "..OhhffffffffffONNNN..",
    "..OhhfffffKKffO.......",
    "..OhhfffffffffO......",
    "..OhhffffffffO.......",
    "..OhhddddddddO.......",
    "...OhhddddddddO......",
    "...OOhddddddddO......",
    "....OOhhhhhhhhhO.....",
    ".....OOOhhhhhhhO.....",
    "........................",
]

BOY_SIDE_BODY = [
    ".....UUuuuuuuuuU.......",
    "....UUuuuuuuuuuuU......",
    "...UuuvvvvvvvvvvuuU....",
    "..UuuvvvvvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvuuuU..",
    "..UuuvvCCvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvuuuU..",
    "...UuuvvvvvvvvvvvuuuU..",
    "...UuuvvvvvvvvvvvuuuU..",
    "....UuuuvvvvvvvvuuuU...",
    "....UuuuuuuuuuuuuuuU...",
    "...UuuvvvvvvvvvvvuuuU..",
    "..UuuvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvuuuU.",
    "..UuuvvvvvvvvvvvvvuuuU.",
    "...UuuvvvvvvvvvvvuuuU..",
    "...UuuvvvvvvvvvvvuuuU..",
    "....UuuuvvvvvvvvuuuU...",
    "....UuuuvvvvvvvvuuuU...",
    ".....UuuuuuuuuuuuU.....",
    ".....UUuuuuuuuuuuUU....",
    ".....wwwwwwwwwwwwww....",
    "....wwwwwwwwwwwwwwww...",
    "...OwwwwwwwwwwwwwwwwO..",
    "...OOOOOOOOOOOOOOOOOO..",
]


def boy_side(d, bx, by, h=70, pal=SKIN, facing=1, mouth=0, bob=0):
    """少年侧面拄拐：左腿残端悬空，右臂拄拐。facing=1 朝右。
    mouth 0=闭嘴/1=开口；bob=头部上下起伏。"""
    head = _mouth_line(BOY_SIDE_HEAD, mouth, row=15, col=10, klen=2) if mouth else BOY_SIDE_HEAD
    art_render(d, head, bx, by - len(BOY_SIDE_BODY) + bob, pal, facing < 0)
    art_render(d, BOY_SIDE_BODY, bx, by, pal, facing < 0)
    # 左腿残端（身体后侧，悬空，裤管卷起露残肢）
    f = facing
    # 残端裤管（短，从臀部下方，悬空）
    _rect(d, bx - 10 * f, by - 14, bx - 2 * f, by - 6, pal['v'])
    _rect(d, bx - 10 * f, by - 14, bx - 2 * f, by - 10, pal['u'])
    # 残肢（裤管末端露肤色）
    _rect(d, bx - 9 * f, by - 7, bx - 3 * f, by - 4, pal['f'])
    # 拐杖（右腋下斜向右下到地面 + 横柄）
    d.line([(bx + 6 * f, by - 30), (bx + 18 * f, by - 2)], fill=(150, 116, 84), width=2)
    d.line([(bx + 2 * f, by - 30), (bx + 10 * f, by - 31)], fill=(150, 116, 84), width=2)


# ============================================================
# 机械赞比（金属躯干 + 发光眼带 + 胸口核心灯 + 线缆下半身）
# ============================================================
MECH = {
    '.': None,
    'O': (10, 14, 22),
    'M': (150, 162, 178),   # 金属高光
    'm': (108, 120, 138),   # 金属亮
    'n': (70, 82, 100),     # 金属中
    'k': (40, 48, 62),      # 金属暗
    'I': (79, 225, 245),    # 眼带/核心灯冰青
    'i': (150, 245, 255),   # 冰青高光
    'R': (190, 70, 60),     # 红线缆
    'G': (200, 160, 70),    # 金线缆
    'Y': (110, 130, 160),   # 灰线缆
}

MECH_HEAD = [
    ".....OOOOOOOOOOOOO.....",
    "....OMMMMMMMMMMMO......",
    "....OMmmmmmmmmmmMO.....",
    "....OMmmmmmmmmmmMO.....",
    "....OMmIIIIIIIIImMO....",
    "....OMmIIIIIIIIImMO....",
    "....OMmiiiiiiiiimMO....",
    "....OMmmmmmmmmmmMO.....",
    "....OMmmmmmmmmmmMO.....",
    "....OMnnnnnnnnnnMO.....",
    "....OMnnnnnnnnnnMO.....",
    ".....OOOOOOOOOOOOO.....",
]

MECH_TORSO = [
    ".....OOOOOOOOOOOOO.....",
    "....OMMMMMMMMMMMO......",
    "....OMmmmmmmmmmmMO.....",
    "....OMmmIIIIIImmMO.....",
    "....OMmmIIIIIImmMO.....",
    "....OMmmiiiiIImmMO.....",
    "....OMmmmmmmmmmmMO.....",
    "....OMmmmmmmmmmmMO.....",
    "....OMnnnnnnnnnnMO.....",
    "....OMnnnnnnnnnnMO.....",
    ".....OOOOOOOOOOOOO.....",
]


def mech_front(d, bx, by, h=80, pal=MECH, facing=1, glow=0, bob=0):
    """机械赞比：金属躯干 + 发光眼带 + 胸口核心灯 + 线缆下半身（无腿）。
    glow 0=正常/1=发光脉冲（说话时眼带核心灯增亮）；bob=身体上下起伏。"""
    art_render(d, MECH_HEAD, bx, by - len(MECH_TORSO) - 24 + bob, pal, facing < 0)
    art_render(d, MECH_TORSO, bx, by - 24 + bob, pal, facing < 0)
    # 线缆下半身（从腰部向下散开的多条彩色线缆）
    cx = bx
    cables = [
        (cx - 8, 190, 70, 60),   # 红
        (cx - 4, 200, 160, 70),  # 金
        (cx, 110, 130, 160),     # 灰
        (cx + 4, 190, 70, 60),   # 红
        (cx + 8, 200, 160, 70),  # 金
    ]
    for i, (xx, r, g, b) in enumerate(cables):
        sway = int(3 * (1 if i % 2 == 0 else -1))
        top = by - 24 + bob
        bot = by - 2
        d.line([(xx, top), (xx + sway, (top + bot) // 2), (xx, bot)], fill=(r, g, b), width=2)
    # 发光脉冲：眼带 + 核心灯加冰青光晕
    if glow > 0:
        g = (79, 225, 245)
        ey = by - 31 + bob   # 眼带中心
        cy = by - 20 + bob   # 核心灯中心
        for dx in range(-6, 7):
            d.point((bx + dx, ey), fill=g)
            d.point((bx + dx, ey + 1), fill=g)
        for dx in range(-5, 6):
            d.point((bx + dx, cy), fill=g)
            d.point((bx + dx, cy + 1), fill=g)


# ============================================================
# 理查德（深棕分头 + 领结 + 深藏青西装）
# ============================================================
RICHARD_HEAD = [
    ".........HHHHHH.........",
    ".......HHHHHHHHHH.......",
    "......HHhhhhhhhhHH......",
    ".....HhhhhhhhhhhhhH.....",
    "....HhhhhhhhhhhhhhhH....",
    "...HhhhhhhhhhhhhhhhhH...",
    "..HhmmmmmmmmmmmmmmmmhH..",
    "..HhmffffffffffffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmffBBffffffBBffmmhH.",
    "..HhmffBBffffffBBffmmhH.",
    "..HhmffWWWffffWWWffmmhH.",
    "..HhmffWPQffffWPQffmmhH.",
    "..HhmffWWWffffWWWffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmfffffNNffffffmmhH..",
    "..HhmfffffNNffffffmmhH..",
    "..HhmffffffffffffffmmhH.",
    "..HhmfffKKKKKKfffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmffffffffffffffmmhH.",
    "..HhmddddddddddddddmmhH.",
    "...HhddddddddddddhmH....",
    "....HhddddddddddhhH.....",
    ".....HhddddddddhhhH.....",
    "......HHhhhhhhhhHH......",
]


def richard_front(d, bx, by, h=85, pal=None, facing=1, mouth=0, bob=0):
    """理查德律师：深棕分头 + 领结 + 深藏青西装。复用老人身体 art，头换深棕。
    mouth 0=闭嘴 / 1=开口；bob=头部上下起伏。"""
    if pal is None:
        pal = dict(ELDER)
        pal.update(HAIR_DARK)  # 深棕发覆盖白发字符
    head = _mouth_line(RICHARD_HEAD, mouth) if mouth else RICHARD_HEAD
    art_render(d, head, bx, by - len(ELDER_BODY) + bob, pal, facing < 0)
    # 身体复用 ELDER_BODY（领带改领结：在领口两侧画两个小方块）
    art_render(d, ELDER_BODY, bx, by, pal, facing < 0)


# ============================================================
# 女孩（侧马尾 + 浅色衣裙）
# ============================================================
GIRL = {
    '.': None,
    'O': (36, 24, 18),
    'H': (150, 108, 70),   # 深棕发高光
    'h': (112, 78, 50),
    'm': (76, 52, 34),
    's': (44, 30, 20),
    'F': (252, 222, 192),
    'f': (224, 184, 150),
    'e': (184, 144, 112),
    'd': (146, 120, 128),
    'W': (242, 246, 252),
    'P': (60, 80, 110),
    'Q': (255, 255, 255),
    'B': (130, 96, 70),
    'N': (176, 136, 120),
    'K': (190, 120, 108),
    'C': (228, 218, 202),  # 浅色衣裙
    'c': (196, 184, 168),
    'j': (156, 144, 130),
}

GIRL_HEAD = [
    "........HHHHHH..........",
    "......HHhhhhhhhhH.......",
    ".....HhhhhhhhhhhhH......",
    "....HhhhhhhhhhhhhH......",
    "...HhhhhhhhhhhhhhhH.....",
    "...HhmmmmmmmmmmmmhhH....",
    "..HhmffffffffffffmmhH...",
    "..HhmffffffffffffmmhH...",
    "..HhmffffffffffffmmhH...",
    "..HhmfBBffffffBBfmmhH...",
    "..HhmfBBffffffBBfmmhH...",
    "..HhmfWWWffffWWWfmmhH...",
    "..HhmfWPQffffWPQfmmhH...",
    "..HhmfWWWffffWWWfmmhH...",
    "..HhmffffffffffffmmhH...",
    "..HhmffffNNffffffmmhH...",
    "..HhmffffNNffffffmmhH...",
    "..HhmffffffffffffmmhH...",
    "..HhmfffKKKKfffffmmhH...",
    "..HhmffffffffffffmmhH...",
    "..HhmffffffffffffmmhH...",
    "...HhddddddddddddmmhH...",
    "....HhddddddddddhmH.....",
    ".....HHhhhhhhhhhHH......",
]

GIRL_BODY = [
    "......CCCCCCCCCC........",
    ".....CCccccccccCC.......",
    "....CCccccccccccCC......",
    "...CccccccccccccccC.....",
    "...CccccccccccccccC.....",
    "...CccccccccccccccC.....",
    "..CccccccccccccccccC....",
    "..CccccccccccccccccC....",
    "..CccccccccccccccccC....",
    ".CccccccccccccccccccC...",
    ".CccccccccccccccccccC...",
    ".CccccccccccccccccccC...",
    ".CccccccccccccccccccC...",
    ".CccccccccccccccccccC...",
    "..CccccccccccccccccC....",
    "..CccccccccccccccccC....",
    "...CccccccccccccccC.....",
    "...CccccccccccccccC.....",
    "....CccccccccccccC......",
    "....CccccccccccccC......",
    ".....CccccccccccC.......",
    ".....CCccccccccCC.......",
    "....ff...........ff.....",
    "....ff...........ff.....",
    "...fff...........fff....",
    "..fff.............fff...",
    "..ffff...........ffff...",
    "..ffff...........ffff...",
    "..ffff...........ffff...",
    ".fffff...........fffff..",
    ".fffff...........fffff..",
    "..ffffffffffffffffff....",
]


def girl_front(d, bx, by, h=65, pal=SKIN, facing=1, mouth=0, bob=0):
    """女孩：侧马尾 + 浅色衣裙。mouth 0=闭嘴/1=开口；bob=头部上下起伏。"""
    head = _mouth_line(GIRL_HEAD, mouth, row=18, col=8, klen=4) if mouth else GIRL_HEAD
    art_render(d, head, bx, by - len(GIRL_BODY) + bob, pal, facing < 0)
    art_render(d, GIRL_BODY, bx, by, pal, facing < 0)


# ============================================================
# 少年跪伏（跪地俯身，头低垂）+ 少年蹲姿（手拿芯片）
# ============================================================
def boy_kneel(d, bx, by, pal=SKIN, facing=1):
    """少年跪伏：膝盖着地，身体前倾，头低垂（雨夜母亲之死，剪影式）。"""
    f = facing
    # 头（低垂前伸，用侧面头 art 整体下移前倾）
    art_render(d, BOY_SIDE_HEAD, bx + 6 * f, by - 16, pal, f < 0)
    # 躯干（前倾的破衣）
    d.polygon([(bx - 8 * f, by - 18), (bx + 6 * f, by - 20), (bx + 4 * f, by - 4), (bx - 10 * f, by - 2)],
              fill=pal['v'])
    d.polygon([(bx - 8 * f, by - 18), (bx + 2 * f, by - 18), (bx + 0 * f, by - 8), (bx - 9 * f, by - 6)],
              fill=pal['u'])
    # 小腿（跪地，向后折叠）
    _rect(d, bx - 14 * f, by - 4, bx - 2 * f, by, pal['v'])
    # 手（撑地）
    _rect(d, bx + 2 * f, by - 3, bx + 6 * f, by, pal['f'])


def boy_squat(d, bx, by, pal=SKIN, facing=1):
    """少年蹲姿，双手在身前拿冰青发光芯片。"""
    f = facing
    # 头（略低，正视前方）
    art_render(d, BOY_SIDE_HEAD, bx, by - 30, pal, f < 0)
    # 躯干（蹲姿压缩）
    d.polygon([(bx - 10 * f, by - 26), (bx + 10 * f, by - 26), (bx + 8 * f, by - 8), (bx - 8 * f, by - 8)],
              fill=pal['v'])
    d.polygon([(bx - 10 * f, by - 26), (bx + 6 * f, by - 26), (bx + 5 * f, by - 16), (bx - 8 * f, by - 16)],
              fill=pal['u'])
    # 大腿（蹲）
    _rect(d, bx - 10 * f, by - 10, bx - 2 * f, by, pal['v'])
    _rect(d, bx + 2 * f, by - 10, bx + 10 * f, by, pal['v'])
    # 双手（身前捧芯片）
    _rect(d, bx - 2 * f, by - 16, bx + 3 * f, by - 12, pal['f'])
    # 冰青芯片（手间发光）
    d.rectangle([bx - 1, by - 16, bx + 2, by - 13], fill=(79, 225, 245))
    d.point((bx, by - 15), fill=(220, 250, 255))


def cube(d, bx, by, size=20, pal=None, glow=0):
    """黑色立方体 + 冰青边缘光。中心 (bx,by)。glow 0=正常/1=能量脉冲（说话时边缘增亮）。"""
    s = size // 2
    # 主体
    d.rectangle([bx - s, by - s, bx + s, by + s], fill=(16, 20, 28))
    # 上边缘高光
    d.rectangle([bx - s, by - s, bx + s, by - s + 1], fill=(60, 80, 100))
    # 冰青边缘光（右下）
    edge = (150, 245, 255) if glow > 0 else (79, 193, 224)
    d.line([(bx - s, by + s), (bx + s, by + s)], fill=edge)
    d.line([(bx + s, by - s), (bx + s, by + s)], fill=edge)
    # 中心微光
    d.point((bx, by), fill=edge)
    if glow > 0:
        for dx in range(-s - 2, s + 3):
            d.point((bx + dx, by - s - 1), fill=(79, 225, 245))
            d.point((bx + dx, by + s + 1), fill=(79, 225, 245))


def draw_sprite_sheet():
    """生成 sprite 测试图，存 frames_pixel/_sheet_v2.png"""
    from PIL import Image
    import os
    W, H = 640, 360
    img = Image.new("RGBA", (W, H), (12, 16, 24, 255))
    d = ImageDraw.Draw(img)
    # 背景网格（弱参考线）
    for x in range(0, W, 16):
        d.line([(x, 0), (x, H)], fill=(24, 30, 42))
    for y in range(0, H, 16):
        d.line([(0, y), (W, y)], fill=(24, 30, 42))
    # 顶行：老人三朝向 + 机械
    elder_front(d, 80, 300, pal=ELDER)
    elder_side(d, 190, 300, pal=ELDER, facing=1)
    elder_lie(d, 290, 300, pal=ELDER)
    mech_front(d, 420, 300)
    # 底行：少年侧面/蹲/跪 + 理查德 + 女孩 + 立方体
    boy_side(d, 80, 340, pal=SKIN, facing=1)
    boy_squat(d, 190, 340, pal=SKIN, facing=1)
    boy_kneel(d, 290, 340, pal=SKIN, facing=1)
    richard_front(d, 400, 340)
    girl_front(d, 500, 340, pal=GIRL)
    cube(d, 590, 340, size=24)
    # 标注
    for (x, label) in [(80, "elder_f"), (190, "elder_s"), (290, "elder_lie"), (420, "mech"),
                       (80, "boy_s"), (190, "squat"), (290, "kneel"), (400, "richard"), (500, "girl"), (590, "cube")]:
        pass
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames_pixel", "_sheet_v2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out)
    print("saved", out)


if __name__ == "__main__":
    draw_sprite_sheet()
