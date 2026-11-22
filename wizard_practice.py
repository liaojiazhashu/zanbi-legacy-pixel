# -*- coding: utf-8 -*-
"""综合创作练习：法师角色正面立绘（LPC 技法：逐像素堆砌+6色调色板+统一描边+暗部色相）
验证 19 份学习笔记的知识内化程度。
坐标系 48×80（每字符=1像素），NEAREST x2 = 96×160 交付规格。
"""
from PIL import Image

# === 调色板（严格按 LPC 规律：每材质 6 色 = 1 描边 + 5 明暗，暗部带色相）===
O = (40, 24, 32)      # 描边 深紫棕 #281820（布料/帽统一描边）
# 紫袍（暗部带蓝相，不是中性灰）
ROBE_D = (45, 27, 61)   # 最暗 #2d1b3d 暗紫
ROBE_4 = (74, 45, 99)   # 暗   #4a2d63
ROBE_3 = (109, 63, 148) # 中   #6d3f94
ROBE_2 = (143, 86, 184) # 亮   #8f56b8
ROBE_1 = (181, 126, 214)# 高光 #b57ed6
# 肤色（LPC 修正版：亮脸，避免暗脸误读）
SKIN_D = (153, 66, 60)  # 暗 #99423c 暖红棕
SKIN_M = (204, 134, 101)# 中 #cc8665
SKIN_L = (228, 164, 124)# 亮 #e4a47c
SKIN_H = (249, 213, 186)# 高光 #f9d5ba
# 白发（银白偏冷，暗部蓝灰，避免读成帽子/绷带）
HAIR_D = (72, 78, 87)   # 暗 #484e57 蓝灰
HAIR_M = (109, 116, 128)# 中 #6d7480
HAIR_L = (154, 160, 173)# 亮 #9aa0ad
HAIR_H = (200, 204, 214)# 高光 #c8ccd6
# 眼睛（深棕虹膜，不用青发光眼）
EYE_D = (41, 60, 73)    # 瞳孔 #293d4b 深棕蓝
EYE_M = (86, 107, 121)  # 虹膜 #566b79
# 法杖木色（3级：木材质递减）
WOOD_D = (66, 55, 39)   # 暗 #423727
WOOD_M = (122, 100, 75) # 中 #7a644b
WOOD_L = (184, 154, 120)# 亮 #b89a78
# 宝石（蓝宝石 3 色，眼睛同源）
GEM_D = (42, 60, 73)    # 暗 #2a3c49
GEM_M = (86, 135, 174)  # 中 #5686ae
GEM_L = (87, 206, 228)  # 亮 #57cee4

PAL = {
    "O": O, "a": ROBE_D, "b": ROBE_4, "c": ROBE_3, "d": ROBE_2, "e": ROBE_1,
    "f": SKIN_D, "g": SKIN_M, "h": SKIN_L, "i": SKIN_H,
    "j": HAIR_D, "k": HAIR_M, "l": HAIR_L, "m": HAIR_H,
    "p": EYE_D, "q": EYE_M,
    "w": WOOD_D, "x": WOOD_M, "y": WOOD_L,
    "r": GEM_D, "s": GEM_M, "t": GEM_L,
    ".": None,
}

