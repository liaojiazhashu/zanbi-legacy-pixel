# -*- coding: utf-8 -*-
"""老年赞比 v4 —— 逐像素手工设计（字符串 art，1:1 96x160）。
不用 ellipse/rect/polygon，不用取模撒点。每一行每个字符=一个像素，手工点出
锯齿轮廓 + 簇状明暗 + 手工细节（皱纹/胡须纹理/纽扣高光/头皮老年斑）。
"""
from PIL import Image
from collections import Counter

PAL = {
    '.': None,
    'O': (39, 25, 32),      # 描边 深紫棕
    'k': (150, 66, 46),     # 肤色 暗（下颌/颈侧阴影）
    'd': (200, 110, 74),    # 肤色 中暗（脸侧）
    'f': (228, 148, 106),   # 肤色 中（脸主色）
    'F': (244, 186, 146),   # 肤色 亮（额/颊高光）
    'G': (150, 150, 162),   # 白发 暗
    'W': (196, 196, 210),   # 白发 中
    'w': (232, 232, 242),   # 白发 亮
    'U': (56, 66, 84),      # 西装 暗（左侧背光）
    'u': (76, 88, 112),     # 西装 中暗
    'v': (102, 118, 146),   # 西装 中
    'V': (134, 150, 178),   # 西装 亮（右肩受光）
    'C': (224, 222, 212),   # 衬衫
    'c': (244, 242, 234),   # 衬衫 高光
    'T': (138, 46, 54),     # 领带 暗
    't': (178, 58, 68),     # 领带 亮
    'P': (50, 54, 64),      # 裤 暗
    'p': (72, 78, 92),      # 裤 中
    'q': (96, 104, 122),    # 裤 亮
    'B': (34, 24, 20),      # 鞋 暗
    'b': (52, 38, 30),      # 鞋 亮
    'E': (28, 24, 22),      # 眼 近黑深棕
}

