# FB_CheckOemLicense
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
| Example | [`examples/P_Demo_FB_CheckOemLicense.xml`](../examples/P_Demo_FB_CheckOemLicense.xml) |

---
## 1. 功能简述

If you use OEM licenses make sure you encrypt your boot project! Remember that the license ID queried via FB_CheckOemLicense in the binary code can easily be found and (with a little effort) manipulated with a hex editor. Therefore, be sure to encrypt your boot project (safest), or at least disguise the queried license ID in the source code as best as possible. The function block FB_CheckOemLicense determines the TwinCAT 3 license status for a given license ID and a given OEM ID.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    tTimeout : TIME;
    sNetId : T_AmsNetId;
    stOemId : GUID;
    stLicenseId : GUID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |
| `sNetId` | `T_AmsNetId` | （详见 PDF） |
| `stOemId` | `GUID` | （详见 PDF） |
| `stLicenseId` | `GUID` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    stCheckLicense : ST_CheckLicense;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrId` | `UDINT` | （详见 PDF） |
| `stCheckLicense` | `ST_CheckLicense` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.12 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.12 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CheckOemLicense.xml`](../examples/P_Demo_FB_CheckOemLicense.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CheckOemLicense
VAR
    fbFB_CheckOemLicense : FB_CheckOemLicense;
    arg_bExecute : BOOL;
    arg_tTimeout : TIME;
    arg_sNetId : T_AmsNetId;
    arg_stOemId : GUID;
    arg_stLicenseId : GUID;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrId : UDINT;
    out_stCheckLicense : ST_CheckLicense;
END_VAR

fbFB_CheckOemLicense(
    bExecute := arg_bExecute,
    tTimeout := arg_tTimeout,
    sNetId := arg_sNetId,
    stOemId := arg_stOemId,
    stLicenseId := arg_stLicenseId,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrId => out_nErrId,
    stCheckLicense => out_stCheckLicense
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
