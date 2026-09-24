#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_manuscript.py · 正文机械校验（写作侧，只读，不改稿）

用途：把「加粗密度 / 链式句 / 长句 / `##` 标题 / 作者元叙事 / AI 套词 / 标点 / 元数据残留 / 敏感词」
从"AI 目测"变成"可重复执行的机械检查"。只依赖 Python 3 标准库，只读不写。

用法：
    python3 .cursor/tools/check_manuscript.py                    # 扫 章节/ 全部
    python3 .cursor/tools/check_manuscript.py 章节/第03章_x       # 扫指定文件/目录
    python3 .cursor/tools/check_manuscript.py --json             # 机器可读输出
    python3 .cursor/tools/check_manuscript.py --quiet            # 只输出 🔴
    python3 .cursor/tools/check_manuscript.py --words            # 只看字数汇总

阈值来源（优先级）：
    1) 项目 `主题/通用约束.md`（表内数值）
    2) 母版默认（`rules/01-novel-language.mdc` / `templates/constraints.md`）
敏感词来源（任一存在即生效）：
    1) 项目 `主题/敏感词表.md`（每行一词，# 开头为注释）
    2) `.cursor/tools/data/sensitive-words.example.txt`

退出码：0 = 无 🔴；1 = 存在 🔴；2 = 用法/参数错误。
本工具**只报告**，不会修改任何正文；报告不入 `章节/`。
"""

import argparse
import json
import os
import re
import sys

# ── 默认阈值（母版口径）──────────────────────────────────────────────────
DEFAULTS = {
    "unit_chars": "cjk",      # 字数单位：cjk = 汉字数
    "sec_target_min": 2000,
    "sec_target_max": 5000,
    "sec_hard_max": 5000,
    "chap_min": 30000,
    "chap_max": 60000,
    "bold_warn": 60.0,        # 加粗密度 🟡
    "bold_fail": 130.0,       # 加粗密度 🔴
    "long_sentence": 30,      # 单句 > 30 字 → 长句
    "short_sentence": 8,      # 连续短句判定阈值
    "short_run": 4,           # 连续 N 句及以上 → 报
    # 标点每章上限（公开去 AI 味阈值：deai ≤2/千字 · inkflow ≤4/章）
    "dash_max": 4,            # 破折号
    "ellipsis_max": 3,        # 省略号
    "exclaim_max": 5,         # 感叹号
}

LEGAL_H2 = ("本节完", "本章完")

# 分镜 / 电影术语（`05-novel-style.mdc` §二）
FILMIC = ["镜头", "全景", "特写", "拉远", "切换到", "画面", "打点", "分镜", "场景切换"]
# 作者元叙事（`.cursor/skills/novel-plan/reference/universal-gates.md` §8）
META_NARRATION = [
    r"第\s*[0-9一二三四五六七八九十百千]+\s*章", r"第\s*[0-9一二三四五六七八九十百千]+\s*节",
    r"上一章", r"前一章", r"下一章",
    r"前文", r"后文", r"后续", r"本章节", r"本节讲",
]
# AI 套词（`01-novel-language.mdc` + `novel-line-scanner` 维度 1/2）
# 硬套词：任何位置命中都算（这些是模板化表述，正常行文不需要）
AI_PHRASES_ANYWHERE = [
    "眼中闪过", "嘴角勾起", "空气中弥漫", "时间凝固", "时间仿佛凝固",
    "心中涌起", "眼神变得复杂", "那一刻，他意识到", "那一刻，她意识到",
    "不由自主", "不由得", "不禁",
    # 取自公开去 AI 味规则的具体套词（zenstory / XINGANLIU 的禁词表）
    "涌上心头", "嘴角微微", "嘴角上扬", "一股",
]

# 成对/结构型套式（正则）——单看某个词没问题，成对出现才是模板腔
PATTERN_RULES = [
    (r"不是[^，。；\n]{1,20}[，,]\s*而是", "「不是X，而是Y」对偶套式"),
    (r"没有[^，。；\n]{1,12}[，,]\s*没有", "否定排比（没有…，没有…）"),
    (r"声音[^，。；\n]{0,8}[，,]\s*却", "「声音不大，却…」反转套式"),
]
# 弱化副词/套词密度：合计超阈值即报（不禁止单个词，只禁止堆叠）
SOFT_TIC_WORDS = ["仿佛", "一丝", "缓缓", "微微", "轻轻", "淡淡"]
SOFT_TIC_PER_KCHAR = 3.0
# 引导词 / 弱化句式：**仅句首或分句首**命中才算
# （`01-novel-language.mdc` §二 禁的是"以仿佛/似乎**开头**的弱化句式"，不是禁止这些词本身）
AI_PHRASES_LEADING = ["然而", "不仅", "事实上", "某种意义上", "本质上", "仿佛", "似乎"]
# 正文中不允许出现的元数据/过程件痕迹
ARTIFACT = ["八股检测报告", "**原**", "批注", "复盘", "修改清单", "TODO", "FIXME", "待补"]

# 句首判定：行首或紧跟句末标点/对话引号之后
LEADING_RE_CACHE = {}


def leading_hits(text, phrase):
    """返回 phrase 在句首/分句首出现的次数。"""
    pat = LEADING_RE_CACHE.get(phrase)
    if pat is None:
        pat = re.compile(r"(?:^|[\n。！？；：…”」』])[\s>*\-]*" + re.escape(phrase))
        LEADING_RE_CACHE[phrase] = pat
    return len(pat.findall(text))


def load_project_blacklist(text):
    """读 `主题/通用约束.md` §3.2 套词黑名单（到下一个 ## 标题为止）。"""
    words = []
    m = re.search(r"^###\s*3\.2[^\n]*$", text, re.M)
    if not m:
        return words
    rest = text[m.end():]
    end = re.search(r"^#{2,3}\s", rest, re.M)
    block = rest[:end.start()] if end else rest
    for line in block.splitlines():
        s = line.strip()
        if not s or s.startswith(">") or s.startswith("|"):
            continue
        s = s.lstrip("-* ").strip()
        s = s.strip("`")
        if s and not s.startswith("<") and len(s) < 40:
            words.append(s)
    return words


