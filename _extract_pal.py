# -*- coding: utf-8 -*-
"""提取 f380 白底角色像素数据：定位角色 bbox + 调色板统计。"""
from PIL import Image
from collections import Counter

im = Image.open("_ref2_frames/f380.png").convert("RGB")
W, H = im.size
px = im.load()

# 白色面板内，找非白像素（角色）的 bbox
minx, maxx, miny, maxy = W, 0, H, 0
colors = Counter()
for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        if not (r > 200 and g > 200 and b > 200):  # 非白
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
            colors[(r, g, b)] += 1

print(f"角色 bbox: x[{minx},{maxx}] y[{miny},{maxy}] 尺寸 {maxx-minx+1}x{maxy-miny+1}")
print(f"\n调色板（{len(colors)} 色，按频率排序）:")
for c, n in colors.most_common(30):
    print(f"  RGB{c} × {n}")

# crop 角色 bbox（含 2px 边距）放大 10 倍
pad = 2
crop = im.crop((max(0, minx - pad), max(0, miny - pad),
                min(W, maxx + 1 + pad), min(H, maxy + 1 + pad)))
crop = crop.resize((crop.width * 10, crop.height * 10), Image.NEAREST)
crop.save("_ref2_char_zoom.png")
print(f"\n角色实际尺寸: {crop.width//10}x{crop.height//10}，已放大10倍到 {crop.size}")
