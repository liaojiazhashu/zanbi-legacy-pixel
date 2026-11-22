# -*- coding: utf-8 -*-
"""调试：检查单帧各图层，找出脸变黑的原因。"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
LAYERS = os.path.join(ROOT, "lpc_layers")
TEMPLATES = os.path.join(ROOT, "lpc_templates")

COL, ROW = 0, 2
FX, FY = COL * 64, ROW * 64

def load(path):
    im = Image.open(path)
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    return im.crop((FX, FY, FX + 64, FY + 64))

def ascii_dump(im, title, x0=17, x1=47, y0=14, y1=62):
    print(f"\n=== {title} (bbox x{x0}-{x1} y{y0}-{y1}) ===")
    px = im.load()
    LUM = "@%#*+=-:. "
    for y in range(y0, y1):
        row = []
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if a < 16:
                row.append(" ")
            else:
                lum = int(0.299*r + 0.587*g + 0.114*b)
                idx = min(len(LUM)-1, int(lum / 256 * len(LUM)))
                row.append(LUM[idx])
        print("".join(row))

# 检查 base 的透明处理
base_full = Image.open(os.path.join(TEMPLATES, "male_idle.png"))
print(f"male_idle.png mode={base_full.mode}")
if base_full.mode == "P":
    print(f"  调色板大小={len(base_full.getpalette())//3}")
    # 检查透明索引
    if "transparency" in base_full.info:
        print(f"  transparency={base_full.info['transparency']}")

base = load(os.path.join(TEMPLATES, "male_idle.png"))
ascii_dump(base, "BASE (male body)")

legs = load(os.path.join(LAYERS, "legs_formal_male_idle.png"))
ascii_dump(legs, "LEGS (formal pants)")

torso = load(os.path.join(LAYERS, "torso_longsleeve.png"))
ascii_dump(torso, "TORSO (longsleeve)")

hair = load(os.path.join(LAYERS, "hair_swoop.png"))
ascii_dump(hair, "HAIR (swoop)")

eyes = load(os.path.join(LAYERS, "eyes_human_adult_default_idle.png"))
ascii_dump(eyes, "EYES (adult default)")
