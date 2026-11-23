"""提取 Elfia.png 的 24 个精灵为独立透明 PNG。"""
from PIL import Image
import os

p = r"D:\AAAAI\动画视频尝试\赞比的遗产\kenney\female\Elfia.png"
im = Image.open(p).convert("RGBA")
px = im.load()
w, h = im.size

# 内容块边界（从空白列/行分析）
col_blocks = [(23,36),(50,68),(83,96),(133,149),(161,180),(189,203)]
row_blocks = [(16,45),(54,81),(93,119),(132,175)]

dst = r"D:\AAAAI\动画视频尝试\赞比的遗产\part_library\characters\elfia"
os.makedirs(dst, exist_ok=True)

idx = 0
for ri, (y0, y1) in enumerate(row_blocks):
    for ci, (x0, x1) in enumerate(col_blocks):
        crop = im.crop((x0, y0, x1+1, y1+1))
        # 裁掉透明边
        bbox = crop.getbbox()
        if bbox:
            crop = crop.crop(bbox)
        name = f"elfia_r{ri}_c{ci}.png"
        crop.save(os.path.join(dst, name))
        print(f"{name} {crop.size}")
        idx += 1
print(f"共 {idx} 个")
