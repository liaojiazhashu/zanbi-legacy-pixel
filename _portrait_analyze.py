from PIL import Image
from collections import Counter

base = r"D:\AAAAI\动画视频尝试\赞比的遗产\kenney\town_guards\Town_Guards_Vol1\portraits"
files = [
    "sword_shield_portrait_01.png",
    "captain_portrait_64_72.png",
    "heavy_guard_portrait.png",
    "archer_portrait_01.png",
    "standard_bearer_portrait_01.png",
]

def lum(c):
    r, g, b = c
    return int(0.2126*r + 0.7152*g + 0.0722*b)

for f in files:
    img = Image.open(base + "\\" + f).convert("RGBA")
    w, h = img.size
    cnt = Counter()
    for y in range(h):
        for x in range(w):
            r, g, b, a = img.getpixel((x, y))
            if a > 0:
                cnt[(r, g, b)] += 1
    top = cnt.most_common(10)
    print(f"{f} {w}x{h} {len(cnt)}色")
    for c, n in top:
        print(f"  #{c[0]:02x}{c[1]:02x}{c[2]:02x} lum={lum(c)} x{n}")
    print()
