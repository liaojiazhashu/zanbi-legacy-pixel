# -*- coding: utf-8 -*-
"""提取 LPC male base 向下站立帧 → 生成 LibreSprite 复刻脚本 + 放大观察图"""
from PIL import Image
import os, json, sys
sys.stdout.reconfigure(encoding="utf-8")

D = "lpc_templates"
im = Image.open(os.path.join(D, "male_walk.png")).convert("RGBA")
# 向下方向 row=2, walk cycle 第0帧
fr = im.crop((0, 2*64, 64, 3*64))
px = fr.load()

# 收集非透明像素
pixels = []
for y in range(64):
    for x in range(64):
        r, g, b, a = px[x, y]
        if a > 0:
            pixels.append((x, y, r, g, b))

print(f"非透明像素 {len(pixels)}")

# 放大 8 倍保存观察图
big = fr.resize((64*8, 64*8), Image.NEAREST)
big.save("lpc_templates/male_base_down_frame0_x8.png")

# 生成 LibreSprite JS 脚本（无中文路径）
lines = []
lines.append("// LPC male base 向下站立帧 复刻（逐像素）")
lines.append("var spr = app.activeSprite;")
lines.append("var img = spr.layer(0).cel(0).image;")

# 调色板缓存：按 RGB 去重
pal = {}
for (x, y, r, g, b) in pixels:
    key = (r, g, b)
    if key not in pal:
        pal[key] = f"c{len(pal)}"
for (r, g, b), name in pal.items():
    lines.append(f"var {name} = app.pixelColor.rgba({r}, {g}, {b}, 255);")

for (x, y, r, g, b) in pixels:
    lines.append(f"img.putPixel({x}, {y}, {pal[(r,g,b)]});")

lines.append('spr.saveAs("D:/AAAAI/_tools/libresprite_scripts/lpc_male_base.ase", true);')
lines.append('spr.saveAs("D:/AAAAI/_tools/libresprite_scripts/lpc_male_base.png", true);')

out = "D:/AAAAI/_tools/libresprite_scripts/replicate_lpc_male.js"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"JS 脚本已生成: {out} ({len(lines)} 行, {len(pal)} 色)")
