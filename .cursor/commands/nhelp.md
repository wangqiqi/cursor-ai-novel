---
name: nhelp
description: 【帮助】小说命令路由 — 卡了该走哪
---

# /nhelp · 迷路路由

不确定用哪个命令时看这张表（或说「卡了」「下一步」）。

> **母版**：本 `.cursor` 真源在仓库 `cursor-ai-novel`。新书先复制母版再 `/nnew`。

## 主路由

| # | 你想… | 用这个 |
|---|---|---|
| 1 | 先想清楚 / 拆任务（≥5 步） | `/nplan` |
| 2 | 按 plan 推进 | `/nrun` |
| 3 | 持续连跑（决策才停） | `/nloop` |
| 4 | 写章/节 | `/nwrite` |
| 5 | 自洽/完整性检查 | `/ncheck` |
| 6 | 修订润色 | `/nfix` |
| 7 | 更新 CHANGELOG / 归档说明 | `/nlog` |
| 8 | 看进度 | `/nstatus` |
| 9 | 新建小说骨架 | `/nnew` |
| 10 | 沉淀声口/约定到 Growth | `/nlearn` |
| 11 | 外发打包 / 推介材料 | `/npublish` |
| 12 | 切换沟通语气 | 说「呼叫老周 / 妮妮 / …」（见 `config/roles.json`） |

## 分流口诀

| 症状 | 去向 |
|---|---|
| 不知道写啥 | `/nplan` → `novel-brainstorm` / `novel-plot` |
| 写完不放心 | `/ncheck`（章级；缺什么开专项，勿无故全书 8 维连打） |
| AI 味重 | `/nwrite` 第 5 步 或 `/nfix` 第 3 轮（文字层） |
| 字数/密度/敏感词想机械核对 | `python3 .cursor/tools/check_manuscript.py` |
| 书稿太长一次查不完 | `skills/novel-check/reference/chunked-scan.md`（分批） |
| 类型工艺（推理公平 / 感情线 / 境界 / 考据 / 笑点） | `novel-genre` |
| 文风太平 / 想要某类作家的味道 | `novel-style`（`tools/analyze_style.py --list-proto` 看 10 原型） |
| 风格/节奏有偏差 | `python3 .cursor/tools/check_manuscript.py --style` |
| 对白不像人 | `novel-dialogue`（7 项硬指标） |
| 跨章矛盾 | `novel-continuity` / `/ncheck`（含量纲漏网） |
| 人物不像 | `novel-character` + `novel-character-coach` |
| 设定有洞 | `novel-world` + `novel-world-keeper` |
| 多卷 / 多线要规划 | `templates/volume-outline.md` · `templates/pov-ledger.md` |
| 改稿怕改坏 | `python3 .cursor/tools/snapshot.py snapshot --note <说明>` |
| 准备外发 | `/npublish`（三尺闸；尺未绿不打 v1.0） |
| 想一口气推 | `/nloop`（须 `PLAN_APPROVED`；设定/生死/转向/`MAX_LOOPS` 仍会停） |
| 改完不记得沉淀 | `/nlearn`（写 `.cursorGrowth/learn/`） |

详表：`skills/novel-plan/reference/routes.md`
