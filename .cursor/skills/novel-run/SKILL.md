---
name: novel-run
description: 小说创作执行技能。按 `.cursorGrowth/plan.md` 逐步执行任务，确保每步必验、偏差必录、即时归档。适用于用户说"开始"、"执行"或 "/nrun" 时。
disable-model-invocation: false
---

# 小说创作执行 · novel-run

> **"计划定下，执行必严；每步必验，偏差必录。"**
> 本技能负责把 `.cursorGrowth/plan.md` 的任务表从 `⬜` 推到 `✅`。
> **schema 真源**：`.cursor/templates/plan.md`（头部 9 个字段 + `Active sprint` + `下一 Sprint 候选`）；勿自创格式。

## 触发场景

- 用户说："开始"、"执行"、"go"、"按计划做"
- `.cursorGrowth/plan.md` 中有 `Active sprint` 且任务未完成
- `/nloop` 自动流转到执行阶段

## 工作流（3 阶段）

### 阶段 1：启动与路由
- **动作**：读取 `.cursorGrowth/plan.md`，定位第一个未完成任务。
- **读约定**：读 `.cursorGrowth/learn/`（存在时）——`.cursorGrowth/learn/acceptance.md` 是**「完成定义」的项目级真源**，`.cursorGrowth/learn/decisions.md` 是已拍板决策（不得改口径），`.cursorGrowth/learn/writing-voice.md` / `.cursorGrowth/learn/rhythm.md` 约束产出质量。
- **完成定义取值顺序**：plan 任务的 `Acceptance` 列 ＞ `.cursorGrowth/learn/acceptance.md` ＞ 该 skill 的默认验收。**前者存在时不得跳过**。
- **闸**（`/nloop` 或用户说「开始」时）：`PLAN_APPROVED` 须为 `true`；否则停问，勿执行。`/nloop` 另须遵守 `MAX_LOOPS`（见 `commands/nloop.md`）。
- **路由**：根据任务类型自动加载上下文：
    - **写作类**：加载 `主题/` 核心文件 + `章节/` 前文。
    - **设定类**：加载 `主题/世界观.md` + `主题/人物/`。
    - **检查类**：加载 `novel-check` 技能。

### 阶段 2：原子执行循环
对于 `.cursorGrowth/plan.md` 中的每一个子任务：
1. **执行**：调用相关工具完成操作。
2. **自检**：对比「完成定义」进行验证。
3. **同步**：
    - 更新 `.cursorGrowth/plan.md` 状态（`⬜` → `🔄` → `✅`）与头部 `ACTIVE` / `NEXT`。
    - 重大变更（文件增删、章节完稿）同步至 `CHANGELOG.md`。

### 阶段 3：收尾与归档
- **动作**：
    1. 更新 `.cursorGrowth/plan.md` 头部 `LAST_DONE`。
    2. 若 Sprint 全面达成：**整段移除** `Active sprint` 区块，笔记写入 `.cursorGrowth/archive/`，并刷新 `下一 Sprint 候选`；`SPRINT_STATUS: closed`。
    3. **提交纪律（分级）**：更新 `CHANGELOG.md` → `git add <具体文件>` → `git commit`。
       `git tag` / `git push` **仅当** plan 的完成定义要求、且用户未禁止时执行；无 remote 时只 commit，**禁止**默认 push。
    4. 总结报告：列出完成项、产出文件、偏差及 CHANGELOG 版本。

## 执行约束

- **备份优先**：覆盖重要文件前，必须先备份至 `.cursorGrowth/archive/`。
- **偏差记录**：实际执行与计划有出入时，必须在 `plan.md` 或报告中说明。
- **铁律遵循**：执行过程中严禁在章节正文插入元数据。
- **验过再勾**：任务 ✅ 前须满足完成定义（写作类至少过一遍相关 check/扫描）；禁止口头「过了」。
- **最小 diff**：只做 ACTIVE 任务；禁止顺手改无关章/设定（见 `08-novel-discipline`）。
- **自治续跑**：`/nloop` 下同会话续下一任务；仅 `.cursor/config/workflow.json` 的 `interrupt_on` / `confirm_before` 与 `MAX_LOOPS` 停问人。

## 反模式

- ❌ 未确认 `plan.md` 就盲目执行。
- ❌ 任务完成后不及时勾选 `.cursorGrowth/plan.md`。
- ❌ CHANGELOG 与实际变更不一致。
- ❌ 忽略 `novel-check` 的负面反馈强行推进。
- ❌ 声称 check 过却未调度 `novel-check` / scanner。

## 关联
- **上游**：`novel-plan`（提供计划）
- **模板**：`.cursor/templates/plan.md`（schema 真源）
- **规则**：`00-novel-meta.mdc`、`00-novel-values.mdc`、`08-novel-discipline.mdc`
- **命令**：`/nrun` · `/nloop`
- **路由**：`../novel-plan/reference/routes.md` · `/nhelp`
