# -*- coding: utf-8 -*-
"""拼图查看第二个参考视频内容（莉莉传奇僵尸战争）+ 放大角色像素。"""
from PIL import Image
import glob

frames = sorted(glob.glob("_ref2_frames/f*.png"))
print("frames:", len(frames))

# 拼图：取 12 帧（均匀分布，覆盖全片）
n = len(frames)
sel = [frames[int(i * (n - 1) / 11)] for i in range(12)]
imgs = [Image.open(f) for f in sel]
w, h = imgs[0].size
grid = Image.new("RGB", (w * 4 + 12, h * 3 + 8), (15, 15, 15))
for i, im in enumerate(imgs):
    r, c = i // 4, i % 4
    grid.paste(im, (c * (w + 2), r * (h + 2)))
grid.save("_ref2_grid.png")
print("grid:", grid.size)

# 放大一个角色帧（取中间帧，crop 中心 200x150 放大 6 倍）
im = Image.open(frames[n // 2])
crop = im.crop((120, 50, 320, 200))
crop = crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST)
crop.save("_ref2_zoom.png")
print("zoom:", crop.size)
