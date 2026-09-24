---
name: novel-scaffold
description: 新项目骨架搭建。基于 `.cursor/templates/scaffold/` 基座模板，用 AskQuestion 出 6 个关键选择题（主题/字数/文体/视角/结构/哲学深度），复制模板到新项目根，生成骨架。被 `/nnew` 命令调用。也可独立调用用于"重新生成项目元信息"。
disable-model-invocation: false
---

# 新项目骨架 · novel-scaffold

> **"6 个选择题定下全部项目基因。"**
> 本技能负责从项目名到骨架文件的完整初始化。

## 触发场景

- `/nnew <项目名>` 命令触发
- 用户说："新建项目" / "重新搭骨架" / "换一种类型试试"

## 前置条件

- 新项目根已有从母版仓库 **`cursor-ai-novel`** 复制的完整 `.cursor/`（见 `/nnew` Step 0）。
- 复制方式用相对路径或 `git clone` 后的仓根，**禁止**在文档/示例中写本机绝对路径。

## 输入

- **项目名**（必填，来自 `/nnew` 命令行参数）

## 输出

- 项目根目录下的骨架（**新建项目**的情形）：
  ```
  <项目根>/
  ├── 主题/
  │   ├── 人物/                    # .gitkeep 占位
  │   ├── 章节卡/                  # .gitkeep 占位（章前卡/节前卡）
  │   ├── 总览.md                   # 来自 scaffold（含元信息）
  │   ├── 世界观.md                 # 来自 scaffold
  │   ├── 主线剧情.md               # 来自 scaffold
  │   ├── 哲学母题.md               # ⭐ 仅当 Q6=深度时复制
  │   ├── 通用约束.md               # 项目阈值真源（templates/constraints.md）
  │   ├── 节奏窗.md                 # 按 Q2+N 换算（templates/rhythm-window.md）
  │   ├── 伏笔板.md                 # 空板（templates/foreshadow-board.md）
  │   └── 敏感词表.md               # 占位（tools/data/sensitive-words.example.txt）
  ├── 章节/                         # 空目录
  ├── .cursorGrowth/
  │   ├── archive/                  # 闭合归档
  │   ├── check/                    # 当前检测报告（所有检查 skill 的写入口）
  │   ├── learn/                    # /nlearn 项目约定
  │   └── plan.md                   # 工作板（复制 templates/plan.md，含头部闸门字段）
  ├── .cursor/                      # 来自母版仓 cursor-ai-novel（先复制再 /nnew）
  └── (其他由 /nnew 写入)
  ```
- **元信息表**（被 `/nnew` 用于填充 `总览.md` 与 `CHANGELOG.md`）

> **目录先建**：`.cursorGrowth/{archive,check,learn}/`、`主题/人物/`、`主题/章节卡/`、`章节/` 若不存在，先 `mkdir -p` 再写文件。**禁止**因目录缺失而跳过报告落点（所有报告只进 `.cursorGrowth/check/`）。

---

## 工作流

### 阶段 1 · 6 个关键选择题（并行 `AskQuestion`）

> **6 个问题全部并行**（同一 `AskQuestion` 调用中提交），用户一次性选完。
> **无 AskQuestion 工具时**：改为在正文用编号选项列表提问，一次性列全 6 题，收到答复后再继续（勿逐题串行）。

#### Q1 · 主题 / 类型

```yaml
question: "Q1. 这个项目的类型是？（影响后续推荐的世界观模板与示例）"
options:
  - label: "科幻（推荐）"
    description: "硬科幻 / 软科幻 / 赛博朋克 / 反乌托邦"
  - label: "奇幻"
    description: "高奇幻 / 低奇幻 / 仙侠 / 玄幻"
  - label: "现实 / 文艺"
    description: "严肃文学 / 现实题材 / 言情"
  - label: "悬疑 / 推理"
    description: "本格推理 / 社会派 / 惊悚"
  - label: "历史 / 架空"
    description: "历史小说 / 架空历史"
  - label: "混合类型"
    description: "多类型融合"
```

