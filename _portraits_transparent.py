"""批量处理 Town Guards portraits：检测背景色→透明，保存到 part_library/characters/town_guards/portraits/。"""
from PIL import Image
import os, glob

SRC = r"D:\AAAAI\动画视频尝试\赞比的遗产\kenney\town_guards\Town_Guards_Vol1\portraits"
DST = r"D:\AAAAI\动画视频尝试\赞比的遗产\part_library\characters\town_guards\portraits"
os.makedirs(DST, exist_ok=True)

def bg_color(im):
    w, h = im.size
    px = im.load()
    # 四角像素作为背景候选
    corners = [px[0,0], px[w-1,0], px[0,h-1], px[w-1,h-1]]
    # 取出现最多的颜色
    from collections import Counter
    c = Counter(corners)
    return c.most_common(1)[0][0]

for f in glob.glob(os.path.join(SRC, "*.png")):
    im = Image.open(f).convert("RGBA")
    px = im.load()
    bg = bg_color(im)
    w, h = im.size
    tol = 30  # 容差
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0 and abs(r-bg[0]) < tol and abs(g-bg[1]) < tol and abs(b-bg[2]) < tol:
                px[x, y] = (r, g, b, 0)
    name = os.path.basename(f).replace(".png", "_t.png")
    im.save(os.path.join(DST, name))
    print(f"{name} bg={bg} size={im.size}")
