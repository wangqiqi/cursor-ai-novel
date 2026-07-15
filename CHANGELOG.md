# CHANGELOG · cursor-ai-novel（小说 `.cursor` 母版）

> 倒序记录母版变更（最新在最上）。  
> 标签约定与小说项目一致；提交时与本文件同步打 tag。

---

## [v0.65.2] · 2026-07-15 · sync · 合并 FP `/nloop` 闸补强并双向对齐

### 合并自 Formatted-Paradise
- `config/workflow.json` · `interrupt_on` 增加 `max_loops`
- `rules/07-novel-persona.mdc` · 自治口诀对齐 `PLAN_APPROVED` / `MAX_LOOPS`

### 保留并回流（母版身份）
- `.cursor/README.md` · 母版说明
- `rules/00-novel-meta.mdc` · 「〇、母版真源」
- `commands/nnew.md` · Step 0 复制母版
- `commands/nhelp.md` · `config/README.md` · `skills/novel-scaffold/SKILL.md` · 母版指针

### 对齐
- 母版 ↔ Formatted-Paradise `.cursor/` 已 rsync 双向一致（同内容）

### 标签
`sync-fp-cursor` `fix-nloop-gates` `chore-align`

---

## [v0.65.1] · 2026-07-15 · init · 吸收 Formatted-Paradise `.cursor` 为母版真源

### 新增
- 完整迁入 `.cursor/`（rules · skills · agents · commands · config · templates，73 文件）
- `.cursor/README.md` · 母版身份、新书复制流程、维护约定
- 根 `README.md` · 本仓库定位与开书步骤
- （本地）`.cursorGrowth/archive/20260715_233820_吸收_Formatted-Paradise-cursor母版.md` · 不入库

### 变更
- `rules/00-novel-meta.mdc` · 声明本仓库为母版真源
- `commands/nnew.md` · `skills/novel-scaffold/SKILL.md` · 新书必须先从本仓库复制 `.cursor/`
- `config/README.md` · 标注母版仓库名

### 来源
- `/home/jwzhou/workspace/小说/Formatted-Paradise/.cursor`（对齐其 CHANGELOG v0.65.1）

### 标签
`init-master-cursor` `absorb-formatted-paradise`

---
