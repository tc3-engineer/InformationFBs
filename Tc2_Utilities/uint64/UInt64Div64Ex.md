# UInt64Div64Ex
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Div64Ex.xml`](../examples/P_Demo_UInt64Div64Ex.xml) |

---
## 1. 功能简述

**T_ULARGE_INTEGER 整除（带余数）**。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Div64Ex : T_ULARGE_INTEGER
VAR_INPUT
    dividend : T_ULARGE_INTEGER;
    divisor : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `dividend` | `T_ULARGE_INTEGER` | 被除数 |
| `divisor` | `T_ULARGE_INTEGER` | 除数 |

### 返回值

`T_ULARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    remainder : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `remainder` | `T_ULARGE_INTEGER` | 余数（出参） |

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_ULARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- **除零行为未定义**。
- 等价于 `UInt64Div64` + `UInt64Mod64` 一次完成。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Div64Ex.xml`](../examples/P_Demo_UInt64Div64Ex.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UInt64Div64Ex
VAR
    rResult : T_ULARGE_INTEGER;
    bRun    : BOOL;
    a, b, q, r : T_ULARGE_INTEGER;
END_VAR

a := ULARGE_INTEGER(0, 100); b := ULARGE_INTEGER(0, 7);
IF bRun THEN
    rResult := UInt64Div64Ex(dividend := a, divisor := b, remainder := r);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
