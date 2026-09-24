# 基座模板 · `.cursor/templates/scaffold/`

> **新小说项目的骨架模板库**。
> 被 `/nnew` 命令 + `novel-scaffold` skill 引用，用于一键创建新项目。

---

## 一、目录结构

```
.cursor/templates/scaffold/
├── README.md                       # 本文件
├── .cursorGrowth/                  # 工作区占位（check / learn / archive）
├── 主题/                           # 主题层基座
│   ├── 人物/
│   │   └── .gitkeep
│   ├── 章节卡/
│   │   └── .gitkeep
│   ├── 世界观.md                   # 空模板
│   ├── 主线剧情.md                 # 空模板
│   ├── 哲学母题.md                 # 空模板（仅 Q6=深度时复制）
│   └── 总览.md                     # 模板（含元信息 `<Q1>`–`<Q6>` 占位）
└── 章节/
    └── .gitkeep
```

> 以下文件**不在**本目录，由 `/nnew` 从 `.cursor/templates/` 直接复制：
> `constraints.md` → `主题/通用约束.md`｜`foreshadow-board.md` → `主题/伏笔板.md`｜`rhythm-window.md` → `主题/节奏窗.md`｜`logline.md` → `主题/logline.md`｜`plan.md` → `.cursorGrowth/plan.md`

## 二、设计原则

1. **完全通用** —— 所有内容用 `<...>` 占位符，不绑定任何具体项目
2. **扁平化** —— 主题层资产全部在 `主题/` 下，避免多层目录嵌套
3. **基座而非内容** —— 这是骨架，不是文案。用户调用 `/nnew` 后，需自行填充
4. **不造第二份真源** —— 工作板只认 `.cursorGrowth/plan.md`；正文只认 `章节/`

## 三、使用方式

### 方式 1：通过 `/nnew` 命令（推荐）

```bash
/nnew <项目名>
```

命令会调用 `novel-scaffold` skill，**并行** `AskQuestion` 问 **6** 个关键选择题（Q1 类型 / Q2 字数 / Q3 文体 / Q4 视角 / Q5 结构 / Q6 哲学深度），然后：

1. 替换 `<项目名>` / `<Q1>`–`<Q6>` / `<N>` / `<日期>` 占位符
2. 复制 `scaffold/主题/` 与 `scaffold/章节/` 到新项目根（`哲学母题.md` 仅 Q6=深度）
3. 从 `.cursor/templates/` 生成 `通用约束.md` / `伏笔板.md` / `节奏窗.md` / `logline.md` / `.cursorGrowth/plan.md`
4. 建齐 `.cursorGrowth/{check,learn,archive}/`、`主题/章节卡/`、`主题/人物/`、`章节/`
5. 生成 `CHANGELOG.md` 初始条目

### 方式 2：手动复制

```bash
# 复制整个基座到新项目根目录
cp -r .cursor/templates/scaffold/主题/ <新项目>/主题/
cp -r .cursor/templates/scaffold/章节/ <新项目>/章节/
cp -a .cursor/templates/scaffold/.cursorGrowth/ <新项目>/.cursorGrowth/
# 再按上表补齐 templates/ 下的 5 个卡片模板
```

## 四、按 Q6 决定哲学母题文档

| Q6 选择 | 处理 |
|---------|------|
| 不需要独立母题 | **不复制** `哲学母题.md` |
| 轻量（主题层） | **不复制**；母题并入 `主题/世界观.md` 的哲学层 |
| 深度（独立母题文档） | 完整复制 `哲学母题.md` |

> 不要「先复制再标记未启用」——那会留下与规则冲突的空文件。

## 五、维护规则

- **修改模板前**：评估影响范围（是否破坏通用性）
- **新增占位符**：同步登记到 `skills/novel-scaffold/SKILL.md` §阶段 2 替换表
- **新增强制文件**：在 `rules/00-novel-meta.mdc` 资产登记表同步登记
- **删除文件**：需谨慎，先评估是否所有项目都需要
- **交付自检**：`grep -n '<[^>]*>' <新项目>/主题/` 不应出现选项清单
