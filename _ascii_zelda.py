from PIL import Image

img = Image.open(r'kenney\zelda\gfx\character.png').convert('RGBA')
# 字符映射（按亮度）
LUM_CHARS = "@%#*+=-:. "

def ascii_frame(img, cx, cy, fw=16, fh=16):
    out = []
    for y in range(cy, cy + fh):
        row = []
        for x in range(cx, cx + fw):
            p = img.getpixel((x, y))
            if p[3] == 0:
                row.append(' ')
            else:
                lum = 0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2]
                idx = min(9, int(lum / 256 * 10))
                row.append(LUM_CHARS[idx])
        out.append(''.join(row))
    return '\n'.join(out)

# 打印前几个帧（第一行：向下站立/走路）
print("=== frame (0,0) 向下站立 ===")
print(ascii_frame(img, 0, 0))
print()
print("=== frame (16,0) ===")
print(ascii_frame(img, 16, 0))
print()
print("=== frame (32,0) ===")
print(ascii_frame(img, 32, 0))
print()
print("=== frame (48,0) ===")
print(ascii_frame(img, 48, 0))
