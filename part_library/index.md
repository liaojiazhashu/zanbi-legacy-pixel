# 像素素材库索引（part_library）

> 目标：覆盖所有职业/性别/年龄/身份/科幻/奇幻/生物，供未来拼接调用。
> 索引格式：`路径 | 类别 | 尺寸 | 调色板 | 来源许可`

## 一、目录结构

```
lpc_layers/            LPC 分层素材（体型/发型/服装/眼睛，64×64 分层 PNG）
kenney/                已下载的 Kenney/OpenGameArt 完整素材包
part_library/          【新建】拆解后的部位素材库（头/身/腿/武器/道具）
  ├── head/            头部（露脸头像/头盔/帽子）
  ├── body/            身体（躯干/服装）
  ├── legs/            腿/鞋
  ├── arms/            手臂/手
  ├── weapon/          武器
  ├── item/            道具/配件
  └── full/            完整角色（按类别子目录：职业/性别/年龄/身份/科幻/奇幻/生物）
```

## 二、类别覆盖矩阵（✅已有 / ⬜待下载 / 🔶部分）

| 类别 | 状态 | 已有素材 | 缺口 |
|------|------|---------|------|
| 职业-战士系 | ✅ | Town Guards 6 职业卫兵 | 无 |
| 职业-法师 | ⬜ | 无 | 法师/巫师 |
| 职业-平民 | ⬜ | 无 | 农民/商人/医生/工匠 |
| 性别-男 | ✅ | LPC male/muscular + 卫兵 | 无 |
| 性别-女 | 🔶 | LPC female + Cartoon Female | 女性职业少 |
| 年龄-儿童 | 🔶 | LPC child | 儿童职业/服装少 |
| 年龄-老年 | 🔶 | LPC elderly 眼 + balding | 老年专用素材少 |
| 身份-贵族 | ⬜ | 无 | 国王/贵族/僧侣 |
| 科幻-机械 | 🔶 | scifi_characters（1 个） | 机器人/宇航员/外星人 |
| 奇幻-种族 | ⬜ | 无 | 精灵/矮人/兽人/亡灵 |
| 生物-动物 | ✅ | cute-animals 33 种 | 无 |
| 生物-怪物 | 🔶 | spiky monster（1 个） | 龙/神话生物/坐骑 |

## 三、已有素材清单（详细）

### LPC（lpc_layers/，CC0/CC-BY，Universal-LPC-Spritesheet-Character-Generator）
- body/：6 体型（male/muscular/female/pregnant/teen/child）× idle+walk，每体型独立调色板
- hair/：65 发型（balding/swoop/buzzcut/parted/messy/pigtails/natural 等）× idle+walk
- legs/：formal/pants/skirts_plain/skirts_legion 等 6 款
- torso/：longsleeve/longsleeves/longsleeve_female/aprons 2款/armour 3款/jacket santa
- eyes/：adult/elderly/child，各 6 表情（default/anger/closing/sad/shock/shame）

### Kenney（kenney/，CC0）
- pixel-platformer/：18×18 tile 平台跳跃角色
- tiny-dungeon/：16×16 地牢角色
- tiny-town/：16×16 城镇角色
- tiny-battle/：16×16 战斗角色
- roguelike-characters/：16×16 肉鸽角色

### Town Guards（kenney/town_guards/，CC0，64×64）
- 6 职业：spearman/sword_shield/heavy_guard/captain/standard_bearer/archer
- 各 3 帧 idle + walk/attack + portraits 肖像

### 女性（kenney/female/，CC0）
- Elfia.png（256×175，9 动画约 30 小精灵，绿衣金发女精灵）
- turn-around.png（1153×847，Cartoon Female 转身+走路）

### 怪物/动物/科幻
- kenney/monster/：spiky monster（369×369 金色尖刺怪物）
- cute-animals/：33 动物（2-18 色极简）
- scifi_characters.png：机械角色（14 色，蓝黑描边+发光青）
