# RTC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35013643.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_RTC.xml`](../examples/P_Demo_RTC.xml) |

---

## 1. 功能简述

RTC（Real-Time Clock）是 PLC 内部的软时钟基础版：给一个起始日期时间和秒级使能信号，FB 按 PLC 周期自走，每秒推进 1 秒，输出当前日期时间。在没有外部时间源（DCF77 / SNTP）的场合做时间戳基础。

起始时间需要业务程序在 `EN := TRUE` 上升沿前预置；之后 FB 内部不再依赖外部输入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    EN : BOOL;
    PDT : DATE_AND_TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `EN` | `BOOL` | TRUE 使能时钟推进；上升沿装载 `PDT` 为起点。 |
| `PDT` | `DATE_AND_TIME` | 起始日期时间。`EN` 上升沿时被复制到内部时钟。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q : BOOL;
    CDT : DATE_AND_TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | 输出布尔标志：`Q`。具体语义见 §3 行为说明。 |
| `CDT` | `DATE_AND_TIME` | 夏令时标志（基础版恒为 FALSE）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**启动**：`EN := TRUE` 上升沿瞬间，FB 把 `PDT` 输入装入内部状态，作为时间基准。

**自走**：使能期间，每个 PLC 周期内部累加 PLC 任务周期时长；累积 ≥ 1 秒时 `ACT_TIME` 输出 +1 秒。因为基于 PLC 任务计数，精度受任务周期抖动影响，长期会漂移（典型每天数秒）。

**停止 / 重启**：`EN := FALSE` 时 FB 暂停推进，`ACT_TIME` 保留最后值；再次 `EN := TRUE` 上升沿会重新把 `PDT` 装载，等于 reset。

**`CDT` 输出**：固定为 FALSE（基础版 RTC 不感知夏令时；要夏令时改用 RTC_EX 或 RTC_EX2）。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- 精度受 PLC 任务周期决定，长期不准（典型每天漂移数秒到数十秒）。需要精准时间应配合 `FB_LocalSystemTime` 或 DCF77 周期校准。
- `EN := TRUE` 上升沿会重新装载 `PDT`，业务代码必须保证此刻 `PDT` 已是期望的起点；否则时间会跳回。
- 没有夏令时支持——CDT 永远 FALSE。
- PLC 重启后 RTC 状态丢失，需要业务代码持久化保存 `ACT_TIME` 并在启动时回写到 `PDT`。（工程经验补充）（工程经验补充）
- 基础版 RTC 已被 RTC_EX2 全面取代；新代码建议直接用 RTC_EX2。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RTC.xml`](../examples/P_Demo_RTC.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：OEM 设备出厂没有外部时间源，用 PLC 程序里硬编码的起始时间 + RTC 自走，给现场日志打粗略时间戳。
- **价值**：封装秒级累加和起点装载逻辑，替代手写 `DT_ADD` + 计时器。
- **替代方案对比**：
  - 自写 TON + DT_ADD：可行，约 10 行代码。
  - **本 FB**：标准库提供。
  - 升级路径：用 RTC_EX2 + 同步源（DCF77 / SNTP / 本机 Windows 时间）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.79
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35013643.html
- **相关 FB**：`RTC_EX`, `RTC_EX2`, `FB_LocalSystemTime`
