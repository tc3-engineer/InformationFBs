# FB_LicFileRead
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
| Example | [`examples/P_Demo_FB_LicFileRead.xml`](../examples/P_Demo_FB_LicFileRead.xml) |

---
## 1. 功能简述

The function block reads a file from the license dongle into a provided buffer (pDestBuff and cbReadLen) via a rising edge at bExecute. The buffer must be large enough for the file, otherwise only the first part of the file is read.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    nPort : UINT;
    sFileName : STRING;
    pDestBuff : PVOID;
    cbReadLen : UDINT;
    bExecute : BOOL;
    dwPassCode : DWORD;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetId` | `T_AmsNetId` | （详见 PDF） |
| `nPort` | `UINT` | （详见 PDF） |
| `sFileName` | `STRING` | （详见 PDF） |
| `pDestBuff` | `PVOID` | （详见 PDF） |
| `cbReadLen` | `UDINT` | （详见 PDF） |
| `bExecute` | `BOOL` | （详见 PDF） |
| `dwPassCode` | `DWORD` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
    cbBytesread : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrorId` | `UDINT` | （详见 PDF） |
| `cbBytesread` | `UDINT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.45 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.45 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_LicFileRead.xml`](../examples/P_Demo_FB_LicFileRead.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_LicFileRead
VAR
    fbFB_LicFileRead : FB_LicFileRead;
    arg_sNetId : T_AmsNetId;
    arg_nPort : UINT;
    arg_sFileName : STRING;
    arg_pDestBuff : PVOID;
    arg_cbReadLen : UDINT;
    arg_bExecute : BOOL;
    arg_dwPassCode : DWORD;
    arg_tTimeout : TIME;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrorId : UDINT;
    out_cbBytesread : UDINT;
END_VAR

fbFB_LicFileRead(
    sNetId := arg_sNetId,
    nPort := arg_nPort,
    sFileName := arg_sFileName,
    pDestBuff := arg_pDestBuff,
    cbReadLen := arg_cbReadLen,
    bExecute := arg_bExecute,
    dwPassCode := arg_dwPassCode,
    tTimeout := arg_tTimeout,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrorId => out_nErrorId,
    cbBytesread => out_cbBytesread
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
