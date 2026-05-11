# FB_RequestEventClassDetails
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
| Example | [`examples/P_Demo_FB_RequestEventClassDetails.xml`](../examples/P_Demo_FB_RequestEventClassDetails.xml) |

---
## 1. 功能简述

This function block can be used to query the details of an event class in the form of FB_TcDetail [ }   31 ] . Each "detail" (DescriptionText, DescriptionUrl, Comment) – see when creating the event) has an index and the key ((DescriptionText, DescriptionUrl, Comment) and the value are supplied for each index.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nIndex : UDINT;
    fbDetail : REFERENCE TO FB_TcDetail;
    eventClass : GUID;
    nLangId : DINT;
    ipRemoteLogger : I_TcRemoteEventLogger;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nIndex` | `UDINT` | （详见 PDF） |
| `fbDetail` | `REFERENCE TO FB_TcDetail` | （详见 PDF） |
| `eventClass` | `GUID` | （详见 PDF） |
| `nLangId` | `DINT` | （详见 PDF） |
| `ipRemoteLogger` | `I_TcRemoteEventLogger` | （详见 PDF） |

### VAR_OUTPUT

无 VAR_OUTPUT。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.1.3 节。

## 4. 错误码 / 返回值

本 FB 自身无返回值；运行状态/错误反馈通过其方法返回的 `HRESULT` 或对应输出参数获取，具体见 PDF / InfoSys（⚠️ 待人工确认）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.1.3 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RequestEventClassDetails.xml`](../examples/P_Demo_FB_RequestEventClassDetails.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_RequestEventClassDetails
VAR
    fbFB_RequestEventClassDetails : FB_RequestEventClassDetails;
    arg_nIndex : UDINT;
    arg_fbDetail : REFERENCE TO FB_TcDetail;
    arg_eventClass : GUID;
    arg_nLangId : DINT;
    arg_ipRemoteLogger : I_TcRemoteEventLogger;
END_VAR

fbFB_RequestEventClassDetails(
    nIndex := arg_nIndex,
    fbDetail := arg_fbDetail,
    eventClass := arg_eventClass,
    nLangId := arg_nLangId,
    ipRemoteLogger := arg_ipRemoteLogger
);
```

## 7. 相关

- 见 [`Tc3_EventLogger README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
