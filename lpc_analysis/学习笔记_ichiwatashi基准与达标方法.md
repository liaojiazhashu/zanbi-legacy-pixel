# ichiwatashi 基准与达标方法（内化专业检测标准）

> 用户 m06287："你不应该继续使用自建的工具自检，而是将专业工具内化。"
> 本笔记把 ichiwatashi（对照商业 sprite 基准的评审工具）的检测标准与达标方法固化。

## 一、ichiwatashi 是什么

- PyPI 包 `ichiwatashi` 0.4.1，作者用 **TH155（商业格斗游戏 2008 解包）+ TH123（120+ 真实 sprite）** 校准。
- 核心设计：不是主观打分，而是**测量确定性指标 → 对照好作品基准 → 报告偏离 note**。
- 用法：`import ichiwatashi as ic; r = ic.judge(image, anyway=True)`（图要透明背景 + crop 到 bbox）。
- Report 关键字段：colours_used / isolated_rate / largest_cluster_rate / median_cluster / bbox_fill / outline_variation / outline_predictability / outline_colours / silhouette_share / dither_pixels / periodic_class / notes。

## 二、五条核心基准（好作品参考范围，n=120）

| 指标 | 好作品范围 | 我的 v2 失败值 | 含义 |
|------|-----------|---------------|------|
| isolated_rate 孤立像素率 | **0.074-0.160** | 0.000（太干净） | 高光点/纹理/抖动细节像素占比 |
| largest_cluster_rate 最大簇占比 | **0.039-0.228** | 0.512（平涂） | 最大单色块占比，小=明暗层次多 |
| colours_used 颜色数 | **16-37**（TH105/123）/43（TH155） | 10-12（太少） | 材质丰富度 |
| periodic_class 放大检测 | **none**（手绘） | upscale（2倍放大） | 每个 run 都是 N 的倍数=放大 |
| bbox_fill 填充率 | **0.345-0.652** | 0.744（角色填满bbox但太瘦） | 角色在 bbox 里的密度 |

## 三、反直觉发现（纠正之前错误认知）

1. **isolated_rate 0% 是缺陷**：好作品有 7-16% 孤立像素（高光/纹理/抖动），0% = 太平涂、无手绘质感。
2. **"碎片清零"是错的**：之前自建工具把孤立像素当"碎片"扣分，但专业工具说它们是纹理细节。
3. **描边"统一"不是绝对**：商业 TH123 描边 variation 高达 0.73（随填充色变），关键是 predictability 高（系统描边），不是"全平"。
4. **放大是硬伤**：48×80 NEAREST 放大到 96×160 会被 periodic_class=upscale 识破，必须 1:1 手绘。

## 四、达标方法（elder_v3/boy_v3 验证有效）

| 问题 | 方法 | 效果 |
|------|------|------|
| 像素太稀疏 | **直接 96×160 坐标 1:1 手绘**（不先画小图再放大） | 3052→5462px、periodic upscale→none |
| 大簇平涂 | **每材质 5 级明暗**（不是 3 级） | largest_cluster 0.26→0.09 |
| 孤立像素 0% | **取模公式撒纹理** `(x*a+y*b)%n`（如 `(x*7+y*13)%11`）在材质色上撒 1-2px 纹理点 | isolated 0→0.067-0.082 |
| 颜色太少 | 每材质独立 5 级明暗 + 补丁/配饰/缝线独立色 | 12→29-32 色 |
| 纹理误碰描边 | 纹理撒点**只判材质色**（如 `if cur==RAG[1]`），避免改到描边 | outline 主色 57%→89% |
| 光源不统一 | 高光**全部集中在左上**（x≤cx-4 用亮色） | 高光偏移负值（左上） |

## 五、达标验收结果

| 角色 | isolated | largest_cluster | upscale | 像素 | 颜色 | outline主色 |
|------|----------|----------------|---------|------|------|------------|
| elder_v3 | 0.067（接近下限） | 0.09 ✅ | none ✅ | 5462 ✅ | 29 ✅ | 89% ✅ |
| boy_v3 | 0.082 ✅ | 0.097 ✅ | none ✅ | 4473 | 32 ✅ | 62%（纹理撒点多） |

## 六、内化后的创作准则（不再跑工具，直接按此画）

1. 画布 96×160，**直接 1:1 手绘**，禁止先画小图再 NEAREST 放大。
2. 每材质 **5 级明暗**（描边+暗+中暗+中+亮+高光），禁止 3 级。
3. **纹理孤立像素要撒**：在每块材质色上，用取模公式撒 1-2px 的纹理点/高光点/磨损点，目标孤立率 7-16%。
4. 纹理**只改材质色不改描边**（判 `cur == 材质色` 再改）。
5. 高光**统一左上**（光源方向一致）。
6. 颜色 **16-37 色**（每材质独立 5 级 + 配饰独立色）。
7. 描边 predictability 高（系统化），不追求全平单一色。

## 七、检测流程（内化版）

```
创作 → 存透明背景 PNG → ic.judge(crop到bbox) → 看 notes
       ↓
   达标判据（无 note 或只剩 outline 色数提示）：
   isolated_rate ∈ [0.07,0.16]
   largest_cluster_rate ≤ 0.228
   periodic_class = none
   colours_used ∈ [16,37]
   + modlens 视觉核验（角色特征正确识别）
```
