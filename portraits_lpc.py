# -*- coding: utf-8 -*-
"""《赞比的遗产》8 角色正面立绘 —— 统一 LPC 达标方法生成。
96x160 直接 1:1 手绘 + 每材质 5 级明暗 + 取模纹理孤立像素 + 高光左上。
ichiwatashi 基准：isolated_rate 0.07-0.16、largest_cluster<=0.228、无 upscale、16-37 色。
已达标：elder_v3.py / boy_v3.py（本文件生成其余 6 角色）。
"""
from PIL import Image
from collections import Counter

W, H = 96, 160

def new_canvas():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return img, img.load()

def P(px, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c

def hline(px, x1, x2, y, c):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        P(px, x, y, c)

def ellipse(px, cx, cy, rx, ry, c):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if rx > 0 and ry > 0 and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                P(px, x, y, c)

def tex(px, x, y, cur, pal, idx, a, b, n):
    """取模纹理：在指定材质色上撒明暗变化，制造孤立像素。cur 必须精确等于 pal[idx] 才改。"""
    if (x * a + y * b) % n == 0:
        if cur == pal[idx]:
            return pal[idx + 1] if idx + 1 < len(pal) else pal[idx]
        elif cur == pal[idx + 1]:
            return pal[idx + 2] if idx + 2 < len(pal) else pal[idx + 1]
    return cur

def save(img, name):
    img.save(f"portraits/{name}.png")
    cnt = Counter()
    for y in range(H):
        for x in range(W):
            if img.getpixel((x, y))[3] > 0:
                cnt[img.getpixel((x, y))[:3]] += 1
    print(f"saved portraits/{name}.png 颜色{len(cnt)} 像素{sum(cnt.values())}")

OUT = (39, 25, 32)
CX = 48

# ============ 共用调色板 ============
SKIN = [(160, 74, 48), (208, 122, 80), (232, 154, 112), (245, 192, 154), (251, 224, 200)]
HAIR_BROWN = [(58, 26, 16), (90, 42, 24), (122, 58, 32), (154, 74, 40), (184, 90, 48)]
EYE_BROWN = [(30, 22, 18), (50, 36, 26), (70, 50, 34)]
WHITE_SHIRT = [(180, 176, 168), (210, 206, 198), (228, 225, 218), (240, 238, 232), (250, 249, 245)]
GRAY_SUIT = [(58, 56, 62), (82, 80, 88), (106, 104, 114), (130, 128, 140), (154, 152, 164)]
GRAY_PANTS = [(52, 54, 60), (74, 76, 84), (96, 98, 108), (118, 120, 132), (140, 142, 154)]
SHOE = [(26, 18, 16), (42, 26, 22), (58, 40, 32)]

# ============ 头部通用（无胡子成年男性）============
def head_base(px, hair_pal, hair_style, face_detail=True):
    ellipse(px, CX, 25, 16, 19, OUT)
    ellipse(px, CX, 25, 15, 18, SKIN[2])
    for y in range(9, 42):
        for x in range(CX - 14, CX + 15):
            d = ((x - CX) / 15) ** 2 + ((y - 25) / 18) ** 2
            if d <= 1:
                if x <= CX - 4:
                    P(px, x, y, SKIN[3])
                elif x <= CX + 8:
                    P(px, x, y, SKIN[2])
                else:
                    P(px, x, y, SKIN[1])
    if hair_style == "swoop":
        swoop_hair(px, hair_pal)
    elif hair_style == "buzzcut":
        buzzcut_hair(px, hair_pal)
    # 眉毛
    for y in (20, 21):
        for x in range(CX - 10, CX - 3):
            P(px, x, y, hair_pal[0])
        for x in range(CX + 3, CX + 10):
            P(px, x, y, hair_pal[0])
    # 眼睛（深棕 + 高光）
    for ec in (CX - 5, CX + 5):
        P(px, ec, 24, EYE_BROWN[1]); P(px, ec, 25, EYE_BROWN[2]); P(px, ec, 26, EYE_BROWN[1])
        P(px, ec - 1, 24, EYE_BROWN[0]); P(px, ec - 1, 25, EYE_BROWN[1]); P(px, ec - 1, 26, EYE_BROWN[0])
        P(px, ec + 1, 25, EYE_BROWN[0])
        P(px, ec, 23, SKIN[4])
    # 鼻子
    P(px, CX, 27, SKIN[1]); P(px, CX, 28, SKIN[1]); P(px, CX, 29, SKIN[2])
    P(px, CX - 1, 29, SKIN[1]); P(px, CX + 1, 29, SKIN[1]); P(px, CX, 26, SKIN[4])
    # 嘴
    hline(px, CX - 2, CX + 2, 32, SKIN[0])

def swoop_hair(px, pal):
    """偏分（swoop）：蓬松 + 一侧刘海垂下 + 分缝高光"""
    for y in range(6, 27):
        for x in range(CX - 16, CX + 17):
            d = ((x - CX) / 17) ** 2 + ((y - 12) / 9) ** 2
            if d <= 1.05 and y <= 26:
                # 分缝（右侧 x>CX 更亮，偏分）
                m = (x * 5 + y * 11) % 13
                if x > CX + 2:
                    P(px, x, y, pal[3] if m > 7 else pal[2])
                else:
                    P(px, x, y, pal[2] if m > 5 else pal[1])
    # 分缝高光（偏分线，孤立亮像素）
    for y in range(8, 20):
        P(px, CX + 3, y, pal[4])
    # 一侧刘海垂下（右侧，到 y24）
    for y in range(18, 25):
        for x in range(CX + 4, CX + 12):
            if (x + y) % 3 != 0:
                P(px, x, y, pal[1])
    # 顶部高光
    for x, y in [(CX - 6, 7), (CX - 2, 6), (CX + 5, 7)]:
        P(px, x, y, pal[4])

def buzzcut_hair(px, pal):
    """寸头（buzzcut）：薄层贴头皮 + 发际线清晰"""
    for y in range(10, 22):
        for x in range(CX - 15, CX + 16):
            d = ((x - CX) / 15.5) ** 2 + ((y - 16) / 6.5) ** 2
            if d <= 1.02:
                m = (x * 3 + y * 5) % 9
                if m == 0:
                    P(px, x, y, SKIN[1])  # 露头皮
                elif m <= 3:
                    P(px, x, y, pal[1])
                elif m <= 6:
                    P(px, x, y, pal[2])
                else:
                    P(px, x, y, pal[3])
    # 发际线（清晰弧线）
    for x in range(CX - 14, CX + 15):
        y = 18 - int(2 * ((x - CX) / 15) ** 2)
        P(px, x, y, pal[0])
    # 高光（头顶）
    for x, y in [(CX - 4, 12), (CX, 11), (CX + 4, 12)]:
        P(px, x, y, pal[3])

# ============ 西装躯干通用 ============
def suit_body(px, suit_pal, shirt_pal, tie_pal, tie_style="tie"):
    # 脖子
    P(px, CX - 3, 40, SKIN[1]); P(px, CX - 3, 41, SKIN[2]); P(px, CX + 3, 40, SKIN[1]); P(px, CX + 3, 41, SKIN[2])
    hline(px, CX - 3, CX + 3, 40, SKIN[2]); hline(px, CX - 3, CX + 3, 41, SKIN[2])
    # 西装（肩宽 22，收腰）
    for y in range(42, 88):
        shoulder_w = 22
        waist_w = 16
        if y <= 60:
            half = shoulder_w - (shoulder_w - waist_w) * (y - 42) / 18
        else:
            half = waist_w
        half = int(half)
        for x in range(CX - half, CX + half + 1):
            rel = x - CX
            if rel < -11:
                P(px, x, y, suit_pal[3])
            elif rel < -4:
                P(px, x, y, suit_pal[2])
            elif rel < 4:
                P(px, x, y, suit_pal[1])
            else:
                P(px, x, y, suit_pal[0])
    # 西装描边
    for y in range(42, 88):
        shoulder_w = 22; waist_w = 16
        half = int(shoulder_w - (shoulder_w - waist_w) * (y - 42) / 18) if y <= 60 else waist_w
        P(px, CX - half, y, OUT); P(px, CX + half, y, OUT)
    hline(px, CX - 22, CX + 22, 42, OUT); hline(px, CX - 22, CX + 22, 43, OUT)
    hline(px, CX - 16, CX + 16, 87, OUT)
    # 衬衫（V 领）
    for y in range(44, 62):
        for x in range(CX - 6, CX + 7):
            if abs(x - CX) <= (y - 44) // 2 + 3:
                P(px, x, y, shirt_pal[2] if (x + y) % 4 else shirt_pal[1])
    # 领带
    if tie_style == "tie":
        for y in range(45, 66):
            w = 3 if y < 58 else 2
            for x in range(CX - w, CX + w + 1):
                P(px, x, y, tie_pal[1] if (x + y) % 5 else tie_pal[0])
        # 领带结
        for x in range(CX - 3, CX + 4):
            P(px, x, 45, tie_pal[1]); P(px, x, 46, tie_pal[0])
    # 西装纹理
    for y in range(44, 86):
        for x in range(CX - 21, CX + 21):
            cur = px[x, y]
            if (x * 7 + y * 3) % 13 == 0 and cur in (suit_pal[1], suit_pal[2], suit_pal[3]):
                idx = suit_pal.index(cur)
                P(px, x, y, suit_pal[min(idx + 1, 4)])
    # 纽扣（左上高光）
    for y in (66, 74):
        P(px, CX - 1, y, suit_pal[0]); P(px, CX, y, suit_pal[1]); P(px, CX + 1, y, suit_pal[0])
        P(px, CX, y - 1, suit_pal[4])
    # 手臂
    for y in range(46, 84):
        for x in range(CX - 25, CX - 20):
            P(px, x, y, suit_pal[2] if (x + y) % 6 else suit_pal[3])
        P(px, CX - 25, y, OUT); P(px, CX - 20, y, OUT)
        for x in range(CX + 20, CX + 25):
            P(px, x, y, suit_pal[1] if (x + y) % 6 else suit_pal[2])
        P(px, CX + 20, y, OUT); P(px, CX + 25, y, OUT)
    # 手
    for y in range(80, 86):
        for x in range(CX - 25, CX - 20):
            P(px, x, y, SKIN[2] if (x + y) % 5 else SKIN[3])
        for x in range(CX + 20, CX + 25):
            P(px, x, y, SKIN[2] if (x + y) % 5 else SKIN[3])
    P(px, CX - 22, 82, SKIN[4]); P(px, CX + 22, 82, SKIN[4])
    # 裤腿
    for y in range(88, 148):
        for x in range(CX - 14, CX):
            P(px, x, y, GRAY_PANTS[3] if x < CX - 9 else GRAY_PANTS[2])
        for x in range(CX, CX + 14):
            P(px, x, y, GRAY_PANTS[1])
        P(px, CX - 14, y, OUT); P(px, CX + 13, y, OUT)
    hline(px, CX - 14, CX + 13, 147, OUT)
    # 裤纹理
    for y in range(90, 146):
        for x in range(CX - 13, CX + 13):
            cur = px[x, y]
            if (x * 5 + y * 7) % 9 == 0 and cur in (GRAY_PANTS[1], GRAY_PANTS[2], GRAY_PANTS[3]):
                idx = GRAY_PANTS.index(cur)
                P(px, x, y, GRAY_PANTS[min(idx + 1, 4)])
    # 鞋
    for y in range(147, 153):
        for x in range(CX - 14, CX + 13):
            P(px, x, y, SHOE[1] if x < CX else SHOE[2])
    hline(px, CX - 14, CX + 13, 152, OUT); hline(px, CX - 14, CX + 13, 153, OUT)
    P(px, CX + 10, 149, SHOE[2])

# ============ 青年赞比 ============
def young():
    img, px = new_canvas()
    head_base(px, HAIR_BROWN, "swoop")
    suit_body(px, GRAY_SUIT, WHITE_SHIRT, [(120, 40, 44), (150, 52, 58), (180, 64, 70)], "tie")
    return img

# ============ 克隆赞比（灰蓝工装+编号）============
WORK_BLUE = [(40, 52, 68), (58, 74, 96), (76, 96, 124), (96, 120, 152), (118, 144, 178)]
def clone():
    img, px = new_canvas()
    head_base(px, HAIR_BROWN, "buzzcut")
    # 灰蓝工装（连体工作服）
    for y in range(42, 148):
        half = 17 if y < 62 else 14
        half = int(half - (half - 11) * max(0, y - 100) / 48)
        for x in range(CX - half, CX + half + 1):
            rel = x - CX
            if rel < -8:
                P(px, x, y, WORK_BLUE[3])
            elif rel < -2:
                P(px, x, y, WORK_BLUE[2])
            elif rel < 4:
                P(px, x, y, WORK_BLUE[1])
            else:
                P(px, x, y, WORK_BLUE[0])
        P(px, CX - half, y, OUT); P(px, CX + half, y, OUT)
    hline(px, CX - 17, CX + 17, 42, OUT); hline(px, CX - 17, CX + 17, 43, OUT)
    hline(px, CX - 11, CX + 11, 147, OUT)
    # 工装纹理
    for y in range(44, 146):
        for x in range(CX - 16, CX + 17):
            cur = px[x, y]
            if (x * 5 + y * 11) % 9 == 0 and cur in (WORK_BLUE[1], WORK_BLUE[2], WORK_BLUE[3]):
                idx = WORK_BLUE.index(cur)
                P(px, x, y, WORK_BLUE[min(idx + 1, 4)])
    # 编号胸牌（左上）
    for y in range(50, 58):
        for x in range(CX - 15, CX - 7):
            P(px, x, y, (200, 200, 196))
    hline(px, CX - 15, CX - 7, 50, OUT); hline(px, CX - 15, CX - 7, 57, OUT)
    P(px, CX - 15, 50, OUT); P(px, CX - 7, 50, OUT); P(px, CX - 15, 57, OUT); P(px, CX - 7, 57, OUT)
    # 编号 0715（白胸牌上的深数字，简化）
    for dx, dy in [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (1, 5), (2, 5), (3, 5)]:
        P(px, CX - 14 + dx, 50 + dy, (40, 40, 44))
    # 腰带
    hline(px, CX - 14, CX + 14, 82, (40, 44, 52)); hline(px, CX - 14, CX + 14, 83, (40, 44, 52))
    P(px, CX - 2, 82, (150, 150, 140)); P(px, CX - 1, 82, (150, 150, 140))  # 腰带扣
    # 手臂
    for y in range(46, 84):
        for x in range(CX - 20, CX - 15):
            P(px, x, y, WORK_BLUE[2] if (x + y) % 6 else WORK_BLUE[3])
        P(px, CX - 20, y, OUT); P(px, CX - 15, y, OUT)
        for x in range(CX + 15, CX + 20):
            P(px, x, y, WORK_BLUE[1] if (x + y) % 6 else WORK_BLUE[2])
        P(px, CX + 15, y, OUT); P(px, CX + 20, y, OUT)
    for y in range(80, 86):
        for x in range(CX - 20, CX - 15):
            P(px, x, y, SKIN[2] if (x + y) % 5 else SKIN[3])
        for x in range(CX + 15, CX + 20):
            P(px, x, y, SKIN[2] if (x + y) % 5 else SKIN[3])
    P(px, CX - 17, 82, SKIN[4]); P(px, CX + 17, 82, SKIN[4])
    # 鞋
    for y in range(147, 153):
        for x in range(CX - 11, CX + 12):
            P(px, x, y, SHOE[1] if x < CX else SHOE[2])
    hline(px, CX - 11, CX + 12, 152, OUT); hline(px, CX - 11, CX + 12, 153, OUT)
    return img

if __name__ == "__main__":
    save(young(), "young_v3")
    save(clone(), "clone_v3")
