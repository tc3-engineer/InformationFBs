# SendMessage2
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
| Example | [`examples/P_Demo_SendMessage2.xml`](../examples/P_Demo_SendMessage2.xml) |

---
## 1. 功能简述

This method sends a message. Syntax METHOD SendMessage2 : HRESULT

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eventClass : GUID;
    nEventId : UDINT;
    eSeverity : TcEventSeverity;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eventClass` | `GUID` | （详见 PDF） |
| `nEventId` | `UDINT` | （详见 PDF） |
| `eSeverity` | `TcEventSeverity` | （详见 PDF） |
| `ipSourceInfo` | `I_TcSourceInfo` | （详见 PDF） |
| `nTimeStamp` | `ULINT` | （详见 PDF） |
| `ipArguments` | `I_TcArguments` | （详见 PDF） |

### VAR_OUTPUT

无 VAR_OUTPUT。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sJsonAttribute : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJsonAttribute` | `STRING` | （详见 PDF） |

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.10.12 节。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（`S_OK` = 成功；其他错误码请见对应 InfoSys 页面，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.10.12 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendMessage2.xml`](../examples/P_Demo_SendMessage2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_SendMessage2
VAR
    fbSendMessage2 : SendMessage2;
    arg_eventClass : GUID;
    arg_nEventId : UDINT;
    arg_eSeverity : TcEventSeverity;
    arg_ipSourceInfo : I_TcSourceInfo;
    arg_nTimeStamp : ULINT;
    arg_ipArguments : I_TcArguments;
    io_sJsonAttribute : STRING;
END_VAR

fbSendMessage2(
    eventClass := arg_eventClass,
    nEventId := arg_nEventId,
    eSeverity := arg_eSeverity,
    ipSourceInfo := arg_ipSourceInfo,
    nTimeStamp := arg_nTimeStamp,
    ipArguments := arg_ipArguments,
    sJsonAttribute := io_sJsonAttribute
);
```

## 7. 相关

- 见 [`Tc3_EventLogger README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
