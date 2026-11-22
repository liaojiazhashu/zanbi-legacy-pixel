# -*- coding: utf-8 -*-
"""生成三视图总表 tri_view.png（8 角色 × 正面/侧面右/侧面左/背面，含身高差异+独特性）。"""
from PIL import Image, ImageDraw, ImageFont

names = ["elder", "young", "clone", "richard", "boy", "girl", "mech", "cube"]
labels = ["老年赞比", "青年赞比", "克隆赞比", "理查德·史密斯", "少年赞比", "女孩", "机械赞比", "立方体赞比"]

CELL_W, CELL_H = 480, 800
PAD = 24
LABEL_H = 44
COLS = 4
ROWS = len(names)

W = PAD * 2 + COLS * CELL_W + (COLS - 1) * PAD
H = PAD * 2 + ROWS * (CELL_H + LABEL_H) + (ROWS - 1) * PAD
BG = (24, 26, 30)

sheet = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(sheet)

try:
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 30)
    font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
except Exception:
    font = ImageFont.load_default()
    font_small = font

for r, (name, label) in enumerate(zip(names, labels)):
    y0 = PAD + r * (CELL_H + LABEL_H + PAD)
    # 行标签
    d.text((PAD, y0 - LABEL_H), label, fill=(255, 255, 255), font=font)
    for c, prefix in enumerate(["v5_", "side_", "side_", "back_"]):
        if c == 2:
            path = f"portraits/side_{name}_left.png"
        else:
            path = f"portraits/{prefix}{name}.png"
        try:
            img = Image.open(path).convert("RGB")
            if img.size != (CELL_W, CELL_H):
                img = img.resize((CELL_W, CELL_H), Image.NEAREST)
            x0 = PAD + c * (CELL_W + PAD)
            sheet.paste(img, (x0, y0))
        except FileNotFoundError:
            d.text((PAD + c * (CELL_W + PAD) + 8, y0 + 8), "MISSING", fill=(200, 60, 60), font=font_small)
    # 列标题（仅第一行）
    if r == 0:
        for c, title in enumerate(["正面", "侧面(右)", "侧面(左)", "背面"]):
            x0 = PAD + c * (CELL_W + PAD)
            d.text((x0 + 8, y0 + CELL_H + 6), title, fill=(180, 180, 180), font=font_small)

sheet.save("portraits/tri_view.png")
print("saved portraits/tri_view.png", sheet.size)
