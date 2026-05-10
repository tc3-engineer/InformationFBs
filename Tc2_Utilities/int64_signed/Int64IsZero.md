# Int64IsZero
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
| Example | [`examples/P_Demo_Int64IsZero.xml`](../examples/P_Demo_Int64IsZero.xml) |

---
## 1. 功能简述

**判 T_LARGE_INTEGER 是否为零**：高低位都为 0 时返回 TRUE。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION Int64IsZero : BOOL
VAR_INPUT
    i64 : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `i64` | `T_LARGE_INTEGER` | 待测值 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- PDF 返回值表里写成 `Int64isZero`（小写 i）——这是 PDF 排版瑕疵，**实际函数名是 `Int64IsZero`**（TOC 与 VAR 区均用大写 I）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Int64IsZero.xml`](../examples/P_Demo_Int64IsZero.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_Int64IsZero
VAR
    rResult : BOOL;
    bRun    : BOOL;
    a : T_LARGE_INTEGER;
END_VAR

a := LARGE_INTEGER(0, 0);
IF bRun THEN
    rResult := Int64IsZero(a);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
