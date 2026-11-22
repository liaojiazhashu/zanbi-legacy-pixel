# -*- coding: utf-8 -*-
"""少年赞比正面立绘 v3 —— 96x160 直接 1:1 手绘。
乱发 + 深棕眼 + 棕破衣(补丁) + 左腿截肢 + 拐杖。
对照 ichiwatashi 好作品基准：isolated_rate 0.07-0.16、largest_cluster<=0.228、无 upscale。
"""
from PIL import Image

W, H = 96, 160
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
px = img.load()

OUT = (39, 25, 32)
# 年轻肤色（稍亮暖）
SKIN = [(160, 74, 48), (208, 122, 80), (232, 154, 112), (245, 192, 154), (251, 224, 200)]
# 深棕乱发
HAIR = [(58, 26, 16), (90, 42, 24), (122, 58, 32), (154, 74, 40), (184, 90, 48)]
# 棕破衣
RAG = [(74, 42, 24), (106, 58, 32), (138, 74, 40), (170, 90, 48), (200, 106, 56)]
# 补丁浅棕
PATCH = [(154, 122, 80), (178, 144, 96)]
# 深棕眼（近黑，避免误读成红色）
EYE = [(30, 22, 18), (50, 36, 26), (70, 50, 34)]
# 裤子深灰蓝
PANTS = [(42, 48, 56), (58, 66, 76), (74, 84, 96), (90, 102, 116), (106, 120, 136)]
# 拐杖木色
CANE = [(90, 58, 32), (122, 80, 48), (154, 104, 64), (184, 128, 80)]
# 鞋
SHOE = [(26, 18, 16), (42, 26, 22), (58, 40, 32)]

