# RTC_EX2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35016203.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_RTC_EX2.TcPOU`](../examples/P_Demo_RTC_EX2.TcPOU) |

---

## 1. 功能简述

RTC_EX2 是 RTC 系列的最终版：在 RTC_EX 基础上把 `TIMESTRUCT` 全面替换为 `TIMESTRUCT`（含毫秒）输出，并加上时区 / 夏令时支持（`CDT` 现在真的会根据时区状态翻 TRUE/FALSE）。是 `FB_LocalSystemTime` 内部用来做自走时钟的底层 FB。

新代码做时间戳 / 日志时钟基础推荐直接用 RTC_EX2 + 配合 NT_GetTime（外部校准源）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    EN : BOOL;
    PDT : TIMESTRUCT;
    PMICRO : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `EN` | `BOOL` | TRUE 使能；上升沿装载 `PDT`。 |
| `PDT` | `TIMESTRUCT` | 外部参考时间（带时区信息），使能期间也可校准。 |
| `PMICRO` | `DWORD` | 无符号整数输入：`PMICRO`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q : BOOL;
    CDT : TIMESTRUCT;
    CMICRO : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | 输出布尔标志：`Q`。具体语义见 §3 行为说明。 |
| `CDT` | `TIMESTRUCT` | TRUE = 当前为夏令时；FALSE = 标准时。 |
| `CMICRO` | `DWORD` | 无符号整数输出：`CMICRO`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**启动 / 推进 / 校准**：与 RTC_EX 相同。

**夏令时**：FB 内部不再硬编码 CDT = FALSE，而是从 `PDT` 中提取（如果 `PDT` 由 FB_LocalSystemTime 提供，则带时区信息），或在使用 NT_GetTime 校准时一并采集时区状态。

**毫秒精度**：每个 PLC 周期把任务周期累加，输出 `TIMESTRUCT` 含 `wMilliseconds` 字段。

**典型用法**：通常不直接调用 RTC_EX2，而是用更高层的 `FB_LocalSystemTime`（它内部组合了 RTC_EX2 + NT_GetTime + 时区查询）。直接使用 RTC_EX2 的场景是定制时间源（如 GPS / DCF77 输入做 `PDT`）。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **优先用 FB_LocalSystemTime**：直接用 RTC_EX2 需要自己提供 `PDT` 与时区一致性；用 FB_LocalSystemTime 一行调用即可。（工程经验补充）
- `PDT` 输入要在每次校准时同步更新时区，否则 `CDT` 不会跟随切换。
- 毫秒精度仍受 PLC 任务周期限制（10 ms 任务 → 5 ms 抖动）。
- PLC 重启后状态丢失。（工程经验补充）
- PDF 没有列错误码——本 FB 无错误输出。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RTC_EX2.TcPOU`](../examples/P_Demo_RTC_EX2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：GPS 接收模块输出 PPS + 时间报文，业务程序解析后填 `PDT`，用 RTC_EX2 在 GPS 帧之间自走。
- **价值**：带时区感知 + 毫秒 + 自动校准的软时钟，是 FB_LocalSystemTime 内部底层。
- **替代方案对比**：
  - FB_LocalSystemTime（推荐）：一行调用搞定，省 5-6 个底层 FB 组合。
  - RTC_EX：无时区支持。
  - **本 FB**：自定义校准源场景。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.81
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35016203.html
- **相关 FB**：`RTC`, `RTC_EX`, `FB_LocalSystemTime`, `NT_GetTime`
