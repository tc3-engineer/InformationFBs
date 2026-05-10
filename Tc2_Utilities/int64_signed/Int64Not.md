# Int64Not
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
| Example | [`examples/P_Demo_Int64Not.xml`](../examples/P_Demo_Int64Not.xml) |

---
## 1. 功能简述

**按位 NOT**：返回所有 64 bit 取反的结果。等价于 `LREAL_TO_INT64(0) - i64 - 1`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION Int64Not : T_LARGE_INTEGER
VAR_INPUT
    i64 : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `i64` | `T_LARGE_INTEGER` | 待按位取反 |

### 返回值

`T_LARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_LARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- 无特殊注意事项。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Int64Not.xml`](../examples/P_Demo_Int64Not.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_Int64Not
VAR
    rResult : T_LARGE_INTEGER;
    bRun    : BOOL;
    a : T_LARGE_INTEGER;
END_VAR

a := LARGE_INTEGER(0, 0);
IF bRun THEN
    rResult := Int64Not(a);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
