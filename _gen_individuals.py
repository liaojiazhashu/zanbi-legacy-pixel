# -*- coding: utf-8 -*-
"""批量生成 8 张单独立绘 PNG（4x 放大），存 portraits/。"""
from PIL import Image, ImageDraw
import portrait

roles = [
    ('boy', portrait.boy_portrait),
    ('young', portrait.young_portrait),
    ('elder', portrait.elder_portrait),
    ('clone', portrait.clone_portrait),
    ('mech', portrait.mech_portrait),
    ('cube', portrait.cube_portrait),
    ('richard', portrait.richard_portrait),
    ('girl', portrait.girl_portrait),
]
for key, fn in roles:
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fn(d, 128, 228)
    portrait._reflection(img, 128, 228, 0.18)
    img = img.convert('RGB').resize((1024, 1024), Image.NEAREST)
    img.save('portraits/%s.png' % key)
    print('OK', key)
print('done', len(roles))
