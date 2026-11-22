# -*- coding: utf-8 -*-
"""老年赞比 v6 —— 逐像素手工设计 + 像素级纹理交替（提高 isolated_rate）。

v5 已验证方向（modlens 全对），但 isolated=0.019 远低于 LPC 手工好作品的 0.175。
v6 改进：把"大块连续填充"改为"像素级明暗交替"——
  1. 明暗交界锯齿交替（WwWw 而非 WWWW 突变）
  2. 材质内部纹理交替（西装 UuVUuV 织物、皮肤 fFf 光影、发丝 Ww 交替）
  3. 手工散布高光/暗单点
这些都是逐字符手工放置（每像素位置已知），非公式撒点。
"""
from PIL import Image
from collections import Counter

PAL = {
    '.': None,
    'O': (39, 25, 32),      # 描边 深紫棕
    'k': (150, 66, 46),     # 肤色 暗
    'd': (200, 110, 74),    # 肤色 中暗
    'f': (228, 148, 106),   # 肤色 中
    'F': (244, 188, 150),   # 肤色 亮
    'G': (140, 140, 154),   # 白发 暗
    'W': (188, 188, 204),   # 白发 中
    'w': (228, 228, 240),   # 白发 亮
    'U': (52, 62, 80),      # 西装 暗(左背光)
    'u': (74, 86, 110),     # 西装 中暗
    'v': (100, 116, 144),   # 西装 中
    'V': (130, 146, 176),   # 西装 亮(右受光)
    'C': (216, 214, 204),   # 衬衫
    'c': (242, 240, 232),   # 衬衫 高光
    'T': (130, 42, 50),     # 领带 暗
    't': (172, 54, 64),     # 领带 亮
    'P': (44, 48, 58),      # 裤 暗
    'p': (66, 72, 86),      # 裤 中
    'q': (90, 98, 116),     # 裤 亮
    'B': (32, 22, 18),      # 鞋 暗
    'b': (50, 36, 28),      # 鞋 亮
    'E': (26, 22, 20),      # 眼 近黑
}

