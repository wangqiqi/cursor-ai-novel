#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selftest.py · 母版守卫的**反向测试**（负向测试 / tamper matrix）

为什么需要它：
    "自检通过"本身不是证据 —— 如果守卫写错了、或根本没触发，自检照样打印 ✓。
    本脚本故意**投毒**：往 `.cursor/` 的临时副本里注入每一类已知缺陷，
    然后确认对应守卫**真的报错**。守卫不响 = 回归，本脚本退 1。

用法：
    python3 .cursor/tools/selftest.py            # 全部用例
    python3 .cursor/tools/selftest.py -v         # 打印每个用例的输出摘要

退出码：0 全部守卫按预期触发；1 有用例未触发（守卫失效）。
只依赖标准库；只写临时目录，不动真实仓库。
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)                       # 真实 .cursor/
VERBOSE = "-v" in sys.argv


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def fresh(sandbox):
    """在沙箱里放一份干净的 .cursor 副本，返回其路径。"""
    dst = os.path.join(sandbox, ".cursor")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(SRC, dst)
    return dst


def patch(path, old, new, count=1):
    with open(path, encoding="utf-8") as fh:
        t = fh.read()
    if old not in t:
        raise AssertionError(f"投毒锚点未命中：{path} :: {old[:60]!r}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(t.replace(old, new, count))


def append(path, text):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(text)


# ── 用例：每个返回 (是否需要检测到, 期望出现在输出里的标记) ──────────────────

def t_clause(cur):
    """§ 引用指向不存在的条款"""
    append(os.path.join(cur, "skills", "novel-style", "SKILL.md"),
           "\n- 见 `主题/通用约束.md` §九九（该节不存在）\n")
    return "[clause]"


def t_glob(cur):
    """资产不再被语义对口的规则覆盖"""
    p = os.path.join(cur, "rules", "05-novel-style.mdc")
    patch(p, "globs: 章节/**/*.md, 主题/风格档.md", "globs: 章节/**/*.md")
    return "[glob]"


def t_axis_declared(cur):
    """_axes 声明了没有人实现的指标"""
    p = os.path.join(cur, "tools", "data", "style-archetypes.json")
    patch(p, '"avg_sentence_len": {', '"fake_axis_zzz": { "name": "假轴", "unit": "个/千字" },\n    "avg_sentence_len": {')
    return "[axis]"


def t_axis_unit(cur):
    """单位不可读（伪装成指标）"""
    p = os.path.join(cur, "tools", "data", "style-archetypes.json")
    patch(p, '"unit": "汉字/句"', '"unit": "光年/平方秒"')
    return "[axis]"


def t_write_read(cur):
    """登记了一个没人读的资产"""
    p = os.path.join(cur, "rules", "00-novel-meta.mdc")
    patch(p, "| 风格档 |", "| 孤儿资产 | `主题/孤儿测试.md` | — | `novel-plot` | — |\n| 风格档 |")
    return "[write-read]"


def t_style_missing_ref(cur):
    """原型 reference 文件缺失"""
    os.remove(os.path.join(cur, "skills", "novel-style", "reference", "cold-minimal.md"))
    return "[style]"


def t_style_ref_path(cur):
    """原型 reference 指向不存在的路径"""
    p = os.path.join(cur, "tools", "data", "style-archetypes.json")
    patch(p, '"reference": "skills/novel-style/reference/magic-daily.md"',
          '"reference": "skills/novel-style/reference/nope.md"')
    return "[style]"


def t_json_broken(cur):
    """风格数值真源 JSON 损坏"""
    p = os.path.join(cur, "tools", "data", "style-archetypes.json")
    append(p, "{ 这不是合法 JSON")
    return "[axis]"


def t_frontmatter(cur):
    """规则 frontmatter 破坏了加载契约"""
    p = os.path.join(cur, "rules", "01-novel-language.mdc")
    patch(p, "globs: 章节/**/*.md, 主题/**/*.md", "globs:")
    return "[frontmatter]"


def t_link(cur):
    """引用了一个不存在的母版文件"""
    append(os.path.join(cur, "skills", "novel-chapter", "SKILL.md"),
           "\n- 见 `.cursor/tools/does_not_exist.py`\n")
    return "[link]"


def t_skill_name(cur):
    """skill 名与目录不一致（不会被加载）"""
    p = os.path.join(cur, "skills", "novel-style", "SKILL.md")
    patch(p, "name: novel-style", "name: novel-style-typo")
    return "[skill]"


def t_genre(cur):
    """类型参考未被派发表登记"""
    os.remove(os.path.join(cur, "skills", "novel-genre", "reference", "comedy-craft.md"))
    return "[genre]"


# (名称, 投毒函数, 期望标记, 期望至少几条)
INTEGRITY_CASES = [
    ("clause：悬空 § 引用", t_clause, "[clause]", 1),
    ("glob：资产失去对口规则覆盖", t_glob, "[glob]", 1),
    ("axis：声明了未实现的指标", t_axis_declared, "[axis]", 1),
    ("axis：单位不可读", t_axis_unit, "[axis]", 1),
    ("write-read：资产无人读", t_write_read, "[write-read]", 1),
    ("style：reference 文件缺失", t_style_missing_ref, "[style]", 1),
    ("style：reference 路径错误", t_style_ref_path, "[style]", 1),
    ("JSON：数值真源损坏", t_json_broken, "[axis]", 1),
    ("frontmatter：规则永不加载", t_frontmatter, "[frontmatter]", 1),
    ("link：悬空文件引用", t_link, "[link]", 1),
    ("skill：name 与目录不一致", t_skill_name, "[skill]", 1),
    ("genre：类型参考缺失", t_genre, "[genre]", 1),
]

# ── 其它工具的门禁（各自在临时小项目里跑）─────────────────────────────────

def mini_project(sandbox, name):
    """造一个最小项目：复制工具 + 数值真源，含一节正文。"""
    root = os.path.join(sandbox, name)
    for d in (".cursor/tools/data", "主题", "章节/第01章_a"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    for f in ("check_manuscript.py", "analyze_style.py", "snapshot.py", "build_export.py",
              "check_continuity.py"):
        shutil.copy(os.path.join(HERE, f), os.path.join(root, ".cursor/tools", f))
    shutil.copy(os.path.join(HERE, "data", "style-archetypes.json"),
                os.path.join(root, ".cursor/tools/data/style-archetypes.json"))
    with open(os.path.join(root, "章节/第01章_a/第01节_a.md"), "w", encoding="utf-8") as fh:
        fh.write("# 第01节 a\n\n> 【视角：他】\n\n雨停了。他站起来。门开着。\n")
    return root


def profile(root, rows):
    with open(os.path.join(root, "主题", "风格档.md"), "w", encoding="utf-8") as fh:
        fh.write("# 风格档\n\n| 轴 | 指标 | 目标 | 实测 |\n|---|---|---|---|\n" + rows)


def tool_case(sandbox, name, body):
    """body(root) 返回 (是否按预期被拦/报错)。"""
    root = mini_project(sandbox, name)
    try:
        return bool(body(root)), ""
    except AssertionError as exc:
        return False, str(exc)
    except Exception as exc:                     # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def tc_style_usnit(root):
    """目标带单位必须仍被解析并拦截（曾经的绕过路径）"""
    profile(root, "| 平均句长 | `avg_sentence_len` | 30–48 字 | |\n")
    rc, _ = run([sys.executable, ".cursor/tools/check_manuscript.py", "--style", "--quiet"], root)
    return rc != 0


def tc_style_notarget(root):
    """目标解析不到 → 必须按失败计"""
    profile(root, "| 平均句长 | `avg_sentence_len` | 待定 | |\n")
    rc, _ = run([sys.executable, ".cursor/tools/check_manuscript.py", "--style", "--quiet"], root)
    return rc != 0


def tc_style_fake_exempt(root):
    """备注列写「见 §三 豁免」不得算豁免"""
    profile(root, "| 平均句长 | `avg_sentence_len` | 40–50 | 见 §三 豁免 |\n")
    rc, _ = run([sys.executable, ".cursor/tools/check_manuscript.py", "--style", "--quiet"], root)
    return rc != 0


def tc_style_json(root):
    """--style --json 的退出码必须与文本模式一致"""
    profile(root, "| 平均句长 | `avg_sentence_len` | 40–50 | |\n")
    rc, out = run([sys.executable, ".cursor/tools/check_manuscript.py", "--style", "--json"], root)
    return rc != 0 and '"style"' in out


def tc_empty_file(root):
    """0 汉字文件必须判 🔴"""
    open(os.path.join(root, "章节/第01章_a/第02节_e.md"), "w").close()
    rc, _ = run([sys.executable, ".cursor/tools/check_manuscript.py", "--quiet"], root)
    return rc != 0


def tc_snapshot_diff_gate(root):
    """快照后有改动 → diff 必须退 1"""
    run([sys.executable, ".cursor/tools/snapshot.py", "snapshot", "--note", "t"], root)
    with open(os.path.join(root, "章节/第01章_a/第01节_a.md"), "w", encoding="utf-8") as fh:
        fh.write("# 第01节 a\n\n改了。\n")
    rc, _ = run([sys.executable, ".cursor/tools/snapshot.py", "diff"], root)
    return rc != 0


def tc_snapshot_restore_incomplete(root):
    """快照内缺文件时回滚必须退 1（不得静默降级）"""
    run([sys.executable, ".cursor/tools/snapshot.py", "snapshot", "--note", "t"], root)
    adir = os.path.join(root, ".cursorGrowth/archive")
    snap = sorted(os.listdir(adir))[-1]
    for dp, _dn, fns in os.walk(os.path.join(adir, snap)):
        for fn in fns:
            if fn.endswith(".md") and "manifest" not in fn:
                os.remove(os.path.join(dp, fn))
    rc, _ = run([sys.executable, ".cursor/tools/snapshot.py", "restore", "latest", "--yes"], root)
    return rc != 0


def tc_export_bad_format(root):
    """未知 --format 必须退 2（不得静默无产出）"""
    rc, _ = run([sys.executable, ".cursor/tools/build_export.py", "--format", "epubx",
                 "--title", "X"], root)
    return rc == 2


def tc_export_xml_ok(root):
    """含 XML 非法控制字符也必须产出良构 EPUB"""
    with open(os.path.join(root, "章节/第01章_a/第01节_a.md"), "w", encoding="utf-8") as fh:
        fh.write("# 第01节 a\n\n正常\x01坏\x0b字\x00\n")
    run([sys.executable, ".cursor/tools/build_export.py", "--title", "CTL", "--author", "t",
         "--strip-structural"], root)
    ep = os.path.join(root, "build/CTL.epub")
    if not os.path.isfile(ep):
        return False
    import xml.etree.ElementTree as ET
    import zipfile
    with zipfile.ZipFile(ep) as z:
        for n in z.namelist():
            if n.endswith((".xhtml", ".opf", ".xml")):
                ET.fromstring(z.read(n))
    return True


def tc_analyze_bad_json(root):
    """数值真源损坏 → analyze_style 优雅退 2（不得 traceback）"""
    with open(os.path.join(root, ".cursor/tools/data/style-archetypes.json"), "w",
              encoding="utf-8") as fh:
        fh.write("{ broken")
    rc, out = run([sys.executable, ".cursor/tools/analyze_style.py", "--list-proto"], root)
    return rc == 2 and "Traceback" not in out


def tc_calibration_separation(root):
    """★ 评审校准：已知坏样本必须命中多项，已知好样本必须零 🔴。

    写作类项目的评审判官不能只看"跑通了"——要先用**手写的已知坏样本**校准，
    确认它真的能区分好坏。否则规则会在它本该抓的失败上变绿。
    """
    bad = ("# 第01节 坏\n\n> 【视角：他】\n\n"
           "他眼中闪过一丝犹疑，嘴角微微上扬，一股暖意涌上心头。不是害怕，而是解脱。\n"
           "没有犹豫，没有生涩，声音不大，却传得很远，仿佛——仿佛时间凝固。\n"
           "缓缓地，他微微抬头，轻轻地叹了口气，淡淡地笑了，一丝不安掠过。\n"
           "他走了。他说了。他看了。他停了。他站着。他坐着。他等着。他来了。\n")
    good = ("# 第01节 好\n\n> 【视角：他】\n\n"
            "他推开门。屋里很冷，炉子早灭了，煤渣上结着一层白霜。\n"
            "他在桌边坐下，把信纸摊平，又折起来，折成很小的一块，塞进袖口。\n"
            "窗外有辆板车过去，轮子碾在冻土上，吱呀吱呀地叫。他听着，没动。\n"
            "过了很久。他站起来，走到门口，还是把那块纸掏出来，就着炉灰点了。\n"
            "火苗很小。他盯着它，直到手指被烫了一下。他甩了甩手，出了门。\n"
            "天亮了。街上的水洼结着冰，踩上去先硬后脆，碎成一片一片。\n"
            "他去码头。船还在。他没上船，在石阶上坐下，看着水。\n")
    with open(os.path.join(root, "章节/第01章_a/第01节_坏.md"), "w", encoding="utf-8") as fh:
        fh.write(bad)
    with open(os.path.join(root, "章节/第01章_a/第02节_好.md"), "w", encoding="utf-8") as fh:
        fh.write(good)
    rc_bad, out_bad = run([sys.executable, ".cursor/tools/check_manuscript.py", "--json"], root)
    rc_good, out_good = run([sys.executable, ".cursor/tools/check_manuscript.py", "--json"], root)
    # 分开跑，避免两份文件互相干扰
    rc_bad, out_bad = run([sys.executable, ".cursor/tools/check_manuscript.py", "--json",
                           "章节/第01章_a/第01节_坏.md"], root)
    rc_good, out_good = run([sys.executable, ".cursor/tools/check_manuscript.py", "--json",
                             "章节/第01章_a/第02节_好.md"], root)
    import json as _json
    bad_find = _json.loads(out_bad)["files"][0]["issues"]
    good_find = _json.loads(out_good)["files"][0]["issues"]
    n_bad = len([i for i in bad_find if i[0] in ("🔴", "🟡")])
    n_good_red = len([i for i in good_find if i[0] == "🔴"])
    return rc_bad != 0 and n_bad >= 4 and n_good_red == 0


def _ledger_project(sandbox, name, exempt=False):
    root = mini_project(sandbox, name)
    for n in ("001", "002", "003", "004"):
        os.makedirs(os.path.join(root, "章节", f"第{n}章_测试"), exist_ok=True)
        with open(os.path.join(root, "章节", f"第{n}章_测试", "s.md"), "w", encoding="utf-8") as fh:
            fh.write("# 第01节\n\n阿禾与老陈同行。\n" if n in ("001", "004")
                     else "# 第01节\n\n老陈倒下了。\n")
    ex = ("| 老陈 | 死后于第004章出现 [dead-reappear] | 那是幻影，读者已知 | 第004章 |"
          if exempt else "| | | | |")
    with open(os.path.join(root, "主题", "连续性台账.md"), "w", encoding="utf-8") as fh:
        fh.write(
            "# 连续性台账\n\n## 一、角色状态\n\n"
            "| 角色 | 状态 | 变动章 | 最后更新章 | 备注 |\n|---|---|---|---|---|\n"
            "| 阿禾 | 在世 | — | 第004章 | |\n| 老陈 | 已死亡 | 第002章 | 第002章 | |\n\n"
            "## 二、境界 / 实力层级\n\n| 角色 | 当前层级 | 层级序号 | 更新章 |\n|---|---|---|---|\n"
            "| 阿禾 | 引气三层 | 3 | 第002章 |\n\n"
            "## 三、资源账本\n\n| 物品 | 归属 | 状态 | 变动章 |\n|---|---|---|---|\n"
            "| 铜铃 | 阿禾 | 持有 | 第001章 |\n\n"
            "## 四、子线推进\n\n| 子线 | 最近推进章 | 停滞阈值（章） |\n|---|---|---|\n"
            "| 支线 | 第004章 | 20 |\n\n"
            "## 五、节奏与事件配额\n\n| 章 | 档位 | 本章推进项数 | 事件类型 | 备注 |\n|---|---|---|---|---|\n"
            "| 第004章 | 中 | 1 | | |\n\n"
            "## 六、豁免账本\n\n| 对象 | 事实 | 原因 | 登记章 |\n|---|---|---|---|\n" + ex + "\n")
    return root


def tc_continuity_detects(root):
    """退场角色再出场必须被机械抓到"""
    r = _ledger_project(os.path.dirname(root), os.path.basename(root) + "_c1")
    rc, out = run([sys.executable, ".cursor/tools/check_continuity.py"], r)
    return rc != 0 and "dead-reappear" in out


def tc_continuity_exemption(root):
    """登记豁免后必须降级（否则同一非错误会被反复重报，工具最终被忽略）"""
    r = _ledger_project(os.path.dirname(root), os.path.basename(root) + "_c2", exempt=True)
    rc, out = run([sys.executable, ".cursor/tools/check_continuity.py"], r)
    return "已登记豁免" in out


def tc_continuity_no_ledger(root):
    """没有台账不得崩，且不得假通过为 🔴"""
    r = mini_project(os.path.dirname(root), os.path.basename(root) + "_c3")
    rc, out = run([sys.executable, ".cursor/tools/check_continuity.py"], r)
    return rc == 0 and "Traceback" not in out


TOOL_CASES = [
    ("check_manuscript：目标带单位仍被拦", tc_style_usnit),
    ("check_manuscript：目标无法解析按失败计", tc_style_notarget),
    ("check_manuscript：备注列伪造豁免失效", tc_style_fake_exempt),
    ("check_manuscript：--style --json 退码一致", tc_style_json),
    ("check_manuscript：空文件被拦", tc_empty_file),
    ("★ 评审校准：坏样本命中、好样本零 🔴", tc_calibration_separation),
    ("check_continuity：退场角色再出场被拦", tc_continuity_detects),
    ("check_continuity：豁免登记后降级", tc_continuity_exemption),
    ("check_continuity：无台账不崩不假报", tc_continuity_no_ledger),
    ("snapshot：diff 可作门禁（有差异退 1）", tc_snapshot_diff_gate),
    ("snapshot：回滚不完整退 1", tc_snapshot_restore_incomplete),
    ("build_export：未知格式退 2", tc_export_bad_format),
    ("build_export：控制字符下 EPUB 仍良构", tc_export_xml_ok),
    ("analyze_style：坏 JSON 优雅退 2", tc_analyze_bad_json),
]


def main():
    sandbox = tempfile.mkdtemp(prefix="novel-selftest-")
    ok = bad = 0
    print("守卫反向测试（投毒 → 期望守卫报警）\n")
    try:
        # 0) 基线：干净副本必须零错误
        cur = fresh(sandbox)
        rc, out = run([sys.executable, ".cursor/tools/check_integrity.py"], sandbox)
        baseline = rc == 0 and "✓ 无错误" in out
        print(f"  {'✓' if baseline else '✗'} 基线：干净副本自检通过（守卫不误报）")
        ok += baseline
        bad += 0 if baseline else 1

        # 1) check_integrity 的各类守卫
        for label, mutate, marker, least in INTEGRITY_CASES:
            cur = fresh(sandbox)
            try:
                mutate(cur)
                rc, out = run([sys.executable, ".cursor/tools/check_integrity.py"], sandbox)
                hits = out.count(marker)
                passed = rc != 0 and hits >= least
                note = f"{marker} × {hits}" if passed else f"未触发（rc={rc}, {marker}×{hits}）"
            except AssertionError as exc:
                passed, note = False, f"投毒失败：{exc}"
            print(f"  {'✓' if passed else '✗'} {label:<34} {note}")
            if VERBOSE and not passed:
                print("      " + out.strip().replace("\n", "\n      ")[:600])
            ok += passed
            bad += 0 if passed else 1

        # 2) 其它工具的门禁
        print()
        for label, body in TOOL_CASES:
            passed, note = tool_case(sandbox, re.sub(r"\W+", "_", label)[:40], body)
            print(f"  {'✓' if passed else '✗'} {label:<40} {note}")
            ok += passed
            bad += 0 if passed else 1
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    print(f"\n{'✓ 全部守卫按预期触发' if not bad else f'✗ {bad} 项守卫未触发（守卫失效 / 已回归）'}"
          f"  {ok}/{ok + bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
