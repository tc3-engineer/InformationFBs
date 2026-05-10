---
description: 抓取并解析指定 Beckhoff 库的 PDF，生成 roadmap、库索引和 ADS 类目录
argument-hint: <Library_Name>
---

# /discover

为 Beckhoff TwinCAT 3 库 `$ARGUMENTS` 执行完整的发现流程。

## 输入

- `$ARGUMENTS`：库名，例如 `Tc2_System`、`Tc2_MC2`、`Tc3_JsonXml`
- 当 `$ARGUMENTS` 为空 → 报错并提示用法

## 流程

### 1. 抓 PDF
- URL：`https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_$ARGUMENTS_EN.pdf`
- 用 WebFetch 获取
- 失败（404 / 非 200）→ 写 `_meta/blocked.md`，列出原因，停止

### 2. 提取库元信息
从 PDF 头部抓：
- 版本号（"Version: x.y.z" 这一行）
- 发布日期
- 库的官方简介（Overview 章节首段）

### 3. 解析 TOC
PDF 前几页有 Table of contents。识别：
- 顶级章节如 `3 Function blocks` / `4 Functions` / `5 Functions for ...`
- 子分类如 `3.1 Bistable`、`3.2 Counter`
- 具体条目如 `3.1.1 RS`、`3.1.2 SR`

每个条目记录：name、type（FB/FC）、category（用 PDF 章节标题原文）、章节号。

**禁止脑补**：PDF 里没写的条目不许添加，即便你"知道"该库通常包含某 FB。

### 4. 类别 → 目录映射
按 catalog 中的规则把 category 转成子目录名：
- 全小写
- 空格 → 下划线
- 去括号
- 例：`Timer (LTIME)` → `timer_ltime`、`ADS function blocks` → `ads`

如果 catalog 没定义该类别 → 用上述规则自派生，并把映射追加到 `_meta/category-mapping.md`。

### 5. 生成 `_meta/roadmap-$ARGUMENTS.md`

```markdown
# Roadmap · $ARGUMENTS

- Library Version: `<x.y.z>`
- PDF 发布日期: `<YYYY-MM-DD>`
- Source PDF: <URL>
- InfoSys: <URL>
- Discover 日期: <今日 UTC>
- 总条目数: <N>（FB <a> + FC <b>）

| # | Name | Type | Category | Output Path | Status |
|---|---|---|---|---|---|
...
```

每行 Status 初始为 `pending`。

### 6. 生成 `$ARGUMENTS/README.md`

按 Category 分组的索引表，所有条目初始 ⏳ pending。包含：
- 链接回 InfoSys 与 PDF
- 全部条目的 markdown 链接（即便目标 .md 还不存在，先把链接占位）

### 7. 创建分类目录
对每个 unique category 创建空目录 `$ARGUMENTS/<category_dir>/`。例：`Tc2_System/ads/`、`Tc2_System/file/`。

### 8. 更新 `_meta/library-catalog.md`
找到 `$ARGUMENTS` 对应行，把：
- 状态从 ⏳ pending 改为 🚧 in_progress
- 估算 FB 数改为实际数
- InfoSys 版本字段填实际抓到的值

### 9. 提 PR
- 分支：`claude/discover-$ARGUMENTS-<UTC时间戳>`
- 标题：`discover($ARGUMENTS): <total> items in <num_categories> categories`
- Body 必须包含：
  - PDF 抓取时间与版本号
  - 总条目数（FB / FC 拆分）
  - 每个 category 的条目数
  - 接下来推荐执行的 `/doc-shard` 命令清单（按 category 分批，每批 ≤12 条）

## 输出示例（PR body）

```
Discover Tc2_System v1.17.1 (PDF 2025-11-25)

总计 156 条：FB 142 + FC 14
按类别：
- General (2)
- ADS (15)
- Expanded ADS (12)
- Data access (24)
- File (18)
- EventLogger (8)
- ...

推荐执行（按 category 分批）：
/doc-shard Tc2_System General
/doc-shard Tc2_System ADS
/doc-shard Tc2_System Expanded\ ADS
/doc-shard Tc2_System Data\ access  (24 条 → 拆 2 批)
/doc-shard Tc2_System File  (18 条 → 拆 2 批)
...
```

## 完成标志

- `_meta/roadmap-$ARGUMENTS.md` ✅
- `$ARGUMENTS/README.md` ✅
- 分类子目录 ✅
- `_meta/library-catalog.md` 更新 ✅
- PR 已开 ✅
