#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_integrity.py · .cursor 工具链自检

用途：母版维护 / 回灌 / 复制到新书之后，验证 `.cursor/` 自身仍然自洽。
只依赖 Python 3 标准库。

用法：
    python3 .cursor/tools/check_integrity.py            # 在项目根或 .cursor/ 内运行均可
    python3 .cursor/tools/check_integrity.py --quiet     # 只输出问题

检查项（19 类守卫；每类都有 `selftest.py` 的投毒用例证明它**真的会响**）：
  1  规则 frontmatter     alwaysApply=true 不得带 globs；false 必须带 globs；globs 不得含 < >
  2  skill frontmatter    name/description/disable-model-invocation 齐备，name 与目录同名
  3  command frontmatter  name 与文件名一致，description 存在
  4  agent frontmatter    name 与文件名一致，description 存在
  5  断链引用             文本中引用的 .md/.mdc/.json/.py/.txt 路径必须可解析
  6  孤儿模板             templates/ 下每个模板都应被至少一处引用
  7  配置一致性           role.default / MAX_LOOPS / learn_dir / persona_id 四处对齐
  8  资产登记表交叉核对   00-novel-meta 登记的模板都在 templates/ 里存在
  9  工具语法             tools/*.py 可编译 + 敏感词示例表在位
 10  reference 体例       reference/*.md 无 frontmatter、首行为 `# 标题`
 11  类型工艺派发表        novel-genre 的 5 份参考「目录 ↔ 派发表」双向存在
 12  风格层三层一致       风格档模板 ↔ 原型库引用
 13  轴契约               `_axes` 声明 ↔ analyze_style.py 实际计算 + 单位可读
 14  上下文预算           必读表 ≤ 6 行（超即 ERROR）
 15  § 条款引用           `§X` 必须指向真实条款
 16  规则 glob 覆盖       登记资产须被语义对口的规则覆盖
 17  写—读配对            每个资产都要有读取方（防孤岛资产）
 18  根级文档真值         README/CHANGELOG：断链 · 工具清单 · 版本一致 · 重复行
 19  标点/轴名/阈值契约   两工具标点同口径 · 轴名与轴组数不漂移 · 阈值声明 ↔ 工具常量
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .cursor/
PROJECT = os.path.dirname(ROOT)                                     # 项目根

errors = []
warnings = []

# 项目侧（由工作流在项目里生成，母版中本就不存在）——引用它们不算断链
PROJECT_SIDE = (
    "主题/", "章节/", ".cursorGrowth/", ".dsh/growth/", ".dsh/",
    "build/", "dist/", "out/",
    "archive/", "check/", "learn/", "session/",
)
# 明确允许的根级文件
ROOT_FILES = ("CHANGELOG.md", "README.md", ".gitignore")
# 有意不存在的路径（母版明文禁止/仅为占位说明）
ALLOW_ABSENT = {"plan.md", "xxx.md"}
# 目录前缀（正文里用中文顿号/斜杠简写，不会出现在母版中）
SKIP_PREFIX = (".md", ".mdc", ".json", ".py", ".txt", ".sh", "xxx", "XX", "YY")

PATH_RE = re.compile(r"[`（(\s*|]([A-Za-z0-9_./<>\-]*\.(?:mdc|md|json|py|txt))")
SKIP_SUBSTR = ("<", ">", "*", "…", "NN", "MMDD", "YYYY", "X-Y", "vX.Y",
               "yyyy", "plugin", "http", "node_modules", "xxx", "XXX", "YY")
# 这些行里的文件名是工作流在 .cursorGrowth/ 下生成的，不算断链。
# ⚠ 只跳过**确实由工作流生成**的目录名，不要按行跳过——按行跳会连带放过同行真实断链。
SKIP_LINE_SUBSTR = (".cursorGrowth/", ".cursorGrowth`")


def rel(p):
    return os.path.relpath(p, PROJECT)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def parse_frontmatter(text):
    """返回 (dict, body)；无 frontmatter 返回 (None, text)。"""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    block = text[3:end]
    data = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        data[key.strip()] = val.strip()
    return data, text[end + 4:]


def walk(sub):
    base = os.path.join(ROOT, sub)
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in sorted(filenames):
            yield os.path.join(dirpath, name)


# ── 1. rules ────────────────────────────────────────────────────────────────
def check_rules():
    for path in walk("rules"):
        if not path.endswith(".mdc"):
            continue
        fm, _ = parse_frontmatter(read(path))
        if fm is None:
            errors.append(f"[frontmatter] {rel(path)}: 缺少 frontmatter")
            continue
        if "description" not in fm:
            errors.append(f"[frontmatter] {rel(path)}: 缺 description")
        always = fm.get("alwaysApply", "").lower()
        globs = fm.get("globs", "")
        if always == "true" and globs:
            errors.append(f"[frontmatter] {rel(path)}: alwaysApply:true 不应带 globs")
        if always == "false" and not globs:
            errors.append(f"[frontmatter] {rel(path)}: alwaysApply:false 却没有 globs（永不加载）")
        if always not in ("true", "false"):
            warnings.append(f"[frontmatter] {rel(path)}: alwaysApply 值异常：{always!r}")
        if "<" in globs or ">" in globs:
            errors.append(f"[frontmatter] {rel(path)}: globs 含字面尖括号，永远匹配不到 → {globs}")


# ── 2. skills ───────────────────────────────────────────────────────────────
def check_skills():
    base = os.path.join(ROOT, "skills")
    for entry in sorted(os.listdir(base)):
        skill = os.path.join(base, entry, "SKILL.md")
        if not os.path.isfile(skill):
            warnings.append(f"[skill] skills/{entry}/ 下没有 SKILL.md")
            continue
        fm, _ = parse_frontmatter(read(skill))
        if fm is None:
            errors.append(f"[skill] {rel(skill)}: 缺少 frontmatter")
            continue
        if fm.get("name") != entry:
            errors.append(f"[skill] {rel(skill)}: name={fm.get('name')!r} 与目录 {entry!r} 不一致")
        if not fm.get("description"):
            errors.append(f"[skill] {rel(skill)}: 缺 description")
        if "disable-model-invocation" not in fm:
            errors.append(f"[skill] {rel(skill)}: 缺 disable-model-invocation（约定：false）")


# ── 3/4. commands & agents ─────────────────────────────────────────────────
def check_commands():
    for path in walk("commands"):
        if not path.endswith(".md"):
            continue
        stem = os.path.basename(path)[:-3]
        fm, _ = parse_frontmatter(read(path))
        if fm is None:
            errors.append(f"[command] {rel(path)}: 缺少 frontmatter")
            continue
        if fm.get("name") != stem:
            errors.append(f"[command] {rel(path)}: name={fm.get('name')!r} 应为 {stem!r}")
        if not fm.get("description"):
            errors.append(f"[command] {rel(path)}: 缺 description")


def check_agents():
    for path in walk("agents"):
        if not path.endswith(".agent.md"):
            continue
        stem = os.path.basename(path)[: -len(".agent.md")]
        fm, _ = parse_frontmatter(read(path))
        if fm is None:
            errors.append(f"[agent] {rel(path)}: 缺少 frontmatter")
            continue
        if fm.get("name") != stem:
            errors.append(f"[agent] {rel(path)}: name={fm.get('name')!r} 应为 {stem!r}")
        if not fm.get("description"):
            errors.append(f"[agent] {rel(path)}: 缺 description")


# ── 5. 断链引用 ─────────────────────────────────────────────────────────────
def resolves(token, origin_dir):
    """返回 'ok' | 'rootfile'（项目根由工作流创建，允许暂缺）| 'missing'。无副作用。"""
    if token.startswith(PROJECT_SIDE):
        return "ok"
    if token in ALLOW_ABSENT:
        return "ok"
    # 已带 `.cursor/` 前缀 → 相对项目根解析
    if token.startswith(".cursor/"):
        return "ok" if os.path.exists(os.path.join(PROJECT, token)) else "missing"
    candidates = [
        os.path.join(origin_dir, token),                 # 同目录相对
        os.path.join(PROJECT, token),                    # 项目根
        os.path.join(ROOT, token),                       # .cursor/
        os.path.join(ROOT, "skills", token),             # 略去 skills/ 前缀
        os.path.join(ROOT, "skills", "novel-plan", token),
        os.path.join(ROOT, "skills", "novel-plot", token),
        os.path.join(ROOT, "commands", token),
        os.path.join(ROOT, "rules", token),
        os.path.join(ROOT, "templates", token),
        os.path.join(ROOT, "config", token),
        os.path.join(ROOT, "agents", token),
        os.path.join(ROOT, "tools", token),
        os.path.join(ROOT, "tools", "data", token),
    ]
    if any(os.path.exists(c) for c in candidates):
        return "ok"
    if token in ROOT_FILES:
        return "rootfile"
    return "missing"


def check_links():
    seen = set()
    warned_rootfile = set()
    for sub in ("rules", "skills", "commands", "agents", "config", "templates"):
        for path in walk(sub):
            if not path.endswith((".md", ".mdc", ".json")):
                continue
            origin_dir = os.path.dirname(path)
            for i, line in enumerate(read(path).splitlines(), 1):
                if any(s in line for s in SKIP_LINE_SUBSTR):
                    continue
                for token in PATH_RE.findall(line):
                    token = token.strip("`（）()|,;:")
                    if not token or token.startswith(SKIP_PREFIX):
                        continue
                    if any(s in token for s in SKIP_SUBSTR):
                        continue
                    if token.startswith(PROJECT_SIDE):
                        continue
                    if token in ALLOW_ABSENT:
                        continue
                    key = (token,)
                    if key in seen:
                        continue
                    status = resolves(token, origin_dir)
                    if status == "ok":
                        continue
                    if status == "rootfile":
                        if token not in warned_rootfile:
                            warned_rootfile.add(token)
                            warnings.append(
                                f"[link] {token}: 项目根尚无此文件（由工作流创建，非断链）")
                        continue
                    seen.add(key)
                    errors.append(
                        f"[link] {rel(path)}:{i}: 引用无法解析 → {token}"
                    )


# ── 6. 孤儿模板 ─────────────────────────────────────────────────────────────
def check_orphan_templates():
    text_cache = {}
    for path in list(walk("rules")) + list(walk("skills")) + list(walk("commands")) + list(walk("agents")):
        if path.endswith((".md", ".mdc")):
            text_cache[path] = read(path)
    config_readme = os.path.join(ROOT, "config", "README.md")
    if os.path.isfile(config_readme):
        text_cache[config_readme] = read(config_readme)
    for path in walk("templates"):
        if not path.endswith((".md", ".json")):
            continue
        base = os.path.basename(path)
        if base == "README.md":
            continue
        if any(base in body for body in text_cache.values()):
            continue
        warnings.append(f"[template] {rel(path)}: 没有任何 rule/skill/command/agent 引用（孤儿模板）")


# ── 7. 配置一致性 ───────────────────────────────────────────────────────────
def check_config():
    wf_path = os.path.join(ROOT, "config", "workflow.json")
    roles_path = os.path.join(ROOT, "config", "roles.json")
    plan_tpl = os.path.join(ROOT, "templates", "plan.md")
    persona_tpl = os.path.join(ROOT, "templates", "session", "persona.json")
    for p in (wf_path, roles_path, plan_tpl, persona_tpl):
        if not os.path.isfile(p):
            errors.append(f"[config] 缺少 {rel(p)}")
            return
    try:
        wf = json.loads(read(wf_path))
        roles = json.loads(read(roles_path))
        persona = json.loads(read(persona_tpl))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"[config] JSON 解析失败：{exc}")
        return

    role_default = wf.get("role", {}).get("default")
    if role_default != roles.get("default"):
        errors.append(
            f"[config] workflow.role.default={role_default!r} != roles.default={roles.get('default')!r}"
        )
    ids = {p.get("id") for p in roles.get("personas", [])}
    if role_default not in ids:
        errors.append(f"[config] role.default={role_default!r} 不在 roles.json personas[].id 中")
    if persona.get("persona_id") != role_default:
        errors.append(
            f"[config] templates/session/persona.json persona_id={persona.get('persona_id')!r} "
            f"应为默认 {role_default!r}"
        )

    loops = wf.get("autonomous", {}).get("max_loops_default")
    plan_text = read(plan_tpl)
    m = re.search(r"<!--\s*MAX_LOOPS:\s*(\d+)", plan_text)
    if not m:
        errors.append("[config] templates/plan.md 缺 MAX_LOOPS 头部字段")
    elif int(m.group(1)) != loops:
        errors.append(f"[config] plan 模板 MAX_LOOPS={m.group(1)} != workflow {loops}")

    plan_fields = set(re.findall(r"<!--\s*([A-Z_]+):", plan_text))
    required = {"PLANNING", "SPRINT", "PLAN_APPROVED", "AUTONOMOUS",
                "SPRINT_STATUS", "ACTIVE", "NEXT", "LAST_DONE", "MAX_LOOPS"}
    missing = required - plan_fields
    if missing:
        errors.append(f"[config] plan 模板缺头部字段：{sorted(missing)}")

    # 值行必须是纯值：不得混入说明文字（否则闸门读到的是说明而非 true/false）
    for name, value in re.findall(r"<!--\s*([A-Z_]+):\s*([^\n]*?)-->", plan_text):
        if name not in required:
            continue
        if any(ch in value for ch in "|→<>"):
            errors.append(
                f"[config] plan 头部 {name} 的值行混入说明：{value.strip()!r}（应只写当前值）"
            )

    learn_dir = wf.get("growth", {}).get("learn_dir")
    learn_skill = os.path.join(ROOT, "skills", "novel-learn", "SKILL.md")
    if os.path.isfile(learn_skill) and learn_dir not in read(learn_skill):
        warnings.append(f"[config] growth.learn_dir={learn_dir!r} 未出现在 novel-learn skill 中")


# ── 8. 资产登记表交叉核对 ───────────────────────────────────────────────────
def check_asset_registry():
    meta = os.path.join(ROOT, "rules", "00-novel-meta.mdc")
    if not os.path.isfile(meta):
        errors.append("[assets] 缺 rules/00-novel-meta.mdc")
        return
    text = read(meta)
    for tpl in sorted(set(re.findall(r"`?(templates/[A-Za-z0-9_./\-]+\.(?:md|json))`?", text))):
        if not os.path.exists(os.path.join(ROOT, tpl)):
            errors.append(f"[assets] 资产登记表引用了不存在的模板 → {tpl}")
    # 关键项目资产必须出现在登记表里
    for asset in ("主题/通用约束.md", "主题/伏笔板.md", "主题/节奏窗.md",
                  "主题/章节卡/", "主题/人物关系矩阵.md", "主题/节拍表.md",
                  "主题/POV台账.md", "主题/敏感词表.md", "主题/分卷/"):
        if asset not in text:
            errors.append(f"[assets] 资产登记表缺关键资产 → {asset}")


# ── 9. tools/ 自检 ─────────────────────────────────────────────────────────
def check_tools():
    tools_dir = os.path.join(ROOT, "tools")
    if not os.path.isdir(tools_dir):
        errors.append("[tools] 缺 tools/ 目录")
        return
    names = [f for f in sorted(os.listdir(tools_dir)) if f.endswith(".py")]
    if not names:
        errors.append("[tools] tools/ 下没有任何 .py")
    for n in names:
        p = os.path.join(tools_dir, n)
        try:
            compile(read(p), p, "exec")       # 只做语法检查，不落 .pyc
        except SyntaxError as exc:
            errors.append(f"[tools] {n} 语法错误：{exc}")
    # 敏感词示例数据文件必须在位（被 check_manuscript 回退引用）
    ex = os.path.join(tools_dir, "data", "sensitive-words.example.txt")
    if not os.path.isfile(ex):
        errors.append("[tools] 缺 tools/data/sensitive-words.example.txt（check_manuscript 的回退词表）")
    # `tools/` 随母版**复制给每一本新书**：带上 .pyc/__pycache__ 会污染下游项目。
    # （`compile()` 只做语法检查、不落盘，就是为了不产生它；本地手跑 py_compile 会。）
    for dirpath, dirnames, filenames in os.walk(tools_dir):
        if "__pycache__" in dirnames:
            errors.append(f"[tools] {rel(os.path.join(dirpath, '__pycache__'))}/ 不应留在母版"
                          f"（随 .cursor/ 分发会带到新书项目；已加入 .gitignore）")
        for fn in filenames:
            if fn.endswith(".pyc"):
                errors.append(f"[tools] {rel(os.path.join(dirpath, fn))} 不应留在母版")


# ── 10. reference 文件体例 ──────────────────────────────────────────────────
def check_references():
    for sub in os.listdir(os.path.join(ROOT, "skills")):
        ref_dir = os.path.join(ROOT, "skills", sub, "reference")
        if not os.path.isdir(ref_dir):
            continue
        for fn in sorted(os.listdir(ref_dir)):
            if not fn.endswith(".md"):
                continue
            p = os.path.join(ref_dir, fn)
            text = read(p)
            if text.startswith("---"):
                errors.append(f"[reference] {rel(p)}: reference 文件不应有 frontmatter")
            if not text.lstrip().startswith("# "):
                errors.append(f"[reference] {rel(p)}: 首行应为 `# 标题`")


# ── 11. novel-genre 派发表完整性 ────────────────────────────────────────────
def check_genre_coverage():
    skill = os.path.join(ROOT, "skills", "novel-genre", "SKILL.md")
    ref_dir = os.path.join(ROOT, "skills", "novel-genre", "reference")
    if not os.path.isfile(skill):
        return
    if not os.path.isdir(ref_dir):
        errors.append("[genre] novel-genre 有 SKILL.md 但没有 reference/")
        return
    body = read(skill)
    for fn in sorted(os.listdir(ref_dir)):
        if fn.endswith(".md") and fn not in body:
            errors.append(f"[genre] skills/novel-genre/reference/{fn} 未出现在 SKILL.md 派发表中")
    # 反向：SKILL.md 点名了某份 reference，磁盘上就必须有（否则派发表是假的）
    for name in sorted(set(re.findall(r"reference/([a-z0-9-]+\.md)", body))):
        if not os.path.isfile(os.path.join(ref_dir, name)):
            errors.append(f"[genre] SKILL.md 点名了 reference/{name}，但该文件不存在")


# ── 12. 条款号（§）引用有效性 ───────────────────────────────────────────────
CN = "一二三四五六七八九十"
CLAUSE_RE = re.compile(r"§\s*([0-9]+\.[0-9]+|[0-9]+|[" + CN + r"]+)")


def _section_index(path):
    """返回 (中文节号集合, 形如 '3.1' 的子节号集合, 阿拉伯节号集合)。"""
    text = read(path)
    cn_secs = set(re.findall(r"^##\s*([" + CN + r"]+)\s*、", text, re.M))
    arab_secs = set(re.findall(r"^#{2,3}\s*([0-9]+)[．.、]", text, re.M))
    subs = set(re.findall(r"^#{2,4}\s*([0-9]+\.[0-9]+)", text, re.M))
    return cn_secs, subs, arab_secs


def asset_template_map():
    """从资产登记表建 `主题/X.md` → 母版模板文件 的映射，用于校验指向项目资产的 § 引用。"""
    meta = os.path.join(ROOT, "rules", "00-novel-meta.mdc")
    out = {}
    if not os.path.isfile(meta):
        return out
    for line in read(meta).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        am = re.search(r"`((?:主题|\.cursorGrowth)/[^`]+)`", cells[1])
        tm = re.search(r"`((?:templates|tools)/[^`]+)`", cells[4])
        if not (am and tm):
            continue
        key = re.sub(r"<[^>]*>", "", am.group(1))
        tpl = os.path.join(ROOT, tm.group(1))
        if os.path.isfile(tpl):
            out[key] = tpl
    return out


def rule_prefix_map():
    """规则的数字前缀 → 文件（如 02 → 02-novel-plot-design.mdc）；前缀不唯一则剔除。"""
    out, dup = {}, set()
    for path in walk("rules"):
        b = os.path.basename(path)
        m = re.match(r"^(\d{2})-", b)
        if not m:
            continue
        key = m.group(1)
        if key in out:
            dup.add(key)
        out[key] = path
    return {k: v for k, v in out.items() if k not in dup}


def check_clause_citations():
    """找出指向不存在条款的 § 引用。仅在同行能唯一确定被引文件时才判定，避免误报。"""
    base_targets = {}
    for sub in ("rules", "templates", "skills", "commands", "agents"):
        for path in walk(sub):
            if path.endswith((".md", ".mdc")):
                base_targets[os.path.basename(path)] = path
    amap = asset_template_map()
    pref = rule_prefix_map()

    for sub in ("rules", "templates", "skills", "commands", "agents"):
        for path in walk(sub):
            if not path.endswith((".md", ".mdc")):
                continue
            self_base = os.path.basename(path)
            self_text = read(path)
            self_cn, self_subs, self_arab = _section_index(path)
            for i, line in enumerate(self_text.splitlines(), 1):
                clauses = CLAUSE_RE.findall(line)
                if not clauses:
                    continue
                cands = {}
                for key, tpl in amap.items():
                    if key in line:
                        cands[key] = tpl
                for b, p in base_targets.items():
                    if b != self_base and b in line and b not in cands:
                        cands[b] = p
                # 规则简写：`02 §七` / `01 §二.3`
                for pfx, p in pref.items():
                    if re.search(r"(?<![\d])" + pfx + r"(?![\d-])", line):
                        cands.setdefault(os.path.basename(p), p)
                if len(cands) != 1:
                    continue
                name, tgt = next(iter(cands.items()))
                if not os.path.isfile(tgt):
                    continue
                cn_secs, subs, arab = _section_index(tgt)
                for c in clauses:
                    ok = (c in subs) or (c in cn_secs) or (c in arab)
                    if not ok and "." in c and c.split(".")[0] in cn_secs:
                        ok = True
                    # 指本文自身必须写明（如「见本文 §5」），否则视为对被引文件的引用：
                    # 宁可报出来让作者写清楚，也不要放过真正的悬空引用。
                    if not ok and re.search(r"(本文|本文件|本节)[^。\n]{0,4}§\s*" + re.escape(c), line):
                        ok = True
                    if not ok:
                        errors.append(
                            f"[clause] {rel(path)}:{i}: 引用了 {name} 中不存在的条款 §{c}"
                        )


# ── 13. 资产 ↔ 规则 globs 覆盖 ──────────────────────────────────────────────
# 关键资产必须有「语义对口」的规则覆盖，而不只是被某条泛规则扫到
EXPECTED_OWNER = {
    "主题/风格档.md": "05-novel-style.mdc",
    "主题/节拍表.md": "02-novel-plot-design.mdc",
    "主题/分卷/": "02-novel-plot-design.mdc",
    "主题/POV台账.md": "02-novel-plot-design.mdc",
    "主题/章节卡/": "02-novel-plot-design.mdc",
    "主题/人物/": "03-novel-character.mdc",
    "主题/世界观.md": "04-novel-worldbuilding.mdc",
    "主题/主线剧情.md": "02-novel-plot-design.mdc",
    "主题/伏笔板.md": "02-novel-plot-design.mdc",
}


def _glob_match(pat, path):
    rx = re.escape(pat.strip())
    rx = rx.replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(rx, path) is not None


def check_rule_glob_coverage():
    meta = os.path.join(ROOT, "rules", "00-novel-meta.mdc")
    if not os.path.isfile(meta):
        return
    # 从资产登记表取「优先」列里的 主题/ 资产（去掉占位符）
    assets = set()
    for line in read(meta).splitlines():
        if not line.strip().startswith("|"):
            continue
        for m in re.finditer(r"`(主题/[^`]+)`", line):
            a = m.group(1)
            a = re.sub(r"<[^>]*>", "", a)
            if a.endswith(".md"):
                assets.add(a)
            elif a.endswith("/"):
                assets.add(a + "x.md")
    if not assets:
        return
    globs = {}
    for path in walk("rules"):
        if not path.endswith(".mdc"):
            continue
        m = re.search(r"^globs:\s*(.+)$", read(path), re.M)
        if m:
            globs[os.path.basename(path)] = [p.strip() for p in m.group(1).split(",")]
    for a in sorted(assets):
        matchers = [f for f, pats in globs.items() if any(_glob_match(p, a) for p in pats)]
        if not matchers:
            errors.append(f"[glob] 资产 {a} 不被任何规则的 globs 覆盖（规则不会自动附着）")
            continue
        owner = EXPECTED_OWNER.get(a) or EXPECTED_OWNER.get(a.rsplit("/", 1)[0] + "/")
        if owner and owner not in matchers:
            errors.append(
                f"[glob] 资产 {a} 未被语义对口的规则 {owner} 覆盖（现仅 {', '.join(matchers)}）"
            )


# 非指标的内部字段（用于把「实现侧多余键」排除出反向比对）
BOOKKEEPING_KEYS = {"chars", "sentences", "paragraphs", "sense_distribution"}

# ── 14a. 上下文预算守卫（防"读取清单无限膨胀"）──────────────────────────────
BUDGET_MAX_REQUIRED = 6      # novel-chapter「必读」表的行数上限


def check_context_budget():
    p = os.path.join(ROOT, "skills", "novel-chapter", "SKILL.md")
    if not os.path.isfile(p):
        return
    text = read(p)
    m = re.search(r"^##\s*动笔前必读.*?$", text, re.M)
    if not m:
        warnings.append("[budget] novel-chapter 缺「动笔前必读」小节")
        return
    rows = 0
    for line in text[m.end():].splitlines():
        if line.strip().startswith("###") or line.strip().startswith("## "):
            break
        if line.strip().startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", line.strip()):
            cs = [c.strip() for c in line.strip().strip("|").split("|")]
            if cs and cs[0] in ("源（必读）", "源") or cs[0].startswith("`"):
                rows += 1
    if rows > BUDGET_MAX_REQUIRED:
        errors.append(
            f"[budget] novel-chapter「必读」表 {rows} 行 > 上限 {BUDGET_MAX_REQUIRED}"
            "（读取预算会失控：加行前先问『不读它，本章会具体错在哪』，否则移入「按需」）")
    elif rows == BUDGET_MAX_REQUIRED:
        warnings.append(f"[budget] 必读表已达上限 {rows} 行 —— 下次再加就必须先移出一项")


# ── 14b. 风格指标契约：`_axes` 声明 ↔ analyze_style 实现 ─────────────────────
UNIT_OK = re.compile(r"[汉字个次%比段通道比值字]")


def check_axis_contract():
    """`style-archetypes.json` 声明的每个轴，必须真的被 analyze_style.py 计算；
    且单位串必须是可读的中文计量（防止写「光年/平方秒」这类假单位）。"""
    json_p = os.path.join(ROOT, "tools", "data", "style-archetypes.json")
    ast_p = os.path.join(ROOT, "tools", "analyze_style.py")
    if not (os.path.isfile(json_p) and os.path.isfile(ast_p)):
        errors.append("[axis] 缺 style-archetypes.json 或 analyze_style.py")
        return
    try:
        data = json.loads(read(json_p))
    except json.JSONDecodeError as exc:
        errors.append(f"[axis] style-archetypes.json 解析失败：{exc}")
        return
    declared = set(data.get("_axes", {}))
    src = read(ast_p)
    # 只在 analyze() 函数体内取指标键（否则会把 main() 的输出字典也当成指标）
    fn = re.search(r"def analyze\(.*?(?=\ndef |\Z)", src, re.S)
    body = fn.group(0) if fn else src
    computed = set(re.findall(r'"([a-z0-9_]{3,})"\s*:', body))
    computed |= set(re.findall(r'm\["([a-z0-9_]{3,})"\]\s*=', body))
    computed -= BOOKKEEPING_KEYS
    for k in sorted(declared - computed):
        errors.append(f"[axis] `_axes` 声明了 {k}，但 analyze_style.py 从未计算它（声明与实现漂移）")
    for k in sorted(computed - declared):
        errors.append(f"[axis] analyze_style.py 计算了 {k}，但 `_axes` 未声明（无单位/无文档）")
    for k, meta in data.get("_axes", {}).items():
        unit = str(meta.get("unit", ""))
        if not unit:
            errors.append(f"[axis] {k} 缺 unit")
        elif not UNIT_OK.search(unit):
            errors.append(f"[axis] {k} 的 unit 可疑：`{unit}`（应为可读的中文计量）")


# ── 15. 风格层三层一致性（JSON ↔ reference ↔ SKILL 派发表）────────────────
def check_style_layer():
    data_p = os.path.join(ROOT, "tools", "data", "style-archetypes.json")
    skill_p = os.path.join(ROOT, "skills", "novel-style", "SKILL.md")
    ref_dir = os.path.join(ROOT, "skills", "novel-style", "reference")
    if not os.path.isfile(data_p):
        errors.append("[style] 缺 tools/data/style-archetypes.json")
        return
    try:
        data = json.loads(read(data_p))
    except json.JSONDecodeError as exc:
        errors.append(f"[style] style-archetypes.json 解析失败：{exc}")
        return
    arch = data.get("archetypes", {})
    if not arch:
        errors.append("[style] style-archetypes.json 无 archetypes")
        return
    skill_text = read(skill_p) if os.path.isfile(skill_p) else ""
    if not skill_text:
        errors.append("[style] 缺 skills/novel-style/SKILL.md")
    refs = sorted(os.listdir(ref_dir)) if os.path.isdir(ref_dir) else []
    if not refs:
        errors.append("[style] 缺 skills/novel-style/reference/")
        return

    for pid, a in arch.items():
        rel_ref = a.get("reference", "")
        base = os.path.basename(rel_ref)
        # JSON 里的 reference 相对 `.cursor/` 写；也容忍相对项目根
        if not (os.path.isfile(os.path.join(ROOT, rel_ref))
                or os.path.isfile(os.path.join(PROJECT, rel_ref))):
            errors.append(f"[style] 原型 {pid} 的 reference 不存在 → {rel_ref}")
        if base and base not in skill_text:
            errors.append(f"[style] {base} 未出现在 novel-style/SKILL.md 派发表中")
        if not a.get("targets"):
            errors.append(f"[style] 原型 {pid} 缺 targets")
        if not a.get("exemptions"):
            warnings.append(f"[style] 原型 {pid} 未声明任何 exemption（可接受，但请确认）")
        for key in a.get("targets", {}):
            if key not in data.get("_axes", {}):
                errors.append(f"[style] 原型 {pid} 的目标 {key} 未在 _axes 定义")
    # 反向：reference 目录里有没有 JSON 未登记的原型文件
    declared = {os.path.basename(a.get("reference", "")) for a in arch.values()}
    for fn in refs:
        if fn.endswith(".md") and fn not in declared:
            warnings.append(f"[style] reference/{fn} 未在 style-archetypes.json 登记")


# ── 14. 写—读配对（防止"只写不读"的孤岛资产）──────────────────────────────
# 允许"无 skill 读取方"的资产：人读交付物 / 过程笔记 / 有意只读
ALLOW_NO_READER = {
    "主题/推介包.md": "人读交付物（终局外发，无工具读取）",
    "主题/敏感词表.md": "由用户维护、由 tools/check_manuscript.py 读取",
    "主题/_meta/": "旧路径回退，只读不改（00-novel-meta 明令禁止再写入）",
    ".cursorGrowth/learn/craft-notes/": "过程笔记，收尾由 /nlearn 并入 writing-voice/rhythm",
    ".cursorGrowth/archive/": "归档由 snapshot/restore 与 /nlog 消费，非 skill 读取",
    ".cursorGrowth/session/persona.json": "由 rules/07 读取（alwaysApply，不属 skill）",
}


def _registry_assets():
    """从资产登记表取 (优先路径, 创建者) 列表，已去占位符。"""
    meta = os.path.join(ROOT, "rules", "00-novel-meta.mdc")
    out = []
    if not os.path.isfile(meta):
        return out
    for line in read(meta).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        m = re.search(r"`((?:主题|\.cursorGrowth)/[^`]+)`", cells[1])
        if not m:
            continue
        asset = re.sub(r"<[^>]*>", "", m.group(1))
        out.append((asset, cells[3]))
    return out


def _asset_needles(asset):
    """从资产路径推出用于找读者的「关键词」。完全由占位符构成者返回空 = 跳过。

    优先级：够长的中文尾段（章前卡/节前卡/场景卡/节奏窗）＞ 英文名（logline）
    ＞ 目录名（分卷 —— 该行文件名除去占位符只剩「第卷」，不足以匹配）。
    """
    stripped = re.sub(r"<[^>]*>", "", asset)
    base = os.path.basename(stripped)
    stem = re.sub(r"\.md$", "", base).strip("_ ")
    dirname = os.path.basename(os.path.dirname(stripped)).strip()
    toks = [t for t in re.split(r"[_\d]+", stem)
            if len(t) >= 2 and re.search(r"[\u4e00-\u9fff]", t)]
    if toks and len(toks[-1]) >= 3:
        return {toks[-1]}                      # 章前卡 / 节前卡 / 场景卡 …
    if stem and len(stem) >= 3 and not toks:
        return {stem}                          # logline / POV台账 …
    if dirname and dirname != "主题":
        return {dirname}                       # 分卷 / 章节卡 …
    return {stem} if len(stem) >= 3 else set()


def check_write_read_pairs():
    """每个登记的 `主题/` 资产，至少要有 1 个「非创建者」的读取方。

    只查 `主题/` 内容层：这是"写了没人读 = 白写"最容易发生的地方。
    """
    for asset, creator in _registry_assets():
        if not asset.startswith("主题/"):
            continue
        if asset in ALLOW_NO_READER or any(
                asset.startswith(k) for k in ALLOW_NO_READER if k.endswith("/")):
            continue
        needles = _asset_needles(asset)
        if not needles:
            continue
        owner_tokens = re.findall(r"[a-z][a-z-]{3,}", creator)
        readers = set()
        for sub in ("skills", "commands", "agents", "rules"):
            for path in walk(sub):
                if not path.endswith((".md", ".mdc")):
                    continue
                p = rel(path)
                if p.endswith("00-novel-meta.mdc"):
                    continue
                if any(f"skills/{t}/" in p for t in owner_tokens):
                    continue          # 创建者自己不算
                text = read(path)
                if any(n in text for n in needles):
                    readers.add(p)
        if not readers:
            errors.append(
                f"[write-read] 资产 {asset} 没有任何非创建者的读取方"
                f"（创建者：{creator or '未标注'}；关键词 {sorted(needles)}；写了没人读 = 白写）"
            )

    # learn/ 四件套额外加固（历史上出过问题）
    readers = {}
    for sub in ("skills", "commands"):
        for path in walk(sub):
            if not path.endswith((".md", ".mdc")):
                continue
            p = rel(path)
            text = read(path)
            for name in ("writing-voice.md", "rhythm.md", "decisions.md", "acceptance.md"):
                if f"learn/{name}" in text:
                    readers.setdefault(name, set()).add(p)
    for name, who in sorted(readers.items()):
        external = {w for w in who if "novel-learn/" not in w}
        if len(external) < 2:
            errors.append(
                f"[write-read] learn/{name} 只被 {sorted(external) or '「无」'} 读取（需要 ≥2 个非 novel-learn 的读取方）"
            )


# ── 16. 根级文档真值（README / CHANGELOG）──────────────────────────────────
# 此前自检只走 `.cursor/`，而母版**对外**的承诺（工具清单、计数、版本、
# "改完怎么验"）全写在仓库根两份文档里，一处守卫都没有。
DUP_MIN_LEN = 25          # 短行（表格分隔、`---`、空标题）重复是正常的
VERSION_RE = re.compile(r"当前：\*\*(v[\d.]+)\*\*")
CHLOG_VER_RE = re.compile(r"^##\s*\[(v[\d.]+)\]", re.M)


def _resolves_root(token, origin_dir):
    """根文档专用解析：先走通用 resolves，再按 basename 全树兜底。

    根文档正文常用不带路径的短名（如 `comedy-craft.md`），而 CHANGELOG 里的
    `xxx.md→yyy.md` 是**改名记录**——只在最新条目上做断链检查（见 check_root_docs）。
    """
    if resolves(token, origin_dir) != "missing":
        return "ok"
    if "/" not in token:
        for _dp, _dn, fns in os.walk(ROOT):
            if token in fns:
                return "ok"
    return "missing"


def _current_section(lines):
    """CHANGELOG 只检查**最新一条**：历史条目是"当时发生过什么"的记录，
    里面天然含有已被改名/删除的旧路径（如 `xxx.md→yyy.md`），
    用今天的文件系统去判它就是假阳性，还会逼人改写历史。"""
    seen = 0
    for i, line in enumerate(lines):
        if line.startswith("## ["):
            seen += 1
            if seen == 2:
                return lines[:i]
    return lines


def check_root_docs():
    """① 断链 ② 工具清单覆盖 ③ 版本一致 ④ 全等重复行。"""
    readme_p = os.path.join(PROJECT, "README.md")
    if not os.path.isfile(readme_p):
        return                      # 消费方书项目没有母版 README 属正常
    chlog_p = os.path.join(PROJECT, "CHANGELOG.md")
    docs = [(readme_p, "README.md", read(readme_p).splitlines())]
    if os.path.isfile(chlog_p):
        docs.append((chlog_p, "CHANGELOG.md", _current_section(read(chlog_p).splitlines())))
    cur_readme_p = os.path.join(ROOT, "README.md")

    # ① 断链：根文档里引用的文件必须能解析（含 `.cursor/...` 与裸文件名）
    for _path, label, lines in docs:
        for i, line in enumerate(lines, 1):
            if any(s in line for s in SKIP_LINE_SUBSTR):
                continue
            for token in PATH_RE.findall(line):
                token = token.strip("`（）()|,;:")
                if not token or token.startswith(SKIP_PREFIX):
                    continue
                if any(s in token for s in SKIP_SUBSTR):
                    continue
                if _resolves_root(token, PROJECT) == "missing":
                    errors.append(f"[root-docs] {label}:{i}: 引用无法解析 → {token}")

    # ② 工具清单覆盖：新加工具而两处清单没跟上 = 文档债
    tools = sorted(f for f in os.listdir(os.path.join(ROOT, "tools")) if f.endswith(".py"))
    readme_text = read(readme_p)
    cur_text = read(cur_readme_p) if os.path.isfile(cur_readme_p) else ""
    for f in tools:
        if f not in readme_text:
            errors.append(f"[root-docs] 根 README 未登记新工具 tools/{f}（清单漂移）")
        if cur_text and f not in cur_text:
            errors.append(f"[root-docs] .cursor/README.md 未登记新工具 tools/{f}（清单漂移）")

    # ③ 版本一致：README 声明 == CHANGELOG 首条（git tag 缺失只警告）
    m = VERSION_RE.search(readme_text)
    if not m:
        errors.append("[root-docs] 根 README 缺「当前：**vX.Y.Z**」版本声明")
    elif os.path.isfile(chlog_p):
        mc = CHLOG_VER_RE.search(read(chlog_p))
        if not mc:
            errors.append("[root-docs] CHANGELOG 缺 `## [vX.Y.Z]` 首条版本")
        elif mc.group(1) != m.group(1):
            errors.append(f"[root-docs] 版本不一致：README {m.group(1)} != CHANGELOG {mc.group(1)}")
        elif os.path.isdir(os.path.join(PROJECT, ".git")):
            import subprocess
            try:
                got = subprocess.run(["git", "tag", "-l", m.group(1)], cwd=PROJECT,
                                     capture_output=True, text=True, timeout=10)
                if not got.stdout.strip():
                    warnings.append(
                        f"[root-docs] 版本 {m.group(1)} 尚无 git tag（提交时应同步打 tag）")
            except Exception:       # noqa: BLE001  缺 git / 超时都不该中断自检
                pass

    # ④ 全等重复行：复制粘贴事故（如 README 里同一条命令出现两次）
    for _path, label, lines in docs:
        seen = {}
        for i, line in enumerate(lines, 1):
            s = line.strip()
            if len(s) < DUP_MIN_LEN or s[0] in "#|>-":
                continue
            if s in seen:
                errors.append(f"[root-docs] {label}:{i}: 与第 {seen[s]} 行完全重复 → {s[:40]}…")
            else:
                seen[s] = i


# ── 17. 标点变体归一契约（check_manuscript ↔ analyze_style）──────────────
PUNCT_KEYS = ("DASH_PAT", "ELLIPSIS_PAT")


def check_punct_contract():
    """同一段文本，写作闸门与风格指纹必须得到同一个「用了几次」。

    两个工具都是可直接单跑的脚本、不共享模块，所以标点模式是各自定义的字面量，
    会漂移。它**已经漂移过**：`analyze_style` 认 `...` 算省略号，`check_manuscript`
    不认 —— 同一份样本，指纹说「省略号 8 次/千字」，闸门报 0 处。
    """
    pats = {}
    for tool in ("check_manuscript.py", "analyze_style.py"):
        p = os.path.join(ROOT, "tools", tool)
        if not os.path.isfile(p):
            errors.append(f"[punct] 缺 tools/{tool}")
            return
        src = read(p)
        for key in PUNCT_KEYS:
            m = re.search(rf'^{key}\s*=\s*(?:re\.compile\()?r"([^"]+)"', src, re.M)
            if not m:
                errors.append(f"[punct] tools/{tool} 找不到 {key} 的字面量（守卫无法比对）")
                continue
            pats.setdefault(key, {})[tool] = m.group(1)
    for key, got in pats.items():
        if len(set(got.values())) > 1:
            errors.append(
                f"[punct] {key} 两处口径不一致："
                + "；".join(f"{t}={v}" for t, v in sorted(got.items()))
                + "（写作闸门与风格指纹必须同口径）")


# ── 18. 风格轴名 / 轴组声明（正文 ↔ `_axes` 真源）──────────────────────────
AXIS_CLAIM_RE = re.compile(r"(\d+)\s*轴组\s*/\s*(\d+)\s*项")
AXIS_TOKEN_RE = re.compile(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`")


def check_axis_refs():
    """① 参考文档里反引号包着的轴名必须真在 `_axes` 里；
       ② 「N 轴组 / M 项」的声明必须与 `_axes` 实际数量一致。

    为什么需要：`[axis]` 只比对 JSON ↔ analyze_style.py，**正文是盲区**。
    已实证：`cold-minimal.md` 写 `first_ratio`（真名 `first_person_ratio`）、
    20 处正文把 8 个轴组说成「8 轴」，而机器真源是 8 组 / 20 项。
    """
    json_p = os.path.join(ROOT, "tools", "data", "style-archetypes.json")
    if not os.path.isfile(json_p):
        return
    try:
        axes = json.loads(read(json_p)).get("_axes", {})
    except json.JSONDecodeError:
        return                      # 解析失败已由 [axis] 报，不重复
    if not axes:
        return
    groups = {v.get("axis") for v in axes.values() if v.get("axis")}
    style_dir = os.path.join(ROOT, "skills", "novel-style")

    for dirpath, _dirnames, filenames in os.walk(ROOT):
        for fn in sorted(filenames):
            if not fn.endswith((".md", ".mdc")):
                continue
            path = os.path.join(dirpath, fn)
            for i, line in enumerate(read(path).splitlines(), 1):
                if os.path.commonpath([path, style_dir]) == style_dir:
                    for tok in AXIS_TOKEN_RE.findall(line):
                        if tok not in axes:
                            errors.append(
                                f"[axis-ref] {rel(path)}:{i}: `{tok}` 不是 `_axes` 里的轴名"
                                f"（正文与机器真源漂移）")
                for g, n in AXIS_CLAIM_RE.findall(line):
                    if int(g) != len(groups) or int(n) != len(axes):
                        errors.append(
                            f"[axis-ref] {rel(path)}:{i}: 写「{g} 轴组 / {n} 项」，"
                            f"真源是 {len(groups)} 组 / {len(axes)} 项")


# ── 19. 阈值契约（声明真源 ↔ 工具常量）────────────────────────────────────
# `主题/通用约束.md` 自称"本项目唯一的阈值真源"，但这些数字原先**只活在代码里**。
# 双向比对：
#   ① 契约表每个键 → 工具常量必须存在且数值相等（改工具不改模板 → ERROR）；
#   ② 工具每个阈值常量 → 契约表必须登记（隐形阈值 → ERROR）。
THRESHOLD_CONTRACT = (
    ("bold_warn", "check_manuscript.py", "DEFAULTS:bold_warn"),
    ("bold_fail", "check_manuscript.py", "DEFAULTS:bold_fail"),
    ("sec_target_min", "check_manuscript.py", "DEFAULTS:sec_target_min"),
    ("sec_target_max", "check_manuscript.py", "DEFAULTS:sec_target_max"),
    ("sec_hard_max", "check_manuscript.py", "DEFAULTS:sec_hard_max"),
    ("long_sentence", "check_manuscript.py", "DEFAULTS:long_sentence"),
    ("short_sentence", "check_manuscript.py", "DEFAULTS:short_sentence"),
    ("short_run", "check_manuscript.py", "DEFAULTS:short_run"),
    ("dash_max", "check_manuscript.py", "DEFAULTS:dash_max"),
    ("ellipsis_max", "check_manuscript.py", "DEFAULTS:ellipsis_max"),
    ("exclaim_max", "check_manuscript.py", "DEFAULTS:exclaim_max"),
    ("soft_tic_per_kchar", "check_manuscript.py", "CONST:SOFT_TIC_PER_KCHAR"),
    ("sentence_cv_min", "check_manuscript.py", "CONST:SENTENCE_CV_MIN"),
    ("short_per_100", "check_manuscript.py", "CONST:SHORT_PER_100"),
    ("quota_per_chapter", "check_continuity.py", "CONST:QUOTA_PER_CHAPTER"),
    ("fast_streak_trigger", "check_continuity.py", "CONST:FAST_STREAK"),
    ("absent_max", "check_continuity.py", "CONST:ABSENT_MAX"),
    ("cooldown_conflict_thrill", "check_continuity.py", "COOLDOWN:冲突刺激"),
    ("cooldown_bond_deepening", "check_continuity.py", "COOLDOWN:关系深化"),
    ("cooldown_faction_building", "check_continuity.py", "COOLDOWN:势力经营"),
    ("cooldown_world_painting", "check_continuity.py", "COOLDOWN:世界观铺陈"),
    ("cooldown_tension_escalation", "check_continuity.py", "COOLDOWN:张力升级"),
)
CONTRACT_TABLE = os.path.join("templates", "constraints.md")
CONTRACT_ROW_RE = re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|\s*([0-9.]+)\s*\|", re.M)


def _tool_threshold(src, expr):
    """按 `DEFAULTS:key` / `CONST:NAME` / `COOLDOWN:事件名` 取工具常量的数值。"""
    kind, _, key = expr.partition(":")
    if kind == "CONST":
        m = re.search(rf"^{re.escape(key)}\s*=\s*([0-9.]+)", src, re.M)
    else:                                   # DEFAULTS / COOLDOWN 都是字典字面量
        m = re.search(rf'"{re.escape(key)}"\s*:\s*([0-9.]+)', src)
    return float(m.group(1)) if m else None


def check_threshold_contract():
    table_p = os.path.join(ROOT, CONTRACT_TABLE)
    if not os.path.isfile(table_p):
        errors.append(f"[threshold] 缺 {rel(table_p)}（阈值契约表真源）")
        return
    declared = {k: float(v) for k, v in CONTRACT_ROW_RE.findall(read(table_p))}
    if not declared:
        errors.append(f"[threshold] {rel(table_p)} 里没有解析到任何契约行")
        return

    checked, bad = 0, len(errors)
    for key, tool, expr in THRESHOLD_CONTRACT:
        tool_p = os.path.join(ROOT, "tools", tool)
        if not os.path.isfile(tool_p):
            errors.append(f"[threshold] {key}: 缺 tools/{tool}")
            continue
        got = _tool_threshold(read(tool_p), expr)
        if got is None:
            errors.append(f"[threshold] {key}: tools/{tool} 里找不到 {expr}"
                          f"（常量被改名/删除——守卫无法比对）")
        elif key not in declared:
            errors.append(f"[threshold] `{key}`（{tool} {expr}={got:g}）未登记进 "
                          f"{CONTRACT_TABLE} §2.1——隐形阈值，作者查不到")
        elif abs(declared[key] - got) > 1e-9:
            errors.append(f"[threshold] `{key}` 声明 {declared[key]:g} != "
                          f"{tool} {expr}={got:g}（改一处忘另一处）")
        else:
            checked += 1
    for key in sorted(set(declared) - {k for k, _t, _e in THRESHOLD_CONTRACT}):
        errors.append(f"[threshold] {CONTRACT_TABLE} 登记的 `{key}` 在守卫契约表里不存在"
                      f"（登记项没有对应工具常量）")
    if checked and len(errors) == bad:
        warnings.append(f"[threshold] 阈值契约 {checked} 项一致（声明 ↔ 工具常量）")


def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        return 0
    quiet = "--quiet" in sys.argv
    check_rules()
    check_skills()
    check_commands()
    check_agents()
    check_links()
    check_orphan_templates()
    check_config()
    check_asset_registry()
    check_tools()
    check_references()
    check_genre_coverage()
    check_style_layer()
    check_axis_contract()
    check_context_budget()
    check_clause_citations()
    check_rule_glob_coverage()
    check_write_read_pairs()
    check_root_docs()
    check_punct_contract()
    check_axis_refs()
    check_threshold_contract()

    if not quiet:
        rules = len(list(walk("rules")))
        skills = len([d for d in os.listdir(os.path.join(ROOT, "skills"))
                      if os.path.isfile(os.path.join(ROOT, "skills", d, "SKILL.md"))])
        tools = len([f for f in os.listdir(os.path.join(ROOT, "tools")) if f.endswith(".py")]) \
            if os.path.isdir(os.path.join(ROOT, "tools")) else 0
        print(f".cursor 自检 · 规则 {rules} · skill {skills} · "
              f"command {len(list(walk('commands')))} · agent {len(list(walk('agents')))} · tool {tools}")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\n✗ {len(errors)} 个错误，{len(warnings)} 个警告")
        return 1
    print(f"\n✓ 无错误，{len(warnings)} 个警告")
    return 0


if __name__ == "__main__":
    sys.exit(main())
