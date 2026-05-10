# UINT64_TO_LREAL
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
| Example | [`examples/P_Demo_UINT64_TO_LREAL.xml`](../examples/P_Demo_UINT64_TO_LREAL.xml) |

---
## 1. 功能简述

**T_ULARGE_INTEGER → LREAL**。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UINT64_TO_LREAL : LREAL
VAR_INPUT
    in : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_ULARGE_INTEGER` | 源 legacy 64-bit 无符号 |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `LREAL`。无独立错误码。

## 5. 使用注意 / 常见坑

- LREAL 53-bit 尾数，> 2⁵³ 的值损失精度。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UINT64_TO_LREAL.xml`](../examples/P_Demo_UINT64_TO_LREAL.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UINT64_TO_LREAL
VAR
    rResult : LREAL;
    bRun    : BOOL;
    tu : T_ULARGE_INTEGER;
END_VAR

tu := ULARGE_INTEGER(0, 1234);
IF bRun THEN
    rResult := UINT64_TO_LREAL(tu);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
