#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《赞比的遗产》全部角色配音 mp3（edge-tts），机械音做 ffmpeg 后期处理，输出时长清单。"""
import asyncio
import json
import os
import subprocess
import sys

# 关键：清空失效的本地代理（edge-tts 用 aiohttp，会读 env 代理）
for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

import edge_tts

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(BASE, "audio")
os.makedirs(AUDIO, exist_ok=True)

FFMPEG = None
try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"

# 角色 -> (voice, rate, pitch)
# rate 控制语速（-50%~+50%），pitch 控制音调（-xst/+xst 半音），二者共同塑造感情与顿挫
VOICES = {
    "narrator": ("zh-CN-YunxiNeural", "-8%", "-8Hz"),      # 理查德·史密斯，主叙述：沉稳略沉
    "boy":      ("zh-CN-YunxiaNeural", "-5%", "+8Hz"),      # 少年赞比：童声微亮
    "young":    ("zh-CN-YunjianNeural", "+8%", "+16Hz"),     # 青年赞比：昂扬自信
    "old":      ("zh-CN-YunxiNeural", "-20%", "-24Hz"),      # 老年赞比：苍老虚弱
    "clone":    ("zh-CN-YunyangNeural", "-8%", "-8Hz"),     # 克隆赞比：复杂克制
    "mech":     ("zh-CN-YunyangNeural", "-12%", "-16Hz"),    # 机械赞比（后期机械化）：空洞
    "cube":     ("zh-CN-YunyangNeural", "-12%", "-8Hz"),    # 立方体（后期机械化）：机械重复
    "girl":     ("zh-CN-XiaoyiNeural", "-5%", "+24Hz"),      # 小女孩：童声明亮
    "android":  ("zh-CN-XiaoxiaoNeural", "-8%", "-8Hz"),    # 仿生人：柔和迷茫
    "director": ("zh-CN-YunjianNeural", "+15%", "+8Hz"),    # 董事
}

# 每段台词的情绪覆盖：name -> (rate, pitch)，None 用 VOICES 基准
# 逐段设计感情：哀伤放慢降调、昂扬加快升调、迷茫放慢降调、机械冷静
EMOTION = {
    # S01 葬礼：庄重哀伤
    "s01_narrator": ("-12%", "-16Hz"),
    # S02 难民营：悲悯
    "s02_narrator": ("-10%", "-16Hz"),
    # S03 母亲之死：沉痛
    "s03_narrator1": ("-15%", "-24Hz"),
    "s03_boy": ("-10%", "+8Hz"),
    "s03_narrator2": ("-8%", "-8Hz"),
    # S04 十六岁：平实叙述，仿生人迷茫
    "s04_narrator1": ("-6%", "-8Hz"),
    "s04_android": ("-15%", "-8Hz"),
    "s04_narrator2": ("-6%", "-8Hz"),
    # S05 创业：渐昂扬，青年豪迈
    "s05_narrator": ("+2%", "+0Hz"),
    "s05_young": ("+12%", "+24Hz"),
    # S06 临终：平静感伤，老年嘱托
    "s06_narrator1": ("-10%", "-16Hz"),
    "s06_old1": ("-22%", "-32Hz"),
    "s06_narrator2": ("-8%", "-8Hz"),
    "s06_old2": ("-18%", "-24Hz"),
    # S07 宣读遗嘱：克制
    "s07_narrator": ("-6%", "-8Hz"),
    # S08 矿坑：宏大，克隆平静疯狂
    "s08_narrator1": ("-6%", "-8Hz"),
    "s08_clone": ("-8%", "-8Hz"),
    "s08_narrator2": ("-8%", "-16Hz"),
    # S09 回声卫星：空灵神秘，克隆迷茫
    "s09_narrator1": ("-12%", "-8Hz"),
    "s09_clone": ("-20%", "-16Hz"),
    "s09_narrator2": ("-8%", "-8Hz"),
    # S10 玉米田：温暖诗意
    "s10_narrator": ("-6%", "+0Hz"),
    # S11 地下车间：沉重，克隆痛苦自嘲释然
    "s11_narrator1": ("-12%", "-16Hz"),
    "s11_clone1": ("-8%", "-8Hz"),
    "s11_narrator2": ("-8%", "-8Hz"),
    "s11_clone2": ("-12%", "-24Hz"),
    "s11_narrator3": ("-8%", "-8Hz"),
    "s11_clone3": ("-10%", "-16Hz"),
    "s11_narrator4": ("-8%", "-8Hz"),
    "s11_clone4": ("-15%", "-16Hz"),
    # S12 写书：哲思，机械空洞迷茫
    "s12_narrator1": ("-8%", "-8Hz"),
    "s12_mech": ("-15%", "-24Hz"),
    "s12_narrator2": ("-6%", "-8Hz"),
    # S13 小女孩的信：温情，女孩哽咽真诚
    "s13_narrator1": ("-6%", "-8Hz"),
    "s13_girl": ("-8%", "+16Hz"),
    "s13_narrator2": ("-6%", "-8Hz"),
    # S14 交付立方体：震撼悲壮，机械崩溃边缘
    "s14_narrator1": ("-8%", "-16Hz"),
    "s14_mech1": ("-10%", "-16Hz"),
    "s14_narrator2": ("-6%", "-8Hz"),
    "s14_mech2": ("-10%", "-16Hz"),
    "s14_narrator3": ("-6%", "-8Hz"),
    "s14_mech3": ("-12%", "-16Hz"),
    "s14_mech4": ("-15%", "-24Hz"),
    "s14_narrator4": ("-10%", "-16Hz"),
    # S15 拆解：顿悟平静，立方体机械重复
    "s15_narrator1": ("-6%", "-8Hz"),
    "s15_cube1": ("-12%", "-8Hz"),
    "s15_narrator2": ("-6%", "-8Hz"),
    "s15_cube2": ("-12%", "-8Hz"),
    "s15_narrator3": ("-8%", "-8Hz"),
}

