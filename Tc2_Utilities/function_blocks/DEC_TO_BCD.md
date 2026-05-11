# DEC_TO_BCD
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
| Example | [`examples/P_Demo_DEC_TO_BCD.xml`](../examples/P_Demo_DEC_TO_BCD.xml) |

---
## 1. 功能简述

The function block "DEC_TO_BCD" allows decimal numbers to be converted to BCD format. The number to be converted is checked for admissibility of the values.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    START : BOOL;
    DIN : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `START` | `BOOL` | （详见 PDF） |
| `DIN` | `BYTE` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    BOUT : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | （详见 PDF） |
| `ERR` | `BOOL` | （详见 PDF） |
| `ERRID` | `UDINT` | （详见 PDF） |
| `BOUT` | `BYTE` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.5 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.5 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DEC_TO_BCD.xml`](../examples/P_Demo_DEC_TO_BCD.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DEC_TO_BCD
VAR
    fbDEC_TO_BCD : DEC_TO_BCD;
    arg_START : BOOL;
    arg_DIN : BYTE;
    out_BUSY : BOOL;
    out_ERR : BOOL;
    out_ERRID : UDINT;
    out_BOUT : BYTE;
END_VAR

fbDEC_TO_BCD(
    START := arg_START,
    DIN := arg_DIN,
    BUSY => out_BUSY,
    ERR => out_ERR,
    ERRID => out_ERRID,
    BOUT => out_BOUT
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
