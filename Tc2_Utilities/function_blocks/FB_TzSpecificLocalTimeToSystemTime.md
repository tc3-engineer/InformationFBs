# FB_TzSpecificLocalTimeToSystemTime
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TzSpecificLocalTimeToSystemTime.xml`](../examples/P_Demo_FB_TzSpecificLocalTimeToSystemTime.xml) |

---
## 1. 功能简述

The function block converts the local time (structured system time format) to UTC time (structured system time format), taking into account the specified time zone information. The function block FB_TzSpecificLocalTimeToFileTime64 [ }   123 ]  has similar functionality but uses a different time format (file time format). The function block is only suitable for conversion of continuous  local timestamp information. Step changes in local time caused by daylight saving time/standard time changeover are permitted and are correctly detected by the function block. Arbitrary changes in local time result in incorrect conversion. The reason: the last converted time is stored internally in the function block in order to be able to identify the daylight saving time/standard time information and the B times (see below) when the local time is reset. The function block is associated with an action: A_Reset(). If this action is called the function block outputs and the locally stored (last converted) time are reset to zero. The step changes in the local time are problematic, since they have to be converted to a linear UTC time. It is therefore advisable to use the (continuous) UTC time for time s

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : TIMESTRUCT;
    tzInfo : ST_TimeZoneInformation;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `TIMESTRUCT` | （详见 PDF） |
| `tzInfo` | `ST_TimeZoneInformation` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    out : TIMESTRUCT;
    eTzID : E_TimeZoneID;
    bB : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `out` | `TIMESTRUCT` | （详见 PDF） |
| `eTzID` | `E_TimeZoneID` | （详见 PDF） |
| `bB` | `BOOL` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.61 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.61 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TzSpecificLocalTimeToSystemTime.xml`](../examples/P_Demo_FB_TzSpecificLocalTimeToSystemTime.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_TzSpecificLocalTimeToSystemTime
VAR
    fbFB_TzSpecificLocalTimeToSystemTime : FB_TzSpecificLocalTimeToSystemTime;
    arg_in : TIMESTRUCT;
    arg_tzInfo : ST_TimeZoneInformation;
    out_out : TIMESTRUCT;
    out_eTzID : E_TimeZoneID;
    out_bB : BOOL;
END_VAR

fbFB_TzSpecificLocalTimeToSystemTime(
    in := arg_in,
    tzInfo := arg_tzInfo,
    out => out_out,
    eTzID => out_eTzID,
    bB => out_bB
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
