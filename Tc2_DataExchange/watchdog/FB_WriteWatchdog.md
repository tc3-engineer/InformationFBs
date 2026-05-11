# FB_WriteWatchdog

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
| Example | [`examples/P_Demo_FB_WriteWatchdog.xml`](../examples/P_Demo_FB_WriteWatchdog.xml) |

---

## 1. 功能简述

向另一 ADS 设备（PLC、Bus Terminal Controller…）周期写入 watchdog 计数器（每次成功发送后 +1）。接收方用 `FB_CheckWatchdog` 评估。地址通过 AmsNetId + Port 指定，写入位置由 IndexGroup/Offset 或符号名指定。`tWatchdogTime` 不应小于 1 秒；`= 0s` 则停止发送。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable          :  BOOL := FALSE;
    sNetId           :  T_AmsNetId;
    nPort            :  T_AmsPort;
    nIdxGrp          :  UDINT;
    nIdxOffs         :  UDINT;
    sVarName         :  STRING;
    tWatchdogTime    :  TIME := t#0s;
    bSendNow         :  BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEnable` | `BOOL` | 使能 |
| `sNetId` | `T_AmsNetId` | 目标 ADS 设备 AmsNetId |
| `nPort` | `T_AmsPort` | 目标 AMS 端口 |
| `nIdxGrp` | `UDINT` | 目标 IndexGroup |
| `nIdxOffs` | `UDINT` | 目标 IndexOffset |
| `sVarName` | `STRING` | 目标符号名（IndexGroup/Offset 与之二选一） |
| `tWatchdogTime` | `TIME` | 发送周期 |
| `bSendNow` | `BOOL` | 上升沿立即发送一次 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     :  BOOL := FALSE;
    nLastCnt  :  UDINT := 0;
    bError    :  BOOL := FALSE;
    nErrorId  :  UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 传输进行中 |
| `nLastCnt` | `UDINT` | 最近一次发送的计数值 |
| `bError` | `BOOL` | 传输出错 |
| `nErrorId` | `UDINT` | ADS 错误号 |


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

> 配套可导入文件：[`examples/P_Demo_FB_WriteWatchdog.xml`](../examples/P_Demo_FB_WriteWatchdog.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_WriteWatchdog
VAR
    fbFB_WriteWatchdog : FB_WriteWatchdog;
    arg_bEnable       : BOOL;
    arg_sNetId        : T_AmsNetId;
    arg_nPort         : T_AmsPort;
    arg_nIdxGrp       : UDINT;
    arg_nIdxOffs      : UDINT;
    arg_sVarName      : STRING;
    arg_tWatchdogTime : TIME;
    arg_bSendNow      : BOOL;
    out_bBusy         : BOOL;
    out_nLastCnt      : UDINT;
    out_bError        : BOOL;
    out_nErrorId      : UDINT;
END_VAR

fbFB_WriteWatchdog(
    bEnable := arg_bEnable,
    sNetId := arg_sNetId,
    nPort := arg_nPort,
    nIdxGrp := arg_nIdxGrp,
    nIdxOffs := arg_nIdxOffs,
    sVarName := arg_sVarName,
    tWatchdogTime := arg_tWatchdogTime,
    bSendNow := arg_bSendNow,
    bBusy => out_bBusy,
    nLastCnt => out_nLastCnt,
    bError => out_bError,
    nErrorId => out_nErrorId
);
```

## 7. 相关

- 见 [`Tc2_DataExchange README`](../README.md) 同库其他条目

## 8. 待确认项


- 错误码表：PDF 未列出，需参考 InfoSys 或 Beckhoff support 进一步补充。
