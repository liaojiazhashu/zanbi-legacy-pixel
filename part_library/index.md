# 像素素材库索引（part_library）

> 目标：全覆盖所有职业/性别/年龄/身份/科幻/奇幻/生物，为「文生像素图客户端」打基础。
> 三端：本机 D:\AAAAI\动画视频尝试\赞比的遗产\part_library / 服务器 srv:/www/git/zanbi-legacy-pixel.git / GitHub liaojiazhashu/zanbi-legacy-pixel

## 一、LPC 分层配件（part_library/lpc_parts/，下载中 21000/39009）

LPC（Liberated Pixel Cup）官方分层系统：每材质独立 6 色（1描边+5明暗），按 base→legs→torso→head→hair→eyes 叠加。23 顶层目录：arms/backpack/beards/body/cape/dress/eyes/facial/feet/hair/hat/head/legs/neck/quiver/shadow/shield/shoulders/tools/torso/weapon。

| 类别 | 数量/内容 |
|------|-----------|
| 帽子 hat/ | 15415 文件：pirate 7851 / magic 2811 / formal 1950 / holiday 1137 / cloth 870 / helmet 480 / accessory 189 / headband 127 |
| 身体 body/ | 6 体型（male/muscular/female/pregnant/teen/child）× 尾巴变体 |
| 其余 | arms/backpack/beards/cape/dress/eyes/facial/feet/head/legs/neck/quiver/shadow/shield/shoulders/tools/torso/weapon（下载中） |

## 二、肤色/发色变体

| 文件 | 内容 |
|------|------|
| remapped/skin_*_male_idle.png | 10 肤色变体：green/lime（兽人绿皮）、gray（亡灵灰皮）、coffee/copper/sienna（深肤色）、gold/dove/comet/ivory（浅肤色） |
| palettes/skin/*.gpl | 20 调色板（肤色10+发色9+眼睛3+金属6+布料25） |

## 三、Town Guards（Kenney 64px 卫兵，CC0）

| 目录 | 内容 |
|------|------|
| characters/town_guards/GUARD_0X_idle_down.png | 6 职业完整角色（24-28×55-71 透明 PNG） |
| characters/town_guards/portraits/*.png | 14 头像（archer 露脸/spearman/captain/heavy_guard 头盔/sword_shield/standard_bearer） |

## 四、奇幻种族

| 目录 | 内容 | 许可 |
|------|------|------|
| fantasy/dark_elves/ | 暗精灵 8 PNG（Nila122） | CC-BY |
| fantasy/long_ears/ | 精灵耳/兽人耳 12 部件 | CC-BY |
| fantasy/dwarves/ | 矮人 6 变体（普通/老年/守护者/英雄/领袖）×3 尺寸 | CC-BY/OGA-BY |
| fantasy/minotaur/ | 牛头人/牧神 6 PNG | CC-BY-SA/GPL |
| fantasy/skeleton/ | 骷髅（wulax） | CC-BY |

## 五、职业素材

| 目录 | 内容 |
|------|------|
| wulax/ | 中世纪奇幻包：盾/剑/矛/弓/骷髅战士 |
| farming/daneeklu | 农业包：character/magic 5/tilesets 12/ui |
| magic/starhat | 法师帽 |
| Skorpio_SciFi/ | 特工/装甲/机器人 Cutiebots 5/Mechs/武器 |

## 六、生物/怪物/坐骑

| 目录 | 内容 |
|------|------|
| animals/ | 动物 33 + 马 5 色 + 天马 pegasus |
| monsters/ | 哥布林/魔像/蜘蛛 11sheet/狼 7/小恶魔/蛙人 3/南瓜怪/甲虫 |
| fantasy/dragon/ | 龙 4 色双尾背龙 |
| kenney/monster/ | 尖刺怪物（Bevouliin） |

## 七、科幻

| 目录 | 内容 |
|------|------|
| scifi/ | 太空瓦片 + items + 科幻敌人 14 critter |
| Skorpio_SciFi/ | 完整科幻角色包 |
| environment/Pack01_PixelArt_scifi_forest/ | 190+ 科幻+森林资产（下载中） |

## 八、特效（effects/）

| 目录 | 内容 |
|------|------|
| pixelart_spells/ | 23 法术（火/冰/雷/魔法/水/风/暗）PNG+Aseprite |
| spell_effects/ | 火球 9帧/冰矛 6帧/雷球 8帧 逐帧 PNG |

## 九、UI/图标/字体/场景

| 目录 | 内容 |
|------|------|
| ui/ | 科幻 UI（scifi_ui_buch.psd）+ 金色奇幻 UI（golden_ui.psd+split.png） |
| icons/ | 496 RPG 图标（7Soul1 CC0，武器/盔甲/药水/食物/宝石） |
| fonts/ | Boxy Bold 像素字体（CC0 TTF） |
| environment/town_rpg_pack/ | RPG 城镇瓦片（ansimuz CC0，FF6/SNES 风格） |
| environment/ | 太空瓦片 + 190+ 科幻森林包 |

## 十、待补缺口

- 平民职业（商人/医生/僧侣）—— LPC hat 目录含王冠/僧侣帽/商人帽，下载后补齐
- 身份（国王/贵族）—— LPC hat 王冠
- 更多科幻角色（宇航员）
- 龙/神话生物更多变体

## 十一、学习笔记（lpc_analysis/，24+ 份）

调色板系统/人物架构/6体型/6风格/职业差异化/动画帧间/女性角色/怪物设计/动物/Tiny16/表情/武器道具/特效/ichiwatashi基准/露脸头像/PonyTown/奇幻调色板/表情/科幻敌人……

## 十二、素材库统计（2026-11-23 盘点）

| 目录 | 文件数 | 大小 | 内容 |
|------|--------|------|------|
| lpc_parts | 37814 | 53.4 MB | LPC 分层配件（下载中，目标 39009） |
| icons | 497 | 2.9 MB | 496 RPG 图标 |
| scifi | 93 | 2.3 MB | 科幻（Skorpio/瓦片/敌人） |
| fantasy | 65 | 2.1 MB | 奇幻种族（精灵/矮人/牛头人/龙） |
| monsters | 21 | 2.1 MB | 怪物（哥布林/蜘蛛/狼/小恶魔） |
| environment | 28 | 1.3 MB | 场景（城镇瓦片/太空/科幻森林） |
| farming | 26 | 1.1 MB | 农业包 |
| creatures | 5 | 1.0 MB | 生物 |
| ui | 3 | 0.7 MB | UI（科幻+金色） |
| animals | 7 | 0.3 MB | 马/天马/动物 |
| characters | 46 | 0.2 MB | 卫兵/肖像/精灵女 |
| effects | 68 | 0.1 MB | 特效（23法术+火冰雷） |
| 其余 | 63 | 0.0 MB | 调色板/肤色变体/部位/字体 |
| **总计** | **38751** | **67.6 MB** | 11 大类全覆盖 |
