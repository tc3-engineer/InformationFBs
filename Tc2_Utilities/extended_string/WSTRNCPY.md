# WSTRNCPY
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
| Example | [`examples/P_Demo_WSTRNCPY.xml`](../examples/P_Demo_WSTRNCPY.xml) |

---
## 1. 功能简述

**安全 WSTRING 复制**：等价 `STRNCPY` 的 WSTRING 版。返回 TRUE = 完整复制；FALSE = 因 dst 不够被截断。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WSTRNCPY : BOOL
VAR_INPUT
    pDst : POINTER TO WSTRING;
    pSrc : POINTER TO WSTRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDst` | `POINTER TO WSTRING` | 目标 WSTRING 指针 |
| `pSrc` | `POINTER TO WSTRING` | 源 WSTRING 指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数（含 NUL） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nSrcLen : UDINT;
    nDstLen : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nSrcLen` | `UDINT` | 源字符数 |
| `nDstLen` | `UDINT` | 实际复制字符数 |

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`WSTRNCPY(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 截断时保留 NUL 结束符。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WSTRNCPY.xml`](../examples/P_Demo_WSTRNCPY.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_WSTRNCPY
VAR
    rResult : BOOL;
    bRun    : BOOL;
    wsSrc : WSTRING(255);
    wsDst : WSTRING(63);
    nSrcLen, nDstLen : UDINT;
END_VAR

wsSrc := "hello";
IF bRun THEN
    rResult := WSTRNCPY(pDst := ADR(wsDst), pSrc := ADR(wsSrc), nDstSize := SIZEOF(wsDst), nSrcLen => nSrcLen, nDstLen => nDstLen);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
