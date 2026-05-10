# Int64Div64Ex
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit functions (signed)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_Int64Div64Ex.xml`](../examples/P_Demo_Int64Div64Ex.xml) |

---
## 1. 功能简述

**T_LARGE_INTEGER 整除**：返回商，余数通过 `remainder` 出参返回。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION Int64Div64Ex : T_LARGE_INTEGER
VAR_INPUT
    dividend : T_LARGE_INTEGER;
    divisor : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `dividend` | `T_LARGE_INTEGER` | 被除数 |
| `divisor` | `T_LARGE_INTEGER` | 除数 |

### 返回值

`T_LARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    remainder : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `remainder` | `T_LARGE_INTEGER` | 余数（出参） |

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_LARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- `remainder` 是 VAR_IN_OUT——传变量本身。
- **除零行为未定义**——调用方应先检查 `divisor != 0`（⚠️ PDF 未明示）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Int64Div64Ex.xml`](../examples/P_Demo_Int64Div64Ex.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_Int64Div64Ex
VAR
    rResult : T_LARGE_INTEGER;
    bRun    : BOOL;
    a, b, q, r : T_LARGE_INTEGER;
END_VAR

a := LARGE_INTEGER(0, 100); b := LARGE_INTEGER(0, 7);
IF bRun THEN
    rResult := Int64Div64Ex(dividend := a, divisor := b, remainder := r);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
