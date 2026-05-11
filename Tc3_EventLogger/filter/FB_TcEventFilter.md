# FB_TcEventFilter
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
| Example | [`examples/P_Demo_FB_TcEventFilter.xml`](../examples/P_Demo_FB_TcEventFilter.xml) |

---
## 1. 功能简述

Provides the functionality to specify an event filter. The filters are provided via a floating interface following a structured query language. It describes which messages should apply. • Conditions can be linked via .AND_OP()  and .OR_OP() . • Conditions can be negated by .NOT_OP() . • Conditions can be defined by properties such as . isAlarm() or .EventClass.EqualsTo(<EventClass>) , for example. A complete list of properties can be found in the API documentation. • A grouping can be formulated via .FilterExpression(<SubCondition>) . The <SubCodition> is itself another FB_TcEventFilter  or ITcEventFilter . A filter is applied once it has been compiled. To receive messages, for example, it is assigned to a recipient via FB_ListenerBase2.subscribe() . In this way FB_ListenerBase2  takes over the filter and provides a corresponding return value, which is described here. The filter can be amended by repeating FB_ListenerBase2.subscribe() . A maximum of 255 filter conditions can be set - after which an ADS_NOMOREHDL is returned as an error message.

## 2. 接口定义

### VAR_INPUT

无 VAR_INPUT。

### VAR_OUTPUT

无 VAR_OUTPUT。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.3.3 节。

## 4. 错误码 / 返回值

本方法/FB 返回 `HRESULT`（`S_OK` = 成功；其他码表请见对应 InfoSys 页面，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.3.3 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcEventFilter.xml`](../examples/P_Demo_FB_TcEventFilter.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_TcEventFilter
VAR
    fbFB_TcEventFilter : FB_TcEventFilter;
END_VAR

fbFB_TcEventFilter(

);
```

## 7. 相关

- 见 [`Tc3_EventLogger README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
