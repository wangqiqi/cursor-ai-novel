#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py · 母版**单入口验收**（一条命令证明 `.cursor/` 自洽）

为什么需要它：
    在它之前，验收契约是**两条手工命令**（check_integrity + selftest），
    散落在 README、CHANGELOG、`.cursor/README.md` 与 plan 的 VERIFY 字段里。
    契约不能一条命令复现，就等于没有契约：
      · 少跑一条没人发现（多数回归是"只跑了自检、没跑反向测试"）；
      · plan/workflow 的 VERIFY 字段没有可执行目标。

用法：
    python3 .cursor/tools/verify.py              # 全部步骤
    python3 .cursor/tools/verify.py --json       # 机器可读（含每步耗时/退出码）
    python3 .cursor/tools/verify.py --quiet      # 只打印失败步骤
    python3 .cursor/tools/verify.py --no-selftest  # 跳过反向测试（供 selftest 自身调用，防递归）
    python3 .cursor/tools/verify.py --list       # 只列出将要执行的步骤

步骤：
    1  check_integrity.py      结构自检：断链 / frontmatter / 配置 / 资产登记 / 各守卫
    2  selftest.py             守卫反向测试：逐条投毒，确认守卫**真的会响**
    3  tools/*.py --help       7 个工具的参数契约与 import 冒烟

退出码：0 全部通过；1 有步骤失败（**门禁关闭**）；2 用法错误。
    只依赖标准库；只读母版，不改任何文件。
"""

import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # .cursor/
PROJECT = os.path.dirname(ROOT)       # 项目根（子进程 cwd）
# 反向测试（selftest）会调用本脚本验证"门禁会关"——它必须显式传 --no-selftest
# 防无限递归。**不设环境变量隐式跳过**：静默跳过一步等于验收说谎。


def run_step(cmd):
    """执行一步，返回 (rc, 输出, 耗时秒)。"""
    t0 = time.time()
    p = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or ""), time.time() - t0


def step_integrity():
    path = os.path.join(HERE, "check_integrity.py")
    if not os.path.isfile(path):
        return {"name": "check_integrity", "ok": False, "rc": 2,
                "detail": f"缺 {os.path.relpath(path, PROJECT)}"}
    rc, out, secs = run_step([sys.executable, path])
    errs = [ln.strip() for ln in out.splitlines() if ln.startswith("ERROR")]
    detail = f"{len(errs)} 个错误" if errs else "无错误"
    if errs:
        detail += "：" + "；".join(errs[:3]) + ("…" if len(errs) > 3 else "")
    return {"name": "check_integrity", "ok": rc == 0, "rc": rc,
            "seconds": round(secs, 2), "detail": detail}


def step_selftest():
    path = os.path.join(HERE, "selftest.py")
    if not os.path.isfile(path):
        return {"name": "selftest", "ok": False, "rc": 2,
                "detail": f"缺 {os.path.relpath(path, PROJECT)}"}
    rc, out, secs = run_step([sys.executable, path])
    tally = ""
    for ln in reversed(out.splitlines()):
        if "/" in ln and ("✓" in ln or "✗" in ln):
            tally = ln.strip()
            break
    return {"name": "selftest", "ok": rc == 0, "rc": rc,
            "seconds": round(secs, 2), "detail": tally or f"rc={rc}"}


def step_tool_help():
    """每个工具 `--help` 必须退 0，且**只打印用法**——不得顺便把整套检查跑一遍。

    只看 rc 是不够的：`--help` 触发全量运行的脚本同样退 0，却让"参数契约冒烟"
    变成一次昂贵的副作用。所以这里额外要求输出里出现用法标记。
    """
    tools = sorted(f for f in os.listdir(HERE) if f.endswith(".py"))
    failed, secs_all = [], 0.0
    for f in tools:
        rc, out, secs = run_step([sys.executable, os.path.join(HERE, f), "--help"])
        secs_all += secs
        if rc != 0:
            failed.append(f"{f}(rc={rc})")
        elif not ("用法" in out or "usage" in out.lower()):
            failed.append(f"{f}(--help 未打印用法：疑似执行了实际工作)")
    n = len(tools)
    detail = f"{n - len(failed)}/{n} 通过" + (f"；失败：{', '.join(failed)}" if failed else "")
    return {"name": "tool_help", "ok": not failed, "rc": 0 if not failed else 1,
            "seconds": round(secs_all, 2), "detail": detail, "tools": n}


def build_steps(args):
    steps = [step_integrity]
    if not args.no_selftest:
        steps.append(step_selftest)
    steps.append(step_tool_help)
    return steps


def main():
    ap = argparse.ArgumentParser(
        prog="verify.py",
        description="母版单入口验收：结构自检 + 守卫反向测试 + 工具 --help 冒烟",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0 全绿；1 门禁关闭；2 用法错误。")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    ap.add_argument("--quiet", action="store_true", help="只打印失败步骤")
    ap.add_argument("--no-selftest", action="store_true",
                    help="跳过反向测试（selftest 自调用防递归）")
    ap.add_argument("--list", action="store_true", help="只列出步骤，不执行")
    args = ap.parse_args()

    steps = build_steps(args)
    names = [s.__name__.replace("step_", "") for s in steps]

    if args.list:
        for n in names:
            print(n)
        return 0

    results = [s() for s in steps]
    ok = all(r["ok"] for r in results)
    total = round(sum(r.get("seconds", 0.0) for r in results), 2)

    if args.json:
        print(json.dumps({
            "ok": ok,
            "steps": results,
            "seconds": total,
            "root": os.path.relpath(ROOT, PROJECT),
        }, ensure_ascii=False, indent=2))
        return 0 if ok else 1

    if not args.quiet:
        print(f"母版验收 · {os.path.relpath(ROOT, PROJECT)} · {len(results)} 步\n")
    for r in results:
        if args.quiet and r["ok"]:
            continue
        mark = "✓" if r["ok"] else "✗"
        print(f"  {mark} {r['name']:<18} {r.get('detail', '')}"
              f"（{r.get('seconds', 0.0)}s）")
    if not args.quiet or not ok:
        print(f"\n{'✓ 验收通过' if ok else '✗ 验收失败（门禁关闭）'}"
              f"  {sum(1 for r in results if r['ok'])}/{len(results)} · {total}s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
