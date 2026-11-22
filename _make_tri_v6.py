# -*- coding: utf-8 -*-
"""拼接 8 角色三视图总表：正面/侧面/背面 × 8 角色。"""
from PIL import Image, ImageDraw, ImageFont

BG = (24, 26, 34)
ROLES = [
    ("elder", "老年赞比"),
    ("young", "青年赞比"),
    ("clone", "克隆赞比"),
    ("richard", "理查德·史密斯"),
    ("boy", "少年赞比"),
    ("girl", "女孩"),
    ("mech", "机械赞比"),
    ("cube", "立方体赞比"),
]
COLS = ["正面", "侧面", "背面"]


def main():
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 30)
    font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
    img_w, img_h = 384, 640
    label_w = 220
    header_h = 60
    gap = 12
    # 每个角色：一行 [角色名 | 正面 | 侧面 | 背面]
    cell_h = img_h + gap
    total_w = label_w + 3 * (img_w + gap) + gap
    total_h = header_h + 8 * cell_h + gap
    sheet = Image.new("RGB", (total_w, total_h), BG)
    d = ImageDraw.Draw(sheet)
    # 表头
    for j, name in enumerate(COLS):
        x = label_w + gap + j * (img_w + gap) + img_w // 2
        bbox = d.textbbox((0, 0), name, font=font)
        d.text((x - (bbox[2] - bbox[0]) // 2, 14), name, font=font, fill=(200, 200, 210))
    for i, (name, label) in enumerate(ROLES):
        y0 = header_h + i * cell_h
        # 角色名
        d.text((20, y0 + img_h // 2 - 15), label, font=font, fill=(230, 230, 240))
        # 三视图
        for j, suffix in enumerate(["", "_side", "_back"]):
            path = f"portraits_v6/{name}{suffix}.png"
            im = Image.open(path)
            x = label_w + gap + j * (img_w + gap)
            sheet.paste(im, (x, y0))
    sheet.save("portraits_v6/tri_view.png")
    print("tri_view saved", sheet.size)


if __name__ == "__main__":
    main()
