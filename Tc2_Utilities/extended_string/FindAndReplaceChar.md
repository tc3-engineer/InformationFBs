# FindAndReplaceChar
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FindAndReplaceChar.xml`](../examples/P_Demo_FindAndReplaceChar.xml) |

---
## 1. 功能简述

**查找并替换单字符**：把 src 中所有 `sDeleteChar` 替换为 `sInsertChar`。返回替换次数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FindAndReplaceChar : UDINT
VAR_INPUT
    pSrcString : POINTER TO STRING;
    sDeleteChar : STRING(1);
    sInsertChar : STRING(1);
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcString` | `POINTER TO STRING` | 源 STRING 指针 |
| `sDeleteChar` | `STRING(1)` | 要替换的字符 |
| `sInsertChar` | `STRING(1)` | 替换为字符 |
| `pDstString` | `POINTER TO STRING` | 目标 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`FindAndReplaceChar(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 针对单字符比 `FindAndReplace` 更快。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndReplaceChar.xml`](../examples/P_Demo_FindAndReplaceChar.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FindAndReplaceChar
VAR
    rResult : UDINT;
    bRun    : BOOL;
    sIn  : STRING(255) := 'a-b-c-d';
    sOut : STRING(255);
END_VAR

IF bRun THEN
    rResult := FindAndReplaceChar(ADR(sIn), '-', '_', ADR(sOut), SIZEOF(sOut));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
