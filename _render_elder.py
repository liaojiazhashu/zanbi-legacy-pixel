# -*- coding: utf-8 -*-
"""用修正后的行渲染老年赞比，看效果。"""
from pixel_art import PAL_ELDER, render

rows = open("_elder_fixed.txt", encoding="utf-8").read().strip().split("\n")
ELDER = [r.strip().strip('",') for r in rows]
print("行数:", len(ELDER), "行宽:", set(len(r) for r in ELDER))

img = render(ELDER, PAL_ELDER, scale=5)
img.save("portraits/_elder_px.png")
print("saved", img.size)
