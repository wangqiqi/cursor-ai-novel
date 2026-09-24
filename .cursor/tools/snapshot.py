#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
snapshot.py · 快照 / 比对 / 回滚（改稿安全网）

用途：`novel-rewrite` / `novel-line-rewriter` 覆盖正文前先留快照；改坏了一键回滚。
只依赖 Python 3 标准库。默认只操作 `章节/`（正文层），不带 `主题/`。

用法：
    python3 .cursor/tools/snapshot.py snapshot --note 去AI味第03章
    python3 .cursor/tools/snapshot.py list
    python3 .cursor/tools/snapshot.py diff latest                 # 当前 vs 最近快照
    python3 .cursor/tools/snapshot.py diff 20260924_223401_快照_x
    python3 .cursor/tools/snapshot.py verify latest               # 校验是否被改动
    python3 .cursor/tools/snapshot.py restore latest --yes        # 回滚（会先给当前状态留快照）

    python3 .cursor/tools/snapshot.py snapshot --paths 章节 主题/世界观.md

快照目录：
    .cursorGrowth/archive/YYYYMMDD_HHMMSS_快照_<note>/    （含 manifest.json + 文件镜像）
退出码：0 成功；1 失败；2 用法错误。
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime

DEFAULT_PATHS = ("章节",)


def project_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def archive_dir(root):
    return os.path.join(root, ".cursorGrowth", "archive")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cjk_count(path):
    try:
        with open(path, encoding="utf-8") as fh:
            t = fh.read()
        return len(re.findall(r"[\u4e00-\u9fff]", t))
    except (UnicodeDecodeError, OSError):
        return 0


def iter_files(root, paths):
    out = []
    for p in paths:
        ap = p if os.path.isabs(p) else os.path.join(root, p)
        if os.path.isfile(ap):
            out.append(ap)
        elif os.path.isdir(ap):
            for dp, dns, fns in os.walk(ap):
                dns[:] = [d for d in dns if d not in (".git", "node_modules")]
                for fn in fns:
                    out.append(os.path.join(dp, fn))
    return sorted(set(out))


def snapshots(root):
    """返回 [(name, path, manifest|None)]，按时间倒序。"""
    d = archive_dir(root)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d), reverse=True):
        p = os.path.join(d, name)
        if not os.path.isdir(p):
            continue
        mf = os.path.join(p, "manifest.json")
        man = None
        if os.path.isfile(mf):
            try:
                man = json.load(open(mf, encoding="utf-8"))
            except json.JSONDecodeError:
                man = None
        out.append((name, p, man))
    return out


def resolve_snapshot(root, token):
    snaps = snapshots(root)
    if not snaps:
        return None
    if token in ("latest", "last", "-1"):
        return snaps[0]
    for name, p, man in snaps:
        if name == token or name.startswith(token):
            return (name, p, man)
    return None


