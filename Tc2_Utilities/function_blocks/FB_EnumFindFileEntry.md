# FB_EnumFindFileEntry
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
| Example | [`examples/P_Demo_FB_EnumFindFileEntry.xml`](../examples/P_Demo_FB_EnumFindFileEntry.xml) |

---
## 1. 功能简述

This function block searches a directory for a file or a subdirectory whose name is similar to the specified name. Any entries found can be read individually. See also description of the FB_EnumFindFileList function block. The input parameter eCmd  is used for navigating through the list of entries. The eCmd  input determines whether the first or the next input is read, for example. Important notes: A new search may be started only if the previous search has been fully completed. The function block instance may need to be activated several times (by a rising edge at the bExecute input) for a complete search. The search is only fully complete if bEOE =TRUE was reached or if the search was terminated prematurely with ECMD = eEnumCmd_Abort. For the TwinCAT system, the search may not yet be completed if the PLC application has already found the file or directory that was sought. If not all entries are to be read (i.e. bEOE=TRUE  is not reached), the function block subsequently has to be called with the input parameter eCmd = eEnumCmd_Abort . This is necessary in order to complete the search and release all internal resources (file handles). If bEOE=TRUE  was reached or if an error occu

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID;
    sPathName : T_MaxString;
    eCmd : E_EnumCmdType := eEnumCmd_First;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetID` | `T_AmsNetID` | （详见 PDF） |
| `sPathName` | `T_MaxString` | （详见 PDF） |
| `eCmd` | `E_EnumCmdType` | （详见 PDF） |
| `bExecute` | `BOOL` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    bEOE : BOOL;
    stFindFile : ST_FindFileEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrId` | `UDINT` | （详见 PDF） |
| `bEOE` | `BOOL` | （详见 PDF） |
| `stFindFile` | `ST_FindFileEntry` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.15 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.15 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnumFindFileEntry.xml`](../examples/P_Demo_FB_EnumFindFileEntry.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_EnumFindFileEntry
VAR
    fbFB_EnumFindFileEntry : FB_EnumFindFileEntry;
    arg_sNetID : T_AmsNetID;
    arg_sPathName : T_MaxString;
    arg_eCmd : E_EnumCmdType;
    arg_bExecute : BOOL;
    arg_tTimeout : TIME;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrId : UDINT;
    out_bEOE : BOOL;
    out_stFindFile : ST_FindFileEntry;
END_VAR

fbFB_EnumFindFileEntry(
    sNetID := arg_sNetID,
    sPathName := arg_sPathName,
    eCmd := arg_eCmd,
    bExecute := arg_bExecute,
    tTimeout := arg_tTimeout,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrId => out_nErrId,
    bEOE => out_bEOE,
    stFindFile => out_stFindFile
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
