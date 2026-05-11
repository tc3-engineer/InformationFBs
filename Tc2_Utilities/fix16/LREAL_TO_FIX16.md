# LREAL_TO_FIX16
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
| Example | [`examples/P_Demo_LREAL_TO_FIX16.xml`](../examples/P_Demo_LREAL_TO_FIX16.xml) |

---
## 1. 功能简述

把 LREAL 浮点数转为有符号 16-bit 定点数，可指定小数位数 `n`。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LREAL_TO_FIX16 : T_FIX16
VAR_INPUT
    in : LREAL;
    n : WORD(0..15) := 15;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `LREAL` | 输入 LREAL |
| `n` | `WORD(0..15)` | 目标小数位数（默认 15） |

### 返回值

`T_FIX16` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `LREAL_TO_FIX16(12.5, 8)`，返回 `T_FIX16` 类型结果。
- 期望：`FIX16{val=3200, n=8}（约 12.5）`

## 4. 错误码 / 返回值

返回 `T_FIX16`。无错误码。

## 5. 使用注意 / 常见坑

- **舍入误差**：浮点转定点常有精度丢失（PDF 标注 q2/q15 都可能有误差）。
- `n` 决定小数精度；`n=15` 时整数部分仅 1 bit + 符号——实际范围很小。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LREAL_TO_FIX16.xml`](../examples/P_Demo_LREAL_TO_FIX16.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LREAL_TO_FIX16
VAR
    bResult : T_FIX16;
    bRun    : BOOL;
END_VAR


IF bRun THEN
    bResult := LREAL_TO_FIX16(12.5, 8);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
