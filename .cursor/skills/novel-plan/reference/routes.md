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
| 7 | 更新日志 / 归档 | `/nlog` · `99-novel-archive` |
| 8 | 状态 / 帮助 | `/nstatus` · `/nhelp` |

闸门（任意小说）：`novel-plan/reference/universal-gates.md`（三层文档 · 漏网 · 量纲 · 加厚 · 三尺 · CHANGELOG）

## 扩展

| 关键词 | 去向 |
|---|---|
| 新建项目 | `/nnew` · `novel-scaffold` |
| 类型工艺（推理公平 / 感情线 / 境界体系 / 考据 / 笑点） | `novel-genre`（按 Q1 派发 5 份 reference） |
| 世界观 / 设定洞 | `novel-world` · `novel-world-keeper` |
| 人物不像 | `novel-character` · `novel-character-coach` |
| 结构 / 节拍 / 爽点钩子 / 节奏窗 | `novel-plot` · `skills/novel-plot/reference/opening-protocol.md` · `skills/novel-plot/reference/reader-rewards.md` · `novel-architect` |
| 分卷 / 多卷本 | `templates/volume-outline.md` → `主题/分卷/` |
| 多线 / 群像 / 视角越界 | `templates/pov-ledger.md` → `主题/POV台账.md` |
| 情绪调性 / 甜虐节奏 | `skills/novel-plot/reference/emotion-craft.md` · 章前卡「本章调性」 |
| 类型向金手指·反套路（可选） | `skills/novel-plot/reference/commercial-hooks.md` · `novel-brainstorm` |
| 扫榜拆文 | `skills/novel-plot/reference/craft-intake.md` · `/nlearn` |
| 对白 | `novel-dialogue` |
| 伏笔 / 连续 / 量纲漏网 | `novel-continuity` · `novel-continuity-sleuth` |
| 去 AI 味 | `novel-line-scanner` → `novel-line-rewriter` |
| 字数 / 密度 / 敏感词机械校验 | `tools/check_manuscript.py` |
| 超长篇分批检查 | `skills/novel-check/reference/chunked-scan.md` |
| 改稿前留档 / 回滚 | `tools/snapshot.py`（snapshot · diff · restore） |
| 外发 / 上架包 | `/npublish` · `novel-publish`（三尺闸）· `tools/build_export.py`（EPUB/TXT） |
| 更新日志 / 归档 | `/nlog` · `99-novel-archive` |
| 记住约定 | `/nlearn` · `novel-learn` |
| 呼叫某人设 | `config/roles.json` + `07-novel-persona.mdc` |

## 自治（`/nloop`）

| 项 | 口径 |
|---|---|
| 启动闸 | `PLAN_APPROVED: true` + Sprint 非 planning/closed + 有未完成任务 |
| 圈数 | plan 头 `MAX_LOOPS`（默认见 `.cursor/config/workflow.json` → `max_loops_default`）；到上限停问 |
| 打断 | `decision_needed`（含核心设定 / 人物生死 / 重大转向 / **新 Sprint 待批**）· `blocker` · `check_fail_twice` · `goal_drift` · `max_loops`（真源：`config/workflow.json` → `autonomous.interrupt_on`，逐项对应 `commands/nloop.md` 停顿表） |
| 详规 | `.cursor/commands/nloop.md` |
