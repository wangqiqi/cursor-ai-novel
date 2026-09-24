# Agents 索引 · 层级关系

> 本目录所有 agent 的层级关系、调用规则、协作模式。
> 创作时按需调用，避免重复调度。

---

## 一、Agent 总览（v0.49.0 起 · 8 个 agent）

| Agent | 层级 | 专长 | 调用入口 |
|-------|------|------|---------|
| `novel-architect` | 专项专家 | 三幕结构 / 节拍表 / 节奏控制 | `novel-plot` / `novel-plan` |
| `novel-character-coach` | 专项专家 | 人物弧光 / 核心命题闭环 / 关键台词与瞬间 | `novel-character` / `novel-check` |
| `novel-world-keeper` | 专项专家 | 三层世界观 / 闭合性 / 新概念注册 | `novel-world` / `novel-check` |
| `novel-line-scanner` | 专项专家 | 9 维八股检测 · **只扫描不改稿** | `/nwrite`（第 5 步 · 前置扫描） · `novel-check` · `novel-rewrite`（第 3 轮） |
| `novel-line-rewriter` | 专项专家 | 改稿 + 「去 AI 味」 · 必改项执行 | `/nwrite`（第 5 步 · 紧跟 scanner） · `novel-rewrite`（第 3 轮） · "去 AI 味" |
| `novel-continuity-sleuth` | 专项专家 | 跨章扫描 / 伏笔 / 时间·量纲 / 同义漏网 | `novel-continuity` / `novel-check` / `novel-rewrite`（每轮） |
| `novel-reader-simulator` | 专项专家 | 读者视角 / 代入感 / 节奏感 | `novel-check`（维度 8） · `novel-publish` |
| `novel-check-master` | **执行主控** | 聚合调度 **5 个专项 agent**（维度 6 内置） | `novel-check`（`/ncheck`） |

> `novel-line-editor` 已于 v0.49.0 拆分；**v0.63.1 删除 stub**，现行仅 `scanner` + `rewriter`。
> **计数口径**：本目录共 **8 个 agent** = 7 个专项专家 + 1 个执行主控；`novel-check-master` 去重后实际调度 **5 个**（character-coach / architect / world-keeper / continuity-sleuth / reader-simulator，其中 1·2 与 5·7 各复用同一 agent）。

---

## 二、层级关系

### 2.1 7 个专项专家（平行）

```
novel-architect               ← 结构专家
novel-character-coach         ← 人物专家
novel-world-keeper            ← 设定专家
novel-line-scanner            ← 扫描专家（只读）
novel-line-rewriter           ← 改稿专家（写）
novel-continuity-sleuth       ← 一致性专家
novel-reader-simulator        ← 读者视角专家
```

- **平行关系**：7 个专项专家是平行的，各自负责一个领域
- **不互调**：专项专家之间不互相调用（**例外**：`line-scanner` → `line-rewriter` 是合法协作链路）
- **被调度**：专项专家被各种 skill / command 调度

### 2.2 1 个执行主控

```
novel-check-master            ← 完整性检查主控
```

- **特殊位置**：唯一主控型 agent
- **职责**：聚合调度 **5 个专项 agent**（character-coach / architect / world-keeper / continuity-sleuth / reader-simulator）
- **被调度**：`novel-check` skill（8 维度主控 · `/ncheck`）

### 2.3 层级图

```
                  ┌────────────────────┐
                  │   novel-check      │ ← skill（最高层）
                  │   (8 维度主控)      │
                  └─────────┬──────────┘
                            ↓
                  ┌────────────────────┐
                  │  novel-check-      │ ← agent（执行主控）
                  │  master            │
                  └─────────┬──────────┘
                            ↓ 调度 5 个专项
        ┌──────────┬──────────┬──────────┬──────────┬──────────┐
        ↓          ↓          ↓          ↓          ↓
  architect  character  world-keeper  continuity  reader
                                （维度 1·2/5·7 各复用同一 agent）
  ※ line-scanner / line-rewriter 不在 8 维内：由 /nwrite 第 5 步与
    novel-rewrite 第 3 轮（文字层）调度
```

---

## 三、调用规则

### 3.1 触发词速查

