# RTC_EX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35014923.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_RTC_EX.xml`](../examples/P_Demo_RTC_EX.xml) |

---

## 1. 功能简述

RTC_EX 是 RTC 的增强版：在 RTC 的基础上增加毫秒级精度（`ACT_TIME` 类型 `LTIME` 或带毫秒的 `TIMESTRUCT`），并且支持外部时钟源校准——`PDT` 输入在使能期间发生变化也会被采纳，不再仅限于上升沿装载。

适合需要做毫秒级时间戳的报表 / 日志场景，但精度仍受 PLC 任务周期限制（任务周期 10 ms → 毫秒数也只能 ±5 ms 抖动）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    EN : BOOL;
    PDT : DATE_AND_TIME;
    PMSEK : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `EN` | `BOOL` | TRUE 使能；上升沿装载 `PDT`。 |
| `PDT` | `DATE_AND_TIME` | 外部参考时间，使能期间也可被采纳做校准。 |
| `PMSEK` | `DWORD` | 无符号整数输入：`PMSEK`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q : BOOL;
    CDT : DATE_AND_TIME;
    CMSEK : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | 输出布尔标志：`Q`。具体语义见 §3 行为说明。 |
| `CDT` | `DATE_AND_TIME` | 夏令时标志（恒 FALSE）。 |
| `CMSEK` | `DWORD` | 无符号整数输出：`CMSEK`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**初始装载**：与 RTC 相同，`EN` 上升沿装载 `PDT`。

**外部校准**：使能期间若 `PDT` 与 FB 内部当前时间差超过阈值（PDF 列出的阈值在毫秒级），FB 把内部时间向 `PDT` 拉过去，实现外部时钟（如 NT_GetTime 周期读出来）对内部 RTC 的校准。

**推进精度**：每个 PLC 周期把任务周期时长累加到 `ACT_TIME`，输出含毫秒字段。

**夏令时**：仍不支持。要时区 / 夏令时应继续向 RTC_EX2 升级。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- `PDT` 在使能期间不再是只读输入——业务侧若用同一变量做存储和输入，会被 FB 周期性拉值，可能产生反馈环。建议给 FB 专用的 `PDT` 输入变量。（工程经验补充）
- 毫秒字段精度受任务周期限制（10 ms 任务 → 毫秒抖动 ±5 ms），别用于硬实时同步。
- 夏令时 / 时区仍不支持。
- 外部校准阈值是固定的（PDF 详情见 RTC_EX2，RTC_EX 阈值在 1 秒级别）。校准太频繁会导致输出值跳动；推荐外部源采样率与 FB 调用周期匹配。（工程经验补充）
- PLC 重启后状态丢失，需要业务代码做断电保护。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RTC_EX.xml`](../examples/P_Demo_RTC_EX.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：给 OEM 设备的事件日志打带毫秒的时间戳，用 NT_GetTime 每 5 秒读一次 Windows 时间作为 PDT 校准源。
- **价值**：替代自写 RTC + 外部校准对比逻辑，约省 15 行代码。
- **替代方案对比**：
  - RTC（基础版）：无毫秒、无校准。
  - RTC_EX2（推荐）：在 RTC_EX 基础上加时区 / 夏令时支持。
  - **本 FB**：过渡选择，建议新代码直接用 RTC_EX2。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.80
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35014923.html
- **相关 FB**：`RTC`, `RTC_EX2`, `NT_GetTime`
