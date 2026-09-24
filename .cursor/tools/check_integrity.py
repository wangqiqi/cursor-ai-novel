#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_integrity.py · .cursor 工具链自检

用途：母版维护 / 回灌 / 复制到新书之后，验证 `.cursor/` 自身仍然自洽。
只依赖 Python 3 标准库。

用法：
    python3 .cursor/tools/check_integrity.py            # 在项目根或 .cursor/ 内运行均可
    python3 .cursor/tools/check_integrity.py --quiet     # 只输出问题

检查项：
  1  规则 frontmatter     alwaysApply=true 不得带 globs；false 必须带 globs；globs 不得含 < >
  2  skill frontmatter    name/description/disable-model-invocation 齐备，name 与目录同名
  3  command frontmatter  name 与文件名一致，description 存在
  4  agent frontmatter    name 与文件名一致，description 存在
  5  断链引用             文本中引用的 .md/.mdc/.json 路径必须可解析
  6  孤儿模板             templates/ 下每个模板都应被至少一处引用
  7  配置一致性           role.default / MAX_LOOPS / learn_dir / persona_id 四处对齐
  8  资产登记表交叉核对   00-novel-meta 登记的模板都在 templates/ 里存在
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
    "主题/", "章节/", ".cursorGrowth/", "build/", "dist/", "out/",
    "archive/", "check/", "learn/", "session/",
)
# 明确允许的根级文件
ROOT_FILES = ("CHANGELOG.md", "README.md", ".gitignore")
# 有意不存在的路径（母版明文禁止/仅为占位说明）
ALLOW_ABSENT = {"plan.md", "xxx.md"}
# 目录前缀（正文里用中文顿号/斜杠简写，不会出现在母版中）
SKIP_PREFIX = (".md", ".mdc", ".json", "xxx", "XX", "YY")

PATH_RE = re.compile(r"[`（(\s*|]([A-Za-z0-9_./<>\-]*\.(?:mdc|md|json))")
SKIP_SUBSTR = ("<", ">", "*", "…", "NN", "MMDD", "YYYY", "X-Y", "vX.Y",
               "yyyy", "plugin", "http", "node_modules", "xxx", "XXX", "YY")
# 这些行里的文件名是工作流在 .cursorGrowth/ 下生成的，不算断链
SKIP_LINE_SUBSTR = (".cursorGrowth", "learn/", "archive/", "check/")


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
