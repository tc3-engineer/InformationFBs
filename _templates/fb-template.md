# <FB_OR_FC_NAME>

<!--
本模板是强约束。生成文档时必须严格按此格式输出。
2026-05-11 起执行新硬规则（详见 CLAUDE.md B/C/D/E）：
 - 正文全中文叙述，禁止英文整句
 - 禁止 "详见 PDF" / "见上方" / "请对照 PDF 第 X 节" 等占位短语
 - 每篇必带 InfoSys topic URL + InfoSys-checked 状态
 - 例程必带 场景/价值/验证步骤 三件套
缺失字段标 ⚠️ 待人工确认，不要凭空补全。
-->

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_XXXX` |
| Library Version | `x.y.z` |
| Type | `FUNCTION_BLOCK` / `FUNCTION` / `METHOD` |
| Category | `Bistable` / `Counter` / `Timer` / ... |
| Source PDF | `https://download.beckhoff.com/.../TwinCAT_3_PLC_Lib_Tc2_XXXX_EN.pdf` |
| Source InfoSys | `https://infosys.beckhoff.com/content/1033/tcplclib_tc2_xxxx/<topicid>.html` |
| Verified | `YYYY-MM-DD` ✅ |
| InfoSys-checked | `✅ YYYY-MM-DD` / `⚠️ not-on-infosys` |
| Status | `verified` / `⚠️ verify-failed` / `pending` |
| Example | [`examples/P_Demo_<Name>.xml`](../examples/P_Demo_<Name>.xml) |

---

## 1. 功能简述

<!-- 2-4 句中文叙述。把 PDF / InfoSys 的英文 Description 段翻译成中文，
不许残留 "This function block ..." 英文原句。技术名词首次出现标双语。 -->

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    <name> : <type> := <default>;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `<name>` | `<type>` | `<default>` | 翻译自 InfoSys/PDF Description 列；不许填"（详见 PDF）" |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    <name> : <type>;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `<name>` | `<type>` | 翻译自 InfoSys/PDF Description 列 |

### VAR_IN_OUT

无 / `<name> : <type>` （明确写"无"，不要写"见 PDF"）

## 3. 行为说明

<!-- 必须中文叙述（≥80 个汉字）。覆盖：
   - 时序：什么触发执行（上升沿/电平/调用即执行）
   - 状态机：如有 Busy/Done/Error 三态，画分支
   - 触发语义区分：电平 vs 边沿
   - 典型用法：调用周期、何时清错
   - 典型陷阱：忘清错、tTimeout 太小、并发实例冲突等
禁止 "见上方功能简述" / "请对照 PDF 第 X 节"。 -->

## 4. 错误码 / 返回值

<!-- 按 FUNCTION/METHOD 实际声明的返回类型填：
  - HRESULT 类：列出 S_OK / E_FAIL / E_INVALIDARG / 自定义码
  - BOOL 类：说明 TRUE = 什么 / FALSE = 什么
  - 通过 bError + nErrorId 输出的类：列错误码表
PDF + InfoSys 都没列 → 整段写 "PDF + InfoSys 均未列错误码（⚠️ 待人工确认）" -->

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `S_OK` / 0 | 成功 | 继续下一步 |

## 5. 使用注意 / 常见坑

<!-- 来自 PDF/InfoSys 的注意事项原话翻译 + 工程经验补充。
工程经验补充必须明确标注 "（工程经验补充）"。 -->

- 

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_<Name>.xml`](../examples/P_Demo_<Name>.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_<Name>
VAR
    fb<Name> : <Name>;
    // ... 业务化命名的输入信号
END_VAR

// 单次调用形式：所有 VAR_INPUT 显式赋值
fb<Name>(
    arg1 := value1,
    arg2 := value2,
    out1 => watch1
);
```

## 7. 业务场景与实际价值

<!-- 强制章节。回答三个问题，每问一段中文：
 1. 场景：这个 FB 在真实工程里解决什么具体问题？（设备/系统/工况）
 2. 价值：用 vs 不用的区别？（节省了哪些手写代码 / 避免了什么坑）
 3. 替代方案：不用本 FB 还能怎么做？为什么本 FB 更好？
-->

- **场景**：
- **价值**：
- **替代方案对比**：

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_<Lib>_EN.pdf`](<URL>) 第 X.Y 节
- **InfoSys topic**：<InfoSys URL>
- **相关 FB / FC**：`<other>`（同类）、`<other>`（上下游）

## 9. 待确认项 (⚠️)

<!-- PDF 与 InfoSys 都不一致 / 都缺失 / 含糊的字段列在这里。
如无则整段删除。 -->

- 
