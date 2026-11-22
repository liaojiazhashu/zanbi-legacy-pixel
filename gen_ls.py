# -*- coding: utf-8 -*-
"""生成 LibreSprite JS 脚本（内联 8 角色 RGBA 像素数据），供 putImageData 批量重绘。"""
import sys
sys.path.insert(0, r"D:\AAAAI\动画视频尝试\赞比的遗产")
from pixel_engine import Canvas
import portrait_v5

W, H = 96, 160
OUT_JS = r"D:\AAAAI\_tools\libresprite_cfg\draw_all2.js"

parts = []
parts.append("var sprite = app.activeSprite;")
parts.append("var img = sprite.layer(0).cel(0).image;")
parts.append("var pc = app.pixelColor;")
parts.append("var W = 96, H = 160;")
parts.append("var names = ['elder','young','clone','richard','boy','girl','mech','cube'];")
parts.append("var datas = {};")

for name, fn in portrait_v5.ROLES:
    cv = Canvas(W, H)
    fn(cv)
    # 导出 RGBA 字节
    vals = []
    for y in range(H):
        for x in range(W):
            r, g, b = cv.px[x, y]
            vals.append(str(r)); vals.append(str(g)); vals.append(str(b)); vals.append("255")
    data_str = ",".join(vals)
    parts.append(f"datas['{name}'] = [{data_str}];")
    print(f"{name}: {len(vals)//4} px, {len(data_str)} chars")

parts.append("""
for (var i = 0; i < names.length; i++) {
    var name = names[i];
    var arr = datas[name];
    var u8 = new Uint8Array(arr.length);
    for (var j = 0; j < arr.length; j++) u8[j] = arr[j];
    img.putImageData(u8);
    var out = "D:/AAAAI/_tools/libresprite_cfg/out/" + name + ".png";
    sprite.saveAs(out, true);
    console.log("saved " + name);
}
console.log("ALL DONE");
""")

js = "\n".join(parts)
with open(OUT_JS, "w", encoding="utf-8") as f:
    f.write(js)
print(f"written {OUT_JS} ({len(js)} chars)")