# === 法师正面立绘 48×80（逐字符=1像素，手工设计像素簇）===
# 尖帽（弯折）+ 脸 + 白胡须 + 紫袍 A 字下摆 + 右法杖
ART = [
# 尖帽（行 0-13）：帽尖弯折向右，描边 O，紫袍色 a-e
"....................O.............................", #0
"...................OeO............................", #1
"..................OdeO............................", #2
".................OdeeO...........................", #3
"................OdeebO..........................", #4
"...............OdeeecO..........................", #5
"..............OdeeecbO.........................", #6
".............OdeeecbbO.........................", #7
"............OdeeecbbaO........................", #8
"...........OdeeecbbaaO.......................", #9
"..........OdeeecbbaaaO......................", #10
".........OdeeecbbaaaaO.....................", #11
"........OdeeecbbaaaaO....................", #12
# 帽檐（行 13-14）：宽帽檐
"......OOOOOOOOOOOOOOOOOOOOO...............", #13
"................................O.............", #14
# 脸（行 15-26）：亮肤色，白发鬓角，眼睛，鼻，嘴，白胡须
"......jkkkkkkkkkkkkkkkkkkj.................", #15 白发顶部
".....jkllllllllllllllllllkj................", #16
".....jkllhhhhhhhhhhhhhhllkj................", #17 额头（亮肤）
".....jklhhhhhhhhhhhhhhhlkj................", #18
".....jklhphqhhhhhhphqhlkj................", #19 眼睛（深棕虹膜+瞳孔）
".....jklhhhhhhhhhhhhhhhlkj................", #20
".....jklhhhggggggggghhhhlkj................", #21 鼻梁
".....jkllhhhhhhhhhhhhhhllkj................", #22
".....jkllhhhhhfffhhhhllkj................", #23 嘴（暗肤色更明显）
".....jklmmmmmmmmmmmmmmmlkj................", #24 白胡须上
".....jkmmmmmmmmmmmmmmmmmmkj................", #25 白胡须
"......jkkkkkkkkkkkkkkkkkkj.................", #26 胡须下描边
# 身体/长袍（行 27-45）：紫袍，V 领，宽大 A 字下摆
".........OOOOOOOOOOOOOOOOOOO..............", #27 肩部描边
"........OaaaaaaaaaaaaaaaaaaaaO.............", #28 肩
"........OabbbbbbbbbbbbbbbbbbaO.............", #29
"........OabbcccccccccccccccbaO.............", #30 胸
"........OabcccdddddddddddccbaO.............", #31 胸亮部
"........OabcddedddddddddeecbaO.............", #32 高光（胸前隆起）
"........OabcdeeddddddddddecbaO.............", #33
".........OabcddddddddddddccbaO.............", #34 腰
"..........OabccccccccccccccbaO............", #35 腰
"..........OabbbbbbbbbbbbbbbbaO............", #36
".........OabbbbbbbbbbbbbbbbbaO...........", #37 平缓展开
".........OaaaaaaaaaaaaaaaaaaaaO..........", #38
"........OabbbbbbbbbbbbbbbbbbbbaO.........", #39
"........OaaaaaaaaaaaaaaaaaaaaaaO.........", #40
".......OabbbbbbbbbbbbbbbbbbbbbbaO........", #41
".......OaaaaaaaaaaaaaaaaaaaaaaaaO.......", #42
"......OabbbbbbbbbbbbbbbbbbbbbbbbaO......", #43
"......OaaaaaaaaaaaaaaaaaaaaaaaaaaO......", #44
".....OabbbbbbbbbbbbbbbbbbbbbbbbbbaO.....", #45
".....OaaaaaaaaaaaaaaaaaaaaaaaaaaaaO.....", #46 达到最宽(30)
".....OabaaaaaaaaaaaaaaaaaaaaaaaaabO.....", #47 断续褶皱
".....OaaaaaaabaaaaaaaaaaaaaaaaaaaaO.....", #48
".....OaaaaaaaaaaaaaaaaabaaaaaaaaaaO.....", #49 褶皱错位
".....OaaaaabaaaaaaaaaaaaaaaaaaaaaaO.....", #50
".....OaaaaaaaaaaaaaaaaaaaaaaaaabaaO.....", #51
".....OaaaaaaaaaaabaaaaaaaaaaaaaaaaO.....", #52
".....OabaaaaaaaaaaaaaaaaaaaaaaaaaaO.....", #53
".....OaaaaaaaaaaaaaaaaaaaaabaaaaaaO.....", #54
".....OaaaaaabaaaaaaaaaaaaaaaaaaaaaO.....", #55
".....OaaaaaaaaaaaaaaaaaaaaaaaaaaaaO.....", #56
".....OaaaaaaaaabaaaaaaaaaaaaaaaaaaO.....", #57
".....OabaaaaaaaaaaaaaaaaaaaaaaaaaaO.....", #58
".....OaaaaaaaaaaaaaaaaaaaaaabaaaaaO.....", #59
".....OaaaaabaaaaaaaaaaaaaaaaaaaaaaO.....", #60
".....OaaaaaaaaaaaaaaaaaaaaaaaaaaaaO.....", #61
".....OaaaaaaaaaaaaaaaaabaaaaaaaaaaO.....", #62
".....OabaaaaaaaaaaaaaaaaaaaaaaaaaaO.....", #63
".....OaaaaaaaaaaaaaaaaaaaaaaaaaaaaO.....", #64
".....OaaaaaaabaaaaaaaaaaaaaaaaaaaaO.....", #65
".....OaaaaaaaaaaaaaaaaaaaaaabaaaaaO.....", #66
".....OaaaaaaaaaaaaaaaaaaaaaaaaaaaaO.....", #67
".....OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO.....", #68 下摆底边
".....ObbbbbbbbbbbbbbbbbbbbbbbbbbbbO.....", #69 鞋上
".....OooooooooooooooooooooooooooooO.....", #70 鞋（描边色）
".....OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO.....", #71 鞋底
]

