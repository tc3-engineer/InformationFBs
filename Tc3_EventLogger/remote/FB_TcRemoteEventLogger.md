# FB_TcRemoteEventLogger
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcRemoteEventLogger.xml`](../examples/P_Demo_FB_TcRemoteEventLogger.xml) |

---
## 1. 功能简述

This function block represents the TwinCAT 3 EventLogger for a remote system. Syntax FUNCTION_BLOCK FB_RemoteEventLogger IMPLEMENTS I_RemoteEventLogger

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nTimeStamp : ULINT := 0;
    bResetConfirmation : BOOL := FALSE;
    ipFilter : I_TcEventFilter;
    ipClearSettings : I_TcClearLoggedEventsSettings;
    sNetId : T_AmsNetId;
    eventClass : GUID;
    nEventId : UDINT;
    eSeverity : TcEventSeverity;
    ipSourceInfo : I_TcSourceInfo := 0;
    ipArguments : I_TcArguments := 0;
    stEventEntry : TcEventEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nTimeStamp` | `ULINT` | （详见 PDF） |
| `bResetConfirmation` | `BOOL` | （详见 PDF） |
| `ipFilter` | `I_TcEventFilter` | （详见 PDF） |
| `ipClearSettings` | `I_TcClearLoggedEventsSettings` | （详见 PDF） |
| `sNetId` | `T_AmsNetId` | （详见 PDF） |
| `eventClass` | `GUID` | （详见 PDF） |
| `nEventId` | `UDINT` | （详见 PDF） |
| `eSeverity` | `TcEventSeverity` | （详见 PDF） |
| `ipSourceInfo` | `I_TcSourceInfo` | （详见 PDF） |
| `ipArguments` | `I_TcArguments` | （详见 PDF） |
| `stEventEntry` | `TcEventEntry` | （详见 PDF） |

### VAR_OUTPUT

无 VAR_OUTPUT。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.4.2 节。

## 4. 错误码 / 返回值

本 FB 自身无返回值；运行状态/错误反馈通过其方法返回的 `HRESULT` 或对应输出参数获取，具体见 PDF / InfoSys（⚠️ 待人工确认）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.4.2 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcRemoteEventLogger.xml`](../examples/P_Demo_FB_TcRemoteEventLogger.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_TcRemoteEventLogger
VAR
    fbFB_TcRemoteEventLogger : FB_TcRemoteEventLogger;
    arg_nTimeStamp : ULINT;
    arg_bResetConfirmation : BOOL;
    arg_ipFilter : I_TcEventFilter;
    arg_ipClearSettings : I_TcClearLoggedEventsSettings;
    arg_sNetId : T_AmsNetId;
    arg_eventClass : GUID;
    arg_nEventId : UDINT;
    arg_eSeverity : TcEventSeverity;
    arg_ipSourceInfo : I_TcSourceInfo;
    arg_ipArguments : I_TcArguments;
    arg_stEventEntry : TcEventEntry;
END_VAR

fbFB_TcRemoteEventLogger(
    nTimeStamp := arg_nTimeStamp,
    bResetConfirmation := arg_bResetConfirmation,
    ipFilter := arg_ipFilter,
    ipClearSettings := arg_ipClearSettings,
    sNetId := arg_sNetId,
    eventClass := arg_eventClass,
    nEventId := arg_nEventId,
    eSeverity := arg_eSeverity,
    ipSourceInfo := arg_ipSourceInfo,
    ipArguments := arg_ipArguments,
    stEventEntry := arg_stEventEntry
);
```

## 7. 相关

- 见 [`Tc3_EventLogger README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
