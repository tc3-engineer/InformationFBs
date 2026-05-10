# LINT_TO_LARGE
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
| Example | [`examples/P_Demo_LINT_TO_LARGE.xml`](../examples/P_Demo_LINT_TO_LARGE.xml) |

---
## 1. 功能简述

**native → legacy 64-bit**：LINT → T_LARGE_INTEGER。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LINT_TO_LARGE : T_LARGE_INTEGER
VAR_INPUT
    in : LINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `LINT` | 原生 64-bit 有符号 |

### 返回值

`T_LARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_LARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- 桥接到 TwinCAT 2 风格 API；新代码尽量保留 LINT 直至边界。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LINT_TO_LARGE.xml`](../examples/P_Demo_LINT_TO_LARGE.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LINT_TO_LARGE
VAR
    rResult : T_LARGE_INTEGER;
    bRun    : BOOL;
    li : LINT := 100;
END_VAR

IF bRun THEN
    rResult := LINT_TO_LARGE(li);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