def P(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def hline(x1, x2, y, c):
    for x in range(x1, x2 + 1):
        P(x, y, c)

def rect(x1, y1, x2, y2, c):
    for y in range(y1, y2 + 1):
        hline(x1, x2, y, c)

def ellipse(cx, cy, rx, ry, c):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                P(x, y, c)

CX = 48

# ================= 头部（y6-42，乱发覆盖头顶）=================
# 头轮廓（描边底）
ellipse(CX, 25, 16, 19, OUT)
# 头主体（肤色）
ellipse(CX, 25, 15, 18, SKIN[2])
# 面部明暗（左上光源）
for y in range(9, 42):
    for x in range(CX - 14, CX + 15):
        d = ((x - CX) / 15) ** 2 + ((y - 25) / 18) ** 2
        if d <= 1:
            if x <= CX - 4:
                P(x, y, SKIN[3])
            elif x <= CX + 8:
                P(x, y, SKIN[2])
            else:
                P(x, y, SKIN[1])

# 乱发（messy，多簇不规则，覆盖头顶 y6-26）
def messy_hair():
    # 主体（覆盖头顶+两侧）
    for y in range(6, 27):
        for x in range(CX - 16, CX + 17):
            # 头顶弧 + 两侧垂发
            d = ((x - CX) / 17) ** 2 + ((y - 12) / 9) ** 2
            if d <= 1.05 and y <= 26:
                # 乱发纹理（多簇）
                m = (x * 5 + y * 11) % 13
                if m == 0:
                    P(x, y, HAIR[0])  # 深缝
                elif m <= 3:
                    P(x, y, HAIR[1])
                elif m <= 6:
                    P(x, y, HAIR[2])
                elif m <= 9:
                    P(x, y, HAIR[3])
                else:
                    P(x, y, HAIR[4])
    # 乱发翘起簇（顶部不规则，打破对称）
    for x, y in [(CX-12, 4), (CX-8, 3), (CX-4, 4), (CX+2, 3), (CX+7, 4), (CX+11, 5), (CX-15, 8), (CX+14, 7)]:
        P(x, y, HAIR[3]); P(x, y-1, HAIR[4])
    # 刘海（垂到额头 y17-19，不遮眼睛）
    for y in range(16, 20):
        for x in range(CX - 9, CX + 10):
            if (x + y) % 3 != 0:
                P(x, y, HAIR[2] if x < CX else HAIR[1])
    # 两侧垂发（贴耳，垂到 y28）
    for y in range(18, 29):
        for x in (CX - 15, CX - 14, CX + 14, CX + 15):
            P(x, y, HAIR[1] if (x + y) % 4 else HAIR[2])
    # 高光（发顶，孤立）
    for x, y in [(CX-6, 8), (CX-2, 7), (CX+4, 8)]:
        P(x, y, HAIR[4])
messy_hair()

# 眉毛（深棕）
for y in (20, 21):
    for x in range(CX - 10, CX - 3):
        P(x, y, HAIR[0])
    for x in range(CX + 3, CX + 10):
        P(x, y, HAIR[0])

# 眼睛（深棕虹膜 + 高光孤立）
def eye(cx):
    P(cx, 24, EYE[1]); P(cx, 25, EYE[2]); P(cx, 26, EYE[1])
    P(cx - 1, 24, EYE[0]); P(cx - 1, 25, EYE[1]); P(cx - 1, 26, EYE[0])
    P(cx + 1, 25, EYE[0])
    P(cx, 23, SKIN[4])  # 高光点
eye(CX - 5); eye(CX + 5)

# 鼻子
P(CX, 27, SKIN[1]); P(CX, 28, SKIN[1]); P(CX, 29, SKIN[2])
P(CX - 1, 29, SKIN[1]); P(CX + 1, 29, SKIN[1])
P(CX, 26, SKIN[4])  # 鼻梁高光

# 嘴（年轻，小）
P(CX - 2, 32, SKIN[0]); P(CX - 1, 32, SKIN[0]); P(CX, 32, SKIN[0]); P(CX + 1, 32, SKIN[0]); P(CX + 2, 32, SKIN[0])

# 脸颊脏污（孤儿在难民营，1-2px 污渍纹理）
for x, y in [(CX - 11, 28), (CX + 12, 27), (CX - 9, 33), (CX + 10, 34)]:
    P(x, y, (90, 58, 40))

# ================= 脖子+躯干（y42-90，棕破衣瘦削）=================
rect(CX - 4, 40, CX + 4, 44, SKIN[1])
hline(CX - 4, CX + 4, 41, SKIN[2])

# 棕破衣主体（瘦削，肩窄）
def rag_body():
    for y in range(44, 88):
        shoulder_w = 20
        waist_w = 15
        if y <= 60:
            half = shoulder_w - (shoulder_w - waist_w) * (y - 44) / 16
        else:
            half = waist_w
        half = int(half)
        for x in range(CX - half, CX + half + 1):
            rel = x - CX
            if rel < -9:
                P(x, y, RAG[3])
            elif rel < -3:
                P(x, y, RAG[2])
            elif rel < 4:
                P(x, y, RAG[1])
            else:
                P(x, y, RAG[0])
rag_body()

# 破衣描边
def rag_outline():
    for y in range(44, 88):
        shoulder_w = 20
        waist_w = 15
        if y <= 60:
            half = shoulder_w - (shoulder_w - waist_w) * (y - 44) / 16
        else:
            half = waist_w
        half = int(half)
        P(CX - half, y, OUT)
        P(CX + half, y, OUT)
    hline(CX - 15, CX + 15, 87, OUT)
    hline(CX - 20, CX + 20, 44, OUT)
    hline(CX - 20, CX + 20, 45, OUT)
rag_outline()

# 破衣补丁（2 块，浅棕 + 缝线）
def patches():
    # 左肩补丁
    for y in range(50, 58):
        for x in range(CX - 17, CX - 10):
            P(x, y, PATCH[0] if (x + y) % 3 else PATCH[1])
    # 右侧补丁
    for y in range(62, 68):
        for x in range(CX + 8, CX + 15):
            P(x, y, PATCH[0] if (x + y) % 3 else PATCH[1])
    # 缝线（孤立深像素）
    for y in range(50, 58, 2):
        P(CX - 17, y, OUT); P(CX - 10, y, OUT)
    for y in range(62, 68, 2):
        P(CX + 8, y, OUT); P(CX + 15, y, OUT)
patches()

# 破衣纹理（织物磨损点）
for y in range(46, 86):
    for x in range(CX - 19, CX + 19):
        if (x * 7 + y * 3) % 11 == 0:
            cur = px[x, y]
            if cur == RAG[1]:
                P(x, y, RAG[2])
            elif cur == RAG[2]:
                P(x, y, RAG[3])
            elif cur == RAG[3]:
                P(x, y, RAG[4])
# 破洞（衣服破损，露出肤色/深洞）
for x, y in [(CX - 13, 60), (CX - 14, 61), (CX + 12, 71), (CX + 13, 72)]:
    P(x, y, (30, 20, 16))

# ================= 手臂 =================
def arms():
    # 左臂（破衣袖）
    for y in range(48, 84):
        for x in range(CX - 23, CX - 18):
            P(x, y, RAG[2] if (x + y) % 6 else RAG[3])
        P(CX - 23, y, OUT); P(CX - 18, y, OUT)
    # 左手（肤色）
    for y in range(80, 86):
        for x in range(CX - 23, CX - 18):
            P(x, y, SKIN[2] if (x + y) % 5 else SKIN[3])
    # 右臂（破衣袖）
    for y in range(48, 84):
        for x in range(CX + 18, CX + 23):
            P(x, y, RAG[1] if (x + y) % 6 else RAG[2])
        P(CX + 18, y, OUT); P(CX + 23, y, OUT)
    # 右手（肤色）
    for y in range(80, 86):
        for x in range(CX + 18, CX + 23):
            P(x, y, SKIN[2] if (x + y) % 5 else SKIN[3])
    # 手高光
    P(CX - 20, 82, SKIN[4]); P(CX + 20, 82, SKIN[4])
arms()

# ================= 腿（左截肢+拐杖，右腿正常）=================
def legs():
    # 右腿（裤，正常）
    for y in range(88, 148):
        for x in range(CX + 3, CX + 17):
            rel = x - (CX + 10)
            if rel < -5:
                P(x, y, PANTS[3])
            elif rel < 1:
                P(x, y, PANTS[2])
            else:
                P(x, y, PANTS[1])
    for y in range(88, 148):
        P(CX + 3, y, OUT); P(CX + 17, y, OUT)
    hline(CX + 3, CX + 17, 147, OUT)
    # 右腿纹理
    for y in range(90, 146):
        for x in range(CX + 4, CX + 16):
            if (x * 5 + y * 7) % 9 == 0:
                cur = px[x, y]
                if cur == PANTS[2]:
                    P(x, y, PANTS[3])
                elif cur == PANTS[3]:
                    P(x, y, PANTS[4])
    # 右裤腿褶皱
    for y in range(94, 144, 5):
        P(CX + 10, y, PANTS[0])
    # 右鞋
    for y in range(147, 153):
        for x in range(CX + 3, CX + 17):
            P(x, y, SHOE[1] if x < CX + 10 else SHOE[2])
    hline(CX + 3, CX + 17, 153, OUT); hline(CX + 3, CX + 17, 152, OUT)
    P(CX + 14, 149, SHOE[2])  # 高光
legs()

# 左腿截肢（残端到膝盖 y110，用破衣/裤包住）
def amputation():
    # 左裤腿（短，到 y110）
    for y in range(88, 110):
        for x in range(CX - 17, CX - 3):
            rel = x - (CX - 10)
            if rel < -5:
                P(x, y, PANTS[3])
            elif rel < 1:
                P(x, y, PANTS[2])
            else:
                P(x, y, PANTS[1])
    for y in range(88, 110):
        P(CX - 17, y, OUT); P(CX - 3, y, OUT)
    # 残端（裤腿扎口，圆钝，明显截断）
    hline(CX - 17, CX - 3, 110, OUT)
    hline(CX - 17, CX - 3, 111, OUT)
    hline(CX - 16, CX - 4, 112, PANTS[0])
    # 残端中心截面（浅色，表现截断面）
    for x in range(CX - 12, CX - 8):
        P(x, 112, (200, 190, 180))
    # 残端纹理
    for x in range(CX - 15, CX - 4, 3):
        P(x, 111, PANTS[0])
amputation()

# 拐杖（左侧，木色，2px 宽竖直 + 握把 + 底脚）
def cane():
    cx = CX - 22
    # 主杆（竖直 2px）
    for y in range(58, 149):
        P(cx, y, CANE[1]); P(cx + 1, y, CANE[2])
    # 杆身明暗（左上光源，左亮右暗）
    for y in range(58, 149):
        P(cx, y, CANE[2] if (y % 6) == 0 else CANE[3])
        P(cx + 1, y, CANE[1])
    # 握把（横杆，手抓处 y82）
    hline(cx - 3, cx + 3, 82, CANE[1])
    hline(cx - 3, cx + 3, 83, CANE[2])
    P(cx - 3, 83, CANE[3])  # 高光
    # 底脚（橡胶头，深色）
    for y in range(149, 153):
        P(cx, y, SHOE[0]); P(cx + 1, y, SHOE[0])
    hline(cx - 1, cx + 2, 153, OUT)
cane()

img.save("portraits/boy_v3.png")
print("saved portraits/boy_v3.png", img.size)

from collections import Counter
cnt = Counter()
for y in range(H):
    for x in range(W):
        if px[x, y][3] > 0:
            cnt[px[x, y][:3]] += 1
print("颜色数", len(cnt), "像素量", sum(cnt.values()))
