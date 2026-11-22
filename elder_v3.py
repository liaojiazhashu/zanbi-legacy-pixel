# -*- coding: utf-8 -*-
"""老年赞比正面立绘 v3 —— 96x160 直接 1:1 手绘，5 级明暗 + 纹理孤立像素。
对照 ichiwatashi 好作品基准重做：
- isolated_rate 目标 0.07-0.16（纹理/高光/抖动孤立像素）
- largest_cluster_rate 目标 <=0.228（拉开明暗，避免大面积平涂）
- periodic_class 目标 非 upscale（直接 1:1，非放大）
"""
from PIL import Image

W, H = 96, 160
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
px = img.load()

# ---- 调色板（LPC 修正版，每材质 5 级明暗 + 描边）----
# 描边（深紫棕统一）
OUT = (39, 25, 32)
# 肤色（亮脸修正，暗部暖红棕）
SKIN = [(153, 66, 60), (204, 134, 101), (228, 164, 124), (249, 213, 186), (250, 236, 231)]
# 银白残发（暗部冷灰）
HAIR = [(72, 78, 87), (107, 112, 120), (143, 149, 156), (184, 188, 194), (216, 219, 224)]
# 藏青西装
SUIT = [(26, 32, 48), (42, 53, 72), (61, 76, 102), (85, 104, 138), (111, 131, 168)]
# 白衬衫
SHIRT = [(150, 142, 130), (196, 181, 159), (216, 208, 192), (232, 226, 212), (245, 240, 230)]
# 酒红领带
TIE = [(90, 26, 34), (122, 40, 50), (154, 56, 68), (184, 80, 92), (210, 108, 118)]
# 深棕眼
EYE = [(42, 26, 16), (90, 58, 36), (138, 90, 58)]
# 老人斑
SPOT = (176, 136, 104)
# 鞋深棕
SHOE = [(26, 18, 16), (42, 26, 22), (58, 40, 32)]

