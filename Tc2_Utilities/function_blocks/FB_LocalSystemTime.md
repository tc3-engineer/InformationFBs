# FB_LocalSystemTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35008651.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_LocalSystemTime.xml`](../examples/P_Demo_FB_LocalSystemTime.xml) |

---

## 1. 功能简述

FB_LocalSystemTime 把本机 Windows 系统时间（任务栏右下角看到的那个时钟）周期同步到 PLC 内部，并把当前时区状态（夏令时 / 标准时）一并提供给业务程序。PLC 内部用同步后的时间打时间戳，可以保证 HMI 日志、报表、报警的时间戳与操作员桌面时钟一致。

内部组合 RTC_EX2、NT_GetTime、FB_GetTimeZoneInformation、NT_SetTimeToRTCTime 四个底层 FB：首次使能用 NT_GetTime 拉 Windows 时间作为基准，之后由 RTC_EX2 自走，按 `dwCycle` 秒周期重同步以抗时钟漂移。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID := '';
    bEnable : BOOL;
    dwCycle : DWORD(1..86400) := 5;
    dwOpt : DWORD := 1;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `bEnable` | `BOOL` | - | TRUE 时启用周期同步；FALSE 时停止。电平触发，不是上升沿。 |
| `dwCycle` | `DWORD(1..86400)` | `5` | 重同步周期，单位秒。范围 1..86400。默认 5。 |
| `dwOpt` | `DWORD` | `1` | 选项位掩码。Bit0 = 1 同步时也写硬件 RTC；= 0 仅软件同步。默认 1。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bValid : BOOL;
    systemTime : TIMESTRUCT;
    tzID : E_TimeZoneID := eTimeZoneID_Invalid;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bValid` | `BOOL` | - | TRUE 表示 `systemTime` 已装载有效值；首次同步未完成或被禁用时为 FALSE。 |
| `systemTime` | `TIMESTRUCT` | - | 同步后的本地系统时间，`TIMESTRUCT` 结构。 |
| `tzID` | `E_TimeZoneID` | `eTimeZoneID_Invalid` | 当前时区标识：`eTimeZoneID_Standard` / `eTimeZoneID_Daylight` / `eTimeZoneID_Invalid`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须周期调用（建议每 PLC 周期一次或每秒一次），否则两次同步之间的累加无法推进。

**时序**：`bEnable` 上升沿后通过 ADS 异步读 Windows 时间，数个 PLC 周期后 `bValid := TRUE` 并装载 `systemTime` 与 `tzID`；之后内部自走，每过 `dwCycle` 秒重新同步一次。`bEnable := FALSE` 时停止内部计数，`bValid := FALSE`，`systemTime` 保留最后值。

**`dwOpt` 位掩码**：Bit0 = 1 表示同步后也写硬件 RTC（CMOS 时钟），= 0 仅同步软件时间。默认 1。

**夏令时切换**：FB 不可能精确踩在切换瞬间，所以切换会被延迟到下一次同步窗口才反映在 `tzID` 上，PDF 例子显示延迟通常在 15 秒内。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- `dwCycle` 类型为 `DWORD(1..86400)`，写 0 或 > 86400 会编译报错。
- `systemTime.wMilliseconds` 由 RTC_EX2 内部按 PLC 周期累加，并非 Windows 真实毫秒；只适合相对计时。
- ADS 抖动导致首次同步可能要 1-2 个 PLC 周期才把 `bValid` 拉起，使能后不要立刻读 `systemTime` 做关键判断。
- CX 设备断电后 Windows 系统时间本身可能不准（CMOS 电池耗尽），同步出来的也不准；需要精确时钟应外接 SNTP / DCF77。（工程经验补充）
- `tTimeout` 设得过短（< 100 ms）在跨网段调用时容易超时，本地一般 5 秒（默认）足够。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_LocalSystemTime.xml`](../examples/P_Demo_FB_LocalSystemTime.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 工控机首次上电后把 Windows 时间同步到 PLC，让 HMI 日志、报表时间戳与桌面时钟一致；按 5 秒周期重同步抗漂移。
- **价值**：不用本 FB 时需要组合 `NT_GetTime` + `RTC_EX2` + `FB_GetTimeZoneInformation` 三个底层调用并自己维护同步状态机，本 FB 一行调用替代约 30 行手写代码。
- **替代方案对比**：
  - `NT_GetTime`：只能单次读取，不能周期同步。
  - `RTC_EX2`：能走时但与 Windows 时钟不同步，会漂移。
  - **本 FB**：两者组合并自动重同步，是 Tc2_Utilities 推荐方案。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.47
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35008651.html
- **相关 FB**：`NT_GetTime`, `RTC_EX2`, `FB_GetTimeZoneInformation`, `NT_SetTimeToRTCTime`
