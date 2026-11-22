# -*- coding: utf-8 -*-
"""LPC base 帧 ASCII 可视化：按亮度层打印像素，理解明暗簇状分布与轮廓"""
from PIL import Image
import os, sys
sys.stdout.reconfigure(encoding="utf-8")

D = "lpc_templates"
im = Image.open(os.path.join(D, "male_walk.png")).convert("RGBA")
fr = im.crop((0, 2*64, 64, 3*64))
px = fr.load()

# 亮度分层：把 RGB 映射到字符（描边最暗→高光最亮）
def ch(r, g, b, a):
    if a == 0:
        return " "
    lum = (r + g + b) / 3
    if lum < 50: return "#"   # 描边
    if lum < 120: return "@"  # 最暗肤色
    if lum < 160: return "o"  # 暗肤色
    if lum < 195: return "="  # 中肤色（主）
    if lum < 230: return "."  # 亮肤色
    return ":"                # 高光

# 只打印 bbox 区域
xs = [x for y in range(64) for x in range(64) if px[x, y][3] > 0]
ys = [y for y in range(64) for x in range(64) if px[x, y][3] > 0]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
print(f"bbox x[{x0},{x1}] y[{y0},{y1}]\n")
for y in range(y0, y1 + 1):
    row = "".join(ch(*px[x, y]) for x in range(x0, x1 + 1))
    print(f"{y:2d} {row}")
