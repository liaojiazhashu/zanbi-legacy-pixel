# Pony Town 分层绘制法（像素角色部件化设计）

> 来源：Pony Town 社区教程（贴吧私服美工教程）+ Spriters Resource sprite sheet + pixel.horse 开源仓库。

## 一、Pony Town 的核心设计方法：部件分层

角色 = 多个「部件」分层叠加，每部件独立绘制：

| 层（前→后） | 部件 | 说明 |
|------------|------|------|
| front | 刘海（前鬃毛最上层） | 最前，可理解为人的刘海 |
| top | 前鬃毛主体 | 在耳朵、角的下层 |
| behind | 前鬃毛后发 | 后发，最下 |
| back | 后鬃毛（背毛） | 长在背上，耳朵下、身体上 |
| back behind | 后鬃毛后发 | 最后 |

**核心法则**：所有图层都要把「被遮挡的部分」画完（不准偷懒）——这样部件换位置/换部件时不露破绽。

## 二、配色规律（Pony Town 官方）

- 描边：**深灰**（非纯黑）。
- 底色：**白色**。
- 阴影：**浅灰**。
- 光源：**左上角打光 → 右下方画阴影**。
- 抗锯齿：在线条边缘点阴影，提供柔和的 AA 视觉效果。

## 三、可迁移的设计方法（重点）

1. **部件化分层**（同 LPC base+legs+torso+hair+eyes）：角色拆成独立部件，每部件画完整（含被遮挡部分），叠加拼合。
2. **柔和描边**：深灰描边（非纯黑）+ 边缘阴影做 AA，比硬黑描边更柔和。
3. **左上光源统一**：所有部件阴影方向一致（右下），保证拼合后光影统一。
4. **白底浅灰阴影**：高明度浅灰系配色，适合可爱/柔和风格（vs LPC 的深紫棕描边+暖棕暗部）。

## 四、素材来源与版权（重要）

- **Pony Town 官方素材**：pixel.horse 开源仓库明确「**assets cannot be used for commercial purposes**... without permission」（CC BY，不可商用）——只能学习参考技法，不可商用。
- **fan-made sprite sheet**（DeviantArt Eclipse-Knight15 "upgraded PonyTown sprite sheet (ponies version)" 1300x1935px + "Background parts"）："no permission required, but please give credit"（可自由用，署名游戏+作者）。
- **Spriters Resource**：Pony Town General Sprites（993x345，37.37KB），可下载学习。
- **Lospec**（lospec.com）/ **Pixel Joint**（pixeljoint.com）：像素画社区，调色板数据库+教程+sprite 集合，免费学习资源。

## 五、对素材库的贡献

- 设计方法：部件化分层 + 柔和描边 + 左上光源统一（补 LPC 之外的第二套分层范式）。
- 素材：Pony Town 风格适合「可爱/柔和」题材（vs LPC 的「写实 RPG」题材），覆盖素材库的「萌系/社交游戏」风格缺口。