# 每行 96 字符，'.' 为透明。角色占中央 x≈26..70。
ART = [
"................................OOOOOO................................", # y0
"..............................OOffffFFOO..............................", # y1
".............................OfFFFFFFFfO.............................", # y2
"............................OfFFFFFFFFFFO............................", # y3
"...........................OfFFFFFFFFFFfO...........................", # y4
"..........................OffFFFFFFFFFFFFO..........................", # y5
".........................OWffFFwwwwwwFFffWO.........................", # y6 头顶：中央头皮+两侧银发
"........................OWwwffwwwwwwwwffwwWO........................", # y7
".......................OWwwwwfwwwwwwwwfwwwwWO.......................", # y8
"......................OWwwwwwfwwwwwwwwfwwwwwWO......................", # y9
".....................OWwwwwwwfwwwwwwwwfwwwwwwWO.....................", # y10
"....................OWwwwwwwwfwwwwwwwwfwwwwwwwWO....................", # y11
"...................OWwwwwwwwwfwwwwwwwwfwwwwwwwwWO...................", # y12
"..................OWwwwwwwwwwfwwwwwwwwfwwwwwwwwwWO..................", # y13
".................OWwwwwwwwwwwfwwwwwwwwfwwwwwwwwwwWO.................", # y14
"................OWwwwwwwwwwwwfwwwwwwwwfwwwwwwwwwwwWO................", # y15
"...............OWwwwwwwwwwwwwffffffddffffffwwwwwwwwwwWO...............", # y16
"..............OWwwwwwwwwwwwwffffddddddffffwwwwwwwwwwwwWO..............", # y17
".............OWwwwwwwwwwwwwwfdddddddddddffwwwwwwwwwwwwwWO.............", # y18
"............OWwwwwwwwwwwwwwwfddddkkkkdddddffwwwwwwwwwwwwwwWO............", # y19
"...........OWwwwwwwwwwwwwwwwfdddkkkkkkkkddddffwwwwwwwwwwwwwwwWO...........", # y20
"..........OWwwwwwwwwwwwwwwwfdddkkkkkkkkkkdddffwwwwwwwwwwwwwwwWO..........", # y21
".........OWwwwwwwwwwwwwwwwffdddkkkOOkkkkkdddffwwwwwwwwwwwwwwwWO.........", # y22 眉
"........OWwwwwwwwwwwwwwwwfffdddkOEEEOkkkdddfffwwwwwwwwwwwwwwwWO........", # y23 眼
".......OWwwwwwwwwwwwwwwwffffdddkOEEEfOkkdddffffwwwwwwwwwwwwwwwWO.......", # y24 眼
"......OWwwwwwwwwwwwwwwwfffffdddkkOEEEOkkdddfffffwwwwwwwwwwwwwwwWO......", # y25 眼
".....OWwwwwwwwwwwwwwwwfffffddddkkkkkkkkddddfffffwwwwwwwwwwwwwwwWO.....", # y26
"....OWwwwwwwwwwwwwwwwfffffdddddddddddddddfffffwwwwwwwwwwwwwwwWO....", # y27
"...OWwwwwwwwwwwwwwwwfffffdddddddFFdddffffffffwwwwwwwwwwwwwwwWO...", # y28 鼻梁高光
"..OWwwwwwwwwwwwwwwwfffffdddddddFkFddddddfffffwwwwwwwwwwwwwwwWO..", # y29 鼻
".OWwwwwwwwwwwwwwwwfffffddddddddkkdddddddfffffwwwwwwwwwwwwwwwWO.", # y30 鼻
".OWwwwwwwwwwwwwwwwfffffdddddddddddddddddfffffwwwwwwwwwwwwwwwWO.", # y31
".OWwwwwwwwwwwwwwwwfffffddddddddOOOOdddddfffffwwwwwwwwwwwwwwwWO.", # y32 嘴
".OWwwwwwwwwwwwwwwwfffffdddddddddkkddddddfffffwwwwwwwwwwwwwwwWO.", # y33
".OWwwwwwwwwwwwwwwwfffffdddddddddddddddfffffwwwwwwwwwwwwwwwWO.", # y34
"OWwwwwwwwwwwwwwwwwfffffdddddddddddddfffffwwwwwwwwwwwwwwwWO", # y35 胡子开始
"OWwwwwwwwwwwwwwwwwfffffdddddddddddfffffwwwwwwwwwwwwwwWO", # y36
"OWwwwwwwwwwwwwwwwWffffddddddddddffffWwwwwwwwwwwwwwWO", # y37 胡子（银白）
"OWwwwwwwwwwwwwwwWWwwffddddddddffwwWWwwwwwwwwwwwwWO", # y38
"OWwwwwwwwwwwwwwWWwwwwfddddddddwwwwWWwwwwwwwwwwwWO", # y39
"OWwwwwwwwwwwwwWWwwwwwfddddddddwwwwwWWwwwwwwwwwwWO", # y40
".OWwwwwwwwwwwwWWwwwwwWfddddddddwwwwwWWwwwwwwwwwWO.", # y41 下巴胡须尖
"..OWwwwwwwwwwwWWwwwwwwWWffddWWwwwwwwWWwwwwwwwwWO..", # y42
"...OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO...", # y43 颈部/衣领上沿
"....OUUUUUUUUCCCCCCCCCCCCCCCUUUUUUUUUUUUUUUUO....", # y44 衣领
"....OUUUUUUUccTTTTTTTTTTTTTcccUUUUUUUUUUUUUUUO....", # y45 领带结
"....OUUUUUUUcTTTTTTTTTTTTTTTccUUUUUUUUUUUUUUUO....", # y46
"....OUUUUUUccTTttTTTTTTTTTTTcccUUUUUUUUUUUUUUO....", # y47
"....OUUUUUUUcTTTttTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y48
"....OUUUUUUcTTTTTtTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y49
"....OUUUUUUUcTTTTTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y50
"....OUUUUUUcTTTTTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y51
"....OUUUUUUcTTTTTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y52
"....OUUUUUUcTTTTTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y53
"....OUUUUUUUcTTTTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y54
"....OUUUUUUUUcTTTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y55
"....OUUUUUUUUUcTTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y56
"....OUUUUUUUUUUcTTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y57
"....OUUUUUUUUUUUcTTTTTTTTTTccUUUUUUUUUUUUUUO....", # y58 领带渐尖
"....OUUUUUUUUUUUUcTTTTTTTTTccUUUUUUUUUUUUUUO....", # y59
"....OUUUUUUUUUUUUUcTTTTTTTTccUUUUUUUUUUUUUUO....", # y60
"....OUUUUUUUUUUUUUUcTTTTTTTccUUUUUUUUUUUUUUO....", # y61
"....OUUUUUUUUUUUUUUUcTTTTTTccUUUUUUUUUUUUUUO....", # y62
"....OUUUUUUUUUUUUUUUUcTTTTTccUUUUUUUUUUUUUUO....", # y63
"....OUUUUUUUUUUUUUUUUUcTTTTccUUUUUUUUUUUUUUO....", # y64
"....OUUUUUUUUUUUUUUUUUUcTTTccUUUUUUUUUUUUUUO....", # y65
"....OUUUUUUUUUUUUUUUUUUUcTTccUUUUUUUUUUUUUUO....", # y66
"....OUUUUUUUUUUUUUUUUUUUUcTccUUUUUUUUUUUUUUO....", # y67 领带尾
"....OUUUUUUUUUUUUUUUUUUUUUccUUUUUUUUUUUUUUUO....", # y68
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y69 西装下摆
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y70
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y71
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y72
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y73
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y74
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y75
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y76
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y77
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y78
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y79
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y80
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y81
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y82
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y83
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y84
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y85
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y86
"....OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO....", # y87 西装下摆底
"....OPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPO....", # y88 裤腰
"....OPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPO....", # y89
"....OPPPPppppppppppppppppppppppppppppPPPPO....", # y90
"....OPPPPppppppppppppppppppppppppppppPPPPO....", # y91
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y92
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y93
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y94
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y95
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y96
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y97
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y98
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y99
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y100
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y101
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y102
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y103
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y104
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y105
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y106
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y107
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y108
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y109
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y110
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y111
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y112
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y113
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y114
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y115
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y116
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y117
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y118
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y119
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y120
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y121
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y122
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y123
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y124
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y125
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y126
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y127
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y128
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y129
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y130
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y131
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y132
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y133
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y134
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y135
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y136
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y137
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y138
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y139
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y140
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y141
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y142
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y143
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y144
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y145
"....OPPPPppppppppppppppppppppppppppppppPPPO....", # y146 裤脚
"....OBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBO....", # y147 鞋上沿
"....OBBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBBO....", # y148
"....OBBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBBO....", # y149
"....OBBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBBO....", # y150
"....OBBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBBO....", # y151
"....OBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBO....", # y152
"....OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO....", # y153
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
    img.save("portraits/elder_v4.png")
    # 放大 4x 预览
    img.resize((384, 640), Image.NEAREST).save("portraits/elder_v4_x4.png")
    cnt = Counter()
    for y in range(160):
        for x in range(96):
            if img.getpixel((x, y))[3] > 0:
                cnt[img.getpixel((x, y))[:3]] += 1
    print(f"saved elder_v4.png 颜色{len(cnt)} 像素{sum(cnt.values())}")

if __name__ == "__main__":
    render()
