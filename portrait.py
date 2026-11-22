# -*- coding: utf-8 -*-
"""《赞比的遗产》角色像素立绘引擎 V2（参考 B 站像素动画 + 星露谷美术水准）。

每个角色一个 draw_xxx(d, cx, gy) 函数，画在 256x256 立绘画布上，
脚底对齐 gy，水平居中 cx。角色高约 190-205px。

美学规则（参考视频提取）：
- 每材质 4 层明暗（hi 受光 / mid 基色 / lo 背光 / dk 最深）+ 深色描边（非纯黑）
- 五官精细：眼白+虹膜+瞳孔+高光、眉、鼻、嘴（分表情）
- 发型分层发束，自然发际线，非对称
- 服饰有褶皱线、纹样、金属高光
- 底部镜面倒影（vertical flip 半透明）

generate_sheet() 把角色排成合集图，NEAREST 3x 放大输出 portraits/。
"""
import os
from PIL import Image, ImageDraw, ImageFont

PW, PH = 256, 256

# ---- 通用调色板（每材质 4 层 + 描边）----
OUTLINE = (40, 34, 32)
SKIN = {"hi": (240, 198, 152), "mid": (224, 172, 128), "lo": (182, 132, 94), "dk": (120, 84, 60)}
HAIR_DARK = {"hi": (110, 78, 52), "mid": (82, 58, 42), "lo": (56, 40, 30), "dk": (36, 26, 20)}
HAIR_BROWN = {"hi": (150, 110, 74), "mid": (120, 86, 56), "lo": (90, 64, 42), "dk": (60, 42, 28)}
HAIR_WHITE = {"hi": (244, 244, 244), "mid": (220, 218, 214), "lo": (178, 176, 172), "dk": (128, 126, 122)}
NAVY = {"hi": (128, 156, 194), "mid": (88, 112, 150), "lo": (60, 78, 114), "dk": (34, 46, 72)}
DARKSUIT = {"hi": (108, 116, 132), "mid": (74, 82, 96), "lo": (50, 56, 68), "dk": (30, 34, 42)}
SHIRT = {"hi": (244, 246, 250), "mid": (224, 228, 236), "lo": (184, 190, 200)}
TIE = {"hi": (188, 78, 84), "mid": (150, 52, 58), "lo": (108, 36, 42)}
ICE = {"hi": (170, 250, 255), "mid": (79, 193, 224), "lo": (46, 128, 156), "dk": (26, 78, 100)}
GOLD = {"hi": (246, 224, 150), "mid": (206, 176, 106), "lo": (156, 128, 74)}


def _ell(d, x0, y0, x1, y1, fill, outline=None, w=2):
    d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline, width=w)


def _rr(d, x0, y0, x1, y1, fill, outline=None, w=2):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=w)


