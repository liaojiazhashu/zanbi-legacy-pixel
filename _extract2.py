# -*- coding: utf-8 -*-
"""从参考视频帧里找背景最干净的帧，精确提取角色像素画法。"""
from PIL import Image
import glob, math
from collections import Counter

frames = sorted(glob.glob("_anim_frames/b*.png"))
print("frames:", len(frames))

def bg_score(im):
    """背景干净度：边缘像素的颜色离散度越低越干净。"""
    w, h = im.size
    px = im.load()
    # 取四角 + 顶部边缘的像素颜色
    edge = []
    for x in range(0, w, 3):
        edge.append(px[x, 0]); edge.append(px[x, h - 1])
    for y in range(0, h, 3):
        edge.append(px[0, y]); edge.append(px[w - 1, y])
    # 颜色种类数（量化到 16 级）
    q = set()
    for c in edge:
        q.add((c[0] // 16, c[1] // 16, c[2] // 16))
    return len(q)

scores = []
for f in frames:
    im = Image.open(f)
    scores.append((bg_score(im), f, im))
scores.sort()
print("=== 最干净的 6 帧（背景颜色最单一）===")
for s, f, im in scores[:6]:
    print(f"{s:3d}  {f}")
    # 统计这些帧的角落颜色
    px = im.load(); w, h = im.size
    corners = [px[0,0], px[w-1,0], px[0,h-1], px[w-1,h-1]]
    print("     corners:", corners)

# 导出最干净的帧放大
best = scores[0][2]
best = best.resize((best.width * 4, best.height * 4), Image.NEAREST)
best.save("_ref_clean_zoom.png")
print("clean frame saved:", scores[0][1])