#### Q2 · 预计字数

```yaml
question: "Q2. 预计总字数？"
options:
  - label: "短篇（< 5 万字，推荐试水）"
    description: "适合实验性写作，节拍紧凑，约 3-15 章；建项后按 N 换算节奏窗"
  - label: "中篇（5-15 万字）"
    description: "标准商业小说长度，约 15-40 章；建项后按 N 换算节奏窗"
  - label: "长篇（15-50 万字）"
    description: "完整系列单本，约 40-120 章；建项后按 N 换算节奏窗"
  - label: "史诗（> 50 万字）"
    description: "多卷本；全书 + 卷内开篇窗均按公式换算，不写死前 N 章"
```

#### Q3 · 文体风格

```yaml
question: "Q3. 语言风格偏向？"
options:
  - label: "类型小说（推荐）"
    description: "快节奏 / 强情节 / 通俗易懂"
  - label: "严肃文学"
    description: "沉静 / 留白 / 注重内心与语言密度"
  - label: "古典 / 文言"
    description: "古典白话 / 韵文 / 章回体"
  - label: "网络 / 通俗"
    description: "轻快 / 短句 / 强情绪"
  - label: "实验 / 先锋"
    description: "打破常规 / 元叙事 / 跨形式"
```

#### Q4 · 主角视角

```yaml
question: "Q4. 主角叙事视角？"
options:
  - label: "紧贴第三人称（推荐）"
    description: "有限视角 + 内心独白 / 主流商业小说选择"
  - label: "第一人称"
    description: "主角自述 / 强代入 / 便于内心戏"
  - label: "全知视角"
    description: "上帝视角 / 多线并进 / 古典叙事"
  - label: "多线 POV"
    description: "多个角色轮流 / 群像 / 适合推理 / 史诗"
  - label: "非人类视角"
    description: "AI / 异族 / 神性 / 非常规视角"
```

#### Q5 · 叙事结构

```yaml
question: "Q5. 整体叙事结构？"
options:
  - label: "三幕标准（推荐）"
    description: "建立 / 对抗 / 解决 + 15 节拍 / 通用商业结构"
  - label: "起承转合"
    description: "中国古典 / 起 / 承 / 转 / 合 / 适合中短篇"
  - label: "英雄之旅"
    description: "12 阶段 / 召唤 / 试炼 / 回归 / 类型化强"
  - label: "自由结构"
    description: "无固定节拍 / 章节独立 / 散文诗式"
  - label: "多线交叉"
    description: "多视角交织 / 群像 / 适合长篇 / 推理"
```

#### Q6 · 哲学深度

```yaml
question: "Q6. 哲学深度？"
options:
  - label: "不需要独立母题（推荐）"
    description: "娱乐向 / 类型小说 / 重点在情节"
  - label: "轻量（主题层）"
    description: "有价值倾向，但不深究哲学。母题合并到世界观"
  - label: "深度（独立母题文档）"
    description: "严肃文学 / 实验文学。启用 哲学母题.md 独立文档"
```

> **所有选项都带"推荐"标签**，用户可一键选默认（科幻 / 中篇 / 类型 / 紧贴第三人称 / 三幕标准 / 不需要）。

#### Q2 追问 · 计划总章数 N 与颗粒度档

Q2 只给字数档，节奏窗还需要 **N** 与**颗粒度档**（见阶段 3b）。取值顺序：用户明确说过的章数 ＞ Q2 章数区间中值 ＞ 由「目标字数 ÷ 预估章均字数」取整。**不要为此再开一轮提问**，直接采用中值并在元信息表标注 `planned_chapters_source`，把档位写入 `主题/通用约束.md` §1.1。

---

### 阶段 2 · 模板变量替换

> **模板里的 `<Qn>` 占位符就是替换目标**。替换后不得残留 `<…>` 选项清单。

