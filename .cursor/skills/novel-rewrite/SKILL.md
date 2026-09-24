---
name: novel-rewrite
description: 修订与精修流水线。提供从故事逻辑到文字校对的 5 轮修订框架。
disable-model-invocation: false
---

# 修订与精修 · novel-rewrite

> **"好小说是改出来的。"**
> 本技能提供一套系统性的修订流程，确保作品从粗糙走向精致。

## 触发场景

- "精修" / "通读改稿"
- 完成初稿后的系统性修订
- 针对特定问题的专项优化

## 5 轮修订流水线

### 第 1 轮：故事层 (Story)
- **焦点**：逻辑漏洞、节奏、动机。
- **动作**：检查主线自洽，删除不推动情节的废戏。

### 第 2 轮：场景层 (Scene)
- **焦点**：开场钩子、转折点、结尾衔接。
- **动作**：优化场景进入速度，确保每个场景都有信息揭示。
- **加厚 vs 瘦身**：目标相反，先对清单再动笔。加厚只补场面，不灌设定/开会课（`novel-plan/reference/universal-gates.md` §5）。

### 第 3 轮：文字层 (Line)
- **焦点**：去 AI 味、冗词、动词强度、节奏。
- **动作**：**调度 `novel-line-scanner` 扫描 → 由 `novel-line-rewriter` 只改 🔴 项**（含用户点名的 🟡）；拆分长句，替换虚词，增加感官细节。
- **注意**：`novel-rewrite` 的第 4 轮是**主题层**，不是文字层——不要把 scanner/rewriter 说成"第 4 轮"。

### 第 4 轮：主题层 (Theme)
- **焦点**：母题落地、意象呼应。
- **动作**：确保关键意象在结尾有回响，避免说教。

### 第 5 轮：校对层 (Proofread)
- **焦点**：错字、标点、格式、引号统一。

## 工作流
1. **备份**：覆盖正文前先留快照（**唯一推荐方式**）：
   ```bash
   python3 .cursor/tools/snapshot.py snapshot --note 修订-<章节>
   ```
   改坏了一键回滚：`python3 .cursor/tools/snapshot.py restore latest --yes`（会先给当前状态补安全快照）。归档命名见 `99-novel-archive.mdc` §六·五。
2. **机械先行**：`python3 .cursor/tools/check_manuscript.py` 先看字数/密度/长句/元数据/敏感词，避免把排版级问题当创作问题。
3. **专项修订**：按 5 轮顺序执行，每轮聚焦单一维度。
4. **验证**：调用 `novel-check`（章级闸门）或 `novel-continuity`（单维）验证修改效果。
5. **同步（独立调用时必做）**：更新 `CHANGELOG.md`；若属某个 `plan.md` 任务，同步勾 `✅` 与 `LAST_DONE`（`/nfix` 可脱离 `/nrun` 单跑，不能因此漏记）。
6. **报告落点**：修订报告只进 `.cursorGrowth/check/`（闭合迁 `archive/`）。

## 最小 diff
- 每轮只动该轮焦点；文字轮只改 🔴（用户点名的 🟡 除外）。
- 禁止「顺便」重写整章、改母题、改人物生死（须停问或另开 `/nplan`）。
- 覆盖前备份 `.cursorGrowth/archive/`。

## 反模式
- ❌ 一轮试图解决所有层级的问题。
- ❌ 不通读全篇就动手修改。
- ❌ 修改后不进行一致性验证。
- ❌ 扩大改动范围却仍标本轮完成。
- ❌ 加厚写成世界观讲义或多人轮流表态。

## 关联
- **上游**：`novel-chapter`
- **下游**：`novel-publish`
- **规则**：`01-novel-language.mdc`、`05-novel-style.mdc`、`08-novel-discipline.mdc`
- **命令**：`/nfix`
