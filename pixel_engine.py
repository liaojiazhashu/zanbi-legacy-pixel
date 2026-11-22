# -*- coding: utf-8 -*-
"""程序化像素美术引擎：锯齿轮廓 + 簇状明暗 + 抖动过渡 + 服装褶皱。

核心思想（真正像素风，非几何平滑）：
- 所有线条用 Bresenham 锯齿线；
- 明暗按固定光照方向（左上）分 4 层色阶，边界是阶梯簇状而非渐变；
- 明暗过渡用棋盘格抖动 dithering；
- 服装加褶皱线、纽扣、纹理点等细节。
"""
from PIL import Image


class Canvas:
    def __init__(self, w, h, bg=(24, 26, 30)):
        self.w, self.h = w, h
        self.img = Image.new("RGB", (w, h), bg)
        self.px = self.img.load()

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = c

    # Bresenham 锯齿线
    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx = abs(x1 - x0); sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0); sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    # 像素椭圆（中点算法，锯齿边缘）
    def ellipse(self, cx, cy, rx, ry, c):
        cx, cy, rx, ry = int(cx), int(cy), int(rx), int(ry)
        if rx <= 0 or ry <= 0:
            return
        x, y = rx, 0
        dx, dy = 1 - 2 * rx, 1
        err = 0
        while x >= y:
            self.set(cx + x, cy + y, c); self.set(cx - x, cy + y, c)
            self.set(cx + x, cy - y, c); self.set(cx - x, cy - y, c)
            self.set(cx + y, cy + x, c); self.set(cx - y, cy + x, c)
            self.set(cx + y, cy - x, c); self.set(cx - y, cy - x, c)
            y += 1; err += dy; dy += 2
            if 2 * err + dx > 0:
                x -= 1; err += dx; dx += 2

    # 实心椭圆（带明暗 4 层，光照左上）
    def ellipse_shaded(self, cx, cy, rx, ry, pal, outline=None):
        cx, cy, rx, ry = int(cx), int(cy), int(rx), int(ry)
        if rx <= 0 or ry <= 0:
            return
        hi, mid, lo, dk = pal[0], pal[1], pal[2], pal[3]
        for dy in range(-ry, ry + 1):
            for dx in range(-rx, rx + 1):
                v = (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry)
                if v > 1.0:
                    continue
                # 光照：左上亮，右下暗；径向渐变 4 层
                if v <= 0.25:
                    c = hi
                elif v <= 0.55:
                    c = mid
                elif v <= 0.80:
                    c = lo
                else:
                    c = dk
                # 边缘抖动：最外层用 dk 加棋盘格
                if v > 0.85 and (dx + dy) % 2 == 0:
                    c = dk
                self.set(cx + dx, cy + dy, c)
        if outline:
            self.ellipse(cx, cy, rx, ry, outline)
            self.ellipse(cx, cy, rx + 1, ry + 1, outline)

    # 实心矩形（带明暗，光照左上）
    def rect_shaded(self, x0, y0, x1, y1, pal, outline=None):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        hi, mid, lo, dk = pal[0], pal[1], pal[2], pal[3]
        w, h = x1 - x0, y1 - y0
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                # 左上亮，右下暗
                u = (x - x0) / max(1, w)
                v = (y - y0) / max(1, h)
                d = u + v  # 对角光照
                if d < 0.7:
                    c = hi
                elif d < 1.1:
                    c = mid
                elif d < 1.5:
                    c = lo
                else:
                    c = dk
                # 边缘暗一圈
                if x == x0 or y == y0:
                    c = hi
                if x == x1 or y == y1:
                    c = dk
                self.set(x, y, c)
        if outline:
            self.rect(x0, y0, x1, y1, outline)

    def rect(self, x0, y0, x1, y1, c):
        self.line(x0, y0, x1, y0, c)
        self.line(x1, y0, x1, y1, c)
        self.line(x1, y1, x0, y1, c)
        self.line(x0, y1, x0, y0, c)

    def fill(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    # 抖动填充（两种颜色棋盘格）
    def dither(self, x0, y0, x1, y1, c1, c2, phase=0):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        if x0 > x1: x0, x1 = x1, x0
        if y0 > y1: y0, y1 = y1, y0
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c1 if (x + y + phase) % 2 == 0 else c2)


def upscale(cv, scale=3):
    return cv.img.resize((cv.w * scale, cv.h * scale), Image.NEAREST)
