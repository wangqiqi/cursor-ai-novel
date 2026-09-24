---
name: nloop
description: 【自主】持续循环：规划 → 执行 → 检查 → 归档。仅决策点 / 圈数上限停。
---

# /nloop · 自主推进循环

## 启动前硬闸（缺一不可）

读 `.cursorGrowth/plan.md` 头部与 `.cursor/config/workflow.json` → `autonomous`：

| 闸 | 要求 | 不满足时 |
|---|---|---|
| **PLAN_APPROVED** | 必须为 `true`（用户已「确认 / go / 开始」） | **停**：请用户批准或先 `/nplan`，禁止空跑 |
| **Active sprint** | 有未完成 TASK，或明确可自动规划的下一候选 | 无任务且无候选 → **退出**（见下） |
| **MAX_LOOPS** | 本会话累计循环 ≤ plan 头 `MAX_LOOPS`（缺省取 `.cursor/config/workflow.json` → `max_loops_default`，现为 **15**） | 触顶 → **停问人**，汇报已完成 / 剩余 |

`AUTONOMOUS: false` 时：本命令降级为单次 `/nrun` 语义，勿连跑。

## 核心逻辑

进入「自主推进模式」后，同会话按环自动推进，**勿每步问「要不要继续」**：

1. **规划** (`/nplan`) —— 仅当 Active 空、但有下一候选且无决策点时，可自动拆下一 Sprint；**新 Sprint 写完仍须把 `PLAN_APPROVED` 置回待确认并停问**（高风险例外见下表）。
2. **执行** (`/nrun`) —— 逐项完成 `.cursorGrowth/plan.md` 中 `NEXT` / 未完成 TASK。
3. **检查** (`/ncheck`) —— 写作类章/节完成后触发；框架类改 `.cursor` 则以完成定义自检为准。
4. **归档** (`/nlog`) —— 通过后更新 CHANGELOG；commit / tag / push **仅当** plan 的完成定义要求，且非用户禁止时执行。

每完成一环：更新 plan 头 `ACTIVE` / `NEXT` / `LAST_DONE`，循环计数 +1，再取下一任务。

## 🔴 瓶颈停顿（必须暂停问人）

与 `.cursor/config/workflow.json` → `autonomous.interrupt_on` / `confirm_before` 对齐：

| 打断 | 例子 |
|---|---|
| **decision_needed** | 核心设定变更 · 人物生死 · 重大剧情转向（= `confirm_before`） |
| **check_fail_twice** | 同一任务连续 2 轮 `ncheck` 不通过 |
| **blocker** | 缺前置输入 / 缺人物卡 / 缺章前卡 / 缺批准 plan |
| **goal_drift** | 范围蔓延、顺手改无关章/设定、静默扩大 Sprint |
| **max_loops** | 达到 `MAX_LOOPS` |

非上表事项：**同会话继续**下一任务。

## 退出条件

- 用户明确输入「停止」、「暂停」或「exit」。
- 当前 Sprint 全部达成，且无下一候选（或候选需新决策）。
- 触发「瓶颈停顿」任一项（含 `max_loops`）。
- `PLAN_APPROVED` 被置回非 `true`（例如新 Sprint 待批）。

## 用这个 / 不是这个

| 用这个 | 不是这个 |
|--------|----------|
| plan 已批准，想一口气推完 Sprint | plan 还在 `PLANNING` / 未批准 |
| 方向清楚，只需决策点打断 | 探索初期、频繁要对齐目标 |
| 单任务执行 | → `/nrun` |

**铁律**：自主模式下仍须遵守 `00-novel-meta.mdc` · `08-novel-discipline.mdc`；声称 check 过必须真跑；章节正文不含元数据。
