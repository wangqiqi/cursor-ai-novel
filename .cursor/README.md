# `.cursor` · 小说创作母版

> **本目录是小说编写 Cursor 工具链的唯一母版真源。**
> 随仓库 `cursor-ai-novel` 分发。复制到新书项目根即可用，**不含本机绝对路径、不含具体小说内容**。

---

## 目录

| 层 | 路径 | 职责 |
|---|---|---|
| **Rules** | `rules/` | 红线与标准（alwaysApply / 按需） |
| **Skills** | `skills/` | 可执行流程 |
| **Agents** | `agents/` | 专项角色（被 skill 调度） |
| **Commands** | `commands/` | 用户入口（`/nhelp` `/nplan` `/nwrite` …） |
| **Config** | `config/` | `workflow.json` · `roles.json`（字段消费表见 `config/README.md`） |
| **Templates** | `templates/` | 卡片 / scaffold / 计划板 / 分卷 / POV 台账 |
| **Tools** | `tools/` | 7 个只读或受控脚本（见下表） |

完整命令路由：`commands/nhelp.md` · `skills/novel-plan/reference/routes.md`
Agent 层级：`agents/README.md`｜路径真源：`rules/00-novel-meta.mdc` 资产登记表

### Tools（全部仅标准库 · 不改正文）

| 脚本 | 作用 | 何时跑 |
|------|------|--------|
| `tools/check_integrity.py` | **母版自检**：断链 / 孤儿模板 / frontmatter / 配置一致性 / 资产登记表 | 每次改 `.cursor/` 后 |
| `tools/check_manuscript.py` | **正文机械校验**：字数 / 加粗密度 / 长句 / 连续短句 / `##` 标题 / 作者元叙事 / AI 套词 / 标点 / 元数据残留 / 敏感词 | 每节写完、改稿后、check 前 |
| `tools/snapshot.py` | **快照 · diff · 回滚**：`snapshot` / `list` / `diff` / `verify` / `restore` | 覆盖正文**之前**必留 |
| `tools/build_export.py` | **外发打包**：合并 Markdown · 分章 TXT · EPUB3（手写）· 统计报告 | `/npublish` 阶段 |
| `tools/analyze_style.py` | **风格指纹**：样本反推 8 轴 · 原型对比 · 生成风格档草稿 | 定风格 / 风格漂移排查 |
| `tools/check_continuity.py` | **连续性机械核对**（零 token）：退场角色再出场 · 资源再现 · 层级回退 · 伏笔超期 · 节奏配额 · 事件冷却；带豁免账本 | `/nwrite` 定稿后 · `/ncheck` 阶段 1 |
| `tools/selftest.py` | **守卫反向测试**：向临时副本投毒，确认每条守卫真的报警（守卫不响=回归） | 改完母版后必跑 |

```bash
python3 .cursor/tools/check_integrity.py          # 母版自检
python3 .cursor/tools/check_manuscript.py         # 正文机械校验（阈值读 主题/通用约束.md）
python3 .cursor/tools/snapshot.py snapshot --note 改稿前
python3 .cursor/tools/build_export.py --author "<署名>"
```

---

## 如何用于新小说项目

1. **复制母版**：将本仓库整个 `.cursor/` 复制到新项目根
2. **建骨架**：在新项目中执行 `/nnew <项目名>`（调用 `novel-scaffold`）
3. **项目特化**：只写进 `主题/` 与 `.cursorGrowth/`，**禁止**回写母版

```bash
# 假定母版仓与新书目录同级（按需改相对路径）
cp -a ../cursor-ai-novel/.cursor ./my-novel/.cursor
cp ../cursor-ai-novel/.gitignore ./my-novel/   # 可选
cd my-novel
# 用 Cursor 打开本目录后执行：/nnew <项目名>
```

### 新项目会得到什么（由 `/nnew` 生成）

