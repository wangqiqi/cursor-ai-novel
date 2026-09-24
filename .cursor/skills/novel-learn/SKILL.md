---
name: novel-learn
description: 学习本小说项目约定：声口、黑名单词、节奏阈值、读者反馈 → 写入 .cursorGrowth/learn/。不改 .cursor。用户说「记住」「学一下」「沉淀约定」或 /nlearn 时用。
disable-model-invocation: false
---

# 小说项目学习 · novel-learn

> 把**本仓特化**写进 Growth，别堆进 `.cursor/`。

## 触发

- `/nlearn` · 「记住」· 「沉淀约定」· Sprint 收尾需要固化偏好

## 输入源（按需扫）

> 源的清单真源：`config/workflow.json` → `growth.learn_sources`。**改清单改那里**，并同步本表。

| 源 | 取什么 |
|---|---|
| `CHANGELOG.md` | 近期创作决策 |
| `.cursorGrowth/check/` | 八股/节奏/读者反应（活跃报告） |
| `.cursorGrowth/archive/` | 历史决策摘要 |
| `.cursorGrowth/plan.md` | 完成定义、偏差记录 |
| `主题/总览.md` · `主题/` | 项目元信息、母题表、阈值现状 |
| 用户口头偏好 | 声口、禁忌词、章长 |

## 输出（只写 Growth）

默认目录：`.cursorGrowth/learn/`（见 `config/workflow.json` → `growth.learn_dir`）

> **这些文件不是日志，是下游的输入。** 写完必须确认读取方知道它们存在：

| 文件（均在 `.cursorGrowth/learn/`） | 内容 | **谁读** |
|---|---|---|
| `.cursorGrowth/learn/writing-voice.md` | 声口、称呼、禁套词（项目级） | `novel-chapter` 动笔前 · `novel-rewrite` 第 1 步 · `novel-dialogue` 输入 |
| `.cursorGrowth/learn/rhythm.md` | 节长、加粗密度、感官偏好 | `novel-chapter` 动笔前 · `novel-rewrite` 第 1 步 |
| `.cursorGrowth/learn/decisions.md` | 已拍板设定/剧情决策摘要 | `novel-chapter` · `novel-rewrite` · `novel-check` 资产清单 |
| `.cursorGrowth/learn/acceptance.md` | 何谓「这章过了」（项目 Done when） | `novel-run` 阶段 1（**完成定义真源**）· `novel-check` 判定口径 |

> **写入后自检**：`ls .cursorGrowth/learn/` 应能看到上述文件；若某个文件从没被写，不要留空壳——空壳会让下游误以为"项目无约定"。
> `.cursorGrowth/learn/acceptance.md` 与 `.cursorGrowth/plan.md` 的 `Acceptance` 列冲突时，**plan 的当前任务定义优先**（更具体），但两者都不得违反本书的 `主题/通用约束.md`。

## 每 10 章 · 深度压缩与风格校准（冻结层）

每完成 10 章，除常规沉淀外，额外做两件事——**这是防止"传话游戏"式细节衰减的唯一机制**：

1. **冻结摘要**：把最近 10 章压成 ≤200 字，**追加**到 `主题/分卷/第<VOL>卷_<卷名>.md`
   的「卷内滚动摘要（冻结）」表。**已写段落一律不改写**，只追加新行。
2. **风格校准**：跑 `python3 .cursor/tools/analyze_style.py --manuscript`，与 `主题/风格档.md` 的
   目标值比对；有漂移则把结论写进 `.cursorGrowth/learn/writing-voice.md`（而不是改风格档——改档要走 `/nplan`）。

> 不做这一步的后果：第 300 章时没人记得第 20 章写过什么，只能回读正文——上下文彻底失控。

## 禁止

- ❌ 把项目特化写进 `.cursor/rules` / skills（除非用户明确授权改母版）
- ❌ 用 learn 代替 `/ncheck` 验收

## 关联

- **命令**：`/nlearn`
- **配置**：`config/workflow.json` → `growth.learn_dir` / `growth.learn_sources`
- **人格会话**：`.cursorGrowth/session/persona.json`
- **规则**：`00-novel-meta.mdc` · `08-novel-discipline.mdc`
- **扫榜拆文（可选方法）**：`skills/novel-plot/reference/craft-intake.md`（笔记仍写 Growth，不改母版）
