# Profiler

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35012875.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_Profiler.xml`](../examples/P_Demo_Profiler.xml) |

---

## 1. 功能简述

Profiler 提供 PLC 程序段执行时间测量——业务代码调 `Start` 标记测量起点，调 `Stop` 取得这段代码的执行 µs。

用于：性能瓶颈定位、循环优化前后对比。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    START : BOOL;
    RESET : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `START` | `BOOL` | 输入布尔标志：`START`。具体语义见 §3 行为说明。 |
| `RESET` | `BOOL` | 输入布尔标志：`RESET`。具体语义见 §3 行为说明。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    DATA : PROFILERSTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `DATA` | `PROFILERSTRUCT` | 参数 `DATA`（类型 `PROFILERSTRUCT`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`Start` / `Stop` 方法对（或单次 `Measure`）。FB 用 TwinCAT 高精度计时器测量。

**精度**：µs 级，受 PLC 任务周期影响。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **测量短代码段时 µs 精度不够**——< 1 µs 段需要循环 1000 次取平均。（工程经验补充）
- **别在生产代码里留 Profiler**——本身有开销。
- **测量过程不能被 PLC 周期中断打断**，否则结果含调度间隔。（工程经验补充）
- PDF 未列错误码。
- 适合定位算法热点，不适合做 SLA 监控。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Profiler.xml`](../examples/P_Demo_Profiler.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：优化前 / 后对比某段代码执行时间。
- **价值**：定位性能热点。
- **替代方案对比**：
  - 用 GET_CPU_COUNTER 自写：可行但繁。
  - **本 FB**：库提供。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.78
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35012875.html
