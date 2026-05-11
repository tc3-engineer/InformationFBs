# FB_CheckWatchdog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DataExchange` |
| Library Version | `1.2.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Watchdog function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dataexchange/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CheckWatchdog.xml`](../examples/P_Demo_FB_CheckWatchdog.xml) |

---

## 1. 功能简述

监视由 `FB_WriteWatchdog` 发送的 watchdog 计数器。被监视设备周期性把递增的计数值发到本设备，FB 监控 `nCnt` 是否在 `tWatchdogTime` 内变化——不变则置 `bWatchdog = TRUE`。`tWatchdogTime = 0s` 时 `bWatchdog` 强制 FALSE。建议 `tWatchdogTime` 设为发送周期的 5-10 倍。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable        :  BOOL := FALSE;
    tWatchdogTime  :  TIME := t#0s;
    nCnt           :  UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEnable` | `BOOL` | 使能 |
| `tWatchdogTime` | `TIME` | nCnt 必须在此时长内发生变化 |
| `nCnt` | `UDINT` | watchdog 信号当前计数值 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bWatchdog  : BOOL := FALSE;
    nLastCnt   : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bWatchdog` | `BOOL` | FALSE = 监视信号有效；TRUE = 超时未变化 |
| `nLastCnt` | `UDINT` | 最近一次成功收到的计数值 |


### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方'功能简述'。
- 调用细节随平台/参数而异，请逐项核对 PDF 原文。

## 4. 错误码 / 返回值


PDF 列出了 ERR/bError 与 ERRID/nErrId 输出但未列具体错误码表（⚠️ 待人工补充错误码表，可参考 InfoSys 在线版）。

## 5. 使用注意 / 常见坑


- `tWatchdogTime` 应至少为发送周期的 5-10 倍，避免抖动误报。
- `tWatchdogTime = 0s` 在 `FB_CheckWatchdog` 强制 `bWatchdog = FALSE`；在 `FB_WriteWatchdog` 停止发送。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CheckWatchdog.xml`](../examples/P_Demo_FB_CheckWatchdog.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CheckWatchdog
VAR
    fbFB_CheckWatchdog : FB_CheckWatchdog;
    arg_bEnable       : BOOL;
    arg_tWatchdogTime : TIME;
    arg_nCnt          : UDINT;
    out_bWatchdog     : BOOL;
    out_nLastCnt      : UDINT;
END_VAR

fbFB_CheckWatchdog(
    bEnable := arg_bEnable,
    tWatchdogTime := arg_tWatchdogTime,
    nCnt := arg_nCnt,
    bWatchdog => out_bWatchdog,
    nLastCnt => out_nLastCnt
);
```

## 7. 相关

- 见 [`Tc2_DataExchange README`](../README.md) 同库其他条目

## 8. 待确认项


- 错误码表：PDF 未列出，需参考 InfoSys 或 Beckhoff support 进一步补充。
