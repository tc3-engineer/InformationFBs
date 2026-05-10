# INT64_TO_LREAL
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
| Example | [`examples/P_Demo_INT64_TO_LREAL.xml`](../examples/P_Demo_INT64_TO_LREAL.xml) |

---
## 1. 功能简述

**T_LARGE_INTEGER → LREAL**：把 TwinCAT 2 legacy 64-bit 有符号整数（结构体）转为双精度浮点。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION INT64_TO_LREAL : LREAL
VAR_INPUT
    in : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_LARGE_INTEGER` | TwinCAT 2 signed 64-bit legacy 结构 |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `LREAL`。无独立错误码。

## 5. 使用注意 / 常见坑

- LREAL 53-bit 尾数，绝对值 > 2⁵³ 的 INT64 会损失精度。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_INT64_TO_LREAL.xml`](../examples/P_Demo_INT64_TO_LREAL.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_INT64_TO_LREAL
VAR
    rResult : LREAL;
    bRun    : BOOL;
    ti : T_LARGE_INTEGER;
END_VAR

ti := LARGE_INTEGER(0, 1234);
IF bRun THEN
    rResult := INT64_TO_LREAL(ti);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
