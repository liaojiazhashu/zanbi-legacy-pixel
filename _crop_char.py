# -*- coding: utf-8 -*-
"""精确定位 f380.png 白底角色，crop 放大到像素级。"""
from PIL import Image

im = Image.open("_ref2_frames/f380.png").convert("RGB")
W, H = im.size
px = im.load()

# 找白色面板边界（白色像素 > 200）
minx, maxx, miny, maxy = W, 0, H, 0
for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        if r > 200 and g > 200 and b > 200:
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
print(f"白色区域: x[{minx},{maxx}] y[{miny},{maxy}] 尺寸 {maxx-minx+1}x{maxy-miny+1}")

# crop 白色面板，放大 8 倍
crop = im.crop((minx, miny, maxx + 1, maxy + 1))
crop = crop.resize((crop.width * 8, crop.height * 8), Image.NEAREST)
crop.save("_ref2_char.png")
print("saved _ref2_char.png", crop.size)

# 也保存原尺寸 crop（不放大，便于看每个像素）
crop1 = im.crop((minx, miny, maxx + 1, maxy + 1))
crop1.save("_ref2_char_1x.png")
print("saved _ref2_char_1x.png", crop1.size)
