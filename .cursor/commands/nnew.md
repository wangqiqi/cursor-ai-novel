---
name: nnew
description: 新建小说项目骨架。调用 `novel-scaffold` skill 出 6 个关键选择题（主题/字数/文体/视角/结构/哲学深度），复制 `.cursor/templates/scaffold/` 模板到新项目根，生成骨架与初始文档。适用于全新项目启动。
---

# /nnew · 新建项目

## 用法

```
/nnew <项目名>
```

示例：
```
/nnew 长安拾梦录
/nnew 时间褶皱
/nnew 末代守夜人
```

> **设计原则**：6 个选择题（≤ 10 秒完成），不打断思路。所有选项都带"推荐"标签，可一键选默认。

---

## 执行流（5 步）

### Step 0 · 确认母版 `.cursor` 已就位

新项目根必须已有从 **母版仓库 `cursor-ai-novel`** 复制来的完整 `.cursor/`。

若缺失 → 先复制再继续（相对路径示例；按你的目录层级改 `../cursor-ai-novel`）：

```bash
# 先：git clone https://github.com/wangqiqi/cursor-ai-novel.git
cp -a ../cursor-ai-novel/.cursor <新项目根>/.cursor
```

母版说明见：母版仓 `.cursor/README.md` · `rules/00-novel-meta.mdc`「〇、母版真源」。

---

### Step 1 · 接收项目名

从 `/nnew <项目名>` 的参数中获取项目名（**不在交互中再问**）。

如未提供参数 → 提示：
> "请提供项目名：`/nnew <项目名>`"

---

### Step 2 · 调用 scaffold skill

加载并执行 `.cursor/skills/novel-scaffold/SKILL.md`：
- 出 6 个并行选择题（Q1-Q6）
- 收集答案 → 生成项目骨架
- 填充初始元信息

> **不在本命令中重复定义问题**。所有选项 / 元信息字段 / 模板变量替换逻辑都在 skill 内。

---

### Step 3 · 写初始文档

`scaffold` skill 完成后，本命令接管后续：

1. **`主题/总览.md`** —— 确认元信息已写入
2. **`CHANGELOG.md`** —— 写入初始条目
3. **`plan.md`** —— 写入 `.cursorGrowth/plan.md` 引导性任务

具体模板见下方「附录 · 初始文档模板」。

---

### Step 4 · 提示用户下一步

> "✅ 项目 `<项目名>` 骨架已建立！
>
> 已生成：
> - `主题/` —— 5 个核心文档（部分待填写）
> - `章节/` —— 空目录
> - `CHANGELOG.md` —— 初始版本
> - `.cursorGrowth/plan.md` —— 引导任务
>
> 下一步建议（用 `/nplan <任务>` 启动）：
> 1. **创建世界观** —— 填入 `主题/世界观.md`
> 2. **创建主线剧情** —— 填入 `主题/主线剧情.md`
> 3. **创建主角人物卡** —— 填入 `主题/人物/<主角>.md`
> 4. **开始写第一章** —— 用 `/nwrite 1 <标题>`"

---

## 附录 · 初始文档模板

### `CHANGELOG.md` 初始条目

```markdown
## [vX.Y.Z] · <日期> · 初始化 · 项目骨架建立

### 新增
- 项目骨架（来自 .cursor/templates/scaffold/）
- 主题/（世界观、主线剧情、总览 等）
- 章节/、.cursorGrowth/archive/

### 元信息
- 项目名：<项目名>
- 类型：<Q1 答案>
- 字数：<Q2 答案>
- 文体：<Q3 答案>
- 视角：<Q4 答案>
- 结构：<Q5 答案>
- 哲学深度：<Q6 答案>

### 标签
`init` `scaffold`
```

### `.cursorGrowth/plan.md` 引导任务

```markdown
# 计划 · <项目名> · 启动

## 第一步 · 用 /nplan 创建世界观
## 第二步 · 用 /nplan 创建主线剧情
## 第三步 · 用 /nplan 创建主角人物卡
## 第四步 · 用 /nwrite 1 开始写第一章
```

---

## 反模式（避免）

- ❌ 跳过 Step 0，用某本具体小说的 `.cursor` 冒充母版
- ❌ 在本命令中重新定义 6 个选择题（应调用 scaffold skill）
- ❌ 串行调用 6 个问题（必须并行，10 秒内完成）
- ❌ 在交互中再次问项目名
- ❌ 复制本项目特定内容到新项目（违反通用性）
- ❌ 不替换 `<项目名>` 占位符就交付

## 关联

- **母版真源**：仓库 `cursor-ai-novel` 的 `.cursor/`
- **核心 skill**：`novel-scaffold`（6 选题 + 元信息表）
- **基座模板**：`.cursor/templates/scaffold/`
- **元规则**：`.cursor/rules/00-novel-meta.mdc`
- **后续命令**：`/nplan`、`/nwrite`