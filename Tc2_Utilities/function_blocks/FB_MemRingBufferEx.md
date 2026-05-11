# FB_MemRingBufferEx
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
| Example | [`examples/P_Demo_FB_MemRingBufferEx.xml`](../examples/P_Demo_FB_MemRingBufferEx.xml) |

---
## 1. 功能简述

The function block FB_MemRingBufferEx can be used to write data sets with different lengths in a ring buffer or to read previously written data sets from the ring buffer. The written data sets are read out according to the FIFO principle in the same order in which they were previously written to the ring buffer. This means that the oldest entries are the first ones that are read. The buffer memory is made available to the function block via the pBuffer / cbBuffer  input variables. Writing/reading of data sets is controlled via action calls. The functionality of this function block is similar to that of the FB_MemRingBuffer [ }   103 ]  function block. During reading of data sets the FB_MemRingBuffer copies the data into an external buffer variable. FB_MemRingBufferEx only provides a reference for the data set (address pointer/length). The application must then copy the data itself for further processing. The function block features the following tasks: • A_AddTail  (writes a new data set into the ring buffer.) • A_GetHead  (returns a reference: address pointer/length of the oldest data set in the ring buffer, but does not remove it.) • A_FreeHead  (reads and removes the oldest data

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pWrite : POINTER TO BYTE;
    cbWrite : UDINT;
    pBuffer : POINTER TO BYTE;
    cbBuffer : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pWrite` | `POINTER TO BYTE` | （详见 PDF） |
| `cbWrite` | `UDINT` | （详见 PDF） |
| `pBuffer` | `POINTER TO BYTE` | （详见 PDF） |
| `cbBuffer` | `UDINT` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    pRead : POINTER TO BYTE;
    cbRead : UDINT;
    nCount : UDINT;
    cbSize : UDINT;
    cbFree : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOk` | `BOOL` | （详见 PDF） |
| `pRead` | `POINTER TO BYTE` | （详见 PDF） |
| `cbRead` | `UDINT` | （详见 PDF） |
| `nCount` | `UDINT` | （详见 PDF） |
| `cbSize` | `UDINT` | （详见 PDF） |
| `cbFree` | `UDINT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.51 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.51 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_MemRingBufferEx.xml`](../examples/P_Demo_FB_MemRingBufferEx.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_MemRingBufferEx
VAR
    fbFB_MemRingBufferEx : FB_MemRingBufferEx;
    arg_pWrite : POINTER TO BYTE;
    arg_cbWrite : UDINT;
    arg_pBuffer : POINTER TO BYTE;
    arg_cbBuffer : UDINT;
    out_bOk : BOOL;
    out_pRead : POINTER TO BYTE;
    out_cbRead : UDINT;
    out_nCount : UDINT;
    out_cbSize : UDINT;
    out_cbFree : UDINT;
END_VAR

fbFB_MemRingBufferEx(
    pWrite := arg_pWrite,
    cbWrite := arg_cbWrite,
    pBuffer := arg_pBuffer,
    cbBuffer := arg_cbBuffer,
    bOk => out_bOk,
    pRead => out_pRead,
    cbRead => out_cbRead,
    nCount => out_nCount,
    cbSize => out_cbSize,
    cbFree => out_cbFree
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
