# FB_FileRingBuffer
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
| Example | [`examples/P_Demo_FB_FileRingBuffer.xml`](../examples/P_Demo_FB_FileRingBuffer.xml) |

---
## 1. 功能简述

The function block FB_FileRingBuffer allows data sets of varying lengths to be written into a ring buffer file, or for data sets that have previously been written there to be removed from the ring buffer file. The written data sets are read out according to the FIFO principle in the same order in which they were previously written to the ring buffer file. This means that the oldest entries are the first ones that are read. Opening, closing, writing and reading the data sets is controlled by action calls. The function block features the following tasks: • A_Open  (Opens an existing ring buffer file for appending or generating new data sets. No error is returned if the file is already open. ) • A_Close  (Closes an open ring buffer file. No error is returned if the file is already closed. ) • A_Create  (Opens a new ring buffer file. If the file already exists, it is overwritten. No error is returned if the file is already open) • A_AddTail  (Writes a new data set into the ring buffer file. ) • A_GetHead  (Reads the oldest data set from the ring buffer file, but does not remove it – the file pointer is not moved to the next data set. ) • A_RemoveHead  (Reads and removes the oldest data

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    sPathName : T_MaxString;
    ePath : E_OpenPath;
    nID : UDINT;
    cbBuffer : UDINT;
    bOverwrite : BOOL;
    pWriteBuff : POINTER TO BYTE;
    cbWriteLen : UDINT;
    pReadBuff : POINTER TO BYTE;
    cbReadLen : UDINT;
    tTimeout : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetId` | `T_AmsNetId` | （详见 PDF） |
| `sPathName` | `T_MaxString` | （详见 PDF） |
| `ePath` | `E_OpenPath` | （详见 PDF） |
| `nID` | `UDINT` | （详见 PDF） |
| `cbBuffer` | `UDINT` | （详见 PDF） |
| `bOverwrite` | `BOOL` | （详见 PDF） |
| `pWriteBuff` | `POINTER TO BYTE` | （详见 PDF） |
| `cbWriteLen` | `UDINT` | （详见 PDF） |
| `pReadBuff` | `POINTER TO BYTE` | （详见 PDF） |
| `cbReadLen` | `UDINT` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbReturn : UDINT;
    stHeader : ST_FileRBufferHead;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrId` | `UDINT` | （详见 PDF） |
| `cbReturn` | `UDINT` | （详见 PDF） |
| `stHeader` | `ST_FileRBufferHead` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.20 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.20 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileRingBuffer.xml`](../examples/P_Demo_FB_FileRingBuffer.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_FileRingBuffer
VAR
    fbFB_FileRingBuffer : FB_FileRingBuffer;
    arg_sNetId : T_AmsNetId;
    arg_sPathName : T_MaxString;
    arg_ePath : E_OpenPath;
    arg_nID : UDINT;
    arg_cbBuffer : UDINT;
    arg_bOverwrite : BOOL;
    arg_pWriteBuff : POINTER TO BYTE;
    arg_cbWriteLen : UDINT;
    arg_pReadBuff : POINTER TO BYTE;
    arg_cbReadLen : UDINT;
    arg_tTimeout : TIME;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrId : UDINT;
    out_cbReturn : UDINT;
    out_stHeader : ST_FileRBufferHead;
END_VAR

fbFB_FileRingBuffer(
    sNetId := arg_sNetId,
    sPathName := arg_sPathName,
    ePath := arg_ePath,
    nID := arg_nID,
    cbBuffer := arg_cbBuffer,
    bOverwrite := arg_bOverwrite,
    pWriteBuff := arg_pWriteBuff,
    cbWriteLen := arg_cbWriteLen,
    pReadBuff := arg_pReadBuff,
    cbReadLen := arg_cbReadLen,
    tTimeout := arg_tTimeout,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrId => out_nErrId,
    cbReturn => out_cbReturn,
    stHeader => out_stHeader
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
