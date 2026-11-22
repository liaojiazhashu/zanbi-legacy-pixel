from PIL import Image
from collections import Counter

# 读 LPC male base
base = Image.open(r"D:\AAAAI\动画视频尝试\赞比的遗产\lpc_layers\body\body_male_idle.png").convert("RGBA")
w, h = base.size
print(f"male base 尺寸 {w}x{h}")

# 调色板
cnt = Counter()
for y in range(h):
    for x in range(w):
        r, g, b, a = base.getpixel((x, y))
        if a > 0:
            cnt[(r, g, b)] += 1
print(f"颜色数 {len(cnt)}")
for c, n in cnt.most_common():
    print(f"  #{c[0]:02x}{c[1]:02x}{c[2]:02x} x{n}")

# 向下站立帧 = col0,row2 = (0,128) 到 (64,192)
px = base.load()
frame = base.crop((0, 128, 64, 192))
fpx = frame.load()

# bbox
xs = [x for x in range(64) for y in range(64) if fpx[x, y][3] > 0]
ys = [y for x in range(64) for y in range(64) if fpx[x, y][3] > 0]
bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
print(f"\n向下帧 bbox=({bx0},{by0})-({bx1},{by1}) {bx1-bx0+1}x{by1-by0+1}")

# ASCII 明暗
LUM_CHARS = "@%#*+=-:. "
def lum(rgb):
    r, g, b = rgb
    return int(0.2126*r + 0.7152*g + 0.0722*b)

print(f"\nASCII (向下帧):")
for y in range(by0, by1+1):
    line = ""
    for x in range(bx0, bx1+1):
        r, g, b, a = fpx[x, y]
        if a == 0:
            line += " "
        else:
            idx = min(9, lum((r, g, b)) * 10 // 256)
            line += LUM_CHARS[idx]
    print(line)
print("DONE")
