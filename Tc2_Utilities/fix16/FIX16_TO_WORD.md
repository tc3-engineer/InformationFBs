# FIX16_TO_WORD
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
| Example | [`examples/P_Demo_FIX16_TO_WORD.xml`](../examples/P_Demo_FIX16_TO_WORD.xml) |

---
## 1. 功能简述

把 16-bit 定点数（`T_FIX16`）转为 WORD（含数值位 + 小数位编码）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIX16_TO_WORD : WORD
VAR_INPUT
    in : T_FIX16;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_FIX16` | 要转换的定点数 |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `FIX16_TO_WORD(fp)`，返回 `WORD` 类型结果。
- 期望：`16#0C80（即 2#0000110010000000）`

## 4. 错误码 / 返回值

返回 `WORD`。无错误码。

## 5. 使用注意 / 常见坑

- WORD 直接含定点数的位编码——`FIX16_TO_WORD(LREAL_TO_FIX16(12.5, 8))` = `2#0000110010000000`。
- 用 `WORD_TO_FIX16` 可逆向。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIX16_TO_WORD.xml`](../examples/P_Demo_FIX16_TO_WORD.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FIX16_TO_WORD
VAR
    bResult : WORD;
    bRun    : BOOL;
    fp : T_FIX16;
END_VAR

fp := LREAL_TO_FIX16(12.5, 8);
IF bRun THEN
    bResult := FIX16_TO_WORD(fp);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
