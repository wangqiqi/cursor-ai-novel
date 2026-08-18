---
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
| 11 | 切换沟通语气 | 说「呼叫老周 / 妮妮 / …」（见 `config/roles.json`） |

## 分流口诀

| 症状 | 去向 |
|---|---|
| 不知道写啥 | `/nplan` → brainstorm/plot |
| 写完不放心 | `/ncheck`（章级；缺什么开专项，勿无故全书 8 维连打） |
| AI 味重 | `/nwrite` 4.5 或 `/nfix` 文字轮 |
| 跨章矛盾 | `novel-continuity` / `/ncheck`（含量纲漏网） |
| 准备外发 | `novel-publish`（三尺闸；尺未绿不打 v1.0） |
| 想一口气推 | `/nloop`（须 `PLAN_APPROVED`；设定/生死/转向/`MAX_LOOPS` 仍会停） |

详表：`skills/novel-plan/reference/routes.md`
