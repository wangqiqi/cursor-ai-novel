---
name: novel-publish
description: 发布打包与推介材料生成。合并章节、目录、字数；简介/腰封；上架填写卡；发表三尺闸门。
disable-model-invocation: false
---

# 发布打包与推介 · novel-publish

> **"完稿是终点，发布是起点。"**
> 本技能负责全书完结后的技术打包与商业推介材料准备。

## 触发场景

- "准备发布" / "导出" / "打包"
- "写简介" / "做推荐语" / "出版前准备"
- 全文完结或阶段性成果展示

## 工作流

### 阶段 0：三尺闸门（先打分，再打包）

分开记录，禁止合成一个「过了」。细则 `skills/novel-plan/reference/universal-gates.md` §7–8。

| 尺 | 问什么 | 未绿时 |
|---|---|---|
| **情节尺** | 主线节拍是否走完、终局是否落地 | 可出阶段包，不升主版本 |
| **出版尺** | 节长/高潮是否有肉、外发硬伤是否清零 | 不打 v1.0 |
| **体量尺** | 是否达到作者自定的长制/短制目标 | 只作进度，不单独挡外发 |

**外发硬伤（正文禁）**：作者元叙事（「第 N 章」）、未落地专名剧透、控制层术语当对白。

### 阶段 1：推介材料 (Pitching)
- **动作**：基于 Logline 与世界观生成推介包。
- **产出**：
    - **一句话推介**（≤ 30 字，用于书城/简介）。
    - **三百字简介**（结构：世界+主角 -> 冲突+转折 -> 钩子）。
    - **腰封/推荐语**（短小有力，带母题金句）。
    - **模拟短评**（5 条不同风格，含争议型）。
    - **上架填写卡**（书名、作者署名、分类、目录、对外字数口径）。**只根据 `章节/` 写**，不把 `主题/` 当读者读物。

### 阶段 2：技术打包 (Packaging)
- **动作**：合并章节为 `build/<书名>_全文.md`（源只能是 `章节/`）。
- **一键打包（推荐）**：

  ```bash
  python3 .cursor/tools/build_export.py --author "<署名>"
  # 产出：build/<书名>_全文.md · build/<书名>_分章/*.txt · build/<书名>.epub · build/<书名>_统计报告.md
  ```

  | 选项 | 作用 |
  |------|------|
  | `--format md,txt,epub` | 选择产出格式 |
  | `--title` / `--author` / `--lang` | 书名 / 署名 / 语言（缺省从 `主题/总览.md` 取书名） |
  | `--strip-structural` | 去掉 `## 本节完` / `## 本章完`（**发布必开**） |
  | `--strip-viewpoint` | 再去掉 `> 【视角：…】` 行 |
  | `--keep-section-titles` | 合并 Markdown 保留节标题（降为 `###`） |

- **规范**：
    - 章标题取自**章目录名**（`第NN章_标题`），节文件自带的 H1 不重复输出；
    - 自动生成目录（EPUB nav / Markdown 章节标题）；
    - 敏感词扫描（用 `python3 .cursor/tools/check_manuscript.py`，词表读 `主题/敏感词表.md`）；
    - 统计报告：总字数、平均章字数、逐章字数。

> **EPUB 为手写 EPUB3（仅标准库）**：`mimetype`（STORED）· `META-INF/container.xml` · `content.opf` · `nav.xhtml` · 样式表。
> 需要 DOCX 时自行用 pandoc 从 `build/<书名>_全文.md` 转换（母版不内置 DOCX，避免引入非标准库依赖）。

### 阶段 3：归档与版本 (Archive)
- **动作**：
    - 更新 `CHANGELOG.md`：出版尺未绿 → 只打阶段版本；**禁止**升主版本（如 v1.0）。
    - `git tag` 仅当用户同意（见 `99-novel-archive.mdc` §六）。
    - 备份至 `.cursorGrowth/archive/YYYYMMDD_HHMMSS_发布_<版本>/`。

> **`build/` 与 `.gitignore`**：`.gitignore` 默认忽略 `build/`——这是**有意**的：`build/` 是外发产物，不进版本库。
> 需要版本化的推介材料一律写 `主题/推介包.md`；`build/` 只作交付物，重跑即可再生。

## 输出
- `主题/推介包.md`（版本化真源）
- `build/<书名>_全文.md`（外发产物，gitignore）
- `build/<书名>_分章/*.txt`（分章 TXT，gitignore）
- `build/<书名>.epub`（EPUB3，gitignore）
- `build/<书名>_统计报告.md`（外发产物，gitignore）

## 反模式
- ❌ 简介剧透核心反转。
- ❌ 直接发布不扫描敏感词。
- ❌ 不打 tag 或不归档。
- ❌ 出版尺未绿仍打 v1.0。
- ❌ 用 `主题/` / 讨论稿当读者读物写简介。
- ❌ 正文残留「第 N 章」等作者元叙事。
- ❌ 把 `build/` 当版本化真源（它被 gitignore，真正的推介真源是 `主题/推介包.md`）。

## 关联
- **上游**：`novel-chapter`、`novel-rewrite`
- **规则**：`00-novel-meta.mdc`、`99-novel-archive.mdc`
- **闸门**：`novel-plan/reference/universal-gates.md`（§7 三尺 · §8 外发硬伤）
- **命令**：`/npublish`
