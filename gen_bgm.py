# -*- coding: utf-8 -*-
"""程序化合成 BGM——分情绪主题，无外部模型，纯 Python 波形合成。
生成 5 个主题 WAV，供 assemble() 按场景情绪混合到成片。
"""
import math
import array
import wave
import os

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bgm")
os.makedirs(OUT, exist_ok=True)

# 音符频率（Hz）
NOTE = {
    "A2": 110.00, "B2": 123.47, "C3": 130.81, "D3": 146.83, "E3": 164.81,
    "F3": 174.61, "G3": 196.00, "A3": 220.00, "B3": 246.94, "C4": 261.63,
    "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00, "A4": 440.00,
    "B4": 493.88, "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99,
    "A5": 880.00,
}


def note_freq(name):
    return NOTE[name]


class Synth:
    def __init__(self):
        self.buf = array.array("h")

    def _env(self, i, n, attack, release):
        a = int(attack * SR)
        r = int(release * SR)
        if i < a:
            return i / a
        if i > n - r:
            return max(0.0, (n - i) / r)
        return 1.0

    def tone(self, freq, dur, vol=0.3, attack=0.04, release=0.12, vibrato=0.0):
        n = int(dur * SR)
        for i in range(n):
            env = self._env(i, n, attack, release)
            # 颤音（缓慢音高波动）
            vf = freq
            if vibrato > 0:
                vf = freq * (1.0 + vibrato * math.sin(2 * math.pi * 5.0 * i / SR))
            # 基频 + 泛音（模拟弦乐/柔和音色）
            t = 2 * math.pi * i / SR
            s = (math.sin(vf * t)
                 + 0.35 * math.sin(2 * vf * t)
                 + 0.15 * math.sin(3 * vf * t)
                 + 0.06 * math.sin(4 * vf * t))
            s *= 0.6  # 归一化
            self.buf.append(int(s * env * vol * 32767))
        return self

    def drone(self, freq, dur, vol=0.10, attack=1.0, release=1.0):
        """低音持续氛围底，音量低。"""
        n = int(dur * SR)
        for i in range(n):
            env = self._env(i, n, attack, release)
            t = 2 * math.pi * i / SR
            s = math.sin(freq * t) + 0.3 * math.sin(2 * freq * t)
            self.buf.append(int(s * env * vol * 32767))
        return self

    def silence(self, dur):
        n = int(dur * SR)
        for _ in range(n):
            self.buf.append(0)
        return self

    def write(self, path):
        with wave.open(path, "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(self.buf.tobytes())
        return path


def make_sorrow():
    """哀伤——A 小调，慢速下行，葬礼/死亡。"""
    s = Synth()
    # 低音 drone A2
    s.drone(NOTE["A2"], 30, vol=0.12)
    seq = ["A3", "C4", "E4", "A4", "G4", "E4", "C4", "A3"]
    s2 = Synth()
    for i, n in enumerate(seq):
        s2.tone(note_freq(n), 3.0, vol=0.22, attack=0.3, release=0.8, vibrato=0.004)
    # 叠加：旋律层从 8s 开始，drone 在前
    full = array.array("h")
    for i in range(30 * SR):
        dv = s.buf[i] if i < len(s.buf) else 0
        mv = s2.buf[i] if i < len(s2.buf) else 0
        full.append(int(0.7 * dv + 0.8 * mv))
    s.buf = full
    return s.write(os.path.join(OUT, "sorrow.wav"))


def make_hope():
    """温暖/希望——C 大调，中速上行，创业/复苏。"""
    s = Synth()
    s.drone(NOTE["C3"], 32, vol=0.10)
    seq = ["C4", "E4", "G4", "C5", "G4", "E4", "D4", "E4", "C4", "D4", "E4", "G4"]
    s2 = Synth()
    for n in seq:
        s2.tone(note_freq(n), 1.6, vol=0.20, attack=0.08, release=0.2, vibrato=0.003)
    full = array.array("h")
    for i in range(32 * SR):
        dv = s.buf[i] if i < len(s.buf) else 0
        mv = s2.buf[i] if i < len(s2.buf) else 0
        full.append(int(0.7 * dv + 0.8 * mv))
    s.buf = full
    return s.write(os.path.join(OUT, "hope.wav"))


def make_mystery():
    """神秘/疏离——稀疏低音 + 空灵高音，矿坑/回声/车间。"""
    s = Synth()
    s.drone(NOTE["D3"], 34, vol=0.11)
    seq = ["D3", "A3", "D4", "E4", "A3", "E4", "D4", "A3", "D3", "A3", "E4", "A4"]
    s2 = Synth()
    for i, n in enumerate(seq):
        s2.tone(note_freq(n), 2.2, vol=0.16, attack=0.5, release=1.0, vibrato=0.005)
    full = array.array("h")
    for i in range(34 * SR):
        dv = s.buf[i] if i < len(s.buf) else 0
        mv = s2.buf[i] if i < len(s2.buf) else 0
        full.append(int(0.75 * dv + 0.8 * mv))
    s.buf = full
    return s.write(os.path.join(OUT, "mystery.wav"))


def make_epic():
    """史诗/悲壮——低音强奏渐强，戴森环崩塌。"""
    s = Synth()
    s.drone(NOTE["A2"], 36, vol=0.16)
    seq = ["A2", "A2", "C3", "D3", "E3", "D3", "C3", "A2", "A2", "C3", "D3", "E3",
           "E3", "F3", "G3", "A3", "G3", "E3"]
    s2 = Synth()
    for i, n in enumerate(seq):
        vol = 0.16 + 0.012 * i  # 渐强
        s2.tone(note_freq(n), 1.8, vol=min(vol, 0.34), attack=0.05, release=0.3)
    full = array.array("h")
    for i in range(36 * SR):
        dv = s.buf[i] if i < len(s.buf) else 0
        mv = s2.buf[i] if i < len(s2.buf) else 0
        full.append(int(0.7 * dv + 0.85 * mv))
    s.buf = full
    return s.write(os.path.join(OUT, "epic.wav"))


def make_serene():
    """空灵/终结——极简高音长音，写书/立方体。"""
    s = Synth()
    s.drone(NOTE["A3"], 38, vol=0.09)
    seq = ["A4", "G4", "E4", "A4", "G4", "E4", "C5", "A4"]
    s2 = Synth()
    for n in seq:
        s2.tone(note_freq(n), 3.5, vol=0.15, attack=1.2, release=1.8, vibrato=0.006)
    full = array.array("h")
    for i in range(38 * SR):
        dv = s.buf[i] if i < len(s.buf) else 0
        mv = s2.buf[i] if i < len(s2.buf) else 0
        full.append(int(0.7 * dv + 0.8 * mv))
    s.buf = full
    return s.write(os.path.join(OUT, "serene.wav"))


if __name__ == "__main__":
    print(make_sorrow())
    print(make_hope())
    print(make_mystery())
    print(make_epic())
    print(make_serene())
    print("BGM 生成完成")
