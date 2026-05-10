# STRING_TO_WSTRING2
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
| Example | [`examples/P_Demo_STRING_TO_WSTRING2.xml`](../examples/P_Demo_STRING_TO_WSTRING2.xml) |

---
## 1. 功能简述

**STRING → WSTRING（任意长版）**。返回 TRUE = 成功完整转换。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION STRING_TO_WSTRING2 : BOOL
VAR_INPUT
    pDstWSTRING : POINTER TO WSTRING;
    pSrcSTRING : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDstWSTRING` | `POINTER TO WSTRING` | 目标 WSTRING 指针 |
| `pSrcSTRING` | `POINTER TO STRING` | 源 STRING 指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`STRING_TO_WSTRING2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 对应 IEC `STRING_TO_WSTRING` 的安全版（带长度检查）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_WSTRING2.xml`](../examples/P_Demo_STRING_TO_WSTRING2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_STRING_TO_WSTRING2
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sIn   : STRING(255) := 'hello';
    wsOut : WSTRING(255);
END_VAR

IF bRun THEN
    rResult := STRING_TO_WSTRING2(ADR(wsOut), ADR(sIn), SIZEOF(wsOut));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
