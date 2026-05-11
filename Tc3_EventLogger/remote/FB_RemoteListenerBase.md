# FB_RemoteListenerBase
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
| Example | [`examples/P_Demo_FB_RemoteListenerBase.xml`](../examples/P_Demo_FB_RemoteListenerBase.xml) |

---
## 1. 功能简述

The function block serves as the basic implementation of an event listener of a remote system. New messages and state changes of alarms can be recognized through the overwriting of the event-driven methods. This function block provides access to the EventLogger of a remote system and can be used to send events there or receive events from there. Syntax FUNCTION_BLOCK FB_RemoteListenerBase IMPLEMENTS I_RemoteListener

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipContext : I_TcListenerContext;
    fbEvent : REFERENCE TO FB_TcEvent;
    eReason : TcRemoteConnectionChangeReason;
    eReason : TcDatabaseChangeReason;
    hr : HRESULT;
    ipRemoteLogger : I_TcRemoteEventLogger;
    ipEventFilter : I_TcEventFilterBase;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipContext` | `I_TcListenerContext` | （详见 PDF） |
| `fbEvent` | `REFERENCE TO FB_TcEvent` | （详见 PDF） |
| `eReason` | `TcRemoteConnectionChangeReason` | （详见 PDF） |
| `eReason` | `TcDatabaseChangeReason` | （详见 PDF） |
| `hr` | `HRESULT` | （详见 PDF） |
| `ipRemoteLogger` | `I_TcRemoteEventLogger` | （详见 PDF） |
| `ipEventFilter` | `I_TcEventFilterBase` | （详见 PDF） |

### VAR_OUTPUT

无 VAR_OUTPUT。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.4.1 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.4.1 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RemoteListenerBase.xml`](../examples/P_Demo_FB_RemoteListenerBase.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_RemoteListenerBase
VAR
    fbFB_RemoteListenerBase : FB_RemoteListenerBase;
    arg_ipContext : I_TcListenerContext;
    arg_fbEvent : REFERENCE TO FB_TcEvent;
    arg_eReason : TcRemoteConnectionChangeReason;
    arg_eReason : TcDatabaseChangeReason;
    arg_hr : HRESULT;
    arg_ipRemoteLogger : I_TcRemoteEventLogger;
    arg_ipEventFilter : I_TcEventFilterBase;
END_VAR

fbFB_RemoteListenerBase(
    ipContext := arg_ipContext,
    fbEvent := arg_fbEvent,
    eReason := arg_eReason,
    eReason := arg_eReason,
    hr := arg_hr,
    ipRemoteLogger := arg_ipRemoteLogger,
    ipEventFilter := arg_ipEventFilter
);
```

## 7. 相关

- 见 [`Tc3_EventLogger README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
