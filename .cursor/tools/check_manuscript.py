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
AI_PHRASES = [
    "眼中闪过", "嘴角勾起", "空气中弥漫", "时间凝固", "时间仿佛凝固",
    "心中涌起", "眼神变得复杂", "那一刻，他意识到", "那一刻，她意识到",
    "然而，", "不仅", "事实上，", "某种意义上", "本质上，", "不由自主",
    "不由得", "不禁", "仿佛", "似乎",
]
# 正文中不允许出现的元数据/过程件痕迹
ARTIFACT = ["八股检测报告", "**原**", "批注", "复盘", "修改清单", "TODO", "FIXME", "待补"]


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


def check_file(path, cfg, sensitive):
    raw = open(path, encoding="utf-8").read()
    text = strip_code(raw)
    issues = []          # (level, code, detail)

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

    # ── AI 套词 ──
    for w in AI_PHRASES:
        c = text.count(w)
        if c:
            lvl = "🔴" if w in ("眼中闪过", "嘴角勾起", "空气中弥漫", "时间凝固", "时间仿佛凝固") else "🟡"
            add(lvl, "ai-phrase", f"`{w}` ×{c}")

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
    if cjk:
        if cjk > cfg["sec_hard_max"]:
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
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    root = args.root or os.path.dirname(os.path.dirname(here))
    if not os.path.isdir(root):
        print(f"✗ 项目根不存在：{root}", file=sys.stderr)
        return 2

    cfg_path, cfg_text = find_cfg_text(root)
    cfg = apply_constraints(dict(DEFAULTS), cfg_text)
    sensitive, sens_src = load_sensitive_words(root)

    files = collect(args.targets, root)
    if not files:
        print(f"✗ 未找到正文文件（默认目录 {os.path.join(root, '章节')}）", file=sys.stderr)
        return 2

    results = [check_file(f, cfg, sensitive) for f in files]

    if args.json:
        print(json.dumps({
            "root": root,
            "config_source": cfg_path and os.path.relpath(cfg_path, root),
            "sensitive_source": sens_src,
            "thresholds": cfg,
            "files": results,
        }, ensure_ascii=False, indent=2))
        return 1 if any(i[0] == "🔴" for r in results for i in r["issues"]) else 0

    total_cjk = sum(r["cjk"] for r in results)
    print(f"正文校验 · {len(results)} 个文件 · 合计 {total_cjk} 汉字")
    print(f"阈值来源：{os.path.relpath(cfg_path, root) if cfg_path else '母版默认'}"
          f" · 敏感词：{sens_src or '（未配置）'}")

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
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