# 法杖（右侧，行 8-71）：木杆 + 顶部宝石
STAFF_X = 44  # 法杖 x 位置（下摆右边缘外）
STAFF_TOP = 8  # 宝石顶部

def render():
    img = Image.new("RGBA", (48, 80), (0, 0, 0, 0))
    px = img.load()
    rows = len(ART)
    for y, row in enumerate(ART):
        for x, ch in enumerate(row):
            c = PAL.get(ch)
            if c:
                px[x, y] = c
    # 法杖：木杆（从宝石下到脚底）
    for y in range(STAFF_TOP + 5, 72):
        px[STAFF_X, y] = WOOD_M
        px[STAFF_X + 1, y] = WOOD_D  # 右侧暗部
    # 法杖顶部宝石（圆形，半径 3，带高光）
    gem_cx = STAFF_X
    gem_cy = STAFF_TOP + 3
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            dist = dx*dx + dy*dy
            if dist <= 9:  # 半径 3 圆
                xx, yy = gem_cx + dx, gem_cy + dy
                if 0 <= xx < 48 and 0 <= yy < 80:
                    if dist <= 2:  # 中心
                        px[xx, yy] = GEM_L
                    elif dist <= 5:  # 中间
                        px[xx, yy] = GEM_M
                    else:  # 边缘
                        px[xx, yy] = GEM_D
    # 宝石高光（左上小亮点）
    px[gem_cx - 1, gem_cy - 1] = GEM_L
    px[gem_cx, gem_cy - 2] = GEM_L
    # 法杖顶端（宝石上方细尖）
    px[gem_cx, STAFF_TOP] = GEM_M
    px[gem_cx, STAFF_TOP + 1] = GEM_L

    return img

if __name__ == "__main__":
    img = render()
    # x2 放大到 96×160
    big = img.resize((96, 160), Image.NEAREST)
    out = r"D:\AAAAI\动画视频尝试\赞比的遗产\portraits\wizard_front.png"
    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    big.save(out)
    # 也保存 x4 预览
    big.save(r"D:\AAAAI\动画视频尝试\赞比的遗产\portraits\wizard_front_x4.png")
    # 放大预览图（背景深色便于观察）
    bg = Image.new("RGBA", (96, 160), (26, 26, 46, 255))
    bg.paste(big, (0, 0), big)
    bg.save(r"D:\AAAAI\动画视频尝试\赞比的遗产\portraits\wizard_front_bg.png")
    print("saved", out)
