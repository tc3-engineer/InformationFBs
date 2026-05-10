# LREAL_TO_INT64
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
| Example | [`examples/P_Demo_LREAL_TO_INT64.xml`](../examples/P_Demo_LREAL_TO_INT64.xml) |

---
## 1. 功能简述

**LREAL → T_LARGE_INTEGER**：浮点数转 legacy 64-bit 整数（截断）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LREAL_TO_INT64 : T_LARGE_INTEGER
VAR_INPUT
    in : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `LREAL` | 源 LREAL 浮点数 |

### 返回值

`T_LARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_LARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- **截断到整数部分**（朝零方向）。
- LREAL 范围 ±1.79E308 远大于 INT64 ±9.22E18，**超界行为未定义**——⚠️ 待人工确认。
- NaN/INF 输入会触发 FPU 异常——配合 `IsFinite(F_LREAL(x))` 守门。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LREAL_TO_INT64.xml`](../examples/P_Demo_LREAL_TO_INT64.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LREAL_TO_INT64
VAR
    rResult : T_LARGE_INTEGER;
    bRun    : BOOL;
    rX : LREAL := 1.234E9;
END_VAR

IF bRun THEN
    rResult := LREAL_TO_INT64(rX);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
