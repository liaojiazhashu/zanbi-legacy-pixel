"""提取 Town Guards 6 卫兵的 idle 站立完整角色（透明背景 PNG）。

从 npc_XX__down.png 提取第一个内容块（idle 帧1 的左侧角色），
裁剪 bbox → 保存透明 PNG 到 part_library/characters/town_guards/。
"""
from PIL import Image
import os, glob

SRC = r"D:\AAAAI\动画视频尝试\赞比的遗产\kenney\town_guards\Town_Guards_Vol1"
DST = r"D:\AAAAI\动画视频尝试\赞比的遗产\part_library\characters\town_guards"
os.makedirs(DST, exist_ok=True)

for guard in sorted(os.listdir(SRC)):
    gdir = os.path.join(SRC, guard)
    if not os.path.isdir(gdir):
        continue
    down = os.path.join(gdir, f"npc_{guard.split('_')[-1].lower()}__down.png")
    # 实际文件名是 npc_01__down.png 这种
    files = glob.glob(os.path.join(gdir, "npc_*__down.png"))
    if not files:
        continue
    down = files[0]
    im = Image.open(down).convert("RGBA")
    px = im.load()
    # idle 帧1 区域 x0-192, y0-96，找第一个内容块
    minx, miny, maxx, maxy = 999, 999, -1, -1
    for y in range(96):
        for x in range(192):
            if px[x, y][3] > 0:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if maxx < 0:
        print(f"{guard}: 无内容")
        continue
    # 裁剪第一个内容块（左侧角色，x 范围取前 96px 内的 bbox）
    # 若 bbox 宽 > 96，说明 2 角色并排，只取左侧
    w = maxx - minx + 1
    if w > 96:
        # 重新找左侧 96px 内的 bbox
        maxx = minx + 95
        real_maxx = -1
        for x in range(minx, maxx+1):
            if any(px[x, y][3] > 0 for y in range(96)):
                real_maxx = x
        maxx = real_maxx
    char = im.crop((minx, miny, maxx+1, maxy+1))
    name = f"{guard}_idle_down.png"
    char.save(os.path.join(DST, name))
    print(f"{guard}: {name} {char.size}")