def _shade(d, cx, cy, w, h, hi, mid, lo, dk):
    """椭圆体明暗：受光在左上，背光在右下。"""
    d.ellipse([cx - w // 2, cy, cx + w // 2, cy + h], fill=mid)
    d.ellipse([cx - w // 2, cy, cx + w // 4, cy + h], fill=hi)          # 左受光
    d.ellipse([cx + w // 4, cy + h // 2, cx + w // 2, cy + h], fill=lo)  # 右下背光
    d.ellipse([cx + w // 3, cy + h - 4, cx + w // 2, cy + h], fill=dk)


def _eyes(d, cx, ey, sep, iris=(70, 120, 160), brow=None, brow_tilt=0, bags=False):
    """双眼 + 眉。sep=眼间距。brow_tilt 正=上扬 负=下垂。"""
    for side in (-1, 1):
        ex = cx + side * sep
        # 眼白 + 虹膜 + 瞳孔 + 高光
        d.ellipse([ex - 7, ey - 4, ex + 7, ey + 4], fill=(252, 252, 252), outline=OUTLINE, width=1)
        d.ellipse([ex - 3, ey - 2, ex + 3, ey + 2], fill=iris)
        d.point((ex, ey), fill=(20, 24, 30))
        d.point((ex + 2, ey - 2), fill=(255, 255, 255))
        # 上眼睑
        d.line([(ex - 7, ey - 4), (ex + 7, ey - 4)], fill=OUTLINE, width=1)
        if bags:
            # 眼袋：眼睛下方淡淡暗色椭圆（浮肿感），非横线（避免被读成眼镜）
            d.ellipse([ex - 6, ey + 4, ex + 6, ey + 9], fill=SKIN["lo"])
    if brow is not None:
        for side in (-1, 1):
            bx = cx + side * sep
            d.line([(bx - 8, ey - 9 - brow_tilt), (bx + 8, ey - 9 + brow_tilt)],
                   fill=brow, width=3)


def _nose(d, cx, ey, mouth_off=18):
    d.line([(cx, ey + 5), (cx - 2, ey + 13), (cx + 3, ey + 15)], fill=SKIN["dk"], width=2)


def _mouth(d, cx, my, w=9, expr="calm", color=(150, 92, 78)):
    """嘴：calm 抿嘴 / smile 微笑 / sad 悲伤 / frown 倔强 / open 微张。"""
    if expr == "calm":
        d.line([(cx - w, my), (cx + w, my)], fill=color, width=2)
    elif expr == "smile":
        d.arc([cx - w, my - 5, cx + w, my + 5], 20, 160, fill=color, width=2)
    elif expr == "sad":
        d.arc([cx - w, my + 2, cx + w, my + 12], 200, 340, fill=color, width=2)
    elif expr == "frown":
        d.line([(cx - w, my), (cx + w, my)], fill=color, width=2)
        d.line([(cx - w, my), (cx - w - 2, my + 1)], fill=color, width=1)
        d.line([(cx + w, my), (cx + w + 2, my + 1)], fill=color, width=1)
    elif expr == "open":
        d.ellipse([cx - 4, my - 2, cx + 4, my + 4], fill=(110, 52, 44))


def _head(d, cx, top, w, h, skin=SKIN, outline=OUTLINE):
    """椭圆头 + 描边 + 脸颊阴影。返回 (top, chin)。"""
    chin = top + h
    d.ellipse([cx - w // 2, top, cx + w // 2, chin], fill=skin["mid"], outline=outline, width=2)
    d.ellipse([cx - w // 2, top, cx - w // 6, chin - 8], fill=skin["hi"])       # 左受光
    d.ellipse([cx + w // 4, chin - 26, cx + w // 2 - 2, chin - 2], fill=skin["lo"])  # 右下阴影
    return top, chin


def _body_suit(d, cx, top, w, bot, suit=NAVY, shirt=SHIRT, tie=TIE, tie_color=None):
    """西装上身：翻领 + 衬衫 V 领 + 领带 + 纽扣。返回 shoulder_y。"""
    sh = top + 12
    # 西装主体
    d.rectangle([cx - w // 2, top, cx + w // 2, bot], fill=suit["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx - w // 2, top, cx - w // 2 + 8, bot], fill=suit["dk"])       # 左暗
    d.rectangle([cx + w // 2 - 8, top, cx + w // 2, bot], fill=suit["lo"])       # 右次暗
    d.rectangle([cx - w // 2 + 8, top, cx + w // 2 - 8, top + 10], fill=suit["hi"])  # 肩受光
    # 翻领（V 形深色）
    for side in (-1, 1):
        d.polygon([(cx + side * 6, sh), (cx + side * 20, sh + 28), (cx + side * 6, sh + 40)],
                  fill=suit["dk"])
    # 衬衫 V 领
    d.polygon([(cx - 9, sh), (cx + 9, sh), (cx + 5, sh + 30), (cx - 5, sh + 30)],
              fill=shirt["mid"])
    d.polygon([(cx - 9, sh), (cx - 2, sh + 20), (cx - 5, sh + 30), (cx - 9, sh + 30)],
              fill=shirt["lo"])
    # 领带
    tc = tie_color or TIE
    d.polygon([(cx - 5, sh + 4), (cx + 5, sh + 4), (cx + 2, sh + 20),
               (cx, sh + 38), (cx - 2, sh + 20)], fill=tc["mid"])
    d.polygon([(cx - 5, sh + 4), (cx, sh + 8), (cx - 2, sh + 20)], fill=tc["hi"])
    d.rectangle([cx - 4, sh + 2, cx + 4, sh + 9], fill=tc["mid"], outline=tc["lo"], width=1)
    # 纽扣
    for by in (sh + 48, sh + 58):
        d.ellipse([cx - 2, by - 2, cx + 2, by + 2], fill=suit["hi"], outline=suit["dk"], width=1)
    return sh


def _arms(d, cx, sh, bot, suit, skin=SKIN, sleeve_len=None):
    """双臂自然下垂。返回手部 y。"""
    hand_y = bot - 40 if sleeve_len is None else sleeve_len
    for side in (-1, 1):
        ax = cx + side * (42)
        d.rectangle([ax - 9, sh + 6, ax + 9, hand_y], fill=suit["mid"], outline=OUTLINE, width=2)
        d.rectangle([ax - 9, sh + 6, ax - 3, hand_y], fill=suit["dk"])
        d.ellipse([ax - 6, hand_y - 2, ax + 6, hand_y + 12], fill=skin["mid"])
        d.ellipse([ax - 6, hand_y - 2, ax, hand_y + 12], fill=skin["hi"])
    return hand_y


def _head_side(d, cx, top, w, h, facing=1, skin=SKIN):
    """侧面头：后脑勺圆润 + 鼻子凸出（facing=1 朝右 / -1 朝左）。返回 (top, chin, nose_tip_x)。"""
    chin = top + h
    f = facing
    d.ellipse([cx - w // 2, top, cx + w // 2, chin], fill=skin["mid"], outline=OUTLINE, width=2)
    d.ellipse([cx - f * w // 2, top, cx - f * w // 8, chin], fill=skin["hi"])   # 后脑受光
    d.ellipse([cx + f * w // 4, chin - 18, cx + f * w // 2, chin], fill=skin["lo"])  # 下颌
    # 鼻子凸出（向前）
    nx = cx + f * (w // 2)
    nh = max(6, h // 6)
    d.polygon([(nx - f * 3, top + h // 3), (nx + f * nh, top + h // 2),
               (nx - f * 3, top + h // 2 + 5)], fill=skin["mid"], outline=OUTLINE, width=1)
    return top, chin, nx + f * nh


def _eye_side(d, cx, ey, facing=1, iris=(70, 120, 160), brow=None):
    """侧面单眼（在鼻子后方）。"""
    f = facing
    ex = cx + f * 3
    d.ellipse([ex - 5, ey - 3, ex + 5, ey + 3], fill=(252, 252, 252), outline=OUTLINE, width=1)
    d.ellipse([ex - 2, ey - 1, ex + 2, ey + 2], fill=iris)
    d.point((ex + f, ey), fill=(20, 24, 30))
    d.point((ex + f * 2, ey - 2), fill=(255, 255, 255))
    if brow is not None:
        d.line([(ex - 6, ey - 8), (ex + 6, ey - 8)], fill=brow, width=2)


def _reflection(img, cx, gy, strength=0.20):
    """底部镜面倒影：把整个立绘垂直翻转 + 半透明，贴到脚底下方。"""
    flip = img.transpose(Image.FLIP_TOP_BOTTOM)
    flip = flip.resize((img.width, int(img.height * 0.5)), Image.NEAREST)
    flip.putalpha(Image.new("L", flip.size, 0).point(lambda a: int(255 * strength)))
    # 倒影顶部对齐脚底 gy
    img.alpha_composite(flip, (0, gy))


# ============================================================
# 1. 老年赞比（79 岁临终：白发稀疏 + 藏青西装 + 酒红领带 + 怀表链）
# ============================================================
def elder_portrait(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(62), S(56)
    # 头
    _head(d, cx, top, head_w, head_h)
    chin = top + head_h
    # 头发：发际线后移的稀疏白发（顶部 + 两侧鬓发）
    d.ellipse([cx - head_w // 2, top - 2, cx + head_w // 2, top + S(16)], fill=HAIR_WHITE["mid"])
    d.ellipse([cx - head_w // 2, top - 2, cx + head_w // 4, top + S(16)], fill=HAIR_WHITE["hi"])
    d.ellipse([cx + head_w // 4, top + S(6), cx + head_w // 2, top + S(16)], fill=HAIR_WHITE["lo"])
    # 额前几缕
    for i, dx in enumerate((-S(16), -S(6), S(6), S(16))):
        d.line([(cx + dx, top + S(8)), (cx + dx, top + S(18))], fill=HAIR_WHITE["lo"], width=2)
    # 两侧鬓发（稀疏，贴耳）
    for side in (-1, 1):
        d.ellipse([cx + side * (head_w // 2 - 4) - 5, top + S(16),
                   cx + side * (head_w // 2 - 4) + 5, chin - S(8)], fill=HAIR_WHITE["mid"])
        d.ellipse([cx + side * (head_w // 2 - 4) - 5, chin - S(20),
                   cx + side * (head_w // 2 - 4) + 3, chin - S(8)], fill=HAIR_WHITE["lo"])
    # 五官
    ey = top + S(30)
    _eyes(d, cx, ey, S(15), iris=(70, 118, 158), brow=HAIR_WHITE["lo"], brow_tilt=-2, bags=True)
    _nose(d, cx, ey)
    _mouth(d, cx, ey + S(26), w=S(8), expr="calm")
    # 法令纹 + 额头纹
    for side in (-1, 1):
        d.line([(cx + side * S(10), ey + S(14)), (cx + side * S(8), ey + S(26))], fill=SKIN["lo"], width=2)
    for i, wx in enumerate((S(22), S(30), S(38))):
        d.line([(cx - wx, top + S(20) + i * 5), (cx + wx, top + S(20) + i * 5)], fill=SKIN["lo"], width=1)
    # 身体
    body_top = chin + S(2)
    body_w = S(80)
    sh = _body_suit(d, cx, body_top, body_w, gy - S(62))
    # 腿 + 鞋
    d.rectangle([cx - S(20), gy - S(62), cx - S(6), gy], fill=NAVY["lo"], outline=OUTLINE, width=2)
    d.rectangle([cx + S(6), gy - S(62), cx + S(20), gy], fill=NAVY["lo"], outline=OUTLINE, width=2)
    d.rectangle([cx - S(22), gy - S(8), cx - S(6), gy], fill=(28, 30, 36))
    d.rectangle([cx + S(6), gy - S(8), cx + S(22), gy], fill=(28, 30, 36))
    # 手臂
    _arms(d, cx, sh, gy - S(40), NAVY)
    # 怀表链
    d.arc([cx + S(10), sh + S(30), cx + S(26), sh + S(46)], 240, 320, fill=GOLD["mid"], width=2)
    d.ellipse([cx + S(22), sh + S(34), cx + S(27), sh + S(40)], fill=GOLD["hi"], outline=GOLD["lo"], width=1)
    # 底部阴影
    d.ellipse([cx - S(40), gy - 4, cx + S(40), gy + 2], fill=(36, 38, 44))


# ============================================================
# 2. 少年赞比（10 岁孤儿：乱发 + 补丁破衣 + 木拐杖 + 左腿残端 + 芯片）
# ============================================================
def boy_portrait(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    _head(d, cx, top, head_w, head_h)
    chin = top + head_h
    # 乱发（多束，深棕，遮额）
    for dx, ww, hh in ((-S(24), S(24), S(16)), (-S(8), S(28), S(18)), (S(8), S(28), S(16)), (S(24), S(22), S(14))):
        d.ellipse([cx + dx - ww // 2, top - 4, cx + dx + ww // 2, top + hh], fill=HAIR_DARK["mid"])
    d.ellipse([cx - head_w // 2, top - 2, cx + head_w // 4, top + S(14)], fill=HAIR_DARK["hi"])
    # 刘海（遮额，锯齿）
    d.polygon([(cx - S(28), top + S(14)), (cx - S(14), top + S(6)), (cx, top + S(12)),
               (cx + S(14), top + S(6)), (cx + S(28), top + S(14)),
               (cx + S(24), top + S(22)), (cx - S(24), top + S(22))], fill=HAIR_DARK["mid"])
    # 脏污
    d.ellipse([cx + S(10), chin - S(26), cx + head_w // 2 - 4, chin - S(6)], fill=SKIN["lo"])
    # 五官（倔强）
    ey = top + S(28)
    _eyes(d, cx, ey, S(14), iris=(74, 104, 62), brow=HAIR_DARK["dk"], brow_tilt=3)
    _nose(d, cx, ey)
    _mouth(d, cx, ey + S(24), w=S(7), expr="frown")
    # 身体（破衣）
    body_top = chin + S(2)
    body_w = S(70)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(50)], fill=(120, 92, 60), outline=OUTLINE, width=2)
    d.rectangle([cx - body_w // 2, body_top, cx - body_w // 2 + 7, gy - S(50)], fill=(96, 72, 46))
    d.rectangle([cx + body_w // 2 - 7, body_top, cx + body_w // 2, gy - S(50)], fill=(96, 72, 46))
    # 补丁（两块，缝线）
    for px, py, pw, ph in ((S(6), S(18), S(16), S(16)), (-S(28), S(42), S(16), S(14))):
        d.rectangle([cx + px, body_top + py, cx + px + pw, body_top + py + ph],
                    fill=(156, 124, 84), outline=(90, 68, 44), width=1)
        for i in range(3):
            d.point((cx + px + 4 + i * 4, body_top + py + 3), fill=(90, 68, 44))
            d.point((cx + px + 4 + i * 4, body_top + py + ph - 3), fill=(90, 68, 44))
    # 破洞
    d.ellipse([cx - S(18), body_top + S(62), cx - S(10), body_top + S(72)], fill=(70, 54, 38))
    # 右腿（唯一站立的腿）
    d.rectangle([cx + S(2), gy - S(56), cx + S(15), gy], fill=(84, 70, 50), outline=OUTLINE, width=2)
    d.rectangle([cx + S(2), gy - S(56), cx + S(6), gy], fill=(96, 80, 58))
    d.ellipse([cx + S(2), gy - S(8), cx + S(17), gy], fill=(40, 34, 30))
    # 左腿残端（悬空裤管，膝下打结，明显不触地）
    d.rectangle([cx - S(16), gy - S(48), cx - S(4), gy - S(24)], fill=(84, 70, 50), outline=OUTLINE, width=2)
    d.rectangle([cx - S(16), gy - S(48), cx - S(11), gy - S(24)], fill=(96, 80, 58))
    # 裤管口打结（扎紧的结，悬空）
    d.polygon([(cx - S(15), gy - S(28)), (cx - S(5), gy - S(28)),
               (cx - S(7), gy - S(18)), (cx - S(13), gy - S(18))],
              fill=(70, 56, 40), outline=OUTLINE, width=1)
    d.line([(cx - S(12), gy - S(18)), (cx - S(12), gy - S(13))], fill=(70, 56, 40), width=2)
    d.line([(cx - S(8), gy - S(18)), (cx - S(8), gy - S(14))], fill=(70, 56, 40), width=2)
    # 木拐杖（右腋下斜撑，T 形横档，明显超出身体）
    crutch_top = body_top + S(4)
    d.line([(cx + S(26), crutch_top), (cx + S(46), gy)], fill=(108, 76, 48), width=7)
    d.line([(cx + S(27), crutch_top), (cx + S(47), gy)], fill=(152, 110, 70), width=3)
    # 腋下横档（T 形）
    d.line([(cx + S(20), crutch_top + S(6)), (cx + S(34), crutch_top + S(6))], fill=(108, 76, 48), width=5)
    d.line([(cx + S(20), crutch_top + S(6)), (cx + S(34), crutch_top + S(6))], fill=(152, 110, 70), width=2)
    # 拐杖底部防滑
    d.ellipse([cx + S(43), gy - S(4), cx + S(50), gy], fill=(60, 44, 30))
    # 左臂（弯曲，手举芯片到胸前）
    ax = cx - S(22)
    d.rectangle([ax - 6, body_top + S(10), ax + 6, body_top + S(32)], fill=(120, 92, 60), outline=OUTLINE, width=2)
    d.ellipse([ax - 5, body_top + S(26), ax + 5, body_top + S(36)], fill=SKIN["mid"])
    # 左手芯片（冰青发光，举在胸前）
    chip_y = body_top + S(30)
    d.rectangle([ax - 4, chip_y - 3, ax + 4, chip_y + 5], fill=ICE["mid"], outline=ICE["hi"], width=1)
    d.point((ax, chip_y), fill=ICE["hi"])
    # 右臂（搭在拐杖横档上）
    ax2 = cx + S(26)
    d.rectangle([ax2 - 6, body_top + S(10), ax2 + 6, crutch_top + S(10)], fill=(120, 92, 60), outline=OUTLINE, width=2)
    d.ellipse([ax2 - 5, crutch_top + S(4), ax2 + 5, crutch_top + S(14)], fill=SKIN["mid"])
    # 底部阴影
    d.ellipse([cx - S(40), gy - 4, cx + S(46), gy + 2], fill=(36, 38, 44))


# ============================================================
# 3. 青年赞比（26 岁创业：利落短发 + 深灰西装 + 自信微笑）
# ============================================================
def young_portrait(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    _head(d, cx, top, head_w, head_h)
    chin = top + head_h
    # 利落短发（深棕，后梳）
    d.ellipse([cx - head_w // 2, top - 4, cx + head_w // 2, top + S(18)], fill=HAIR_BROWN["mid"])
    d.ellipse([cx - head_w // 2, top - 4, cx + head_w // 4, top + S(18)], fill=HAIR_BROWN["hi"])
    d.ellipse([cx + head_w // 4, top + S(6), cx + head_w // 2, top + S(18)], fill=HAIR_BROWN["lo"])
    # 分发线
    d.line([(cx - S(6), top), (cx - S(2), top + S(16))], fill=HAIR_BROWN["dk"], width=2)
    # 五官（自信）
    ey = top + S(28)
    _eyes(d, cx, ey, S(15), iris=(78, 108, 66), brow=HAIR_BROWN["dk"], brow_tilt=1)
    _nose(d, cx, ey)
    _mouth(d, cx, ey + S(24), w=S(8), expr="smile")
    # 身体（深灰西装）
    body_top = chin + S(2)
    body_w = S(78)
    sh = _body_suit(d, cx, body_top, body_w, gy - S(60), suit=DARKSUIT)
    # 腿鞋
    d.rectangle([cx - S(20), gy - S(60), cx - S(6), gy], fill=DARKSUIT["lo"], outline=OUTLINE, width=2)
    d.rectangle([cx + S(6), gy - S(60), cx + S(20), gy], fill=DARKSUIT["lo"], outline=OUTLINE, width=2)
    d.rectangle([cx - S(22), gy - S(8), cx - S(6), gy], fill=(26, 28, 34))
    d.rectangle([cx + S(6), gy - S(8), cx + S(22), gy], fill=(26, 28, 34))
    _arms(d, cx, sh, gy - S(38), DARKSUIT)
    # 胸针（公司 logo 光点）
    d.ellipse([cx + S(22), sh + S(14), cx + S(28), sh + S(20)], fill=ICE["mid"], outline=ICE["hi"], width=1)
    d.ellipse([cx - S(40), gy - 4, cx + S(40), gy + 2], fill=(36, 38, 44))


# ============================================================
# 4. 克隆赞比（年轻力壮版：深棕发 + 藏青西装 + 无表情冷静）
# ============================================================
def clone_portrait(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    _head(d, cx, top, head_w, head_h)
    chin = top + head_h
    # 深棕发（与老年赞比同款但深色、浓密）
    d.ellipse([cx - head_w // 2, top - 4, cx + head_w // 2, top + S(18)], fill=HAIR_DARK["mid"])
    d.ellipse([cx - head_w // 2, top - 4, cx + head_w // 4, top + S(18)], fill=HAIR_DARK["hi"])
    d.ellipse([cx + head_w // 4, top + S(6), cx + head_w // 2, top + S(18)], fill=HAIR_DARK["lo"])
    for side in (-1, 1):
        d.ellipse([cx + side * (head_w // 2 - 4) - 5, top + S(16),
                   cx + side * (head_w // 2 - 4) + 5, chin - S(8)], fill=HAIR_DARK["mid"])
    # 五官（无表情，平眉）
    ey = top + S(30)
    _eyes(d, cx, ey, S(15), iris=(70, 118, 158), brow=HAIR_DARK["mid"], brow_tilt=0)
    _nose(d, cx, ey)
    _mouth(d, cx, ey + S(26), w=S(7), expr="calm")
    # 身体（藏青西装，同款）
    body_top = chin + S(2)
    body_w = S(80)
    sh = _body_suit(d, cx, body_top, body_w, gy - S(62))
    d.rectangle([cx - S(20), gy - S(62), cx - S(6), gy], fill=NAVY["lo"], outline=OUTLINE, width=2)
    d.rectangle([cx + S(6), gy - S(62), cx + S(20), gy], fill=NAVY["lo"], outline=OUTLINE, width=2)
    d.rectangle([cx - S(22), gy - S(8), cx - S(6), gy], fill=(28, 30, 36))
    d.rectangle([cx + S(6), gy - S(8), cx + S(22), gy], fill=(28, 30, 36))
    _arms(d, cx, sh, gy - S(40), NAVY)
    d.ellipse([cx - S(40), gy - 4, cx + S(40), gy + 2], fill=(36, 38, 44))


# ============================================================
# 5. 机械赞比（半具机器人：金属躯干 + 发光眼带 + 核心灯 + 线缆下半身）
# ============================================================
def mech_portrait(d, cx, gy, h=190):
    k = h / 190.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(56), S(44)
    # 金属头（圆角矩形）
    d.rounded_rectangle([cx - head_w // 2, top, cx + head_w // 2, top + head_h],
                        radius=S(8), fill=(74, 84, 100), outline=OUTLINE, width=2)
    d.rounded_rectangle([cx - head_w // 2, top, cx - head_w // 6, top + head_h],
                        radius=S(8), fill=(96, 108, 126))
    # 发光眼带（冰青横条）
    d.rectangle([cx - S(18), top + S(16), cx + S(18), top + S(24)], fill=ICE["mid"], outline=ICE["hi"], width=1)
    d.rectangle([cx - S(18), top + S(16), cx + S(18), top + S(19)], fill=ICE["hi"])
    # 金属下巴
    d.line([(cx - S(8), top + S(34)), (cx + S(8), top + S(34))], fill=(50, 56, 68), width=2)
    # 后脑光纤束
    for i in range(5):
        d.line([(cx + head_w // 2, top + S(10) + i * 6), (cx + head_w // 2 + S(18), top + S(4) + i * 7)],
               fill=ICE["mid"], width=2)
    # 躯干（金属胸甲）
    body_top = top + head_h + S(4)
    body_w = S(70)
    d.rounded_rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(46)],
                        radius=S(6), fill=(74, 84, 100), outline=OUTLINE, width=2)
    d.rounded_rectangle([cx - body_w // 2, body_top, cx - body_w // 6, gy - S(46)],
                        radius=S(6), fill=(96, 108, 126))
    # 胸口核心灯（圆形，冰青，发光）
    core = gy - S(46) - S(14)
    for rr, aa in ((S(16), 30), (S(12), 60), (S(8), 120)):
        d.ellipse([cx - rr, core - rr, cx + rr, core + rr], outline=(120, 220, 250), width=1)
    d.ellipse([cx - S(7), core - S(7), cx + S(7), core + S(7)], fill=ICE["hi"], outline=ICE["mid"], width=2)
    d.point((cx - S(2), core - S(2)), fill=(255, 255, 255))
    # 金属腹甲纹路
    for i in range(3):
        y = core + S(16) + i * S(7)
        d.line([(cx - S(20), y), (cx + S(20), y)], fill=(50, 56, 68), width=2)
    # 线缆下半身（从腰向下散开，无腿）
    cable_top = gy - S(46)
    for i, (dx, c) in enumerate([(-S(24), (190, 70, 60)), (-S(12), (200, 160, 70)),
                                 (S(0), (110, 130, 160)), (S(12), (190, 70, 60)), (S(24), (200, 160, 70))]):
        sway = S(4) * (1 if i % 2 == 0 else -1)
        d.line([(cx + dx, cable_top), (cx + dx + sway, (cable_top + gy) // 2), (cx + dx, gy)],
               fill=c, width=3)
    # 机械臂（两侧）
    for side in (-1, 1):
        ax = cx + side * S(40)
        d.rectangle([ax - 8, body_top + S(10), ax + 8, gy - S(40)], fill=(74, 84, 100), outline=OUTLINE, width=2)
        d.ellipse([ax - 6, gy - S(40), ax + 6, gy - S(28)], fill=(96, 108, 126), outline=OUTLINE, width=2)
        d.line([(ax - 6, gy - S(34)), (ax + 6, gy - S(34))], fill=ICE["mid"], width=2)
    d.ellipse([cx - S(38), gy - 4, cx + S(38), gy + 2], fill=(36, 38, 44))


# ============================================================
# 6. 立方体（最终形态：黑色立方体 + 冰青边缘光，悬浮）
# ============================================================
def cube_portrait(d, cx, gy, h=190):
    k = h / 190.0
    S = lambda v: int(v * k)
    s = S(64)  # 立方体半边长
    top = gy - h + S(20)
    # 悬浮光晕
    for rr, aa in ((s + S(14), 24), (s + S(8), 40), (s + S(3), 60)):
        d.ellipse([cx - rr, top + s - rr, cx + rr, top + s + rr], outline=(79, 193, 224), width=1)
    # 立方体主体（等距视角：顶面 + 正面 + 右面）
    d.polygon([(cx - s, top + s // 2), (cx, top), (cx + s, top + s // 2), (cx, top + s)],
              fill=(40, 50, 66), outline=OUTLINE, width=2)          # 顶面
    d.polygon([(cx - s, top + s // 2), (cx, top + s), (cx, top + s * 2 - s // 2),
               (cx - s, top + s + s // 2)], fill=(16, 20, 28), outline=OUTLINE, width=2)  # 正面
    d.polygon([(cx, top + s), (cx + s, top + s // 2), (cx + s, top + s + s // 2),
               (cx, top + s * 2 - s // 2)], fill=(10, 13, 18), outline=OUTLINE, width=2)  # 右面
    # 冰青边缘光（底 + 右 + 顶）
    d.line([(cx - s, top + s + s // 2), (cx, top + s * 2 - s // 2),
            (cx + s, top + s + s // 2)], fill=ICE["hi"], width=2)
    d.line([(cx + s, top + s // 2), (cx + s, top + s + s // 2)], fill=ICE["mid"], width=2)
    d.line([(cx, top), (cx + s, top + s // 2)], fill=ICE["mid"], width=1)
    # 中心微光
    d.point((cx, top + s), fill=ICE["hi"])
    # 悬浮粒子
    for i, (px, py) in enumerate(((-S(30), -S(10)), (S(26), S(6)), (-S(20), S(16)))):
        d.point((cx + px, top + s + py), fill=ICE["mid"])
    d.ellipse([cx - S(30), gy - 4, cx + S(30), gy + 2], fill=(36, 38, 44))


# ============================================================
# 7. 理查德·史密斯（叙述者律师：深棕分头 + 领结 + 深蓝西装 + 文件夹）
# ============================================================
def richard_portrait(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    _head(d, cx, top, head_w, head_h)
    chin = top + head_h
    # 分头（深棕，三七分）
    d.ellipse([cx - head_w // 2, top - 4, cx + head_w // 2, top + S(18)], fill=HAIR_DARK["mid"])
    d.ellipse([cx - head_w // 2, top - 4, cx + head_w // 4, top + S(18)], fill=HAIR_DARK["hi"])
    d.line([(cx - S(10), top - 2), (cx - S(4), top + S(16))], fill=HAIR_DARK["dk"], width=2)
    # 五官（严肃关切）
    ey = top + S(28)
    _eyes(d, cx, ey, S(15), iris=(80, 74, 66), brow=HAIR_DARK["mid"], brow_tilt=-1)
    _nose(d, cx, ey)
    _mouth(d, cx, ey + S(24), w=S(7), expr="calm")
    # 身体（深蓝西装 + 领结）
    body_top = chin + S(2)
    body_w = S(78)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(60)], fill=NAVY["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx - body_w // 2, body_top, cx - body_w // 2 + 8, gy - S(60)], fill=NAVY["dk"])
    d.rectangle([cx + body_w // 2 - 8, body_top, cx + body_w // 2, gy - S(60)], fill=NAVY["lo"])
    sh = body_top + S(12)
    # 领结（蝴蝶结，替代领带）
    d.polygon([(cx - S(10), sh + S(2)), (cx, sh + S(8)), (cx - S(10), sh + S(14))], fill=TIE["mid"])
    d.polygon([(cx + S(10), sh + S(2)), (cx, sh + S(8)), (cx + S(10), sh + S(14))], fill=TIE["mid"])
    d.rectangle([cx - S(4), sh + S(6), cx + S(4), sh + S(10)], fill=TIE["lo"])
    # 白衬衫
    d.polygon([(cx - S(12), sh), (cx + S(12), sh), (cx + S(6), sh + S(22)), (cx - S(6), sh + S(22))],
              fill=SHIRT["mid"])
    # 纽扣
    for by in (sh + S(30), sh + S(40)):
        d.ellipse([cx - 2, by - 2, cx + 2, by + 2], fill=NAVY["hi"], outline=NAVY["dk"], width=1)
    # 腿鞋
    d.rectangle([cx - S(20), gy - S(60), cx - S(6), gy], fill=NAVY["lo"], outline=OUTLINE, width=2)
    d.rectangle([cx + S(6), gy - S(60), cx + S(20), gy], fill=NAVY["lo"], outline=OUTLINE, width=2)
    d.rectangle([cx - S(22), gy - S(8), cx - S(6), gy], fill=(28, 30, 36))
    d.rectangle([cx + S(6), gy - S(8), cx + S(22), gy], fill=(28, 30, 36))
    # 左臂下垂，右臂夹文件夹
    _arms(d, cx, sh, gy - S(38), NAVY)
    # 文件夹（左手）
    ax = cx - S(40)
    d.rectangle([ax - S(10), gy - S(40), ax + S(10), gy - S(24)], fill=(140, 120, 88), outline=OUTLINE, width=2)
    d.line([(ax - S(10), gy - S(34)), (ax + S(10), gy - S(34))], fill=(110, 92, 64), width=2)
    d.ellipse([cx - S(40), gy - 4, cx + S(40), gy + 2], fill=(36, 38, 44))


# ============================================================
# 8. 女孩（12 岁：侧马尾 + 浅色连衣裙 + 信纸，感动微笑）
# ============================================================
def girl_portrait(d, cx, gy, h=190):
    k = h / 190.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(58), S(52)
    _head(d, cx, top, head_w, head_h)
    chin = top + head_h
    # 橙发（侧马尾，右侧）
    ORANGE = {"hi": (250, 190, 120), "mid": (226, 158, 92), "lo": (180, 118, 66), "dk": (120, 76, 42)}
    d.ellipse([cx - head_w // 2, top - 4, cx + head_w // 2, top + S(16)], fill=ORANGE["mid"])
    d.ellipse([cx - head_w // 2, top - 4, cx + head_w // 4, top + S(16)], fill=ORANGE["hi"])
    # 侧马尾（右侧，扎发）
    d.ellipse([cx + S(24), top + S(6), cx + S(44), top + S(24)], fill=ORANGE["mid"])
    d.ellipse([cx + S(28), top + S(20), cx + S(46), top + S(44)], fill=ORANGE["mid"])
    d.ellipse([cx + S(28), top + S(20), cx + S(38), top + S(44)], fill=ORANGE["hi"])
    d.ellipse([cx + S(38), top + S(30), cx + S(46), top + S(44)], fill=ORANGE["lo"])
    # 发箍
    d.line([(cx - S(20), top + S(8)), (cx + S(26), top + S(8))], fill=(250, 120, 150), width=3)
    # 五官（感动，微笑，微泪）
    ey = top + S(26)
    _eyes(d, cx, ey, S(14), iris=(160, 110, 70), brow=ORANGE["dk"], brow_tilt=2)
    _nose(d, cx, ey)
    _mouth(d, cx, ey + S(23), w=S(7), expr="smile", color=(200, 120, 110))
    # 泪珠
    d.ellipse([cx - S(18), ey + S(2), cx - S(15), ey + S(6)], fill=(170, 210, 240))
    # 身体（浅色连衣裙）
    body_top = chin + S(2)
    body_w = S(62)
    d.polygon([(cx - body_w // 2, body_top), (cx + body_w // 2, body_top),
               (cx + body_w // 2 + S(10), gy - S(10)), (cx - body_w // 2 - S(10), gy - S(10))],
              fill=(244, 226, 216), outline=OUTLINE, width=2)
    d.polygon([(cx - body_w // 2, body_top), (cx - body_w // 4, body_top),
               (cx - body_w // 2 - S(4), gy - S(10))], fill=(224, 200, 190))
    # 裙摆褶
    for i in range(5):
        x = cx - body_w // 2 - S(6) + i * S(8)
        d.line([(x, body_top + S(30)), (x + S(3), gy - S(12))], fill=(220, 196, 186), width=1)
    # 领口
    d.arc([cx - S(10), body_top + S(2), cx + S(10), body_top + S(14)], 0, 180, fill=(230, 150, 170), width=2)
    # 腿 + 鞋
    d.rectangle([cx - S(10), gy - S(30), cx - S(3), gy], fill=(232, 190, 160), outline=OUTLINE, width=2)
    d.rectangle([cx + S(3), gy - S(30), cx + S(10), gy], fill=(232, 190, 160), outline=OUTLINE, width=2)
    d.ellipse([cx - S(12), gy - S(8), cx - S(2), gy], fill=(210, 110, 130))
    d.ellipse([cx + S(2), gy - S(8), cx + S(12), gy], fill=(210, 110, 130))
    # 手臂（双手捧信纸）
    for side in (-1, 1):
        ax = cx + side * S(26)
        d.rectangle([ax - 5, body_top + S(12), ax + 5, gy - S(34)], fill=(244, 226, 216), outline=OUTLINE, width=2)
        d.ellipse([ax - 4, gy - S(34), ax + 4, gy - S(24)], fill=SKIN["mid"])
    # 信纸（胸前）
    d.rectangle([cx - S(16), body_top + S(24), cx + S(16), body_top + S(46)], fill=(252, 248, 236), outline=OUTLINE, width=2)
    for i in range(3):
        d.line([(cx - S(11), body_top + S(30) + i * 5), (cx + S(11), body_top + S(30) + i * 5)],
               fill=(200, 194, 180), width=1)
    d.ellipse([cx - S(34), gy - 4, cx + S(34), gy + 2], fill=(36, 38, 44))


# ============================================================
# 侧面立绘（facing=1 朝右 / -1 朝左）
# ============================================================
def _side_limbs(d, cx, gy, body_top, bot, facing, suit, skin=SKIN, pants=None):
    """侧面肢体：腿一前一后 + 臂一前一后。"""
    f = facing
    pants = pants or suit["lo"]
    # 双腿（前后交错）
    d.rectangle([cx - 10, gy - 56, cx + 2, gy], fill=pants, outline=OUTLINE, width=2)
    d.rectangle([cx + 2, gy - 52, cx + 13, gy], fill=pants, outline=OUTLINE, width=2)
    d.ellipse([cx - 12, gy - 8, cx + 2, gy], fill=(30, 32, 38))
    d.ellipse([cx + 2, gy - 8, cx + 15, gy], fill=(30, 32, 38))
    # 手臂（前臂伸出，后臂在身后）
    d.rectangle([cx + f * 2 - 7, body_top + 8, cx + f * 2 + 7, bot - 34], fill=suit["mid"], outline=OUTLINE, width=2)
    d.ellipse([cx + f * 2 - 5, bot - 34, cx + f * 2 + 5, bot - 22], fill=skin["mid"])


# ============================================================
# 老年赞比 · 侧面
# ============================================================
def elder_side(d, cx, gy, h=196, facing=1):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(62), S(56)
    f = facing
    _head_side(d, cx, top, head_w, head_h, facing=f)
    chin = top + head_h
    # 稀疏白发（侧面：后脑勺圆润 + 顶部稀薄）
    d.ellipse([cx - f * head_w // 2, top - 2, cx + f * head_w // 2, top + S(16)], fill=HAIR_WHITE["mid"])
    d.ellipse([cx - f * head_w // 2, top - 2, cx - f * head_w // 6, top + S(16)], fill=HAIR_WHITE["hi"])
    d.ellipse([cx + f * head_w // 6, top + S(4), cx + f * head_w // 2, top + S(16)], fill=HAIR_WHITE["lo"])
    # 鬓发
    d.ellipse([cx - f * head_w // 2 - 2, top + S(16), cx - f * head_w // 2 + 8, chin - S(8)], fill=HAIR_WHITE["mid"])
    # 侧面单眼 + 眉
    ey = top + S(30)
    _eye_side(d, cx, ey, facing=f, iris=(70, 118, 158), brow=HAIR_WHITE["lo"])
    # 嘴（鼻子下方偏前）
    _mouth(d, cx + f * S(6), ey + S(24), w=S(6), expr="calm")
    # 耳朵
    d.ellipse([cx - f * S(16) - 3, ey - S(2), cx - f * S(16) + 5, ey + S(8)], fill=SKIN["mid"], outline=SKIN["lo"], width=1)
    # 身体（西装侧身）
    body_top = chin + S(2)
    body_w = S(58)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(58)], fill=NAVY["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx - f * body_w // 2, body_top, cx - f * body_w // 6, gy - S(58)], fill=NAVY["dk"])
    d.rectangle([cx + f * body_w // 6, body_top, cx + f * body_w // 2, gy - S(58)], fill=NAVY["lo"])
    # 前襟 + 领带（侧面胸前）
    d.line([(cx + f * S(6), body_top + S(8)), (cx + f * S(8), gy - S(58))], fill=NAVY["dk"], width=2)
    d.line([(cx + f * S(4), body_top + S(10)), (cx + f * S(4), body_top + S(40))], fill=TIE["mid"], width=4)
    # 怀表链（胸前）
    d.arc([cx + f * S(2), body_top + S(30), cx + f * S(16), body_top + S(44)], 230, 310, fill=GOLD["mid"], width=2)
    # 肢体
    _side_limbs(d, cx, gy, body_top, gy - S(40), f, NAVY)
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


# ============================================================
# 少年赞比 · 侧面
# ============================================================
def boy_side(d, cx, gy, h=196, facing=1):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    f = facing
    _head_side(d, cx, top, head_w, head_h, facing=f)
    chin = top + head_h
    # 乱发（侧面）
    d.ellipse([cx - f * head_w // 2, top - 4, cx + f * head_w // 2, top + S(18)], fill=HAIR_DARK["mid"])
    d.ellipse([cx - f * head_w // 2, top - 4, cx - f * head_w // 6, top + S(18)], fill=HAIR_DARK["hi"])
    # 刘海（前垂）
    d.polygon([(cx + f * S(20), top + S(12)), (cx + f * S(28), top + S(6)),
               (cx + f * S(30), top + S(22)), (cx + f * S(22), top + S(20))], fill=HAIR_DARK["mid"])
    ey = top + S(28)
    _eye_side(d, cx, ey, facing=f, iris=(74, 104, 62), brow=HAIR_DARK["dk"])
    _mouth(d, cx + f * S(6), ey + S(22), w=S(5), expr="frown")
    d.ellipse([cx - f * S(16) - 3, ey - S(2), cx - f * S(16) + 5, ey + S(8)], fill=SKIN["mid"], outline=SKIN["lo"], width=1)
    # 身体（破衣侧身）
    body_top = chin + S(2)
    body_w = S(54)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(48)], fill=(120, 92, 60), outline=OUTLINE, width=2)
    d.rectangle([cx - f * body_w // 2, body_top, cx - f * body_w // 6, gy - S(48)], fill=(96, 72, 46))
    # 补丁
    d.rectangle([cx + S(2), body_top + S(20), cx + S(14), body_top + S(34)], fill=(156, 124, 84), outline=(90, 68, 44), width=1)
    # 唯一右腿（站立）+ 左腿残端（悬空）
    d.rectangle([cx - S(4), gy - S(56), cx + S(8), gy], fill=(84, 70, 50), outline=OUTLINE, width=2)
    d.ellipse([cx - S(6), gy - S(8), cx + S(10), gy], fill=(40, 34, 30))
    d.rectangle([cx - S(16), gy - S(46), cx - S(6), gy - S(24)], fill=(84, 70, 50), outline=OUTLINE, width=2)
    d.polygon([(cx - S(15), gy - S(28)), (cx - S(7), gy - S(28)), (cx - S(9), gy - S(18)), (cx - S(13), gy - S(18))],
              fill=(70, 56, 40), outline=OUTLINE, width=1)
    # 拐杖（前伸）
    d.line([(cx + f * S(20), body_top + S(2)), (cx + f * S(36), gy)], fill=(108, 76, 48), width=7)
    d.line([(cx + f * S(21), body_top + S(2)), (cx + f * S(37), gy)], fill=(152, 110, 70), width=3)
    # 前臂（拄拐）+ 后臂
    d.rectangle([cx + f * S(4) - 6, body_top + S(10), cx + f * S(4) + 6, gy - S(38)], fill=(120, 92, 60), outline=OUTLINE, width=2)
    d.ellipse([cx + f * S(4) - 4, gy - S(38), cx + f * S(4) + 4, gy - S(26)], fill=SKIN["mid"])
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


# ============================================================
# 青年赞比 · 侧面
# ============================================================
def young_side(d, cx, gy, h=196, facing=1):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    f = facing
    _head_side(d, cx, top, head_w, head_h, facing=f)
    chin = top + head_h
    d.ellipse([cx - f * head_w // 2, top - 4, cx + f * head_w // 2, top + S(18)], fill=HAIR_BROWN["mid"])
    d.ellipse([cx - f * head_w // 2, top - 4, cx - f * head_w // 6, top + S(18)], fill=HAIR_BROWN["hi"])
    ey = top + S(28)
    _eye_side(d, cx, ey, facing=f, iris=(78, 108, 66), brow=HAIR_BROWN["dk"])
    _mouth(d, cx + f * S(6), ey + S(24), w=S(6), expr="smile")
    d.ellipse([cx - f * S(16) - 3, ey - S(2), cx - f * S(16) + 5, ey + S(8)], fill=SKIN["mid"], outline=SKIN["lo"], width=1)
    body_top = chin + S(2)
    body_w = S(58)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(58)], fill=DARKSUIT["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx - f * body_w // 2, body_top, cx - f * body_w // 6, gy - S(58)], fill=DARKSUIT["dk"])
    d.rectangle([cx + f * body_w // 6, body_top, cx + f * body_w // 2, gy - S(58)], fill=DARKSUIT["lo"])
    d.line([(cx + f * S(6), body_top + S(8)), (cx + f * S(8), gy - S(58))], fill=DARKSUIT["dk"], width=2)
    d.line([(cx + f * S(4), body_top + S(10)), (cx + f * S(4), body_top + S(40))], fill=TIE["mid"], width=4)
    _side_limbs(d, cx, gy, body_top, gy - S(38), f, DARKSUIT)
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


# ============================================================
# 克隆赞比 · 侧面
# ============================================================
def clone_side(d, cx, gy, h=196, facing=1):
    elder_side(d, cx, gy, h=h, facing=facing)  # 同老年侧面，但头发深色
    # 覆盖发色（重画深棕发）
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    f = facing
    d.ellipse([cx - f * head_w // 2, top - 4, cx + f * head_w // 2, top + S(18)], fill=HAIR_DARK["mid"])
    d.ellipse([cx - f * head_w // 2, top - 4, cx - f * head_w // 6, top + S(18)], fill=HAIR_DARK["hi"])


# ============================================================
# 机械赞比 · 侧面
# ============================================================
def mech_side(d, cx, gy, h=190, facing=1):
    k = h / 190.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(56), S(44)
    f = facing
    d.rounded_rectangle([cx - head_w // 2, top, cx + head_w // 2, top + head_h],
                        radius=S(8), fill=(74, 84, 100), outline=OUTLINE, width=2)
    d.rounded_rectangle([cx - f * head_w // 2, top, cx - f * head_w // 6, top + head_h],
                        radius=S(8), fill=(96, 108, 126))
    # 眼带（侧面窄条）
    d.rectangle([cx - S(10), top + S(16), cx + S(18), top + S(24)], fill=ICE["mid"], outline=ICE["hi"], width=1)
    # 光纤束（后脑）
    for i in range(5):
        d.line([(cx - f * head_w // 2, top + S(10) + i * 6), (cx - f * head_w // 2 - S(18), top + S(4) + i * 7)],
               fill=ICE["mid"], width=2)
    body_top = top + head_h + S(4)
    body_w = S(60)
    d.rounded_rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(46)],
                        radius=S(6), fill=(74, 84, 100), outline=OUTLINE, width=2)
    d.rounded_rectangle([cx - f * body_w // 2, body_top, cx - f * body_w // 6, gy - S(46)],
                        radius=S(6), fill=(96, 108, 126))
    # 核心灯（侧面）
    core = gy - S(46) - S(14)
    d.ellipse([cx - S(7), core - S(7), cx + S(7), core + S(7)], fill=ICE["hi"], outline=ICE["mid"], width=2)
    # 线缆下半身
    cable_top = gy - S(46)
    for i, (dx, c) in enumerate([(-S(18), (190, 70, 60)), (-S(6), (200, 160, 70)),
                                 (S(6), (110, 130, 160)), (S(18), (190, 70, 60))]):
        sway = S(4) * (1 if i % 2 == 0 else -1)
        d.line([(cx + dx, cable_top), (cx + dx + sway, (cable_top + gy) // 2), (cx + dx, gy)], fill=c, width=3)
    # 机械臂（前后）
    d.rectangle([cx + f * S(6) - 7, body_top + S(10), cx + f * S(6) + 7, gy - S(40)], fill=(74, 84, 100), outline=OUTLINE, width=2)
    d.ellipse([cx + f * S(6) - 5, gy - S(40), cx + f * S(6) + 5, gy - S(28)], fill=(96, 108, 126), outline=OUTLINE, width=2)
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


# ============================================================
# 立方体 · 侧面（等距视角本身是 3D，旋转角度呈现）
# ============================================================
def cube_side(d, cx, gy, h=190, facing=1):
    k = h / 190.0
    S = lambda v: int(v * k)
    s = S(60)
    top = gy - h + S(24)
    f = facing
    for rr, aa in ((s + S(14), 24), (s + S(8), 40), (s + S(3), 60)):
        d.ellipse([cx - rr, top + s - rr, cx + rr, top + s + rr], outline=(79, 193, 224), width=1)
    # 旋转后的立方体（facing 影响侧面朝向）
    d.polygon([(cx - s, top + s // 2), (cx, top), (cx + s, top + s // 2), (cx, top + s)],
              fill=(40, 50, 66), outline=OUTLINE, width=2)
    d.polygon([(cx - s, top + s // 2), (cx, top + s), (cx, top + s * 2 - s // 2),
               (cx - s, top + s + s // 2)], fill=(16, 20, 28), outline=OUTLINE, width=2)
    d.polygon([(cx, top + s), (cx + s, top + s // 2), (cx + s, top + s + s // 2),
               (cx, top + s * 2 - s // 2)], fill=(10, 13, 18), outline=OUTLINE, width=2)
    d.line([(cx - s, top + s + s // 2), (cx, top + s * 2 - s // 2), (cx + s, top + s + s // 2)], fill=ICE["hi"], width=2)
    d.line([(cx + s, top + s // 2), (cx + s, top + s + s // 2)], fill=ICE["mid"], width=2)
    d.point((cx, top + s), fill=ICE["hi"])
    d.ellipse([cx - S(30), gy - 4, cx + S(30), gy + 2], fill=(36, 38, 44))


# ============================================================
# 理查德 · 侧面
# ============================================================
def richard_side(d, cx, gy, h=196, facing=1):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    f = facing
    _head_side(d, cx, top, head_w, head_h, facing=f)
    chin = top + head_h
    d.ellipse([cx - f * head_w // 2, top - 4, cx + f * head_w // 2, top + S(18)], fill=HAIR_DARK["mid"])
    d.ellipse([cx - f * head_w // 2, top - 4, cx - f * head_w // 6, top + S(18)], fill=HAIR_DARK["hi"])
    ey = top + S(28)
    _eye_side(d, cx, ey, facing=f, iris=(80, 74, 66), brow=HAIR_DARK["mid"])
    _mouth(d, cx + f * S(6), ey + S(24), w=S(5), expr="calm")
    d.ellipse([cx - f * S(16) - 3, ey - S(2), cx - f * S(16) + 5, ey + S(8)], fill=SKIN["mid"], outline=SKIN["lo"], width=1)
    body_top = chin + S(2)
    body_w = S(56)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(58)], fill=NAVY["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx - f * body_w // 2, body_top, cx - f * body_w // 6, gy - S(58)], fill=NAVY["dk"])
    d.rectangle([cx + f * body_w // 6, body_top, cx + f * body_w // 2, gy - S(58)], fill=NAVY["lo"])
    # 领结（侧面）
    d.polygon([(cx + f * S(4), body_top + S(8)), (cx + f * S(12), body_top + S(13)), (cx + f * S(4), body_top + S(18))],
              fill=TIE["mid"])
    _side_limbs(d, cx, gy, body_top, gy - S(38), f, NAVY)
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


# ============================================================
# 女孩 · 侧面
# ============================================================
def girl_side(d, cx, gy, h=190, facing=1):
    k = h / 190.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(58), S(52)
    f = facing
    _head_side(d, cx, top, head_w, head_h, facing=f)
    chin = top + head_h
    ORANGE = {"hi": (250, 190, 120), "mid": (226, 158, 92), "lo": (180, 118, 66), "dk": (120, 76, 42)}
    d.ellipse([cx - f * head_w // 2, top - 4, cx + f * head_w // 2, top + S(16)], fill=ORANGE["mid"])
    # 侧马尾（垂在身后，-f 方向）
    def _mx(a, b):
        return (cx - f * S(a), cx - f * S(b)) if f > 0 else (cx - f * S(b), cx - f * S(a))
    m0, m1 = _mx(44, 24)
    d.ellipse([m0, top + S(6), m1, top + S(24)], fill=ORANGE["mid"])
    m0, m1 = _mx(46, 28)
    d.ellipse([m0, top + S(20), m1, top + S(44)], fill=ORANGE["mid"])
    m0, m1 = _mx(38, 28)
    d.ellipse([m0, top + S(20), m1, top + S(44)], fill=ORANGE["hi"])
    ey = top + S(26)
    _eye_side(d, cx, ey, facing=f, iris=(160, 110, 70), brow=ORANGE["dk"])
    _mouth(d, cx + f * S(6), ey + S(22), w=S(5), expr="smile", color=(200, 120, 110))
    d.ellipse([cx - f * S(16) - 3, ey - S(2), cx - f * S(16) + 5, ey + S(8)], fill=SKIN["mid"], outline=SKIN["lo"], width=1)
    body_top = chin + S(2)
    body_w = S(50)
    d.polygon([(cx - body_w // 2, body_top), (cx + body_w // 2, body_top),
               (cx + body_w // 2 + S(6), gy - S(10)), (cx - body_w // 2 - S(6), gy - S(10))],
              fill=(244, 226, 216), outline=OUTLINE, width=2)
    # 腿
    d.rectangle([cx - S(8), gy - S(30), cx, gy], fill=(232, 190, 160), outline=OUTLINE, width=2)
    d.rectangle([cx, gy - S(28), cx + S(8), gy], fill=(232, 190, 160), outline=OUTLINE, width=2)
    d.ellipse([cx - S(10), gy - S(8), cx, gy], fill=(210, 110, 130))
    d.ellipse([cx, gy - S(8), cx + S(10), gy], fill=(210, 110, 130))
    d.ellipse([cx - S(34), gy - 4, cx + S(34), gy + 2], fill=(36, 38, 44))


# ============================================================
# 背面立绘（无五官，展示后脑勺+背部）
# ============================================================
def _head_back(d, cx, top, w, h, hair):
    """后脑勺（纯头发）。"""
    d.ellipse([cx - w // 2, top, cx + w // 2, top + h], fill=hair["mid"], outline=OUTLINE, width=2)
    d.ellipse([cx - w // 2 + 4, top + 4, cx + w // 4, top + h - 6], fill=hair["hi"])
    d.ellipse([cx - w // 4, top + h // 2, cx + w // 2 - 2, top + h - 4], fill=hair["lo"])
    # 后颈
    d.rectangle([cx - 8, top + h - 4, cx + 8, top + h + 8], fill=SKIN["mid"])


def _back_limbs(d, cx, gy, body_top, bot, suit, pants=None):
    """背面肢体：双腿直立 + 双臂贴身体。"""
    pants = pants or suit["lo"]
    d.rectangle([cx - 14, gy - 56, cx - 2, gy], fill=pants, outline=OUTLINE, width=2)
    d.rectangle([cx + 2, gy - 56, cx + 14, gy], fill=pants, outline=OUTLINE, width=2)
    d.ellipse([cx - 16, gy - 8, cx - 2, gy], fill=(30, 32, 38))
    d.ellipse([cx + 2, gy - 8, cx + 16, gy], fill=(30, 32, 38))
    d.rectangle([cx - 22, body_top + 8, cx - 8, bot - 30], fill=suit["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx + 8, body_top + 8, cx + 22, bot - 30], fill=suit["mid"], outline=OUTLINE, width=2)
    d.ellipse([cx - 22, bot - 30, cx - 8, bot - 18], fill=SKIN["mid"])
    d.ellipse([cx + 8, bot - 30, cx + 22, bot - 18], fill=SKIN["mid"])


def elder_back(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(56)
    _head_back(d, cx, top, head_w, head_h, HAIR_WHITE)
    body_top = top + head_h + S(4)
    body_w = S(58)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(58)], fill=NAVY["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx - body_w // 2, body_top, cx - body_w // 6, gy - S(58)], fill=NAVY["dk"])
    d.rectangle([cx + body_w // 6, body_top, cx + body_w // 2, gy - S(58)], fill=NAVY["lo"])
    # 中缝
    d.line([(cx, body_top + S(6)), (cx, gy - S(58))], fill=NAVY["dk"], width=2)
    _back_limbs(d, cx, gy, body_top, gy - S(38), NAVY)
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


def boy_back(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(58), S(54)
    _head_back(d, cx, top, head_w, head_h, HAIR_DARK)
    body_top = top + head_h + S(4)
    body_w = S(54)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(48)], fill=(120, 92, 60), outline=OUTLINE, width=2)
    d.rectangle([cx - body_w // 2, body_top, cx - body_w // 6, gy - S(48)], fill=(96, 72, 46))
    d.rectangle([cx + S(2), body_top + S(16), cx + S(14), body_top + S(30)], fill=(156, 124, 84), outline=(90, 68, 44), width=1)
    # 右腿 + 左残腿（背面）
    d.rectangle([cx + 2, gy - S(56), cx + 14, gy], fill=(84, 70, 50), outline=OUTLINE, width=2)
    d.ellipse([cx + 2, gy - S(8), cx + 16, gy], fill=(40, 34, 30))
    d.rectangle([cx - 16, gy - S(46), cx - 6, gy - S(24)], fill=(84, 70, 50), outline=OUTLINE, width=2)
    d.polygon([(cx - 15, gy - S(28)), (cx - 7, gy - S(28)), (cx - 9, gy - S(18)), (cx - 13, gy - S(18))],
              fill=(70, 56, 40), outline=OUTLINE, width=1)
    # 拐杖（背面可见）
    d.line([(cx - S(22), body_top + S(2)), (cx - S(38), gy)], fill=(108, 76, 48), width=7)
    d.line([(cx - S(21), body_top + S(2)), (cx - S(37), gy)], fill=(152, 110, 70), width=3)
    _back_limbs(d, cx, gy, body_top, gy - S(36), {"lo": (96, 72, 46), "mid": (120, 92, 60), "hi": (156, 124, 84)})
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


def young_back(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    _head_back(d, cx, top, head_w, head_h, HAIR_BROWN)
    body_top = top + head_h + S(4)
    body_w = S(58)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(58)], fill=DARKSUIT["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx - body_w // 2, body_top, cx - body_w // 6, gy - S(58)], fill=DARKSUIT["dk"])
    d.rectangle([cx + body_w // 6, body_top, cx + body_w // 2, gy - S(58)], fill=DARKSUIT["lo"])
    d.line([(cx, body_top + S(6)), (cx, gy - S(58))], fill=DARKSUIT["dk"], width=2)
    _back_limbs(d, cx, gy, body_top, gy - S(38), DARKSUIT)
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


def clone_back(d, cx, gy, h=196):
    elder_back(d, cx, gy, h=h)
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(56)
    d.ellipse([cx - head_w // 2, top, cx + head_w // 2, top + head_h], fill=HAIR_DARK["mid"], outline=OUTLINE, width=2)
    d.ellipse([cx - head_w // 2 + 4, top + 4, cx + head_w // 4, top + head_h - 6], fill=HAIR_DARK["hi"])


def mech_back(d, cx, gy, h=190):
    k = h / 190.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(56), S(44)
    d.rounded_rectangle([cx - head_w // 2, top, cx + head_w // 2, top + head_h],
                        radius=S(8), fill=(74, 84, 100), outline=OUTLINE, width=2)
    # 后脑光纤束
    for i in range(6):
        d.line([(cx - head_w // 2 + 4 + i * 4, top + S(4)), (cx - head_w // 2 - S(8) + i * 5, top - S(10))],
               fill=ICE["mid"], width=2)
    body_top = top + head_h + S(4)
    body_w = S(60)
    d.rounded_rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(46)],
                        radius=S(6), fill=(74, 84, 100), outline=OUTLINE, width=2)
    d.rounded_rectangle([cx - body_w // 2, body_top, cx - body_w // 6, gy - S(46)],
                        radius=S(6), fill=(96, 108, 126))
    # 背部散热孔
    for i in range(3):
        d.line([(cx - S(14), body_top + S(14) + i * 10), (cx + S(14), body_top + S(14) + i * 10)], fill=(52, 60, 74), width=2)
    # 线缆下半身
    cable_top = gy - S(46)
    for i, (dx, c) in enumerate([(-S(18), (190, 70, 60)), (-S(6), (200, 160, 70)),
                                 (S(6), (110, 130, 160)), (S(18), (190, 70, 60))]):
        sway = S(4) * (1 if i % 2 == 0 else -1)
        d.line([(cx + dx, cable_top), (cx + dx + sway, (cable_top + gy) // 2), (cx + dx, gy)], fill=c, width=3)
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


def cube_back(d, cx, gy, h=190):
    cube_side(d, cx, gy, h=h, facing=-1)


def richard_back(d, cx, gy, h=196):
    k = h / 196.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(60), S(54)
    _head_back(d, cx, top, head_w, head_h, HAIR_DARK)
    body_top = top + head_h + S(4)
    body_w = S(56)
    d.rectangle([cx - body_w // 2, body_top, cx + body_w // 2, gy - S(58)], fill=NAVY["mid"], outline=OUTLINE, width=2)
    d.rectangle([cx - body_w // 2, body_top, cx - body_w // 6, gy - S(58)], fill=NAVY["dk"])
    d.rectangle([cx + body_w // 6, body_top, cx + body_w // 2, gy - S(58)], fill=NAVY["lo"])
    d.line([(cx, body_top + S(6)), (cx, gy - S(58))], fill=NAVY["dk"], width=2)
    _back_limbs(d, cx, gy, body_top, gy - S(38), NAVY)
    d.ellipse([cx - S(36), gy - 4, cx + S(36), gy + 2], fill=(36, 38, 44))


def girl_back(d, cx, gy, h=190):
    k = h / 190.0
    S = lambda v: int(v * k)
    top = gy - h
    head_w, head_h = S(56), S(52)
    ORANGE = {"hi": (250, 190, 120), "mid": (226, 158, 92), "lo": (180, 118, 66), "dk": (120, 76, 42)}
    _head_back(d, cx, top, head_w, head_h, ORANGE)
    # 后马尾（背面更明显）
    d.ellipse([cx - S(10), top + S(6), cx + S(10), top + S(30)], fill=ORANGE["mid"])
    d.ellipse([cx - S(8), top + S(28), cx + S(6), top + S(60)], fill=ORANGE["mid"])
    d.ellipse([cx - S(8), top + S(28), cx + S(2), top + S(60)], fill=ORANGE["hi"])
    body_top = top + head_h + S(4)
    body_w = S(50)
    d.polygon([(cx - body_w // 2, body_top), (cx + body_w // 2, body_top),
               (cx + body_w // 2 + S(6), gy - S(10)), (cx - body_w // 2 - S(6), gy - S(10))],
              fill=(244, 226, 216), outline=OUTLINE, width=2)
    # 背部裙褶
    for i in range(3):
        d.line([(cx - S(12) + i * 12, body_top + S(20)), (cx - S(14) + i * 12, gy - S(14))], fill=(226, 200, 188), width=1)
    d.rectangle([cx - 14, gy - S(30), cx - 2, gy], fill=(232, 190, 160), outline=OUTLINE, width=2)
    d.rectangle([cx + 2, gy - S(30), cx + 14, gy], fill=(232, 190, 160), outline=OUTLINE, width=2)
    d.ellipse([cx - 16, gy - S(8), cx - 2, gy], fill=(210, 110, 130))
    d.ellipse([cx + 2, gy - S(8), cx + 16, gy], fill=(210, 110, 130))
    d.ellipse([cx - S(34), gy - 4, cx + S(34), gy + 2], fill=(36, 38, 44))


# ============================================================
# 合集图生成
# ============================================================
def generate_sheet():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portraits")
    os.makedirs(out_dir, exist_ok=True)
    cols, rows = 4, 2
    cell_w, cell_h = 320, 360
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), (18, 22, 32))
    d = ImageDraw.Draw(sheet)
    roles = [
        (boy_portrait, "少年赞比", "10 岁 · 难民营孤儿 · 左腿残端拄拐"),
        (young_portrait, "青年赞比", "26 岁 · 创业 · 开源协议"),
        (elder_portrait, "老年赞比", "79 岁 · 临终立嘱"),
        (clone_portrait, "克隆赞比", "年轻力壮版 · 无表情"),
        (mech_portrait, "机械赞比", "半具机器人 · 线缆下半身"),
        (cube_portrait, "立方体", "最终形态 · if-then 程序"),
        (richard_portrait, "理查德·史密斯", "叙述者 · 律师"),
        (girl_portrait, "女孩", "12 岁 · 写信"),
    ]
    name_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
    desc_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 13)
    for i, (fn, name, desc) in enumerate(roles):
        r, c = i // cols, i % cols
        ox, oy = c * cell_w, r * cell_h
        d.rectangle([ox + 6, oy + 6, ox + cell_w - 6, oy + cell_h - 6],
                    fill=(28, 34, 48), outline=(52, 62, 82), width=2)
        cell = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cell)
        fn(cd, PW // 2, PH - 28)
        # 倒影
        _reflection(cell, PW // 2, PH - 28, 0.18)
        cell = cell.convert("RGB").resize((cell_w - 40, cell_h - 88), Image.NEAREST)
        sheet.paste(cell, (ox + 20, oy + 12))
        d.text((ox + cell_w // 2, oy + cell_h - 60), name, font=name_font,
               fill=(235, 238, 244), anchor="mm")
        d.text((ox + cell_w // 2, oy + cell_h - 34), desc, font=desc_font,
               fill=(150, 162, 180), anchor="mm")
    out = os.path.join(out_dir, "characters.png")
    sheet.save(out)
    print("saved", out, sheet.size)


if __name__ == "__main__":
    generate_sheet()
