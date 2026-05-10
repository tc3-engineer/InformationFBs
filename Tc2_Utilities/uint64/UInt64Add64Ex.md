# UInt64Add64Ex
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
| Example | [`examples/P_Demo_UInt64Add64Ex.xml`](../examples/P_Demo_UInt64Add64Ex.xml) |

---
## 1. 功能简述

**带溢出检测的 UInt64Add64**。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Add64Ex : T_ULARGE_INTEGER
VAR_INPUT
    augend : T_ULARGE_INTEGER;
    addend : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `augend` | `T_ULARGE_INTEGER` | 加数 a |
| `addend` | `T_ULARGE_INTEGER` | 加数 b |

### 返回值

`T_ULARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    bOV : BOOL; (* TRUE => arithmetic overflow, FALSE => no overflow *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOV` | `BOOL` | 溢出标志（VAR_IN_OUT） |

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_ULARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- `bOV` 必须传变量；溢出后结果未定义。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Add64Ex.xml`](../examples/P_Demo_UInt64Add64Ex.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UInt64Add64Ex
VAR
    rResult : T_ULARGE_INTEGER;
    bRun    : BOOL;
    a, b : T_ULARGE_INTEGER;
    bOV : BOOL;
END_VAR

a := ULARGE_INTEGER(16#FFFFFFFF, 16#FFFFFFFF); b := ULARGE_INTEGER(0, 1);
IF bRun THEN
    rResult := UInt64Add64Ex(augend := a, addend := b, bOV := bOV);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