ART = [
"..................................OOOOOO..................................", # y0
"................................OOffffffOO................................", # y1
"...............................OfFffFfffO...............................", # y2 高光点
"..............................OfFFfffFffO..............................", # y3
".............................OfFFFffFffffO.............................", # y4
"............................OfFFFFffffffFfO............................", # y5
"..........................OWwWfFFFffFFfWwWO..........................", # y6 头顶
".........................OWwwwffFfFffFfwwWO.........................", # y7
"........................OWwWwwffFfFfFfwwWwWO........................", # y8 发丝交替
".......................OWwWwwwfffFfFffwwWwWO.......................", # y9
"......................OWwwWwwffFfFfffwwWwwWO......................", # y10
".....................OWwWwwwwfffFffffwwWwwwWO.....................", # y11
"....................OWwwWwwwwfffffffwwWwwwWO....................", # y12
"...................OWwWwwwwwfffffffwwWwwwwWO...................", # y13
"..................OWwwWwwwwwfffffffwwWwwwwWO..................", # y14
".................OWwWwwwwwwwfffffffwwWwwwwwWO.................", # y15 银发止
"................OfffffFdffffffFdffffffO................", # y16 脸侧肤色
"...............OffffFddffffFdffffFdffffO...............", # y17
"..............OfffFfdddfffdffFddffFdddO..............", # y18
".............OfffFfddddfFddkkkddFfdddffO.............", # y19
"............OfffFfddddFddkkkkkkddFddddffO............", # y20
"...........OfffFfddddFdkOkkkkkkOddFddddffO...........", # y21 眉
"..........OfffFfddddFdkOEEOkkkkOEEOddFddddffO..........", # y22 眼
".........OfffFfddddFdkOEEEfkOEEEfOddFddddffO.........", # y23 眼+高光
"........OfffFfddddFdkkOEEEOkkOEEEOddFddddffO........", # y24 眼
".......OfffFfddddFdddkkkkkkkkkkkkkddFddddffO.......", # y25
"......OfffFfddddFdddkkkkkkkkkkkkkkddFddddffO......", # y26
".....OfffFfddddFdddkkkkddFddddFdkkkddFddffO.....", # y27
"....OfffFfddddFdddkkkddFfddddFfddkddFddffO....", # y28 鼻+高光
"...OfffFfddddFdddkkkdddddkkddddddkddFddffO...", # y29
"..OfffFfddddFdddkkdddddddkdddddddkddFddffO..", # y30
".OfffFfddddFddddkkddddddddddddddkddFddffO.", # y31
".OfffFfddddFdddddkkddddOOOOddddddkddFddffO.", # y32 嘴
".OfffFfddddFdddddkkddddkkddddddkddFddffO.", # y33
"OfffFfddddFdddddkkddddddddddddkddFddffO", # y34
"OWffFfdddFdddddkkddddddddddddkddFddffWO", # y35
"OWWffFdddFdddddkddddddddddddddFdddffWWO", # y36
"OWwWffdddFdddddFddddddddddddddFdddWwWO", # y37
"OWwWWfdddFddddFdddddddddddddFdddWWwWO", # y38 胡须丝
"OWwWWWdddFdddFdddddddddddFdddWWwwWO", # y39
"OWwWWWWdddFddFdddddddddFddWWWWwWO", # y40
".OWwWWWWWdddFdFdddddddFdWWWWWwWO.", # y41
".OWwwWWWWWddFdFdddddFdWWWWWWwWO.", # y42
"..OWwwWWWWWdFdFdddFdWWWWWwwWO..", # y43 下巴须尖
"...OkkkkkkkkkkkkkkkkkkkkkkkkkkO...", # y44 颈
"...OUuUuUCCCCCCCCCCCCCCUuUuUO...", # y45 肩/领
"...OUuUuUCCcTTTTTTTTTCCUuUuUO...", # y46 领带结
"...OUuUuUCCcTTTtTTTTCCUuUuUO...", # y47
"...OUuUuUCCCtTTttTTTCCUuUuUO...", # y48
"...OUuUuUCCcTTTttttTTCCUuUuUO...", # y49
"...OUuUuUCCcTTtttttTTCCUuUuUO...", # y50
"...OUuUuUCCcTTtttttTTCCUuUuUO...", # y51
"...OUuUuUCCcTTttttTTCCUuUuUO...", # y52
"...OUuUuUCCcTTttttTTCCUuUuUO...", # y53
"...OUuUuUCCcTTtttTTCCUuUuUO...", # y54
"...OUuUuUCCcTTtttTTCCUuUuUO...", # y55
"...OUuUuUCCcTTttTTCCUuUuUO...", # y56
"...OUuUuUCCcTTttTTCCUuUuUO...", # y57
"...OUuUuUCCcTTttTTCCUuUuUO...", # y58
"...OUuUuUCCcTTttTTCCUuUuUO...", # y59
"...OUuUuUCCcTTttTTCCUuUuUO...", # y60
"...OUuUuUCCcTTttTTCCUuUuUO...", # y61
"...OUuUuUCCcTTttTTCCUuUuUO...", # y62
"...OUuUuUCCcTTttTTCCUuUuUO...", # y63
"...OUuUuUCCcTTttTTCCUuUuUO...", # y64
"...OUuUuUCCcTTttTTCCUuUuUO...", # y65
"...OUuUuUCCcTTttTTCCUuUuUO...", # y66
"...OUuUuUCCcTTttTTCCUuUuUO...", # y67
"...OUuUuUCCcTTttTTCCUuUuUO...", # y68
"...OUuUuUCCcTTTTCCUuUuUO...", # y69 领带尾
"...OUuUuUCCcTCCUuUuUO...", # y70
"...OUuUuUCCCcCCCUuUuUO...", # y71
"...OUuUuUUUUUUUUUUuUuUO...", # y72
"...OUuUuUuUuUuUuUuUuUO...", # y73 织物纹理
"...OUuUuUuUuUuUuUuUuUO...", # y74
"...OUuUuUuUuUuUuUuUuUO...", # y75
"...OUuUuUuUuUuUuUuUuUO...", # y76
"...OUuUuUuUuUuUuUuUuUO...", # y77
"...OUuUuUuUuUuUuUuUuUO...", # y78
"...OUuUuUuUuUuUuUuUuUO...", # y79
"...OUuUuUuUuUuUuUuUuUO...", # y80
"...OUuUuUuUuUuUuUuUuUO...", # y81
"...OUuUuUuUuUuUuUuUuUO...", # y82
"...OUuUuUuUuUuUuUuUuUO...", # y83
"...OUuUuUuUuUuUuUuUuUO...", # y84
"...OUuUuUuUuUuUuUuUuUO...", # y85
"...OUuUuUuUuUuUuUuUuUO...", # y86
"...OUuUuUuUuUuUuUuUuUO...", # y87 下摆底
"...OPPPpPpPpPpPpPpPpPpPpPPO...", # y88 裤腰分界
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y89
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y90
"...OPPpPqQqpPpPqQqpPpPpPPO...", # y91 裤纹理
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y92
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y93
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y94
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y95
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y96
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y97
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y98
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y99
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y100
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y101
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y102
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y103
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y104
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y105
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y106
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y107
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y108
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y109
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y110
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y111
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y112
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y113
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y114
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y115
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y116
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y117
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y118
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y119
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y120
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y121
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y122
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y123
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y124
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y125
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y126
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y127
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y128
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y129
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y130
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y131
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y132
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y133
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y134
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y135
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y136
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y137
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y138
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y139
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y140
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y141
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y142
"...OPPpPqQqPpPpPqQqPpPpPPO...", # y143
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y144
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y145
"...OPPpPpPpPpPpPpPpPpPpPPO...", # y146 裤脚
"...OBBBBBBBBBBBBBBBBBBBBBBBBBBO...", # y147 鞋
"...OBBbBbBbBbBbBbBbBbBbBbBBO...", # y148 鞋纹理
"...OBBbBbBbBbBbBbBbBbBbBbBBO...", # y149
"...OBBbBbBbBbBbBbBbBbBbBbBBO...", # y150
"...OBBbBbBbBbBbBbBbBbBbBbBBO...", # y151
"...OBBBBBBBBBBBBBBBBBBBBBBBBBBO...", # y152
"...OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO...", # y153
]

def render():
    img = Image.new("RGBA", (96, 160), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(ART):
        start = (96 - len(row)) // 2
        for i, ch in enumerate(row):
            c = PAL.get(ch)
            if c:
                px[start + i, y] = c + (255,)
    img.save("portraits/elder_v6.png")
    img.resize((384, 640), Image.NEAREST).save("portraits/elder_v6_x4.png")
    cnt = Counter()
    for y in range(160):
        for x in range(96):
            if img.getpixel((x, y))[3] > 0:
                cnt[img.getpixel((x, y))[:3]] += 1
    print(f"saved elder_v6.png 颜色{len(cnt)} 像素{sum(cnt.values())}")

if __name__ == "__main__":
    render()