| 占位符 | 替换为 | 出现在 |
|---|---|---|
| `<项目名>` | 用户提供的项目名 | **6 份**：4 份 scaffold 文档（总览/世界观/主线剧情/哲学母题）＋ `主题/通用约束.md` ＋ `主题/伏笔板.md` |
| `<Q1>` | Q1 答案（只留选中项，如「科幻」） | `主题/总览.md` |
| `<Q2>` | Q2 答案（如「中篇（5-15 万字）」） | `主题/总览.md` |
| `<Q3>` | Q3 答案 | `主题/总览.md` |
| `<Q4>` | Q4 答案 | `主题/总览.md` |
| `<Q5>` | Q5 答案 | `主题/总览.md` |
| `<Q6>` | Q6 答案 | `主题/总览.md` |
| `<N>` | 计划总章数 N | `主题/总览.md`、`主题/节奏窗.md` |
| `<日期>` | 当前日期（`YYYY-MM-DD`） | `主题/总览.md`、`主题/通用约束.md` |
| `<YYYY-MM-DD>` | 同 `<日期>`（表单行内写法） | `主题/节奏窗.md`、`主题/通用约束.md` |

> **替换范围涵盖所有已复制文件**（含 `主题/通用约束.md`、`主题/伏笔板.md`），不只 `总览.md`。
> **交付前自检**：`grep -rnE '<(项目名|Q[1-6]|N|日期|YYYY-MM-DD)>' 主题/` 应 **0 命中**；再 `grep -n '<[^>]*>' 主题/` 确认只剩有意保留的正文占位（如「<待写>」）。

---

### 阶段 3 · 复制模板（新建 / 重跑两种模式）

**模式判定**：项目根是否已有 `主题/总览.md`。

| 情形 | 模式 | 要求 |
|---|---|---|
| 无 `主题/总览.md` | **新建** | 直接复制下表「总是」项 |
| 已有 `主题/总览.md` | **重跑** | **先备份**：把将被覆盖的文件复制到 `.cursorGrowth/archive/YYYYMMDD_HHMMSS_骨架重跑_<文件名>.md`；**已存在且非空的项目文档只补缺、不覆盖**（世界观/主线剧情/总览保留原文，仅补缺失章节） |

| 模板源 | 目标 | 条件 |
|---|---|---|
| `scaffold/主题/总览.md` | `主题/总览.md` | 总是 |
| `scaffold/主题/世界观.md` | `主题/世界观.md` | 总是 |
| `scaffold/主题/主线剧情.md` | `主题/主线剧情.md` | 总是 |
| `scaffold/主题/哲学母题.md` | `主题/哲学母题.md` | **仅 Q6 = 深度**（轻量 → 母题并入 `世界观.md`；不要先复制再删） |
| `scaffold/主题/人物/.gitkeep` | `主题/人物/` | 总是 |
| `scaffold/主题/章节卡/.gitkeep` | `主题/章节卡/` | 总是 |
| `scaffold/章节/.gitkeep` | `章节/` | 总是 |
| `templates/logline.md` | `主题/logline.md` | 总是（空白待填） |
| `templates/constraints.md` | `主题/通用约束.md` | 总是（阈值真源） |
| `templates/foreshadow-board.md` | `主题/伏笔板.md` | 总是（空板；`novel-plot` 后续填） |
| `templates/rhythm-window.md` | `主题/节奏窗.md` | 总是（自阶段 3b 填数） |
| `tools/data/sensitive-words.example.txt` | `主题/敏感词表.md` | 总是（占位，待按平台替换） |
| `templates/plan.md` | `.cursorGrowth/plan.md` | 总是（**保留头部闸门注释块**，勿自创格式） |
| `scaffold/.cursorGrowth/*/.gitkeep` | `.cursorGrowth/{archive,check,learn}/` | 总是（模板缺失时用 `mkdir -p` 兜底） |

