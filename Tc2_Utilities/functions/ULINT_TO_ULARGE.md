# ULINT_TO_ULARGE
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_ULINT_TO_ULARGE.xml`](../examples/P_Demo_ULINT_TO_ULARGE.xml) |

---
## 1. 功能简述

**ULINT → T_ULARGE_INTEGER**：TwinCAT 3 native 无符号 64-bit → TwinCAT 2 legacy 结构。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION ULINT_TO_ULARGE : T_ULARGE_INTEGER
VAR_INPUT
    in : ULINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `ULINT` | native unsigned 64-bit |

### 返回值

`T_ULARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_ULARGE_INTEGER`。

## 5. 使用注意 / 常见坑

- 反向：`ULARGE_TO_ULINT`（Round 8）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ULINT_TO_ULARGE.xml`](../examples/P_Demo_ULINT_TO_ULARGE.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_ULINT_TO_ULARGE
VAR
    rResult : T_ULARGE_INTEGER;
    bRun    : BOOL;
    v : ULINT := 12345;
END_VAR

IF bRun THEN
    rResult := ULINT_TO_ULARGE(v);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
