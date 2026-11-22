# -*- coding: utf-8 -*-
"""拼合 LibreSprite 输出的 8 角色立绘为合集图。"""
from PIL import Image

src = r"D:\AAAAI\_tools\libresprite_cfg\out"
names = ["elder", "young", "clone", "richard", "boy", "girl", "mech", "cube"]
imgs = []
for n in names:
    im = Image.open(f"{src}\\{n}.png").convert("RGB")
    imgs.append(im)

w, h = imgs[0].size
scale = 4
W, H = w * scale, h * scale
sheet = Image.new("RGB", (W * 4 + 24, H * 2 + 12), (24, 26, 30))
for i, im in enumerate(imgs):
    r, c = i // 4, i % 4
    im = im.resize((W, H), Image.NEAREST)
    sheet.paste(im, (c * (W + 6), r * (H + 6)))
out = r"D:\AAAAI\动画视频尝试\赞比的遗产\portraits\ls_all_sheet.png"
sheet.save(out)
print("saved", out, sheet.size)
