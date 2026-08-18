---
name: ncheck
description: 小说自洽性与完整性检查。调度多维度 agent 对章节进行深度审计。
---

# /ncheck · 自洽性检查

## 用法
```bash
/ncheck [章节号] [维度]
```

## 核心维度
- **角色一致性**：是否符合人物卡设定。
- **主线推进**：是否符合 15 节拍规划。
- **时间/量纲/伏笔**：日历、数字、标签是否闭环；字面清零后扫同义漏网。
- **哲学/母题**：是否扣中核心母题。

## 流程
1. 判定范围：章级 vs 全书 8 维 vs 专项（见 `universal-gates.md` §2）。禁止同范围全书 8 维连打。
2. 调度 `novel-check-master` 启动对应审计。
2. 生成三档决策（✅ 通过 / 🟡 有条件通过 / 🔴 不通过）。
3. 报告输出至 `.cursorGrowth/check/第NN章_ncheck.md`（闭合迁 `archive/`；禁止写入 `主题/`）。

## 关联
- **Skill**: `novel-check`
- **Agent**: `novel-check-master`
