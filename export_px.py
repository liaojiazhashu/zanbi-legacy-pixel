# -*- coding: utf-8 -*-
"""导出 v5 8 角色的像素数据，供 LibreSprite JS 脚本重绘。"""
import os
import sys
sys.path.insert(0, r"D:\AAAAI\动画视频尝试\赞比的遗产")
from pixel_engine import Canvas
import portrait_v5

OUT_DIR = r"D:\AAAAI\_tools\libresprite_cfg\px"
os.makedirs(OUT_DIR, exist_ok=True)
BG = (24, 26, 30)

for name, fn in portrait_v5.ROLES:
    cv = Canvas(96, 160)
    fn(cv)
    lines = []
    for y in range(160):
        for x in range(96):
            r, g, b = cv.px[x, y]
            if (r, g, b) != BG:
                lines.append(f"{x},{y},{r},{g},{b}")
    out = os.path.join(OUT_DIR, name + ".txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{name}: {len(lines)} px -> {out}")
print("done")
