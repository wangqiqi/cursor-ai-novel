# cursor-ai-novel · 小说编写 `.cursor` 母版

> 在 Cursor 里写长篇中文小说的**通用工具链母版**。  
> 复制 `.cursor/` 到任意新书项目 → `/nnew` → 即可开写。  
> **不含任何具体小说正文、角色或本机路径**；复制即用。

---

## 它解决什么

| 痛点 | 母版做法 |
|------|----------|
| AI 八股、翻译腔 | Rules + 扫描/改稿 Agent，改前备份 |
| 设定写崩、跨章打架 | `/ncheck` 多维自洽 + 伏笔追踪 |
| 想到哪写到哪 | `/nplan` → `/nrun` / `/nloop` 可执行工作流 |
| 每本书重造轮子 | **一次复制母版**，书专有内容只进 `主题/` |

---

## 快速开始（开箱即用）

```bash
# 1. 克隆母版（只需一次，可反复复用）
git clone https://github.com/wangqiqi/cursor-ai-novel.git
cd cursor-ai-novel   # 仅作「母版源」；不必在此写正文

# 2. 建新书目录，复制工具链
mkdir -p ../my-novel && cd ../my-novel
git init
cp -a ../cursor-ai-novel/.cursor ./
cp ../cursor-ai-novel/.gitignore ./   # 可选：忽略 .cursorGrowth/ 等

# 3. 用 Cursor 打开 my-novel，执行：
#    /nnew 我的新书
```

之后常用：`/nplan` 想清楚 → `/nwrite` 写章 → `/ncheck` 自洽 → `/nfix` 去 AI 味。  
迷路看：`/nhelp` 或 `.cursor/commands/nhelp.md`。

> **路径约定**：上例假定新书与母版仓为**同级目录**。若母版在别处，把 `../cursor-ai-novel` 换成你本机上的母版仓根即可——**文档中不写死任何绝对路径**。

---

## 里面有什么

| 组件 | 说明 |
|------|------|
| Rules | 价值观 / 语言 / 情节 / 人物 / 世界观 / 文风 / 象征 / 人格 / 纪律 / 归档 |
| Skills | plan · run · plot · chapter · character · world · check · rewrite · publish · … |
| 闸门 | `skills/novel-plan/reference/universal-gates.md`（任意小说 SOP） |
| Agents | architect / scanner / rewriter / check-master / continuity … |
| Commands | `/nhelp` `/nplan` `/nrun` `/nloop` `/nwrite` `/ncheck` `/nfix` `/nnew` … |
| Templates | 章前卡、人物卡、scaffold、节奏窗、plan … |

母版目录说明：`.cursor/README.md`

---

## 仓库结构

```
cursor-ai-novel/
├── .cursor/           # ⭐ 母版真源（入库 · 复制到新书）
├── CHANGELOG.md       # 母版变更（倒序）
├── README.md
├── .gitignore         # 建议一并复制到新书
└── .cursorGrowth/     # 本地工作记忆（不入库）
```

| 层 | 进 git？ | 放什么 |
|----|----------|--------|
| `.cursor/` | ✅ | 通用框架（禁止写具体书名/角色高潮） |
| `.cursorGrowth/` | ❌ | plan、归档、会话偏好 |
| `主题/` · `章节/` | 各书项目 | **本母版仓不含**；由 `/nnew` 在新书生成 |

---

## 母版 vs 小说项目

| | 母版仓（本仓库） | 小说项目（消费方） |
|--|------------------|-------------------|
| 职责 | 演进通用 `.cursor/` | 写一本具体的书 |
| 复制 | 被复制 | 复制 `.cursor/` 后 `/nnew` |
| 特化 | 禁止 | 只写 `主题/` / `章节/` / `.cursorGrowth/` |
| 回灌 | 接收经授权的通用技法 | 用 `/nlearn` 记项目偏好，不污染母版 |

**禁止**：从某一本已写小说里拷贝「长满特化内容」的 `.cursor/` 冒充母版。

---

## 版本

当前：**v0.67.0**（见 `CHANGELOG.md`）
