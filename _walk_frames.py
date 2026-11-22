from PIL import Image

path = r"D:\AAAAI\动画视频尝试\赞比的遗产\kenney\town_guards\Town_Guards_Vol1\GUARD_01\npc_01__down.png"
img = Image.open(path).convert("RGBA")

LUM = "@%#*+=-:. "

def frame_ascii(img, x0, y0, fw=96, fh=64):
    lines = []
    for y in range(fh):
        row = ""
        for x in range(fw):
            r, g, b, a = img.getpixel((x0 + x, y0 + y))
            if a < 128:
                row += " "
            else:
                lum = int(0.2126*r + 0.7152*g + 0.0722*b)
                idx = min(9, max(0, int((255 - lum) / 25.6)))
                row += LUM[idx]
        lines.append(row)
    return lines

def crop(lines):
    rows = [i for i, l in enumerate(lines) if l.strip()]
    if not rows:
        return lines
    top, bot = rows[0], rows[-1]
    cols = set()
    for l in lines:
        for i, c in enumerate(l):
            if c != ' ':
                cols.add(i)
    left, right = min(cols), max(cols)
    return [l[left:right+1] for l in lines[top:bot+1]]

# walk 帧在底行（y0=64），8 帧，每帧 96px 宽
print("=== walk 向下 8 帧（底行，96px 宽）===")
for f in range(8):
    lines = frame_ascii(img, f*96, 64)
    lines = crop(lines)
    print(f"\n--- 帧 {f} ---")
    for l in lines:
        print(l)
