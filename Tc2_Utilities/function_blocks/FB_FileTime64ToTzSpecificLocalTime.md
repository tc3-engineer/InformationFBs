# FB_FileTime64ToTzSpecificLocalTime
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
| Example | [`examples/P_Demo_FB_FileTime64ToTzSpecificLocalTime.xml`](../examples/P_Demo_FB_FileTime64ToTzSpecificLocalTime.xml) |

---
## 1. 功能简述

The function block converts the UTC time (file time format) to local time (file time format), taking into account the specified time zone information. The function block: FB_SystemTimeToTzSpecificLocalTime [ }   121 ]  has a similar functionality but uses a different time format (structured system time format). The function block is only suitable for conversion of continuous  UTC timestamp information. The function block uses the time zone information to calculate the required time steps (daylight saving time/standard time changeover) in local time. Time steps in UTC input time are not permitted and lead to incorrect conversion. The reason: the function block stores the last converted time internally, so that it can detect the B times (see below) from the UTC input time and the stored value when the local time is changed. The function block is associated with an action: A_Reset(). If this action is called the function block outputs and the locally stored (last converted) time are reset to zero. 1. Graphic representation of the temporal behavior during the changeover from daylight saving time to standard time (tzInfo = WEST_EUROPE_TZI): The UTC input time (green) is continuous. The 

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : T_FILETIME64;
    tzInfo : ST_TimeZoneInformation;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_FILETIME64` | （详见 PDF） |
| `tzInfo` | `ST_TimeZoneInformation` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    out : T_FILETIME64;
    eTzID : E_TimeZoneID;
    bB : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `out` | `T_FILETIME64` | （详见 PDF） |
| `eTzID` | `E_TimeZoneID` | （详见 PDF） |
| `bB` | `BOOL` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.21 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.21 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileTime64ToTzSpecificLocalTime.xml`](../examples/P_Demo_FB_FileTime64ToTzSpecificLocalTime.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_FileTime64ToTzSpecificLocalTime
VAR
    fbFB_FileTime64ToTzSpecificLocalTime : FB_FileTime64ToTzSpecificLocalTime;
    arg_in : T_FILETIME64;
    arg_tzInfo : ST_TimeZoneInformation;
    out_out : T_FILETIME64;
    out_eTzID : E_TimeZoneID;
    out_bB : BOOL;
END_VAR

fbFB_FileTime64ToTzSpecificLocalTime(
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
