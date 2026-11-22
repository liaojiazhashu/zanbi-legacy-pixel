# -*- coding: utf-8 -*-
"""对比 6 种体型 body base 的身体比例（idle 帧，向下方向 = row2）。"""
from PIL import Image
import os

OUT = r"D:\AAAAI\动画视频尝试\赞比的遗产\lpc_layers\body"
BODIES = ["male", "female", "child", "muscular", "pregnant", "teen"]

def bbox_of(img, frame_col=0, frame_row=2):
    """提取某帧的非透明 bbox（64×64 帧）。"""
    px = img.load()
    xs = [x for x in range(64) for y in range(64) if px[frame_col*64+x, frame_row*64+y][3] > 0]
    ys = [y for y in range(64) for x in range(64) if px[frame_col*64+x, frame_row*64+y][3] > 0]
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)

print(f"{'体型':<10} {'bbox':<20} {'宽':>4} {'高':>4} {'宽高比':>6} {'说明'}")
print("-" * 70)
for body in BODIES:
    path = os.path.join(OUT, f"body_{body}_idle.png")
    img = Image.open(path).convert("RGBA")
    b = bbox_of(img)
    if b:
        x0, y0, x1, y1 = b
        w = x1 - x0 + 1
        h = y1 - y0 + 1
        ratio = w / h
        print(f"{body:<10} ({x0},{y0})-({x1},{y1}) {w:>4} {h:>4} {ratio:>6.2f}")
    else:
        print(f"{body:<10} 无内容")
