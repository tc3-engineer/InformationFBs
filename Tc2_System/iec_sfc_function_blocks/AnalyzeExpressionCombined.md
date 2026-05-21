# AnalyzeExpressionCombined

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `IEC steps / SFC flags function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30995851.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_AnalyzeExpressionCombined.xml`](../examples/P_Demo_AnalyzeExpressionCombined.xml) |

---

## 1. 功能简述

AnalyzeExpressionCombined 与 `AnalyzeExpression` / `AnalyzeExpressionTable` 同属 SFC 转换条件分析家族，由编译器自动调用而非业务直接实例化。**库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。

## 2. 接口定义

### VAR_INPUT

```iecst
(* 本 FB 由 SFC 编译器自动调用，无显式 VAR_INPUT *)
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
(* 输出通过 SFC 系统 flag 暴露给业务 *)
```

无 VAR_OUTPUT。

### VAR_IN_OUT

无显式接口。

## 3. 行为说明

**库要求**：仅需要在工程中引用 Tc2_System，编译器在 SFC 项目自动调用本 FB，业务代码无需声明实例。

**与 `AnalyzeExpression` 系列的关系**：本 FB 是 SFC 编译器为 'combined'（组合表达式）分析路径提供的内部 FB，对应包含子表达式组合的复杂 SFC 转换条件。PDF 在本节没有暴露其 VAR_INPUT / VAR_OUTPUT 接口或细化的时序——它是『系统暗调用』的 FB，工程师不直接接触。

**典型用法**：工程师不直接调用本 FB；要做超时诊断就配齐 4 个 SFC flag + 引用 Tc2_System，编译器自然会在合适场景调本 FB。

**何时关心**：仅在排查『SFC 分析功能不工作』时检查 Tc2_System 是否引用即可；其余时间无需了解本 FB 内部。

## 4. 错误码 / 返回值

本 FB 不向业务侧直接暴露错误码；运行错误体现在对应 SFC flag 不更新或更新为空。检查方法：先确认工程引用 Tc2_System 库，再确认 SFCEnableLimit/SFCError/SFCErrorAnalyzation/SFCErrorAnalyzationTable 四个 flag 都已 Active + Declare。

## 5. 使用注意 / 常见坑

- **库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。
- 不应在用户代码里手动实例化本 FB；它是编译器内部使用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_AnalyzeExpressionCombined.xml`](../examples/P_Demo_AnalyzeExpressionCombined.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SFC 工程的转换条件含较复杂的组合表达式（多层括号 + AND/OR 混合），编译器在做超时分析时需要本 FB 协助完成路径标注；工程师只需引用 Tc2_System 库。
- **价值**：让 `AnalyzeExpression` / `AnalyzeExpressionTable` 在复杂表达式下也能工作。
- **替代方案对比**：没有可替代方案——SFC 分析家族是个整体，要么都用要么都不用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.5.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30995851.html
- **相关 FB / FC**：`AnalyzeExpression`、`AnalyzeExpressionTable`、`AppendErrorString`
