# FB_LocalSystemTime
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
| Example | [`examples/P_Demo_FB_LocalSystemTime.xml`](../examples/P_Demo_FB_LocalSystemTime.xml) |

---
## 1. 功能简述

In some applications the local Windows system time is synchronized via the SNTP time server or a radio clock. In many cases the local Windows system time has to be used in the PLC (e.g. in the form of timestamp log messages to the HMI). The local Windows system time is displayed in the taskbar. For such applications the FB_LocalSystemTime function block can be useful. This function block internally combines the function of the following function blocks: RTC_EX2 [ }   151 ] , NT_GetTime [ }   131 ] , FB_GetTimeZoneInformation [ }   84 ]  and NT_SetTimeToRTCTime [ }   135 ] . The RTC_EX2 function block can be used for generating timestamps for log outputs, for example. However, this function block has the disadvantage that its time is not synchronized with the local Windows system time and has to be resynchronized cyclically via the NT_GetTime function block (see RTC function block examples in the documentation). Cyclic synchronization of the internal time ( systemTime  output) is already implemented in the function block. The cycle time can be configured via the dwCycle  input. The function block also provides time zone information (summer time/winter time). The FB_LocalSystemTime f

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID := '';
    bEnable : BOOL;
    dwCycle : DWORD(1..86400) := 5;
    dwOpt : DWORD := 1;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetID` | `T_AmsNetID` | （详见 PDF） |
| `bEnable` | `BOOL` | （详见 PDF） |
| `dwCycle` | `DWORD(1..86400)` | （详见 PDF） |
| `dwOpt` | `DWORD` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bValid : BOOL;
    systemTime : TIMESTRUCT;
    tzID : E_TimeZoneID := eTimeZoneID_Invalid;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bValid` | `BOOL` | （详见 PDF） |
| `systemTime` | `TIMESTRUCT` | （详见 PDF） |
| `tzID` | `E_TimeZoneID` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.47 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.47 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_LocalSystemTime.xml`](../examples/P_Demo_FB_LocalSystemTime.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_LocalSystemTime
VAR
    fbFB_LocalSystemTime : FB_LocalSystemTime;
    arg_sNetID : T_AmsNetID;
    arg_bEnable : BOOL;
    arg_dwCycle : DWORD(1..86400);
    arg_dwOpt : DWORD;
    arg_tTimeout : TIME;
    out_bValid : BOOL;
    out_systemTime : TIMESTRUCT;
    out_tzID : E_TimeZoneID;
END_VAR

fbFB_LocalSystemTime(
    sNetID := arg_sNetID,
    bEnable := arg_bEnable,
    dwCycle := arg_dwCycle,
    dwOpt := arg_dwOpt,
    tTimeout := arg_tTimeout,
    bValid => out_bValid,
    systemTime => out_systemTime,
    tzID => out_tzID
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
