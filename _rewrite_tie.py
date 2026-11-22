# -*- coding: utf-8 -*-
"""重写领带+怀表链区域：去对称金色，改单列细弧线。"""
import re

src = open("portrait_px.py", encoding="utf-8").read()

# 找到 ELDER 列表内容（从 ELDER = [ 到 ]）
m = re.search(r"ELDER = \[(.*?)\n\]", src, re.S)
body = m.group(1)
# 提取每行字符串
rows = re.findall(r'"((?:[^"\\]|\\.)*)"', body)

print("总行数:", len(rows))

# 新领带+怀表链区域（替换原行 62-84，即索引 62..84）
new_block = [
"....ONnnnnnnSSSSGTTTTTTTTTTTSSSSnnnnnnnNO........",
"....ONnnnnnnSSSSGTTTTTTTTTTTSSSSnnnnnnnNO........",
"....ONnnnnnnSSSSsGTTTTTTTTTTSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssGTTTTTTTTTSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSsssGttttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssssGtttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssssGtttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssssGtttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssssGtttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssssGtttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssssGtttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssssGtttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnSSSSssssGtttttttSSSSnnnnnnnnNO........",
"....ONnnnnnnnSSssssGtttttttSSSnnnnnnnnnNO.........",
"....ONnnnnnnnSSssssGtttttttSSSnnnnnnnnnNO.........",
"....ONnnnnnnnnSSsssGtttttttSSnnnnnnnnnnNO.........",
"....ONnnnnnnnnSSsssGtttttttSSnnnnnnnnnnNO.........",
"....ONnnnnnnnnSSSssGtttttttSSSnnnnnnnnnnNO.........",
"....ONnnnnnnnnSSSssGtttttttSSSnnnnnnnnnnNO.........",
"....ONnnnnnnnnnSSssGtttttttSSnnnnnnnnnnnNO.........",
"......ONnnnnnnnnnSSssGttttttSSnnnnnnnnnnnO.........",
]

# 原领带+怀表链区域索引（读源码确认）
# 索引 62-84 是领带垂下+怀表链+西装主体+下摆（25 行），但新块 21 行，需对应
# 实际：先看每行内容，找到第一个含 'SSSSG' 的行
start = None
for i, r in enumerate(rows):
    if 'SSSSG' in r or 'SSSGG' in r or 'SSGGGG' in r:
        start = i
        break
print("第一个含金链行:", start, "内容:", rows[start] if start else None)

# 找到最后一个含 G 或领带收尾的行（下摆结束，裤腿开始前的行）
# 裤腿第一行含 'kttttk'
end = None
for i, r in enumerate(rows):
    if 'kttttk' in r:
        end = i
        break
print("裤腿首行:", end)

if start is not None and end is not None:
    # 替换 start..end-1 为新块
    new_rows = rows[:start] + new_block + rows[end:]
    # 重新拼成列表文本
    out_lines = ['ELDER = [']
    for r in new_rows:
        out_lines.append(f'    "{r}",')
    out_lines.append(']')
    # 替换原 ELDER 列表
    new_list = "\n".join(out_lines)
    src = src[:m.start()] + new_list + src[m.end():]
    open("portrait_px.py", "w", encoding="utf-8").write(src)
    print("已替换，新总行数:", len(new_rows))
else:
    print("未找到边界")