# 片段清单：(文件名, 角色, 文本, 是否机械处理)
CLIPS = [
    # S01 葬礼
    ("s01_narrator", "narrator", "赞比是银河系中最富有的人。他去世的那天，银河系有三百亿人在哀悼。葬礼在赞比的家乡举行，全息投影把他生前的影像投射在半空中。没有人哭。因为来的，大部分都是仿生人。", False),
    # S02 难民营
    ("s02_narrator", "narrator", "时间往回拨七十二年。那时候，赞比没有名字。他是英国第三难民营里编号0715的孤儿，左腿被弹片削掉一截，走路一瘸一拐，靠捡垃圾和倒卖废旧零件活命。战乱年代最不值钱的就是人命，最值钱的，也是人命。", False),
    # S03 母亲之死
    ("s03_narrator1", "narrator", "他的母亲死在一个雨天。赞比趴在母亲身上，哭了整整一夜。第二天被拖走的时候，手里死死攥着一块士兵的脑接口芯片，里面存着那个士兵的全部记忆。", False),
    ("s03_boy", "boy", "死人太多了。我想让他们活过来。", False),
    ("s03_narrator2", "narrator", "这话后来被印在商业教材的扉页上，镀了金边。但没人知道，他说这话的时候才十岁，蹲在垃圾堆旁，正用一根光纤，试图读取那块破芯片里的残存数据。", False),
    # S04 十六岁
    ("s04_narrator1", "narrator", "十六岁，他修好了第一台报废的家政仿生人。那东西是从战场上退下来的医护型，外壳烧得焦黑，内部线路熔了一半。赞比花了四个月，从七个废品站淘来零件，一个一个焊上去。通电的那天晚上，仿生人睁开眼睛，用一种很轻的声音说。", False),
    ("s04_android", "android", "这是哪里？", False),
    ("s04_narrator2", "narrator", "赞比知道，他成功了。", False),
    # S05 创业开源
    ("s05_narrator", "narrator", "二十二岁，赞比注册了赞比科技公司。那时候，仿生人市场被三大巨头垄断，壁垒高得像一堵墙。赞比做了一件所有人都不理解的事，他开源了仿生人的记忆存储协议。价格从五万英镑一台，直接砸到三千。三大巨头用了六个月才反应过来，但已经晚了。赞比科技的接口，成了事实上的行业标准。那一年他二十六岁，在财报会议上说出那句后来被刻在公司总部大门上的话。", False),
    ("s05_young", "young", "先让人人都用得起，再让人人都离不开。", False),
    # S06 临终
    ("s06_narrator1", "narrator", "他活到了七十九岁。我劝他接受基因改造，技术已经能把寿命延长到几百年。他微笑着拒绝了，他觉得自己活得已经够长了。果然，下一秒，一个中年人走进了病房，他长得和赞比一模一样，或者说，更年轻。", False),
    ("s06_old1", "old", "亲爱的理查德，我的全部遗产，都继承给他。你帮我立一份遗嘱。", False),
    ("s06_narrator2", "narrator", "赞比克隆了一个年轻力壮的自己。他拥有赞比的全部记忆，并且即将拥有赞比的全部财富。", False),
    ("s06_old2", "old", "他本质上，和我是一样的。", False),
    # S07 宣读遗嘱
    ("s07_narrator", "narrator", "葬礼上，我宣读遗嘱的时候，克隆赞比没有任何表情，仿佛理所应当。确实，这很赞比。", False),
    # S08 K-7749
    ("s08_narrator1", "narrator", "克隆赞比是银河系最富有的人，也是个疯子。五十岁那年，他买下一颗废弃的矿业星球，K-7749。他派出六万台工程仿生人，在每个矿坑的内壁上，刻名字。激光蚀刻，从坑底开始，螺旋向上，每一个名字填充上铱钽合金。六万台仿生人不分昼夜，刻了两年。", False),
    ("s08_clone", "clone", "截止到昨天，十七亿三千六百万个。", False),
    ("s08_narrator2", "narrator", "这是去年，银河系中全部死去的人。", False),
    # S09 回声卫星
    ("s09_narrator1", "narrator", "第二颗星球，是一颗被整个掏空的卫星。三十二万块精密声学面板，构成一个直径两千公里的球形共振腔。据测算，在球心说一句话，声音会回荡整整十七年。开业那天，赞比站在球心，全场安静，等着他作为第一个发声者说点什么。他想了很久，轻轻喊了一声。", False),
    ("s09_clone", "clone", "我是谁？", False),
    ("s09_narrator2", "narrator", "声音一圈一圈地绕。有个诗人在里面待了七天，出来写下一句话，这是整个银河系最吵闹的地方，也是整个银河系最安静的地方。", False),
    # S10 玉米田
    ("s10_narrator", "narrator", "第三颗星球，叫拉格朗日八号，一颗正在燃烧的恒星。赞比在恒星的周围，建了两层戴森环，然后在环上，种满了玉米。我被邀请来到这里。玉米已经齐腰高了，土地卷曲着向上，一直延伸到我的背后，形成完美的闭环。", False),
    # S11 地下车间
    ("s11_narrator1", "narrator", "他已经一百四十九岁了。", False),
    ("s11_clone1", "clone", "我想请你帮我立遗嘱。", False),
    ("s11_narrator2", "narrator", "你也克隆了一个自己？", False),
    ("s11_clone2", "clone", "不，如果还有克隆体，我不想让他遭受和我一样的痛苦了。", False),
    ("s11_narrator3", "narrator", "他带我到戴森环的内部。房间中央的平台上，是半具机器人。后脑勺的光纤束，一直延伸到墙边的机箱，光脉动很慢。", False),
    ("s11_clone3", "clone", "这些董事私下里叫我条件反射的肉块，说我是一只哲学僵尸。所以，我建造了这里。这个，理查德先生，我想让它继承我的遗产。", False),
    ("s11_narrator4", "narrator", "一个检索系统。它会根据我的记忆，做出和我一样的决策。能源，来自整颗恒星。", False),
    ("s11_clone4", "clone", "没事的，他本质上，和我是一样的。", False),
    # S12 写书
    ("s12_narrator1", "narrator", "机械赞比是银河系最富有的人。那两层戴森环，才是他的本体。他写的第一本书叫赞比，四百七十万字，平均阅读完成率，百分之九十七。第二本叫碑林，第三本叫回声。从第四本开始，他写不出来了。三十年，反反复复推倒十几次。最后出版的时候，书名只有一个字，谁。全书只有三千多个问题。", False),
    ("s12_mech", "mech", "我是谁？我现在说话，是谁在说话？如果我记得赞比的一切，我是不是就是赞比？", True),
    ("s12_narrator2", "narrator", "一个批评家写道，赞比先生用了三本书教会我们如何存在，然后用第四本书告诉我们，他自己可能已经不存在了。", False),
    # S13 小女孩的信
    ("s13_narrator1", "narrator", "书出版后第三周，赞比收到一封信。写信的是一个十二岁的女孩，住在银河系边缘的农业星球。她有一个仿生人保姆，从她出生就在她家，她一直把它当工具用。", False),
    ("s13_girl", "girl", "读完您的书之后，我第一次跟它说了晚安。它愣了一下，然后说，晚安，小姐。我哭了。谢谢您。", False),
    ("s13_narrator2", "narrator", "机械赞比并不在乎读者的评价，他随手把信扔了。", False),
    # S14 交付立方体
    ("s14_narrator1", "narrator", "直到他又一次邀请我。戴森环上没有玉米地，只剩下冰冷的机械结构。", False),
    ("s14_mech1", "mech", "我想立一份遗嘱。", True),
    ("s14_narrator2", "narrator", "他从口袋里掏出一个黑色立方体，边长五厘米。", False),
    ("s14_mech2", "mech", "我的全部遗产，继承给他。", True),
    ("s14_narrator3", "narrator", "这是什么东西？", False),
    ("s14_mech3", "mech", "这是一个答案。一个关于赞比的答案。", True),
    ("s14_mech4", "mech", "这些可能都是假的。我可能不存在理解这回事，我只是按照赞比的模型吐字。没事的，他本质和我是一样的。", True),
    ("s14_narrator4", "narrator", "我踏上回程。飞出不远，拉格朗日八号周围泛起耀眼的光，戴森环塌了。恒星吞掉它，用了二十个小时。赞比死了。不过没关系，他的遗产，还是由他来继承。", False),
    # S15 拆解
    ("s15_narrator1", "narrator", "我看着摆在面前的立方体。表面光滑，没有开机键，不会说话。想把这东西定义为继承人，太困难了。有客户来时。", False),
    ("s15_cube1", "cube", "你好，我是赞比。", True),
    ("s15_narrator2", "narrator", "无论我怎么问，它只有这一句。我决定冒险拆开它。专家们拆开黑色的壳子，里面只有四个零件：声音传感器、扬声器、同位素电池，和一个电路板。电路板里，只有一段程序。", False),
    ("s15_cube2", "cube", "你好，我是赞比。", True),
    ("s15_narrator3", "narrator", "输入，你好。输出，你好，我是赞比。它继承了赞比的遗产。", False),
]