def cjk_count(text):
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def visible_count(text):
    """非空白字符数（去除 Markdown 结构符号后用于密度分母）。"""
    t = re.sub(r"[\s]", "", text)
    return len(t)


def strip_code(text):
    """去掉围栏代码块与行内代码，避免误判标点/黑名单。"""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def strip_markup(text):
    """把加粗/斜体标记替换为占位，保留字符数便于句子分析。"""
    return text


def split_sentences(text):
    """按中文句末标点与换行切句；保留非空句。"""
    parts = re.split(r"[。！？；…\n]+", text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.startswith("#") or p.startswith(">") or p.startswith("|") or p.startswith("-"):
            # 结构行不计入"句子"统计，但仍会做黑名单检查
            continue
        out.append(p)
    return out


def find_cfg_text(root):
    for rel in ("主题/通用约束.md", "主题/_meta/通用约束.md"):
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            return p, open(p, encoding="utf-8").read()
    return None, ""


# 颗粒度档预设（`主题/通用约束.md` §1.1）——档位决定「章」的含义，进而决定字数窗
GRANULARITY = {
    "A": {"chap_min": 2000, "chap_max": 4000,
          "sec_target_min": 1500, "sec_target_max": 4000, "sec_hard_max": 4000},
    "B": {"chap_min": 6000, "chap_max": 12000,
          "sec_target_min": 2000, "sec_target_max": 4000, "sec_hard_max": 5000},
    "C": {"chap_min": 30000, "chap_max": 60000,
          "sec_target_min": 2000, "sec_target_max": 5000, "sec_hard_max": 5000},
}


def apply_constraints(cfg, text):
    """从 `主题/通用约束.md` 的表内数值覆盖默认阈值（宽松解析）。"""
    if not text:
        return cfg
    # 颗粒度档（A 网文 / B 出版 / C 大章）→ 先套预设，再让显式数值覆盖
    m = re.search(r"颗粒度档[^\n|]*\|\s*\**\s*([ABC])", text)
    if m:
        cfg.update(GRANULARITY[m.group(1)])
        cfg["granularity"] = m.group(1)
    m = re.search(r"单节目标字数[^\n]*?(\d+)\s*[–\-~至]\s*(\d+)", text)
    if m:
        cfg["sec_target_min"], cfg["sec_target_max"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"单节硬上限[^\n]*?(\d+)", text)
    if m:
        cfg["sec_hard_max"] = int(m.group(1))
    m = re.search(r"单章字数窗[^\n]*?(\d+)\s*[–\-~至]\s*(\d+)", text)
    if m:
        cfg["chap_min"], cfg["chap_max"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"单章节数窗[^\n]*?(\d+)\s*[–\-~至]\s*(\d+)", text)
    if m:
        cfg["sec_per_chap_min"], cfg["sec_per_chap_max"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"加粗密度[^\n]*?>?\s*(\d+)\s*/\s*100", text)
    if m:
        cfg["bold_fail"] = float(m.group(1))
    m = re.search(r"(\d+)\s*[–\-~]\s*(\d+)\s*/\s*100\s*字[^\n]*(?:偏高|🟡)", text)
    if m:
        cfg["bold_warn"] = float(m.group(2))
    return cfg


def load_style_profile(root):
    """读 `主题/风格档.md`：返回 (targets, exempt_keys)。targets[key]=目标原文。"""
    targets, exempt = {}, set()
    for rel in ("主题/风格档.md",):
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            continue
        text = open(p, encoding="utf-8").read()
        # 指标表：`| 名称 | \`key\` | 目标 | 实测 |`
        # 宽容解析：key 可在任意单元格（优先「指标」列）；目标可带单位/百分号/各种破折号。
        for line in text.splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            if cells[0].startswith(SKIP_CELL0) or "<" in line or ">" in line:
                continue                      # 表头 / 示例行 / 占位行
            key, ki = None, None
            for i, c in enumerate(cells):
                m = re.search(r"`([a-z0-9_]{3,})`", c.replace("*", ""))
                if m and m.group(1) in (AXIS_KEYS | TEXT_AXES):
                    key, ki = m.group(1), i
                    break
            if not key:
                continue
            tgt_cell = cells[ki + 1] if ki + 1 < len(cells) else ""
            raw = re.sub(r"\*|`", "", tgt_cell).strip()
            if raw and raw not in ("（待定）", "待定", "-", ""):
                targets[key] = raw          # 原样保留，比对时再解析
        # 豁免表：**只认「涉及指标」列（末列）** 里的指标名。
        # 不扫整行——否则备注/理由里提到指标名会造成静默豁免。
        for line in text.splitlines():
            if not line.strip().startswith("|"):
                continue
            if "§" not in line and "豁免" not in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            if cells[0].startswith(("例", "（")) or "<" in line or ">" in line:
                continue
            for key in re.findall(r"`([a-z_]{3,})`", cells[-1]):
                if key in AXIS_KEYS:
                    exempt.add(key)
    return targets, exempt


# 指标表行的首列跳过词（表头/示例/占位）
SKIP_CELL0 = ("例", "（", "指标", "名称", "轴", "项")
# 区间写法：兼容 – — ~ ～ - 与「至/到」，数字可带小数
RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[–—~～\-至到]\s*(\d+(?:\.\d+)?)")


def parse_target(raw):
    """'10–16' / '10—16 字' / '5%–12%' / '约 12 字' / '2.5~6.0' → (lo, hi)。

    宽容：剥离单位与百分号、接受 – — ~ ～ - 至 到；只取前两个数。
    """
    s = str(raw)
    m = RANGE_RE.search(s)
    if m:
        return float(m.group(1)), float(m.group(2))
    nums = re.findall(r"\d+(?:\.\d+)?", s)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    if len(nums) == 1:
        v = float(nums[0])
        return v, v
    return None


AXIS_KEYS = {
    "avg_sentence_len", "sentence_len_sd", "comma_per_kchar", "dash_per_kchar",
    "avg_para_len", "simile_per_100", "synesthesia_ratio", "psych_ratio",
    "internal_external", "dialogue_ratio", "exclaim_per_kchar",
    "explicit_time_per_kchar", "first_person_ratio", "essay_ratio",
    "explain_per_kchar", "ellipsis_per_kchar", "colloquial_per_kchar",
    "jargon_per_kchar", "meta_per_kchar",
}
# 非数值型指标（按字符串相符判定，不参与区间比对）
TEXT_AXES = {"sense_priority"}


def style_compare(files, root, cfg, quiet=False):
    """用 analyze_style 的同一套指标算全书/逐文件风格指纹，并与风格档目标对比。

    返回 (失败项数, 结果字典)。**解析不到目标值时视为失败**——否则风格档写错格式
    会让闸门静默放行（"0 项目标 = 通过"是把绿灯泡装在坏电路上）。
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import analyze_style as ast
    except ImportError as exc:
        print(f"⚠ 无法加载 analyze_style.py，跳过 --style：{exc}", file=sys.stderr)
        return 0, {"skipped": str(exc)}
    targets, exempt = load_style_profile(root)
    if not targets:
        print("🔴 `主题/风格档.md` 未解析到任何可用目标值 —— 风格闸门**无法生效**，按失败计。", file=sys.stderr)
        print("   检查 §二 指标表：格式须为 `| 名称 | \\`key\\` | 目标 | 实测 |`，目标如 `10–16`、`30–48`、`2.5–6`。",
              file=sys.stderr)
        print("   或先跑：python3 .cursor/tools/analyze_style.py --sample <样本> --emit-profile", file=sys.stderr)
        return 1, {"error": "no_targets_parsed"}

    text = "\n\n".join(safe_read(f)[0] for f in files)
    m = ast.analyze(text)
    rows, bad, checked = [], 0, 0
    for key, raw in targets.items():
        if key not in m:
            continue
        if key in TEXT_AXES:
            ok = str(raw) == str(m[key])
            rows.append((key, m[key], raw, "✅" if ok else "🔴 与目标不符"))
            checked += 1
            bad += 0 if ok else 1
            continue
        lo_hi = parse_target(raw)
        if not lo_hi:
            rows.append((key, m.get(key), raw, "🟡 目标无法解析"))
            continue
        checked += 1
        lo, hi = lo_hi
        val = float(m[key])
        tol = max(0.5, abs(hi - lo) * 0.05)      # 容差：避免边界抖动刷屏
        if val < lo - tol or val > hi + tol:
            if key in exempt:
                verdict = "🟡 已声明豁免"
            else:
                verdict = "🔴 未声明偏离"
                bad += 1
        else:
            verdict = "✅"
        rows.append((key, m[key], raw, verdict))
    if not quiet:
        print(f"\n风格比对 · {m['chars']} 汉字 · 依据 `主题/风格档.md`（{len(targets)} 项目标，"
              f"{len(exempt)} 项已声明豁免）")
        print("| 指标 | 实际 | 目标 | 判定 |")
        print("|---|---|---|---|")
        for key, val, raw, verdict in rows:
            print(f"| {key} | {val} | {raw} | {verdict} |")
        print(f"\n{'✓ 风格一致' if not bad else f'✗ {bad} 项未声明偏离'}"
              f"（已比对 {checked} 项；未列出的指标为工具无法测量的轴）")
        if bad:
            print("提示：要么改文回到目标区间，要么在 `主题/风格档.md` §三 显式声明豁免"
                  "（写明豁免哪条规则/幅度/理由/涉及指标）。")
    return bad, {"targets": len(targets), "exempt": sorted(exempt), "checked": checked,
                 "rows": [{"metric": k, "actual": v, "target": r, "verdict": d} for k, v, r, d in rows],
                 "failed": bad}


def load_sensitive_words(root):
    words = []
    src = None
    for rel in ("主题/敏感词表.md",):
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            src = rel
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("|") or line.startswith(">"):
                    continue
                if line.startswith("-"):
                    line = line.lstrip("- ").strip()
                if line and not line.startswith("<"):
                    words.append(line)
            break
    example = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "data", "sensitive-words.example.txt")
    if not words and os.path.isfile(example):
        for line in open(example, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("<"):
                continue
            words.append(line)
        if words:
            src = ".cursor/tools/data/sensitive-words.example.txt"
        else:
            src = None
    return words, src


def load_learn_blacklist(root):
    """读 `.cursorGrowth/learn/writing-voice.md` 里「禁套词 / 黑名单」小节。"""
    words = []
    for rel in (".cursorGrowth/learn/writing-voice.md",
                ".cursorGrowth/learn/rhythm.md"):
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            continue
        text = open(p, encoding="utf-8").read()
        m = re.search(r"^#{1,4}[^\n]*(?:禁套词|黑名单|禁忌词)[^\n]*$", text, re.M)
        if not m:
            continue
        rest = text[m.end():]
        end = re.search(r"^#{1,4}\s", rest, re.M)
        for line in (rest[:end.start()] if end else rest).splitlines():
            s = line.strip().lstrip("-* ").strip("`").strip()
            if s and not s.startswith(("<", ">", "|")) and len(s) < 40:
                words.append(s)
    return words


def safe_read(path):
    """返回 (文本, 是否编码异常)。非 UTF-8 不再崩溃，但会明确报出来。"""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read(), False
    except UnicodeDecodeError:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read(), True
    except OSError:
        return "", True


def check_file(path, cfg, sensitive, project_blacklist):
    raw, enc_bad = safe_read(path)
    text = strip_code(raw)
    issues = []          # (level, code, detail)
    if enc_bad:
        issues.append(("🔴", "encoding", "文件不是 UTF-8（已按替换字符读取，需转码）"))

    def add(level, code, detail):
        issues.append((level, code, detail))

    cjk = cjk_count(text)
    chars = visible_count(text)

    # ── 加粗密度 ──
    marks = len(re.findall(r"\*\*", text))
    density = marks / (chars / 100.0) if chars else 0.0
    if density > cfg["bold_fail"]:
        add("🔴", "bold-density", f"{density:.1f}/100 字 > {cfg['bold_fail']:.0f}")
    elif density > cfg["bold_warn"]:
        add("🟡", "bold-density", f"{density:.1f}/100 字 > {cfg['bold_warn']:.0f}")

    # ── `##` 标题白名单 ──
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^##\s+(.*)$", line.strip())
        if m:
            title = m.group(1).strip()
            if title not in LEGAL_H2:
                add("🔴", "illegal-h2", f"L{i}: `## {title}`（仅允许 {'/'.join('## ' + x for x in LEGAL_H2)}）")

    # ── 分镜术语 ──
    for w in FILMIC:
        if w in text:
            add("🔴", "filmic-term", f"`{w}`")

    # ── 标点上限（每章）：取自公开去 AI 味阈值（deai ≤2/千字·inkflow ≤4/章）──
    for label, pat, cap in (("破折号", r"[—－]+", cfg.get("dash_max", 4)),
                            ("省略号", r"[…]+", cfg.get("ellipsis_max", 3)),
                            ("感叹号", r"[！!]", cfg.get("exclaim_max", 5))):
        n = len(re.findall(pat, text))
        if n > cap:
            add("🔴" if n > cap * 2 else "🟡", "punct-overuse",
                f"{label} {n} 处 > 每章上限 {cap}（多用即模板腔，靠句法与留白替代）")

    # ── 结构型套式（成对出现才是模板腔）──
    for pat, why in PATTERN_RULES:
        hits = re.findall(pat, text)
        if hits:
            add("🟡", "pattern-tell", f"{why} ×{len(hits)}")

    # ── 弱化副词堆叠（不禁止单词，只禁止密度）──
    tic = sum(text.count(w) for w in SOFT_TIC_WORDS)
    if cjk and tic / (cjk / 1000) > SOFT_TIC_PER_KCHAR:
        add("🟡", "tic-density",
            f"弱化套词（{'/'.join(SOFT_TIC_WORDS)}）{tic} 次 = "
            f"{tic / (cjk / 1000):.1f}/千字 > {SOFT_TIC_PER_KCHAR}")

    # ── 反均匀化：每 100 字至少 1 句 ≤ 10 字（句子长度过分整齐 = AI 腔）──
    _sents = split_sentences(text)
    if cjk >= 300 and _sents:
        window = 100.0
        per_100 = cjk / window
        short = sum(1 for s in _sents if cjk_count(s) <= 10)
        if short < per_100:
            add("🟡", "uniform-length",
                f"每 100 字仅 {short / per_100:.2f} 个 ≤10 字短句（< 1）——句子长度过于均匀")
        sd = 0.0
        lens = [cjk_count(s) for s in _sents]
        if len(lens) > 1:
            mean = sum(lens) / len(lens)
            sd = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5
            cv = sd / mean if mean else 0
            if cv < 0.25:
                add("🟡", "uniform-length", f"句长变异系数 CV={cv:.2f} < 0.25（过于整齐）")

    # ── 作者元叙事（只看叙事行；`#` 标题、`>` 视角标记、表格/列表行不算正文叙述）──
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s[0] in "#>|-":
            continue
        for pat in META_NARRATION:
            m = re.search(pat, s)
            if m:
                add("🔴", "meta-narration", f"L{i}: `{m.group(0)}`")
                break

    # ── AI 套词：硬套词（任意位置）──
    for w in AI_PHRASES_ANYWHERE:
        c = text.count(w)
        if c:
            lvl = "🔴" if w in ("眼中闪过", "嘴角勾起", "空气中弥漫",
                                "时间凝固", "时间仿佛凝固", "心中涌起", "眼神变得复杂") else "🟡"
            add(lvl, "ai-phrase", f"`{w}` ×{c}")

    # ── 引导词 / 弱化句式：只认句首（避免"仿佛"在句中被误报）──
    for w in AI_PHRASES_LEADING:
        c = leading_hits(text, w)
        if c:
            add("🟡", "ai-leading", f"句首 `{w}` ×{c}")

    # ── 项目黑名单（`主题/通用约束.md` §3.2，由 /nlearn 沉淀）──
    for w in project_blacklist:
        c = text.count(w)
        if c:
            add("🔴", "project-blacklist", f"`{w}` ×{c}（项目黑名单）")

    # ── 过程件/元数据残留 ──
    for w in ARTIFACT:
        if w in text:
            add("🔴", "artifact", f"`{w}`")
    if re.search(r"<!--.*?-->", text, re.S):
        add("🔴", "html-comment", "正文含 HTML 注释（元数据）")

    # ── 标点：半角与引号 ──
    for m in re.finditer(r"[\u4e00-\u9fff][,;!?]", text):
        add("🟡", "halfwidth-punct", f"`{m.group(0)}`")
        break
    if re.search(r'["\']', text):
        add("🟡", "ascii-quote", "含半角引号（约定用全角弯引号 / 「」）")

    # ── 长句与连续短句 ──
    sents = split_sentences(text)
    long_n = 0
    for s in sents:
        if cjk_count(s) > cfg["long_sentence"]:
            long_n += 1
    if long_n:
        add("🟡", "long-sentence", f"{long_n} 句 > {cfg['long_sentence']} 字")

    run = 0
    worst = 0
    for s in sents:
        if 0 < cjk_count(s) <= cfg["short_sentence"]:
            run += 1
            worst = max(worst, run)
        else:
            run = 0
    if worst >= cfg["short_run"]:
        add("🟡", "short-run", f"连续 {worst} 个短句（≥{cfg['short_run']}）")

    # ── 敏感词 ──
    for w in sensitive:
        if w and w in text:
            add("🔴", "sensitive", f"`{w}`")

    # ── 节长 ──
    if cjk == 0:
        # 空文件/纯结构行：不能报 ✅ —— 截断的章节必须拦住
        add("🔴", "empty", "文件无正文汉字（空文件、被截断，或只剩结构与标记行）")
    elif cjk > cfg["sec_hard_max"]:
        add("🔴", "section-length", f"{cjk} 汉字 > 硬上限 {cfg['sec_hard_max']}")
    elif cjk < cfg["sec_target_min"]:
        add("🟡", "section-length", f"{cjk} 汉字 < 目标下限 {cfg['sec_target_min']}")

    return {"path": path, "cjk": cjk, "chars": chars, "bold_density": round(density, 2),
            "sentences": len(sents), "issues": issues}


def chapter_of(path):
    """从 `章节/第NN章_x/第SS节_y.md` 取章目录；否则取父目录。"""
    d = os.path.dirname(path)
    base = os.path.basename(d)
    return base or "."


def collect(targets, root):
    files = []
    for t in targets:
        p = t if os.path.isabs(t) else os.path.join(root, t)
        if os.path.isfile(p) and p.endswith(".md"):
            files.append(p)
        elif os.path.isdir(p):
            for dp, _dn, fns in os.walk(p):
                for fn in sorted(fns):
                    if fn.endswith(".md"):
                        files.append(os.path.join(dp, fn))
    if not files:
        default = os.path.join(root, "章节")
        if os.path.isdir(default):
            for dp, _dn, fns in os.walk(default):
                for fn in sorted(fns):
                    if fn.endswith(".md"):
                        files.append(os.path.join(dp, fn))
    return sorted(set(files))


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("targets", nargs="*", help="要扫的文件/目录（默认 章节/）")
    ap.add_argument("--root", default=None, help="项目根（默认 .cursor/ 的上级）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="只输出 🔴")
    ap.add_argument("--words", action="store_true", help="只看字数汇总")
    ap.add_argument("--style", action="store_true",
                    help="与 主题/风格档.md 的目标值比对风格指纹（未声明偏离=🔴）")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    root = args.root or os.path.dirname(os.path.dirname(here))
    if not os.path.isdir(root):
        print(f"✗ 项目根不存在：{root}", file=sys.stderr)
        return 2

    cfg_path, cfg_text = find_cfg_text(root)
    cfg = apply_constraints(dict(DEFAULTS), cfg_text)
    sensitive, sens_src = load_sensitive_words(root)
    blacklist = load_project_blacklist(cfg_text) + load_learn_blacklist(root)
    # 去重保序
    blacklist = list(dict.fromkeys(blacklist))

    files = collect(args.targets, root)
    if not files:
        print(f"✗ 未找到正文文件（默认目录 {os.path.join(root, '章节')}）", file=sys.stderr)
        return 2

    results = [check_file(f, cfg, sensitive, blacklist) for f in files]

    if args.json:
        payload = {
            "root": root,
            "config_source": cfg_path and os.path.relpath(cfg_path, root),
            "sensitive_source": sens_src,
            "project_blacklist": blacklist,
            "thresholds": cfg,
            "files": results,
        }
        # --json 也必须跑风格比对并把判定反映到退出码（否则 --style 被静默吞掉）
        style_fail = 0
        if args.style:
            style_fail, payload["style"] = style_compare(files, root, cfg, quiet=True)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        hard = any(i[0] == "🔴" for r in results for i in r["issues"])
        return 1 if (hard or style_fail) else 0

    total_cjk = sum(r["cjk"] for r in results)
    print(f"正文校验 · {len(results)} 个文件 · 合计 {total_cjk} 汉字")
    print(f"阈值来源：{os.path.relpath(cfg_path, root) if cfg_path else '母版默认'}"
          f" · 敏感词：{sens_src or '（未配置）'}"
          f" · 项目黑名单：{len(blacklist)} 条")

    if not args.words:
        for r in results:
            rel = os.path.relpath(r["path"], root)
            marks = [i for i in r["issues"] if i[0] == "🔴"]
            warns = [i for i in r["issues"] if i[0] == "🟡"]
            if args.quiet and not marks:
                continue
            flag = "🔴" if marks else ("🟡" if warns else "✅")
            print(f"\n{flag} {rel}  ({r['cjk']} 汉字 · 加粗密度 {r['bold_density']}/100)")
            for lvl, code, detail in r["issues"]:
                if args.quiet and lvl != "🔴":
                    continue
                print(f"    {lvl} [{code}] {detail}")

    # 章节聚合
    chaps = {}
    for r in results:
        chaps.setdefault(chapter_of(r["path"]), 0)
        chaps[chapter_of(r["path"])] += r["cjk"]
    if len(chaps) > 1 or (chaps and list(chaps)[0] not in ("章节", ".")):
        print("\n章汇总：")
        for c, n in sorted(chaps.items()):
            if c in ("章节", "."):
                continue
            warn = ""
            if n > cfg["chap_max"]:
                warn = f"  🟡 > 章窗上限 {cfg['chap_max']}"
            elif n < cfg["chap_min"]:
                warn = f"  🟡 < 章窗下限 {cfg['chap_min']}"
            print(f"  {c}: {n} 汉字{warn}")

    n_fail = sum(1 for r in results for i in r["issues"] if i[0] == "🔴")
    n_warn = sum(1 for r in results for i in r["issues"] if i[0] == "🟡")
    print(f"\n{'✗' if n_fail else '✓'} 🔴 {n_fail} · 🟡 {n_warn}")
    if n_fail:
        print("提示：本工具只报告。改稿走 novel-line-rewriter（先备份），改完重跑本命令。")

    style_fail = 0
    if args.style:
        style_fail, _style = style_compare(files, root, cfg)
        if style_fail:
            print("风格偏差计入失败：请改文或在 `主题/风格档.md` §三 声明豁免。")
    return 1 if (n_fail or style_fail) else 0


if __name__ == "__main__":
    sys.exit(main())
