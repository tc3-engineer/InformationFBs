# Project: tc3-libraries-kb

> 本文件由 Claude Code 在每次 session 启动时自动加载。所有 slash command 共享这些规则。
> **2026-05-11 行动纲领更新**：项目目标重写为"读者不再需要打开 PDF"。
> 占位短语、英文直抄、PDF 单源都视为 P0 bug。

## 项目目标

为 Beckhoff TwinCAT 3 的全部公开 PLC 库生成**可独立阅读的中文技术文档** + **可直接拖入 XAE 的实用演示程序**。覆盖 ~40 个库 / ~1500-2000 个 FB+FC。

**核心衡量标准**：本仓库存在的意义是让中文工程师**不必去翻 PDF 也不必去查 InfoSys** 就能用上 Beckhoff 库。如果一篇文档让读者还得去看 PDF 才知道某个变量意思 / 某段时序怎么走 / 错误码什么含义，那这篇文档就是失败的。

> 用一句话自检：把 PDF 链接拿走，这篇文档单独看够不够用？不够 → 重写。

## 双可信源

1. **第一可信源**：Beckhoff 官方 PDF
   `https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_<NAME>_EN.pdf`
2. **第二可信源**：Beckhoff InfoSys 在线手册
   `https://infosys.beckhoff.com/content/1033/tcplclib_<lowercase_library>/<topicid>.html`
   （InfoSys 是 server-rendered HTML，可直接 `urllib` + 正则解析；CLAUDE.md 早期版本"SPA 不可用"是过时结论）

**每条事实必须双源对照**：PDF 文本 = InfoSys 文本，写入文档前两边都查过。一侧没说就标 ⚠️。

不允许：第三方资料、博客、StackOverflow、训练数据记忆、"通常"、"一般"、"可能"、"大致"等推测词。

## 联网取数管线（确定性）

```bash
python3 _meta/tools/fetch_pdf.py <Library>               # PDF 下载 + 抽文 + 24h 缓存
python3 _meta/tools/parse_toc.py <Library>               # JSON 输出 section/name/type/category
python3 _meta/tools/extract_section.py <Lib> <sec>       # 抽指定章节正文（支持 <sec>#mN 切 inline method）
python3 _meta/tools/infosys_fetch.py <url>               # 抓 + 解析 InfoSys topic 页（结构化 JSON）
python3 _meta/tools/verify_doc.py <doc.md>               # 自验证：VAR/默认值/版本/占位短语/InfoSys 链接
python3 _meta/tools/lint_tcpou.py <P_Demo_X.TcPOU>       # 例程结构 lint
```

缓存：`_meta/.pdf-cache/<Library>.{pdf,txt,meta.json}`（gitignore）、`_meta/.infosys-cache/<sha1>.html`（gitignore）。

## 硬规则（违反即 P0 bug）

### A. 准确性（PDF + InfoSys 双源）
1. **逐字搬运 VAR 区**：变量名、类型、默认值（`:= xxx`）、注释必须与 PDF 完全一致（拼写、大小写、空格、分号）。
2. **不许补全缺失字段**：PDF 没写、InfoSys 也没写的，标 `⚠️ 待人工确认`，禁止脑补。
3. **库版本从 PDF 头部 "Version: x.y.z" 抓**；不许引用别处。
4. **跨库零混用**：同名 FB 在不同库定义不同；以当前 library 字段为准。
5. **元信息表 10 行全填**：库名、版本、类型、类别、Source PDF、Source InfoSys、Verified、Status、Example、InfoSys-checked。无信息填 `-`，禁止留空。

### B. 全中文表达（新增 2026-05-11）
6. **正文必须是中文叙述**。允许保留英文的只有：
   - IEC 关键字：`VAR_INPUT` / `VAR_OUTPUT` / `VAR_IN_OUT` / `END_VAR` / `METHOD` / `FUNCTION` 等
   - IEC 基本类型：`BOOL` / `INT` / `DINT` / `UDINT` / `WORD` / `DWORD` / `LWORD` / `REAL` / `LREAL` / `TIME` / `STRING` / `DATE` 等
   - Beckhoff 类型/枚举/接口名：`AMSADDR` / `E_AdsErr` / `T_AmsNetId` / `I_TcSourceInfo` / `HRESULT` 等
   - 变量名（引脚名）：`bExecute` / `nEventId` / `eSeverity` 等
   - 关键术语首次出现时双语：「功能块（Function Block, FB）」
   - 库名、PDF URL、InfoSys URL
