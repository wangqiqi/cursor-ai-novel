---
name: novel-style
description: 文风原型与风格指纹。按项目风格档加载对应原型参考，把"像谁"落成可测参数（句长/修辞/心理距离/留白），并管理对通用文风规则的合法偏离。当用户说"文风"、"风格太普通"、"想要某作家的味道"、"句子节奏不对"时使用。
disable-model-invocation: false
---

# 文风原型 · novel-style

> **"风格不是形容词，是一组可以被量出来的选择。"**
> 本技能不做审美判断，只负责把"想写成什么样"变成**参数 + 可验证的偏差**。

## 触发场景

- 用户说"文风"、"风格太平"、"想要冷一点的句子"、"节奏不对"、"比喻太多/太少"
- `/nnew` 之后定风格档（可跳过，但跳过后本技能不生效）
- `novel-chapter` 动笔前（读风格档目标）
- `novel-rewrite` 文字层（按风格档改，而非按通用审美改）
- `novel-check`（风格一致性由 `check_manuscript.py --style` 机械复核）

## 三层结构（别混）

| 层 | 文件 | 性质 |
|---|---|---|
| **数值层** | `tools/data/style-archetypes.json` | 10 个原型的 8 轴区间（**机器真源**） |
| **技法层** | `reference/<原型>.md`（本目录） | 每个原型的**怎么做**（人读参考） |
| **项目层** | `主题/风格档.md`（模板 `templates/style-profile.md`） | 本书的目标值 + **合法偏离声明** |

> 三层各司其职：原型给起点，技法给手法，风格档给**本书的承诺**。改数值只改 JSON；改本书目标只改风格档。

## 工作流

### 阶段 1 · 定风格（三选一）

| 入口 | 做法 |
|---|---|
| **有参照样本**（推荐） | 贴 1–2 千字 → `python3 .cursor/tools/analyze_style.py --sample <文件> --emit-profile` → 反推 8 轴数值 → 生成 `主题/风格档.md` 草稿 |
| **没样本，只想"像某类"** | `python3 .cursor/tools/analyze_style.py --list-proto` 挑原型 → 按其区间手填风格档 |
| **已有书稿想看看现状** | `python3 .cursor/tools/analyze_style.py --manuscript` → 看当前实际指纹 |

### 阶段 2 · 加载原型技法

读 `主题/风格档.md` 的「主原型」→ 加载 `reference/<主原型 file>.md`；有副原型再加载一份（**最多 2 份**）。
每份参考都含：原型签名 · 8 轴要点 · 可操作技法 · **最容易做砸的地方** · 合法偏离声明 · 自检清单。

### 阶段 3 · 落参数（不许只读不落）

| 落到哪 | 落什么 |
|---|---|
| `主题/风格档.md` §二 | 8 轴**本项目目标值**（原型区间为基础，可调） |
| `主题/风格档.md` §三 | **合法偏离声明**——豁免哪条规则 / 放宽幅度 / 理由 |
| `主题/通用约束.md` §九 | 风格登记（主副原型 + 一句话定位），供其他 skill 快速读取 |
| `主题/通用约束.md` §3.2 | 该原型的**禁用万能词**（`check_manuscript.py` 会机械扫） |

### 阶段 4 · 校验

```bash
python3 .cursor/tools/check_manuscript.py --style      # 与 主题/风格档.md 目标对比报偏差
python3 .cursor/tools/analyze_style.py --manuscript    # 看全书实际指纹
```

- 偏差落在**已声明的豁免**内 → 🟡 已声明豁免（不算违规）
- 偏差**未声明** → 🔴，须改文或补声明
- 风格是**分布**不是单点：只看平均句长会被长句掩盖，必须同时看标准差

## 合法偏离机制（本技能存在的核心理由）

`01-novel-language.mdc` 与 `05-novel-style.mdc` 的阈值是为"通用好文风"设的，**某些风格天然违反**：

| 原型 | 天然违反的规则 |
|---|---|
| 冷峻极简 | `01` §二.3「严禁连续 3 个以上短句」 |
| 绵密缠绕 | `01` §二.3「不超过 30 字长句」 |
| 奇喻感官 / 哥特压迫 | `01` §一（八股检测维度表）「形容词堆砌 🔴」 |
| 智性迷宫 | `05` §二「严禁元叙事发散」（仅限虚构档案，**不含**作品自身制作痕迹） |
| 散文化留白 | `02`「每章 ≥1 爽点 / 冲突必须升级」 |

**做法**：这些偏离必须在 `主题/风格档.md` §三**显式声明**（豁免哪条 / 放宽到多少 / 为什么本书需要）。
- 已声明 → `check_manuscript.py --style` 判 🟡（标明"已声明豁免"）
- **未声明 → 一律照 🔴 处理**，不得拿"这是风格"当免罪金牌

## 不得豁免的红线（任何风格都不能碰）

- `00-novel-values.mdc` 全部条款（价值观宪法）
- 正文不含元数据 / 批注 / 报告（`00-novel-meta.mdc` §二）
- 不美化暴力、犯罪、强迫；亲密描写需自愿清醒可撤回
- **不照搬任何作家的具体句子或段落**——只提炼特征，不复制文本

## 反模式

- ❌ 只抄词汇不学句法（做出"风格皮肤"，一读就假）
- ❌ 把风格当规则豁免的万能借口（未声明就偏离）
- ❌ 为凑指标机械堆短句/长句（风格是结果，不是 KPI）
- ❌ 同时加载 3 份以上原型（风格会糊）
- ❌ 中途悄悄改风格目标而不更新风格档（改档须走 `/nplan`）
- ❌ 让风格层覆盖价值观、伏笔回收、量纲一致性等硬约束

## 关联

- **参考（10 原型）**：`reference/cold-minimal.md`（冷峻极简 · 海明威/卡佛/余华）· `reference/dense-interwoven.md`（绵密缠绕 · 福克纳/普鲁斯特/金宇澄）· `reference/strange-metaphor.md`（奇喻感官 · 张爱玲/莫言/苏童）· `reference/cold-irony.md`（冷眼反讽 · 鲁迅/卡夫卡/简·奥斯汀）· `reference/lyric-whitespace.md`（散文化留白 · 沈从文/汪曾祺/萧红）· `reference/vernacular-folksy.md`（市井口语 · 老舍/王朔/刘震云）· `reference/intellectual-labyrinth.md`（智性迷宫 · 博尔赫斯/卡尔维诺/纳博科夫）· `reference/conceptual-grand.md`（概念宏大 · 刘慈欣/阿西莫夫/勒古恩）· `reference/gothic-oppression.md`（哥特压迫 · 爱伦·坡/洛夫克拉夫特/雪莉·杰克逊）· `reference/magic-daily.md`（魔幻日常 · 马尔克斯/鲁尔福/富恩特斯）
- **规则**：`05-novel-style.mdc` · `01-novel-language.mdc`（阈值可被合法偏离声明覆盖）
- **模板**：`templates/style-profile.md`
- **工具**：`tools/analyze_style.py` · `tools/data/style-archetypes.json` · `tools/check_manuscript.py`
- **技能**：`novel-chapter` · `novel-rewrite` · `novel-dialogue` · `novel-check` · `novel-genre`（类型与风格正交，可叠加）
