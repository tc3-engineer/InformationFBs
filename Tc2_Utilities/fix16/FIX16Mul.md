# FIX16Mul
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `16 bit fixed point number functions (signed)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FIX16Mul.xml`](../examples/P_Demo_FIX16Mul.xml) |

---
## 1. 功能简述

两个 16-bit 定点数相乘（截断对齐到较低分辨率），返回 T_FIX16。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIX16Mul : T_FIX16
VAR_INPUT
    multiA : T_FIX16;
    multiB : T_FIX16;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `multiA` | `T_FIX16` | 第一乘数 |
| `multiB` | `T_FIX16` | 第二乘数 |

### 返回值

`T_FIX16` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `FIX16Mul(a, b)`，返回 `T_FIX16` 类型结果。
- 期望：`2.5（=0.25×10.0）`

## 4. 错误码 / 返回值

返回 `T_FIX16`。无错误码。

## 5. 使用注意 / 常见坑

- PDF 示例：0.25 × 10.0 = 2.5。
- 可能溢出（16-bit 限制）——⚠️ 待人工确认行为。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIX16Mul.xml`](../examples/P_Demo_FIX16Mul.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FIX16Mul
VAR
    bResult : T_FIX16;
    bRun    : BOOL;
    a, b : T_FIX16;
END_VAR

a := LREAL_TO_FIX16(0.25, 8); b := LREAL_TO_FIX16(10.0, 8);
IF bRun THEN
    bResult := FIX16Mul(a, b);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