> **禁止**在项目根写第二份 `plan.md`（真源只有 `.cursorGrowth/plan.md`）。

---

### 阶段 3b · 换算节奏窗（强制）

1. **先定颗粒度档**（写入 `主题/通用约束.md` §1.1）——按上架形态推荐：

   | Q2 / 用途 | 推荐档 | 含义 |
   |---|---|---|
   | 平台日更 / 追读制 | **A · 网文连载** | 2000–4000 汉字/章，1 章 ≈ 1 话 |
   | 实体出版 / 单本长篇 | **B · 出版长篇** | 6000–12000 汉字/章 |
   | 大章制 / 单章多场景（母版默认） | **C · 大章 / 卷** | 30000–60000 汉字/章 |

2. 确定 **N**（与用户确认计划总章数；**按所选档的"章"计数**，可用 Q2 章数区间中值作初稿）
3. 按 `skills/novel-plot/reference/opening-protocol.md` 选 `r_open`，算出开篇窗 / 中点 / 高潮区
4. 写入 `主题/节奏窗.md`
5. **禁止**把算出的绝对章号写回 `.cursor/` 母版

> `主题/总览.md`、`主题/节奏窗.md`、`主题/通用约束.md` 三处的 **N 与颗粒度档必须一致**；改档等于改全书标尺，须走 `/nplan`。

---

### 阶段 4 · 元信息填表（输出给 `/nnew`）

返回给 `/nnew` 命令的结构化元信息：

```yaml
project_name: <项目名>
type: <Q1 答案>
word_count: <Q2 答案>
style: <Q3 答案>
pov: <Q4 答案>
structure: <Q5 答案>
philosophy_depth: <Q6 答案>
planned_chapters: <N>
planned_chapters_source: <user | q2_midpoint | derived>
date: <日期>
needs_philosophy_doc: <Q6 == 深度>
granularity: <A | B | C>
rhythm_window_path: 主题/节奏窗.md
constraints_path: 主题/通用约束.md
foreshadow_board_path: 主题/伏笔板.md
logline_path: 主题/logline.md
sensitive_words_path: 主题/敏感词表.md
plan_path: .cursorGrowth/plan.md
```

`/nnew` 命令会用这个结构：
- 写入 `主题/总览.md` 的元信息字段
- 写入 `主题/节奏窗.md`
- 写入 `CHANGELOG.md` 初始条目
- 校验 `.cursorGrowth/plan.md` 已按 `templates/plan.md` 生成引导任务

---

## 反模式

- ❌ 串行调用 6 个问题（必须并行，10 秒内完成）
- ❌ 用 free-form 文本提问（应全部用 AskQuestion 选项；无工具时才退回编号选项）
- ❌ 在交互中再次问项目名
- ❌ 复制本项目特定内容到新项目（违反通用性）
- ❌ 不替换 `<项目名>` / `<Q1>`–`<Q6>` / `<N>` / `<日期>` 占位符就交付（会留下选项清单）
- ❌ Q6 = 轻量时仍复制 `哲学母题.md`（应合并到 `世界观.md`）
- ❌ 重跑骨架时覆盖已有 `主题/` 文档而不备份
- ❌ 只复制模板却不建 `.cursorGrowth/{archive,check,learn}/` 与 `主题/章节卡/`（后续报告无处落）
- ❌ 在母版 rules 写死「前 N 章」；节奏窗只进项目 `主题/`

## 关联

- **母版真源**：仓库 `cursor-ai-novel` 的 `.cursor/`
- **调用方**：`/nnew` 命令
- **基座模板**：`.cursor/templates/scaffold/`
- **卡片模板**：`.cursor/templates/`（`constraints.md` · `foreshadow-board.md` · `rhythm-window.md` · `logline.md` · `plan.md`）
- **开篇协议**：`skills/novel-plot/reference/opening-protocol.md`
- **元规则**：`.cursor/rules/00-novel-meta.mdc`（资产登记表 + 缺失资产降级协议）