| 位置 | 内容 |
|---|---|
| `主题/` | 总览 · 世界观 · 主线剧情 ·（哲学母题）· logline · 通用约束 · 节奏窗 · 伏笔板 · 敏感词表 · 风格档 · **连续性台账** |
| `主题/人物/` `主题/章节卡/` | 空目录占位 |
| `主题/分卷/` · `主题/POV台账.md` | 多卷本 / 多线时由 `novel-plot` 生成 |
| `章节/` | 正文目录 |
| `.cursorGrowth/` | `plan.md`（工作板）· `check/`（报告）· `learn/`（约定）· `archive/`（归档 + 快照） |
| 根 | `CHANGELOG.md` |

### 四条按需加载的扩展（不跑也不阻塞）

| 场景 | 入口 |
|------|------|
| 类型工艺（推理公平 / 感情线 / 境界体系 / 历史考据 / 喜剧笑点） | `skills/novel-genre/`（按 Q1 派发，最多 3 份） |
| 文风（想写成某一类） | `skills/novel-style/`（10 原型）· `tools/analyze_style.py` · `主题/风格档.md` |
| 书稿 > 30 万字，一次查不完 | `skills/novel-check/reference/chunked-scan.md`（分批 → 检查点 → 汇总） |
| 网文 / 出版 / 大章三种颗粒度 | `主题/通用约束.md` §1.1（决定「章」是什么） |
| 外发 EPUB / TXT | `tools/build_export.py` |

---

## 母版维护约定

1. **通用性**：不写具体书名、角色、绝对高潮章号；不写本机绝对路径
2. **节奏窗**：只给比例公式（`skills/novel-plot/reference/opening-protocol.md`）；绝对章号只在各项目 `主题/节奏窗.md`
3. **回灌**：某书沉淀出的通用技法，经授权后再合入本母版；项目偏好用 `/nlearn` 进 Growth。跨书 SOP 真源：`skills/novel-plan/reference/universal-gates.md`。
4. **版本**：母版变更记入仓库根 `CHANGELOG.md`，并打 tag
5. **改完必自检**：

```bash
python3 .cursor/tools/check_integrity.py
```

校验：规则 frontmatter/globs、skill/command/agent 头部字段、**全部交叉引用不断链**、孤儿模板、tools 语法、reference 体例、`novel-genre` 派发表完整性、**写—读配对**（防止"只写不读"的孤岛资产）、`role.default` / `MAX_LOOPS` / `learn_dir` 四处配置一致、资产登记表与 `templates/` 对齐。

---

## 铁律（摘要）

- 正文文件只含小说文稿；检测/批注/复盘进 `.cursorGrowth/check/`（**禁止**写入 `主题/` / `章节/`）
- plan 真源：`.cursorGrowth/plan.md`（schema 真源 `templates/plan.md`；禁止项目根第二份）
- 章级写完必须走 `/ncheck`；🔴 未清不得开下一章
- **覆盖正文前必须留快照**（`tools/snapshot.py snapshot`），否则不得改稿
- **「章」的颗粒度由 `主题/通用约束.md` §1.1 决定**（网文 A / 出版 B / 大章 C），节拍与节奏窗按它解释
- **`/nlearn` 沉淀的约定必须被读**：`.cursorGrowth/learn/` 是动笔前、改稿前、check 前的必读输入；写到不读 = 违纪
- **单一真源**：N 只在 `主题/总览.md`；节拍表只在 `主题/节拍表.md`；加粗白名单只在 `主题/通用约束.md` §3.1
- 主题弧线真源：`主题/主线剧情.md`（`总览.md` 只放摘要）
- 类型工艺按需加载（`novel-genre`）并**必须过 check 闸门**；不因类型降低验证标准
- **风格偏离必须显式声明**：未在 `主题/风格档.md` §三 登记的偏离一律 🔴；风格不得覆盖价值观与硬约束
- **只提炼风格特征，不照搬任何作家的具体文本**
- 中文交流；操作前确认**当前工作区**路径（勿把本机路径写进母版文档）
