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

| 文件（均在 `.cursorGrowth/learn/`） | 内容 |
|---|---|
| `.cursorGrowth/learn/writing-voice.md` | 声口、称呼、禁套词（项目级） |
| `.cursorGrowth/learn/rhythm.md` | 节长、加粗密度、感官偏好 |
| `.cursorGrowth/learn/decisions.md` | 已拍板设定/剧情决策摘要 |
| `.cursorGrowth/learn/acceptance.md` | 何谓「这章过了」（项目 Done when） |

## 禁止

- ❌ 把项目特化写进 `.cursor/rules` / skills（除非用户明确授权改母版）
- ❌ 用 learn 代替 `/ncheck` 验收

## 关联

- **命令**：`/nlearn`
- **配置**：`config/workflow.json` → `growth.learn_dir` / `growth.learn_sources`
- **人格会话**：`.cursorGrowth/session/persona.json`
- **规则**：`00-novel-meta.mdc` · `08-novel-discipline.mdc`
- **扫榜拆文（可选方法）**：`skills/novel-plot/reference/craft-intake.md`（笔记仍写 Growth，不改母版）
