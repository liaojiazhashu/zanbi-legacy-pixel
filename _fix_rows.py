# -*- coding: utf-8 -*-
"""自动修正 portrait_px.py 里 ELDER 列表的行宽到 48。

规则：右端多余的点删掉；不足 48 补点。
输出修正后的列表文本，可直接替换。
"""
src = open("portrait_px.py", encoding="utf-8").read()
ns = {}
exec(src.split("if __name__")[0], ns)
ELDER = ns["ELDER"]

fixed = []
for r in ELDER:
    if len(r) > 48:
        # 从右端删，优先删点
        excess = len(r) - 48
        # 检查右端是否都是点
        r = r[:48] if r.endswith("." * excess) else r[:48]
    elif len(r) < 48:
        r = r + "." * (48 - len(r))
    fixed.append(r)

bad = [(i, len(r)) for i, r in enumerate(fixed) if len(r) != 48]
print("修正后坏行:", bad)
print("总行数:", len(fixed))

# 输出可复制的 Python 列表
with open("_elder_fixed.txt", "w", encoding="utf-8") as f:
    for r in fixed:
        f.write(f'"{r}",\n')
print("已写入 _elder_fixed.txt")
