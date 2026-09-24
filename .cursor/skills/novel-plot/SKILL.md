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
- **前置**：读 `主题/logline.md`（无则回退 `主题/主线剧情.md` §一）——本技能的上游产物必须落地回读，否则 logline 是死文件。
- **动作**：划分三幕占比（25% / 50% / 25%），确定中点反转与至暗时刻。

### 阶段 2：15 节拍填充 (Beat Sheet)
- **动作**：参考 Save the Cat 填充 15 个关键节拍。
- **要求**：每个节拍标注章节位置、场景摘要、情绪曲线。
- **落点**：写入 `主题/节拍表.md`（模板 `.cursor/templates/beat-sheet.md`）。`主题/主线剧情.md` §三 **只保留幕级分派与编号索引**（不再复制全表）；**结构真源是 `主题/节拍表.md`**（章前卡与 `/ncheck` 维度 3 按它定位）。

### 阶段 3：伏笔与冲突 (Planting & Conflict)
- **动作**：
    - 埋设 5-10 个关键伏笔，登记到 `主题/伏笔板.md`（模板 `.cursor/templates/foreshadow-board.md`；回退 `主题/_meta/伏笔板.md`），分配 `fs-NNN` 与「预期回收距离」。
    - 确保每场戏至少推进一个冲突轴（理念/权力/情感等），且弧内**冲突升级**；冲突轴登记在 `主题/主要冲突点.md`（可选；也可并入 `主题/主线剧情.md` §五 冲突轴）。
    - 规划关键节点的**钩子 + 爽点**（见 `reference/reader-rewards.md`）。
    - 按 `reference/opening-protocol.md` 换算并写入/更新 `主题/节奏窗.md`（无则回退 `_meta/`；开篇窗·中点·高潮区）。

## 输出
- **主输出**：`主题/主线剧情.md`（或更新已有大纲）。
- **配套**：`主题/节拍表.md` · `主题/伏笔板.md` · `主题/节奏窗.md` · `主题/主要冲突点.md`（可选）（路径见 `00-novel-meta.mdc` 资产登记表）。
- **多卷本**：`主题/分卷/第<VOL>卷_<卷名>.md`（模板 `.cursor/templates/volume-outline.md`）——全书 15 节拍只定一次，各卷做**分派**。
- **多线 / 群像**（Q4 = 多线 POV 或 Q5 = 多线交叉）：`主题/POV台账.md`（模板 `.cursor/templates/pov-ledger.md`）——线登记 / 视角切换规则 / **信息边界** / 各线微缩节奏窗 / 并轨点。
- **类型工艺**：按 `主题/总览.md` 的 Q1 调 `novel-genre` skill（推理 / 言情 / 仙侠体系 / 历史考据 / 喜剧五选，最多 3 份）。

## 调度

- 三幕占比、节拍密度、节奏曲线由 **`novel-architect`** 复核（尤其"卡在中段"时）。
- 类型工艺由 `novel-genre` 加载；文风原型由 `novel-style` 决定，本技能不替它们做审美。

## 反模式
- ❌ 缺少中点反转或至暗时刻。
- ❌ 伏笔只埋不收。
- ❌ 大纲过于细节，忽略了结构比例。
- ❌ 只挖坑不安排情绪兑现。
- ❌ 在母版写死绝对高潮章号。

## 关联
- **上游**：`novel-brainstorm`
- **下游**：`novel-chapter`、`novel-character`、`novel-genre`、`novel-check`（维度 3 主线对齐 / 维度 7 伏笔）
- **规则**：`02-novel-plot-design.mdc`
- **模板**：`.cursor/templates/beat-sheet.md` · `.cursor/templates/foreshadow-board.md` · `.cursor/templates/rhythm-window.md` · `.cursor/templates/volume-outline.md` · `.cursor/templates/pov-ledger.md`
- **参考**：`reference/reader-rewards.md` · `reference/opening-protocol.md` · `reference/emotion-craft.md` · `reference/commercial-hooks.md`（可选）
