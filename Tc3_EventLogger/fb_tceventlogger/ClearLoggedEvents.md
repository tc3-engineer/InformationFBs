# ClearLoggedEvents
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
| Example | [`examples/P_Demo_ClearLoggedEvents.xml`](../examples/P_Demo_ClearLoggedEvents.xml) |

---
## 1. 功能简述

Async method for clearing logged events. Returns TRUE if the asynchronous request is no longer assigned. Syntax METHOD ClearLoggedEvents : BOOL

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipClearSettings : I_TcClearLoggedEventsSettings;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipClearSettings` | `I_TcClearLoggedEventsSettings` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError : BOOL;
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | （详见 PDF） |
| `hrErrorCode` | `HRESULT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.10.3 节。

## 4. 错误码 / 返回值

本方法返回 `BOOL`（`TRUE` = 成功；`FALSE` = 失败。具体失败语义 PDF 未列出，请见 InfoSys，⚠️ 待人工确认）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.10.3 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ClearLoggedEvents.xml`](../examples/P_Demo_ClearLoggedEvents.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_ClearLoggedEvents
VAR
    fbClearLoggedEvents : ClearLoggedEvents;
    arg_ipClearSettings : I_TcClearLoggedEventsSettings;
    out_bError : BOOL;
    out_hrErrorCode : HRESULT;
END_VAR

fbClearLoggedEvents(
    ipClearSettings := arg_ipClearSettings,
    bError => out_bError,
    hrErrorCode => out_hrErrorCode
);
```

## 7. 相关

- 见 [`Tc3_EventLogger README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
