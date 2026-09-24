#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_continuity.py · 连续性机械核对（仅标准库 · 零 token）

定位：**在 LLM 评审之前**跑的确定性检查。全部结论来自账本 + 正文的集合运算，
      不消耗模型、可复现、可作为门禁。发现的问题再作为输入喂给语义评审。

读三处：
    `主题/连续性台账.md`   角色状态 / 境界层级 / 资源归属 / 子线进度 / 节奏配额 / 豁免账本
    `主题/伏笔板.md`        伏笔是否超期未收（长篇最常见的缺陷）
    `章节/第NNN章_*/`      正文（按章号顺序扫名字与物品）

检查项（code）：
    dead-reappear      已死亡/已退场的角色在变动章之后再出场        🔴
    resource-reappear  已消耗/已损毁的物品在变动章之后再被使用      🔴
    progression-drop   境界/实力层级序号回退（量纲一致性）          🔴
    foreshadow-overdue 伏笔超过计划回收章仍未回收                   🔴
    quota-exceed       单章"实质推进项" > 1（防剧情加速）           🔴
    dormant-subplot    子线停滞超过阈值                             🟡
    absent-character   在世角色长期未出场（可能被遗忘）             🟡
    fast-streak        连续 3 章为"快档"（读者会疲）                🟡
    event-cooldown     同一事件类型两次触发间隔不足冷却              🟡
    ledger-ahead       台账章号超前于已有正文                       🟡

**豁免**：命中项若在台账 §六 已登记（`事实` 或 `原因` 里写明 code），降级为 🟡 已登记豁免。
        机械检查分不清"不可靠叙述者"与"写错了"——没有豁免登记，同一非错误会被反复重报，
        最终作者不再读报告，工具就此失效。

用法：
    python3 .cursor/tools/check_continuity.py [--root .] [--quiet] [--json]