7. **禁止英文整句**：PDF 抽出的英文段落必须翻译为中文叙述，不许保留 "This function block enables..." 这种原文残留。
8. **禁止"中英混杂占位"**：例如 `## 1. 功能简述` 下只放一句英文摘要再加 `Syntax Definition: ...`，这是早期模板的脏数据。

### C. 禁止占位短语（新增 2026-05-11）
9. **下列短语在任何文档里都不允许**（视为未完成）：
   - `详见 PDF` / `（详见 PDF）`
   - `见上方功能简述。`（§3 行为说明的偷懒）
   - `请对照 PDF 第 X.X 节。`（§3 末尾的"看 PDF 自己悟"指引）
   - `见上方使用注意中标 ⚠️ 的项。`（§5 的偷懒交叉引用）
   - `请见对应 InfoSys 页面，⚠️ 待人工补全。`（§4 错误码的偷懒）
   - `（详细见 PDF）` / `（详见 InfoSys）` 单作描述
10. **变量描述单元格不可只填 "（详见 PDF）"**：必须翻译 InfoSys / PDF 中的英文 Description 列为中文一句话。InfoSys 没列的才标 ⚠️。
11. **§3 行为说明不可退化为"见上方"+"看 PDF"**：必须用中文叙述时序、状态机分支、上升沿/边沿/电平触发语义、典型用法、典型陷阱；InfoSys 行为段落必须翻译进去。

### D. 例程必须有业务价值（新增 2026-05-11）
12. **例程不可只是"声明 + 实例化 + 调用 + 看输出"**。每个 P_Demo_X.TcPOU 必须在头部用中文注释回答：
    - **场景**：这个 FB 在真实工程里解决什么问题？（例：FB_S_UPS_CB3011 → CX 控制器掉电时 2 秒内把 retain 数据写入 SD 卡，避免下次开机数据丢失）
    - **价值**：用 vs 不用的区别是什么？
    - **验证步骤**：如何在线观察这个例程"真的在做事"，而不只是编译过？（"在线写 bEnable := TRUE，观察 systemTime 在 2-3 秒后开始变化"）
13. **例程的输入信号要有意义**：不要 `bSig := TRUE;` 这种空名字。用 `bMotorStartReq` / `bEmergencyStop` / `tRecoveryTime` 等贴近工业语义的命名。
14. **例程的注释比例**：注释行数 ≥ 代码行数的 1/3。注释解释**为什么这么写**，不是复述代码做什么。

### E. InfoSys 强制交叉验证（新增 2026-05-11）
15. **每篇文档必须含 InfoSys topic URL**（元信息 `Source InfoSys` 行），不是库根 URL 而是该 FB / method 的具体 topic 页 URL。
16. **每篇文档生成完必跑 `infosys_fetch.py <url>` + 与 PDF diff**：
    - VAR 名/类型/默认值/Description 完全一致 → 在元信息表 `InfoSys-checked` 行填 `✅ <date>`
    - 不一致 → 列出差异，按"InfoSys 详细 > PDF 概要"原则取详细一侧，并在 §3 行为说明里点明这一不一致
17. **InfoSys 没收录的 entry**（罕见，主要是新版 PDF 抢先发布）→ `InfoSys-checked` 填 `⚠️ not-on-infosys`，并在 PR body 里点名。

## 自验证（每篇文档必做）

`python3 _meta/tools/verify_doc.py <path>`：
- 退出码 0 = PASS：写 verify 报告到 `_meta/verify/<library>/<name>.md`，标 ✅
- 退出码 1 = MINOR：检查 diagnostics，能修立即修；修后再跑直到 PASS
- 退出码 2 = FAIL：**重写整篇**（不是补丁）；二次仍 FAIL → 头部 Status 改 `⚠️ verify-failed`，列入 `_meta/blocked.md`

verify_doc.py 现在检的不仅是 VAR 一致性，还包括：
- 默认值字面对比
- 裸参数恢复（METHOD 没 VAR_INPUT 包裹的情况）
- 内联方法 `#mN` 切片
- **占位短语扫描**（C 节列出的全部短语）
- **`Source InfoSys` 行必须含 `infosys.beckhoff.com/content/...` 具体 topic URL**
- **`InfoSys-checked` 行必须为 `✅ <YYYY-MM-DD>` 或显式 `⚠️ not-on-infosys`**
- **§3 行为说明长度阈值**：去掉占位短语和子弹点后中文字符数 ≥ 80（短描述也得说人话）

## 例程文件（每篇文档必产）

