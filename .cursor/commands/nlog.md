---
name: nlog
description: 生成 / 更新 CHANGELOG.md。统一版本号、Tag、归档条目。
---

# /nlog · 更新日志

## 用法

```
/nlog
/nlog <版本> 完成第二章
```

## 流程

调用 `.cursor/rules/99-novel-archive.mdc`：

1. **读取最近状态**：
   - 上次 CHANGELOG 版本
   - 上次 git tag
   - 最近的 archive 文件

2. **检测本次变更**：
   - git status（新增/修改/删除的文件）
   - 与上一版本对比

3. **生成版本号**（如未指定）：
   - 主版本：全书完结
   - 次版本：完成章节 / 重大体系升级
   - 修订：小修改、bug fix

4. **写入 CHANGELOG.md**（倒序顶部）

5. **生成归档条目**（如有重大变更）

## 输出

- 更新：`CHANGELOG.md`
- 输出：版本号 + Tag 列表 + 归档路径
- 提示用户执行 git commit + tag

## CHANGELOG 模板

```markdown
## [vX.Y.Z] · YYYY-MM-DD HH:MM · <一句话>

### 新增
- <文件/功能> · 一句话说明

### 修改
- <文件> · 一句话说明

### 删除
- <文件> · 一句话说明

### 归档
- `.cursorGrowth/archive/...md` · 一句话说明

### 标签
`tag1` `tag2` `tag3`
```

## 强制约束（按用户规则 #6、#7）

- 倒序写入
- 每次实质性修改 → 更新
- Tag 与 CHANGELOG 中的标签一致
- git 提交前先 CHANGELOG
