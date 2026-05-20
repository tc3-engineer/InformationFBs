# AnalyzeExpressionTable

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `IEC steps / SFC flags function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/27021600003712651.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_AnalyzeExpressionTable.xml`](../examples/P_Demo_AnalyzeExpressionTable.xml) |

---

## 1. 功能简述

AnalyzeExpressionTable 与 `AnalyzeExpression` 配对：同样在 SFC 步超时时由编译器自动调用，但输出方式不同——把每个未满足的变量做成数组元素，每元素附带变量名、地址、注释、当前值。结果写入 SFC flag `SFCErrorAnalyzationTable`。**库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。

## 2. 接口定义

### VAR_INPUT

```iecst
(* 本 FB 由 SFC 编译器自动调用，无显式 VAR_INPUT *)
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
(* 输出通过 SFC flag SFCErrorAnalyzationTable 暴露给业务 *)
```

无 VAR_OUTPUT。

### VAR_IN_OUT

无显式接口。

## 3. 行为说明

**用法是配置而非调用**：与 `AnalyzeExpression` 完全相同的工程配置——引用 Tc2_System、声明 `SFCEnableLimit`、配置步最大激活时间、勾选 SFC flag、勾选 `Calculate active transitions only`。

**与 AnalyzeExpression 的差异**：(1) 输出 ARRAY 而非 STRING；(2) 每个未满足变量含名、地址、注释、当前值；(3) 适合 HMI 表格化展示或自动日志结构化记录。

**典型时序**：转换条件 `b1 AND (b2 OR b3)`，b1 = FALSE、b2 = FALSE、b3 = FALSE 时 `SFCErrorAnalyzationTable` 列出 b1、b2、b3 三项；若只 b1 = TRUE，则只列出 b2、b3 两项。

**限制**：与 `AnalyzeExpression` 相同——只支持 ST 编写的转换条件，不支持 CFC / LD。

## 4. 错误码 / 返回值

本 FB 通过 SFC flag `SFCErrorAnalyzationTable` 暴露分析结果数组，没有错误码。未触发超时时数组保持上次值或空。

## 5. 使用注意 / 常见坑

- **库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。
- 结构化输出便于 HMI 把『未满足变量列表 + 当前值』直接做成表格化诊断；比纯字符串分析的 `AnalyzeExpression` 更易自动化处理。
- 同样要求 ST 写的转换 + 4 个 SFC flag 都开启。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_AnalyzeExpressionTable.xml`](../examples/P_Demo_AnalyzeExpressionTable.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：智能产线想把每次 SFC 卡步事件结构化记录到 MES 数据库；用本 FB 的 `SFCErrorAnalyzationTable` 直接拿到『变量名 + 当前值』的数组，循环遍历写入 SQL 表。
- **价值**：替代解析字符串 `SFCErrorAnalyzation` 再 split + lookup 当前值。
- **替代方案对比**：HMI 仅做表面展示用 `AnalyzeExpression` 字符串够；自动日志/数据分析必须用本 FB 的结构化输出。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/27021600003712651.html
- **相关 FB / FC**：`AnalyzeExpression`（STRING 版本）、`AnalyzeExpressionCombined`
