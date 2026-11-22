# -*- coding: utf-8 -*-
"""精确提取参考视频角色的像素：分离深灰渐变背景，提取前景角色。"""
from PIL import Image

im = Image.open("_anim_frames/b008.png").convert("RGB")
w, h = im.size
px = im.load()

# 背景是深灰渐变 (53,53,53)->(28,28,28)，接近无色（R≈G≈B）
# 角色有彩色（银盔偏白但带蓝、蓝披风、金色装饰）
def is_bg(c):
    r, g, b = c
    # 无色（R≈G≈B）且偏暗 → 背景
    spread = max(r, g, b) - min(r, g, b)
    return spread < 18 and r < 90

# 找前景 bounding box
minx, miny, maxx, maxy = w, h, 0, 0
for y in range(h):
    for x in range(w):
        if not is_bg(px[x, y]):
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
print(f"角色 bounding box: x[{minx},{maxx}] y[{miny},{maxy}] 宽{maxx-minx+1} 高{maxy-miny+1}")

# 提取角色（背景设透明）
crop = im.crop((minx, miny, maxx + 1, maxy + 1))
out = Image.new("RGBA", crop.size, (0, 0, 0, 0))
opx = out.load()
for y in range(crop.size[1]):
    for x in range(crop.size[0]):
        c = crop.getpixel((x, y))
        if not is_bg(c):
            opx[x, y] = (*c, 255)
out.save("_ref_sprite_extract.png")
print("sprite 尺寸:", out.size)

# 放大 4 倍查看
zoom = out.resize((out.width * 4, out.height * 4), Image.NEAREST)
zoom.save("_ref_sprite_zoom.png")
print("zoom saved")

# 统计角色的调色板（量化）
from collections import Counter
cnt = Counter()
for y in range(crop.size[1]):
    for x in range(crop.size[0]):
        c = crop.getpixel((x, y))
        if not is_bg(c):
            q = (c[0] // 24 * 24, c[1] // 24 * 24, c[2] // 24 * 24)
            cnt[q] += 1
print("=== 调色板（量化到 24 级，前 20）===")
for color, n in cnt.most_common(20):
    print(f"  RGB{color}  x{n}")
