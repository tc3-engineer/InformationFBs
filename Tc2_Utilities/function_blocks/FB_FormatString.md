# FB_FormatString
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
| Example | [`examples/P_Demo_FB_FormatString.xml`](../examples/P_Demo_FB_FormatString.xml) |

---
## 1. 功能简述

This function block can be used for converting up to 10 arguments (similar to fprintf) into a string and formatting them according to the format specification [ }   406 ] . The formatting takes place in the same PLC cycle. This means that the output string is available immediately after calling the FB.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sFormat : T_MaxString;
    arg1 : T_Arg;
    arg2 : T_Arg;
    arg3 : T_Arg;
    arg4 : T_Arg;
    arg5 : T_Arg;
    arg6 : T_Arg;
    arg7 : T_Arg;
    arg8 : T_Arg;
    arg9 : T_Arg;
    arg10 : T_Arg;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sFormat` | `T_MaxString` | （详见 PDF） |
| `arg1` | `T_Arg` | （详见 PDF） |
| `arg2` | `T_Arg` | （详见 PDF） |
| `arg3` | `T_Arg` | （详见 PDF） |
| `arg4` | `T_Arg` | （详见 PDF） |
| `arg5` | `T_Arg` | （详见 PDF） |
| `arg6` | `T_Arg` | （详见 PDF） |
| `arg7` | `T_Arg` | （详见 PDF） |
| `arg8` | `T_Arg` | （详见 PDF） |
| `arg9` | `T_Arg` | （详见 PDF） |
| `arg10` | `T_Arg` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError : BOOL;
    nErrId : UDINT;
    sOut : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | （详见 PDF） |
| `nErrId` | `UDINT` | （详见 PDF） |
| `sOut` | `T_MaxString` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.22 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.22 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FormatString.xml`](../examples/P_Demo_FB_FormatString.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_FormatString
VAR
    fbFB_FormatString : FB_FormatString;
    arg_sFormat : T_MaxString;
    arg_arg1 : T_Arg;
    arg_arg2 : T_Arg;
    arg_arg3 : T_Arg;
    arg_arg4 : T_Arg;
    arg_arg5 : T_Arg;
    arg_arg6 : T_Arg;
    arg_arg7 : T_Arg;
    arg_arg8 : T_Arg;
    arg_arg9 : T_Arg;
    arg_arg10 : T_Arg;
    out_bError : BOOL;
    out_nErrId : UDINT;
    out_sOut : T_MaxString;
END_VAR

fbFB_FormatString(
    sFormat := arg_sFormat,
    arg1 := arg_arg1,
    arg2 := arg_arg2,
    arg3 := arg_arg3,
    arg4 := arg_arg4,
    arg5 := arg_arg5,
    arg6 := arg_arg6,
    arg7 := arg_arg7,
    arg8 := arg_arg8,
    arg9 := arg_arg9,
    arg10 := arg_arg10,
    bError => out_bError,
    nErrId => out_nErrId,
    sOut => out_sOut
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
