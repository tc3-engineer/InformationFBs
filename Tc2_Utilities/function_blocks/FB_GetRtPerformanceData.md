# FB_GetRtPerformanceData
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
| Example | [`examples/P_Demo_FB_GetRtPerformanceData.xml`](../examples/P_Demo_FB_GetRtPerformanceData.xml) |

---
## 1. 功能简述

The function block FB_GetRtPerformanceData can be used to determine the current RealTime Performance data of a TwinCAT system.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    bReset : BOOL;
    tTimeout : TIME;
    sNetId : T_AmsNetId;
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
    nUsedCpuCount : UDINT;
    stRtPerformanceData : ARRAY [1..nMaxCpuCount] OF ST_RtPerformanceData;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | （详见 PDF） |
| `bReset` | `BOOL` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |
| `sNetId` | `T_AmsNetId` | （详见 PDF） |
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrorId` | `UDINT` | （详见 PDF） |
| `nUsedCpuCount` | `UDINT` | （详见 PDF） |
| `stRtPerformanceData` | `ARRAY [1..nMaxCpuCount] OF ST_RtPerformanceData` | （详见 PDF） |

### VAR_OUTPUT

无 VAR_OUTPUT。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.63 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.63 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetRtPerformanceData.xml`](../examples/P_Demo_FB_GetRtPerformanceData.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_GetRtPerformanceData
VAR
    fbFB_GetRtPerformanceData : FB_GetRtPerformanceData;
    arg_bExecute : BOOL;
    arg_bReset : BOOL;
    arg_tTimeout : TIME;
    arg_sNetId : T_AmsNetId;
    arg_bBusy : BOOL;
    arg_bError : BOOL;
    arg_nErrorId : UDINT;
    arg_nUsedCpuCount : UDINT;
    arg_stRtPerformanceData : ARRAY [1..nMaxCpuCount] OF ST_RtPerformanceData;
END_VAR

fbFB_GetRtPerformanceData(
    bExecute := arg_bExecute,
    bReset := arg_bReset,
    tTimeout := arg_tTimeout,
    sNetId := arg_sNetId,
    bBusy := arg_bBusy,
    bError := arg_bError,
    nErrorId := arg_nErrorId,
    nUsedCpuCount := arg_nUsedCpuCount,
    stRtPerformanceData := arg_stRtPerformanceData
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
