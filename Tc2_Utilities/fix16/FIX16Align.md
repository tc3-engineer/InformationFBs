# FIX16Align
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
| Example | [`examples/P_Demo_FIX16Align.xml`](../examples/P_Demo_FIX16Align.xml) |

---
## 1. 功能简述

改变 T_FIX16 的小数位数（resolution）。返回新的定点数。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIX16Align : T_FIX16
VAR_INPUT
    in : T_FIX16;
    n : BYTE(0..15);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_FIX16` | 原定点数 |
| `n` | `BYTE(0..15)` | 新的小数位数 |

### 返回值

`T_FIX16` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `FIX16Align(q8, 4)`，返回 `T_FIX16` 类型结果。
- 期望：`0.5625（q8 装 0.6 后转 q4）`

## 4. 错误码 / 返回值

返回 `T_FIX16`。无错误码。

## 5. 使用注意 / 常见坑

- **截断（不四舍五入）**：从 q8 转 q4 时，小数位减半 → 0.6015625 变 0.5625（PDF 例子）。
- 用于不同精度间转换。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIX16Align.xml`](../examples/P_Demo_FIX16Align.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FIX16Align
VAR
    bResult : T_FIX16;
    bRun    : BOOL;
    q8 : T_FIX16;
END_VAR

q8 := LREAL_TO_FIX16(0.6, 8);
IF bRun THEN
    bResult := FIX16Align(q8, 4);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
