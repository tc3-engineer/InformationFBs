# FB_TcEventLogger
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
| Example | [`examples/P_Demo_FB_TcEventLogger.xml`](../examples/P_Demo_FB_TcEventLogger.xml) |

---
## 1. 功能简述

This function block represents the TwinCAT 3 EventLogger itself. Syntax Definition: FUNCTION_BLOCK FB_TcEventLogger

## 2. 接口定义

### VAR_INPUT

无 VAR_INPUT。

### VAR_OUTPUT

无 VAR_OUTPUT。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.10 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.10 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcEventLogger.xml`](../examples/P_Demo_FB_TcEventLogger.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_TcEventLogger
VAR
    fbFB_TcEventLogger : FB_TcEventLogger;
END_VAR

fbFB_TcEventLogger(

);
```

## 7. 相关

- 见 [`Tc3_EventLogger README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
