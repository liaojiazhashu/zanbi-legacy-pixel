# -*- coding: utf-8 -*-
"""6 种体型 body base 的向下帧（row2 col0）并排 ASCII 对比，看身体形状差异。"""
from PIL import Image
import os

OUT = r"D:\AAAAI\动画视频尝试\赞比的遗产\lpc_layers\body"
BODIES = ["male", "female", "child", "muscular", "pregnant", "teen"]
LUM = "@%#*+=-:. "

def frame_ascii(img, col=0, row=2):
    """提取 64×64 帧，转 ASCII。透明=空格，非透明按亮度。"""
    px = img.load()
    lines = []
    for y in range(64):
        line = ""
        for x in range(64):
            r, g, b, a = px[col*64+x, row*64+y]
            if a == 0:
                line += " "
            else:
                lum = (r*299 + g*587 + b*114) // 1000
                idx = min(9, lum * 10 // 256)
                line += LUM[idx]
        lines.append(line.rstrip())
    return lines

# 只显示 bbox 区域（y30-62，x15-48）
X0, X1, Y0, Y1 = 15, 48, 30, 62
print("体型对比（向下帧，body base 光头无五官，@暗→空格亮）")
print(f"每行 6 个体型并排，x{X0}-{X1} y{Y0}-{Y1}")
print()
header = "".join(f"{b:<32}" for b in BODIES)
print(header)
print("-" * len(header))

asciis = []
for body in BODIES:
    path = os.path.join(OUT, f"body_{body}_idle.png")
    img = Image.open(path).convert("RGBA")
    asciis.append(frame_ascii(img))

for y in range(Y0, Y1+1):
    row = ""
    for a in asciis:
        line = a[y][X0:X1+1]
        row += f"{line:<32}"
    print(row)
