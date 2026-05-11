# PVOID_TO_BINSTR
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_PVOID_TO_BINSTR.xml`](../examples/P_Demo_PVOID_TO_BINSTR.xml) |

---
## 1. 功能简述

**PVOID → 二进制字符串**（基 2）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION PVOID_TO_BINSTR : T_MaxString
VAR_INPUT
    in : PVOID;
    iPrecision : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `PVOID` | 待转换 PVOID |
| `iPrecision` | `INT` | 最少位数，不足前补 0；过多不截断 |

### 返回值

`T_MaxString` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_MaxString`。

## 5. 使用注意 / 常见坑

- `iPrecision = 0` 且 `in = 0` → 返回空字符串。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PVOID_TO_BINSTR.xml`](../examples/P_Demo_PVOID_TO_BINSTR.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_PVOID_TO_BINSTR
VAR
    rResult : T_MaxString;
    bRun    : BOOL;
    v : PVOID;
END_VAR

v := 16#FF;
IF bRun THEN
    rResult := PVOID_TO_BINSTR(v, 8);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