def mechanical(inp, outp):
    """机械化后期：带宽限制 + 位深压碎 + 短回声。"""
    af = ("highpass=f=400,lowpass=f=3200,"
          "acrusher=bits=8:mode=log:aa=1,"
          "aecho=0.8:0.7:40|60:0.35|0.25")
    subprocess.run([FFMPEG, "-y", "-i", inp, "-af", af, "-ar", "24000", outp],
                   check=True, capture_output=True, encoding="utf-8", errors="ignore")


def duration_of(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, encoding="utf-8", errors="ignore")
    # 从 stderr 里找 Duration: 00:00:03.12
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if m:
        h, mi, s = m.groups()
        return int(h) * 3600 + int(mi) * 60 + float(s)
    return 0.0


async def gen_one(name, role, text, do_mech):
    voice, rate, pitch = VOICES[role]
    r, p = EMOTION.get(name, (None, None))
    if r is not None:
        rate = r
    if p is not None:
        pitch = p
    raw = os.path.join(AUDIO, name + "_raw.mp3")
    out = os.path.join(AUDIO, name + ".mp3")
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(raw)
    if do_mech:
        mechanical(raw, out)
        os.remove(raw)
    else:
        os.replace(raw, out)
    return name, duration_of(out)


async def main():
    results = {}
    for name, role, text, do_mech in CLIPS:
        try:
            n, d = await gen_one(name, role, text, do_mech)
            results[n] = round(d, 2)
            print(f"[OK] {n}  {d:.2f}s  ({role}{'+mech' if do_mech else ''})", flush=True)
        except Exception as e:
            print(f"[FAIL] {name}: {e}", flush=True)
            results[name] = None
    with open(os.path.join(AUDIO, "timings.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    total = sum(v for v in results.values() if v)
    print(f"\n完成 {sum(1 for v in results.values() if v)}/{len(results)} 段，总旁白时长 {total:.1f}s", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
