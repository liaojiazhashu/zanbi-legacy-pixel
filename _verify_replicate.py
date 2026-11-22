# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image

a = Image.open("D:/AAAAI/_tools/libresprite_scripts/lpc_male_base.png").convert("RGBA")
b = Image.open("D:/AAAAI/动画视频尝试/赞比的遗产/lpc_templates/male_walk.png").convert("RGBA").crop((0, 128, 64, 192))
pa, pb = a.load(), b.load()
diff = 0
for y in range(64):
    for x in range(64):
        if pa[x, y] != pb[x, y]:
            diff += 1
print("复刻 size", a.size, "原帧 size", b.size)
print("不同像素数:", diff, "（0 = 完全一致）")
