import pixel_sprites as ps
from PIL import Image, ImageDraw

# 渲染真侧面头（放大 8 倍查看）
img = Image.new('RGB', (220, 260), (40, 40, 48))
d = ImageDraw.Draw(img)
ps.art_render(d, ps.ELDER_SIDE_HEAD, 110, 24, ps.ELDER, False)
img = img.resize((1760, 2080), Image.NEAREST)
img.save('_chk_side_head.png')

# 渲染完整侧面站姿
img2 = Image.new('RGB', (120, 120), (40, 40, 48))
d2 = ImageDraw.Draw(img2)
ps.elder_side(d2, 60, 100, h=64, pal=ps.ELDER, facing=1)
img2 = img2.resize((960, 960), Image.NEAREST)
img2.save('_chk_side_full.png')

# 渲染躺姿
img3 = Image.new('RGB', (140, 100), (40, 40, 48))
d3 = ImageDraw.Draw(img3)
ps.elder_lie(d3, 10, 80, pal=ps.ELDER, facing=1)
img3 = img3.resize((1120, 800), Image.NEAREST)
img3.save('_chk_lie.png')

# 渲染少年侧面（对照）
img4 = Image.new('RGB', (120, 120), (40, 40, 48))
d4 = ImageDraw.Draw(img4)
ps.boy_side(d4, 60, 100, h=70, pal=ps.SKIN, facing=1)
img4 = img4.resize((960, 960), Image.NEAREST)
img4.save('_chk_boy_side.png')

print('done')
