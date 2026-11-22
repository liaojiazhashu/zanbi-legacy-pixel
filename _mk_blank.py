# -*- coding: utf-8 -*-
"""生成空白 96×160 透明 PNG 作为 LibreSprite 画布。"""
from PIL import Image

im = Image.new("RGBA", (96, 160), (0, 0, 0, 0))
im.save("D:/AAAAI/_tools/libresprite_cfg/blank.png")
print("saved blank.png 96x160")
