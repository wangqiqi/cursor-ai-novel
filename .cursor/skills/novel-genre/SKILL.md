---
name: novel-genre
description: 类型专项工艺。按项目类型（推理/言情/仙侠玄幻/历史架空/喜剧）加载对应工艺参考，把类型特有的硬约束落到章前卡、世界观登记与检查维度。当用户说"推理公平性"、"感情线推进"、"境界体系"、"考据/防穿越"、"笑点"或写作时发现类型特征需要专门处理时使用。
disable-model-invocation: false
---

# 类型专项 · novel-genre

> **"通用规则保证不塌，类型工艺决定好看。"**
> 本技能不做创作决策，只负责**把类型特有的硬约束找出来、落到可校验的位置**。

## 触发场景

- 用户点名类型问题："这推理公平吗" / "感情线太拖" / "境界体系崩了" / "好穿越" / "笑点太尬"
- `/nplan` 拆任务时识别到类型特征（Q1 已定）
- `novel-chapter` 阶段 0 填章前卡时，类型字段需要口径
- **`novel-check` 阶段 1/2 调度**（Q1 命中类型时**必调**；未加载即视为本次 check 未完成）
- `novel-dialogue` / `novel-rewrite` 需要类型工艺时

## 派发表（Q1 → 参考）

> Q1 真源：`主题/总览.md` 元信息表。可**多选**（混合类型同时加载）。

| Q1 类型 | 加载 | 落点 |
|---|---|---|
| 悬疑 / 推理 / 惊悚 | `reference/mystery-fairplay.md` | 章前卡「本节埋线 / 本节回收 / 读者当前可知」；伏笔板；`novel-check` 维度 3·6·7 |
| 现实 / 文艺 / 言情 | `reference/romance-arc.md` | 章前卡「本章关系位移 / 本章调性（甜·虐）」；人物卡 Need；`novel-check` 维度 1·6 |
| 奇幻 / 玄幻 / 仙侠（含系统流、异能） | `reference/power-system.md` | `主题/世界观.md` 或 `主题/<体系>.md` 的层级/代价登记；`novel-check` 维度 5 量纲与闭合 |
| 历史 / 架空 | `reference/historical-accuracy.md` | `主题/世界观.md` 或 `主题/<朝代>.md`；章前卡「本节考据风险点」；`novel-check` 漏网/量纲 |
| 喜剧向（或正剧需调性调剂） | `reference/comedy-craft.md` | 章前卡「本章调性」；`novel-dialogue` 断句；`novel-rewrite` 第 2 轮 |
| 混合类型 | 取交集，**最多同时加载 3 份** | 冲突处（如 推理×言情）以**主线类型**优先，副类型让位于节奏 |

> 无匹配类型 → 不加载任何参考，只走通用规则与闸门（这是正常的，不是失败）。

## 工作流

### 阶段 1 · 定类型（读，不猜）

1. 读 `主题/总览.md` 元信息表的 **Q1**；无该文件 → 视为类型未定，提示先 `/nnew` 或 `/nplan`。
2. 项目可覆盖：若 `主题/通用约束.md` §一 写明了子类型（如"本格推理"、"双男主言情"），**以它为准**。

### 阶段 2 · 加载参考并抽取硬约束

对每份加载的参考，抽出其中的**可校验项**，落到三个位置（不要只读不用）：

| 落到哪 | 落什么 |
|--------|--------|
| `主题/通用约束.md` | 类型阈值（如 推理的线索配比、言情的甜虐比、喜剧的笑点密度） |
| 章前卡 / 节前卡 | 类型字段（该类型要求的登记项） |
| `主题/世界观.md` | 类型设定登记（力量体系层级、架空规则、考据档） |

### 阶段 3 · 交接

- **写作类**：把类型字段写进 `novel-chapter` 阶段 0/1 的卡面。
- **检查类**：`novel-check` 阶段 1/2 必须调本技能；类型参考的检查清单**挂进既有维度**核验，核验结果与阈值回填 `主题/通用约束.md` §八。**Q1 命中类型而未加载参考 → 本次 check 未完成。**
- **修订类**：类型工艺问题在 `novel-rewrite` 对应轮次处理（结构→第 1–2 轮，文字→第 3 轮）。

## 边界（不做什么）

- ❌ 不新增检查维度（8 维不变；类型项挂在既有维度下）
- ❌ 不覆盖价值观宪法：类型参考里与 `00-novel-values.mdc` 冲突的内容一律以宪法为准
- ❌ 不写死章号：所有类型阈值用比例/区间
- ❌ 不因"类型需要"降低 `08-novel-discipline.mdc` 的验证标准
- ❌ 不为类型参考单独建 always 规则（保持按需加载）

## 反模式

- ❌ 把类型参考当"必读全文"塞进每一章（应按类型按需加载）
- ❌ 同一本书加载 4 份以上参考（主线会被稀释）
- ❌ 参考里读到的阈值不写进 `主题/通用约束.md` → 下章又凭感觉
- ❌ 用类型口味替代结构（如"这是爽文所以不用伏笔"）

## 关联

- **参考**：`reference/mystery-fairplay.md` · `reference/romance-arc.md` · `reference/power-system.md` · `reference/historical-accuracy.md` · `reference/comedy-craft.md`
- **规则**：`00-novel-values.mdc`（最高）· `02-novel-plot-design.mdc` · `04-novel-worldbuilding.mdc` · `05-novel-style.mdc`
- **技能**：`novel-plot` · `novel-character` · `novel-world` · `novel-chapter` · `novel-dialogue` · `novel-check` · `novel-rewrite`
- **模板**：`.cursor/templates/constraints.md` · `.cursor/templates/chapter-brief.md` · `.cursor/templates/volume-outline.md` · `.cursor/templates/pov-ledger.md`
- **配置**：`主题/总览.md`（Q1）· `主题/通用约束.md`
