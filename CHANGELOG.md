# CHANGELOG · cursor-ai-novel（小说 `.cursor` 母版）

> 倒序记录母版变更（最新在最上）。  
> 标签约定与小说项目一致；提交时与本文件同步打 tag。

---

## [v0.67.0] · 2026-08-18 · feat · 通用创作闸门（任意小说 SOP）

### 新增
- `skills/novel-plan/reference/universal-gates.md` · 跨书闸门真源（三层文档 / 检查范围 / 漏网 / 量纲 / 加厚 / 对白 / 发表三尺 / 外发硬伤 / CHANGELOG 纪律）

### 修改
- `00-novel-meta` · `08-novel-discipline` · `99-novel-archive`
- skills：`novel-check` · `novel-continuity` · `novel-chapter` · `novel-rewrite` · `novel-dialogue` · `novel-publish` · `novel-plan` · `routes`
- agents：`novel-check-master` · `novel-continuity-sleuth` · `agents/README`
- commands：`ncheck` · `nlog` · `nhelp`
- templates：`chapter-brief`（节长窗与加厚口径）
- `.cursor/README.md` 指向闸门真源

### 来源
- 消费仓通用技法回灌；**无**书名 / 角色 / 母题数字 / 本机路径

### 标签
`feat-gates` `docs-meta` `universal-gates`

---

## [v0.66.0] · 2026-08-17 · sync · 过程件落点 + 主题扁平路径回灌

### 变更（`.cursor`）
- **检测/批注/复盘** 只进 `.cursorGrowth/check/`（闭合迁 `archive/`）；**禁止**写入 `主题/` 或 `章节/`
- **常驻资产优先主题根**：章前卡 `主题/章节卡/` · 伏笔板/节奏窗/通用约束在 `主题/`；`主题/_meta/` 仅旧路径回退
- 对齐文件：`00-novel-meta` · `01-novel-language` · `02-novel-plot-design` · `08-novel-discipline`
- skills：`novel-check` · `novel-chapter` · `novel-plot` · `novel-scaffold` · `novel-continuity` · `novel-dialogue` · `novel-learn` · `opening-protocol`
- commands：`ncheck` · `nwrite` · `nrun` · `nplan`
- agents：`novel-line-scanner` · `novel-line-rewriter`
- templates：`chapter-brief` · `section-brief` · `rhythm-window` · `main-file` · `scaffold/主题/总览`
- `config/workflow.json` · `.cursor/README.md`

### 来源
- 消费仓通用口径回灌（对应其 CHANGELOG v0.97 过程件卫生）；无书名/角色/本机路径

### 标签
`sync-consumer-cursor` `docs-meta` `chore-path-hygiene`

---

## [v0.65.3] · 2026-07-15 · docs · 母版脱敏与开箱即用

### 修改
- 根 `README.md` · 去掉本机绝对路径与具体书仓叙事；改为 `git clone` + 相对路径复制流程
- `.cursor/README.md` · 同上；维护约定增加「禁止本机绝对路径」
- `rules/00-novel-meta.mdc` · 母版真源脱敏；AI 约束改为「勿写本机路径进母版」
- `commands/nnew.md` · Step 0 示例改为相对路径 / clone
- `skills/novel-scaffold/SKILL.md` · 去掉本机路径示例

### 历史脱敏
- 本文件既有条目中的本机绝对路径、具体消费仓书名改为通用表述

### 标签
`docs-desensitize` `docs-readme` `chore-portable`

---

## [v0.65.2] · 2026-07-15 · sync · 合并 `/nloop` 闸补强并双向对齐

### 合并自消费仓回流
- `config/workflow.json` · `interrupt_on` 增加 `max_loops`
- `rules/07-novel-persona.mdc` · 自治口诀对齐 `PLAN_APPROVED` / `MAX_LOOPS`

### 保留并回流（母版身份）
- `.cursor/README.md` · 母版说明
- `rules/00-novel-meta.mdc` · 「〇、母版真源」
- `commands/nnew.md` · Step 0 复制母版
- `commands/nhelp.md` · `config/README.md` · `skills/novel-scaffold/SKILL.md` · 母版指针

### 对齐
- 母版与消费仓 `.cursor/` 内容对齐

### 标签
`sync-consumer-cursor` `fix-nloop-gates` `chore-align`

---

## [v0.65.1] · 2026-07-15 · init · 吸收既有小说项目 `.cursor` 为母版真源

### 新增
- 完整迁入 `.cursor/`（rules · skills · agents · commands · config · templates）
- `.cursor/README.md` · 母版身份、新书复制流程、维护约定
- 根 `README.md` · 本仓库定位与开书步骤
- （本地）`.cursorGrowth/archive/` · 吸收说明归档 · 不入库

### 变更
- `rules/00-novel-meta.mdc` · 声明本仓库为母版真源
- `commands/nnew.md` · `skills/novel-scaffold/SKILL.md` · 新书必须先从本仓库复制 `.cursor/`
- `config/README.md` · 标注母版仓库名

### 来源
- 既有长篇消费仓的 `.cursor/`（对齐其 CHANGELOG v0.65.1；路径与书名不入库）

### 标签
`init-master-cursor` `absorb-consumer-cursor`

---
