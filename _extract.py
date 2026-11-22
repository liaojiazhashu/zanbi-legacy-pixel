# -*- coding: utf-8 -*-
"""提取参考视频角色的像素数据：边界框、调色板、放大图。"""
from PIL import Image
import glob
from collections import Counter

frames = sorted(glob.glob("_anim_frames/b*.png"))
im = Image.open(frames[12]).convert("RGB")
W, H = im.size
px = im.load()

# 背景是深灰渐变，角色是非背景像素。先统计颜色直方图找背景。
cnt = Counter()
for y in range(0, H, 2):
    for x in range(0, W, 2):
        cnt[px[x, y]] += 1
print("=== top colors ===")
for c, n in cnt.most_common(12):
    print(c, n)

# 找非背景像素（亮度较高或饱和度较高的像素）的边界
# 背景深灰约 (30-60)，角色有亮色。用"与背景差异大"判定。
bg = cnt.most_common(1)[0][0]
print("bg ~", bg)

minx, miny, maxx, maxy = W, H, 0, 0
for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > 60:
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
print("bbox:", minx, miny, maxx, maxy, "size", maxx - minx + 1, maxy - miny + 1)

# 角色调色板（bbox 内的颜色，排除接近背景的）
chars = Counter()
for y in range(miny, maxy + 1):
    for x in range(minx, maxx + 1):
        r, g, b = px[x, y]
        if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > 60:
            chars[(r, g, b)] += 1
print("=== character palette (%d colors) ===" % len(chars))
for c, n in chars.most_common(20):
    print(c, n)

# 放大角色区保存
crop = im.crop((minx, miny, maxx + 1, maxy + 1))
crop = crop.resize((crop.width * 10, crop.height * 10), Image.NEAREST)
crop.save("_char_zoom.png")
print("saved _char_zoom.png", crop.size)
