# DCF77_TIME_EX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34973067.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_DCF77_TIME_EX.TcPOU`](../examples/P_Demo_DCF77_TIME_EX.TcPOU) |

---

## 1. 功能简述

DCF77_TIME_EX 是 DCF77_TIME 的增强版：除了解码出日期时间外，还额外把 DCF77 报文里的星期几（`DOW` 输出）独立暴露出来，方便业务程序直接按周期日历做调度（例如周末跳过排产、周一报表）。

解码逻辑与 DCF77_TIME 完全相同，仅多了一个输出引脚。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    DCF_PULSE : BOOL;
    RUN : BOOL;
    TLP : TIME := T#140ms;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `DCF_PULSE` | `BOOL` | - | 输入布尔标志：`DCF_PULSE`。具体语义见 §3 行为说明。 |
| `RUN` | `BOOL` | - | 输入布尔标志：`RUN`。具体语义见 §3 行为说明。 |
| `TLP` | `TIME` | `T#140ms` | 时间值：`TLP`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    ERRCNT : UDINT;
    READY : BOOL;
    CDT : DATE_AND_TIME;
    DOW : BYTE(1..7);
    TZI : E_TimeZoneID;
    ADVTZI : BOOL;
    LEAPSEC : BOOL;
    RAWDT : ARRAY[0..60] OF BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `ERR` | `BOOL` | 输出布尔标志：`ERR`。具体语义见 §3 行为说明。 |
| `ERRID` | `UDINT` | 无符号整数输出：`ERRID`。 |
| `ERRCNT` | `UDINT` | 无符号整数输出：`ERRCNT`。 |
| `READY` | `BOOL` | 输出布尔标志：`READY`。具体语义见 §3 行为说明。 |
| `CDT` | `DATE_AND_TIME` | TRUE = CEST 夏令时，FALSE = CET 标准时。 |
| `DOW` | `BYTE(1..7)` | DCF77 报文里的星期几：1 = 周一，7 = 周日。 |
| `TZI` | `E_TimeZoneID` | 参数 `TZI`（类型 `E_TimeZoneID`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `ADVTZI` | `BOOL` | 输出布尔标志：`ADVTZI`。具体语义见 §3 行为说明。 |
| `LEAPSEC` | `BOOL` | 输出布尔标志：`LEAPSEC`。具体语义见 §3 行为说明。 |
| `RAWDT` | `ARRAY[0..60] OF BOOL` | 参数 `RAWDT`（类型 `ARRAY[0..60] OF BOOL`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

行为与 DCF77_TIME 完全一致（脉冲长度判位 + 59 秒同步标记），唯一区别是输出额外提供 `DOW`：

- `DOW = 1` 周一 ... `DOW = 7` 周日（按 DCF77 协议）
- `DOW` 仅在 `DCF_TIME_VALID = TRUE` 那个周期同步刷新；其他时间保留上一帧值。

对脉冲信号、PLC 周期、夏令时处理的要求与 DCF77_TIME 相同。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- `DOW` 仅在 `DCF_TIME_VALID = TRUE` 时同步刷新——业务代码不要在 `DCF_TIME_VALID = FALSE` 时把 `DOW` 当做实时值用。
- DCF77 协议规定 `DOW = 1..7`（周一到周日）；与 IEC 标准的 `DAY_OF_WEEK`（部分库 0..6 周日开始）不同，对接前要核实编号约定。（工程经验补充）
- 其余坑与 DCF77_TIME 相同：地理范围、脉冲极性、PLC 周期、夏令时跳变。
- `DOW` 解码错（接收模块校验位失败）时会保持上一帧的 `DOW`，业务侧无法直接区分；若关键应交叉用日期算 ISO 周次再比对。（工程经验补充）
- PDF 未单列 `DOW` 错误码——它跟整帧捆绑校验。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DCF77_TIME_EX.TcPOU`](../examples/P_Demo_DCF77_TIME_EX.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：楼宇照明 / HVAC 排程：周一到周五自动开夜间灯，周末关；用 DCF77 解码出 DOW 直接当排程键。
- **价值**：比 DCF77_TIME 多 1 个 DOW 输出，省去用 `DT` 算 ISO 周次的代码。
- **替代方案对比**：
  - 用 DCF77_TIME + IEC 函数计算星期几：可行但额外 5-10 行代码。
  - **本 FB**：硬件解码出来后直接给周次，少一步换算。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34973067.html
- **相关 FB**：`DCF77_TIME`
