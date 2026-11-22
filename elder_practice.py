# -*- coding: utf-8 -*-
"""老年赞比立绘 v2：明确秃顶(中央大片头皮)+分腿裤+白胡子(男性)。
修正 v1 误读：银白残发→"盘发"(女性)、长下摆→"裙"、嘴线→"腮红"。
"""
from PIL import Image

PAL = {
    'O': (26, 26, 46),      # 描边深蓝黑
    'H': (232, 232, 240),   # 银发高光
    'h': (200, 200, 216),   # 银发亮
    'm': (160, 160, 176),   # 银发中
    's': (120, 120, 136),   # 银发暗
    'F': (250, 236, 231),   # 肤高光
    'f': (228, 164, 124),   # 肤亮(主)
    'e': (204, 134, 101),   # 肤中
    'd': (153, 66, 60),     # 肤暗
    'W': (255, 255, 255),   # 白(眼高光/胡子/衬衫)
    'P': (58, 42, 26),      # 深棕虹膜
    'U': (42, 58, 90),      # 西装暗
    'u': (58, 74, 110),     # 西装中暗
    'v': (74, 90, 130),     # 西装中
    'w': (90, 106, 150),    # 西装亮
    'c': (216, 216, 224),   # 衬衫暗白
    'T': (150, 34, 42),     # 领带酒红
    't': (196, 58, 68),     # 领带亮
}

ART = [
"................OOOOOOOOOOO.................", #0 头顶描边
"...............OHHHfffffHHHO................", #1 残发两侧+中央秃
"..............OhhHfffffffHhhO...............", #2
"..............OhhfffffffffhhO...............", #3 残发变薄
"..............OhfffffffffffhO...............", #4
".............OohfffffffffffhoO..............", #5 残发到耳边
".............OofffffffffffffoO..............", #6 耳
".............OoffffffffffffoO...............", #7 残发尾耳后
".............OfffffffffffffO................", #8 额头(全肤色)
".............OffffffFFFFfffO................", #9
".............OffffffffffffO.................", #10
".............OffffffefffffO.................", #11 额头皱纹
".............OfffffffffffffO................", #12
".............OfffeeeeeeeeffO................", #13 眉毛
".............OfffWPWfffWPWfO................", #14 深棕眼+高光
".............OfffffffffffffO................", #15
".............OfffffffefffffO................", #16 鼻
".............OfffffffefffffO................", #17
".............OfffeefeeefffO.................", #18 嘴线
".............OfffWWWWWWWfffO................", #19 白胡子(上唇)
".............OffWWWWWWWWWffO................", #20 白胡子(下巴)
".............OoffWWWWWWWfoO.................", #21 白胡子底
".............OOccccccccccOO..................", #22 衬衫领
"..............OccTTTTTTccO...................", #23 领带
".............OUUuUUuUUuUUUO..................", #24 肩
"............OUUUUUUUUUUUUUUO.................", #25 西装胸
"............OUuUUUUUUUUUUUuUO................", #26
"............OUUUUUUUUUUUUUUUO................", #27
"............OUUuUUUUUUUUUUuUUO...............", #28
"............OUUUUUUUUUUUUUUUO................", #29
"............OcUUUUUUUUUUUUUUcO...............", #30 衬衫V领
"............OccUUUUUUUUUUUUccO...............", #31
".............OccUUUUUUUUUUccO................", #32 腰
"..............OccUUUUUUUUccO.................", #33
".............OUUUUUUUUUUUUUO..................", #34 西装下摆
"............OUUUUUUUUUUUUUUUO.................", #35
"...........OUUUUUUUUUUUUUUUUUO................", #36
"...........OUuUUUUUUUUUUUUUuUO................", #37
"...........OUUUUUUUUUUUUUUUUUO................", #38
"..........OOOOOOOOOOOOOOOOOOOO................", #39 下摆底边(臀)
"..........OUUUUUUUOOUUUUUUUUO.................", #40 分腿(中间分缝)
"..........OUUUUUUUOOUUUUUUUUO.................", #41 左裤腿|右裤腿
"..........OUuUUUUUOOUUUUUuUUO.................", #42
"..........OUUUUUUUOOUUUUUUUUO.................", #43
"..........OUUUUUUUOOUUUUUUUUO.................", #44
"..........OUuUUUUUOOUUUUUuUUO.................", #45
"..........OUUUUUUUOOUUUUUUUUO.................", #46
"..........OUUUUUUUOOUUUUUUUUO.................", #47
"..........OUuUUUUUOOUUUUUuUUO.................", #48
"..........OUUUUUUUOOUUUUUUUUO.................", #49
"..........OUUUUUUUOOUUUUUUUUO.................", #50
"..........OUuUUUUUOOUUUUUuUUO.................", #51
"..........OUUUUUUUOOUUUUUUUUO.................", #52
"..........OUUUUUUUOOUUUUUUUUO.................", #53
"..........OUuUUUUUOOUUUUUuUUO.................", #54
"..........OUUUUUUUOOUUUUUUUUO.................", #55
"..........OOOOOOOOOOOOOOOOOOOO................", #56 裤脚
"..........OddddddddOdddddddO..................", #57 鞋上
"..........OooooooooOoooooooO..................", #58 鞋
"..........OOOOOOOOOOOOOOOOOOOO................", #59 鞋底
]

W, H = 48, 80
img = Image.new("RGB", (W, H), (26, 26, 46))
px = img.load()
for y, row in enumerate(ART):
    for x, ch in enumerate(row):
        if ch in PAL:
            px[x, y] = PAL[ch]

out = img.resize((96, 160), Image.NEAREST)
out.save(r"D:\AAAAI\动画视频尝试\赞比的遗产\portraits\elder_front_lpc.png")
big = img.resize((W*3, H*3), Image.NEAREST)
big.save(r"D:\AAAAI\动画视频尝试\赞比的遗产\portraits\elder_front_lpc_x3.png")
print("saved elder_front_lpc.png")
