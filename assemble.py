# -*- coding: utf-8 -*-
"""把全部场景的 PNG 帧序列合成带配音的 mp4，再按顺序拼接成《赞比的遗产》成片。

步骤：
1. 每场景 PNG 序列 -> 无音轨 mp4（libx264, yuv420p, 30fps, 1920x1080）。
2. 每场景多段配音按各自起始时间 adelay 延迟 -> amix 合并 -> aac 音轨 -> mux。
   （章节卡 c0a/c0b/c0c 无配音，补静音音轨，保证 concat 参数一致。）
3. 18 场景按 ORDER 顺序 concat 成 D:\AAAAI\动画视频尝试\赞比的遗产\赞比的遗产.mp4。
"""
import json
import os
import subprocess
from collections import OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(BASE, "frames")
AUDIO = os.path.join(BASE, "audio")
CLIPS_DIR = os.path.join(BASE, "clips")
FINAL = os.path.join(BASE, "赞比的遗产.mp4")

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"

# 场景顺序（成片拼接顺序：上 / 中 / 下 三幕）
ORDER = [
    "c0a", "s01", "s02", "s03", "s04", "s05", "s06", "s07",
    "c0b", "s08", "s09", "s10", "s11",
    "c0c", "s12", "s13", "s14", "s15",
]

# 场景 key -> 帧目录名（帧目录与场景 key 一致）
FRAME_DIR = {k: k for k in ORDER}

from gen_audio import CLIPS  # noqa: E402

with open(os.path.join(AUDIO, "timings.json"), encoding="utf-8") as f:
    DUR = json.load(f)

# 每场景的配音段列表（保持 CLIPS 顺序）
scenes = OrderedDict()
for name, role, text, mech in CLIPS:
    key = name.split("_")[0]
    scenes.setdefault(key, []).append(name)

START = {"s02": 0.8}
GAP = 0.2


def seg_starts(key):
    """返回 [(音频名, 起始秒), ...]，起始 = 段累计（复用 recalc_subtitles.py 的约定）。"""
    t = START.get(key, 1.0)
    out = []
    for name in scenes.get(key, []):
        out.append((name, t))
        t += (DUR.get(name) or 0.0) + GAP
    return out


def run(args):
    r = subprocess.run(args, capture_output=True, encoding="utf-8", errors="ignore")
    if r.returncode != 0:
        raise SystemExit(f"[FAIL] {' '.join(args[:6])}...\n{r.stderr[-3000:]}")
    return r


def render_video(key):
    """PNG -> 无音轨 mp4。"""
    out = os.path.join(CLIPS_DIR, f"{key}_v.mp4")
    src = os.path.join(FRAMES, FRAME_DIR[key], "f%05d.png")
    run([FFMPEG, "-y", "-framerate", "30", "-i", src,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
         "-an", out])
    return out


def mux_audio(key, video):
    """给视频配音轨。无配音 -> 静音；多段 -> adelay + amix。"""
    out = os.path.join(CLIPS_DIR, f"{key}.mp4")
    starts = seg_starts(key)
    if not starts:
        # 章节卡：静音音轨（时长取视频时长）
        run([FFMPEG, "-y", "-i", video,
             "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out])
        return out

    inputs = [video] + [os.path.join(AUDIO, f"{n}.mp3") for n, _ in starts]
    # filter_complex
    parts = []
    labels = []
    for i, (n, s) in enumerate(starts):
        ms = int(round(s * 1000))
        parts.append(f"[{i + 1}:a]adelay={ms}:all=1,aresample=48000,"
                     f"aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]")
        labels.append(f"[a{i}]")
    parts.append(f"{''.join(labels)}amix=inputs={len(starts)}:duration=longest,apad[aout]")
    fc = ";".join(parts)

    cmd = [FFMPEG, "-y", "-i", video]
    for n, _ in starts:
        cmd += ["-i", os.path.join(AUDIO, f"{n}.mp3")]
    cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-shortest", out]
    run(cmd)
    return out


def main():
    os.makedirs(CLIPS_DIR, exist_ok=True)
    clips = []
    for key in ORDER:
        print(f"[1/2] 渲染视频 {key}", flush=True)
        v = render_video(key)
        print(f"[2/2] 配音 {key}", flush=True)
        c = mux_audio(key, v)
        clips.append(c)
        print(f"  -> {c}", flush=True)

    # concat
    listfile = os.path.join(CLIPS_DIR, "concat.txt")
    with open(listfile, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.replace(os.sep, '/')}'\n")
    print("拼接成片 ...", flush=True)
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listfile,
         "-c", "copy", FINAL])
    print(f"\n完成 -> {FINAL}", flush=True)


if __name__ == "__main__":
    main()
