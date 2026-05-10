# WSTRING_TO_UTF8
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
| Example | [`examples/P_Demo_WSTRING_TO_UTF8.xml`](../examples/P_Demo_WSTRING_TO_UTF8.xml) |

---
## 1. 功能简述

**WSTRING → UTF-8**。返回 TRUE = 成功；FALSE = 字符集不支持（理论上不应发生）。无法编码的字符被跳过。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WSTRING_TO_UTF8 : BOOL
VAR_INPUT
    pDstUTF8 : PVOID;
    pSrcWSTRING : POINTER TO WSTRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDstUTF8` | `PVOID` | 目标 UTF-8 指针 |
| `pSrcWSTRING` | `POINTER TO WSTRING` | 源 WSTRING 指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`WSTRING_TO_UTF8(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- WSTRING 是 UTF-16，UTF-8 几乎能完整表达——这条路径几乎不会丢字符。
- UTF-8 比 WSTRING 字节数可多可少（取决于字符集分布）；nDstSize 适当预留。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WSTRING_TO_UTF8.xml`](../examples/P_Demo_WSTRING_TO_UTF8.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_WSTRING_TO_UTF8
VAR
    rResult : BOOL;
    bRun    : BOOL;
    ws    : WSTRING(255);
    sUtf8 : STRING(511);
END_VAR

ws := "café";
IF bRun THEN
    rResult := WSTRING_TO_UTF8(ADR(sUtf8), ADR(ws), SIZEOF(sUtf8));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
