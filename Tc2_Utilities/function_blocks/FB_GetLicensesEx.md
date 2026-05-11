# FB_GetLicensesEx
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
| Example | [`examples/P_Demo_FB_GetLicensesEx.xml`](../examples/P_Demo_FB_GetLicensesEx.xml) |

---
## 1. 功能简述

The function block FB_GetLicensesEx determines the status of all TwinCAT 3 licenses and OEM licenses.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    tTimeout : TIME;
    sNetId : T_AmsNetId;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |
| `sNetId` | `T_AmsNetId` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
    nValidLicenses : UDINT;
    aValidLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nPendingLicenses : UDINT;
    aPendingLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nDemoLicenses : UDINT;
    aDemoLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nOemLicenses : UDINT;
    aOemLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nFailedLicenses : UDINT;
    aFailedLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    nInvalidLicenses : UDINT;
    aInvalidLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrorId` | `UDINT` | （详见 PDF） |
| `nValidLicenses` | `UDINT` | （详见 PDF） |
| `aValidLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | （详见 PDF） |
| `nPendingLicenses` | `UDINT` | （详见 PDF） |
| `aPendingLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | （详见 PDF） |
| `nDemoLicenses` | `UDINT` | （详见 PDF） |
| `aDemoLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | （详见 PDF） |
| `nOemLicenses` | `UDINT` | （详见 PDF） |
| `aOemLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | （详见 PDF） |
| `nFailedLicenses` | `UDINT` | （详见 PDF） |
| `aFailedLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | （详见 PDF） |
| `nInvalidLicenses` | `UDINT` | （详见 PDF） |
| `aInvalidLicenses` | `ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.32 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.32 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetLicensesEx.xml`](../examples/P_Demo_FB_GetLicensesEx.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_GetLicensesEx
VAR
    fbFB_GetLicensesEx : FB_GetLicensesEx;
    arg_bExecute : BOOL;
    arg_tTimeout : TIME;
    arg_sNetId : T_AmsNetId;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrorId : UDINT;
    out_nValidLicenses : UDINT;
    out_aValidLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    out_nPendingLicenses : UDINT;
    out_aPendingLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    out_nDemoLicenses : UDINT;
    out_aDemoLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    out_nOemLicenses : UDINT;
    out_aOemLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    out_nFailedLicenses : UDINT;
    out_aFailedLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
    out_nInvalidLicenses : UDINT;
    out_aInvalidLicenses : ARRAY[1..nMaxLicenses} OF ST_TcOnlineLicenseInfoDataEx;
END_VAR

fbFB_GetLicensesEx(
    bExecute := arg_bExecute,
    tTimeout := arg_tTimeout,
    sNetId := arg_sNetId,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrorId => out_nErrorId,
    nValidLicenses => out_nValidLicenses,
    aValidLicenses => out_aValidLicenses,
    nPendingLicenses => out_nPendingLicenses,
    aPendingLicenses => out_aPendingLicenses,
    nDemoLicenses => out_nDemoLicenses,
    aDemoLicenses => out_aDemoLicenses,
    nOemLicenses => out_nOemLicenses,
    aOemLicenses => out_aOemLicenses,
    nFailedLicenses => out_nFailedLicenses,
    aFailedLicenses => out_aFailedLicenses,
    nInvalidLicenses => out_nInvalidLicenses,
    aInvalidLicenses => out_aInvalidLicenses
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
