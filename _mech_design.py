from PIL import Image

# 读 LPC male base 向下站立帧
base = Image.open(r"D:\AAAAI\动画视频尝试\赞比的遗产\lpc_layers\body\body_male_idle.png").convert("RGBA")
frame = base.crop((0, 128, 64, 192))  # 64x64 向下帧
fpx = frame.load()

# 肤色 6 色 -> 金属蓝 6 色（换色系统）
MAP = {
    (39, 25, 32):  (26, 32, 44),   # 描边 #271920 -> 深蓝黑 #1a202c
    (153, 66, 60): (74, 85, 104),  # 暗 #99423c -> 灰蓝 #4a5568（调亮，避免脸中央过暗）
    (204, 134, 101): (96, 125, 168),# 中暗 #cc8665 -> 亮灰蓝 #607da8（头部主体调亮）
    (228, 164, 124): (59, 130, 246),# 中 #e4a47c -> 亮蓝 #3b82f6
    (249, 213, 186): (96, 165, 250),# 亮 #f9d5ba -> 更亮蓝 #60a5fa
    (250, 236, 231): (147, 197, 253),# 高光 #faece7 -> 浅蓝 #93c5fd
}

CYAN = (0, 240, 255)   # 发光青 #00f0ff（眼带+核心灯）
DARK = (26, 32, 44)    # 深蓝黑

out = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
opx = out.load()

# 1. 换色（逐像素映射）
for y in range(64):
    for x in range(64):
        r, g, b, a = fpx[x, y]
        if a > 0:
            key = (r, g, b)
            if key in MAP:
                nr, ng, nb = MAP[key]
            else:
                nr, ng, nb = r, g, b  # 未知色保留
            opx[x, y] = (nr, ng, nb, 255)

# 2. 发光眼带（头部，眼睛位置 y35-37，横条覆盖整个头部宽度）
# 原帧头部 y32-41，眼睛约 y35-36
for y in range(35, 38):
    for x in range(20, 44):
        r, g, b, a = opx[x, y]
        if a > 0:
            opx[x, y] = (CYAN[0], CYAN[1], CYAN[2], 255)

# 眼带上下描边
for x in range(20, 44):
    for y in (34, 38):
        r, g, b, a = opx[x, y]
        if a > 0:
            opx[x, y] = (DARK[0], DARK[1], DARK[2], 255)

# 3. 胸口核心灯（胸中央 y44-46）
for y in range(44, 47):
    for x in range(26, 38):
        r, g, b, a = opx[x, y]
        if a > 0:
            opx[x, y] = (CYAN[0], CYAN[1], CYAN[2], 255)

# 4. 关节分块线（腿的膝关节处加深色横线）
# 原帧腿在 y50-61，膝关节约 y53-54
for y in (53, 54):
    for x in range(18, 46):
        r, g, b, a = opx[x, y]
        if a > 0 and r != DARK[0]:  # 不覆盖描边
            opx[x, y] = (DARK[0], DARK[1], DARK[2], 255)

# 保存
out.save(r"D:\AAAAI\动画视频尝试\赞比的遗产\lpc_composite\mech_recolor.png")

# 放大预览
big = out.resize((64*6, 64*6), Image.NEAREST)
big.save(r"D:\AAAAI\动画视频尝试\赞比的遗产\lpc_composite\mech_recolor_x6.png")

# ASCII 预览
LUM_CHARS = "@%#*+=-:. "
def lum(rgb):
    r, g, b = rgb
    return int(0.2126*r + 0.7152*g + 0.0722*b)

print("ASCII (机械赞比 64x64):")
for y in range(64):
    line = ""
    for x in range(64):
        r, g, b, a = opx[x, y]
        if a == 0:
            line += " "
        else:
            idx = min(9, lum((r, g, b)) * 10 // 256)
            line += LUM_CHARS[idx]
    print(line)
print("DONE")