输出到 `<library>/examples/P_Demo_<Name>.TcPOU`。

要求：
1. 格式：TwinCAT 3 原生 .TcPOU（XML / TcPlcObject schema），根节点 `<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">`
2. POU 类型 `pouType="program"`，名为 `P_Demo_<Name>`
3. 基于 `_templates/tcpou-program.xml` 骨架（顶层 `<TcPlcObject>` + 单个 `<POU>` + `<Declaration>` + `<Implementation>/<ST>`）
4. 用户右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本文件 → 编译 → 登录 → 运行验证
5. **demo 内容（D 节硬规则）**：
   - 顶部中文注释三件套：**场景 / 价值 / 验证步骤**
   - 局部变量名贴近工业语义（`bMotorStartReq` 不是 `bSig1`）
   - 包含 FB 实例 `fb<Name> : <Name>;`，所有 VAR_INPUT 显式赋值
   - 调用风格：`fbX(IN := ..., PT := T#3S, Q => bRunOk);` 单次调用形式
   - 注释行数 ≥ 代码行数的 1/3，解释 WHY 不复述 WHAT
6. 文本编码：Declaration 和 ST 体均放在 `<![CDATA[...]]>` 内，IEC 文本里的 `<` `>` `&` **不需要转义**（CDATA 透传）
7. 类型直接写 IEC 文本（在 Declaration CDATA 内）：
   - 基本类型直接写 `BOOL` / `INT` / `TIME` 等
   - `STRING(N)` 直接写 `STRING(80)` 等
   - `POINTER TO X` 直接写 `POINTER TO BOOL` 等
   - `ARRAY[L..U] OF X` 直接写 `ARRAY[0..9] OF BYTE` 等
   - 命名 DUT/FB/接口/枚举直接写类型名
8. 不加 TwinCAT 私有 attribute pragma；POU `SpecialFunc="None"`；Id 用稳定 UUID5（`_meta/tools/plcopen_to_tcpou.py` 里的 `_stable_guid`）
9. `lint_tcpou.py` 退出 0 才算通过

## 流程

1. 工作分支：`claude/<command>-<library>-<timestamp>`，禁止直接 push main
2. PR 必填：每篇文档的 verify 状态、PDF + InfoSys URL、访问日期、例程文件链接
3. 进度记录：每完成一篇追加一行到 `_meta/progress.md`
4. 索引同步：每完成一批立即更新 `<library>/README.md` 与 `_meta/library-catalog.md`

## 文档模板

`_templates/fb-template.md`（文档主体）与 `_templates/tcpou-program.xml`（例程，TwinCAT 3 原生 `.TcPOU` 骨架）。
**模板章节顺序与字段名固定，不许增删章节**。当前章节：
1. 功能简述（中文 2-4 句，不抄英文原句）
2. 接口定义（VAR_INPUT/OUTPUT/IN_OUT + 中文 Description 表）
3. 行为说明（时序、状态机、触发语义、典型用法、典型陷阱；不准 "见上方"）
4. 错误码 / 返回值（按 FUNCTION/METHOD 实际返回类型写；HRESULT/BOOL/无返回各自模板）
5. 使用注意 / 常见坑（工程经验补充允许标"工程经验补充"区分）
6. 最小例程（指向 .TcPOU 文件）
7. 业务场景与实际价值（新增 D 节要求）
8. 参考资料（PDF 章节 + InfoSys URL）

## 中英对照规范（B 节细化）

详见硬规则 B。简化版：
- 章节标题：中文
- 引脚名、类型名、IEC 关键字：英文保留
- 描述、行为、注释、场景：必须中文
- URL、库名、版本号：原样不译

## 失败处理

- `fetch_pdf.py` 非 200 → `_meta/blocked.md`，列原因，停止该库（不试 InfoSys 替代 PDF）
- `parse_toc.py` 与人工估算偏差大 → PR body 列 JSON + 标 `⚠️ 待 review TOC`
- `verify_doc.py` 退出 2 → 整篇重写一次；二次仍 FAIL 标 `⚠️ verify-failed` 进 blocked.md
- `lint_tcpou.py` 退出 2 → 重写例程；二次失败标 `⚠️ example-build-failed`
- InfoSys 取不到 / 404 → `InfoSys-checked` 标 `⚠️ not-on-infosys`，**不停止流程**
- 任何不确定 → 标 `⚠️` 而非编造

## 反例（不再犯）

