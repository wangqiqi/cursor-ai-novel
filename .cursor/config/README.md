# config · 小说 .cursor

> 母版仓库：`cursor-ai-novel`（本目录随母版 `.cursor/` 一并分发）。

| 文件 | 用途 |
|---|---|
| `roles.json` | 12 人格语气（呼叫切换；能力不降级） |
| `workflow.json` | `plan_file`=`.cursorGrowth/plan.md` · archive/Growth · 自治打断 · 默认人格 |

会话覆盖：`.cursorGrowth/session/persona.json`（模板在 `templates/session/persona.json`）。
plan 模板：`.cursor/templates/plan.md` → 复制到 Growth 真源（schema 真源）。

---

## `workflow.json` 字段消费表

> 改字段前先看这里：**未被消费的字段改了不会有任何效果**。

| 字段 | 值 | 谁消费 |
|------|-----|--------|
| `profile` | `novel` | 母版标识（人类可读；无程序消费） |
| `plan_file` | `.cursorGrowth/plan.md` | `00-novel-meta.mdc` §三 · `novel-plan` · `novel-run` · `/nrun` · `/nloop` |
| `archive_dir` | `.cursorGrowth/archive` | `99-novel-archive.mdc` · `novel-check` 阶段 5 · 各改稿 skill 的备份 |
| `growth.enabled` | `true` | 说明 Growth 机制是否启用（人类可读） |
| `growth.dir` | `.cursorGrowth` | `00-novel-meta.mdc` 目录约定 |
| `growth.learn_dir` | `learn` | `novel-learn` 输出目录（`.cursorGrowth/learn/`） |
| `growth.learn_sources` | 源清单 | `novel-learn` §输入源（两处必须一致） |
| `autonomous.default` | `true` | plan 头 `AUTONOMOUS` 的缺省值（真实闸门在 plan 头） |
| `autonomous.max_loops_default` | `15` | `/nloop` 圈数上限缺省（plan 头 `MAX_LOOPS` 优先） |
| `autonomous.confirm_before` | 3 项 | `commands/nloop.md` 必须暂停问人的情形 |
| `autonomous.interrupt_on` | 5 项 | `commands/nloop.md` 打断表 |
| `role.default` | `dashu` | `07-novel-persona.mdc` · `config/roles.json` 的 `default` |
| `role.config` | `.cursor/config/roles.json` | 人格数据真源指针 |

### 一致性红线

- `role.default` 必须等于 `roles.json` 的 `default`（现均为 `dashu`）。
- `autonomous.max_loops_default` 与 `templates/plan.md` 头的 `MAX_LOOPS` 缺省值一致（现均为 `15`）。
- `growth.learn_dir` 与 `novel-learn` 的输出目录一致（`learn`）。
- `autonomous.interrupt_on` / `confirm_before` 与 `commands/nloop.md` 的停顿表逐项对应。

自检：`.cursor/tools/check_integrity.py` 会校验以上红线。
