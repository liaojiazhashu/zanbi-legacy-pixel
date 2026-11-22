# -*- coding: utf-8 -*-
"""生成三视图总表（8 角色 × 正面/侧面/背面）。"""
from PIL import Image, ImageDraw

names = ['elder', 'young', 'clone', 'richard', 'boy', 'girl', 'mech', 'cube']
CW, CH = 96 * 5, 160 * 5
sheet = Image.new('RGB', (CW * 3 + 60, CH * 8 + 30), (24, 26, 30))
d = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    for j, view in enumerate(['v5', 'side', 'back']):
        p = f'portraits/{view}_{n}.png'
        img = Image.open(p)
        x = j * (CW + 4) + 10
        y = i * (CH + 2) + 14
        sheet.paste(img, (x, y))
d.text((10, 2), 'FRONT', fill=(255, 220, 120))
d.text((CW + 14, 2), 'SIDE', fill=(255, 220, 120))
d.text((2 * CW + 18, 2), 'BACK', fill=(255, 220, 120))
for i, n in enumerate(names):
    d.text((CW * 3 + 14, i * (CH + 2) + CH // 2), n, fill=(255, 255, 255))
sheet.save('portraits/tri_view.png')
print('saved', sheet.size)