| 触发词 | 调用的 agent | 模式 |
|--------|------------|------|
| "看结构 / 调整大纲 / 把控节奏" | `novel-architect` | - |
| "看人物 / 对白不顺 / 角色不像" | `novel-character-coach` | - |
| "检查设定 / 补充世界观 / 设定有漏洞" | `novel-world-keeper` | - |
| "扫一下 / 看一下 / 八股检测" | `novel-line-scanner` | 扫描 |
| **"去 AI 味" / "修一下"** | **`novel-line-scanner` → `novel-line-rewriter`** | 扫描+改稿 |
| **`/nwrite` 第 5 步（自动）** | **`novel-line-scanner` → `novel-line-rewriter`** | 扫描+改稿（强制） |
| "检查冲突 / 看伏笔 / 有没有矛盾" | `novel-continuity-sleuth` | - |
| "看读者反应 / 能不能打动 / 节奏拖" | `novel-reader-simulator` | - |
| "check / 自洽性 / 完整性" | `novel-check-master` | 主控 |

### 3.2 专项 ↔ 主控的反模式

- ❌ 直接调用 `novel-check-master` 做局部检查（应用专项专家）
- ❌ 手动一个个调度 5 个专项 agent 做完整检查（应用 `novel-check-master`）
- ❌ 在不该调 agent 的场景（如查文档、生成模板）硬调 agent

---

## 四、专项专家调用矩阵

| 入口命令 / skill | architect | character | world | line-scanner | line-rewriter | continuity | reader |
|------------------|-----------|-----------|-------|--------------|---------------|------------|--------|
| `novel-plot` | ✅ | - | - | - | - | - | - |
| `novel-character` | - | ✅ | - | - | - | - | - |
| `novel-world` | - | - | ✅ | - | - | - | - |
| `novel-chapter`（阶段 3） | - | - | - | **✅ 强制** | **✅ 强制** | - | - |
| `/nwrite`（第 5 步） | - | - | - | **✅ 强制** | **✅ 强制** | - | - |
| `novel-rewrite`（5 轮中的第 3 轮 = 文字层） | - | - | - | ✅（第 3 轮） | ✅（第 3 轮） | ✅（每轮） | - |
| `novel-publish` | - | - | - | - | - | - | ✅ |
| `novel-continuity` | - | - | - | - | - | ✅ | - |
| `novel-check`（8 维） | ✅ | ✅ | ✅ | ✅（点名时·不计分） | - | ✅ | ✅ |
| `novel-check-master`（主控） | ✅ | ✅ | ✅ | - | - | ✅ | ✅ |

> - ✅ 表示该 skill 调度此 agent
> - **加粗** = 强制调度（每节初稿完成后自动跑）
> - `line-scanner` 与 `line-rewriter` 是 v0.49.0 拆分后的新协作链路（同一轮内**先扫后改**）
> - **文字层不在 8 维内**：`novel-check` 默认不调度 scanner/rewriter；**仅当用户点名「去 AI 味 / 八股 / 密度」时**才调度，且**不计入 8 维评分**。常规去 AI 味走 `/nwrite` 第 5 步或 `novel-rewrite` 第 3 轮。

---

## 五、与 .cursor/ 其他层的关系

| 层 | 角色 | 与 agent 的关系 |
|---|---|---|
| **rules** | 约束（红线 / 标准） | agent 执行时**必须遵守** |
| **skills** | 流程（怎么做的步骤） | skill **调度** agent 执行特定任务 |
| **commands** | 入口（用户快捷方式） | command 调用 skill，再由 skill 调度 agent |
| **agents** | 角色（具备某项专长的实体） | 协作链路终点（agent → 改文件 / 出报告） |

完整链路：`command → skill → agent → 文件 / 报告`

---

## 六、新增 Agent 规范

1. **专一性**：一个 agent 只负责一个领域（不复合）
2. **可被调度**：必须能被至少一个 skill 或 command 调度
3. **不重复**：已存在的 8 个 agent 已覆盖主要领域，新增前先评估
4. **命名一致**：`novel-<角色>.agent.md` 格式
5. **有 description**：清晰说明触发词、专长、调用入口
6. **优先拆分而非合并**：单文件超过 ~200 行应优先考虑拆分为两个 agent（如 v0.49.0 的 line-scanner / line-rewriter）