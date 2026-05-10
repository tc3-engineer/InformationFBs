# UInt64isZero
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
| Example | [`examples/P_Demo_UInt64isZero.xml`](../examples/P_Demo_UInt64isZero.xml) |

---
## 1. 功能简述

**判 T_ULARGE_INTEGER 是否为零**。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64isZero : BOOL
VAR_INPUT
    ui64 : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ui64` | `T_ULARGE_INTEGER` | 待测值 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- **函数名为 `UInt64isZero`（小写 `is`）**——区别于 Round 7 的 `Int64IsZero`（大写 `Is`）。
- TOC、Return value 表、VAR 区均一致用 `UInt64isZero`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64isZero.xml`](../examples/P_Demo_UInt64isZero.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UInt64isZero
VAR
    rResult : BOOL;
    bRun    : BOOL;
    a : T_ULARGE_INTEGER;
END_VAR

a := ULARGE_INTEGER(0, 0);
IF bRun THEN
    rResult := UInt64isZero(a);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
