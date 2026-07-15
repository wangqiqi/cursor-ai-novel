---
name: novel-plot
description: 剧情大纲设计。基于 Logline 扩展为三幕结构、15 节拍及伏笔板。
disable-model-invocation: false
---

# 剧情大纲设计 · novel-plot

> **"大纲是故事的骨架，节拍是故事的脉搏。"**
> 本技能负责将内核扩展为可操作的结构化大纲。

## 触发场景

- 已有 Logline，要展开为完整大纲
- 需要 15 节拍表（Beat Sheet）
- 卡在中段，需要重新规划节奏

## 工作流

### 阶段 1：三幕骨架 (Three-Act)
- **动作**：划分三幕占比（25% / 50% / 25%），确定中点反转与至暗时刻。

### 阶段 2：15 节拍填充 (Beat Sheet)
- **动作**：参考 Save the Cat 填充 15 个关键节拍。
- **要求**：每个节拍标注章节位置、场景摘要、情绪曲线。

### 阶段 3：伏笔与冲突 (Planting & Conflict)
- **动作**：
    - 埋设 5-10 个关键伏笔，记录在 `主题/_meta/伏笔板.md`。
    - 确保每场戏至少推进一个冲突轴（理念/权力/情感等），且弧内**冲突升级**。
    - 规划关键节点的**钩子 + 爽点**（见 `reference/reader-rewards.md`）。
    - 按 `reference/opening-protocol.md` 换算并写入/更新 `主题/_meta/节奏窗.md`（开篇窗·中点·高潮区）。

## 输出
- **主输出**：`主题/主线剧情.md`（或更新已有大纲）。
- **配套**：`主题/_meta/伏笔板.md` · `主题/_meta/节奏窗.md`。

## 反模式
- ❌ 缺少中点反转或至暗时刻。
- ❌ 伏笔只埋不收。
- ❌ 大纲过于细节，忽略了结构比例。
- ❌ 只挖坑不安排情绪兑现。
- ❌ 在母版写死绝对高潮章号。

## 关联
- **上游**：`novel-brainstorm`
- **下游**：`novel-chapter`、`novel-character`
- **规则**：`02-novel-plot-design.mdc`
- **参考**：`reference/reader-rewards.md` · `reference/opening-protocol.md` · `reference/emotion-craft.md` · `reference/commercial-hooks.md`（可选）
