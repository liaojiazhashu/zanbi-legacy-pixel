# -*- coding: utf-8 -*-
"""真正的像素风引擎：字符串 art 逐像素堆砌（非几何拼凑）。

每个字符 = 一个像素 = 一种颜色。手工设计的阶梯轮廓 + 簇状明暗 + 抖动。
"""
from PIL import Image

# 每材质 4 层明暗 + 轮廓。'.' = 透明背景。
PAL_ELDER = {
    'O': (44, 36, 30),   # 轮廓
    # 皮肤 hi/mid/lo/dk
    'A': (246, 202, 168), 'B': (226, 178, 146), 'C': (196, 148, 118), 'D': (158, 112, 88),
    'x': (186, 136, 106),  # 皮肤暗线（皱纹）
    # 白发 hi/mid/lo/dk（更冷白）
    'H': (250, 248, 246), 'h': (226, 222, 216), 'i': (178, 170, 162), 'j': (122, 114, 106),
    # 眼睛
    'W': (250, 250, 250), 'E': (88, 138, 178), 'P': (40, 50, 70), 'Q': (252, 252, 255),
    'b': (120, 100, 88),   # 灰白眉
    'M': (156, 92, 78), 'm': (128, 72, 60),  # 嘴
    # 西装 hi/mid/lo/dk
    'N': (110, 130, 165), 'n': (82, 98, 132), 'l': (58, 72, 100), 'k': (36, 46, 66),
    # 衬衫
    'S': (246, 246, 246), 's': (212, 212, 216),
    # 领带
    'T': (196, 84, 92), 't': (150, 52, 58), 'r': (108, 36, 42),
    # 金怀表链
    'G': (250, 210, 120), 'g': (196, 158, 84),
    # 皮鞋
    'F': (66, 56, 50), 'f': (40, 32, 28),
}


def render(art, pal, scale=6, bg=(24, 26, 30)):
    """字符串 art → PIL Image（逐像素放置，NEAREST 放大）。"""
    rows = len(art)
    cols = max(len(r) for r in art)
    img = Image.new("RGB", (cols, rows), bg)
    px = img.load()
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch == '.' or ch == ' ':
                continue
            if ch in pal:
                px[x, y] = pal[ch]
    return img.resize((cols * scale, rows * scale), Image.NEAREST)


if __name__ == "__main__":
    # 测试：画一个最小验证块
    test = ["..OO..", ".OAAO.", "OAWWAD", ".OAAO.", "..OO.."]
    render(test, PAL_ELDER, scale=20).save("_pixel_test.png")
    print("test saved")
