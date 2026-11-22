# -*- coding: utf-8 -*-
"""精确放大参考视频角色，分析像素美术画法。"""
from PIL import Image
import glob

frames = sorted(glob.glob("_anim_frames/b*.png"))
im = Image.open(frames[12])
print("frame:", im.size)

# 角色在画面中央偏下，crop 多个候选区域放大 8 倍
candidates = {
    "center": (150, 30, 290, 210),
    "mid": (130, 20, 310, 220),
    "low": (120, 10, 320, 230),
}
for name, box in candidates.items():
    crop = im.crop(box)
    crop = crop.resize((crop.width * 8, crop.height * 8), Image.NEAREST)
    crop.save(f"_zoom_{name}.png")
    print(name, "saved", crop.size)
