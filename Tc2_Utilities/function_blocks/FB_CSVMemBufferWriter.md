# FB_CSVMemBufferWriter
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
| Example | [`examples/P_Demo_FB_CSVMemBufferWriter.xml`](../examples/P_Demo_FB_CSVMemBufferWriter.xml) |

---
## 1. 功能简述

This function block can be used to generate data sets in an external buffer in CSV format from individual data fields. The content of the buffer can then be written into a file, e.g. with the aid of the function blocks for file access. The new data field can be transferred to the function block either via the putValue variable (string) or via the optional pValue  and cbValue  variables. This depends on whether you want to write data fields without control characters (string) or data fields with control characters or binary data to the data set. The function block can generate several data sets in the buffer until the maximum available buffer size is reached. The end of the data set (last data field in the current data set) is automatically appended to the data field if the bCRLF variable was set to TRUE during writing of the data field. The function block automatically adds the data field separators. The default data field separator is a semicolon. The separator can be configured from semicolon to comma via the global PLC variable DEFAULT_CSV_FIELD_SEP .

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eCmd : E_EnumCmdType;
    putValue : T_MaxString;
    pValue : POINTER TO BYTE;
    cbValue : UDINT;
    bCRLF : BOOL;
    pBuffer : POINTER TO BYTE;
    cbBuffer : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eCmd` | `E_EnumCmdType` | （详见 PDF） |
| `putValue` | `T_MaxString` | （详见 PDF） |
| `pValue` | `POINTER TO BYTE` | （详见 PDF） |
| `cbValue` | `UDINT` | （详见 PDF） |
| `bCRLF` | `BOOL` | （详见 PDF） |
| `pBuffer` | `POINTER TO BYTE` | （详见 PDF） |
| `cbBuffer` | `UDINT` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    cbSize : UDINT;
    cbFree : UDINT;
    nFields : UDINT;
    nRecords : UDINT;
    cbWrite : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOk` | `BOOL` | （详见 PDF） |
| `cbSize` | `UDINT` | （详见 PDF） |
| `cbFree` | `UDINT` | （详见 PDF） |
| `nFields` | `UDINT` | （详见 PDF） |
| `nRecords` | `UDINT` | （详见 PDF） |
| `cbWrite` | `UDINT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.14 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.14 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CSVMemBufferWriter.xml`](../examples/P_Demo_FB_CSVMemBufferWriter.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CSVMemBufferWriter
VAR
    fbFB_CSVMemBufferWriter : FB_CSVMemBufferWriter;
    arg_eCmd : E_EnumCmdType;
    arg_putValue : T_MaxString;
    arg_pValue : POINTER TO BYTE;
    arg_cbValue : UDINT;
    arg_bCRLF : BOOL;
    arg_pBuffer : POINTER TO BYTE;
    arg_cbBuffer : UDINT;
    out_bOk : BOOL;
    out_cbSize : UDINT;
    out_cbFree : UDINT;
    out_nFields : UDINT;
    out_nRecords : UDINT;
    out_cbWrite : UDINT;
END_VAR

fbFB_CSVMemBufferWriter(
    eCmd := arg_eCmd,
    putValue := arg_putValue,
    pValue := arg_pValue,
    cbValue := arg_cbValue,
    bCRLF := arg_bCRLF,
    pBuffer := arg_pBuffer,
    cbBuffer := arg_cbBuffer,
    bOk => out_bOk,
    cbSize => out_cbSize,
    cbFree => out_cbFree,
    nFields => out_nFields,
    nRecords => out_nRecords,
    cbWrite => out_cbWrite
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
