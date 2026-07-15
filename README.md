# cursor-ai-novel · 小说编写 `.cursor` 母版

> 本仓库是 **小说创作 Cursor 工具链** 的母版真源。  
> 新建任何小说项目时，应整目录复制本仓库的 `.cursor/`，再使用 `/nnew` 搭骨架。

---

## 它是什么

从 Formatted-Paradise 的 `.cursor` **完整吸收**而来的通用框架（不绑定任何一部具体小说）：

| 组件 | 说明 |
|------|------|
| Rules | 元规则 / 价值观 / 语言 / 情节 / 人物 / 世界观 / 文风 / 象征 / 人格 / 纪律 / 归档 |
| Skills | plan · run · plot · chapter · character · world · check · rewrite · … |
| Agents | 8 个专项（architect / scanner / rewriter / check-master …） |
| Commands | `/nhelp` `/nplan` `/nrun` `/nloop` `/nwrite` `/ncheck` `/nfix` `/nnew` … |
| Templates | 章前卡、人物卡、scaffold、节奏窗、plan … |

入口帮助：`.cursor/commands/nhelp.md`  
母版说明：`.cursor/README.md`

---

## 快速开始 · 开一本新书

```bash
# 1. 建空项目目录
mkdir -p ~/workspace/小说/我的新书 && cd ~/workspace/小说/我的新书
git init

# 2. 复制母版 .cursor
cp -a /home/jwzhou/workspace/cursor-ai-novel/.cursor ./

# 3. 复制 gitignore 建议（可选）
cp /home/jwzhou/workspace/cursor-ai-novel/.gitignore ./

# 4. 在 Cursor 打开该目录，执行：
#    /nnew 我的新书
```

之后用 `/nplan` 想清楚 → `/nwrite` 写章 → `/ncheck` 自洽。

---

## 本仓库目录

```
cursor-ai-novel/
├── .cursor/              # ⭐ 母版真源（入库）
├── CHANGELOG.md          # 母版变更（倒序，入库）
├── README.md             # 本文件（入库）
├── .gitignore            # 忽略 .cursorGrowth/ 等
└── .cursorGrowth/        # 本地工作记忆（不入库）
    ├── plan.md           # plan 真源
    └── archive/          # 归档说明
```

**分层**：`.cursor/` 入库；`.cursorGrowth/` 永不 git 跟踪。  
**不包含**具体小说的 `主题/`、`章节/` —— 那些属于各书项目。

---

## 与 Formatted-Paradise 的关系

| 仓库 | 角色 |
|------|------|
| **cursor-ai-novel** | `.cursor` 母版；以后通用能力只在此演进 |
| Formatted-Paradise 等小说仓 | 消费母版；项目特化进 `主题/` / `.cursorGrowth/` |

从某书回灌通用技法到母版时：先改本仓库 → 再同步到各书的 `.cursor/`。

---

## 版本

当前对齐基线：**v0.65.1**（吸收自 Formatted-Paradise `.cursor`，2026-07-15）
