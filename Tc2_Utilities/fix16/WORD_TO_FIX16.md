# WORD_TO_FIX16
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
| Example | [`examples/P_Demo_WORD_TO_FIX16.xml`](../examples/P_Demo_WORD_TO_FIX16.xml) |

---
## 1. 功能简述

把含定点位编码的 WORD 转回 T_FIX16（与 `FIX16_TO_WORD` 互逆）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WORD_TO_FIX16 : T_FIX16
VAR_INPUT
    in : WORD; (* 16 bit fixed point number *)
    n : WORD(0..15); (* number of fractional bits *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `WORD` | 16-bit 定点位编码 |
| `n` | `WORD(0..15)` | 小数位数 |

### 返回值

`T_FIX16` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `WORD_TO_FIX16(2#0000110010000000, 8)`，返回 `T_FIX16` 类型结果。
- 期望：`12.5（after FIX16_TO_LREAL）`

## 4. 错误码 / 返回值

返回 `T_FIX16`。无错误码。

## 5. 使用注意 / 常见坑

- PDF 例子：`WORD_TO_FIX16(2#0000110010000000, 8)` 经 FIX16_TO_LREAL 后 = 12.5。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WORD_TO_FIX16.xml`](../examples/P_Demo_WORD_TO_FIX16.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_WORD_TO_FIX16
VAR
    bResult : T_FIX16;
    bRun    : BOOL;
END_VAR


IF bRun THEN
    bResult := WORD_TO_FIX16(2#0000110010000000, 8);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