退出码：0 无 🔴；1 有 🔴；2 用法/环境错误。
"""

import argparse
import json
import os
import re
import sys

LEDGER = "主题/连续性台账.md"
FORESHADOW = "主题/伏笔板.md"
CHAPTERS = "章节"

# 母版默认阈值（项目可在 `主题/通用约束.md` §五 覆盖）
ABSENT_MAX = 8          # 在世角色连续 N 章未出场 → 🟡
FAST_STREAK = 3         # 连续 N 章"快档" → 🟡
EVENT_COOLDOWN = {      # 事件类型 → 冷却章数
    "冲突刺激": 2, "conflict_thrill": 2,
    "关系深化": 1, "bond_deepening": 1,
    "势力经营": 2, "faction_building": 2,
    "世界观铺陈": 3, "world_painting": 3,
    "张力升级": 2, "tension_escalation": 2,
}
FUTURE_WORDS = ("已死亡", "已退场")
GONE_WORDS = ("已消耗", "已损毁", "已转手")


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return ""


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def table_after(text, heading_re):
    """取某个小标题之后的第一个 markdown 表格的数据行。"""
    m = re.search(heading_re, text, re.M)
    if not m:
        return []
    rows = []
    for line in text[m.end():].splitlines():
        if line.strip().startswith("##"):
            break
        if not line.strip().startswith("|"):
            continue
        cs = cells(line)
        if not cs or set("".join(cs)) <= set("-: "):
            continue
        rows.append(cs)
    if rows and rows[0] and rows[0][0] in ("角色", "物品", "子线", "章", "对象"):
        rows = rows[1:]                      # 去掉表头
    return [r for r in rows if any(r)]


def chapter_no(name):
    """`第012章_x` → 12；无法解析返回 None。"""
    m = re.search(r"第\s*([0-9一二三四五六七八九十百千]+)\s*章", name)
    if not m:
        return None
    s = m.group(1)
    if s.isdigit():
        return int(s)
    cn = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    if s == "十":
        return 10
    if "十" in s:
        a, _, b = s.partition("十")
        return (cn.get(a, 1) if a else 1) * 10 + (cn.get(b, 0) if b else 0)
    return cn.get(s)


def norm_ch(v):
    """'第012章' / '12' / '——' → int|None"""
    if not v:
        return None
    m = re.search(r"([0-9]+)", v)
    if m:
        return int(m.group(1))
    return chapter_no(v)


def collect_chapters(root):
    base = os.path.join(root, CHAPTERS)
    out = []
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        no = chapter_no(name)
        if no is None:
            continue
        text = []
        for dp, _dn, fns in os.walk(d):
            for fn in sorted(fns):
                if fn.endswith(".md"):
                    text.append(read(os.path.join(dp, fn)))
        out.append((no, name, "\n".join(text)))
    return sorted(out)


def parse_ledger(root):
    text = read(os.path.join(root, LEDGER))
    if not text:
        return None
    return {
        "chars": table_after(text, r"^##\s*一、角色状态"),
        "levels": table_after(text, r"^##\s*二、境界"),
        "res": table_after(text, r"^##\s*三、资源"),
        "subs": table_after(text, r"^##\s*四、子线"),
        "pacing": table_after(text, r"^##\s*五、节奏"),
        "exempt": table_after(text, r"^##\s*六、豁免"),
        "raw": text,
    }


def parse_foreshadow(root):
    text = read(os.path.join(root, FORESHADOW))
    if not text:
        return []
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cs = cells(line)
        if len(cs) < 8 or cs[0].startswith(("ID", "-", ":")):
            continue
        if not re.match(r"^fs-|^[A-Za-z]+-\d+", cs[0]):
            continue
        rows.append(cs)
    return rows


def exempted(exempt_rows, code, name):
    for r in exempt_rows:
        if len(r) < 3:
            continue
        if name and name not in r[0]:
            continue
        blob = " ".join(r)
        if code in blob:
            return True
        if name and name in r[0] and code in (r[1] if len(r) > 1 else ""):
            return True
    return False


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", default=None)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    root = args.root or os.path.dirname(os.path.dirname(here))
    if not os.path.isdir(root):
        print(f"✗ 项目根不存在：{root}", file=sys.stderr)
        return 2

    chapters = collect_chapters(root)
    latest = max((c[0] for c in chapters), default=0)
    led = parse_ledger(root)
    if led is None:
        msg = (f"⚠ 未找到 `{LEDGER}` —— 连续性机械核对**未生效**。\n"
               f"  复制模板建立台账：.cursor/templates/continuity-ledger.md")
        if args.json:
            print(json.dumps({"error": "no_ledger"}, ensure_ascii=False))
        else:
            print(msg, file=sys.stderr)
        return 0 if not chapters else 0      # 新项目不算失败；不阻断

    findings = []      # (level, code, detail)

    def hit(level, code, name, detail):
        if exempted(led["exempt"], code, name):
            findings.append(("🟡", code, f"已登记豁免 · {detail}"))
        else:
            findings.append((level, code, detail))

    text_by_ch = {no: t for no, _n, t in chapters}

    def appears_after(name, after_no):
        """返回变动章之后仍出现 name 的章号列表。"""
        return [no for no, _n, t in chapters if no > after_no and name and name in t]

    # ── 1. 已死亡/已退场角色再出场 ──
    for r in led["chars"]:
        if len(r) < 3:
            continue
        name, status, chg = r[0], r[1], norm_ch(r[2])
        if not name or any(w in status for w in FUTURE_WORDS) and chg:
            for no in appears_after(name, chg):
                hit("🔴", "dead-reappear", name,
                    f"{name} 已于第{chg:03d}章「{status}」，但第{no:03d}章正文仍出现该角色")

    # ── 2. 已消耗/损毁/转手资源再现 ──
    for r in led["res"]:
        if len(r) < 4:
            continue
        item, _owner, status, chg = r[0], r[1], r[2], norm_ch(r[3])
        if not item or not chg or not any(w in status for w in GONE_WORDS):
            continue
        for no in appears_after(item, chg):
            hit("🔴", "resource-reappear", item,
                f"「{item}」已于第{chg:03d}章「{status}」，但第{no:03d}章正文仍出现")

    # ── 3. 层级序号单调性 ──
    by_char = {}
    for r in led["levels"]:
        if len(r) < 4:
            continue
        name, tier, idx, ch = r[0], r[1], r[2], norm_ch(r[3])
        m = re.search(r"-?\d+", idx)
        if not name or not m or ch is None:
            continue
        by_char.setdefault(name, []).append((ch, float(m.group(0)), tier))
    for name, seq in by_char.items():
        seq.sort()
        for (c1, i1, t1), (c2, i2, t2) in zip(seq, seq[1:]):
            if i2 < i1:
                hit("🔴", "progression-drop", name,
                    f"{name} 层级序号回退：第{c1:03d}章 {t1}({i1:g}) → 第{c2:03d}章 {t2}({i2:g})")

    # ── 4. 伏笔超期未收 ──
    for r in parse_foreshadow(root):
        fid, _desc, _type, _plant, _dist, plan, status = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
        if any(w in status for w in ("已回收", "已放弃", "作废")):
            continue
        p = norm_ch(plan)
        if p and latest and p < latest:
            hit("🔴", "foreshadow-overdue", fid,
                f"{fid}（{r[1][:18]}）计划第{p:03d}章回收，现已到第{latest:03d}章仍未回收")

    # ── 5. 节奏配额 / 档位 / 事件冷却 ──
    rows = []
    for r in led["pacing"]:
        if len(r) < 3:
            continue
        no = norm_ch(r[0])
        if no is None:
            continue
        cnt = re.search(r"\d+", r[2])
        rows.append((no, r[1].strip(), int(cnt.group(0)) if cnt else 0,
                     r[3] if len(r) > 3 else ""))
    rows.sort()
    for no, gear, cnt, ev in rows:
        if cnt > 1:
            hit("🔴", "quota-exceed", f"第{no:03d}章",
                f"第{no:03d}章实质推进项 {cnt} 项 > 每章上限 1（防剧情加速：配额是硬上限）")
        if no > latest:
            hit("🟡", "ledger-ahead", f"第{no:03d}章",
                f"台账已登记第{no:03d}章，但正文只到第{latest:03d}章")
    for i in range(len(rows) - FAST_STREAK + 1):
        win = rows[i:i + FAST_STREAK]
        if all(w[1] == "快" for w in win):
            hit("🟡", "fast-streak", f"第{win[0][0]:03d}章",
                f"第{win[0][0]:03d}–{win[-1][0]:03d}章 连续 {FAST_STREAK} 章「快档」——读者会疲")
    last_seen = {}
    for no, _gear, _cnt, ev in rows:
        key = ev.strip()
        cd = EVENT_COOLDOWN.get(key)
        if not cd or not key:
            continue
        if key in last_seen and no - last_seen[key] <= cd:
            hit("🟡", "event-cooldown", f"第{no:03d}章",
                f"「{key}」第{last_seen[key]:03d}章刚用过，第{no:03d}章再用（需间隔 {cd} 章）")
        last_seen[key] = no

    # ── 6. 在世角色长期未出场 ──
    if latest:
        for r in led["chars"]:
            if len(r) < 4:
                continue
            name, status, _chg, upd = r[0], r[1], r[2], norm_ch(r[3])
            if not name or any(w in status for w in FUTURE_WORDS):
                continue
            last = max([no for no, _n, t in chapters if name in t], default=upd or 0)
            if last and latest - last >= ABSENT_MAX:
                hit("🟡", "absent-character", name,
                    f"{name} 自第{last:03d}章起连续 {latest - last} 章未出场（≥{ABSENT_MAX}）——"
                    f"容易被遗忘，复出时需重新立人")

    # ── 7. 子线停滞 ──
    for r in led["subs"]:
        if len(r) < 3:
            continue
        name, lastc, thr = r[0], norm_ch(r[1]), norm_ch(r[2])
        if not name or not lastc or not thr or not latest:
            continue
        if latest - lastc > thr:
            hit("🟡", "dormant-subplot", name,
                f"子线「{name}」自第{lastc:03d}章起停滞 {latest - lastc} 章（阈值 {thr}）")

    fails = [f for f in findings if f[0] == "🔴"]
    warns = [f for f in findings if f[0] == "🟡"]

    if args.json:
        print(json.dumps({
            "root": root, "latest_chapter": latest,
            "ledger": {"chars": len(led["chars"]), "levels": len(led["levels"]),
                       "resources": len(led["res"]), "subplots": len(led["subs"]),
                       "pacing": len(led["pacing"]), "exemptions": len(led["exempt"])},
            "findings": [{"level": l, "code": c, "detail": d} for l, c, d in findings],
            "fail": len(fails), "warn": len(warns),
        }, ensure_ascii=False, indent=2))
        return 1 if fails else 0

    if not args.quiet:
        print(f"连续性机械核对 · 正文到第{latest:03d}章 · "
              f"台账（角色 {len(led['chars'])} · 层级 {len(led['levels'])} · "
              f"资源 {len(led['res'])} · 子线 {len(led['subs'])} · "
              f"节奏 {len(led['pacing'])} · 豁免 {len(led['exempt'])}）")
        for level, code, detail in findings:
            print(f"  {level} [{code}] {detail}")
        if not findings:
            print("  ✓ 未发现机械可查的连续性问题")
    print(f"\n{'✗' if fails else '✓'} 🔴 {len(fails)} · 🟡 {len(warns)}")
    if fails:
        print("提示：改正文，或在 `主题/连续性台账.md` §六 登记豁免"
              "（`事实`/`原因` 里写明检查 code，如 dead-reappear）。")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
