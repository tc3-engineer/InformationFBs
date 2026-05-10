# Int64Sub64
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
| Example | [`examples/P_Demo_Int64Sub64.xml`](../examples/P_Demo_Int64Sub64.xml) |

---
## 1. 功能简述

**T_LARGE_INTEGER 相减**：返回 a - b。**不检查溢出**。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION Int64Sub64 : T_LARGE_INTEGER
VAR_INPUT
    i64a : T_LARGE_INTEGER;
    i64b : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `i64a` | `T_LARGE_INTEGER` | 被减数 |
| `i64b` | `T_LARGE_INTEGER` | 减数 |

### 返回值

`T_LARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_LARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- 对应加法 `Int64Add64`；目前无 SubEx 溢出检测变体。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Int64Sub64.xml`](../examples/P_Demo_Int64Sub64.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_Int64Sub64
VAR
    rResult : T_LARGE_INTEGER;
    bRun    : BOOL;
    a, b : T_LARGE_INTEGER;
END_VAR

a := LARGE_INTEGER(0, 100); b := LARGE_INTEGER(0, 30);
IF bRun THEN
    rResult := Int64Sub64(a, b);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
