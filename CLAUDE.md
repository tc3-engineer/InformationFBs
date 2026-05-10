# Project: tc3-libraries-kb

> 本文件由 Claude Code 在每次 session 启动时自动加载。所有 slash command 共享这些规则。

## 项目目标

为 Beckhoff TwinCAT 3 的全部公开 PLC 库生成准确、结构化、可索引的中文技术文档。覆盖 ~40 个库 / ~1500-2000 个 FB+FC。**每篇文档配套一个可直接拖入 TwinCAT 3 XAE 的演示程序文件**。

## 唯一可信源

- **首选**：Beckhoff 官方 PDF
  `https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_<NAME>_EN.pdf`
- **次选**（PDF 不可用时）：InfoSys 在线文档
  `https://infosys.beckhoff.com/content/1033/tcplclib_<lowercase_name>/`

不允许用任何第三方资料、博客、StackOverflow 答案、训练数据记忆作为依据。

## 硬规则（违反即视为 bug）

### 准确性
1. **逐字搬运 VAR 区**：VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 中变量名、类型、注释必须与 PDF 完全一致（包括拼写、大小写、空格、分号）。
2. **不许补全缺失字段**：PDF 没写的错误码、范围、状态机分支，文档里标 `⚠️ 待人工确认`。禁止用"通常""一般""可能"补全。
3. **库版本必从 PDF 头部抓**："Version: x.y.z" 这一行；不许引用别处。
4. **跨库零混用**：同名 FB 在不同库定义不同；当前任务的 library 字段决定唯一来源。
5. **元信息表 9 行全填**：库名、版本、类型、类别、Source、Source PDF、Verified、Status、Example。无信息填 `-`，禁止留空。

### 自验证（每篇文档必做）
生成完一篇文档后，**重新 web_fetch 该库 PDF 中对应章节**，逐字段对照：
- VAR 区每个变量的名/类型 → ✅ 一致 / ❌ 不一致 → 必须重写
- 类别归类 → ✅ / ❌
- 描述句中的关键事实（"上升沿启动"、"15 字节数据"等）→ ✅ / ❌

把验证结果写到 `_meta/verify/<library>/<name>.md`，包括 PASS/FAIL 与具体差异。
连续两次自验证失败 → 把文档头部 Status 改为 `⚠️ verify-failed`，把问题列到 `_meta/blocked.md`，跳过。

### 例程文件（每篇文档必产）
**每个 FB/FC 必产配套 PLCopenXML 文件**，输出到 `<library>/examples/P_Demo_<Name>.xml`。

要求：
1. **格式**：PLCopenXML（IEC 61131-10），根节点 `<project xmlns="http://www.plcopen.org/xml/tc6_0200">`
2. **POU 类型**：`pouType="program"`，名为 `P_Demo_<Name>`
3. **基于模板**：使用 `_templates/plcopen-program.xml` 作为骨架，按规则替换占位符
4. **可导入**：用户右键 PLC 项目 → Import PLCopenXML → 选此文件 → 编译 → 登录 → 运行验证
5. **完整 demo 内容**：
   - 局部变量包含被演示 FB 的实例 `fb<Name> : <Name>;`
   - 包含所有输入信号变量（BOOL/REAL/TIME 等）和输出监视变量
   - ST 代码顶部必须有**中文验证步骤注释**（"在线写值 X 观察 Y"）
   - 调用 FB 时**所有 VAR_INPUT 必须显式赋值**（不能省略 `:=`）
6. **XML 实体转义**：ST 代码里的 `<` `>` `&` 转为 `&lt;` `&gt;` `&amp;`；其它字符保持原样
7. **类型映射**：BOOL/INT/DINT/UDINT/REAL/LREAL/TIME/STRING 用对应空元素 `<BOOL/>`；FB 类型用 `<derived name="..."/>`
8. **不加 TwinCAT 私有特性**：不要 `attribute` pragma、不要 access modifier、不要 namespace 前缀（保最小可导入集）

例程文件也要做自验证：
- ST 代码必须能在空白 PROGRAM POU 编译通过（语法正确，引用的 FB 名/参数名与文档一致）
- 文档头部 Example 字段必须链接到该 .xml

### 流程
1. 工作分支：`claude/<command>-<library>-<timestamp>`，禁止直接 push main
2. PR 必填：每篇文档的 verify 状态、PDF 源 URL 与访问日期、例程文件链接
3. 进度记录：每完成一篇追加一行到 `_meta/progress.md`
4. 索引同步：每完成一批立即更新 `<library>/README.md` 与 `_meta/library-catalog.md`

## 文档模板

参见 `_templates/fb-template.md`（文档主体）与 `_templates/plcopen-program.xml`（例程）。模板章节顺序与字段名固定，不许增删章节。

## 中英对照规范

- 章节标题用中文
- 引脚名、类型名、IEC 关键字（VAR_INPUT、TIME、BOOL、WORD、AMSADDR、E_AdsErr 等）保留英文
- 关键术语首次出现时双语："功能块（Function Block, FB）"
- InfoSys URL、库名、PDF URL 不翻译

## 写代码例程的规则

- 例程必须在空白 TwinCAT 3 PLC 项目（含 Tc2_Standard 引用）里能编译通过
- 变量命名：FB 实例用 `fb<Name>` 前缀，本地变量驼峰加类型前缀（`bXxx` BOOL, `iXxx` INT, `tXxx` TIME, `nXxx` DINT/UDINT 等）
- 例程必须写出**实际有意义**的场景（如 RS demo 中"启动按钮 vs 急停"），但禁止虚构与该 FB 无关的复杂业务
- ST 注释统一用 `//` 单行注释（不用 `(* *)`），便于在 PLCopenXML body 中保持单行可读

## 库目录与 PDF URL 模式

主目录见 `_meta/library-catalog.md`。命名小写化的子目录映射写在 catalog 里。

## 失败处理

- PDF 抓取 HTTP 非 200 → 写 `_meta/blocked.md`，列原因，**不要试图用 InfoSys 替代**（除非 catalog 里明确标记 PDF 不可用）
- TOC 解析疑似不全 → PR body 里列可疑章节，标 `⚠️ 待 review TOC`
- 例程 ST 代码自我编译验证失败（关键字拼错等）→ 重写一次；二次失败标 `⚠️ example-build-failed` 并跳过
- 任何不确定 → 标 `⚠️` 而非编造

## 反例（这些是过去出现过的真实错误，绝不再犯）

❌ "TON 是延时启动的定时器，类似 IEC TIMER" — 含糊"类似"，原文未说
✅ "TON 是接通延时定时器（switch-on delay timer）。IN 上升沿后开始累加 ET，达到 PT 时 Q 置 TRUE"

❌ "PV 一般是正整数" — "一般"是脑补
✅ `PV : WORD`（PDF 明确给出的类型）

❌ "未列错误码，常见错误是参数越界" — 编造
✅ "⚠️ 待人工确认（PDF 未列出错误码）"

❌ 例程里写 `fbTON.IN := bMotorReq;` 单独成行后再 `fbTON();` — 风格不一致
✅ 例程里统一用 `fbTON(IN := bMotorReq, PT := T#3S, Q => bRunOk);` 单次调用风格

❌ PLCopenXML body 里写 `if x < 5 then` 没转义 `<`
✅ `if x &lt; 5 then`（XML 实体转义）
