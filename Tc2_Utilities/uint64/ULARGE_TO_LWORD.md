# ULARGE_TO_LWORD
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
| Example | [`examples/P_Demo_ULARGE_TO_LWORD.xml`](../examples/P_Demo_ULARGE_TO_LWORD.xml) |

---
## 1. 功能简述

**legacy → native 64-bit 无符号位字**：T_ULARGE_INTEGER → LWORD。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION ULARGE_TO_LWORD : LWORD
VAR_INPUT
    in : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_ULARGE_INTEGER` | 源 legacy 64-bit 无符号 |

### 返回值

`LWORD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `LWORD`。无独立错误码。

## 5. 使用注意 / 常见坑

- ULINT vs LWORD 仅类型语义不同（前者为无符号整数，后者为无类型 64-bit 位字）；位模式相同。
- 对应 `LWORD_TO_ULARGE` 反向。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ULARGE_TO_LWORD.xml`](../examples/P_Demo_ULARGE_TO_LWORD.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_ULARGE_TO_LWORD
VAR
    rResult : LWORD;
    bRun    : BOOL;
    tu : T_ULARGE_INTEGER;
END_VAR

tu := ULARGE_INTEGER(0, 100);
IF bRun THEN
    rResult := ULARGE_TO_LWORD(tu);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
