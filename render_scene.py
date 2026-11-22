#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""渲染单个场景 HTML 为 PNG 帧序列（Playwright/Edge，默认 1920x1080）。

用法：
    python render_scene.py <scene.html> <输出目录> [--fps 30] [--duration 6] [--w 1920] [--h 1080]

场景 HTML 约定：必须实现 window.setTime(t)，t 为秒；可选 window.SCENE_DURATION。
"""
import argparse
import os
import sys
from urllib.request import pathname2url

from playwright.sync_api import sync_playwright


def render(html_path, out_dir, fps=30.0, duration=6.0, width=1920, height=1080):
    html_path = os.path.abspath(html_path)
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    n_frames = int(round(duration * fps))
    file_url = "file:///" + pathname2url(html_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=True,
            args=[
                "--ignore-gpu-blocklist",
                "--enable-gpu",
                "--use-angle=d3d11",
            ],
        )
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=1,
        )
        page.goto(file_url)
        page.wait_for_load_state("load")
        page.wait_for_function("typeof window.setTime === 'function'")

        # 若页面声明了时长，覆盖命令行时长
        declared = page.evaluate("typeof window.SCENE_DURATION === 'number' ? window.SCENE_DURATION : null")
        if declared:
            duration = float(declared)
            n_frames = int(round(duration * fps))
            print(f"scene 声明时长 {duration:.2f}s -> {n_frames} 帧", flush=True)

        for i in range(n_frames):
            t = i / fps
            page.evaluate("window.setTime(%r)" % t)
            out_png = os.path.join(out_dir, "f%05d.png" % i)
            page.screenshot(path=out_png)
            if i % 60 == 0:
                print(f"frame {i}/{n_frames} (t={t:.2f}s)", flush=True)

        browser.close()

    print(f"DONE: {n_frames} frames -> {out_dir}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("out_dir")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--duration", type=float, default=6.0)
    ap.add_argument("--w", type=int, default=1920)
    ap.add_argument("--h", type=int, default=1080)
    args = ap.parse_args()
    render(args.scene, args.out_dir, args.fps, args.duration, args.w, args.h)


if __name__ == "__main__":
    main()
