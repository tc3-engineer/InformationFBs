# LARGE_INTEGER
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
| Example | [`examples/P_Demo_LARGE_INTEGER.xml`](../examples/P_Demo_LARGE_INTEGER.xml) |

---
## 1. 功能简述

**T_LARGE_INTEGER 构造器**：从 (HighPart, LowPart) 构造一个 T_LARGE_INTEGER 结构。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LARGE_INTEGER : T_LARGE_INTEGER
VAR_INPUT
    dwHighPart : DWORD;
    dwLowPart : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `dwHighPart` | `DWORD` | 高 32 bit |
| `dwLowPart` | `DWORD` | 低 32 bit |

### 返回值

`T_LARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_LARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- **注意符号**：dwHighPart 的最高 bit 决定整体符号——`16#80000000` 起始为负数。
- 用于把 32+32 数据拼成 64-bit；常和 `INT64_TO_LREAL` / `LREAL_TO_INT64` 配合。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LARGE_INTEGER.xml`](../examples/P_Demo_LARGE_INTEGER.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LARGE_INTEGER
VAR
    rResult : T_LARGE_INTEGER;
    bRun    : BOOL;
    result : T_LARGE_INTEGER;
END_VAR

IF bRun THEN
    rResult := LARGE_INTEGER(0, 16#12345678);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
