# F_GetSystemTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/3622991755.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetSystemTime.xml`](../examples/P_Demo_F_GetSystemTime.xml) |

---

## 1. 功能简述

F_GetSystemTime 是同步函数：读取当前操作系统时间戳。返回 64-bit `ULINT`，以 100 ns 为单位，原点为 1601-01-01 00:00:00 UTC（Windows FILETIME 风格）。每次 PLC 调用时刷新。可用于时序测量、给事件打绝对时间戳。

## 2. 接口定义

### VAR_INPUT

```iecst
(* 函数无显式 VAR_INPUT *)
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    F_GetSystemTime   : ULINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `F_GetSystemTime` | `ULINT` | 操作系统时间戳，64-bit，单位 100 ns，原点为 1601-01-01 00:00:00 UTC。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步即出值。返回的 64-bit 整数代表从 1601-01-01 UTC 起经过的 100 ns 数。Windows FILETIME 格式（与 .NET DateTime.Ticks 同基准）。

**精度与更新**：PDF 明确每次 PLC 调用时刷新，精度 100 ns。注意这是『PLC 周期级精度』而非『百纳秒级时间戳准确度』——任务周期是 1 ms 的话两次相邻调用差值不会小于 1 ms。

**典型用法**：(1) 给事件 / 工件 / 报警打绝对时间戳并写入日志或 MES；(2) 长时间间隔测量（>429 s，比 32-bit 的 `GETCPUACCOUNT` 适用范围更广）；(3) NTP 同步后做跨设备时间对齐。

**与 `GETCPUCOUNTER` 区别**：GETCPUCOUNTER 是系统启动以来的 100 ns 累计（不受 NTP 同步影响，单调）；F_GetSystemTime 是 UTC 绝对时间（受 NTP 同步可能跳变）。要做时间戳给人看用本函数；要做时序差值（不能跳变）用 GETCPUCOUNTER。

**与 `GETSYSTEMTIME` 区别**：旧 FB `GETSYSTEMTIME` 返回 2 个 UDINT 拼 64-bit（因为 IEC FUNCTION 旧规范不支持 ULINT 返回值）；新函数 `F_GetSystemTime` 直接返回 ULINT 简洁。

## 4. 错误码 / 返回值

本函数不暴露错误输出。返回值始终为当前系统时间戳。

## 5. 使用注意 / 常见坑

- 本函数自 Tc2_System >= 3.4.17.0 起可用；旧版本只能用 `GETSYSTEMTIME` FB。
- 时间原点是 1601-01-01 UTC（Windows FILETIME），不是 Unix epoch（1970-01-01）；要转 Unix 时间戳须减 `116444736000000000`（即 1601 到 1970 的 100 ns 数）。（工程经验补充）
- NTP 同步可能让时间戳跳变（往前 / 往后）；做差值测量请用 `GETCPUCOUNTER`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetSystemTime.xml`](../examples/P_Demo_F_GetSystemTime.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：包装线给每件下线产品打一个 100 ns 精度的 Windows FILETIME 时间戳并写入 MES，方便事后做产能分析。
- **价值**：替代 `GETSYSTEMTIME` FB 的两步拼接（lo+hi → 64-bit）；直接 ULINT 一行调用。
- **替代方案对比**：`GETSYSTEMTIME` FB 是旧 32-bit 双返回版；`GETCPUCOUNTER` 不是 UTC 时间不能给人看；本函数是首选。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/3622991755.html
- **相关 FB / FC**：`GETSYSTEMTIME`（旧 FB 版本，已被本函数取代）、`GETCPUCOUNTER`（单调递增，适合差值测量）、`F_GetTaskTime`
