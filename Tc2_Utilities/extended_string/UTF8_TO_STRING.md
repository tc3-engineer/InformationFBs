# UTF8_TO_STRING
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
| Example | [`examples/P_Demo_UTF8_TO_STRING.xml`](../examples/P_Demo_UTF8_TO_STRING.xml) |

---
## 1. 功能简述

**UTF-8 → STRING**。返回 TRUE = 成功；FALSE = 字符集不支持。无法编码的字符被跳过。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UTF8_TO_STRING : BOOL
VAR_INPUT
    pDstSTRING : POINTER TO STRING;
    pSrcUTF8 : PVOID;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDstSTRING` | `POINTER TO STRING` | 目标 STRING 指针 |
| `pSrcUTF8` | `PVOID` | 源 UTF-8 字符串指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nDstLen : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nDstLen` | `UDINT` | 实际写入字符数 |

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`UTF8_TO_STRING(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- UTF-8 中超出 ASCII 的字符在 STRING 字符集（典型 Windows-1252）中可能没法表示——这些会被跳过。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UTF8_TO_STRING.xml`](../examples/P_Demo_UTF8_TO_STRING.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UTF8_TO_STRING
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sUtf8 : STRING(511);
    sOut  : STRING(255);
    nDstLen : UDINT;
END_VAR

sUtf8 := sLiteral_TO_UTF8('café');
IF bRun THEN
    rResult := UTF8_TO_STRING(pDstSTRING := ADR(sOut), pSrcUTF8 := ADR(sUtf8), nDstSize := SIZEOF(sOut), nDstLen => nDstLen);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
