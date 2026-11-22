# -*- coding: utf-8 -*-
"""对比 6 体型 body base 的向下站立帧，理解体型差异。"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
BODY = os.path.join(ROOT, "lpc_layers", "body")
OUT = os.path.join(ROOT, "lpc_analysis")

BODY_TYPES = ["male", "female", "muscular", "pregnant", "teen", "child"]

# 向下站立帧 = col0, row2（x=0, y=128），64×64
FX, FY = 0, 128

def frame_ascii(im):
    """把 64×64 帧转成紧凑 ASCII（只取 bbox）。"""
    px = im.load()
    bbox = im.getbbox() or (0, 0, 64, 64)
    x0, y0, x1, y1 = bbox
    # 用亮度字符，透明=空格
    chars = "@%#*+=-:. "
    lines = []
    for y in range(y0, y1):
        row = []
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a < 128:
                row.append(" ")
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            idx = min(9, int(lum / 256 * 10))
            row.append(chars[idx])
        lines.append("".join(row))
    return lines, bbox

results = {}
for bt in BODY_TYPES:
    path = os.path.join(BODY, f"body_{bt}_idle.png")
    im = Image.open(path).convert("RGBA")
    frame = im.crop((FX, FY, FX + 64, FY + 64))
    lines, bbox = frame_ascii(frame)
    results[bt] = (lines, bbox)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    print(f"=== {bt}: bbox={bbox} 宽×高={w}×{h} ===")

# 并排输出（每行：6 体型的同一行）
max_h = max(len(v[0]) for v in results.values())
for row_i in range(max_h):
    parts = []
    for bt in BODY_TYPES:
        lines, bbox = results[bt]
        if row_i < len(lines):
            parts.append(lines[row_i])
        else:
            parts.append(" " * len(lines[0]))
    print("  ".join(parts))
