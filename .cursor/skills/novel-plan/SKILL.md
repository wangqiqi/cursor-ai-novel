---
name: novel-plan
description: 小说创作规划技能。维护 `.cursorGrowth/plan.md` 工作板，确保复杂任务先规划、后执行。适用于用户说"规划"、"做计划"或任务 ≥ 5 步时。
disable-model-invocation: false
---

# 小说创作规划 · novel-plan

> **".cursorGrowth/plan.md` 是工作板，不是档案馆。"**
> 本技能负责维护 `.cursorGrowth/plan.md` 的卫生与任务流转。

## 触发场景

- 用户说："规划"、"做计划"、"先想清楚"
- 任务 ≥ 5 个步骤（强制）
- 涉及跨章节、多角色或底层规则的重大变更
- 启动新 Sprint 或大版本修订

## 工作流（5 阶段）

### 阶段 1：需求澄清 (Clarify)
- **动作**：复述目标，识别歧义，用 `AskQuestion` 确认（≤ 6 个问题，一次并行提交；**无 AskQuestion 工具时**改为正文编号选项，一次列全）。
- **输出**：明确「成功标准」与「范围边界」。

### 阶段 2：现状盘点 (Inventory)
- **动作**：扫描 `主题/`（含 `主题/人物/`）、`章节/`、`CHANGELOG.md`、`.cursorGrowth/plan.md`；缺资产按 `00-novel-meta.mdc` 降级协议处理。
- **输出**：识别已有资产与当前缺口，避免重复造轮子。

### 阶段 3：任务分解 (Decompose)
- **动作**：拆解为 ≤ 5 步的子任务。
- **原则**：每步必须「可验证」且「依赖明确」。

### 阶段 4：写入 `.cursorGrowth/plan.md` (Commit)
- **动作**：**按 `.cursor/templates/plan.md` 的既有 schema** 更新 `.cursorGrowth/plan.md`（勿自创格式——`/nrun` 与 `/nloop` 按该头部字段读闸门）。
- **规范**：
    - 更新头部 HTML 注释（`PLANNING: true`、`SPRINT`、`SPRINT_STATUS: planning`、`NEXT`、`ACTIVE`）。
    - 填充 `Active sprint` 区块（Goal / Done when / Out of scope / Task 表 / 执行顺序）。
    - 维护 `下一 Sprint 候选` 区块。
    - 阈值（如单节字数）取自 `主题/通用约束.md`，不在本技能里硬编码。

### 阶段 5：用户确认 (Confirm)
- **动作**：停下来，展示 `plan.md` 变更，等待用户输入「go/开始/确认」；确认后写 `PLAN_APPROVED: true`、`SPRINT_STATUS: active`。
- **与 `/nloop`**：新 Sprint / 首次批准 **不可**跳过。仅当已批准且无 `decision_needed` 时，loop 内「补位拆下一小批（≤5、不扩 scope）」可不停问。

## `.cursorGrowth/plan.md` 维护规范

> **唯一 schema 真源**：`.cursor/templates/plan.md`。头部字段共 9 个：
> `PLANNING` · `SPRINT` · `PLAN_APPROVED` · `AUTONOMOUS` · `SPRINT_STATUS` · `ACTIVE` · `NEXT` · `LAST_DONE` · `MAX_LOOPS`。

1. **头部卫生**：始终保持 HTML 注释处于最新状态（`ACTIVE` / `NEXT` / `LAST_DONE` 等）。
2. **状态标记**：任务表统一用 `⬜ 未开始` / `🔄 进行中` / `✅ 完成`（**不**使用 `[ ]` 复选框语法）。
3. **活跃内容控制**：`plan.md` 活跃内容应 ≤ 150 行（硬上限 300 行）。
4. **即时清理**：Sprint 全绿后，整段移除 `Active sprint` 区块，笔记写入 `.cursorGrowth/archive/`，并在 `LAST_DONE` 记一行；历史 Sprint 不堆回工作板。
5. **先总后分**：先在 `plan.md` 定大方向，再在子任务中细化。

## 调度

- 结构类任务（改幕、调节拍、控节奏）在阶段 3 拆解后可委 **`novel-architect`** 出方案再落 plan。

## 反模式

- ❌ 任务超过 5 步不写 `plan.md`。
- ❌ 把 `plan.md` 当作历史记录（已完成任务不清理）。
- ❌ 自创 plan.md 格式或另建项目根 `plan.md`。
- ❌ 规划内容与 `.cursor/rules` 重复（规则应归位到 rules）。
- ❌ 任务分解粒度过粗（无法在一个 turn 内完成）。

## 关联
- **下游**：`novel-run`（执行流）
- **模板**：`.cursor/templates/plan.md`（schema 真源）
- **规则**：`00-novel-meta.mdc`（元规则）、`99-novel-archive.mdc`（归档）
- **命令**：`/nplan`
- **闸门**：`reference/universal-gates.md`
