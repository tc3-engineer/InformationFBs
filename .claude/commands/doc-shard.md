---
description: 为指定库的指定类别生成完整 FB/FC 文档 + 配套 TcPOU 例程，每对带自验证
argument-hint: <Library_Name> <Category>
---

# /doc-shard

为库 `$1` 中类别 `$2` 的所有 FB/FC 生成**完整文档 + 配套 TcPOU 例程**（带自验证）。

## 解析参数

`$ARGUMENTS` 形如 `Tc2_System ADS` 或 `Tc2_System Data access`（类别名可含空格）。
- 第一个 token = library
- 余下全部 = category（保留空格）

任一参数为空 → 报错并提示用法。

## 前置检查

1. `_meta/roadmap-<library>.md` 必须存在（否则提示先跑 `/discover <library>`）
2. 从 roadmap 找出本 category 下 status == `pending` 的所有条目
3. 若一批超过 12 条 → 自动拆批，本次只处理前 12 条，剩余在 PR body 提示后续命令

## 流程

### 1. 抓 PDF
```bash
python3 _meta/tools/fetch_pdf.py <library>
```
脚本 24h 内复用缓存。失败 → 写 blocked.md，停止。

### 1.5 对每条目抽章节正文
```bash
python3 _meta/tools/extract_section.py <library> <section_number>
```
章节号从 `_meta/roadmap-<library>.md` 取。这是**生成文档时唯一允许的事实来源**，禁止凭训练数据补全。

### 2. 对每个条目（双产物）

**产物 A：文档** `<library>/<category_dir>/<name>.md`
按 `_templates/fb-template.md` 生成。

**产物 B：例程** `<library>/examples/P_Demo_<Name>.TcPOU`
按 `_templates/tcpou-program.xml` 生成。

两份产物**必须配套生成**——只生成一份视为失败。

#### 文档生成规则
严格遵守 CLAUDE.md 中的硬规则，重点：
- VAR 区逐字搬运（包括类型、注释、分号、大小写）
- 元信息表 9 行全填（**Example 字段必须链接到 .xml**）
- 描述句不超出 PDF 原文事实
- 例程章节必须在最前面提示"配套可导入文件 [examples/P_Demo_<Name>.TcPOU]" 与导入步骤

#### 例程生成规则（TcPOU）
1. 复制 `_templates/tcpou-program.xml` 作为骨架
2. 替换占位符：`{{NAME}}`、`{{LIBRARY}}`、`{{TIMESTAMP}}`（用 ISO8601 当前 UTC）
3. 在 `<localVars>` 中：
   - 必有 `fb<Name> : <Name>;`（用 `<derived name="<Name>"/>`）
   - 为该 FB 的每个 VAR_INPUT 生成对应本地信号变量（基础类型用 `<BOOL/>` 等空元素）
   - 为关键 VAR_OUTPUT 生成监视变量
   - 命名前缀：BOOL → `bXxx`, INT → `iXxx`, DINT → `nXxx`, REAL → `rXxx`, TIME → `tXxx`, STRING → `sXxx`
4. 在 ST `body` 中：
   - 顶部加中文 `// ============` 验证步骤注释块（最少 4 步：登录 → 监视 → 写入 → 期望）
   - 一次完整的 FB 调用，**所有 VAR_INPUT 显式 `:=` 赋值**
   - 关键 VAR_OUTPUT 用 `=>` 输出到本地变量
   - `<` `>` `&` 等 XML 特殊字符必须实体化（`&lt;` `&gt;` `&amp;`）
5. **不加任何 TwinCAT 私有特性**（attribute pragma、access modifier、namespace 前缀）

### 3. 自验证（核心步骤）

#### 3a. 文档验证
```bash
python3 _meta/tools/verify_doc.py <library>/<category_dir>/<name>.md
```
退出 0 PASS / 1 MINOR（看 diagnostics 修） / 2 FAIL。脚本检查：VAR 名+类型与 PDF 一致、版本一致、example 文件存在。

#### 3b. 例程验证
```bash
python3 _meta/tools/lint_tcpou.py <library>/examples/P_Demo_<Name>.TcPOU
```
退出 0 PASS / 2 FAIL。检查：XML 良构、pouType=program、fb<Name> + derived 引用正确、ST body XML 实体化。

任一脚本退出 2 → 重写对应文件；二次仍 FAIL → 文档 Status 标 `⚠️ verify-failed` 或 `⚠️ example-build-failed`，文件保留供人工。

#### 3c. 写验证报告
合并到 `_meta/verify/<library>/<name>.md`：
```markdown
# Verify: <name>

- Verified at: <UTC>
- Source PDF: <URL>
- Doc result: ✅ PASS / ❌ FAIL
- Example result: ✅ PASS / ❌ FAIL

## 文档检查明细
| 项 | 文档值 | PDF 值 | 结果 |
...

## 例程检查明细
| 项 | 结果 | 备注 |
...

## 差异（如有）
- ...
```

#### 3d. 判定
- 文档与例程都全 ✅ → Status: `verified` ✅
- 文档 ❌ → 立即修正文档，重做 verify（最多 1 次重试）
- 例程 ❌ → 立即修正例程，重做 verify（最多 1 次重试）
- 二次仍 ❌ → Status 设 `⚠️ verify-failed` 或 `⚠️ example-build-failed`，问题摘要追加到 `_meta/blocked.md`，**不删任何文件**（留人工评估）

### 4. 更新进度

每完成一篇追加一行到 `_meta/progress.md`：
```
<UTC> | <library> | <category> | <name> | <verified|verify-failed|example-build-failed|skipped> | <note>
```

### 5. 同步索引

- 更新 `<library>/README.md` 中对应行的状态（同时显示文档链接与例程链接）
- 更新 `_meta/roadmap-<library>.md` 中对应行的 Status

### 6. 提 PR

- 分支：`claude/doc-<library>-<category_safe>-<UTC时间戳>`
- 标题：`docs(<library>/<category>): <N> items, <X> verified, <Y> failed`
- Body 必含：
  ```
  Library: <library> v<version>
  Category: <category>
  PDF 抓取: <UTC>，二次验证抓取: <UTC>

  | Name | Doc | Example | Notes |
  |---|---|---|---|
  | RS  | ✅ | ✅ examples/P_Demo_RS.TcPOU | - |
  | SR  | ✅ | ✅ examples/P_Demo_SR.TcPOU | - |
  | XYZ | ⚠️ verify-failed | ⚠️ example-build-failed | 见 blocked.md |

  剩余 pending（如本批超过 12 条）：
  - /doc-shard <library> <category>  # 继续下一批 N 条
  ```

## 完成标志

- 本批每个条目生成 .md + .xml 两份文件 ✅
- 每对 verify 报告生成 ✅
- progress.md / library README / roadmap 同步 ✅
- PR 已开 ✅
- 即便有 verify-failed 也照常提 PR（人工 review 时处理）
