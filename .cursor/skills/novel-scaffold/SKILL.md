---
name: novel-scaffold
description: 新项目骨架搭建。基于 `.cursor/templates/scaffold/` 基座模板，用 AskQuestion 出 6 个关键选择题（主题/字数/文体/视角/结构/哲学深度），复制模板到新项目根，生成骨架。被 `/nnew` 命令调用。也可独立调用用于"重新生成项目元信息"。
---

# 新项目骨架 · novel-scaffold

> **"6 个选择题定下全部项目基因。"**
> 本技能负责从项目名到骨架文件的完整初始化。

## 触发场景

- `/nnew <项目名>` 命令触发
- 用户说："新建项目" / "重新搭骨架" / "换一种类型试试"

## 前置条件

- 新项目根已有从母版仓库 **`cursor-ai-novel`** 复制的完整 `.cursor/`（见 `/nnew` Step 0）。
- 母版路径示例：`/home/jwzhou/workspace/cursor-ai-novel/.cursor`

## 输入

- **项目名**（必填，来自 `/nnew` 命令行参数）

## 输出

- 项目根目录下的骨架：
  ```
  <项目根>/
  ├── 主题/
  │   ├── 人物/                    # .gitkeep 占位
  │   ├── 世界观.md                 # 来自 scaffold
  │   ├── 主线剧情.md               # 来自 scaffold
  │   ├── 哲学母题.md               # ⭐ 仅当 Q6=深度时复制
  │   └── 总览.md                   # 来自 scaffold（含元信息）
  ├── 章节/                         # 空目录
  ├── .cursorGrowth/archive/                      # 空目录
  ├── .cursor/                      # 来自母版仓 cursor-ai-novel（先复制再 /nnew）
  └── (其他由 /nnew 写入)
  ```
- **元信息表**（被 `/nnew` 用于填充 `总览.md` 与 `CHANGELOG.md`）

---

## 工作流

### 阶段 1 · 6 个关键选择题（并行 `AskQuestion`）

> **6 个问题全部并行**（同一 `AskQuestion` 调用中提交），用户一次性选完。

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

---

### 阶段 2 · 模板变量替换

| 占位符 | 替换为 |
|---|---|
| `<项目名>` | 用户提供的项目名 |
| `<Q1>` | Q1 答案 |
| `<Q2>` | Q2 答案 |
| `<Q3>` | Q3 答案 |
| `<Q4>` | Q4 答案 |
| `<Q5>` | Q5 答案 |
| `<Q6>` | Q6 答案 |
| `<日期>` | 当前日期（YYYY-MM-DD） |

---

### 阶段 3 · 复制模板

从 `.cursor/templates/scaffold/` 复制到新项目根：

| 模板 | 条件 |
|---|---|
| `主题/总览.md` | 总是 |
| `主题/世界观.md` | 总是 |
| `主题/主线剧情.md` | 总是 |
| `主题/哲学母题.md` | **仅 Q6 = 深度** |
| `主题/人物/.gitkeep` | 总是 |
| `章节/.gitkeep` | 总是 |
| `.cursorGrowth/archive/.gitkeep` | 总是 |
| `主题/_meta/节奏窗.md` | 总是（自 `.cursor/templates/rhythm-window.md` 复制后按 Q2+N 填数） |

---

### 阶段 3b · 换算节奏窗（强制）

1. 确定 **N**（与用户确认计划总章数；可用 Q2 章数区间中值作初稿）  
2. 按 `skills/novel-plot/reference/opening-protocol.md` 选 `r_open`，算出开篇窗 / 中点 / 高潮区  
3. 写入 `主题/_meta/节奏窗.md`  
4. **禁止**把算出的绝对章号写回 `.cursor/` 母版  

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
date: <日期>
needs_philosophy_doc: <Q6 == 深度>
rhythm_window_path: 主题/_meta/节奏窗.md
```

`/nnew` 命令会用这个结构：
- 写入 `主题/总览.md` 的元信息字段
- 写入 `主题/_meta/节奏窗.md`
- 写入 `CHANGELOG.md` 初始条目
- 写入 `.cursorGrowth/plan.md` 引导任务

---

## 反模式

- ❌ 串行调用 6 个问题（必须并行，10 秒内完成）
- ❌ 用 free-form 文本提问（应全部用 AskQuestion 选项）
- ❌ 在交互中再次问项目名
- ❌ 复制本项目特定内容到新项目（违反通用性）
- ❌ 不替换 `<项目名>` 占位符就交付
- ❌ Q6 = 轻量时仍复制 `哲学母题.md`（应合并到 `世界观.md`）
- ❌ 在母版 rules 写死「前 N 章」；节奏窗只进项目 `主题/`

## 关联

- **母版真源**：仓库 `cursor-ai-novel` 的 `.cursor/`
- **调用方**：`/nnew` 命令
- **基座模板**：`.cursor/templates/scaffold/` · `rhythm-window.md`
- **开篇协议**：`skills/novel-plot/reference/opening-protocol.md`
- **元规则**：`.cursor/rules/00-novel-meta.mdc`
