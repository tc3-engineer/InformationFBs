# DATA_TO_HEXSTR2
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
| Example | [`examples/P_Demo_DATA_TO_HEXSTR2.xml`](../examples/P_Demo_DATA_TO_HEXSTR2.xml) |

---
## 1. 功能简述

**二进制 → 十六进制字符串**：把 binary buffer 转为 hex 文本（如 `[0xAB, 0xCD]` → 'AB CD'）。返回成功转换的字节数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION DATA_TO_HEXSTR2 : UDINT
VAR_INPUT
    pSrcData : POINTER TO BYTE; (* pointer to data buffer *)
    nSrcSize : UDINT; (* size of data buffer in bytes (= number of bytes to be converted) *)
    pDstHexStr : POINTER TO STRING; (* pointer to destination buffer *)
    nDstSize : UDINT; (* size of destination buffer in bytes *)
    bLoCase : BOOL; (* default: use "ABCDEF", if TRUE use "abcdef" characters *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcData` | `POINTER TO BYTE` | 源数据缓冲指针（用 ADR） |
| `nSrcSize` | `UDINT` | 要转换的字节数（用 SIZEOF） |
| `pDstHexStr` | `POINTER TO STRING` | 目标 HEX 字符串指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |
| `bLoCase` | `BOOL` | TRUE = 用小写 abcdef；默认大写 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`DATA_TO_HEXSTR2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 可用于 dump 任意类型变量（基础类型、struct）。
- 目标超长时末尾补 `'.'` 表示截断。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DATA_TO_HEXSTR2.xml`](../examples/P_Demo_DATA_TO_HEXSTR2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DATA_TO_HEXSTR2
VAR
    rResult : UDINT;
    bRun    : BOOL;
    stData : ARRAY[0..3] OF BYTE := [16#AB, 16#CD, 16#01, 16#23];
    sHex : STRING(63);
END_VAR

IF bRun THEN
    rResult := DATA_TO_HEXSTR2(ADR(stData), SIZEOF(stData), ADR(sHex), SIZEOF(sHex), FALSE);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
