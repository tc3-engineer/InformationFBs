# FB_RequestEventText
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
| Example | [`examples/P_Demo_FB_RequestEventText.xml`](../examples/P_Demo_FB_RequestEventText.xml) |

---
## 1. 功能简述

This function block enables the asynchronous request for an event text in the desired language.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sResult : REFERENCE TO STRING;
    nResult : UDINT;
    eventClass : GUID;
    nEventId : UDINT;
    nLangId : DINT;
    ipArgs : I_TcArguments;
    ipRemoteLogger : I_TcRemoteEventLogger;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sResult` | `REFERENCE TO STRING` | （详见 PDF） |
| `nResult` | `UDINT` | （详见 PDF） |
| `eventClass` | `GUID` | （详见 PDF） |
| `nEventId` | `UDINT` | （详见 PDF） |
| `nLangId` | `DINT` | （详见 PDF） |
| `ipArgs` | `I_TcArguments` | （详见 PDF） |
| `ipRemoteLogger` | `I_TcRemoteEventLogger` | （详见 PDF） |

### VAR_OUTPUT

无 VAR_OUTPUT。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.1.6 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.1.6 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RequestEventText.xml`](../examples/P_Demo_FB_RequestEventText.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_RequestEventText
VAR
    fbFB_RequestEventText : FB_RequestEventText;
    arg_sResult : REFERENCE TO STRING;
    arg_nResult : UDINT;
    arg_eventClass : GUID;
    arg_nEventId : UDINT;
    arg_nLangId : DINT;
    arg_ipArgs : I_TcArguments;
    arg_ipRemoteLogger : I_TcRemoteEventLogger;
END_VAR

fbFB_RequestEventText(
    sResult := arg_sResult,
    nResult := arg_nResult,
    eventClass := arg_eventClass,
    nEventId := arg_nEventId,
    nLangId := arg_nLangId,
    ipArgs := arg_ipArgs,
    ipRemoteLogger := arg_ipRemoteLogger
);
```

## 7. 相关

- 见 [`Tc3_EventLogger README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
