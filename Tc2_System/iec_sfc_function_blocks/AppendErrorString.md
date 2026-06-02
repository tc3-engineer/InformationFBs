# AppendErrorString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `IEC steps / SFC flags function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30997387.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_AppendErrorString.TcPOU`](../examples/P_Demo_AppendErrorString.TcPOU) |

---

## 1. 功能简述

AppendErrorString 是 SFC 错误分析家族的辅助函数（PDF 标 FB，实际语义上是辅助），用于在 SFC 项目里把错误片段追加到错误字符串。**库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。

PDF 明确：**用户代码不应直接调用本 FB**，只需把 Tc2_System 库引用进项目即可。

## 2. 接口定义

### VAR_INPUT

```iecst
(* 不暴露 VAR_INPUT；用户代码不应调用此 FB *)
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
(* 不暴露 VAR_OUTPUT *)
```

无 VAR_OUTPUT。

### VAR_IN_OUT

无。

## 3. 行为说明

**用法**：仅需把 Tc2_System 库引用进工程；本 FB 在 SFC 编译器为 `AnalyzeExpression` / `AnalyzeExpressionTable` 拼装错误字符串时被自动调用。PDF 原文明确 'must not be called in the project'。

**为什么 PDF 不暴露 VAR 区？** 因为它是内部辅助，并不向业务暴露稳定接口；接口可能在 Beckhoff 更新库时改变。文档完整列出本 FB 仅为了让工程师在排错时知道 Tc2_System 包含它，而不应试图自己调用。

**InfoSys 一致性**：InfoSys 同步收录本 entry，但与 PDF 一致——不暴露 VAR 区，仅说明 'must not be called in the project'。

## 4. 错误码 / 返回值

本 FB 不向业务暴露错误输出。只在 SFC 错误分析家族整体不工作时（即 `SFCErrorAnalyzation` 始终为空）排查是否 Tc2_System 库引用缺失。

## 5. 使用注意 / 常见坑

- **库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。
- **严禁手动调用本 FB**（PDF 明确）；只要 Tc2_System 引用就行。
- InfoSys 同步收录但同样不暴露调用接口，与 PDF 一致。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_AppendErrorString.TcPOU`](../examples/P_Demo_AppendErrorString.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：在 SFC 项目里使能错误分析功能，本 FB 作为家族成员被引用进来；工程师无感知，只需保证 Tc2_System 在工程的 References 节点下出现。
- **价值**：是 `AnalyzeExpression` / `AnalyzeExpressionTable` 完整工作所需的内部辅助。
- **替代方案对比**：无可替代——本 FB 是 SFC 错误分析家族不可拆分的一部分。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.5.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30997387.html
- **相关 FB / FC**：`AnalyzeExpression`、`AnalyzeExpressionTable`、`AnalyzeExpressionCombined`
