# STRING_TO_UTF8
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
| Example | [`examples/P_Demo_STRING_TO_UTF8.xml`](../examples/P_Demo_STRING_TO_UTF8.xml) |

---
## 1. 功能简述

**STRING → UTF-8**（运行时转换变量）。返回 TRUE = 成功；FALSE = 字符集不支持。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION STRING_TO_UTF8 : BOOL
VAR_INPUT
    pDstUTF8 : PVOID;
    pSrcSTRING : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDstUTF8` | `PVOID` | 目标 UTF-8 字符串指针 |
| `pSrcSTRING` | `POINTER TO STRING` | 源 STRING 指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`STRING_TO_UTF8(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- UTF-8 比 STRING 占用更多字节（多字节字符）；nDstSize 要预留余量。
- 字面量转换用 `sLiteral_TO_UTF8` 更方便。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_UTF8.xml`](../examples/P_Demo_STRING_TO_UTF8.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_STRING_TO_UTF8
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sIn   : STRING(255) := 'café';
    sUtf8 : STRING(511);
END_VAR

IF bRun THEN
    rResult := STRING_TO_UTF8(ADR(sUtf8), ADR(sIn), SIZEOF(sUtf8));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
