#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_style.py · 风格指纹分析（只依赖标准库；除 --emit-profile 外不写任何文件）

用途：把"像不像某种风格"从主观判断变成可重复的**数字**。
    · 贴一段参照样本（1–2 千字）→ 反推 8 轴指纹
    · 分析已有书稿 → 看当前实际风格
    · 与原型目标（tools/data/style-archetypes.json）对比 → 报偏差
    · 生成 `主题/风格档.md` 草稿

用法：
    python3 .cursor/tools/analyze_style.py --sample 参照样本.md
    python3 .cursor/tools/analyze_style.py --manuscript            # 分析 章节/
    python3 .cursor/tools/analyze_style.py --sample x.md --proto cold-minimal
    python3 .cursor/tools/analyze_style.py --sample x.md --emit-profile
    python3 .cursor/tools/analyze_style.py --list-proto

⚠️ 诚实边界：本工具只算**可机械测量**的轴。叙述者态度、留白程度、时间线类型等
   只能给启发式提示，最终仍需人工判定——它们在报告里标注为「人工」。
   术语密度（jargon）与第一人称占比为**代理指标**，置信度低，已在报告中注明。
退出码：0 成功；1 无可分析文本；2 参数错误。
"""

import argparse
import json
import os
import re
import statistics
import sys
from datetime import date

# ── 词表（跨项目通用；项目特化词请写 主题/通用约束.md §3）────────────────
SENSES = {
    "触觉/体感": "冷 热 痛 痒 麻 湿 干 硬 软 烫 凉 寒 暖 硌 黏 滑 钝 胀 酸 重",
    "听觉": "响 声 静 噪 嗡 轰 吱 嘎 哗 咚咚 砰 嗒 嘶 鸣 沉寂 寂静",
    "嗅觉": "香 臭 腥 霉 焦 馊 甜腻 烟味 汗味 土腥",
    "味觉": "甜 苦 涩 咸 酸 鲜 辣 淡 腻 涩口",
    "视觉": "光 色 亮 暗 影 白 黑 红 黄 蓝 灰 青 金 银",
}
SENSE_WORDS = {k: [w for w in v.split() if w] for k, v in SENSES.items()}

SIMILE_PAT = re.compile("|".join(sorted(
    ["仿佛", "宛如", "犹如", "如同", "好像", "好似", "好比", "似的", "像"],
    key=len, reverse=True)))
PSYCH = ["想", "感到", "觉得", "心里", "心中", "意识到", "明白", "记得", "知道",
         "害怕", "难过", "高兴", "痛恨", "期待", "犹豫", "后悔", "愧疚", "惦记", "琢磨"]
EXTERNAL = ["攥", "咬", "抖", "颤", "转身", "低头", "抬眼", "握", "后退", "缩",
            "脸色", "手指", "喉结", "肩膀", "脚步", "呼吸", "脊背", "额角"]
TIME_WORDS = ["十年前", "三年前", "那天", "当天", "夜里", "次日", "翌日", "当年",
              "那时", "后来", "过后", "第二日", "半晌", "黄昏", "黎明", "清晨",
              "傍晚", "入夜", "早上", "昨天", "明天", "上周", "上个月"]
EXPLAIN = ["因为", "所以", "原来", "其实", "也就是", "就是说", "因此", "于是",
           "毕竟", "可见", "难怪", "结果", "总之"]
COLLOQUIAL = ["事儿", "点儿", "玩儿", "差不多", "压根", "得嘞", "咋", "啥", "甭",
              "吧", "呢", "嘛", "呗", "呀", "啊", "哦", "诶", "嘿", "咯"]
ESSAY = ["其实", "本来", "终究", "无非", "不过是", "总是", "从来", "所谓", "显然",
         "当然", "毕竟", "可见", "或许", "大抵", "大约"]
META = ["档案", "手稿", "注释", "引文", "记载", "译者", "编者", "书中", "附录", "注脚", "批注"]
QUOTE_MARKS = "「」“”‘’\"'「」"
# 破折号 / 省略号按「标记串」计数，不按字符计数（"——" 算 1 次，不是 2 次）
DASH_PAT = re.compile(r"[—－]+")
ELLIPSIS_PAT = re.compile(r"[…]+|\.{3,}")
# 中文术语的构词后缀启发式（纯中文文本里拉丁字母串为 0，需要它兜底）。
# 只用**特征性强的多字词**，避免「度/性/子/层」这类高频字把普通叙述算成术语。
JARGON_SUFFIX_PAT = re.compile(
    r"[\u4e00-\u9fff]{2,6}(?:系统|协议|常数|方程|模型|矩阵|算法|定律|效应|波段|引擎|"
    r"机制|阈值|参数|指数|系数|层级|力场|曲率|熵|公理|定理|悖论|异构|拓扑|"
    r"舱|塔|站|舰队|纪元|纪年)")
JARGON_LATIN_PAT = re.compile(r"[A-Za-z]{2,}")

AXIS_LABEL = {
    "avg_sentence_len": "平均句长", "sentence_len_sd": "句长标准差",
    "comma_per_kchar": "逗号密度", "dash_per_kchar": "破折号密度",
    "avg_para_len": "平均段长", "simile_per_100": "比喻密度",
    "synesthesia_ratio": "通感句占比", "psych_ratio": "心理句占比",
    "internal_external": "内耗:外化", "dialogue_ratio": "对话句占比",
    "exclaim_per_kchar": "感叹号密度", "explicit_time_per_kchar": "显性时间密度",
    "first_person_ratio": "第一人称句占比", "essay_ratio": "议论句占比",
    "explain_per_kchar": "解释连接词密度", "ellipsis_per_kchar": "省略号密度",
    "colloquial_per_kchar": "口语标记密度", "jargon_per_kchar": "术语密度(代理)",
    "meta_per_kchar": "元叙事标记密度",
}


def cjk(t):
    return len(re.findall(r"[\u4e00-\u9fff]", t))


def strip_work(text):
    """去掉视角标记行与合法收束标题，避免污染统计。"""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^>\s*【视角", s) or re.match(r"^##\s*(本节完|本章完)\s*$", s):
            continue
        out.append(line)
    return "\n".join(out)


def sentences(text):
    """按中文句末标点切句；丢弃结构行与过短残片。"""
    body = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s[0] in "#>|":
            continue
        body.append(s)
    raw = re.split(r"(?<=[。！？!?])", "".join(body))
    out = []
    for p in raw:
        p = p.strip()
        if cjk(p) >= 2:
            out.append(p)
    return out


def per_k(count, chars, k=1000):
    return round(count / (chars / k), 2) if chars else 0.0


def per_100(count, chars):
    return round(count / (chars / 100), 2) if chars else 0.0


def count_any(text, words):
    return sum(text.count(w) for w in words)


def analyze(text):
    text = strip_work(text)
    chars = cjk(text)
    sents = sentences(text)
    paras = [p for p in re.split(r"\n\s*\n", text) if cjk(p) >= 2]
    n_sent = max(1, len(sents))

    lens = [cjk(s) for s in sents]
    m = {
        "chars": chars, "sentences": n_sent, "paragraphs": max(1, len(paras)),
        "avg_sentence_len": round(statistics.mean(lens), 1) if lens else 0,
        "sentence_len_sd": round(statistics.pstdev(lens), 1) if len(lens) > 1 else 0,
        "comma_per_kchar": per_k(text.count("，") + text.count(","), chars),
        "dash_per_kchar": per_k(len(DASH_PAT.findall(text)), chars),
        "avg_para_len": round(chars / max(1, len(paras)), 1),
        "simile_per_100": per_100(len(SIMILE_PAT.findall(text)), chars),
        "exclaim_per_kchar": per_k(text.count("！") + text.count("!"), chars),
        "ellipsis_per_kchar": per_k(len(ELLIPSIS_PAT.findall(text)), chars),
        "explicit_time_per_kchar": per_k(
            count_any(text, TIME_WORDS) + len(re.findall(r"\d+\s*(?:年|月|日|天|小时)", text)), chars),
        "explain_per_kchar": per_k(count_any(text, EXPLAIN), chars),
        "colloquial_per_kchar": per_k(count_any(text, COLLOQUIAL), chars),
        "meta_per_kchar": per_k(count_any(text, META), chars),
        "jargon_per_kchar": per_k(len(JARGON_LATIN_PAT.findall(text))
                                     + len(JARGON_SUFFIX_PAT.findall(text)), chars),
    }

    # 通感：同句 ≥2 个不同感官通道
    syn = 0
    sense_hits = {k: 0 for k in SENSE_WORDS}
    for s in sents:
        ch = [k for k, ws in SENSE_WORDS.items() if any(w in s for w in ws)]
        for k in ch:
            sense_hits[k] += 1
        if len(ch) >= 2:
            syn += 1
    m["synesthesia_ratio"] = round(syn / n_sent * 100, 1)
    m["sense_distribution"] = {k: round(v / n_sent * 100, 1) for k, v in sense_hits.items()}
    top_sense = sorted(sense_hits.items(), key=lambda kv: -kv[1])
    m["sense_priority"] = top_sense[0][0] if top_sense and top_sense[0][1] else "（样本过短）"

    # 对话句：含引号
    dlg = [s for s in sents if any(q in s for q in "「」“”\"")]
    m["dialogue_ratio"] = round(len(dlg) / n_sent * 100, 1)
    non_dlg = [s for s in sents if s not in dlg]

    # 心理 / 外化
    psych = [s for s in sents if count_any(s, PSYCH)]
    ext = [s for s in sents if count_any(s, EXTERNAL)]
    m["psych_ratio"] = round(len(psych) / n_sent * 100, 1)
    # 无外化样本时不编造比值（0 会被误读成"完全内化"）
    m["internal_external"] = round(len(psych) / len(ext), 2) if ext else None

    # 第一人称（排除对话，降低噪声）
    fp = [s for s in non_dlg if "我" in s]
    m["first_person_ratio"] = round(len(fp) / max(1, len(non_dlg)) * 100, 1)

    # 议论句
    essay = [s for s in non_dlg if count_any(s, ESSAY)]
    m["essay_ratio"] = round(len(essay) / n_sent * 100, 1)

    return m


def compare(m, targets):
    rows = []
    for key, tgt in targets.items():
        if key not in m:
            continue
        val = m[key]
        if val is None:
            continue              # 无法测量（如无外化样本）→ 不比对
        if not isinstance(tgt, list) or len(tgt) != 2:
            rows.append((key, val, tgt, "—"))
            continue
        lo, hi = tgt
        if val < lo:
            verdict = "↓ 偏低"
        elif val > hi:
            verdict = "↑ 偏高"
        else:
            verdict = "✓ 区间内"
        rows.append((key, val, f"{lo}–{hi}", verdict))
    return rows


def load_archetypes():
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, "data", "style-archetypes.json")
    with open(p, encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"✗ {p} 不是合法 JSON：{exc}", file=sys.stderr)
            sys.exit(2)


def collect_manuscript(root):
    base = os.path.join(root, "章节")
    buf = []
    if not os.path.isdir(base):
        return ""
    for dp, _dn, fns in os.walk(base):
        for fn in sorted(fns):
            if fn.endswith(".md"):
                buf.append(open(os.path.join(dp, fn), encoding="utf-8").read())
    return "\n\n".join(buf)


def render_report(m, title):
    out = [f"风格指纹 · {title}", ""]
    out.append(f"样本规模：{m['chars']} 汉字 · {m['sentences']} 句 · {m['paragraphs']} 段")
    out.append("")
    out.append("| 轴 | 指标 | 值 |")
    out.append("|---|---|---|")
    for k in ("avg_sentence_len", "sentence_len_sd", "comma_per_kchar", "dash_per_kchar",
              "avg_para_len", "simile_per_100", "synesthesia_ratio", "psych_ratio",
              "internal_external", "dialogue_ratio", "exclaim_per_kchar",
              "explicit_time_per_kchar", "first_person_ratio", "essay_ratio",
              "explain_per_kchar", "ellipsis_per_kchar", "colloquial_per_kchar",
              "jargon_per_kchar", "meta_per_kchar"):
        if k in m:
            out.append(f"| {AXIS_LABEL.get(k, k)} | `{k}` | {m[k] if m[k] is not None else chr(8212)} |")
    out.append(f"| 感官优先 | `sense_priority` | {m['sense_priority']} |")
    out.append("")
    dist = " · ".join(f"{k} {v}%" for k, v in sorted(m["sense_distribution"].items(),
                                                     key=lambda kv: -kv[1]))
    out.append(f"感官分布（句占比）：{dist}")
    out.append("")
    out.append("**需人工判定（工具不给假数字）**：叙述者态度（同情/反讽/冷峻）· 留白程度 ·")
    out.append("时间线类型（顺叙/倒叙/多线/非线性）· 词汇具象抽象比（需分词器）· 专属意象集。")
    out.append(f"留白提示：解释性连接词 {m['explain_per_kchar']}/千字（越低留白越多）")
    out.append(f"术语密度为**代理指标**（拉丁字母串），第一人称占比已排除对话句。")
    return "\n".join(out)


PROFILE_BEGIN = "<!-- STYLE-METRICS:BEGIN -->"
PROFILE_END = "<!-- STYLE-METRICS:END -->"


def metrics_block(m, proto_code, proto_authors):
    lines = [PROFILE_BEGIN, ""]
    lines.append(f"> 由 `tools/analyze_style.py` 生成 · {date.today().isoformat()}"
                 f" · 参照样本 {m['chars']} 汉字" + (f" · 原型 {proto_code}" if proto_code else ""))
    lines.append("")
    lines.append("| 轴 | 指标 | **本项目目标** | 参照样本实测 |")
    lines.append("|---|---|---|---|")
    for k in ("avg_sentence_len", "sentence_len_sd", "comma_per_kchar", "dash_per_kchar",
              "avg_para_len", "simile_per_100", "synesthesia_ratio", "psych_ratio",
              "internal_external", "dialogue_ratio", "exclaim_per_kchar",
              "explicit_time_per_kchar", "first_person_ratio", "essay_ratio",
              "explain_per_kchar", "ellipsis_per_kchar", "colloquial_per_kchar",
              "jargon_per_kchar", "meta_per_kchar"):
        if k in m:
            lines.append(f"| {AXIS_LABEL.get(k, k)} | `{k}` | （待定） | {m[k]} |")
    lines.append(f"| 感官优先 | `sense_priority` | （待定） | {m['sense_priority']} |")
    lines.append("")
    if proto_code:
        lines.append(f"> 原型 **{proto_code}**（{proto_authors}）的区间见 "
                     f"`tools/data/style-archetypes.json`；把本表「本项目目标」按它填定，"
                     f"或按你的样本数值自定。")
        lines.append("")
    lines.append(PROFILE_END)
    return "\n".join(lines)


def emit_profile(root, m, proto, template_path):
    tpl_path = os.path.join(root, "主题", "风格档.md")
    if not os.path.isfile(tpl_path):
        tpl_path = template_path
    if not os.path.isfile(tpl_path):
        print("✗ 找不到模板 templates/style-profile.md", file=sys.stderr)
        return None
    text = open(tpl_path, encoding="utf-8").read()
    code = proto["code"] if proto else ""
    authors = " / ".join(proto["authors"]) if proto else ""
    block = metrics_block(m, code, authors)
    if PROFILE_BEGIN in text and PROFILE_END in text:
        text = re.sub(re.escape(PROFILE_BEGIN) + r".*?" + re.escape(PROFILE_END),
                      block, text, flags=re.S)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    if proto:
        text = text.replace("<主原型代号>", f"{code}（{' / '.join(proto['authors'])}）", 1)
    dest = os.path.join(root, "主题", "风格档.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text)
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--sample", nargs="*", default=None, help="参照样本文件（可多个）")
    ap.add_argument("--manuscript", action="store_true", help="分析 章节/ 全部正文")
    ap.add_argument("--proto", default=None, help="与某原型对比（见 --list-proto）")
    ap.add_argument("--list-proto", action="store_true")
    ap.add_argument("--emit-profile", action="store_true", help="生成 主题/风格档.md 草稿")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    root = args.root or os.path.dirname(os.path.dirname(here))
    data = load_archetypes()

    if args.list_proto:
        print("可用风格原型（括号内为代表作家，数值见 tools/data/style-archetypes.json）：")
        for pid, a in data["archetypes"].items():
            print(f"  {pid:<24} {a['code']}（{' / '.join(a['authors'])}）")
            print(f"       {a['signature']}")
        return 0

    text = ""
    title = ""
    if args.sample:
        parts = []
        for p in args.sample:
            fp = p if os.path.isabs(p) else os.path.join(root, p)
            if not os.path.isfile(fp):
                print(f"✗ 样本不存在：{p}", file=sys.stderr)
                return 2
            parts.append(open(fp, encoding="utf-8").read())
        text = "\n\n".join(parts)
        title = " / ".join(os.path.basename(p) for p in args.sample)
    elif args.manuscript:
        text = collect_manuscript(root)
        title = "章节/ 全部正文"
    if not text.strip():
        print("✗ 无文本可分析。用 --sample <文件> 或 --manuscript（且 章节/ 非空）", file=sys.stderr)
        return 1

    m = analyze(text)
    if m["chars"] < 500:
        print(f"⚠ 样本偏小（{m['chars']} 汉字）——平均句长等指标波动大，建议 ≥1500 汉字。",
              file=sys.stderr)
        if not args.json:
            print()

    proto = None
    if args.proto:
        proto = data["archetypes"].get(args.proto)
        if not proto:
            print(f"✗ 未知原型：{args.proto}（--list-proto 查看）", file=sys.stderr)
            return 2

    if args.json:
        print(json.dumps({"title": title, "metrics": m,
                          "proto": args.proto,
                          "compare": compare(m, proto["targets"]) if proto else None},
                         ensure_ascii=False, indent=2))
        return 0

    print(render_report(m, title))
    if proto:
        print(f"\n对比原型 **{proto['code']}**（{' / '.join(proto['authors'])}）：")
        print("\n| 指标 | 实测 | 原型区间 | 判定 |")
        print("|---|---|---|---|")
        for key, val, tgt, verdict in compare(m, proto["targets"]):
            print(f"| {AXIS_LABEL.get(key, key)} | {val} | {tgt} | {verdict} |")

    if args.emit_profile:
        dest = emit_profile(root, m, proto, os.path.join(here, "..", "templates", "style-profile.md"))
        if dest:
            print(f"\n✓ 已生成风格档草稿：{os.path.relpath(dest, root)}")
            print("  下一步：把「本项目目标」列按原型区间或你的判断填定，并在 §合法偏离 写明豁免理由。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
