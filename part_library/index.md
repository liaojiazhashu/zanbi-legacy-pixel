# 像素素材库索引（part_library）

> 目标：覆盖所有职业/性别/年龄/身份/科幻/奇幻/生物，供未来拼接调用。
> 索引格式：`路径 | 类别 | 尺寸 | 调色板 | 来源许可`

## 一、目录结构

```
lpc_layers/            LPC 分层素材（体型/发型/服装/眼睛，64×64 分层 PNG）
kenney/                已下载的 Kenney/OpenGameArt 完整素材包
part_library/          【素材库】拆解后的部位素材 + 完整角色 + 调色板
  ├── fantasy/         奇幻（dark_elves 暗精灵 / long_ears 精灵兽人耳 / starhat 法师帽）
  ├── animals/         生物（马5色 / 天马 / horse-1.1.zip）
  ├── scifi/           科幻（太空瓦片 / 能源水晶 / 科幻敌人）
  ├── farming/         农业职业（daneeklu：角色/魔法/瓦片/UI）
  ├── wulax/           奇幻武器（盾/长剑/细剑/长矛/弓/骷髅/战斗假人）
  ├── palettes/        调色板（skin 11 肤色 / hair 9 发色 .gpl）
  └── remapped/        肤色变体（10 种：绿皮/灰皮/深浅肤色）
```

## 二、类别覆盖矩阵（✅已有 / ⬜待下载 / 🔶部分）

| 类别 | 状态 | 已有素材 | 缺口 |
|------|------|---------|------|
| 职业-战士系 | ✅ | Town Guards 6 职业 + wulax 武器 5 种 | 无 |
| 职业-法师 | ✅ | starhat 法师帽 + daneeklu 5 魔法 | 法杖/长袍 |
| 职业-农民 | ✅ | daneeklu 农业包（作物/栅栏/犁地） | 农民角色体 |
| 职业-平民 | ⬜ | 无 | 商人/医生/工匠/厨师 |
| 性别-男 | ✅ | LPC male/muscular + 卫兵 | 无 |
| 性别-女 | 🔶 | LPC female + Cartoon Female + 暗精灵女 | 女性职业少 |
| 年龄-儿童 | 🔶 | LPC child | 儿童职业/服装少 |
| 年龄-老年 | 🔶 | LPC elderly 眼 + balding | 老年专用素材少 |
| 身份-贵族 | ⬜ | 无 | 国王/贵族/僧侣 |
| 科幻-机械 | 🔶 | scifi_characters + 太空瓦片 + 科幻敌人 14 | 宇航员/机器人角色 |
| 奇幻-种族 | ✅ | 暗精灵 8 + 精灵耳 12（含兽人耳）+ 骷髅 | 矮人/亡灵完整体 |
| 奇幻-肤色 | ✅ | 绿皮/灰皮/深浅 10 变体 | 无 |
| 生物-动物 | ✅ | cute-animals 33 + 马 5 色 + 天马 | 无 |
| 生物-怪物 | 🔶 | spiky monster + 科幻敌人 14 | 龙/神话生物 |

## 三、已有素材清单（详细）

### LPC（lpc_layers/，CC0/CC-BY，Universal-LPC-Spritesheet-Character-Generator）
- body/：6 体型（male/muscular/female/pregnant/teen/child）× idle+walk
- hair/：65 发型（balding/swoop/buzzcut/parted/messy/pigtails/natural 等）
- legs/：formal/pants/skirts_plain 等 6 款
- torso/：longsleeve/longsleeves/longsleeve_female/aprons 2款/armour 3款/jacket santa
- eyes/：adult/elderly/child，各 6 表情

### Kenney（kenney/，CC0）
- pixel-platformer（18×18）/ tiny-dungeon（16×16）/ tiny-town（16×16）/ tiny-battle（16×16）/ roguelike-characters（16×16）
- town_guards（64×64 6 职业卫兵 + 肖像）
- female（Elfia.png 女精灵 + turn-around.png 卡通女性）

### 奇幻（part_library/fantasy/）
- dark_elves/：暗精灵完整角色 8 PNG（Nila122，CC-BY/OGA-BY）
- long_ears/：精灵/兽人耳部件 12 PNG（含 orc/rorc 兽人耳）
- LPC_starhat.zip：法师星月帽（Michael Whitlock）

### 武器（part_library/wulax/，CC-BY-SA/GPL/OGA-BY）
- lpc_entry/：盾/长剑/细剑/长矛/弓/骷髅/战斗假人（多动画帧）
- expansion_pack/：盾/剑/骷髅弓/箭袋/战斗假人死亡

### 科幻（part_library/scifi/）
- scifi_space_rpg_tiles_lpcized.png：LPC 太空瓦片（Baŝto，CC-BY-SA/GPL）
- items.png：能源水晶道具
- ScifiCritters4.png：14 个 32×32 科幻敌人 robot/alien（Redshrike，CC-BY/OGA-BY）

### 生物（part_library/animals/）
- horse_{brown,black,gray,golden,white}.png：5 色马（bluecarrot16，CC-BY/GPL）
- pegasus.png：天马（AntumDeluge，翅膀 lemmling CC0）
- horse-1.1.zip：马完整包（AntumDeluge，64×64&64×85）

### 农业（part_library/farming/daneeklu/，CC-BY-SA/GPL）
- character/：grab_sheet + sword_sheet（抓取/剑动画）
- magic/：firelion/iceshield/snakebite/torrentacle/turtleshell 5 魔法
- tilesets/：farming_fishing/fence/plants/plowed_soil/reed/sand/wheat 等 12 瓦片
- ui/：scrollsandblocks（卷轴+木块）

### 调色板（part_library/palettes/，basxto，CC0）
- skin/：11 肤色（ivory/gold/sienna/copper/coffee/comet/dove/gray/lime/green 绿皮兽人/gray 灰皮亡灵）
- hair/：9 发色（brunet/blond/raven/redhead/whiteblond/white/pink/blue/green）

### 肤色变体（part_library/remapped/）
- 10 种肤色 remap body（绿皮/灰皮/深浅肤色，供拼接奇幻种族）

### 其他
- kenney/monster/：spiky monster（金色尖刺怪物）
- cute-animals/：33 动物（2-18 色极简）
- scifi_characters.png：机械角色（14 色，蓝黑描边+发光青）
