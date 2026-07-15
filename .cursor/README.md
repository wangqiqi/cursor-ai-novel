# `.cursor` · 小说创作母版

> **本目录是小说编写 Cursor 工具链的唯一母版真源。**  
> 仓库：`cursor-ai-novel`  
> 同步基线：自 Formatted-Paradise `.cursor` 完整吸收（对齐 v0.65.1）

---

## 目录

| 层 | 路径 | 职责 |
|---|---|---|
| **Rules** | `rules/` | 红线与标准（alwaysApply / 按需） |
| **Skills** | `skills/` | 可执行流程 |
| **Agents** | `agents/` | 专项角色（被 skill 调度） |
| **Commands** | `commands/` | 用户入口（`/nhelp` `/nplan` `/nwrite` …） |
| **Config** | `config/` | `workflow.json` · `roles.json` |
| **Templates** | `templates/` | 卡片 / scaffold / plan / session |

完整命令路由：`commands/nhelp.md` · `skills/novel-plan/reference/routes.md`  
Agent 层级：`agents/README.md`

---

## 如何用于新小说项目

1. **复制母版**：将本仓库整个 `.cursor/` 复制到新项目根  
2. **建骨架**：在新项目中执行 `/nnew <项目名>`（调用 `novel-scaffold`）  
3. **项目特化**：只写进 `主题/` 与 `.cursorGrowth/`，**禁止**回写母版

```bash
# 示例（本机）
cp -a /home/jwzhou/workspace/cursor-ai-novel/.cursor /path/to/新小说项目/.cursor
cd /path/to/新小说项目
# 再在 Cursor 中 /nnew <项目名>
```

---

## 母版维护约定

1. **通用性**：不写具体书名、角色、绝对高潮章号  
2. **节奏窗**：只给比例公式（`skills/novel-plot/reference/opening-protocol.md`）；绝对章号只在各项目 `主题/_meta/节奏窗.md`  
3. **回灌**：某书沉淀出的通用技法，经授权后再合入本母版；项目偏好用 `/nlearn` 进 Growth  
4. **版本**：母版变更记入仓库根 `CHANGELOG.md`，并打 tag

---

## 铁律（摘要）

- 正文文件只含小说文稿；检测/批注进 `主题/_meta/`  
- plan 真源：`.cursorGrowth/plan.md`（见 `config/workflow.json`）  
- 中文交流；操作前确认绝对路径  
