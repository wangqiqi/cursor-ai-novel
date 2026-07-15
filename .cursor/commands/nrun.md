---
description: 【日常】按 `.cursorGrowth/plan.md` 执行（默认做事入口）。每步同步 `.cursorGrowth/plan.md` + CHANGELOG.md + 归档。
---

加载 skill **novel-run**：

```bash
# 前置检查（任一失败 → 停下来询问用户）
# 1. `.cursorGrowth/plan.md` 存在且「用户确认」已勾选
# 2. 当前在项目根目录
# 3. git 状态干净或明确
```

1. **模式识别** —— 关键词/路径/sprint 名字 → 自动选模式（🌐 世界观 / ✍️ 写作 / 🔍 检查 / 📦 工程）
2. **逐项执行** —— 读 plan.md「完成定义」→ 实现 → 自检 → 勾选
3. **同步** —— 每步必同步 `.cursorGrowth/plan.md` + `CHANGELOG.md`（重大步骤）+ `.cursorGrowth/archive/`
4. **收尾** —— 填执行记录 / 总结报告（完成 / 剩余 / 产出 / CHANGELOG 版本）

| 用这个 | 不是这个 |
|--------|----------|
| 已有 `.cursorGrowth/plan.md` · 按计划推进 | 没 `.cursorGrowth/plan.md` 或没确认 → **`/nplan`** |
| 修一致性 / 重写章节 / 审稿 | 还在想清楚要做什么 → **`/nplan`** |

**章节正文铁律**：报告 / 批注 / 复盘**永不**写入 `章节/` 文件，统一入口 `主题/_meta/第NN章_第SS节_复盘.md`（详见 `00-novel-meta.mdc` 第五节）。