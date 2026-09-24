# CHANGELOG · cursor-ai-novel（小说 `.cursor` 母版）

> 倒序记录母版变更（最新在最上）。  
> 标签约定与小说项目一致；提交时与本文件同步打 tag。

---

## [v0.73.0] · 2026-09-24 · feat · 吸收同类方案：上下文预算 · 连续性记账 · 配额制 · 改稿分级 · 评审校准

> 主题：先做**同类方案调研**（14 个长篇创作工具链 + 8 个风格/eval 方案 + 8 篇论文），
> 再只吸收**可被机械验证**的部分。明确不采纳的写在文末，避免"看起来很强但验不了"。

### 调研要点

| 来源 | 拿走的 |
|---|---|
| [ai-novelist](https://github.com/JIRBOY/ai-novelist) | 低上下文策略、节奏配额制、三级伏笔 |
| [inkflow 墨流](https://github.com/real-Elysia886/inkflow) | 两层审计（零 token 代码层 + LLM 层）、真相文件 |
| [oh-story](https://github.com/zenstory-ai/oh-story-claudecode)（7k★） | 12KB 硬上限上下文卡、机械 lint 先行、具体套式黑名单 |
| [long-novel-writer](https://github.com/jiaw-Zh/long-novel-writer) | **冻结分层摘要**（防"传话游戏"衰减）、append-only 账本 |
| [Novel-OS](https://github.com/mrigankad/Novel-OS) | **15 项确定性连续性检查**、**豁免账本**（★ 见下） |
| [novel-creator-skill](https://github.com/leenbj/novel-creator-skill) | 事件冷却矩阵、评审轮数上限 |
| [deai](https://github.com/wei125775-lab/deai) / [yotta-humanize](https://github.com/YottaMeta/yotta-humanize) | 标点与套词**具体阈值**、burstiness/CV 反均匀化 |
| [writing-skills](https://github.com/benjaminjackson/writing-skills) | surgical/substantive 分级、**评审校准方法论** |
| [WritingBench](https://github.com/X-PLUG/WritingBench) / [EQ-Bench](https://eqbench.com/creative_writing_longform.html) | 判官可靠性证据（动态 rubric 79–87% vs 静态 40–69%） |

### ① 上下文预算 + 冻结摘要（补的是我自己制造的债）

- `novel-chapter`「动笔前必读」在前几轮里被**我**越加越多（一度 10 行）。现改为：
  **必读 ≤ 6 行**（只放"不读就会写错"的源）+ **按需表**（命中才读）+ **单章实际打开 ≤ 4 个文件**。
- 新增 `[budget]` 守卫：必读表超 6 行 → **错误**；达上限 → 警告。**该守卫上线时立刻抓到 10 行的现状。**
- 新增**冻结分层摘要**（借 `主题/分卷/` 承接，不新增资产）：每 10 章由 `/nlearn` 追加 ≤200 字到
  「卷内滚动摘要（**只追加不覆盖**）」。滚动摘要反复重写会丢早期细节，冻结层是解药。

### ② 连续性记账 + 机械核对（本轮最大新增）

- 新资产 `主题/连续性台账.md`（模板 `templates/continuity-ledger.md`）：角色状态 / 境界层级 /
  资源账本 / 子线进度 / 节奏配额 / **豁免账本** 六张表。
- 新工具 `tools/check_continuity.py`（**零 token**，仅标准库），10 类检查：
  `dead-reappear` `resource-reappear` `progression-drop` `foreshadow-overdue` `quota-exceed`（🔴）
  `dormant-subplot` `absent-character` `fast-streak` `event-cooldown` `ledger-ahead`（🟡）
- **豁免账本**（来自 Novel-OS 的关键设计）：机械检查分不清"不可靠叙述者"和"写错了"。
  命中但已登记豁免 → 🟡。**没有这条，同一个非错误会每章被重报，作者最后不再看报告，工具就废了。**
- 纪律写进 `novel-check`：**机械核对跑在 8 维语义评审之前**，结论并入评审输入，不重复花 token。

### ③ 节奏配额制（防"剧情加速"）

单章实质推进项 **> 1 → 🔴**；连续 3 章快档 → 🟡；**事件冷却矩阵**（冲突刺激 2 / 关系深化 1 /
势力经营 2 / 世界观铺陈 3 / 张力升级 2 章）→ 🟡。阈值登记在 `主题/通用约束.md` §五。

### ④ 改稿分级 + 风格保护

`novel-rewrite` 现要求每处改动分级：**🩹 surgical**（保义收紧，可直接执行）vs
**⚠️ substantive**（改变说了什么/段落形状，须先列理由并确认）。
**风格保护条款**：会压平情绪或破坏风格档 §三 声明节奏的改动**不执行，只记录**——
风格档声明的偏离是签名，不是待修的错。

### ⑤ 评审校准方法论

`selftest.py` 新增 **★ 评审校准用例**：用**手写的已知坏样本**（套式+套词+10 连短句）与
**已知好样本**（干净散文）校准规则，断言"坏样本命中 ≥4 项且好样本零 🔴"。
这正是公开实践强调的做法——**判官要先证明能区分好坏**，否则会在它本该抓的失败上变绿
（本轮我就把 `NameError` 崩溃误读成"拦截成功"，正是反面教材）。

### 新增的正文规则（全部来自公开去 AI 味阈值）

- 标点**每章上限**：破折号 ≤ 4 · 省略号 ≤ 3 · 感叹号 ≤ 5（超 2 倍 → 🔴）
- **结构型套式**：`不是X，而是Y` · 否定排比（没有…，没有…）· `声音不大，却…`
- **弱化套词密度**：仿佛/一丝/缓缓/微微/轻轻/淡淡 合计 > 3/千字 → 🟡
- **反均匀化**：每 100 字应有 ≥1 个 ≤10 字短句；句长 CV < 0.25 → 🟡
- 套词表补：`涌上心头` `嘴角微微` `嘴角上扬` `一股`

### 明确不采纳（避免"看起来很强"）

- **多候选草稿择优合成**（novel-writer）：能力级新增、成本高，应先单章验证再谈。
- **向量库 / RAG / 知识图谱**：调研中多个项目**主动放弃**（NovelForge 明确说"标签检索比嵌入更准"），
  与母版"零依赖"定位冲突。
- **LLM 判官自动打分作为门禁**：WritingBench 证明动态 rubric 一致性 79–87%，但**仍不达可用门禁水平**；
  Ex3 报告标注者一致性低到 Kendall τ=0.178。**分数只作参考，不作门禁。**

### 校验

- `check_integrity.py` → ✓ 无错误（1 条预算警告：必读表已达上限 6 行，属预期提示）
- `selftest.py` → **✓ 27/27 全部按预期触发**（新增 4 例：评审校准 · 连续性检测 · 豁免降级 · 无台账不假报）
- 连续性核对手工验证：坏账本命中 5🔴+4🟡；登记豁免后 `dead-reappear` 降为 🟡（5🔴→4🔴）

### 标签

`feat-continuity` `feat-budget` `feat-quota` `feat-rewrite-grading` `feat-calibration` `research`

---

## [v0.72.0] · 2026-09-24 · fix · 第 4 轮全量审查：把"假绿灯"堵掉 + 补闭环

> 主题：**审查的真正对象不是文件，而是"工具说 ✓ 时它到底验了什么"**。
> 用 5 个独立只读审计（规则 / 23 份参考 / 5 个脚本 / 文档计数 / 写读闭环）交叉核对，
> 结果抓出**本会话自己引入的缺陷** + 一批**"绿灯泡装在坏电路上"**的工具问题。

### 🔴 工具层：假绿灯（最严重，会让坏稿通过）

| # | 问题 | 事实 | 修法 |
|---|---|---|---|
| T1 | **风格闸门可被排版绕过** | 目标写成 `10–16 字`（带单位）→ 解析到 0 个目标 → **退出码 0**；`10—16`/`5%–12%`/`约 12 字` 同样为 0 | 宽容解析（剥离单位与百分号、接受 `– — ~ ～ - 至 到`）；**解析不到目标一律按失败计** |
| T2 | **豁免可从备注列伪造** | 指标行备注写「见 §三 豁免」→ 该指标被判 🟡 并放行；示例行还会被当成真目标 | 豁免**只认「涉及指标」列**；示例/占位行在两个解析器里都跳过 |
| T3 | **空文件通过** | 0 汉字文件报 `✅` 且退 0 —— 截断章节一路绿灯 | 0 汉字判 🔴 `[empty]` |
| T4 | `--style` 被 `--json` 吞掉 | 文本模式退 1，`--style --json` 退 0 且 JSON 无 style 键 | JSON 也跑风格比对，判定写进载荷与退出码 |
| T5 | `RANGE_RE` 作用域错误 | 定义在函数内、被模块级函数使用 → `NameError`（我自己的回归，且首轮测试误读成"拦截成功"） | 提到模块级 |
| T6 | 破折号/省略号**虚高数倍** | `DASH="—－——"` 等自重字符被逐字符累加，2 个破折号算 6 次 | 改为**标记串**计数（`——` 算 1 次） |
| T7 | 比喻标记误报 | `如果/似乎/相似/比如/如此` 都算比喻，零比喻文本得 `16.18/百字` | 最长优先的非重叠匹配，剔除误报词 |
| T8 | `jargon_per_kchar` 名不副实 | 声明"专名术语密度"却只数拉丁字母 → **纯中文文本恒为 0**，`概念宏大` 目标 [8,30] 永不可达 | 补中文构词后缀启发式，并标注为代理指标 |
| T9 | `sense_priority` 声明了却从不比对 | 不在键集合里，读进来直接丢弃 | 纳入文本轴按相符判定 |
| T10 | 快照回滚**静默降级** | 快照缺文件时打 ✗ 仍退 0；回滚前安全快照失败被忽略（无退路）；`--paths 章节/第1章` 会吞掉 `章节/第1章续/` | 缺文件退 1；安全快照失败**中止回滚**；前缀匹配加路径分隔符 |
| T11 | `snapshot diff` 不能当门禁 | 有差异也退 0，且只在 `--paths` 时看新增文件 | 有差异退 1（同 `diff(1)`）；新增文件始终检查；快照缺文件不再崩 |
| T12 | EPUB 自检看不出格式错 | `testzip` 发现不了 XHTML 不良构；XML 非法控制字符原样写入；OPF 缺 EPUB3 必需 `dcterms:modified` | 写入前剥除 C0 控制字符；自检**逐个 XML 部件真实解析**；补 `dcterms:modified` |
| T13 | `--format` 未知静默无产出 | `--format epubx` 什么都不生成却退 0；书名含 `/` 静默建子目录 | 未知格式退 2；文件名净化；`--strip-structural` 从空开关变真开关 |
| T14 | 非 UTF-8 / 坏 JSON 直接崩 | 崩成 traceback 且退 1（与"有 🔴"撞码） | 优雅降级并明确报出编码/解析问题 |

### 🔧 自检器新增 4 条守卫（否则同类问题会再来）

- **`[clause]` 条款号校验**：`§` 引用必须指向真实存在的条款；支持规则简写（`02 §七`）与项目资产经模板映射（`主题/通用约束.md` → `templates/constraints.md`）。**当场抓出 7 处错引**。
- **`[glob]` 规则覆盖校验**：登记资产必须被**语义对口**的规则覆盖，不只被某条泛规则扫到。
- **`[axis]` 指标契约校验**：`_axes` 声明 ↔ `analyze_style` 实现双向比对 + 单位可读性。
- **`[write-read]` 泛化**：从"只查 learn/ 四个文件名"扩到**整张资产登记表**。

> 这四条不是装饰：`[axis]` 当场抓出 `style-archetypes.json` 被写坏（`avg_sentence_len` 单位成了 `段/公斤`、`jargon` 成了 `光年/平方秒`），`[clause]`/`[glob]`/`[write-read]` 各抓出一批真实缺陷。

### 🔗 闭环修复（写了没人读 = 白写）

| 资产 | 原状 | 修法 |
|---|---|---|
| `主题/POV台账.md` | **只写不读**，而 check 却声称核验"多线信息边界" → 章级闸门静默假通过 | `novel-chapter` 动笔前必读 + `novel-check` 阶段 1 必读 + 维度 6 增「信息边界越界 = 🔴」 |
| `主题/logline.md` | 只写不读（用户被要求填的空板永不生效） | `novel-plot` 阶段 1 前置动作改为读它 |
| `主题/分卷/…` | 只写不读（卷内节拍分派无人回读） | `novel-check` 阶段 1 读**当前卷**大纲 |
| 节前卡 / 场景卡 | 只写不读 | check 维度 6 增「节前卡 vs 该节正文」；动笔前必读补场景卡 |
| `session/persona.json` | **只读不写**（呼叫永远不生效） | `07-novel-persona.mdc` 增写入步骤 + `novel-scaffold` 复制模板 |
| `craft-notes/` | 只写不读 | `craft-intake` 增"收尾由 `/nlearn` 并入 writing-voice/rhythm" |
| `主题/推介包.md` | 未登记 | 资产登记表补行（标注人读交付物） |
| **风格原型技法层** | 10 份 reference 在执行步**无加载点**（只有数值层过闸） | `novel-chapter` 动笔前 / `novel-rewrite` 第 1 步增"按主原型加载 reference（最多 2 份）" |

### 🧩 风格层：机制在规则里不可见（本轮最关键的语义缺口）

- 实测：`01-novel-language.mdc` 提「风格档」**0 次**、`05-novel-style.mdc` **0 次**，而 `01` §二.3「连续 3 短句 / 30 字长句」正是被覆盖的对象 → **只读规则的 Agent 永远不知道豁免存在**。
- 修：`01` §三 新增 **3.1 阈值可被「合法偏离」声明式覆盖**（列明可覆盖条款 + 流程 + 判定口径 + 不可豁免红线）；`05` 全文重写（globs 加 `主题/风格档.md`、修过时的「唯一豁免」表述、`§二.2` 补元叙事局部豁免判据、`§三.3` 明确对白 20 字与叙述 30 字的取严关系）。

### 🩹 冻结的引用与数据错误

- `cold-irony` 的 JSON 豁免错引 `05 §四`（"大段内心独白"实际在 `05 §五`）；`magic-daily` 错引 `06`（应为 `04 §二` 且该处已改对，文件里的说明成了错的）；`intellectual-labyrinth` 宣称三个已存在的文件"尚未落地"、豁免字数与 JSON 不一致（40 vs 52）。
- `lyric-whitespace`/`gothic-oppression` 的豁免表**漏了长句豁免**且明文"其余一律照旧"，等于关掉自己唯一的合法出口；`gothic` 还把判定口径行冒充成豁免、轴号错位（"轴 5 与 7"应为轴 4）。
- `cold-minimal`/`gothic`/`intellectual` 的「8 轴要点」实际只有 6–7 轴（缺词汇指纹 / 叙述者态度），已补齐。
- 方言登记落点 `§3.1`（加粗白名单）→ 改为 `§六`；`strange-metaphor` 母题表挂错文件 → `主题/世界观.md`。

### 📐 规则与文档一致性

- `05` globs 补 `主题/风格档.md`；`02` globs 补 `主题/分卷/**`、`主题/POV台账.md`、`主题/章节卡/*.md`；`03` globs 补人物卡零层兜底。
- `00-novel-meta.mdc` **自相矛盾已修**：「不新增 `主题/` 子目录」vs 登记 `主题/分卷/`；`04`/`06` 的兜底 glob 语义收窄（不再要求 `风格档`/`敏感词表` 做概念注册与命名寓意）。
- `00-novel-values.mdc` 优先级表述自洽（宪法层 + 冲突裁决）；`01` 加粗密度补单位并标记为母版默认值。
- **agents/README 承诺的 6 处专家调度一个都不存在** → 真的接上（character-coach / world-keeper / continuity-sleuth / architect / reader-simulator）；修 scanner 的矩阵矛盾（点名时调度、不计分）。
- 计数过时：`.cursor/README` 与根 README「4 个脚本」→ 5；`nnew` 输出清单补 `风格档`/`敏感词表` 并改正核心文档数；`routes` 的"派发 5 份"→"5 类可选、最多同载 3 份"；`config/README` 字段消费表**如实标注 3 个字段其实无程序消费**；`nfix`/`nrun` 错字与重号步。

### ➕ 新增 `tools/selftest.py`：守卫的**反向测试**

> "自检通过"本身不是证据 —— 守卫写错了、或根本没触发，自检照样打印 ✓。
> 所以新增一个投毒测试：往 `.cursor/` 的临时副本注入每一类缺陷，确认对应守卫**真的报错**。
> **23/23 用例全部按预期触发**（含基线：干净副本必须零误报）。

它当场抓出两个**守卫自身的盲区**并已修：

1. `[link]` 的 `PATH_RE` 只扫 `md/mdc/json` → **悬空的 `.py`/`.txt` 引用无人管**（现扩到 `.py`/`.txt`，并给解析器补 `tools/`、`tools/data/` 候选目录）。
2. `[genre]` 只检查"目录里的文件有没有出现在派发表"，**删掉文件反而无人报**（现补反向校验：SKILL.md 点名的 `reference/*.md` 必须真实存在）。

### 校验

- `python3 .cursor/tools/check_integrity.py` → **✓ 无错误，0 警告**（规则 11 / skill 16 / command 12 / agent 8 / tool 6）
- `python3 .cursor/tools/selftest.py` → **✓ 全部守卫按预期触发 23/23**
- 5 个脚本语法与 `--help` 全通；新增 4 条守卫全部可复现（含投毒测试）
- 复现验证：8 种目标书写格式全部解析成功；备注列伪造豁免失效；空文件被拦；`--style --json` 退出码与文本模式一致；破折号/省略号不再虚高；比喻零误报；中文术语文本术语密度 > 0
- 端到端冒烟：骨架（含 `风格档`/`session/persona.json`）→ 脏节拦截 → 快照 diff 门禁 → 回滚复原 → 风格闸门拦截 → EPUB 全 XML 良构

### 标签

`fix-false-green` `fix-style-gate` `fix-closure` `feat-guards` `feat-selftest` `docs-meta`

---

## [v0.71.0] · 2026-09-24 · feat · 文风层：原型库 + 可测指纹 + 合法偏离机制

> 主题：**"作家风格"此前在母版里完全空白**（实测 `海明威/福克纳/张爱玲/鲁迅/马尔克斯/卡佛/意识流/魔幻现实…` 全 0 命中），唯一落点是个自由文本框。本轮把它做成第三层可测能力。
>
> 关键判断：**风格层不能只往里加内容**——`01-novel-language.mdc` 禁连续 3 短句、禁超 30 字长句，**恰好禁止海明威与福克纳**。所以必须有"合法偏离"机制，否则 Agent 会在"模仿风格"与"遵守规则"之间反复打架。

### 新增

- `skills/novel-style/SKILL.md` · 文风技能（定风格 → 加载原型 → 落参数 → 校验）
- `skills/novel-style/reference/` · **10 个风格原型**（各 93–119 行，共 1074 行）：冷峻极简（海明威/卡佛/余华）· 绵密缠绕（福克纳/普鲁斯特/金宇澄）· 奇喻感官（张爱玲/莫言/苏童）· 冷眼反讽（鲁迅/卡夫卡/简·奥斯汀）· 散文化留白（沈从文/汪曾祺/萧红）· 市井口语（老舍/王朔/刘震云）· 智性迷宫（博尔赫斯/卡尔维诺/纳博科夫）· 概念宏大（刘慈欣/阿西莫夫/勒古恩）· 哥特压迫（爱伦·坡/洛夫克拉夫特/雪莉·杰克逊）· 魔幻日常（马尔克斯/鲁尔福/富恩特斯）
  - 每份含：原型签名 · 8 轴要点 · 可操作技法 · **最容易做砸的地方** · 合法偏离声明 · 自检清单
  - **原型代号为主，作家名仅作括号注解**（母版保持通用；不出现任何书名/作品片段/角色名）
- `tools/data/style-archetypes.json` · 10 原型 × **20 个可测指标**的区间（机器真源）
- `tools/analyze_style.py` · **风格指纹分析**（仅标准库）：贴样本反推 8 轴数值 · `--proto` 与原型对比 · `--manuscript` 看全书实际 · `--emit-profile` 生成风格档草稿
- `templates/style-profile.md` · **风格档**（项目风格契约：8 轴目标 + 合法偏离声明 + 禁用万能词 + 情绪-句式映射）
- `check_manuscript.py --style` · **风格偏差闸门**：拿正文实际指纹与风格档目标比对

### 合法偏离机制（本层存在的核心理由）

- 偏离必须在 `主题/风格档.md` §三**显式声明**（豁免哪条 / 放宽幅度 / 理由 / 涉及指标）
- **已声明 → 🟡 已声明豁免；未声明 → 🔴 且计入失败**（退出码 1）
- 不得豁免的红线固定：价值观宪法 · 正文无元数据 · 不美化暴力 · **不照搬任何作家的具体文本**
- 10 个原型各带 2–3 条 `exemptions`（其中长句上限放宽 6 例、形容词密度 2 例、元叙事 1 例、爽点节奏 1 例，其余为"维持不变"声明），已在 JSON 逐条写清

### 修改

- `templates/constraints.md` · §六 增「可接受方言层」「风格档」行；§九 风格登记由风格档承接
- `rules/00-novel-meta.mdc` · 资产登记表增 `主题/风格档.md`
- `skills/novel-scaffold` · 复制表增 `templates/style-profile.md → 主题/风格档.md`（空板）
- `skills/novel-chapter` · 动笔前必读增风格档
- `skills/novel-rewrite` · 第 1 步"按风格档改，不按通用审美改"
- `skills/novel-check` · 阶段 1 增风格档；偏差由 `--style` 机械复核
- `skills/novel-dialogue` · 输入增风格档（对白句长/口语密度服从本档）
- `skills/novel-plan/reference/routes.md` · `commands/nhelp.md` · 路由增 文风原型 / 风格偏差
- `tools/check_integrity.py` · 新增 **风格层三层一致性**检查（JSON ↔ reference ↔ SKILL 派发表；目标指标必须在 `_axes` 定义）

### 修掉的两个自身缺陷（本轮测试抓出）

1. **风格档解析 bug**：把 §三 豁免表的行误当指标行，导致 `avg_sentence_len` **从未被比对**（"已比对 1 项"）。已改为：仅当 key 落在「指标」列且目标列是数值/区间才计入。
2. **模板示例造成静默豁免**：`style-profile.md` §三 的**示例行**写了真实指标名 → 任何新项目一复制就自带 `avg_sentence_len` 豁免，闸门形同虚设。已改为占位符 + 解析器跳过 `例：`／含占位符的行。实测：模板原样时 `exempt=set()`、两项均 🔴；补真声明后 `avg_sentence_len` 转 🟡、未声明项仍 🔴。
3. 另修正参考文件对规则条款号的错引（`05 §四`→`§二.2`、`01 §二.3 形容词堆砌`→`§一`、`06 设定闭合性`→`04 §二`、方言登记 `§3.1`→`§六`），并补齐 6 个原型的句长豁免声明。

### 校验

- `python3 .cursor/tools/check_integrity.py` → **✓ 无错误，0 警告**（11 规则 / 16 skill / 12 command / 8 agent / 5 tool）
- `analyze_style.py` 判别力实测：冷峻极简样本 → 平均句长 6.1 / 比喻 0 / 解释连接词 0；奇喻感官样本 → 句长 37 / 逗号密度 85.6
- 风格闸门实测：已声明 → 🟡；未声明 → 🔴 且退出码 1
- 10 份 reference 全查：无 frontmatter · 无绝对路径/URL · 无书名号 · 括号平衡

### 标签

`feat-style` `feat-archetypes` `feat-measurement` `fix-style-gate` `docs-meta`

---

## [v0.70.0] · 2026-09-24 · fix · 接闭环 + 并重复：让上一轮加的东西真正被用上

> 主题：两轮补功能之后，问题从"缺件"变成"**线没接上**"。本轮不加功能，只把断开的回环接上、把重复的真源并掉。

### 修复（闭环）

- **`/nlearn` 从写入孤岛变为真闭环**：此前 `.cursorGrowth/learn/` 四个文件**零读取方**，`/nlearn` 沉淀的声口/禁忌/拍板决策下一章不会被读回。现在 `novel-chapter`（动笔前必读）· `novel-rewrite`（第 1 步）· `novel-check`（阶段 1 资产清单）· `novel-dialogue`（输入）· `novel-run`（阶段 1）都显式读它，并写明"读到却不用 = 违纪"
- **`acceptance.md` 定为「完成定义」项目级真源**：`novel-run` 阶段 1 明确取值顺序 `plan.Acceptance` ＞ `.cursorGrowth/learn/acceptance.md` ＞ skill 默认
- **`check_manuscript.py` 真正读项目黑名单**：新增读 `主题/通用约束.md` §3.2 **与** `.cursorGrowth/learn/writing-voice.md` 的「禁套词/黑名单」小节 —— `/nlearn` 沉淀的禁忌从此会出现在机械校验里
- **修我上一轮引入的误报缺陷**：黑名单原先**全文任意位置匹配**，导致正常句子里的 `仿佛` / `似乎` / `不禁` 被误报。改为：硬套词（眼中闪过等）任意位置；**引导词/弱化句式只在句首或分句首命中**（符合 `01-novel-language.mdc` §二"以…开头的弱化句式"原意）。实测句中「他仿佛见过」不再报，句首「仿佛一切都停了」仍报 🟡
- **类型工艺进入检查闸门**：`novel-check` 阶段 1/2 与 `novel-check-master` 调度表增「附 · 类型」；**Q1 命中类型而未加载参考 → 本次 check 视为未完成**；核验结果与阈值回填 `主题/通用约束.md` **§八（新增）**

### 修复（并重复）

- **加粗白名单收敛为单一真源**：原为两处（`主题/通用约束.md` §3.1 与 `主题/世界观.md` 母题表），`novel-line-rewriter` / `novel-line-scanner` 共 5 处指向后者 → **误删白名单**风险。现 `通用约束` §3.1 为唯一真源，母题表须与其一致、冲突以 §3.1 为准；2 个 agent 的 5 处引用全部改指
- **15 节拍表去重**：`templates/beat-sheet.md` 与 `scaffold/主题/主线剧情.md` §三 原各存一张**完整 15 行表**（必然漂移）。`主线剧情` §三 改为**幕级分派 + 编号索引**的指针；`06-novel-symbolism` 与 `novel-plot` 的相关引用同步改指 `主题/节拍表.md`
- **「计划总章数 N」收敛为单一登记处**：原在 `总览` / `节奏窗` / `通用约束` 三处各存一份（我上一轮甚至写了条"三处必须一致"的红线来维护同步——写红线本身即症状）。现 N **只登记在 `主题/总览.md`**，`节奏窗` 与 `通用约束` 只引用，红线删除

### 新增（防回归）

- `check_integrity.py` 增 **`check_write_read_pairs()` 写—读配对守卫**：任何被 skill 写出的项目资产，必须至少有 2 个非写入方的读取方，否则自检报错。这条守卫在落地当天就抓出我自己 4 处"引用用了简写、守卫认不出"的问题并已修正
- `templates/constraints.md` 增 **§八 类型工艺**：登记已加载参考、主线类型、类型阈值与自检项（否则类型参考"读了不用"）
- `00-novel-meta.mdc` 资产登记表下增**写—读配对**说明

### 校验

- `python3 .cursor/tools/check_integrity.py` → **✓ 无错误，0 警告**（含新增的写—读配对守卫）
- `check_manuscript.py` 定向验证：句中 `仿佛`/`似乎` 不再误报；句首 `仿佛` 报 🟡；`通用约束` §3.2 与 `learn/writing-voice.md` 禁套词共 4 条全部命中 🔴
- 端到端冒烟（临时项目）：骨架 0 残留占位 · 脏节被拦（退出码 1）· 干净节通过 · 快照回滚复原 · EPUB 6 条目 `mimetype` STORED `testzip` 干净 · 新书视角自检通过

### 标签

`fix-loop-closure` `fix-single-source` `fix-false-positive` `add-guard` `docs-meta`

---

## [v0.69.0] · 2026-09-24 · feat · 能力补强：写作侧机械校验 · 分批检查 · 类型工艺 · 导出与回滚 · 颗粒度预设

> 主题：回答「**足够写任意小说吗**」中"不够"的四块——P0 机械校验与规模化、P1 类型特化与多卷多线、P2 外发落地与安全回滚、P3 章节颗粒度。

### 新增

- `tools/check_manuscript.py` · **正文机械校验**（写作侧，只读）：字数（节/章/全书）· 加粗密度（双档 🟡/🔴）· 长句 · 连续短句 · `##` 标题白名单 · 作者元叙事 · AI 套词 · 半角标点/引号 · 元数据残留 · 敏感词；阈值自动读 `主题/通用约束.md`，`--json` 可机器消费
- `tools/data/sensitive-words.example.txt` · 敏感词表**格式示例**（占位；真实词表按平台放 `主题/敏感词表.md`）
- `tools/snapshot.py` · **快照 / diff / verify / restore**（`manifest.json` 存逐文件 sha256 + 字数；`restore` 前自动补安全快照）
- `tools/build_export.py` · **外发打包**：合并 Markdown · 分章 TXT · **手写 EPUB3**（`mimetype` STORED · container · opf · nav · 样式表）· 统计报告；仅标准库
- `skills/novel-check/reference/chunked-scan.md` · **分批检查协议**（分批 → `check/` 中间检查点 + 跨批状态 → 只读检查点汇总），解决 30 万字以上一次读不完
- `skills/novel-genre/SKILL.md` + 5 份类型工艺参考：`mystery-fairplay.md`（公平线索/诡计）· `romance-arc.md`（关系推进/甜虐/同意红线）· `power-system.md`（层级/代价/通胀防治）· `historical-accuracy.md`（考据分级/防穿越）· `comedy-craft.md`（笑点机制/避雷）
- `templates/volume-outline.md` · **分卷/分部大纲**（卷功能 · 节拍分派 · 冲突升级链 · 卷末不可逆）
- `templates/pov-ledger.md` · **POV 台账**（线登记 · 切换规则 · **信息边界防越界知情** · 各线微缩节奏窗 · 并轨点）
- `templates/constraints.md` §1.1 · **颗粒度三档预设**（A 网文 / B 出版 / C 大章·卷），把「章是什么」变成显式约定

### 修改

- `rules/00-novel-meta.mdc` · 资产登记表增 `分卷/` · `POV台账.md` · `敏感词表.md`；「章」的颗粒度指向 `通用约束` §1.1
- `rules/99-novel-archive.mdc` · 新增 §六·五 **快照与回滚（强制）**：覆盖正文前必须留快照；检查清单同步
- `skills/novel-plot` · 输出增 分卷大纲 / POV 台账 / 类型工艺；模板与下游接线
- `skills/novel-chapter` · 字数与节数改为**读颗粒度档**；补机械校验入口
- `skills/novel-check` · 超长篇走分批协议；机械项先行（文字层仍不入 8 维）
- `skills/novel-plan/reference/universal-gates.md` · §2 增「分批扫描」闸与机械先行
- `skills/novel-plot/reference/opening-protocol.md` · §1 增**颗粒度档**，明确 N 的含义随档变化
- `skills/novel-publish` · 阶段 2 改为 `build_export.py` 一键打包（EPUB/TXT/MD + 统计）；DOCX 标注为需 pandoc 的可选路径
- `skills/novel-rewrite` · 工作流加**机械先行**与快照回滚
- `skills/novel-scaffold` · Q2 追问增颗粒度档；复制表增 `主题/敏感词表.md`；阶段 3b 按档推荐并强调 N 一致性
- `skills/novel-plan/reference/routes.md` · `commands/nhelp.md` · 扩展路由增 类型工艺 / 分批 / 机械校验 / 快照 / 导出
- `agents/novel-line-rewriter.agent.md` · 备份步骤改为快照工具 + 改完机械复扫
- `templates/constraints.md` · §一 拆为「颗粒度档 + 篇幅结构」并加三处 N 一致性红线
- `tools/check_integrity.py` · 新增 tools 语法检查、reference 体例检查、`novel-genre` 派发表完整性；修复 `.cursor/` 前缀解析与警告重复触发
- `.cursor/README.md` · 新增 Tools 表、扩展入口表、铁律补快照/颗粒度/类型；根 `README.md` 同步

### 校验

- `python3 .cursor/tools/check_integrity.py` → **✓ 无错误，0 警告**（11 规则 / 15 skill / 12 command / 8 agent / 4 tool）
- 四项能力逐一冒烟（临时项目，全部通过）：
  - **骨架**：复制表落地；无残留占位符；颗粒度档 A 正确写入
  - **机械校验**：脏节被拦下（`## 场景二` / 镜头术语 / 眼中闪过 → 退出码 1）；干净节 ✓
  - **快照**：snapshot → 改坏 → diff（+1/−7）→ restore 复原成功
  - **导出**：EPUB 结构自检通过（`mimetype` STORED、6 条目、`testzip` 干净）；分章 TXT 与合并 MD 章标题正确、无重复 H1
- 新书视角自检同样通过（仅 1 条"根尚无 CHANGELOG.md"提示，属预期）

### 标签

`feat-tooling` `feat-genre` `feat-chunked-scan` `feat-export` `feat-granularity` `docs-meta`

---

## [v0.68.0] · 2026-09-24 · fix · 工作流打通：入口可跑通、路径归一、报告落点唯一、母版可自检

> 主题：**让 `/nnew → /nplan → /nrun|/nloop → /nwrite → /ncheck → /nfix → /nlog → /npublish` 全链不断链、不互斥、不因缺资产停摆。**

### 新增

- `templates/constraints.md` · **通用约束**模板（字数窗 / 密度阈值 / 白名单 / 伏笔回收距离 / 黑名单）——此前被 6 处引用却从无创建者
- `templates/foreshadow-board.md` · **伏笔板**模板（`fs-NNN` / 预期回收距离 / 超期口径）——此前是"权威源"却无模板
- `templates/scaffold/.cursorGrowth/{archive,check,learn}/.gitkeep` · `templates/scaffold/主题/章节卡/.gitkeep`——补齐 scaffold 声称会建却不存在的目录
- `commands/npublish.md` · 外发打包入口（此前 `nhelp`/`routes` 指向 `novel-publish` 但无命令）
- `tools/check_integrity.py` · 母版自检：规则 frontmatter/globs、skill/command/agent 头部、**交叉引用断链**、孤儿模板、`role.default`/`MAX_LOOPS`/`learn_dir`/`persona_id` 一致性、资产登记表对齐
- `tools/check_manuscript.py` · 正文机械校验（加粗/长句/套词/元叙事；只读）；`tools/data/sensitive-words.example.txt` 为示例词表
- `tools/snapshot.py` · 改稿前备份；`tools/build_export.py` · 外发合并（配合 `/npublish`）
- `skills/novel-genre/` · 类型专项（推理公平 / 言情弧 / 力量体系 / 历史考据 / 喜剧工艺）
- `skills/novel-check/reference/chunked-scan.md` · 超长篇分批 8 维协议
- `templates/pov-ledger.md` · 多线 POV 台账；`templates/volume-outline.md` · 分卷大纲
- `templates/plan.md` 增 `下一 Sprint 候选` 区块与 9 个头部字段说明、状态标记图例

### 修复（按影响面）

- **入口可跑通**：`novel-scaffold` 补齐输出树与复制表（节奏窗/伏笔板/通用约束/logline/plan/目录），新增**重跑备份与"只补缺不覆盖"**；`/nnew` 附录改为**直接复制 `templates/plan.md`**（原自创格式导致 `/nloop` 的 `PLAN_APPROVED` 闸门读不到）
- **占位符**：`scaffold/主题/总览.md` 的选项清单改为真正的 `<Q1>`–`<Q6>` / `<N>` / `<日期>`；替换表与之对齐（原描述与实际模板互不匹配，会交付未替换的选项清单）
- **章节目录形状**：`novel-check` / `novel-dialogue` 读 `章节/第NN章_*.md` → 统一为 `章节/第NN章_<标题>/第SS节_<标题>.md`（与 `novel-chapter` 写入一致）
- **报告落点唯一**：子报告/主报告一律先落 `.cursorGrowth/check/`，Sprint 闭合才迁 `archive/`（修正 `novel-check` 三处自相矛盾 + `novel-continuity`/`novel-dialogue` 直写 archive + `novel-dialogue` 重复落两处）
- **agent 批注越界**：5 个专家 agent 删除"在当前工作文件旁追加批注"（会写进 `章节/`、`主题/`），统一为 check/ 下的单一路径模板
- **伏笔阈值三口径**：`02` 的「20/50 章」与 `novel-check`/`continuity-sleuth` 的「>10 章」冲突 → 统一为 `主题/通用约束.md` §四 ＞ 伏笔板单条 ＞ 母版默认
- **阶段编号**：`/nwrite` 的「第 4.5 步」与 `novel-chapter` 的「阶段 3.5」全部改为 **第 5 步 / 阶段 3**；scanner/rewriter 的"第 4 轮"改为 `novel-rewrite` **第 3 轮（文字层）**
- **plan 板 schema**：状态标记统一 `⬜/🔄/✅`（原 `[ ]→[x]` 与模板 `⬜` 冲突）；"历史 Sprint 索引"改为"整段移除 + 归档"；`git push` 改为仅在完成定义要求且用户同意时执行
- **主题弧线三处归属**：真源定为 `主题/主线剧情.md`（`总览.md` 只放摘要，`哲学母题.md` 展开内涵），修正 `00-novel-values` §4.1 与 `02` §五
- **断链/假引用**：`novel-logline`→`novel-brainstorm`、`novel-pitch`→`novel-publish`、`/nreview`→`/ncheck`、`skills/novel-run/reference/routes.md`→`../novel-plan/reference/routes.md`；`novel-scaffold/reference` 路径与非全路径 `universal-gates.md` 全部改全路径
- **规则 globs**：`04` 去掉永不匹配的 `主题/<哲学母题>.md`，补组织/地点条目；`03` 补 `人物关系矩阵.md`；`02` 补 `_meta/节奏窗` 与 `logline.md`；`01` 由 `**/*.md` 收窄为 `章节/主题`，并把"完全对齐 scanner"改为"子集摘要"、补 🟡 加粗带
- **孤儿模板**：删除重复的 `templates/main-file.md`（其进度表/伏笔索引/资产清单/反模式已并入 `scaffold/主题/总览.md`）；`beat-sheet.md` / `scene-card.md` 真正接进 `novel-plot` 阶段 2 与 `novel-chapter` 阶段 1，并纠正其虚假自引用
- **规则字段补齐**：`character-card`/`location-card`/`faction-card` 增「命名寓意」；scaffold `世界观.md` 概念表补齐 7 字段；`chapter-brief` 增「本章主运动」
- **归档命名文法**：统一为 `YYYYMMDD_HHMMSS_<功能>_<模块>[_<细分>...].md`（≥4 段即合法），消除 meta/99/各 skill 的 4/5/6 段之争
- **去不可核验引用**：`99` 与 `novel-plan` 的"用户规则 #6–#10"改为自描述条款
- **配置**：`workflow.json` → `growth.learn_sources` 与 `novel-learn` 对齐（补 `check/`、`plan.md`）；`templates/session/persona.json` 默认由 `professional` 改为 `dashu`；`config/README.md` 增**字段消费表**与一致性红线
- **文档**：`.cursor/README.md` 增新项目产物表与自检说明；`scaffold/README.md` 修正「3 个选择题」「生成根 plan.md」「轻量哲学先复制再删」三处事实错误

### 校验

- `python3 .cursor/tools/check_integrity.py` → **✓ 无错误，3 个警告**（规则 11 / skill 15 / command 12 / agent 9 / tool 4；警告为 3 份 reference 缺 `## 关联` 段）
- `/nnew` 骨架冒烟：按 scaffold 复制表临时建项 → `plan.md` 头部 9 字段齐、`check/learn/archive/章节卡` 就位、无残留选项清单

### 标签

`fix-workflow` `fix-links` `docs-meta` `add-templates` `add-tooling`

---

## [v0.67.0] · 2026-08-18 · feat · 通用创作闸门（任意小说 SOP）

### 新增
- `skills/novel-plan/reference/universal-gates.md` · 跨书闸门真源（三层文档 / 检查范围 / 漏网 / 量纲 / 加厚 / 对白 / 发表三尺 / 外发硬伤 / CHANGELOG 纪律）

### 修改
- `00-novel-meta` · `08-novel-discipline` · `99-novel-archive`
- skills：`novel-check` · `novel-continuity` · `novel-chapter` · `novel-rewrite` · `novel-dialogue` · `novel-publish` · `novel-plan` · `routes`
- agents：`novel-check-master` · `novel-continuity-sleuth` · `agents/README`
- commands：`ncheck` · `nlog` · `nhelp`
- templates：`chapter-brief`（节长窗与加厚口径）
- `.cursor/README.md` 指向闸门真源

### 来源
- 消费仓通用技法回灌；**无**书名 / 角色 / 母题数字 / 本机路径

### 标签
`feat-gates` `docs-meta` `universal-gates`

---

## [v0.66.0] · 2026-08-17 · sync · 过程件落点 + 主题扁平路径回灌

### 变更（`.cursor`）
- **检测/批注/复盘** 只进 `.cursorGrowth/check/`（闭合迁 `archive/`）；**禁止**写入 `主题/` 或 `章节/`
- **常驻资产优先主题根**：章前卡 `主题/章节卡/` · 伏笔板/节奏窗/通用约束在 `主题/`；`主题/_meta/` 仅旧路径回退
- 对齐文件：`00-novel-meta` · `01-novel-language` · `02-novel-plot-design` · `08-novel-discipline`
- skills：`novel-check` · `novel-chapter` · `novel-plot` · `novel-scaffold` · `novel-continuity` · `novel-dialogue` · `novel-learn` · `opening-protocol`
- commands：`ncheck` · `nwrite` · `nrun` · `nplan`
- agents：`novel-line-scanner` · `novel-line-rewriter`
- templates：`chapter-brief` · `section-brief` · `rhythm-window` · `main-file` · `scaffold/主题/总览`
- `config/workflow.json` · `.cursor/README.md`

### 来源
- 消费仓通用口径回灌（对应其 CHANGELOG v0.97 过程件卫生）；无书名/角色/本机路径

### 标签
`sync-consumer-cursor` `docs-meta` `chore-path-hygiene`

---

## [v0.65.3] · 2026-07-15 · docs · 母版脱敏与开箱即用

### 修改
- 根 `README.md` · 去掉本机绝对路径与具体书仓叙事；改为 `git clone` + 相对路径复制流程
- `.cursor/README.md` · 同上；维护约定增加「禁止本机绝对路径」
- `rules/00-novel-meta.mdc` · 母版真源脱敏；AI 约束改为「勿写本机路径进母版」
- `commands/nnew.md` · Step 0 示例改为相对路径 / clone
- `skills/novel-scaffold/SKILL.md` · 去掉本机路径示例

### 历史脱敏
- 本文件既有条目中的本机绝对路径、具体消费仓书名改为通用表述

### 标签
`docs-desensitize` `docs-readme` `chore-portable`

---

## [v0.65.2] · 2026-07-15 · sync · 合并 `/nloop` 闸补强并双向对齐

### 合并自消费仓回流
- `config/workflow.json` · `interrupt_on` 增加 `max_loops`
- `rules/07-novel-persona.mdc` · 自治口诀对齐 `PLAN_APPROVED` / `MAX_LOOPS`

### 保留并回流（母版身份）
- `.cursor/README.md` · 母版说明
- `rules/00-novel-meta.mdc` · 「〇、母版真源」
- `commands/nnew.md` · Step 0 复制母版
- `commands/nhelp.md` · `config/README.md` · `skills/novel-scaffold/SKILL.md` · 母版指针

### 对齐
- 母版与消费仓 `.cursor/` 内容对齐

### 标签
`sync-consumer-cursor` `fix-nloop-gates` `chore-align`

---

## [v0.65.1] · 2026-07-15 · init · 吸收既有小说项目 `.cursor` 为母版真源

### 新增
- 完整迁入 `.cursor/`（rules · skills · agents · commands · config · templates）
- `.cursor/README.md` · 母版身份、新书复制流程、维护约定
- 根 `README.md` · 本仓库定位与开书步骤
- （本地）`.cursorGrowth/archive/` · 吸收说明归档 · 不入库

### 变更
- `rules/00-novel-meta.mdc` · 声明本仓库为母版真源
- `commands/nnew.md` · `skills/novel-scaffold/SKILL.md` · 新书必须先从本仓库复制 `.cursor/`
- `config/README.md` · 标注母版仓库名

### 来源
- 既有长篇消费仓的 `.cursor/`（对齐其 CHANGELOG v0.65.1；路径与书名不入库）

### 标签
`init-master-cursor` `absorb-consumer-cursor`

---
