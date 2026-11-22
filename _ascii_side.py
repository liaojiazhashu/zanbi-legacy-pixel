# -*- coding: utf-8 -*-
"""输出侧面立绘的纯轮廓（非背景=#），看清 S 形。逻辑坐标。"""
from PIL import Image

im = Image.open('portraits_v6/young_side.png').convert('RGB')
w, h = im.size
px = im.load()
BG = (24, 26, 34)

for ly in range(55, 291, 3):
    line = []
    for lx in range(192):
        c = px[lx * 2, ly * 2]
        line.append('#' if c != BG else '.')
    print(f"{ly:3d} {''.join(line)}")
