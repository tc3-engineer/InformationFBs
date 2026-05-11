# FB_EnumStringNumbers
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
| Example | [`examples/P_Demo_FB_EnumStringNumbers.xml`](../examples/P_Demo_FB_EnumStringNumbers.xml) |

---
## 1. 功能简述

This function block can be used to search a string in a REPEAT or WHILE loop for numbers. The string may contain several numbers. Any numbers that are found are output as sub-strings at the function block output. The function searches from the current position for the first character that can be interpreted as a numeral. The search is aborted if a character is found that cannot be interpreted as a number. The eCmd  parameter determines whether the search is for the first number or the next number. The eType  parameter determines the format of the numbers in the search string.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSearch : T_MaxString;
    eCmd : E_EnumCmdType;
    eType : E_NumGroupTypes;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sSearch` | `T_MaxString` | （详见 PDF） |
| `eCmd` | `E_EnumCmdType` | （详见 PDF） |
| `eType` | `E_NumGroupTypes` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    sNumber : T_MaxString;
    nPos : INT;
    bEOS : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNumber` | `T_MaxString` | （详见 PDF） |
| `nPos` | `INT` | （详见 PDF） |
| `bEOS` | `BOOL` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.18 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.18 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnumStringNumbers.xml`](../examples/P_Demo_FB_EnumStringNumbers.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_EnumStringNumbers
VAR
    fbFB_EnumStringNumbers : FB_EnumStringNumbers;
    arg_sSearch : T_MaxString;
    arg_eCmd : E_EnumCmdType;
    arg_eType : E_NumGroupTypes;
    out_sNumber : T_MaxString;
    out_nPos : INT;
    out_bEOS : BOOL;
END_VAR

fbFB_EnumStringNumbers(
    sSearch := arg_sSearch,
    eCmd := arg_eCmd,
    eType := arg_eType,
    sNumber => out_sNumber,
    nPos => out_nPos,
    bEOS => out_bEOS
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
