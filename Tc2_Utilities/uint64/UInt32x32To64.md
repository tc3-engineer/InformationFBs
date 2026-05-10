# UInt32x32To64
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
| Example | [`examples/P_Demo_UInt32x32To64.xml`](../examples/P_Demo_UInt32x32To64.xml) |

---
## 1. 功能简述

**32×32 → 64**：两个无符号 32-bit 整数相乘，结果保留为完整 64-bit（无溢出）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt32x32To64 : T_ULARGE_INTEGER
VAR_INPUT
    ui32a : DWORD;
    ui32b : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ui32a` | `DWORD` | 因子 a |
| `ui32b` | `DWORD` | 因子 b |

### 返回值

`T_ULARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_ULARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- 最大输入 (2³²-1)×(2³²-1) ≈ 1.84E19，正好不超过 UINT64 上限。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt32x32To64.xml`](../examples/P_Demo_UInt32x32To64.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UInt32x32To64
VAR
    rResult : T_ULARGE_INTEGER;
    bRun    : BOOL;
    a : DWORD := 16#FFFFFFFF;
    b : DWORD := 16#FFFFFFFF;
END_VAR

IF bRun THEN
    rResult := UInt32x32To64(a, b);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
