# STRNCPY
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
| Example | [`examples/P_Demo_STRNCPY.xml`](../examples/P_Demo_STRNCPY.xml) |

---
## 1. 功能简述

**安全字符串复制**：复制 src 到 dst，返回 TRUE = 完整复制；FALSE = 因 dst 不够长被截断。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION STRNCPY : BOOL
VAR_INPUT
    pDst : POINTER TO STRING;
    pSrc : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDst` | `POINTER TO STRING` | 目标 STRING 指针 |
| `pSrc` | `POINTER TO STRING` | 源 STRING 指针 |
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
| `nSrcLen` | `UDINT` | 源字符串字符数 |
| `nDstLen` | `UDINT` | 实际复制到目标的字符数 |

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`STRNCPY(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 等价于 C 的 `strncpy`：截断时保留 NUL 结束符。
- `nSrcLen` 和 `nDstLen` 输出便于调用方判断是否截断。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRNCPY.xml`](../examples/P_Demo_STRNCPY.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_STRNCPY
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sSrc : STRING(255) := 'hello';
    sDst : STRING(63);
    nSrcLen, nDstLen : UDINT;
END_VAR

IF bRun THEN
    rResult := STRNCPY(pDst := ADR(sDst), pSrc := ADR(sSrc), nDstSize := SIZEOF(sDst), nSrcLen => nSrcLen, nDstLen => nDstLen);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
