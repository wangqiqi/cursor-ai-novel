# CHANGELOG · cursor-ai-novel（小说 `.cursor` 母版）

> 倒序记录母版变更（最新在最上）。  
> 标签约定与小说项目一致；提交时与本文件同步打 tag。

---

## [v0.68.0] · 2026-09-24 · fix · 工作流打通：入口可跑通、路径归一、报告落点唯一、母版可自检

> 主题：**让 `/nnew → /nplan → /nrun|/nloop → /nwrite → /ncheck → /nfix → /nlog → /npublish` 全链不断链、不互斥、不因缺资产停摆。**

### 新增

- `templates/constraints.md` · **通用约束**模板（字数窗 / 密度阈值 / 白名单 / 伏笔回收距离 / 黑名单）——此前被 6 处引用却从无创建者
- `templates/foreshadow-board.md` · **伏笔板**模板（`fs-NNN` / 预期回收距离 / 超期口径）——此前是"权威源"却无模板
- `templates/scaffold/.cursorGrowth/{archive,check,learn}/.gitkeep` · `templates/scaffold/主题/章节卡/.gitkeep`——补齐 scaffold 声称会建却不存在的目录
- `commands/npublish.md` · 外发打包入口（此前 `nhelp`/`routes` 指向 `novel-publish` 但无命令）
- `tools/check_integrity.py` · 母版自检：规则 frontmatter/globs、skill/command/agent 头部、**交叉引用断链**、孤儿模板、`role.default`/`MAX_LOOPS`/`learn_dir`/`persona_id` 一致性、资产登记表对齐
- `tools/check_manuscript.py` · 正文机械校验（加粗/长句/套词/元叙事；只读）；`tools/data/sensitive-words.example.txt` 为示例词表
- `tools/snapshot.py` · 改稿前备份；`tools/build_export.py` · 外发合并（配合 `/npublish`）
- `skills/novel-genre/` · 类型专项（推理公平 / 言情弧 / 力量体系 / 历史考据 / 喜剧工艺）
- `skills/novel-check/reference/chunked-scan.md` · 超长篇分批 8 维协议
- `templates/pov-ledger.md` · 多线 POV 台账；`templates/volume-outline.md` · 分卷大纲
- `templates/plan.md` 增 `下一 Sprint 候选` 区块与 9 个头部字段说明、状态标记图例

### 修复（按影响面）

- **入口可跑通**：`novel-scaffold` 补齐输出树与复制表（节奏窗/伏笔板/通用约束/logline/plan/目录），新增**重跑备份与"只补缺不覆盖"**；`/nnew` 附录改为**直接复制 `templates/plan.md`**（原自创格式导致 `/nloop` 的 `PLAN_APPROVED` 闸门读不到）
- **占位符**：`scaffold/主题/总览.md` 的选项清单改为真正的 `<Q1>`–`<Q6>` / `<N>` / `<日期>`；替换表与之对齐（原描述与实际模板互不匹配，会交付未替换的选项清单）
- **章节目录形状**：`novel-check` / `novel-dialogue` 读 `章节/第NN章_*.md` → 统一为 `章节/第NN章_<标题>/第SS节_<标题>.md`（与 `novel-chapter` 写入一致）
- **报告落点唯一**：子报告/主报告一律先落 `.cursorGrowth/check/`，Sprint 闭合才迁 `archive/`（修正 `novel-check` 三处自相矛盾 + `novel-continuity`/`novel-dialogue` 直写 archive + `novel-dialogue` 重复落两处）
- **agent 批注越界**：5 个专家 agent 删除"在当前工作文件旁追加批注"（会写进 `章节/`、`主题/`），统一为 check/ 下的单一路径模板
- **伏笔阈值三口径**：`02` 的「20/50 章」与 `novel-check`/`continuity-sleuth` 的「>10 章」冲突 → 统一为 `主题/通用约束.md` §四 ＞ 伏笔板单条 ＞ 母版默认
- **阶段编号**：`/nwrite` 的「第 4.5 步」与 `novel-chapter` 的「阶段 3.5」全部改为 **第 5 步 / 阶段 3**；scanner/rewriter 的"第 4 轮"改为 `novel-rewrite` **第 3 轮（文字层）**
- **plan 板 schema**：状态标记统一 `⬜/🔄/✅`（原 `[ ]→[x]` 与模板 `⬜` 冲突）；"历史 Sprint 索引"改为"整段移除 + 归档"；`git push` 改为仅在完成定义要求且用户同意时执行
- **主题弧线三处归属**：真源定为 `主题/主线剧情.md`（`总览.md` 只放摘要，`哲学母题.md` 展开内涵），修正 `00-novel-values` §4.1 与 `02` §五
- **断链/假引用**：`novel-logline`→`novel-brainstorm`、`novel-pitch`→`novel-publish`、`/nreview`→`/ncheck`、`skills/novel-run/reference/routes.md`→`../novel-plan/reference/routes.md`；`novel-scaffold/reference` 路径与非全路径 `universal-gates.md` 全部改全路径
- **规则 globs**：`04` 去掉永不匹配的 `主题/<哲学母题>.md`，补组织/地点条目；`03` 补 `人物关系矩阵.md`；`02` 补 `_meta/节奏窗` 与 `logline.md`；`01` 由 `**/*.md` 收窄为 `章节/主题`，并把"完全对齐 scanner"改为"子集摘要"、补 🟡 加粗带
- **孤儿模板**：删除重复的 `templates/main-file.md`（其进度表/伏笔索引/资产清单/反模式已并入 `scaffold/主题/总览.md`）；`beat-sheet.md` / `scene-card.md` 真正接进 `novel-plot` 阶段 2 与 `novel-chapter` 阶段 1，并纠正其虚假自引用
- **规则字段补齐**：`character-card`/`location-card`/`faction-card` 增「命名寓意」；scaffold `世界观.md` 概念表补齐 7 字段；`chapter-brief` 增「本章主运动」
- **归档命名文法**：统一为 `YYYYMMDD_HHMMSS_<功能>_<模块>[_<细分>...].md`（≥4 段即合法），消除 meta/99/各 skill 的 4/5/6 段之争
- **去不可核验引用**：`99` 与 `novel-plan` 的"用户规则 #6–#10"改为自描述条款
- **配置**：`workflow.json` → `growth.learn_sources` 与 `novel-learn` 对齐（补 `check/`、`plan.md`）；`templates/session/persona.json` 默认由 `professional` 改为 `dashu`；`config/README.md` 增**字段消费表**与一致性红线
- **文档**：`.cursor/README.md` 增新项目产物表与自检说明；`scaffold/README.md` 修正「3 个选择题」「生成根 plan.md」「轻量哲学先复制再删」三处事实错误

### 校验

- `python3 .cursor/tools/check_integrity.py` → **✓ 无错误，3 个警告**（规则 11 / skill 15 / command 12 / agent 9 / tool 4；警告为 3 份 reference 缺 `## 关联` 段）
- `/nnew` 骨架冒烟：按 scaffold 复制表临时建项 → `plan.md` 头部 9 字段齐、`check/learn/archive/章节卡` 就位、无残留选项清单

### 标签

`fix-workflow` `fix-links` `docs-meta` `add-templates` `add-tooling`

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
