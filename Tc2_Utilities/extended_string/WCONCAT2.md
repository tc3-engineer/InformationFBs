# WCONCAT2
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
| Example | [`examples/P_Demo_WCONCAT2.xml`](../examples/P_Demo_WCONCAT2.xml) |

---
## 1. 功能简述

**任意长 WSTRING 拼接**。语义同 `CONCAT2`。返回 TRUE = 成功，FALSE = 截断。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WCONCAT2 : BOOL
VAR_INPUT
    pSrcWString1 : POINTER TO WSTRING;
    pSrcWString2 : POINTER TO WSTRING;
    pDstWString : POINTER TO WSTRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcWString1` | `POINTER TO WSTRING` | 前段 WSTRING 指针 |
| `pSrcWString2` | `POINTER TO WSTRING` | 后段 WSTRING 指针 |
| `pDstWString` | `POINTER TO WSTRING` | 目标 WSTRING 指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`WCONCAT2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 对应 `Tc2_Standard.WCONCAT` 的扩展版（无 WSTRING(255) 限制）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WCONCAT2.xml`](../examples/P_Demo_WCONCAT2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_WCONCAT2
VAR
    rResult : BOOL;
    bRun    : BOOL;
    ws1, ws2, ws3 : WSTRING(255);
END_VAR

ws1 := "Hello, "; ws2 := "World!";
IF bRun THEN
    rResult := WCONCAT2(ADR(ws1), ADR(ws2), ADR(ws3), SIZEOF(ws3));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
