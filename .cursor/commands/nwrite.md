---
name: nwrite
description: 启动章节撰写。章前卡 → 节前卡 → 节正文。
---

# /nwrite · 写作

## 用法
```bash
/nwrite <章号> [节号] [标题]
```

## 流程
1. **读节奏窗**：优先 `主题/节奏窗.md`（回退 `_meta/`；无则按 `opening-protocol` 生成）；标注本章是否开篇窗/高潮区。
2. **章前卡**：目标 ≤3 · 节表 · **本章爽点 ≥1** · **章末钩子类型+钩子句** · 节奏窗位置。
3. **节前卡**：场景 · **本节爽点** · 节末钩子（含类型）。
4. **节初稿**：只写小说正文（可参照起承转爽）。**初稿关闭自我评判**：先完成再完善；精修走 `/nfix`。
5. **八股检测**：`novel-line-scanner` → `novel-line-rewriter`（报告进 `.cursorGrowth/check/`）。
6. **归档**：更新主线 / 伏笔板 / CHANGELOG。

## 🔴 铁律
- **正文严禁元数据**：报告、批注只进 `.cursorGrowth/check/`（禁止 `主题/` / `章节/`）。
- **密度硬约束**：`01-novel-language.mdc`。
- **无死章号**：开篇/高潮以项目节奏窗为准，不套母版「前 N 章」。
- **价值观**：爽点 = 有代价的情绪兑现（`00-novel-values`）。

## 关联
- **Skill**: `novel-chapter`
- **参考**: `skills/novel-plot/reference/opening-protocol.md` · `skills/novel-plot/reference/reader-rewards.md` · `skills/novel-plot/reference/emotion-craft.md`
- **规则**: `02-novel-plot-design.mdc` · `00-novel-values.mdc`
