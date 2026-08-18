# 小说命令路由表

AskQuestion / 迷路时用。无工具则正文编号选项。

## 主路由（≤7 · 日常）

| # | 场景 | 命令 / skill |
|---|---|---|
| 1 | 规划 / 拆任务 | `/nplan` · `novel-plan` |
| 2 | 执行 plan | `/nrun` · `novel-run` |
| 3 | 自主连跑 | `/nloop` |
| 4 | 写章节 | `/nwrite` · `novel-chapter` |
| 5 | 检查 | `/ncheck` · `novel-check` |
| 6 | 修订 | `/nfix` · `novel-rewrite` |
| 7 | 状态 / 帮助 | `/nstatus` · `/nhelp` |

闸门（任意小说）：`novel-plan/reference/universal-gates.md`（三层文档 · 漏网 · 量纲 · 加厚 · 三尺 · CHANGELOG）

## 扩展

| 关键词 | 去向 |
|---|---|
| 新建项目 | `/nnew` · `novel-scaffold` |
| 世界观 / 设定洞 | `novel-world` · `novel-world-keeper` |
| 人物不像 | `novel-character` · `novel-character-coach` |
| 结构 / 节拍 / 爽点钩子 / 节奏窗 | `novel-plot` · `opening-protocol.md` · `reader-rewards.md` · `novel-architect` |
| 情绪调性 / 甜虐节奏 | `emotion-craft.md` · 章前卡「本章调性」 |
| 类型向金手指·反套路（可选） | `commercial-hooks.md` · `novel-brainstorm` |
| 扫榜拆文 | `craft-intake.md` · `/nlearn` |
| 对白 | `novel-dialogue` |
| 伏笔 / 连续 / 量纲漏网 | `novel-continuity` · `novel-continuity-sleuth` |
| 去 AI 味 | `novel-line-scanner` → `novel-line-rewriter` |
| 外发 / 上架包 | `novel-publish` |
| 记住约定 | `/nlearn` · `novel-learn` |
| 呼叫某人设 | `config/roles.json` + `07-novel-persona` |

## 自治（`/nloop`）

| 项 | 口径 |
|---|---|
| 启动闸 | `PLAN_APPROVED: true` + Sprint 非 planning/closed + 有未完成任务 |
| 圈数 | plan 头 `MAX_LOOPS`（默认见 `.cursor/config/workflow.json` → `max_loops_default`）；到上限停问 |
| 打断 | 核心设定 · 人物生死 · 重大转向 · `ncheck` 连挂 2 次 · blocker · 范围蔓延 · 触顶 `MAX_LOOPS` · 新 Sprint 待批 |
| 详规 | `.cursor/commands/nloop.md` |
