# FB_ReadTaskExceedCounter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/11267603979.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ReadTaskExceedCounter.xml`](../examples/P_Demo_FB_ReadTaskExceedCounter.xml) |

---

## 1. 功能简述

FB_ReadTaskExceedCounter 通过 ADS 读取指定任务的 Exceed Counter（周期超限计数）。Exceed Counter 由 TwinCAT 系统在该任务每次未能在规定周期内完成时递增，常用来排查 FOR/WHILE 长循环、阻塞调用、磁盘 I/O 占用导致的实时性问题。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute         : BOOL;
    nTaskAdsPort     : UINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | - | 上升沿触发一次读取。在 `bBusy` 为 TRUE 期间需保持 TRUE 直到完成后再清零。 |
| `nTaskAdsPort` | `UINT` | - | 目标任务的 ADS 端口号。可用 `TwinCAT_SystemInfoVarList._TaskInfo[GETCURTASKINDEXEX()].AdsPort` 取当前任务端口。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy          : BOOL;
    bError         : BOOL;
    nErrorID       : UDINT;
    nExceedCounter : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 正在执行 ADS 读，期间不接受新的 `bExecute` 上升沿。 |
| `bError` | `BOOL` | 上次执行检测到错误。`bBusy` 落沿后稳定可读。 |
| `nErrorID` | `UDINT` | ADS 错误码；详见 ⚠️『ADS Return Codes』参考表。 |
| `nExceedCounter` | `UDINT` | 从任务 ADS 端口读出的当前 Exceed Counter 累计值。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须周期调用让内部 ADS 异步状态机推进。`bExecute` 上升沿启动一次读：`bBusy := TRUE` 直到收到 ADS 应答；应答成功时 `nExceedCounter` 装入读出的值、`bError := FALSE`；应答失败时 `bError := TRUE`、`nErrorID` 写入 ADS 错误码。`bBusy` 回落到 FALSE 后才允许下一次 `bExecute` 上升沿。

**任务端口怎么填**：`nTaskAdsPort` 是 PLC 任务的 ADS 端口（不是 PLC runtime 的 851）。每个任务在系统启动时被分配一个唯一端口号；典型代码 `nTaskAdsPort := TwinCAT_SystemInfoVarList._TaskInfo[GETCURTASKINDEXEX()].AdsPort;` 取当前任务端口。需要查别的任务可改下标。

**典型用法**：在调试或运行监控里周期触发一次，把 `nExceedCounter` 写到 HMI 趋势上；如果计数器持续上扬就需要把任务实时性瓶颈定位出来；可配合 `FB_ResetTaskExceedCounter` 在排查后清零重新观察。

## 4. 错误码 / 返回值

`nErrorID` 为标准 ADS 错误码。常见取值参考 ⚠️『ADS Return Codes』参考表（PDF 与 InfoSys 均未在本节列举完整码表，工程上常见 6 = ADS port not found, 7 = ADS target not found, 1861 = 调用超时）。

## 5. 使用注意 / 常见坑

- 本 FB 自 Tc2_System >= 3.4.25.0 起提供；旧版本工程升级 Tc2_System 才能用。
- `nTaskAdsPort` 写错会得到错误码而不是 0 计数，注意区分。
- 如果想观察实时性趋势，与 `FB_ResetTaskExceedCounter` 搭配先清零再周期采样能避免被历史累计淹没。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ReadTaskExceedCounter.xml`](../examples/P_Demo_FB_ReadTaskExceedCounter.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 控制器上 1 ms 任务最近偶发卡顿，需要量化「每分钟超限多少次」做实时性回归。
- **价值**：替代登录到 System Manager 看 Task 属性窗口，本 FB 一行调用就把 Exceed Counter 取到 PLC 变量，可以接到 HMI 趋势曲线或写入日志。
- **替代方案对比**：手写 `ADSREAD(IDXGRP := ADSIGRP_SYM_VALBYHND, IDXOFFS := <task handle>)` 需要先 `ADSRDWRT` 拿句柄、再 `ADSREAD` 读值，是约 50 行代码且要写错误处理；本 FB 一行替代。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/11267603979.html
- **相关 FB / FC**：`FB_ResetTaskExceedCounter`（同节配对，用于清零）、`GETCURTASKINDEXEX`（取当前任务端口）
