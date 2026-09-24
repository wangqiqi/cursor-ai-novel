<!-- 工作副本：.cursorGrowth/plan.md（gitignore · 真源）· 模板 .cursor/templates/plan.md -->
<!-- 本模板是 plan.md schema 的唯一真源；/nplan /nrun /nloop 均按下列字段读取。 -->
<!-- ===== 机器可读字段：每行格式固定为  NAME: <值>  ，冒号后只写当前值，不要在此加说明 ===== -->
<!-- PLANNING: false -->
<!-- SPRINT: (none) -->
<!-- PLAN_APPROVED: (none) -->
<!-- AUTONOMOUS: true -->
<!-- SPRINT_STATUS: closed -->
<!-- ACTIVE: (none) -->
<!-- NEXT: (none) -->
<!-- LAST_DONE: (none) -->
<!-- MAX_LOOPS: 15 -->
<!--
  字段语义（不要在上一段的值行里写这些说明，否则机器读到的就不是纯值）：
    PLANNING        false | true                    是否正在做需求澄清 / 拆解
    SPRINT          (none) | <sprint 名>            当前 Sprint 名
    PLAN_APPROVED   (none) | true | false           /nrun 与 /nloop 的硬闸，须为 true 才可执行
    AUTONOMOUS      true | false                    false 时 /nloop 降级为单次 /nrun
    SPRINT_STATUS   planning | active | closed      /nloop 要求非 planning / closed
    ACTIVE          (none) | TASK-xxx               当前正在做的任务
    NEXT            (none) | TASK-xxx               下一个任务
    LAST_DONE       (none) | <一句话>                最近完成的事
    MAX_LOOPS       正整数                          本会话循环上限；缺省取 config/workflow.json → max_loops_default
-->

# Plan

无 Active Sprint。新开 → `/nplan`。闭合后笔记进 `.cursorGrowth/archive/`。

**真源**：仅 `.cursorGrowth/plan.md`（`config/workflow.json` → `plan_file`）。**禁止**在仓库根再维护第二份 `plan.md`。

**状态标记**：`⬜ 未开始` · `🔄 进行中` · `✅ 完成`（不使用 `[ ]` 复选框语法）。

**活跃内容**：≤ 150 行（硬上限 300 行）。

---

## Active sprint

（有进行中 Sprint 时写本区块；全绿后**整段移除**，笔记进 `.cursorGrowth/archive/`，并在 `LAST_DONE` 记一行。）

**Goal**: …

**Done when**: …

**Out of scope**: …

| ID | Task | Status | Acceptance |
|----|------|--------|------------|
| TASK-001 | … | ⬜ | … |

**执行顺序**: `TASK-001` → …

**偏差记录**（实际执行与计划不符时在此记一行）：

- …

---

## 下一 Sprint 候选

> 只列**候选**，不展开；挑中后才写入上方 Active sprint。按优先级排序（可选 1–2 条即可、不扩 scope）。

| 候选 | 为什么下一步 | 依赖 / 前置 | 预估 |
|------|-------------|------------|------|
| … | … | … | ≤5 步 |
