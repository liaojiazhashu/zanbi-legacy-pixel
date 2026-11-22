from PIL import Image
import sys

def measure(path):
    img = Image.open(path).convert('RGB')
    w, h = img.size
    px = img.load()
    # 精灵是饱和彩色，水印是半透明灰（低饱和）。用高饱和阈值只抓精灵。
    minx, miny, maxx, maxy = w, h, 0, 0
    count = 0
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            sat = mx - mn  # 饱和度
            if sat > 40 and mx > 60:  # 高饱和 + 足够亮（排除半透明水印和纯黑）
                count += 1
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    print(f'{path}: sat-pixel bbox x[{minx}-{maxx}] y[{miny}-{maxy}] = {maxx-minx+1}x{maxy-miny+1} (count={count})')

for p in sys.argv[1:]:
    measure(p)
