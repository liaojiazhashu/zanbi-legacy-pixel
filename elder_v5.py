# -*- coding: utf-8 -*-
"""老年赞比 v5 —— 逐像素手工设计（字符串 art，1:1 96x160）。
v4 问题修正：①白发只留头顶两侧(不再框脸=兜帽) ②额头高光收敛(去红斑)
③裤腰分界(西装/裤分离=去长袍) ④领带加宽成结(去徽章) ⑤躯干肩宽腰收(去矩形)
⑥手工纹理点(胡须亮丝/西装织物/老人斑/眼睛高光)适度提高 isolated。
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
"...............................OfFfffffffO...............................", # y2
"..............................OfFFffffffFfO..............................", # y3
".............................OfFFFfffffffffO.............................", # y4
"............................OfFFFFfffffffffO............................", # y5
"..........................OWwWfFFFFFFFfffWwWO..........................", # y6 头顶：中央头皮+两侧窄银发
".........................OWwwwffFFffFFfffwwwWO.........................", # y7
"........................OWwwwwfffFffFfffwwwwWO........................", # y8
".......................OWwwwwwfffFfffFfffwwwwwWO.......................", # y9
"......................OWwwwwwwffFffffffwwwwwwWO......................", # y10
".....................OWwwwwwwwfffffffffwwwwwwwWO.....................", # y11
"....................OWwwwwwwwwfffffffffwwwwwwwwWO....................", # y12
"...................OWwwwwwwwwwfffffffffwwwwwwwwwWO...................", # y13
"..................OWwwwwwwwwwwfffffffffwwwwwwwwwwWO..................", # y14
".................OWwwwwwwwwwwwfffffffffwwwwwwwwwwwWO.................", # y15 银发只到此处
"................OffffffffdffffffffffffdffffffO................", # y16 脸侧转肤色
"...............OfffffffdffffffddffffffdfffffffO...............", # y17
"..............OfffffffddffffddddddffffddfffffffO..............", # y18
".............OfffffffddddffddkkkkddffddddfffffO.............", # y19
"............OfffffffddddddddkkkkkkkkdddddddfffffO............", # y20
"...........OfffffffdddddddkOkkkkkkkOdddddddfffffO...........", # y21 眉
"..........OfffffffdddddddkOEEOkkkkOEEOddddddfffffO..........", # y22 眼+高光
".........OfffffffdddddddkkOEEEfkOEEEfOddddddfffffO.........", # y23 眼
"........OfffffffdddddddkkkOEEEOkkOEEEOddddddfffffO........", # y24 眼
".......OfffffffdddddddddkkkkkkkkkkkkkddddddfffffO.......", # y25
"......OfffffffdddddddddkkkkkkkkkkkkkkddddddfffffO......", # y26
".....OfffffffdddddddddkkkkdddddddddkkkdddddfffffO.....", # y27
"....OfffffffdddddddddkkkddFfddddddFfddkdddddfffffO....", # y28 鼻梁+高光点
"...OfffffffdddddddddkkkdddddkkddddddddkddddddfffffO...", # y29 鼻
"..OfffffffddddddddddkdddddddkdddddddddkdddddfffffO..", # y30
".OfffffffdddddddddddkkddddddddddddddddkdddddfffffO.", # y31
".OfffffffdddddddddddddkkddddOOOOddddddkdddddfffffO.", # y32 嘴
".OfffffffddddddddddddddkkddddkkddddddkkdddfffffO.", # y33
"OfffffffdddddddddddddddkkddddddddddddkdddfffffO", # y34
"OWfffffddddddddddddddddkkddddddddddkddddfffffWO", # y35 胡须开始(鬓角银发)
"OWWffffddddddddddddddddkddddddddddddddddffffWWO", # y36
"OWWWfffddddddddddddddddddddddddddddddddfffWWWO", # y37
"OWwWWfddddddddddddddddddddddddddddddddddWWwWO", # y38 胡须亮丝
"OWwwWWdddddddddddddddddddddddddddddddWWwwWO", # y39
"OWwwWWWWdddddddddddddddddddddddddWWWWwwWO", # y40
".OWwwWWWWWWdddddddddddddddddddWWWWWWwwWO.", # y41
".OWwwwWWWWWWWWWddddddddddWWWWWWWWWwwwWO.", # y42 下巴胡须尖
"..OWwwwwWWWWWWWWWWWWWWWWWWWWWWWWwwwwWO..", # y43
"...OkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkO...", # y44 颈
"...OUUUUUUUCCCCCCCCCCCCCCCCCCUUUUUUUO...", # y45 肩/衣领
"...OUUUUUUCCcTTTTTTTTTTTTTcCCCUUUUUUO...", # y46 领带结(宽)
"...OUUUUUUCCcTTTtTTTTTTtTTTcCCUUUUUUO...", # y47
"...OUUUUUUUCCCtTTttTTTTtTTtCCUUUUUUO...", # y48
"...OUUUUUUUUCCcTTTttttttTTTCCcUUUUUUO...", # y49
"...OUUUUUUUUUCCcTTttttttTTTCCcUUUUUUO...", # y50
"...OUUUUUUUUUUCCcTTttttTTTCCcUUUUUUUO...", # y51
"...OUUUUUUUUUUUCCcTTtttTTTCCcUUUUUUUO...", # y52
"...OUUUUUUUUUUUUCCcTTtttTTCCcUUUUUUUUO...", # y53
"...OUUUUUUUUUUUUUCCcTTtttTTCCcUUUUUUUO...", # y54
"...OUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUUO...", # y55
"...OUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y56
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y57
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y58
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y59
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y60
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y61
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y62
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y63
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y64
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y65
"...OUUUUUUUUUUUUUUUUCCcTTttTTCCcUUUUUUUO...", # y66
"...OUUUUUUUUUUUUUUUUUCCcTTtTTCCcUUUUUUUUO...", # y67
"...OUUUUUUUUUUUUUUUUUUCCcTTTTCCcUUUUUUUUO...", # y68 领带尾略宽
"...OUUUUUUUUUUUUUUUUUUUCCcTTCCcUUUUUUUUUO...", # y69
"...OUUUUUUUUUUUUUUUUUUUUCCcTCCcUUUUUUUUUUO...", # y70
"...OUUUUUUUUUUUUUUUUUUUUUCCCcCCCUUUUUUUUUUO...", # y71
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y72
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y73
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y74
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y75
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y76
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y77
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y78
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y79
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y80
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y81
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y82
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y83
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y84
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y85
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y86
"...OUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUO...", # y87 西装下摆底
"...OPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPO...", # y88 裤腰(明显分界)
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y89
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y90
"...OPPPpppqqqqqqppppppqqqqqqppppppPPPPO...", # y91 裤亮纹
"...OPPPpppqqqqqqppppppqqqqqqppppppPPPPO...", # y92
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y93
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y94
"...OPPPppppqqqqqpppppppqqqqqpppppppPPPPO...", # y95
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y96
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y97
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y98
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y99
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y100
"...OPPPppppqqqqppppppppqqqqpppppppPPPPO...", # y101
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y102
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y103
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y104
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y105
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y106
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y107
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y108
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y109
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y110
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y111
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y112
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y113
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y114
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y115
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y116
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y117
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y118
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y119
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y120
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y121
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y122
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y123
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y124
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y125
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y126
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y127
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y128
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y129
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y130
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y131
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y132
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y133
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y134
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y135
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y136
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y137
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y138
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y139
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y140
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y141
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y142
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y143
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y144
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y145
"...OPPPppppppppppppppppppppppppppppPPPPO...", # y146 裤脚
"...OBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBO...", # y147 鞋
"...OBBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBBO...", # y148
"...OBBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBBO...", # y149
"...OBBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBBO...", # y150
"...OBBbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbBBO...", # y151
"...OBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBO...", # y152
"...OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO...", # y153
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
    img.save("portraits/elder_v5.png")
    img.resize((384, 640), Image.NEAREST).save("portraits/elder_v5_x4.png")
    cnt = Counter()
    for y in range(160):
        for x in range(96):
            if img.getpixel((x, y))[3] > 0:
                cnt[img.getpixel((x, y))[:3]] += 1
    print(f"saved elder_v5.png 颜色{len(cnt)} 像素{sum(cnt.values())}")

if __name__ == "__main__":
    render()
