# SFCActionControl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `IEC steps / SFC flags function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30992779.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_SFCActionControl.TcPOU`](../examples/P_Demo_SFCActionControl.TcPOU) |

---

## 1. 功能简述

SFCActionControl 是 IEC SFC 步『action』控制功能块。在 SFC 项目中使用 IEC 步（IEC Steps，区别于经典步）的 action 限定符（N、S、R、P 等）时需要该 FB；编译器自动调用，业务代码不直接实例化。**库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。

## 2. 接口定义

### VAR_INPUT

```iecst
(* 本 FB 由 SFC 编译器自动调用，无显式 VAR_INPUT *)
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
(* 输出由编译器内部使用 *)
```

无 VAR_OUTPUT。

### VAR_IN_OUT

无显式接口。

## 3. 行为说明

**用法**：仅需在使用 IEC 步的 SFC 工程里引用 Tc2_System 库即可；编译器把每个 action 的限定符语义（N - 非保持、S - set、R - reset、P - pulse、L - 限时等）翻译成对本 FB 的调用。

**业务侧零侵入**：工程师在 SFC 图里画出步、连上 action 块、给 action 选限定符，编译就生成正确逻辑；不需要 `fbSFCActionControl : SFCActionControl;` 这种声明。

**何时关心**：仅在『IEC 步的 action 限定符不工作』时排查 Tc2_System 是否引用即可。

**与经典步的区别**：经典 SFC 步只用 N（非保持）限定符；IEC 步支持完整 11 种限定符，需要本 FB 支持。

## 4. 错误码 / 返回值

本 FB 不向业务直接暴露错误码。运行问题体现为 action 限定符语义错误（如 S 之后不停留、P 不脉冲）。检查方法：确认 Tc2_System 库被工程引用。

## 5. 使用注意 / 常见坑

- **库要求**：使用 SFC 流程时此 FB / 函数所在的 Tc2_System 库必须被引用；编译器自动调用，**用户业务代码不需要也不应该手动调用或实例化**。
- 仅 IEC 步需要；经典 SFC 步不需要本 FB。
- IEC 步限定符完整列表（N/S/R/P/L/D/DS/SD/SL/P0/P1）的语义见 IEC 61131-3 SFC 章节。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SFCActionControl.TcPOU`](../examples/P_Demo_SFCActionControl.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：复杂 SFC 工艺需要 'S - set' 限定符（让某 action 一旦被进入步激活就持续保持直到被 R 复位）；用 IEC 步实现而非经典步；只需引用 Tc2_System 即可。
- **价值**：替代用经典步 + 手写 set/reset 全局 flag，节省代码量并由编译器保证语义正确。
- **替代方案对比**：经典步只支持 N，复杂工艺要全限定符必须用 IEC 步并引入 Tc2_System。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.5.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30992779.html
- **相关 FB / FC**：`AnalyzeExpression`、IEC 61131-3 SFC 章节
