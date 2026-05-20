# AnalyzeExpression

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `IEC steps / SFC flags function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30994315.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_AnalyzeExpression.xml`](../examples/P_Demo_AnalyzeExpression.xml) |

---

## 1. 功能简述

AnalyzeExpression 是 SFC 转换条件分析功能块，当 SFC 步因转换条件未满足而停留超时（超过该步配置的『最大激活时间』）时，由系统自动调用本 FB 分析转换表达式中哪些子条件未满足，并把结果作为字符串写入 SFC flag `SFCErrorAnalyzation`。**库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。

## 2. 接口定义

### VAR_INPUT

```iecst
(* 本 FB 由 SFC 编译器自动调用，无显式 VAR_INPUT。
   只要 Tc2_System 库被引用即可启用 SFC error 分析。 *)
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
(* 输出通过 SFC flag SFCErrorAnalyzation : STRING 暴露给业务，
   不通过本 FB 的 VAR_OUTPUT 直接给出 *)
```

无 VAR_OUTPUT。

### VAR_IN_OUT

无显式接口。本 FB 在 SFC 项目中由编译器自动调用。

## 3. 行为说明

**用法是配置而非调用**：(1) 工程引用 Tc2_System 库；(2) 在 SFC POU 里声明 `SFCEnableLimit: BOOL := TRUE;`；(3) 在 SFC 步属性里配置最大激活时间（如 1 s）；(4) 在 PLC 项目属性 → SFC 标签页把 `SFCError`、`SFCEnableLimit`、`SFCErrorAnalyzation`、`SFCErrorAnalyzationTable` 这几个 flag 的 Active / Declare 都勾上；(5) Build 标签页勾选 `Calculate active transitions only`。配齐后即生效。

**典型时序**（PDF 示例）：某步 Step1 配置最大激活时间 1 s，对应转换 Trans_ST 的表达式是 `b1 AND (b2 OR b3)`。1 s 后若三个变量都为 FALSE，则 `SFCErrorAnalyzation := 'b1 AND (b2 OR b3)'`；若只 b1 = TRUE 而 b2、b3 都为 FALSE，则 `SFCErrorAnalyzation := '(b2 OR b3)'`——只列出真正阻塞的子表达式。

**限制**：只能分析在 ST 编程语言中实现的转换 / 步使能条件；CFC、LD 写的转换条件不能用本 FB 分析。

**与 AnalyzeExpressionTable 区别**：本 FB 输出整段 STRING；后者把每个未满足的变量做成 ARRAY 元素并附带变量名、地址、注释、当前值等结构化信息。

## 4. 错误码 / 返回值

本 FB 通过 SFC flag `SFCErrorAnalyzation : STRING` 暴露分析结果，没有错误码。如果未触发条件超时则字符串保持上次值或空。

## 5. 使用注意 / 常见坑

- **库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。
- 只支持 ST 编写的转换条件；CFC / LD 不行（PDF 明确）。
- 需要在 PLC 项目属性里把 4 个 SFC flag 都开启 + 勾选 `Calculate active transitions only`，否则不工作。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_AnalyzeExpression.xml`](../examples/P_Demo_AnalyzeExpression.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工厂生产线 SFC 流程偶发卡顿，操作员只看到『卡在 Step5』但不知道是哪个传感器没到位；启用本 FB 后超时自动把表达式分析结果推到 HMI 显示『等待 (bSensorA OR bSensorB)』，定位故障从分钟级降到秒级。
- **价值**：替代手写每步超时 + 手写表达式诊断（容易写错），编译器自动注入。
- **替代方案对比**：手写诊断代码冗长且不可扩展；本 FB 对所有 ST 转换条件自动分析。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30994315.html
- **相关 FB / FC**：`AnalyzeExpressionTable`（结构化 ARRAY 输出版）、`AnalyzeExpressionCombined`、`AppendErrorString`