### 准确性反例
❌ "TON 是延时启动的定时器，类似 IEC TIMER" — 含糊"类似"
✅ "TON 是接通延时定时器（switch-on delay timer）。IN 上升沿后开始累加 ET，达到 PT 时 Q 置 TRUE"

❌ "PV 一般是正整数" — "一般"是脑补
✅ `PV : WORD`（PDF 明确给出的类型）

❌ "未列错误码，常见错误是参数越界" — 编造
✅ "⚠️ 待人工确认（PDF + InfoSys 均未列错误码）"

### B 节（中文表达）反例
❌ `## 1. 功能简述\n\nThis function block enables the asynchronous request for an event text...`
✅ `## 1. 功能简述\n\n异步请求事件文本的功能块。给定语言 ID 和事件信息后异步返回对应文本，调用方通过该 FB 的 Execute() 方法轮询完成状态...`

### C 节（占位短语）反例
❌ `## 3. 行为说明\n- 见上方功能简述。\n- 详细行为请对照 PDF 第 3.47 节。`
✅ `## 3. 行为说明\n\nbEnable 上升沿启动同步：首次同步用本地 Windows 系统时间，之后按 dwCycle 周期重新同步；bValid = FALSE 时 systemTime 无效；dwOpt 的 Bit0 = 1 时附加同步硬件 RTC...`

❌ `| bExecute | BOOL | （详见 PDF） |`
✅ `| bExecute | BOOL | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零 |`

### D 节（例程价值）反例
❌
```
PROGRAM P_Demo_FB_LocalSystemTime
VAR
    fb : FB_LocalSystemTime;
    bEnable : BOOL;
    st : TIMESTRUCT;
END_VAR
fb(sNetID := '', bEnable := bEnable, systemTime => st);
```
✅
```
// 场景：CX5020 工控机第一次上电，需要把本地 Windows 时间同步进 PLC，让
//       后续报表的时间戳和操作员看的一致。每 5 秒自动重同步抗时钟漂移。
// 价值：不用本 FB 时需要自己写 NT_GetTime+TimeZone 转换+RTC 校准 3 个调
//       用；用本 FB 一行调用就完成（按 InfoSys 35008651 描述）。
// 验证：登录后写 bEnable := TRUE，观察 bValid 在 1-2 个 PLC 周期后变 TRUE，
//       st.wYear/wMonth/wDay 应与本机 Windows 任务栏时钟一致；过 5 秒后
//       不动 bEnable 也能看见 st 自动刷新（cyclic resync）。
PROGRAM P_Demo_FB_LocalSystemTime
VAR
    fbLocalTime  : FB_LocalSystemTime;
    bEnableSync  : BOOL := FALSE;          // 在线置 TRUE 触发首次同步
    stCurrentTime: TIMESTRUCT;              // 在线 monitor 这个观察是否在走
    bTimeValid   : BOOL;                    // 同步成功后该位为 TRUE
END_VAR
// 单次调用形式：用 5 秒作为重同步周期（PDF default 也是 5）
fbLocalTime(sNetID := '', bEnable := bEnableSync, dwCycle := 5, dwOpt := 1,
            tTimeout := DEFAULT_ADS_TIMEOUT,
            bValid => bTimeValid, systemTime => stCurrentTime);
```

### E 节（InfoSys 验证）反例
❌ `Source InfoSys: https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/` — 只到库根，没指到具体 topic
✅ `Source InfoSys: https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35008651.html` — 直接指向 FB_LocalSystemTime topic

❌ `InfoSys-checked: -` — 没做交叉验证
✅ `InfoSys-checked: ✅ 2026-05-11`

### 例程风格反例
❌ `fbTON.IN := bMotorReq;` 单独成行 + `fbTON();` 双步调用
✅ `fbTON(IN := bMotorReq, PT := T#3S, Q => bRunOk);` 单次完整调用

❌ TcPOU CDATA 外的 ST 文本 `if x < 5 then` 没转义
✅ `if x &lt; 5 then`

## 当前数据基线（2026-05-11）

`verify_doc.py` 加占位短语扫描后预计 main 上有 **数百篇** doc FAIL（详见 PR 的 audit 报告）。整改思路：

1. 先合本 PR（charter + 强化的 verify_doc）建立新基线
2. 再按库逐个开 rewrite PR：把 §1 翻译、§3 改写、变量描述补全、例程加场景
3. 每库 rewrite 完跑双源 diff（PDF + InfoSys）确保正确性
4. 不许"批量正则糊弄"——每篇必须被人/agent 实读 PDF + InfoSys 后改写
