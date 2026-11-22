# -*- coding: utf-8 -*-
"""char_builder.py —— 部位素材库拼接生成器（裁剪拼合工作流）。

从 lpc_layers/ 已下载的 LPC 分层素材中选取部位，按 base→legs→torso→hair→eyes
顺序 alpha 叠加拼接成完整角色，并支持调色板换色（修正 LPC 三大误读）。

用法：
    python char_builder.py <角色名> --body male --legs formal --torso longsleeve --hair balding --eyes elderly [--recolor elder]

部位（省略则跳过该层）：
    --body    child/female/male/muscular/pregnant/teen
    --legs    formal/pants/skirts_plain/skirts_legion/...（根目录 legs_*.png）
    --torso   longsleeve/longsleeves/longsleeve_female/armour_leather/armour_legion/armour_plate/aprons_overalls/aprons_suspenders
    --hair    balding/bangs/swoop/pigtails/...（hair/ 子目录 *_adult_idle.png）
    --eyes    adult/elderly/child
    --recolor 预设换色名（见 RECOLOR）

换色预设（修正 LPC 三大误读：暗脸/青发光眼/橙红恶魔角）：
    elder  银白残发+亮脸+深棕眼
    bright 亮脸+深棕眼
"""
import sys, os
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
L = os.path.join(ROOT, "lpc_layers")
OUT = os.path.join(ROOT, "portraits")

def find_file(*candidates):
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def find_body(name, anim="idle"):
    return find_file(os.path.join(L, "body", f"body_{name}_{anim}.png"))

def find_legs(name):
    # 根目录 legs_*.png（可能带 __legs__ 双前缀）
    for c in [
        os.path.join(L, f"legs_{name}.png"),
        os.path.join(L, f"legs_{name}__legs_{name}__male_idle.png"),
    ]:
        if os.path.exists(c):
            return c
    # 匹配任意 legs_{name}*
    import glob
    g = glob.glob(os.path.join(L, f"legs_{name}*.png"))
    return g[0] if g else None

def find_torso(name):
    import glob
    g = glob.glob(os.path.join(L, f"torso_{name}*.png"))
    return g[0] if g else None

def find_hair(name):
    return find_file(os.path.join(L, "hair", f"{name}_adult_idle.png"))

def find_eyes(name):
    import glob
    g = glob.glob(os.path.join(L, f"eyes*_{name}_default_idle.png"))
    return g[0] if g else None

# 换色预设：old -> new（RGB 精确匹配替换）
RECOLOR = {
    "elder": {
        # 银白残发（balding 橙红 -> 银白）
        (106, 17, 8): (138, 138, 154),
        (164, 38, 0): (176, 176, 192),
        (191, 64, 0): (200, 200, 216),
        (229, 86, 0): (224, 224, 238),
        (255, 138, 0): (240, 240, 250),
        (38, 13, 20): (58, 58, 70),
        # 亮脸（LPC 6 色肤色整体调亮）
        (153, 66, 60): (192, 122, 90),
        (204, 134, 101): (217, 150, 110),
        (228, 164, 124): (240, 184, 144),
        (249, 213, 186): (248, 208, 176),
        (250, 236, 231): (252, 232, 216),
        # 深棕眼（elderly 眼 3 色 -> 深棕）
        (41, 61, 75): (26, 20, 8),
        (81, 135, 179): (74, 52, 32),
        (80, 212, 236): (107, 74, 48),
        # 深棕眼（adult 眼 3 色 -> 深棕）
        (42, 60, 73): (26, 20, 8),
        (86, 134, 174): (74, 52, 32),
        (87, 206, 228): (107, 74, 48),
    },
    "bright": {
        (153, 66, 60): (192, 122, 90),
        (204, 134, 101): (217, 150, 110),
        (228, 164, 124): (240, 184, 144),
        (249, 213, 186): (248, 208, 176),
        (250, 236, 231): (252, 232, 216),
        (41, 61, 75): (26, 20, 8),
        (81, 135, 179): (74, 52, 32),
        (80, 212, 236): (107, 74, 48),
        (42, 60, 73): (26, 20, 8),
        (86, 134, 174): (74, 52, 32),
        (87, 206, 228): (107, 74, 48),
    },
}

def recolor_img(img, mapping):
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a > 0 and (r, g, b) in mapping:
                nr, ng, nb = mapping[(r, g, b)]
                px[x, y] = (nr, ng, nb, a)
    return img

def build(name, body=None, legs=None, torso=None, hair=None, eyes=None, recolor=None):
    canvas = Image.new("RGBA", (128, 256), (0, 0, 0, 0))
    layers = []
    if body:
        p = find_body(body)
        assert p, f"body {body} not found"
        layers.append(("body", Image.open(p).convert("RGBA")))
    if legs:
        p = find_legs(legs)
        assert p, f"legs {legs} not found"
        layers.append(("legs", Image.open(p).convert("RGBA")))
    if torso:
        p = find_torso(torso)
        assert p, f"torso {torso} not found"
        layers.append(("torso", Image.open(p).convert("RGBA")))
    if hair:
        p = find_hair(hair)
        assert p, f"hair {hair} not found"
        layers.append(("hair", Image.open(p).convert("RGBA")))
    if eyes:
        p = find_eyes(eyes)
        assert p, f"eyes {eyes} not found"
        layers.append(("eyes", Image.open(p).convert("RGBA")))

    mapping = RECOLOR.get(recolor, {})
    for lname, img in layers:
        if mapping:
            img = recolor_img(img, mapping)
        canvas.alpha_composite(img, (0, 0))

    # crop 到向下站立帧 (col0,row2) = x0,y128, 64×64
    frame = canvas.crop((0, 128, 64, 192))
    bbox = frame.getbbox()
    if bbox:
        frame = frame.crop(bbox)
    out = os.path.join(OUT, f"{name}_lpc.png")
    frame.save(out)
    # 放大 4x 预览
    w, h = frame.size
    frame.resize((w * 4, h * 4), Image.NEAREST).save(os.path.join(OUT, f"{name}_lpc_x4.png"))
    print(f"saved {out} ({w}x{h})")
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    name = args[0]
    kw = {}
    i = 1
    while i < len(args):
        if args[i] == "--body": kw["body"] = args[i+1]; i += 2
        elif args[i] == "--legs": kw["legs"] = args[i+1]; i += 2
        elif args[i] == "--torso": kw["torso"] = args[i+1]; i += 2
        elif args[i] == "--hair": kw["hair"] = args[i+1]; i += 2
        elif args[i] == "--eyes": kw["eyes"] = args[i+1]; i += 2
        elif args[i] == "--recolor": kw["recolor"] = args[i+1]; i += 2
        else: i += 1
    build(name, **kw)
