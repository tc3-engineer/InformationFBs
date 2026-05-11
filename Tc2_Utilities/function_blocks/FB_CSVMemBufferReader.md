# FB_CSVMemBufferReader
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
| Example | [`examples/P_Demo_FB_CSVMemBufferReader.xml`](../examples/P_Demo_FB_CSVMemBufferReader.xml) |

---
## 1. 功能简述

This function block can be used to decompose/interpret data sets stored in an external buffer into individual data fields. The buffer data could first be read from a file with the aid of the function blocks for file access, for example. The function block reads the first or the next data field and returns its value either as a string at the getValue  output or as an address/byte value at the pValue / cbValue  output. The data in the buffer must have a certain format to ensure that the function block can interpret them correctly. The CRLF data set separator (CR = Carriage Return, LF= Line Feed) is used to separate the data sets. The last data set must end with a CRLF. Individual data fields must be separated with the data field separator. The default data field separator is a semicolon. The separator can be configured from semicolon to comma via the global PLC variable DEFAULT_CSV_FIELD_SEP .

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eCmd : E_EnumCmdType := eEnumCmd_First;
    pBuffer : POINTER TO BYTE;
    cbBuffer : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eCmd` | `E_EnumCmdType` | （详见 PDF） |
| `pBuffer` | `POINTER TO BYTE` | （详见 PDF） |
| `cbBuffer` | `UDINT` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    getValue : T_MaxString := '';
    pValue : POINTER TO BYTE := 0;
    cbValue : UDINT := 0;
    bCRLF : BOOL := FALSE;
    cbRead : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOk` | `BOOL` | （详见 PDF） |
| `getValue` | `T_MaxString` | （详见 PDF） |
| `pValue` | `POINTER TO BYTE` | （详见 PDF） |
| `cbValue` | `UDINT` | （详见 PDF） |
| `bCRLF` | `BOOL` | （详见 PDF） |
| `cbRead` | `UDINT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.13 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.13 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CSVMemBufferReader.xml`](../examples/P_Demo_FB_CSVMemBufferReader.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CSVMemBufferReader
VAR
    fbFB_CSVMemBufferReader : FB_CSVMemBufferReader;
    arg_eCmd : E_EnumCmdType;
    arg_pBuffer : POINTER TO BYTE;
    arg_cbBuffer : UDINT;
    out_bOk : BOOL;
    out_getValue : T_MaxString;
    out_pValue : POINTER TO BYTE;
    out_cbValue : UDINT;
    out_bCRLF : BOOL;
    out_cbRead : UDINT;
END_VAR

fbFB_CSVMemBufferReader(
    eCmd := arg_eCmd,
    pBuffer := arg_pBuffer,
    cbBuffer := arg_cbBuffer,
    bOk => out_bOk,
    getValue => out_getValue,
    pValue => out_pValue,
    cbValue => out_cbValue,
    bCRLF => out_bCRLF,
    cbRead => out_cbRead
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