def P(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def hline(x1, x2, y, c):
    for x in range(x1, x2 + 1):
        P(x, y, c)

def vline(x, y1, y2, c):
    for y in range(y1, y2 + 1):
        P(x, y, c)

def rect(x1, y1, x2, y2, c):
    for y in range(y1, y2 + 1):
        hline(x1, x2, y, c)

def ellipse(cx, cy, rx, ry, c):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                P(x, y, c)

# ================= 头部（y6-40）=================
CX = 48  # 中心

# 头轮廓（描边底）
ellipse(CX, 24, 17, 19, OUT)
# 头主体（肤色中）
ellipse(CX, 24, 16, 18, SKIN[2])
# 面部受光（左侧偏亮）—— 左上光源
for y in range(8, 40):
    for x in range(CX - 15, CX + 16):
        d = ((x - CX) / 16) ** 2 + ((y - 24) / 18) ** 2
        if d <= 1:
            if x <= CX - 4:
                P(x, y, SKIN[3])  # 左侧亮
            elif x <= CX + 8:
                P(x, y, SKIN[2])  # 中间中
            else:
                P(x, y, SKIN[1])  # 右侧暗

# 秃顶：头顶中央露头皮（肤色），两侧银白残发
# 头皮区（y6-15，中央 x38-58）
for y in range(6, 16):
    for x in range(CX - 10, CX + 11):
        d = ((x - CX) / 16) ** 2 + ((y - 24) / 18) ** 2
        if d <= 1:
            P(x, y, SKIN[3] if x <= CX else SKIN[2])
# 头皮高光点（孤立）
for x, y in [(CX - 5, 8), (CX + 2, 7), (CX + 8, 9), (CX - 8, 10)]:
    P(x, y, SKIN[4])

# 银白残发（两侧，贴太阳穴，从 y7 垂到 y26，窄条 <=7px）
def hair_side(xr, step):
    for y in range(7, 27):
        for i in range(0, 6):
            x = xr + i * step
            if 30 <= x <= 66:
                # 残发明暗
                if i <= 2:
                    P(x, y, HAIR[2] if (x + y) % 5 != 0 else HAIR[1])
                elif i <= 4:
                    P(x, y, HAIR[3])
                else:
                    P(x, y, HAIR[4] if (x + y) % 3 == 0 else HAIR[3])
# 左侧残发 x33-38
hair_side(33, 1)
# 右侧残发 x58-63
hair_side(58, 1)
# 残发与头皮交界抖动（打破整齐边界）
for y in range(8, 24, 2):
    P(38 + (y % 3), y, HAIR[1])
    P(58 - (y % 3), y, HAIR[1])

# 眉毛（深灰，皱纹感）
for y in (18, 19):
    for x in range(CX - 11, CX - 3):
        P(x, y, HAIR[0])
    for x in range(CX + 3, CX + 11):
        P(x, y, HAIR[0])
# 眉尾纹理（孤立）
P(CX - 11, 18, HAIR[1]); P(CX + 11, 18, HAIR[1])

# 眼睛（深棕虹膜 + 高光点孤立）
def eye(cx):
    P(cx, 23, EYE[1]); P(cx, 24, EYE[2]); P(cx, 25, EYE[1])
    P(cx - 1, 23, EYE[0]); P(cx - 1, 24, EYE[1]); P(cx - 1, 25, EYE[0])
    P(cx + 1, 24, EYE[0])
    P(cx, 22, SKIN[4])  # 高光点（孤立）
eye(CX - 5); eye(CX + 5)

# 眼袋/皱纹（老人特征，断续暗像素）
for x in range(CX - 9, CX + 9, 3):
    P(x, 27, SKIN[1])

# 鼻子
P(CX, 26, SKIN[1]); P(CX, 27, SKIN[1]); P(CX, 28, SKIN[2])
P(CX - 1, 28, SKIN[1]); P(CX + 1, 28, SKIN[1])
# 鼻梁高光（孤立）
P(CX, 25, SKIN[4])

# 嘴（在胡子下，轻微）
P(CX - 2, 31, SKIN[0]); P(CX - 1, 31, SKIN[0]); P(CX, 31, SKIN[0]); P(CX + 1, 31, SKIN[0]); P(CX + 2, 31, SKIN[0])

# 白胡子（覆盖下巴 y28-38，明确男性 + 纹理）
for y in range(28, 39):
    for x in range(CX - 12, CX + 13):
        d = ((x - CX) / 12) ** 2 + ((y - 34) / 8) ** 2
        if d <= 1:
            # 胡须纹理（大量孤立）
            m = (x * 7 + y * 13) % 11
            if m == 0:
                P(x, y, HAIR[0])  # 深缝隙（纹理）
            elif m <= 3:
                P(x, y, HAIR[1])
            elif m <= 6:
                P(x, y, HAIR[2])
            elif m <= 8:
                P(x, y, HAIR[3])
            else:
                P(x, y, HAIR[4])

# 老人斑（皮肤斑点，孤立纹理）
for x, y in [(CX - 12, 16), (CX + 13, 15), (CX + 10, 29), (CX - 13, 22)]:
    P(x, y, SPOT)

# ================= 躯干（y40-92）=================
# 脖子
rect(CX - 4, 38, CX + 4, 42, SKIN[1])
hline(CX - 4, CX + 4, 39, SKIN[2])
# 颈纹
P(CX - 2, 41, SKIN[0]); P(CX + 2, 41, SKIN[0])

# 西装外套主体（5 级明暗，左上光源）
# 肩宽 x25-71，腰 x30-66，下摆 y88
def suit_body():
    for y in range(42, 90):
        # 肩部到腰部收窄
        shoulder_w = 23  # 肩半宽
        waist_w = 18     # 腰半宽
        if y <= 60:
            half = shoulder_w - (shoulder_w - waist_w) * (y - 42) / 18
        else:
            half = waist_w
        half = int(half)
        for x in range(CX - half, CX + half + 1):
            # 明暗：左亮右暗 + 中央躯干
            rel = x - CX
            if rel < -10:
                P(x, y, SUIT[3])
            elif rel < -4:
                P(x, y, SUIT[2])
            elif rel < 6:
                P(x, y, SUIT[1])
            else:
                P(x, y, SUIT[0])
suit_body()

# 西装描边（外套轮廓）
def suit_outline():
    for y in range(42, 90):
        shoulder_w = 23
        waist_w = 18
        if y <= 60:
            half = shoulder_w - (shoulder_w - waist_w) * (y - 42) / 18
        else:
            half = waist_w
        half = int(half)
        P(CX - half, y, OUT)
        P(CX + half, y, OUT)
    # 下摆
    hline(CX - 18, CX + 18, 89, OUT)
    hline(CX - 17, CX + 17, 90, OUT)
    # 肩线
    hline(CX - 23, CX + 23, 42, OUT)
    hline(CX - 23, CX + 23, 43, OUT)
suit_outline()

# 衬衫 V 领 + 领带
def shirt_tie():
    # V 领白衬衫
    for y in range(44, 58):
        half = 6 + (y - 44) // 2
        for x in range(CX - half, CX + half + 1):
            if abs(x - CX) >= 2:  # 领带留中缝
                P(x, y, SHIRT[2] if x < CX else SHIRT[1])
    # 领带（酒红，宽 6，垂到 y70）
    for y in range(45, 71):
        w = 3 if y < 52 else 2
        for x in range(CX - w, CX + w + 1):
            if x < CX:
                P(x, y, TIE[2])
            elif x == CX:
                P(x, y, TIE[3])
            else:
                P(x, y, TIE[1])
    # 领带结
    for y in range(44, 47):
        for x in range(CX - 4, CX + 5):
            P(x, y, TIE[1] if x >= CX else TIE[3])
    # 领带高光（孤立）
    P(CX, 48, TIE[4]); P(CX, 52, TIE[4]); P(CX, 56, TIE[4])
shirt_tie()

# 西装翻领（V 形，左亮右暗）
def lapels():
    # 左翻领
    for i in range(0, 14):
        y = 44 + i
        x = CX - 16 + i
        P(x, y, SUIT[4] if i % 4 == 0 else SUIT[3])
        P(x - 1, y, SUIT[2])
    # 右翻领
    for i in range(0, 14):
        y = 44 + i
        x = CX + 16 - i
        P(x, y, SUIT[1])
        P(x + 1, y, SUIT[0])
lapels()

# 纽扣（2 颗，高光孤立）
for y in (58, 66):
    P(CX - 8, y, OUT); P(CX - 8, y + 1, SUIT[4])
    P(CX + 8, y, OUT); P(CX + 8, y + 1, SUIT[3])
    P(CX - 8, y - 1, SUIT[4])  # 高光点

# 西装纹理（织物点，断续中亮像素 —— 关键孤立纹理）
import random
random.seed(42)
for y in range(46, 88):
    for x in range(CX - 20, CX + 21):
        if 46 <= y <= 88 and (x + y) % 7 == 0:
            # 只在西装区域撒纹理
            if SUIT[1] == px[x, y] or SUIT[2] == px[x, y]:
                P(x, y, SUIT[2] if (x + y) % 14 == 0 else SUIT[3])
            elif SUIT[3] == px[x, y]:
                P(x, y, SUIT[4] if (x + y) % 5 == 0 else SUIT[3])

# ================= 手臂（自然下垂）=================
def arms():
    # 左臂
    for y in range(46, 88):
        for x in range(CX - 26, CX - 21):
            P(x, y, SUIT[2] if (x + y) % 6 != 0 else SUIT[3])
        P(CX - 26, y, OUT); P(CX - 21, y, OUT)
    # 右手（露出，肤色）
    for y in range(82, 88):
        for x in range(CX + 21, CX + 26):
            P(x, y, SKIN[2] if (x + y) % 5 != 0 else SKIN[3])
        P(CX + 21, y, OUT); P(CX + 25, y, OUT)
    # 左手（露出，肤色）
    for y in range(82, 88):
        for x in range(CX - 26, CX - 21):
            P(x, y, SKIN[2] if (x + y) % 5 != 0 else SKIN[3])
    # 手高光（孤立）
    P(CX + 23, 84, SKIN[4]); P(CX - 23, 84, SKIN[4])
arms()

# ================= 腿（y90-152，分腿裤）=================
def legs():
    # 裤腿（两条，中间分缝）
    # 左腿 x30-47，右腿 x49-66
    for y in range(91, 147):
        # 左裤腿
        for x in range(CX - 18, CX - 1):
            rel = x - (CX - 10)
            if rel < -6:
                P(x, y, SUIT[3])
            elif rel < 0:
                P(x, y, SUIT[2])
            else:
                P(x, y, SUIT[1])
        # 右裤腿
        for x in range(CX + 1, CX + 18):
            rel = x - (CX + 10)
            if rel < -6:
                P(x, y, SUIT[3])
            elif rel < 0:
                P(x, y, SUIT[2])
            else:
                P(x, y, SUIT[1])
    # 裤腿描边
    for y in range(91, 147):
        P(CX - 18, y, OUT); P(CX - 1, y, OUT)
        P(CX + 1, y, OUT); P(CX + 18, y, OUT)
    # 裤脚
    hline(CX - 18, CX - 1, 147, OUT)
    hline(CX + 1, CX + 18, 147, OUT)
    # 裤中线（褶皱，断续）
    for y in range(95, 145, 4):
        P(CX - 10, y, SUIT[0]); P(CX + 10, y, SUIT[0])
    # 裤纹理（织物点）
    for y in range(93, 146):
        for x in range(CX - 17, CX + 17):
            if x != CX - 1 and x != CX + 1 and x != CX and (x * 3 + y * 5) % 9 == 0:
                cur = px[x, y]
                if cur == SUIT[1]:
                    P(x, y, SUIT[2])
                elif cur == SUIT[2]:
                    P(x, y, SUIT[3])
legs()

# 鞋（深棕，分左右）
def shoes():
    # 左鞋
    for y in range(147, 153):
        for x in range(CX - 18, CX - 3):
            P(x, y, SHOE[1] if x < CX - 10 else SHOE[2])
    # 右鞋
    for y in range(147, 153):
        for x in range(CX + 3, CX + 18):
            P(x, y, SHOE[1] if x < CX + 10 else SHOE[2])
    # 鞋底描边
    hline(CX - 18, CX - 3, 153, OUT); hline(CX + 3, CX + 18, 153, OUT)
    hline(CX - 18, CX - 3, 152, OUT); hline(CX + 3, CX + 18, 152, OUT)
    # 鞋面高光（孤立）
    P(CX - 14, 149, SHOE[2]); P(CX + 14, 149, SHOE[2])
    P(CX - 6, 149, SHOE[0]); P(CX + 6, 149, SHOE[0])
shoes()

# 保存（透明背景，不 crop，交给检测工具 crop）
img.save("portraits/elder_v3.png")
print("saved portraits/elder_v3.png", img.size)

# 统计
from collections import Counter
cnt = Counter()
for y in range(H):
    for x in range(W):
        if px[x, y][3] > 0:
            cnt[px[x, y][:3]] += 1
print("颜色数", len(cnt), "像素量", sum(cnt.values()))