def cmd_snapshot(root, args):
    paths = args.paths or list(DEFAULT_PATHS)
    files = iter_files(root, paths)
    if not files:
        print(f"✗ 没有可快照的文件（paths={paths}）", file=sys.stderr)
        return 1
    note = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", args.note or "手动").strip("-") or "手动"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{stamp}_快照_{note}"
    dest = os.path.join(archive_dir(root), name)
    os.makedirs(dest, exist_ok=True)

    man = {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "note": args.note or "手动", "paths": paths, "files": []}
    for f in files:
        rel = os.path.relpath(f, root)
        tgt = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(tgt), exist_ok=True)
        shutil.copy2(f, tgt)
        man["files"].append({"path": rel, "sha256": sha256(f),
                             "bytes": os.path.getsize(f), "cjk": cjk_count(f)})
    with open(os.path.join(dest, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=2)

    total = sum(x["cjk"] for x in man["files"])
    print(f"✓ 快照 {name}")
    print(f"  {len(man['files'])} 个文件 · {total} 汉字 · {os.path.relpath(dest, root)}")
    print("  回滚：python3 .cursor/tools/snapshot.py restore " + name + " --yes")
    return 0


def cmd_list(root, args):
    snaps = snapshots(root)
    if not snaps:
        print("（暂无快照）")
        return 0
    print(f"快照 {len(snaps)} 个（新→旧）：")
    for name, _p, man in snaps:
        if man:
            total = sum(x.get("cjk", 0) for x in man.get("files", []))
            print(f"  {name}  · {man.get('created_at','?')} · "
                  f"{len(man.get('files', []))} 文件 · {total} 汉字 · {man.get('note','')}")
        else:
            print(f"  {name}  · (无 manifest)")
    return 0


def cmd_diff(root, args):
    token = args.snapshot or "latest"
    got = resolve_snapshot(root, token)
    if not got:
        print(f"✗ 找不到快照：{token}", file=sys.stderr)
        return 1
    name, spath, man = got
    if not man:
        print(f"✗ 快照 {name} 缺 manifest，无法比对", file=sys.stderr)
        return 1

    changed = added = removed = 0
    plus = minus = 0
    print(f"比对：当前工作区 ←→ 快照 {name}")
    for item in man["files"]:
        rel = item["path"]
        cur = os.path.join(root, rel)
        old = os.path.join(spath, rel)
        if not os.path.isfile(cur):
            print(f"  ✗ 已删除：{rel}")
            removed += 1
            continue
        if sha256(cur) == item["sha256"]:
            continue
        changed += 1
        a = open(old, encoding="utf-8").read().splitlines()
        b = open(cur, encoding="utf-8").read().splitlines()
        d = list(difflib.unified_diff(a, b, fromfile=f"快照/{rel}", tofile=f"当前/{rel}", lineterm="", n=1))
        p = sum(1 for l in d if l.startswith("+") and not l.startswith("+++"))
        m = sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
        plus += p
        minus += m
        print(f"  ✎ {rel}  +{p}/-{m}  ({item['cjk']} → {cjk_count(cur)} 汉字)")
        if args.verbose:
            for l in d:
                print("      " + l)
    # 新增文件
    if args.paths:
        for f in iter_files(root, args.paths):
            rel = os.path.relpath(f, root)
            if not any(x["path"] == rel for x in man["files"]):
                print(f"  + 新增：{rel}")
                added += 1

    print(f"\n{'✓ 无差异' if not (changed or removed or added) else ''}"
          f"改动 {changed} · 删除 {removed} · 新增 {added} · 行 +{plus}/-{minus}")
    if not args.verbose and changed:
        print("提示：加 --verbose 看逐行 diff。")
    return 0


def cmd_verify(root, args):
    got = resolve_snapshot(root, args.snapshot or "latest")
    if not got:
        print(f"✗ 找不到快照：{args.snapshot}", file=sys.stderr)
        return 1
    name, _p, man = got
    if not man:
        print(f"✗ 快照 {name} 缺 manifest", file=sys.stderr)
        return 1
    bad = []
    for item in man["files"]:
        sp = os.path.join(archive_dir(root), name, item["path"])
        if not os.path.isfile(sp):
            bad.append((item["path"], "快照文件缺失"))
        elif sha256(sp) != item["sha256"]:
            bad.append((item["path"], "快照被改动"))
    if bad:
        print(f"✗ 快照 {name} 校验失败：")
        for p, why in bad:
            print(f"  {why}：{p}")
        return 1
    print(f"✓ 快照 {name} 校验通过（{len(man['files'])} 文件哈希一致）")
    return 0


def cmd_restore(root, args):
    got = resolve_snapshot(root, args.snapshot or "latest")
    if not got:
        print(f"✗ 找不到快照：{args.snapshot}", file=sys.stderr)
        return 1
    name, spath, man = got
    if not man:
        print(f"✗ 快照 {name} 缺 manifest", file=sys.stderr)
        return 1
    targets = man["files"]
    if args.paths:
        keep = tuple(args.paths)
        targets = [x for x in targets if x["path"].startswith(keep)]
    if not targets:
        print("✗ 没有匹配的文件可恢复", file=sys.stderr)
        return 1

    if not args.yes:
        print(f"将回滚 {len(targets)} 个文件到快照 {name}：")
        for x in targets[:20]:
            print(f"  - {x['path']}")
        if len(targets) > 20:
            print(f"  … 共 {len(targets)} 个")
        print("\n这是破坏性操作。确认后请加 --yes 重跑。")
        return 0

    # 先给"当前状态"留安全快照
    safe = argparse.Namespace(paths=sorted({os.path.dirname(x["path"]) or "." for x in targets}),
                              note=f"回滚前-{name}")
    cmd_snapshot(root, safe)

    n = 0
    for x in targets:
        src = os.path.join(spath, x["path"])
        dst = os.path.join(root, x["path"])
        if not os.path.isfile(src):
            print(f"  ✗ 快照内缺文件：{x['path']}")
            continue
        os.makedirs(os.path.dirname(dst) or root, exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
    print(f"✓ 已回滚 {n} 个文件到 {name}")
    print("  改动未提交前，可用 git diff 复核。")
    return 0


def main():
    ap = argparse.ArgumentParser(description="快照 / 比对 / 回滚")
    ap.add_argument("--root", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("snapshot", help="给当前正文留快照")
    s.add_argument("--note", default="手动")
    s.add_argument("--paths", nargs="*", default=None)
    s.set_defaults(func=cmd_snapshot)

    s = sub.add_parser("list", help="列出快照")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("diff", help="当前工作区 vs 快照")
    s.add_argument("snapshot", nargs="?", default="latest")
    s.add_argument("--paths", nargs="*", default=None)
    s.add_argument("--verbose", action="store_true")
    s.set_defaults(func=cmd_diff)

    s = sub.add_parser("verify", help="校验快照完整性")
    s.add_argument("snapshot", nargs="?", default="latest")
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("restore", help="从快照回滚（破坏性）")
    s.add_argument("snapshot", nargs="?", default="latest")
    s.add_argument("--paths", nargs="*", default=None)
    s.add_argument("--yes", action="store_true")
    s.set_defaults(func=cmd_restore)

    args = ap.parse_args()
    root = args.root or project_root()
    if not os.path.isdir(root):
        print(f"✗ 项目根不存在：{root}", file=sys.stderr)
        return 2
    return args.func(root, args)


if __name__ == "__main__":
    sys.exit(main())
